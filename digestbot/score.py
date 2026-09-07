"""Scoring, clustering, section routing and quota-based selection.

Implements the formula from sources/review-5-editorial.md §2:

    base  = 26*TOP + 20*SRC + 18*ENG + 14*FORM + 12*ORIG + 10*REC
    final = (base + BONUS) * cluster_decay * entity_mult * domain_mult - PENALTY
"""
from __future__ import annotations

import hashlib
import logging
import math
import re
import unicodedata
from collections import defaultdict
from datetime import datetime, timedelta

log = logging.getLogger("digestbot.score")

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with", "at", "by",
    "from", "as", "is", "are", "was", "were", "be", "been", "it", "its", "that",
    "this", "new", "using", "use", "we", "our", "you", "your", "how", "why", "what",
    "into", "about", "via", "not", "can", "will", "has", "have", "more", "than",
    "и", "в", "на", "с", "по", "для", "как", "что", "не", "из", "к", "о", "за",
    "это", "мы", "все", "при", "или", "но", "его", "их",
}
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF️⬀-⯿]"
)
VERSION = re.compile(r"\bv?(\d+)\.(\d+)(?:\.\d+)?(?:[-.](?:rc|beta|alpha)[-.]?\d*)?\b", re.I)


# ── normalisation ────────────────────────────────────────────────────────────

def norm_title(t: str) -> str:
    t = unicodedata.normalize("NFKC", t or "").lower()
    t = EMOJI.sub(" ", t)
    t = re.sub(r"^\s*(show|ask|tell) hn:\s*", "", t)
    t = re.sub(r"^\s*\[[^\]]{1,20}\]\s*", "", t)
    if len(t) > 45:
        t = re.split(r"\s+[|–—]\s+", t)[0]
    t = re.sub(r"[^\w\s.]", " ", t, flags=re.UNICODE)
    return " ".join(w for w in t.split() if w not in STOPWORDS)


def shingles(text: str, n: int = 3) -> frozenset[str]:
    words = text.split()
    if len(words) < n:
        n = 2
    if len(words) < n:
        return frozenset(words)
    return frozenset(" ".join(words[i:i + n]) for i in range(len(words) - n + 1))


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def simhash64(text: str) -> int:
    """Cheap 64-bit simhash over word 3-grams, used for cross-week similarity."""
    vec = [0] * 64
    for sh in shingles(text) or {text}:
        h = int(hashlib.md5(sh.encode("utf-8", "replace")).hexdigest()[:16], 16)
        for i in range(64):
            vec[i] += 1 if (h >> i) & 1 else -1
    out = 0
    for i, v in enumerate(vec):
        if v > 0:
            out |= 1 << i
    return out


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def entity_of(item: dict, vocab: list[str]) -> str:
    """(project, major.minor) — the key that stops one release arc eating the digest."""
    if item.get("release"):
        repo = item["release"]["repo"]
        project = repo.split("/")[-1].lower()
        m = VERSION.search(item["release"].get("tag", ""))
        return f"{project}@{m.group(1)}.{m.group(2)}" if m else project

    text = f"{item.get('title','')} {item.get('summary','')[:300]}".lower()
    found = None
    for name in vocab:
        if re.search(rf"\b{re.escape(name)}\b", text):
            found = name
            break
    if not found:
        return ""
    m = VERSION.search(item.get("title", ""))
    return f"{found}@{m.group(1)}.{m.group(2)}" if m else found


def build_vocab(feeds: list[dict], repos: dict) -> list[str]:
    """Controlled project vocabulary, longest first so `cluster-api` wins over `api`."""
    vocab = set()
    for group in repos.values():
        for entry in group.get("list", []):
            repo = entry["repo"] if isinstance(entry, dict) else entry
            vocab.add(repo.split("/")[-1].lower())
    for f in feeds:
        vocab.add(f["id"].lower().replace("-", ""))
    return sorted((v for v in vocab if len(v) >= 4), key=lambda v: (-len(v), v))


# ── component scores ─────────────────────────────────────────────────────────

def top_score(item: dict, filters, cfg: dict) -> float:
    text = f"{item.get('title','')} {item.get('summary','')[:600]} {(item.get('body') or '')[:1500]}"
    a, b, c = filters.tier_hits(text)
    ts = cfg["tier_scores"]
    return min(1.0, ts["a"] * a + ts["b"] * b + ts["c"] * c)


def src_score(item: dict) -> float:
    kind = item.get("source_kind")
    if kind == "hn":
        return 0.60
    if kind == "lobsters":
        return 0.55
    if kind == "devto":
        return 0.20
    if kind == "release":
        stars = (item.get("release") or {}).get("stars", 0) or 0
        return max(0.0, min(1.0, 0.45 + 0.15 * math.log10(1 + stars / 1000)))
    return max(0.0, min(1.0, (float(item.get("source_weight", 2)) - 1) / 4.0))


def _log_ratio(value, ceiling) -> float:
    return math.log10(1 + max(0, value or 0)) / math.log10(1 + ceiling)


def eng_score(item: dict, cfg: dict) -> float:
    e = item.get("engagement", {})
    scores = [cfg["eng_floor"]]

    if e.get("hn_points") or e.get("hn_comments"):
        scores.append(min(1.0, 0.6 * _log_ratio(e.get("hn_points"), 800)
                          + 0.4 * _log_ratio(e.get("hn_comments"), 400)))
    if e.get("reddit_score") or e.get("reddit_comments"):
        w = float(item.get("source_weight", 3))
        scores.append(min(1.0, (0.7 * _log_ratio(e.get("reddit_score"), 2500)
                                + 0.3 * _log_ratio(e.get("reddit_comments"), 500))
                          * (0.6 + 0.08 * w)))
    elif e.get("reddit_rank"):
        # RSS fallback: only rank is observable inside the weekly top listing.
        scores.append(min(1.0, max(0.15, 0.95 - 0.03 * e["reddit_rank"])))
    if e.get("lobsters_score"):
        scores.append(min(1.0, 0.7 * _log_ratio(e.get("lobsters_score"), 180)
                          + 0.3 * _log_ratio(e.get("lobsters_comments"), 120)))
    if e.get("devto_reactions"):
        scores.append(min(1.0, _log_ratio(e.get("devto_reactions"), 900)))
    if item.get("release"):
        stars = (item.get("release") or {}).get("stars", 0) or 0
        scores.append(min(1.0, 0.5 * _log_ratio(e.get("reactions"), 300)
                          + 0.5 * _log_ratio(stars, 60000)))
    return max(scores)


def form_score(item: dict) -> float:
    w = item.get("words", 0)
    if w <= 0:
        w = max(1, len(item.get("summary", "")) // 6)
    f = min(1.0, max(0.0, (math.log(max(w, 1)) - math.log(300))
                     / (math.log(3000) - math.log(300)))) * 0.70
    if item.get("code_blocks", 0) >= 2:
        f += 0.15
    if item.get("has_table"):
        f += 0.15
    if w < 250 and item.get("source_kind") != "release":
        f = min(f, 0.10)
    return min(1.0, f)


AGGREGATE_TITLE = re.compile(
    r"\b(this week in|last week in|weekly|дайджест|round-?up|links? of the week|"
    r"issue #?\d+)\b", re.I)


def orig_class(item: dict) -> str:
    if item.get("category") == "newsletter" or AGGREGATE_TITLE.search(item.get("title", "")):
        return "aggregate"
    if item.get("source_kind") == "release":
        return "primary"
    if item.get("category") in ("foundation", "project", "person"):
        return "primary"
    if item.get("category") in ("vendor", "cloud"):
        # A vendor writing about its own product on its own domain is primary.
        return "primary" if item.get("source_kind") == "feed" else "analysis"
    if item.get("category") == "media":
        return "coverage"
    return "analysis"


def rec_score(item: dict, start: datetime, end: datetime, cfg: dict) -> float:
    if item.get("late_arrival"):
        return cfg["late_arrival_rec"]
    pub = item.get("_effective_dt")
    if not pub:
        return cfg["recency_floor"]
    age_h = max(0.0, (end - pub).total_seconds() / 3600)
    span_h = max(1.0, (end - start).total_seconds() / 3600)
    return max(cfg["recency_floor"], min(1.0, 1.0 - 0.6 * (age_h / span_h)))


# ── full score ───────────────────────────────────────────────────────────────

def score_item(item: dict, filters, cfg: dict, start, end, inverted_eng: bool = False) -> dict:
    w = cfg["weights"]
    TOP = top_score(item, filters, cfg)
    SRC = src_score(item)
    ENG = eng_score(item, cfg)
    FORM = form_score(item)
    orig = orig_class(item)
    ORIG = cfg["orig_scores"][orig]
    REC = rec_score(item, start, end, cfg)

    eng_term = (1.0 - ENG) if inverted_eng else ENG
    base = (w["TOP"] * TOP + w["SRC"] * SRC + w["ENG"] * eng_term
            + w["FORM"] * FORM + w["ORIG"] * ORIG + w["REC"] * REC)

    b = cfg["bonus"]
    flags = item.get("flags", {})
    extra_surfaces = max(0, len(set(item.get("surfaces", []))) - 1)
    bonus = min(b["max_surface"], b["per_extra_surface"] * extra_surfaces)
    if item.get("in_newsletter"):
        bonus += b["newsletter_link"]
    if flags.get("security"):
        bonus += b["security"]
    if flags.get("incident"):
        bonus += b["incident"]
    if flags.get("breaking_change"):
        bonus += b["breaking_change"]
    if flags.get("benchmark_numbers"):
        bonus += b["benchmark_numbers"]
    bonus = min(bonus, b["cap"])

    p = cfg["penalty"]
    penalty = 0.0
    if flags.get("vendor_pitch"):
        penalty += p["vendor_pitch"]
    if flags.get("paywalled"):
        penalty += p["paywalled"]
    if flags.get("slop_two_hits"):
        penalty += p["slop_two_hits"]
    if item.get("source_kind") == "devto" and \
            (item.get("engagement", {}).get("devto_reactions") or 0) < 120:
        penalty += p["devto_low_reactions"]
    if item.get("title", "").rstrip().endswith("?") and \
            item.get("source_kind") in ("reddit", "devto"):
        penalty += p["question_title"]
    if flags.get("no_byline_vendor"):
        penalty += p["no_byline_vendor"]
    if flags.get("repeat_cluster"):
        penalty += p["repeat_cluster"]

    item["components"] = {"TOP": round(TOP, 3), "SRC": round(SRC, 3), "ENG": round(ENG, 3),
                          "FORM": round(FORM, 3), "ORIG": ORIG, "REC": round(REC, 3)}
    item["orig_class"] = orig
    item["base"] = round(base, 2)
    item["bonus"] = round(bonus, 2)
    item["penalty"] = round(penalty, 2)
    item["score"] = round(base + bonus - penalty, 2)   # multipliers applied at selection
    return item


# ── clustering ───────────────────────────────────────────────────────────────

def cluster(items: list[dict], cfg: dict) -> dict[str, list[dict]]:
    """Union-find over URL identity, title shingles and (entity, time) pairs."""
    parent = {it["id"]: it["id"] for it in items}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for it in items:
        nt = norm_title(it["title"])
        it["_nt"] = nt
        it["_sh"] = shingles(nt)
        it["_shv"] = shingles(re.sub(r"v?\d+(\.\d+)+", "§", nt))
        it["norm_title_hash"] = hashlib.sha1(nt.encode()).hexdigest()[:16]
        it["simhash"] = simhash64(nt)

    # Bucket by shared shingle so comparisons stay near-linear.
    buckets: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        for sh in sorted(it["_sh"])[:6] or [it["_nt"][:20] or "_"]:
            buckets[sh].append(it)

    th = cfg["cluster"]["title_jaccard"]
    thv = cfg["cluster"]["version_blind_jaccard"]
    for bucket in buckets.values():
        if len(bucket) < 2 or len(bucket) > 120:
            continue
        for i, a in enumerate(bucket):
            for bb in bucket[i + 1:]:
                if jaccard(a["_sh"], bb["_sh"]) >= th or \
                        jaccard(a["_shv"], bb["_shv"]) >= thv:
                    union(a["id"], bb["id"])

    # Same project + same version inside a 96h window is the same story arc.
    window = timedelta(hours=cfg["cluster"]["entity_window_hours"])
    by_entity: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        if it.get("entity") and "@" in it["entity"]:
            by_entity[it["entity"]].append(it)
    for group in by_entity.values():
        group.sort(key=lambda i: i.get("_effective_dt") or datetime.min)
        for i, a in enumerate(group):
            for bb in group[i + 1:]:
                da, db = a.get("_effective_dt"), bb.get("_effective_dt")
                if da and db and abs(db - da) > window:
                    break
                union(a["id"], bb["id"])

    clusters: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        it["cluster_id"] = find(it["id"])
        clusters[it["cluster_id"]].append(it)
        for k in ("_sh", "_shv"):
            it.pop(k, None)

    # Rank inside each cluster and apply the decay.
    decay = cfg["cluster"]["decay"]
    for members in clusters.values():
        members.sort(key=lambda i: -(i["base"] + i["bonus"]))
        for rank, m in enumerate(members):
            m["cluster_rank"] = rank
            m["cluster_decay"] = decay ** rank
    log.info("clustering: %d items -> %d clusters", len(items), len(clusters))
    return clusters


# ── section routing ──────────────────────────────────────────────────────────

def classify(item: dict, filters, ed: dict) -> str:
    flags = item.get("flags", {})
    text = f"{item.get('title','')} {(item.get('body') or item.get('summary',''))[:4000]}"

    if flags.get("security"):
        return "security"
    if flags.get("incident"):
        return "incidents"
    if item.get("source_kind") == "release":
        return "releases"
    if item.get("lang", "en") != "en":
        return "nonenglish"
    if filters.ai_hits(text) >= 2:
        return "ai_infra"
    if filters.ecosystem and filters.ecosystem.search(text):
        return "ecosystem"
    if item.get("novelty") and item["components"]["ENG"] < 0.2:
        return "watchlist"
    longform_min = next((s.get("min_words", 4000) for s in ed["sections"]
                         if s["key"] == "longform"), 4000)
    if item.get("words", 0) > longform_min or item.get("source_kind") in ("talk", "paper"):
        return "longform"
    if item.get("source_kind") in ("hn", "reddit", "lobsters") and item.get("thread_is_canonical"):
        return "community"
    return "deep"


# ── selection ────────────────────────────────────────────────────────────────

def select(items: list[dict], ed: dict) -> tuple[list[dict], list[dict]]:
    """Fill sections under quotas, caps and the protected non-English bucket."""
    cfg = ed["scoring"]
    div = cfg["diversity"]
    threshold = ed["admit_threshold"]
    sections = {s["key"]: s for s in ed["sections"]}
    order = [s["key"] for s in ed["sections"] if not s.get("promotion")]

    entity_count: dict[str, int] = defaultdict(int)
    domain_count: dict[str, int] = defaultdict(int)
    cluster_count: dict[str, int] = defaultdict(int)
    chosen: dict[str, list[dict]] = {k: [] for k in order}
    by_cluster: dict[str, list[dict]] = defaultdict(list)   # index for _adds_angle
    taken: set[str] = set()

    def domain_cap(dom: str) -> int:
        return div["domain_cap_overrides"].get(dom, div["domain_cap"])

    def effective(item: dict) -> float:
        ent_rank = entity_count[item.get("entity", "")] + 1
        dom_rank = domain_count[item.get("domain", "")] + 1
        ent_mult = div["entity_mult"].get(ent_rank, div["entity_mult"].get(4, 0.45))
        dom_mult = 1.0 if dom_rank <= 3 else div["domain_mult_after"]
        return (item["base"] + item["bonus"]) * item.get("cluster_decay", 1.0) \
            * ent_mult * dom_mult - item["penalty"]

    def admissible(item: dict) -> bool:
        if item["id"] in taken:
            return False
        if entity_count.get(item.get("entity", ""), 0) >= div["entity_cap"] and item.get("entity"):
            item["reject"] = "entity_cap"
            return False
        if domain_count[item.get("domain", "")] >= domain_cap(item.get("domain", "")):
            item["reject"] = "domain_cap"
            return False
        if cluster_count[item["cluster_id"]] >= cfg["cluster"]["max_emitted"]:
            item["reject"] = "cluster_sibling"
            return False
        if cluster_count[item["cluster_id"]] == 1 and \
                not _adds_angle(item, by_cluster[item["cluster_id"]]):
            item["reject"] = "cluster_sibling"
            return False
        return True

    def take(item: dict, key: str) -> None:
        item["section"] = key
        item["final"] = round(effective(item), 2)
        chosen[key].append(item)
        by_cluster[item["cluster_id"]].append(item)
        taken.add(item["id"])
        if item.get("entity"):
            entity_count[item["entity"]] += 1
        domain_count[item.get("domain", "")] += 1
        cluster_count[item["cluster_id"]] += 1

    def fill(key: str, pool: list[dict], quota: int) -> int:
        placed = 0
        # Greedy: re-rank after every pick so the diversity multipliers actually bite.
        while placed < quota:
            best, best_val = None, None
            for it in pool:
                if it["id"] in taken or it.get("section_key") != key:
                    continue
                if not admissible(it):
                    continue
                val = effective(it)
                if val < threshold:
                    continue
                if best_val is None or val > best_val:
                    best, best_val = it, val
            if best is None:
                break
            take(best, key)
            placed += 1
        return placed

    # 1. Protected non-English first, honouring its language sub-quotas.
    ne = sections.get("nonenglish")
    if ne:
        subs = ne.get("sub_quotas", {})
        for lang, sub_quota in sorted(subs.items(), key=lambda kv: -kv[1]):
            pool = [i for i in items
                    if i.get("section_key") == "nonenglish" and i.get("lang") == lang]
            placed = 0
            while placed < sub_quota:
                cands = [i for i in pool if i["id"] not in taken and admissible(i)
                         and effective(i) >= threshold]
                if not cands:
                    break
                best = max(cands, key=effective)
                take(best, "nonenglish")
                placed += 1
        # Redistribute the shortfall inside the bucket, never outward.
        fill("nonenglish", items, ne["quota"] - len(chosen["nonenglish"]))

    # 2. Everything else in declaration order.
    for key in order:
        if key == "nonenglish":
            continue
        sec = sections[key]
        fill(key, items, sec["quota"])

    # 3. Spill unmet quota into the permitted sections.
    total = sum(len(v) for v in chosen.values())
    target = ed["target_total"]
    if total < target:
        for key in ed["spill_order"]:
            if total >= target:
                break
            if key in ed.get("no_spill_into", []):
                continue
            got = fill(key, items, target - total)
            total += got

    # 4. Headline is promotion, not selection.
    flat = [i for k in order for i in chosen[k]]
    flat.sort(key=lambda i: -i["final"])
    hq = sections.get("headline", {}).get("quota", 0)
    for i in flat[:hq]:
        i["headline"] = True

    ordered = [(k, chosen[k]) for k in order if chosen[k]]
    leftovers = sorted((i for i in items if i["id"] not in taken),
                       key=lambda i: -(i["base"] + i["bonus"] - i["penalty"]))
    log.info("selection: %d items (%s)", len(flat),
             ", ".join(f"{k}={len(v)}" for k, v in ordered))
    return ordered, leftovers


def _adds_angle(item: dict, siblings: list[dict]) -> bool:
    """A cluster's 2nd member earns a slot only if it says something different:
    another section, a comparable score, and a different kind of source."""
    for other in siblings:
        if other.get("section_key") == item.get("section_key"):
            return False
        if (item["base"] + item["bonus"]) < 0.75 * (other["base"] + other["bonus"]):
            return False
        if other.get("orig_class") == item.get("orig_class"):
            return False
    return True
