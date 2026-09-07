# Reviewer #1 — Feed Validation Report

Scope: every feed URL in `feeds.yaml` **as handed to reviewer #1** (184 feeds)
probed with a real HTTP GET (browser UA `Mozilla/5.0 (compatible;
kuberpodcast-digest/1.0; +https://github.com/tym83/kuberpodcast)`, 20s
timeout, redirects followed, 10-16 way thread pool), parsed with
`feedparser`, classified OK / DEAD / EMPTY / STALE / GEOBLOCKED. Every
replacement URL listed below was independently re-verified with its own HTTP
GET + feedparser parse (entries > 0, real dates) before being accepted.
Raw per-feed data: `sources/.validation.json`.

**Moving-target note:** other reviewers added sources to `feeds.yaml`
concurrently with this validation pass — it grew from 184 → 302 → 441 → 445
entries during this review. Reviewer #1's 184-feed scope was validated
exhaustively (this report); the intermediate 302-entry snapshot was also
validated in full (283 OK, 2 DEAD — `envoy`, `rachelbythebay` — 17 STALE, 0
EMPTY/GEOBLOCKED — see `.validation.json` → `catalog_302_current`). The
~140 feeds added after that snapshot (up to the current 445) have **not**
been validated by reviewer #1 and need a follow-up pass by whoever added
them or by a re-run of this review.

**Self-correction:** an earlier version of this report incorrectly marked
`api7`, `devopsish`, `chronosphere`, and `kubeweekly` as DEAD (checked with a
too-narrow set of URL patterns) and `linkerd`'s fix pointed at a feed that
duplicates the existing `buoyant` entry. All four "dead" calls were wrong —
working feeds exist for all of them. By the time this was caught, those four
entries had already been deleted from `feeds.yaml` on the strength of the
earlier (wrong) report. **I have restored all four with corrected URLs and
fixed `linkerd`'s URL directly in `feeds.yaml`** (see Replacements below for
the corrected URLs). The counts and tables in this report already reflect
the corrected classification.

## Summary

| Metric | Count |
|---|---|
| Total feeds in the 184-feed scope | 184 |
| OK as-shipped (no change needed) | 110 |
| Fixed (URL corrected, now returns real entries) | 52 |
| — of which still low-cadence after fixing (STALE) | 9 |
| — of which fresh after fixing (OK) | 43 |
| Dead, no working replacement found (recommend remove) | 15 |
| Stale (works, but keep — newest entry >120 days old) | 16 (7 unchanged-URL + 9 fixed-URL-but-still-stale) |
| Geoblocked (403/451 from US egress) | 0 |
| **Final health: OK** | **153** |
| **Final health: STALE** | **16** |
| **Final health: DEAD (remove)** | **15** |

153 + 16 + 15 = 184. ✓

## Replacements

`id: old-url -> new-url` — all 52 verified with HTTP 200 + feedparser parse,
entries > 0. (9 of these still come back STALE after fixing — see the Stale
section for their dates; they are listed here too because the URL itself was
still corrected and should be updated in `feeds.yaml`.)

```
apache: https://news.apache.org/foundation/entry/feed.rss -> https://news.apache.org/feed
api7: https://api7.ai/blog/rss.xml -> https://api7.ai/rss.xml
aquasec: https://blog.aquasec.com/rss.xml -> https://www.aquasec.com/feed/
bitfieldconsult: https://bitfieldconsulting.com/rss.xml -> https://bitfieldconsulting.com/posts?format=rss
buildkite: https://buildkite.com/blog/feed.xml -> https://buildkite.com/blog.atom
ceph: https://ceph.io/en/news/blog/index.xml -> https://ceph.io/en/news/blog/feed.xml
chronosphere: https://chronosphere.io/feed/ -> https://chronosphere.io/feed/?post_type=resource
clickhouse: https://clickhouse.com/blog/rss.xml -> https://clickhouse.com/rss.xml
cloudflarelearn: https://www.agwa.name/blog/rss -> https://www.agwa.name/blog/feed
cloudseclist: https://cloudseclist.com/issues/index.xml -> https://cloudseclist.com/feed.xml
cloudwego: https://www.cloudwego.io/blog/index.xml -> https://www.cloudwego.io/index.xml
dapr: https://blog.dapr.io/feed -> https://blog.dapr.io/posts/index.xml
deckhouse: https://deckhouse.io/blog/index.xml -> https://deckhouse.ru/blog/feed/
depot: https://depot.dev/blog/rss.xml -> https://depot.dev/rss.xml
devopsish: https://devopsish.com/index.xml -> https://devopsish.substack.com/feed
digitalocean: https://www.digitalocean.com/blog/rss.xml -> https://www.digitalocean.com/rss/blog.atom
falco: https://falco.org/blog/index.xml -> https://falco.org/feed.xml
fastly: https://www.fastly.com/blog/feed -> https://www.fastly.com/blog_rss.xml
figma: https://www.figma.com/blog/feed.xml -> https://www.figma.com/blog/feed/atom.xml
flant: https://blog.flant.ru/rss/ -> https://flant.ru/feed/
hetzner: https://www.hetzner.com/blog/feed/ -> https://www.hetzner.com/blog/rss.xml
honeycomb: https://www.honeycomb.io/blog/feed -> https://www.honeycomb.io/rss/blog.xml
istio: https://istio.io/latest/blog/index.xml -> https://istio.io/latest/feed.xml
iximiuz: https://iximiuz.com/en/feed.xml -> https://labs.iximiuz.com/feed.rss
jepsen: https://jepsen.io/analyses.atom -> https://jepsen.io/blog.atom
k8s-gateway: https://gateway-api.sigs.k8s.io/feed_rss_created.xml -> https://gateway-api.sigs.k8s.io/index.xml
karmada: https://karmada.io/blog/index.xml -> https://karmada.io/blog/rss.xml
knative: https://knative.dev/blog/index.xml -> https://knative.dev/blog/feed_rss_created.xml
kong: https://konghq.com/blog/feed -> https://konghq.com/feed/rss/blogs
kubeedge: https://kubeedge.io/blog/index.xml -> https://kubeedge.io/blog/rss.xml
kubeweekly: https://www.cncf.io/kubeweekly/feed/ -> https://www.cncf.io/feed/?post_type=lf_kubeweekly
linkerd: https://linkerd.io/blog/index.xml -> https://linkerd.io/blog/feed.xml
mattklein: https://mattklein123.dev/feed.xml -> https://mattklein123.dev/atom.xml
mirantis: https://www.mirantis.com/feed/ -> https://www.mirantis.com/blog/feed/
modal: https://modal.com/blog/feed.xml -> https://modal.com/blog/atom.xml
nutanix: https://www.nutanix.com/blog/rss.xml -> https://www.nutanix.com/blog.rssfeed.xml
opa: https://blog.openpolicyagent.org/feed -> https://www.openpolicyagent.org/blog/rss.xml
openbao: https://openbao.org/blog/index.xml -> https://openbao.org/blog/rss.xml
openinfra: https://openinfra.org/feed -> https://openinfra.org/rss.xml
opentofu: https://opentofu.org/blog/index.xml -> https://opentofu.org/blog/rss.xml
ray: https://www.anyscale.com/blog/rss.xml -> https://www.anyscale.com/rss.xml
render: https://render.com/blog/rss.xml -> https://render.com/blog/feed.xml
slurm: https://slurm.io/rss/ -> https://slurm.io/rss.xml
spacelift: https://spacelift.io/blog/rss.xml -> https://spacelift.io/rss
talos: https://www.siderolabs.com/blog/rss/ -> https://www.siderolabs.com/feed
temporal: https://temporal.io/blog/rss.xml -> https://temporal.io/blog/feed.xml
tetrate: https://tetrate.io/feed/ -> https://tetrate.io/rss.xml
timescale: https://www.tigerdata.com/blog/rss.xml -> https://www.tigerdata.com/blog/rss
traefik: https://traefik.io/blog/feed/ -> https://traefik.io/rss.xml
vllm: https://blog.vllm.ai/feed.xml -> https://vllm.ai/blog/rss.xml
wiz: https://www.wiz.io/feed.xml -> https://www.wiz.io/feed/rss.xml
yandexcloud: https://yandex.cloud/ru/blog/rss -> https://yandex.cloud/ru/feed.rss
```

Notable / non-obvious fixes worth a second look:

- **linkerd** — corrected twice. First pass wrongly concluded `linkerd.io/blog`
  had no feed and repointed it at `buoyant.io/blog/rss.xml` — which duplicates
  the existing `buoyant` catalog entry (same company, same feed). Re-checked:
  `linkerd.io/blog/feed.xml` (note: `feed.xml`, not the dead `index.xml`)
  works fine on its own — 10 entries, newest 2026-06-24 (75 days old, not
  stale). Now points there instead; no more overlap with `buoyant`.
- **api7, devopsish, chronosphere, kubeweekly** — all four were wrongly marked
  DEAD in an earlier pass (checked too few URL patterns) and were deleted from
  `feeds.yaml` as a result. All four actually have working feeds — see
  Replacements above. Restored to `feeds.yaml` with corrected URLs.
  `kubeweekly`'s "working" feed is a frozen historical archive (see Stale
  section) — restored anyway since the URL is real and returns real entries;
  whether a permanently-frozen source belongs in the catalog is an editorial
  call, not a validation one.
- **flant** — `blog.flant.ru` is NXDOMAIN because the company rebranded to
  Deckhouse. Its content now lives at `flant.ru/feed/` (still Russian-language,
  company blog, distinct from `deckhouse.io/blog` which is the OSS
  project blog). Kept as a separate entry from `deckhouse` since they are
  different content streams (company news vs. project blog), both pointing at
  `deckhouse.ru`/`flant.ru` domains post-rebrand — not duplicates of each other.
- **ray** and **timescale** — replacement feeds are real and return 200/entries>0,
  but currently carry only **1 entry each** (`ray`: anyscale.com/rss.xml;
  `timescale`: tigerdata.com/blog/rss). Technically OK, just thin — flag for a
  re-check next cycle in case these are truncated/broken feeds rather than
  genuinely low-volume.
- **k8s-gateway** and **kubesphere** — both replacement/existing feeds return
  entries but **every item's publish date is broken** (`0001-01-01`, a
  template bug — for k8s-gateway it's actually the whole docs site dumped as
  one feed, not a blog). These will look "infinitely stale" or "always fresh"
  depending on how the digest's date-window logic treats a missing date —
  needs a code-side fallback, not a feeds.yaml fix. See Stale section.
- **grafana** (kept, not in replacements list — already OK) — feed is fine
  (10 entries) but its `pubDate` lacks a timezone offset
  (`Thu, 27 Aug 2026 13:03:49`), so `feedparser` leaves `published_parsed =
  None`. Newest post manually confirmed 2026-08-27 (fresh). If the digest
  pipeline relies on `feedparser`'s parsed date fields, this source will be
  silently treated as dateless/dropped — needs a `dateutil` fallback parse.

## Remove

Dead, no working feed found after checking the homepage `<link rel="alternate">`,
all common path patterns (`/feed`, `/rss`, `/rss.xml`, `/feed.xml`, `/atom.xml`,
`/index.xml`, `/blog/rss.xml`, `/blog/index.xml`, etc.), and a web search for a
current blog URL:

| id | old url | reason |
|---|---|---|
| alibaba-cn | https://developer.aliyun.com/rsspage.htm | 404, no feed anywhere; reachable from US egress, not geoblocked |
| bytedance-oss | https://opensource.bytedance.com/blog/rss.xml | React SPA catch-all, identical empty shell for every path, no static feed exists |
| cloudnative-to | https://cloudnative.to/index.xml | **domain has lapsed** — `index.xml` JS-redirects to a GoDaddy "domain for sale" parking page |
| dagger | https://dagger.io/blog.rss | Astro site, no feed link, all patterns 404/500; only `dagger.substack.com/feed` responds and it's frozen with 1 entry from 2022 |
| envoy | https://blog.envoyproxy.io/feed | TLS handshake times out consistently (not a 404) — transient or the host is down from this egress; retry from another network before dropping permanently |
| higress | https://higress.io/blog/index.xml | site migrated `higress.io` → `higress.ai` (Astro/Starlight); ~370 posts exist but no RSS/Atom/sitemap feed found anywhere |
| kyverno | https://kyverno.io/blog/index.xml | site migrated to Astro/Starlight; blog is active at `kyverno.io/blog` but the new site has no RSS/Atom endpoint |
| linkedin-eng | https://www.linkedin.com/blog/engineering/rss | redirects to a feedless page; `/rss` and `/feed` 404 or return HTML with 0 entries |
| loft | https://www.vcluster.com/blog/rss.xml | Loft Labs rebranded to vCluster; `vcluster.com/blog` has no feed link, all common patterns 404 |
| minio | https://blog.min.io/rss/ | `blog.min.io` 301s to `www.min.io/blog`, which has no feed at any common pattern |
| openebs | https://openebs.io/blog/rss.xml | client-rendered Vite/React SPA with catch-all routing, every feed path returns the same empty shell |
| robusta | https://home.robusta.dev/blog/rss.xml | site rebuilt on a JS framework, no feed link in markup, all common patterns 404 |
| tencentcloud | https://cloud.tencent.com/developer/rss | serves the SPA homepage shell (0 entries) for every feed path; reachable from US egress, not geoblocked |
| uber | https://www.uber.com/blog/engineering/rss/ | no feed advertised anymore; `eng.uber.com/feed` and alternate `Accept` headers all fail (406/404) |
| vkcloud | https://cloud.vk.com/blog/rss/ | rebranded `cloud.vk.com` → `cloud.vk.ru`; new blog is a React app with no feed link/endpoint; plain 404, not geoblocked |

Note: `api7`, `devopsish`, `chronosphere`, and `kubeweekly` were previously
listed here in error — see the self-correction note at the top of this
report and the Replacements section above; all four have working feeds and
have been restored to `feeds.yaml`.

## Stale

Feed works (HTTP 200, feedparser parses, entries present) but newest entry is
older than 120 days — **keep**, but flagged:

| id | url (current, post-fix where applicable) | newest entry | age (days) | note |
|---|---|---|---|---|
| oci | https://opencontainers.org/index.xml | 2026-04-06 | 154 | genuinely quiet — spec-maintenance foundation, low cadence is normal |
| backstage | https://backstage.io/blog/rss.xml | 2026-04-20 | 140 | genuinely quiet — matches homepage |
| kubeedge | https://kubeedge.io/blog/rss.xml (fixed URL) | 2026-04-21 | 139 | project posts rarely |
| cloudflarelearn | https://www.agwa.name/blog/feed (fixed URL) | 2026-04-29 | 131 | genuinely quiet; **catalog id is misleading — this is Andrew Ayer's personal blog, not Cloudflare** |
| changelog | https://changelog.com/news/feed | 2026-04-29 | 131 | genuinely quiet — matches homepage |
| cloudwego | https://www.cloudwego.io/index.xml (fixed URL) | 2026-05-08 | 122 | low cadence, matches homepage |
| earthly | https://earthly.dev/blog/feed.xml | 2026-03-09 | 182 | genuinely quiet; company posted a "Shutting Down Earthfiles Cloud" notice Apr 2025 — possible pivot/wind-down, worth re-checking relevance next cycle |
| jepsen | https://jepsen.io/blog.atom (fixed URL) | 2026-03-26 | 165 | low cadence, feed now merges blog+analyses |
| opa | https://www.openpolicyagent.org/blog/rss.xml (fixed URL) | 2025-08-20 | 383 | blog inactive for over a year |
| buildkite | https://buildkite.com/blog.atom (fixed URL) | 2025-12-01 | 280 | low cadence |
| brendangregg | https://www.brendangregg.com/blog/rss.xml | 2026-02-06 | 213 | genuinely quiet — matches homepage |
| mattklein | https://mattklein123.dev/atom.xml (fixed URL) | 2024-04-24 | 866 | blog inactive since Apr 2024 |
| rachelbythebay | https://rachelbythebay.com/w/atom.xml | 2023-10-12 | 1060 | **feed is broken, blog is not**: homepage shows posts through 2026-07-09, but the atom feed is stuck with a single entry from 2023. No alternate feed found. Site also aggressively rate-limits automated fetches (429s on repeated requests). Needs a scraper-based workaround, not an RSS fix, if this source matters. |
| k8s-gateway | https://gateway-api.sigs.k8s.io/index.xml (fixed URL) | — (dates broken, all `0001-01-01`) | n/a | not a real blog — it's the whole docs site dumped as one feed; entries carry no publish date at all |
| kubesphere | https://kubesphere.io/blogs/index.xml | — (dates broken, all `0001-01-01`) | n/a | **project appears dormant**: real last post per homepage inspection is 2026-06-03, with only one post since 2022; the feed's `pubDate` field is a template bug and always reads year 0001 |
| kubeweekly | https://www.cncf.io/feed/?post_type=lf_kubeweekly (fixed URL) | 2025-05-30 | 465 | **frozen archive, will never update**: newest/only-recent entry is issue #434, "This isn't goodbye… it's just the beginning" — CNCF's own announcement that KubeWeekly was discontinued and folded into a signup-only newsletter. Feed is real and returns entries, but nothing new will ever appear here. Restored to `feeds.yaml` per validation scope, but worth an editorial call on whether to keep a source that can only ever be stale. |

## Geoblocked

**None found.** Every feed that returned 403 in the initial pass was
re-checked; all three Chinese-region candidates that might have looked
geoblocked turned out to be plain 404s / empty SPA shells reachable fine from
this (US) egress, not region blocks:

- `alibaba-cn` (developer.aliyun.com) — 404, not geoblocked
- `tencentcloud` (cloud.tencent.com) — SPA shell, not geoblocked
- `vkcloud` (cloud.vk.ru) — 404, not geoblocked

No InfoQ China / OSChina-style mirror situation arose — `infoq-cn` and
`oschina` themselves were both already OK in the original catalog (200,
fresh entries, no blocking observed).

## Reddit

Method: `https://www.reddit.com/r/<name>/top.rss?t=week` with the same
browser UA, sequential requests with backoff (Reddit rate-limits concurrent
`.rss` fetches aggressively — the JSON API note in community.yaml is correct,
and it turns out `.rss` isn't fully exempt from rate limiting either, just
from the outright 403 the JSON API gives).

`community.yaml` lists **28** subreddits.

**27 of 28 confirmed working** — HTTP 200 with real feed content (3–90 KB
response bodies, i.e. real items, not empty stubs):

kubernetes, devops, sre, platform_engineering, docker, terraform, aws, AZURE,
googlecloud, openshift, selfhosted, homelab, sysadmin, networking, linux,
linuxadmin, ExperiencedDevs, dataengineering, LocalLLaMA, rust, golang,
postgres, ceph, opensource, Proxmox, netsec, devopsish — all exist and
returned content. (`devopsish` and `ceph` exist as subreddits, distinct from
the `devopsish`/`ceph` **blog** feed ids in feeds.yaml.)

**1 unresolved: `kubernetes_ops`** — could not be confirmed either way from
this egress. What was actually observed:

| probe | `kubernetes_ops` | control: `kubernetes` | control: nonexistent sub |
|---|---|---|---|
| `top.rss?t=week` | 429 on every attempt (4 tries w/ 8–32s backoff, then 6 more w/ 30s backoff) | 200, 25 entries | **404** |
| `new.rss` | 429-persist (6 tries) | — | — |
| `about.json` | 403 (JSON API blocks datacenter egress generally) | — | — |
| `reddit.com/r/<name>/` HTML | 200, generic 8414-byte JS shell | — | 200, **same** generic 8424-byte shell |
| `old.reddit.com/r/<name>/` | redirected to login | redirected to login | redirected to login |

Two things this rules out, and one it doesn't:

- **Not simply our IP being rate-limited.** `kubernetes` returned 200 in the
  *same interleaved run* in which `kubernetes_ops` 429'd six times — the
  throttling is specific to this subreddit, not blanket egress throttling.
- **Not confirmed to exist by the HTML page.** A 200 on the HTML URL proves
  nothing: Reddit serves a near-identical generic shell (8414 vs 8424 bytes)
  for a subreddit name invented for this test. Any claim of existence based
  on that 200 is unsound.
- **Still unknown whether it exists.** The one probe that *does*
  discriminate — `.rss` — returns 404 for a nonexistent sub but never
  returned 404 here, only 429. That weakly suggests the name resolves to
  something real but feed-restricted; it is not proof. `old.reddit` and
  `about.json` are both unusable from this egress.

Practical consequence either way: **`kubernetes_ops` will yield zero items in
the digest** as long as its `.rss` returns 429. Recommend pulling it once,
isolated in time from the other 27, from the production egress; if it still
429s there, drop it — the catalog already covers the topic via `kubernetes`
and `devops`.

**No subreddit was found to be nonexistent or private.** 27 of the 28
configured names are confirmed real and public; the 28th is unresolved as
described above rather than confirmed either way.

---

# Addendum — full sweep of the grown catalog (445 feeds)

The body of this report covers the 184-feed scope. Since `feeds.yaml` kept growing
during the review, I ran the same validation over the **current 445-entry file** so the
~140 later-added feeds are not shipped unvalidated. Same method (browser UA, 20s timeout,
redirects followed, `feedparser`, 120-day stale threshold). Snapshot taken at 445 entries;
raw data in `.validation.json`.

## Addendum summary

| Classification | Count |
|---|---|
| OK | 413 |
| STALE (>120d) | 23 |
| DEAD | 3 |
| EMPTY | 1 |
| GEOBLOCKED (403) | 1 |
| **Total** | **441** (sweep snapshot; 4 more entries were added while it ran) |

Every id in the 184-feed scope that this report marks as fixed came back OK in this sweep,
so the replacement URLs hold up on a second independent pass.

## New findings not in the main report

**1. `lemire` — 403 is a User-Agent block, NOT geoblocking. This is the actionable one.**

`https://lemire.me/blog/feed/` returns **403 with the digest's own User-Agent**
(`kuberpodcast-digest/1.0`) and **200 with 40 fresh entries** (newest 2026-09-05) using a
normal Chrome UA. Same IP, same second — the only variable is the UA string. The host is
filtering on the bot-identifying UA.

This matters beyond one feed: the project's UA string is *itself* a source of failures, and
any other WAF-fronted host may do the same silently. Options: send a browser-like UA
(dropping the courteous bot identifier), or keep the polite UA and accept losing these
sources. Worth a deliberate decision rather than discovering it per-feed.

**2. `cisecurity` — configured URL is not a feed at all (added by another reviewer).**

`https://www.cisecurity.org/feed` returns 200 but the body is a 238-byte **Sitecore
redirect stub** (`<html><head><title>Object moved</title>...`), so it parses to 0 entries.
`/feed/` is identical; `/insights/blog/rss.xml` 404s; `/insights/feed` returns 247 KB of
HTML (a rendered page, `Content-Type: text/html`), also 0 entries. No working feed found —
**remove unless someone can produce a real CIS feed URL.**

**3. `netflix` — transient, not dead. Do not remove.**

`https://netflixtechblog.com/feed` timed out during the bulk sweep and was classified DEAD,
but two isolated retries (20s and 45s timeouts) both returned **200 with 10 entries**,
newest 2026-08-28. Medium-hosted feeds time out under parallel load. This is a lesson for
the fetcher generally: **a single timeout must not be treated as a dead feed** — retry
serially before dropping anything. `envoy` is the opposite case: it failed on 10+ attempts
across an hour at both 20s and 45s, so its DEAD classification stands.

**4. Additional STALE feeds among the later-added sources** (all work, just old):

| id | url | age |
|---|---|---|
| google-security | https://security.googleblog.com/feeds/posts/default | 136d |
| koordinator | https://koordinator.sh/zh-Hans/blog/rss.xml | 144d |
| nelhage | https://blog.nelhage.com/atom.xml | 168d |
| moelove | https://moelove.info/rss.xml | 196d |
| starrocks | https://www.starrocks.io/blog/rss.xml | 131d |
| cncf-tag-sec | https://tag-security.cncf.io/index.xml | 337d |
| easyperf | https://easyperf.net/feed.xml | 665d |
| brauner | https://people.kernel.org/brauner/feed/ | 1285d |
| travisdowns | https://travisdowns.github.io/feed.xml | 1908d |

`brauner` and `travisdowns` are effectively abandoned (3.5 and 5 years); `easyperf` nearly
two years. Whoever added them should confirm they are wanted before the first run.

**5. `deckhouse` is still missing from `feeds.yaml`.**

The Replacements section lists `deckhouse -> https://deckhouse.ru/blog/feed/` (verified:
200, 10 entries, newest 2026-09-07), but the id is **not present in the current file** —
only `flant` was restored. `flant.ru/feed/` (company blog) and `deckhouse.ru/blog/feed/`
(product blog) are different content streams; both were verified working. Add `deckhouse`
back.

## `kubernetes_ops` — independent confirmation of the control table

I reproduced the Reddit control experiment separately, all three probes in one run with
identical pacing (90s backoff, 60s between subreddits), after a 4-minute cool-off:

| probe | result |
|---|---|
| `r/kubernetes/.rss` (real sub, control) | **200**, 25 entries, feed title "Kubernetes" |
| `r/thissubdoesnotexist99xyz/.rss` (nonexistent, control) | **404**, 517 bytes, "reddit.com: page not found" |
| `r/kubernetes_ops/.rss` | **429 on all 4 attempts** — never a 404 |

This confirms the main report's reading and sharpens it: the nonexistent control returned a
clean 404 *in the same run at the same pacing*, so the 429 on `kubernetes_ops` is not
generic throttling — a nonexistent name would have 404'd. The name resolves to something
Reddit will not serve a feed for. That is consistent with a real-but-restricted subreddit,
but it is **not** proof of existence, and I am not claiming it either way.

Operationally the conclusion is the same regardless: `kubernetes_ops` yields zero items
while its `.rss` returns 429, so it contributes nothing to the digest as configured.

## One method note for the fetcher

Reddit rate-limits hard. A 10-worker parallel sweep of the 28 subreddits produced **1 × 200
and 27 × 429**; the same list run sequentially with ~5s spacing produced 27 × 200. If the
production fetcher pulls subreddits concurrently it will silently lose most of them — the
failure looks like "quiet week on Reddit", not like an error. Pace it sequentially.
