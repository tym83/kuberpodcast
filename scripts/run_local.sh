#!/usr/bin/env bash
# Produce the weekly digest from this machine and land it in the repo.
#
# Worth doing instead of relying on the GitHub runner: Reddit answers a home or
# office IP but blocks datacenter egress, so a local run collects the community
# surface that the scheduled job cannot reach.
#
# Usage:  scripts/run_local.sh [--days N] [--dry-run]
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

DAYS=7
DRY_RUN=0
while [ $# -gt 0 ]; do
  case "$1" in
    --days) DAYS="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

# Homebrew and the like are not on launchd's PATH.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Secrets live outside the repo. ANTHROPIC_API_KEY is what makes the comments
# worth reading; REDDIT_* is optional here because Reddit answers this machine.
ENV_FILE="${KUBERPODCAST_ENV:-$HOME/.config/kuberpodcast/env}"
if [ -f "$ENV_FILE" ]; then
  set -a; . "$ENV_FILE"; set +a
fi

LOG_DIR="$HOME/.local/state/kuberpodcast"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/run-$(date -u +%Y-%m-%dT%H%M%SZ).log"
exec > >(tee -a "$LOG") 2>&1

# One run at a time: a weekly job that overlaps itself corrupts the state store.
LOCK="$LOG_DIR/run.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "another run holds $LOCK — exiting"
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

PY="$REPO_DIR/.venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "creating the virtualenv"
  python3 -m venv "$REPO_DIR/.venv"
  "$REPO_DIR/.venv/bin/pip" -q install -r "$REPO_DIR/requirements.txt"
fi

echo "=== $(date -u) — window: last $DAYS days ==="

git checkout -q main
git pull -q --ff-only origin main

# GitHub Releases and Security Advisories are rate-limited without a token.
if [ -z "${GITHUB_TOKEN:-}" ] && command -v gh >/dev/null 2>&1; then
  GITHUB_TOKEN="$(gh auth token 2>/dev/null || true)"
  export GITHUB_TOKEN
fi

"$PY" scripts/collect_raw.py --days "$DAYS" --out data/raw.json
"$PY" scripts/build_digest.py --raw data/raw.json --outdir digest \
      --selection-out "data/selection-$(date -u +%F).json"

if [ "$DRY_RUN" = "1" ]; then
  echo "dry run: built but not committed"
  git status --short digest state
  exit 0
fi

if [ -z "$(git status --porcelain digest)" ]; then
  echo "no new digest produced — nothing to commit"
  exit 0
fi

FILE="$(git status --porcelain digest | awk '{print $NF}' | grep -E '/[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$' | head -1)"
DATE="$(basename "$FILE" .md)"
BRANCH="digest/$DATE-local"

if git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
  BRANCH="$BRANCH-$(date -u +%H%M)"
fi

git checkout -q -b "$BRANCH"
git add digest state
git commit -q --signoff \
  -m "chore(digest): weekly digest $DATE" \
  -m "Collected from a local run over the preceding $DAYS days."
git push -q -u origin "$BRANCH"

PR_URL="$(gh pr create --base main --head "$BRANCH" \
  --title "chore(digest): weekly digest $DATE" \
  --body "Weekly digest for \`$DATE\`, collected locally by \`scripts/run_local.sh\`.")"
echo "opened $PR_URL"

gh pr merge "$PR_URL" --squash --delete-branch \
  || gh pr merge "$PR_URL" --squash --delete-branch --admin

git checkout -q main
git pull -q --ff-only origin main
echo "=== done: $FILE ==="
