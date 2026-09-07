# Review #5 — Editorial / Product

Reviewer scope: not "do the URLs resolve" and not "is the source list complete", but
**does the design of this digest produce a briefing that two experienced infra hosts can
actually use to pick podcast topics in 20 minutes?**

Document language is English (repo convention); the *digest output* language decision is in §4.
Everything below is written to be implemented without further interpretation: quotas, formulas,
regexes, decision functions, reason codes.

Inventory the spec is written against (measured from the drafts):

| Surface | Count | Notes |
|---|---|---|
| `feeds.yaml` | 184 feeds | en 152, ru 13, zh 11, ja 5, ko 2, de 2 |
| by category | vendor 80, project 28, person 19, cloud 19, foundation 13, media 11, community 8, newsletter 7 |
| by weight | w5 ×6, w4 ×41, w3 ×81, w2 ×55, w1 ×2 |
| `community.yaml` | 28 subreddits, 30 HN queries, Lobsters (8 tags), dev.to (7 tags), SO blog |
| `releases.yaml` | ~230 repos in 14 groups |

Realistic raw weekly volume: RSS ≈ 1 400–2 200 items, Reddit ≈ 900–1 500 posts above `min_score`,
HN ≈ 250–500 stories across 30 queries, releases ≈ 250–450 published events (many repos ship 2–5×/week).
**Total ≈ 3 000–4 500 candidates → 100.** That is a ~2.5 % acceptance rate. Precision matters far
more than recall: one piece of SEO slop in the top 20 costs more trust than ten missed items.

---

## 1. The 100-item shape

### 1.1 Two hard critiques before the quotas

1. **100 flat items is the wrong artefact.** Nobody scans 100 equal-looking bullets. The file must be
   *tiered*: a `## Топ-10 недели` block at the top that repeats (by reference) the ten highest-scoring
   entries with a longer comment, then the sectioned 100. Cost: near zero, since it is a re-render of
   items already scored. Without it the deliverable is an archive, not a briefing.
2. **`releases.yaml` tiering is currently inert.** 12 of 14 groups are `tier: 1`, so "tier" carries no
   information and cannot gate anything. It must be replaced by a per-repo `min_bump` (see §3.7 and §7.12),
   otherwise the Releases section will be 18 slots of Prometheus patch releases.

### 1.2 Section structure and quotas (sum = 100)

Section keys are stable identifiers; the renderer emits them in this order.

| # | key | Section (RU heading in output) | Quota | Rationale for a podcast |
|---|---|---|---|---|
| 1 | `headline` | Главное недели | **8** | The stories a listener will already have seen. If the hosts skip them, the episode reads as out of touch. 8 = roughly one per weekday plus two; more than that and "headline" stops meaning anything. |
| 2 | `releases` | Релизы, которые важны | **18** | The single most defensible recurring segment: dated, checkable, listener-actionable ("надо ли нам апгрейдиться"). 18 out of ~300 release events is aggressive filtering and forces the bump-class rules of §3.7 to do real work. |
| 3 | `deep` | Глубокие технические тексты | **16** | The раw material for the long block of the episode — architecture write-ups, benchmarks, migration reports. Largest non-release quota because this is where the hosts' differentiation lives; news anyone can read, analysis they cannot. |
| 4 | `incidents` | Инциденты и постмортемы | **5** | Highest per-item episode value: a real outage is a ready-made 15-minute segment with a narrative arc. Quota is small only because supply is small (and see §7.2 — right now **no source in the drafts reliably produces these**; the quota is a requirement on the source list, not just on the ranker). |
| 5 | `security` | Безопасность и supply chain | **8** | CVEs in k8s/containerd/Cilium force listener action. Separated from `releases` so a critical CVE is never crowded out by a feature release. Again a source gap: §7.1. |
| 6 | `ecosystem` | Экосистема, деньги и управление | **7** | Licence changes, forks, acquisitions, CNCF sandbox/incubation/graduation, project archival, layoffs at a vendor everyone runs. These generate the most listener email and the most opinion — cheap, high-engagement segments. |
| 7 | `community` | Дискуссии | **10** | HN/Reddit/Lobsters threads where the *argument* is the story. The hosts' job is partly to arbitrate community fights; they need the thread, not just the article. |
| 8 | `ai_infra` | AI-инфраструктура | **8** | GPU scheduling, DRA, vLLM/SGLang, inference topology, KV-cache, power/cooling. This is where the audience's budget is moving in 2026. Capped at 8 so the digest does not become an AI newsletter — the corpus (`ai_infra` repo group + `LocalLLaMA` + half of HN) will happily supply 30 if unbounded. |
| 9 | `nonenglish` | Не на английском | **12** | **Explicit quota, filled by construction, never by competition with English items.** 32 of 184 feeds (17 %) are non-English but they will lose every head-to-head fight: no HN points, no Reddit score, lower `ENG`, and machine-translated titles score worse on keyword relevance. Without a reserved bucket the anglosphere firehose deletes them. Sub-quotas: **ru 5, zh 4, ja/ko 2, de 1.** RU is largest because it is directly usable on air without translation; ZH is second because Alibaba/ByteDance/PingCAP publish operational scale reports that have no English equivalent. |
| 10 | `watchlist` | Слабые сигналы | **5** | Deliberately low-engagement: new KEPs, a sandbox project's first release, a spec draft, a 40-star repo doing something structurally new. This is the section that makes the podcast look early. Selected by **inverted** engagement weighting (§2.7). |
| 11 | `longform` | Длинное чтение и доклады | **3** | Jepsen analyses, USENIX/SREcon/KubeCon talk drops, papers. Rarely fresh weekly, so a small quota that spills readily. |
| | | **Total** | **100** | |

### 1.3 Fill, spill and overflow rules (deterministic)

```
QUOTA = {headline:8, releases:18, deep:16, incidents:5, security:8,
         ecosystem:7, community:10, ai_infra:8, nonenglish:12,
         watchlist:5, longform:3}

MIN   = {headline:5, releases:10, deep:10, incidents:0, security:3,
         ecosystem:2, community:5, ai_infra:3, nonenglish:8,
         watchlist:2, longform:0}          # floors that spill may not breach
```

1. Each item is assigned **exactly one** primary section by the classifier in §1.4. Multi-section
   candidates go to the first matching section in this precedence order:
   `incidents > security > releases > nonenglish > ai_infra > ecosystem > watchlist > longform > deep > community > headline`.
   (`headline` is filled *last*, by promotion — see 4.)
2. Fill each section with its top-`QUOTA[k]` items by final score (§2), applying the per-cluster,
   per-domain and per-entity caps of §2.6.
3. **Spill:** if a section yields fewer than `QUOTA[k]` items above the admission floor
   (`final_score >= 45`), the deficit goes to the next sections in this fixed order:
   `deep → releases → community → nonenglish → ai_infra → ecosystem`. Never spill *into* `incidents`,
   `security`, `watchlist` or `headline` (their scarcity is meaningful; padding them lies to the reader).
4. **`headline` is promotion, not selection.** After sections 2–11 are filled, take the 8 highest
   `final_score` items across the whole digest and *reference* them in `headline` with an extended
   comment. They keep their home section (marked `⭐`), so the file still contains exactly 100 unique
   links. Rationale: a headline story is by definition also a release/incident/discussion; duplicating
   the link would waste a slot.
5. **`nonenglish` is protected**: it is filled *before* the English sections and its members are removed
   from the English candidate pool. A non-English item that would also win an English section on merit
   (rare, e.g. a Habr post with 900 HN points) is placed in the English section and the `nonenglish`
   quota is refilled from the next non-English candidate. Sub-quota shortfall inside `nonenglish`
   redistributes ru→zh→ja/ko→de and back, never outward to English.
6. If the total is still < 100 after spill (a genuinely quiet week — August, Christmas), **do not pad**.
   Emit what qualifies, and print in the header: `Отобрано 87 из 100 — порог не понижался.`
   Padding with junk is the failure mode that kills the product in month two.

### 1.4 Section classifier (rule order, first match wins)

```python
def section_of(item):
    if item.kind == "release":                       return "releases"   # unless security below
    if item.security_flag:                           return "security"   # CVE/GHSA/advisory
    if item.incident_flag:                           return "incidents"  # §1.5
    if item.lang != "en":                            return "nonenglish"
    if topic_hits(item, AI_TERMS) >= 2:              return "ai_infra"
    if topic_hits(item, ECOSYSTEM_TERMS) >= 1:       return "ecosystem"
    if item.novelty_flag and item.ENG < 0.2:         return "watchlist"
    if item.words > 4000 or item.kind in ("talk","paper"): return "longform"
    if item.kind in ("hn","reddit","lobsters") and item.canonical_is_thread: return "community"
    return "deep"
```

`security_flag` overrides `releases` — a patch release that fixes a CVE belongs in `security`.

`incident_flag` = title/body matches
`r'\b(post[- ]?mortem|incident report|root cause|rca\b|outage|degraded (service|performance)|service disruption|we (had|experienced) an? (outage|incident)|разбор (инцидента|аварии)|постмортем)\b'`
**and** the publisher is either the affected party (domain matches the product mentioned) or a
recognised status/incident source. Third-party "AWS was down yesterday" news coverage is `ecosystem`,
not `incidents` — the hosts need the RCA, not the headline.

`novelty_flag` = repo stars < 2000, or the source id appeared in ≤ 2 prior digests, or the item is a
KEP/RFC/spec draft.

---

## 2. Scoring

### 2.1 The formula

All components are normalised to `[0,1]`. Base score is `[0,100]`.

```
base = 26*TOP + 20*SRC + 18*ENG + 14*FORM + 12*ORIG + 10*REC

final = (base + BONUS) * cluster_decay * entity_mult * domain_mult - PENALTY

admit if final >= 45
```

Weight rationale, in one line each:
- `TOP` heaviest (26) — relevance to the show's beat is the only thing that cannot be compensated.
- `SRC` (20) — 184 hand-curated feeds are the main prior; the curation must actually drive ranking.
- `ENG` (18) — real but gameable, and it structurally penalises non-English and niche items.
- `FORM` (14) — depth proxy; distinguishes a 300-word announcement from a 3 000-word write-up.
- `ORIG` (12) — primary source beats rewrite; kills the media-echo layer without a blocklist.
- `REC` (10) — deliberately low. Inside a 7-day window, importance ≫ hours.

### 2.2 `SRC` — source weight

```python
SRC = (feed.weight - 1) / 4.0            # weight 1..5  ->  0.00 .. 1.00
```

For surfaces without a `feeds.yaml` entry:

```python
SRC_reddit  = (sub.weight - 1) / 4.0
SRC_hn      = 0.60                        # HN is a surface, not a source; the target's SRC wins if known
SRC_lobsters= 0.55
SRC_devto   = 0.20                        # dev.to is a slop-heavy surface; low prior on purpose
SRC_release = clamp(0.45 + 0.15*log10(1 + stars/1000), 0, 1.0)
```

When an HN/Reddit item points at a domain that *is* in `feeds.yaml`, use that feed's `SRC` — the
discussion is then merged as a signal (§6.4), not scored independently.

### 2.3 `ENG` — community engagement

```python
def eng_hn(points, comments):
    p = log10(1+points)   / log10(1+800)
    c = log10(1+comments) / log10(1+400)
    return min(1.0, 0.6*p + 0.4*c)

def eng_reddit(score, ncomments, sub_weight):
    s = log10(1+score)     / log10(1+2500)
    c = log10(1+ncomments) / log10(1+500)
    return min(1.0, (0.7*s + 0.3*c) * (0.6 + 0.08*sub_weight))   # w5 -> ×1.0, w2 -> ×0.76

def eng_lobsters(score, comments):
    return min(1.0, 0.7*log10(1+score)/log10(1+180) + 0.3*log10(1+comments)/log10(1+120))

def eng_release(reactions, stars):
    return min(1.0, 0.5*log10(1+reactions)/log10(1+300) + 0.5*log10(1+stars)/log10(1+60000))

ENG_FLOOR = 0.15   # RSS-only item with no community surface
ENG = max(ENG_FLOOR, max(all observed surface scores))
```

The floor is load-bearing: without it, `rachelbythebay`, `jepsen.io`, `lwkd.info` and every Chinese feed
score 0 on 18 points and never appear. Comment weight is high relative to points because for podcast
prep a 300-comment/80-point argument is worth more than a 900-point/12-comment link.

Multi-surface merging is **additive and capped** — see `BONUS` in §2.8.

### 2.4 `REC` — recency inside the window

```python
age_h = (window_end - effective_date).total_seconds()/3600   # 0..168
REC   = clamp(1.0 - 0.6*(age_h/168.0), 0.4, 1.0)
```

Monday's news keeps 40 % of the recency term; it does not get deleted for being Monday.
Special case: items with `late_arrival` (§5.4) get `REC = 0.45` flat.

### 2.5 `TOP` — topic relevance

Three keyword tiers, matched case-insensitively against `title + summary + first 1500 chars of body`,
counting **distinct** terms only (repetition earns nothing).

```python
TIER_A = 0.35   # core beat
TIER_B = 0.18   # adjacent infra
TIER_C = 0.07   # general engineering
TOP = min(1.0, 0.35*a_hits + 0.18*b_hits + 0.07*c_hits)
```

```yaml
tier_a: [kubernetes, k8s, kubelet, kube-apiserver, etcd, containerd, cri-o, runc, kubevirt,
         cilium, ebpf, calico, istio, envoy, linkerd, "gateway api", "service mesh", cni, csi, cri,
         argo cd, argocd, flux, helm, crossplane, operator, crd, controller, "control plane",
         terraform, opentofu, pulumi, prometheus, opentelemetry, otel, grafana, loki, victoriametrics,
         karpenter, cluster-api, "cluster api", talos, k3s, k0s, openshift, rancher, harvester,
         "bare metal", "bare-metal", scheduler, "node pool", kubeadm, "dra", "device plugin",
         "topology manager", cgroup, cgroups, namespace isolation, "admission webhook", kyverno,
         gatekeeper, opa, falco, sigstore, cosign, slsa, sbom, "supply chain",
         postmortem, "root cause", outage, "incident review", multi-tenant, multi-tenancy]
tier_b: [postgres, postgresql, cloudnative-pg, kafka, clickhouse, valkey, redis, ceph, rook, longhorn,
         minio, velero, restic, nats, vitess, tidb, "linux kernel", systemd, io_uring, nvme, rdma,
         wasm, wasmtime, firecracker, gvisor, kata, "kvm", qemu, proxmox, openstack, "finops",
         "cost optimization", "capacity planning", "chaos engineering", "load balanc", bgp, vxlan,
         "srv6", "dpdk", "sr-iov", nixos, "immutable os", "gpu", "cuda", nvlink, infiniband,
         vllm, sglang, kserve, ray, "inference", "kv cache", "model serving", "batch scheduling"]
tier_c: [observability, sre, "platform engineering", devops, "developer experience", ci/cd,
         "on-call", sla, slo, "error budget", microservices, "distributed systems", benchmark,
         latency, throughput, migration, "open source", governance, license]
```

Hard relevance gate: `TOP < 0.20` → drop with reason `off_topic`, regardless of engagement.
This is what keeps `r/linux` at 300 upvotes about a desktop theme out of the file.

### 2.6 `FORM` and `ORIG` (require full-text fetch — see §7.5)

```python
def form(item):
    w = item.words
    f = clamp((log(max(w,1)) - log(300)) / (log(3000) - log(300)), 0, 1) * 0.70
    if item.code_blocks >= 2:                    f += 0.15
    if item.has_table or item.has_chart or item.has_diagram: f += 0.15
    if w < 250 and item.kind != "release":       f  = min(f, 0.10)
    return min(1.0, f)

ORIG = {
  "primary":   1.00,   # project blog, own release, own postmortem, foundation, spec author
  "analysis":  0.70,   # independent deep analysis of someone else's thing (Jepsen, LWN on a kernel patch)
  "coverage":  0.40,   # TNS/InfoQ/Register/Phoronix reporting an announcement
  "aggregate": 0.10,   # newsletter issue, "this week in X" round-up, link dump
}
```

`ORIG` classification rule (no ML needed):
`primary` if `item.domain` is the project's/vendor's own domain **or** `kind == "release"` **or**
`category in (foundation, project, person)`;
`aggregate` if `category == newsletter` or title matches `r'\b(this week in|weekly|дайджест|round-?up|links? of the week)\b'`;
`coverage` if `category in (media,)` and the body contains an outbound link to a `primary` domain in
the first 3 paragraphs; else `analysis`.

**Newsletters should almost never be emitted as items** (`ORIG=0.10` guarantees a low score) — they are
*discovery* inputs. See §7.4; this is the highest-leverage change in the whole design.

### 2.7 `watchlist` inverted scoring

For candidates classified `watchlist`, replace the `ENG` term:

```
base_watchlist = 26*TOP + 20*SRC + 18*(1 - ENG) + 14*FORM + 12*ORIG + 10*REC
```

so that the *least* discussed genuinely novel items surface. Additional gate: `TOP >= 0.35` and
`ORIG == "primary"`, otherwise obscure junk floods this section.

### 2.8 `BONUS` (additive, hard-capped at +14 total)

```python
BONUS  = 0
BONUS += min(8, 3.5 * n_extra_surfaces)          # story appeared on HN *and* Reddit *and* Lobsters
BONUS += 6  if item.url in newsletter_links      # KubeWeekly/LWKD/DevOps'ish/SRE Weekly linked it (§7.4)
BONUS += 5  if item.security_flag
BONUS += 5  if item.incident_flag
BONUS += 4  if breaking_change_flag              # 'breaking change|action required|deprecat|removed in'
BONUS += 3  if item.has_benchmark_numbers
BONUS  = min(BONUS, 14)
```

Cap exists so a single viral story cannot buy its way to the top through surface count alone.

### 2.9 `PENALTY` (additive, subtracted after multipliers)

```python
PENALTY  = 0
PENALTY += 20 if vendor_pitch_flag        # §3.2 soft signals, hard ones are drops
PENALTY += 25 if paywalled                # unless SRC == 1.0
PENALTY += 15 if slop_phrase_hits == 2    # 3+ is a drop, §3.5
PENALTY += 12 if item.kind == 'devto' and item.reactions < 120
PENALTY += 10 if title_is_question and item.kind in ('reddit','devto')
PENALTY += 10 if no_author_byline and category == 'vendor'
PENALTY += 30 if cluster_sibling_emitted_previous_week and not has_new_facts   # §6.6
```

### 2.10 Anti-clustering: detection and slot allocation

**Detection.** Build clusters with union-find over pairs matched by *any* of:

```
(a) identical canonical_url_hash                                   -> same
(b) item_A.canonical_url == item_B.outbound_target                 -> same  (HN/Reddit -> article)
(c) jaccard(shingles3(norm_title_A), shingles3(norm_title_B)) >= 0.55
(d) jaccard >= 0.35  AND  entity_tuple_A == entity_tuple_B  AND  |Δpublished| <= 96h
(e) cosine(embed_A, embed_B) >= 0.86                               (optional, if embeddings available)
```

- `norm_title` = lowercase → strip emoji → strip trailing site name after ` | `, ` — `, ` – `, ` :: `
  → strip leading `[…]`/`Show HN:`/`Ask HN:` → collapse whitespace → drop stopwords.
- `shingles3` = set of word 3-grams.
- `entity_tuple` = (canonical project name from a controlled vocabulary built from `releases.yaml`
  repo names + `feeds.yaml` ids, normalised version string). E.g. `("cilium","1.19")`.
  Version normalisation: `v1.19.0`, `1.19`, `1.19.0-rc.2` → `1.19`.
- Implementation: MinHash(128 permutations) + LSH banding (16 bands × 8 rows) to get candidate pairs
  in O(n), then exact Jaccard on candidates only. At n≈4 000 this runs in under a second.

**Slot allocation.** Inside each cluster, sort members by `base + BONUS` descending, then:

```python
for i, member in enumerate(cluster.sorted_members):
    member.cluster_decay = 0.45 ** i        # 1.00, 0.45, 0.20, 0.09, ...
cluster.max_emitted = 2
# the 2nd member is emitted only if it adds a distinct angle:
#   member[1].section != member[0].section
#   AND member[1].final >= 0.75 * member[0].final
#   AND member[1].ORIG != member[0].ORIG        (e.g. release + independent benchmark)
# otherwise members[1:] are attached as `Ещё:` links under member[0] and consume no slot.
```

**Entity-level diversity** (the "one big story eats 12 slots" guard, one level above clusters —
different clusters can still be the same story arc):

```python
entity_mult = 1.0 if entity_rank <= 2 else (0.70 if entity_rank == 3 else 0.45)
# entity_rank = position of this item among already-selected items sharing the primary entity
# hard cap: max 4 items per primary entity per digest; the 5th is dropped (reason: entity_cap)
```

**Domain diversity:**

```python
domain_mult = 1.0 if domain_rank <= 3 else 0.60
DOMAIN_CAP = 4          # 6 for kubernetes.io, cncf.io, github.com (github.com counts per-repo, not per-host)
AUTHOR_CAP = 3
```

Selection is greedy over the globally sorted candidate list, recomputing `entity_rank`/`domain_rank`
after each pick — not a single sort pass. Ties broken by (higher `ORIG`, then earlier `published`).

---

## 3. Noise filters

Every drop is logged with a reason code into `digest/<date>-rejected.md` (§7.15). Filters run in this
order; the first hard match short-circuits.

Regexes are Python, `re.IGNORECASE | re.UNICODE`, applied to the **title** unless stated otherwise.

### 3.1 SEO listicles / slop titles — HARD DROP (`seo_listicle`)

```python
SEO_DROP = [
  r'^\s*(the\s+)?(top|best)\s+\d{1,3}\b',
  r'\b(top|best)\s+\d{1,3}\s+\w+.{0,60}\b20\d\d\b',
  r'\b\d{1,3}\s+(best|top|essential|must[- ](know|have|read)|awesome|amazing|powerful)\b',
  r'\b(ultimate|complete|definitive|comprehensive|only)\s+(guide|tutorial|handbook|checklist)\b',
  r'\b(a\s+)?(beginner|newbie|noob|dummies)(\'?s)?\s+(guide|intro|introduction)\b',
  r'\bfor\s+(beginners|dummies|newbies)\b',
  r'\b(getting started|step[- ]by[- ]step|from scratch|zero to hero|crash course|cheat[- ]?sheet)\b',
  r'\b(what|why|how)\s+is\s+\w+\s*\??$',
  r'\b(kubernetes|docker|devops|terraform|linux)\s+(101|basics|fundamentals|tutorial)\b',
  r'\b(day|week)\s?[-–]?\s?\d{1,3}\s+of\b',
  r'\b\d{2,3}\s?days?\s+of\s+\w+',
  r'\b(explained (simply|in \d+ minutes)|in\s+5\s+minutes|tl;?dr guide)\b',
  r'\b(everything you need to know|all you need to know)\b',
  r'\b(vs\.?|versus)\b.{0,30}\b(which (one )?(should you|to) (choose|use|pick))\b',
]
```

Structural companions (any two → drop, one → `PENALTY += 15`):
- H2 headings are all of the form `1. X`, `2. X`, … and count between 5 and 15;
- ≥ 60 % of H2 sections are 60–160 words (uniform section length is the content-farm fingerprint);
- body contains a "Conclusion"/"Final Thoughts"/"Wrapping Up" H2 **and** zero code blocks;
- outbound links point only to the author's own domain or to vendor landing pages.

Soft: `r'\bpart\s+\d+\s*(of|/)\s*\d+\b'` — **not** a drop (legit series exist), but `PENALTY += 8`
and dedupe against earlier parts by title stem across 8 weeks.

### 3.2 Vendor press releases / marketing — HARD DROP or heavy penalty

Hard drop (`vendor_pr`):

```python
PR_DROP = [
  r'\b(named|recognized|positioned) (a|as) .{0,40}\b(leader|visionary|challenger)\b',
  r'\b(magic quadrant|forrester wave|gartner peer insights|idc marketscape)\b',
  r'\b(webinar|register (now|today)|save your seat|reserve your spot|book a demo|free trial|
      sign up (today|now)|join us (live|for a)|watch on[- ]demand)\b',
  r'\b(sponsor(ed|ship)?|call for (papers|proposals|speakers)|cfp (is )?(open|closes)|
      early[- ]bird|ticket(s)? (are )?(now )?(on sale|available)|diamond sponsor)\b',
  r'\b(now available (on|in) the (aws|azure|google cloud|gcp) marketplace)\b',
  r'\b(achieves|earns|receives) \b(soc ?2|iso ?27001|fedramp|hipaa|pci ?dss)\b.{0,20}(compliance|certification)\b',
  r'\b(customer (story|success)|case study|testimonial)\b',
  r'^\s*press release\b',
]
PR_DOMAINS = {prnewswire.com, businesswire.com, globenewswire.com, einpresswire.com,
              accesswire.com, newswire.com, prweb.com, openpr.com}
```

Structural PR detection (body; **2+ signals → drop**, 1 signal → `vendor_pitch_flag`, `PENALTY += 20`):
1. Contains a boilerplate closer: `r'\bAbout\s+[A-Z][\w .&-]{2,30}\s*$'` as an H2 in the last 25 % of the body.
2. Contains `r'\b(media|press) (contact|inquiries)\b'` or `r'\bFor more information,? visit\b'`.
3. ≥ 3 attributed quotes: `r'[,"”]\s*(said|says|according to)\s+[A-Z][a-z]+ [A-Z]'` and < 2 code blocks.
4. Word count < 350 **and** the final paragraph contains a CTA link to a pricing/demo/signup path
   (`/pricing`, `/demo`, `/signup`, `/contact-sales`, `/get-started`, `/trial`).
5. First-person plural announcement opener with no technical noun in the first 200 chars:
   `r"\bwe(’|')?re (excited|thrilled|proud|pleased|happy) to announce\b"` and `TOP < 0.30`.

Note: `we're excited to announce` alone is **not** a drop — real projects announce real releases that
way. It only fires combined with low `TOP`.

Funding / acquisition items (`r'\b(raises|secures|closes|lands) \$?\d+(\.\d+)?\s?(m|mm|million|b|billion)\b'`,
`r'\b(acquir|acquisition|merges? with|to buy)\b'`) are **not** dropped — they are routed to `ecosystem`.

### 3.3 Beginner content — HARD DROP (`beginner`)

Beyond the title regexes in 3.1:

```python
BEGINNER_BODY = [
  r'\bin this (article|tutorial|post),? (you|we) will learn\b',
  r'\bprerequisites?:\s*(basic|a basic|some) (knowledge|understanding|familiarity)\b',
  r'\bif you(\'re| are) new to\b',
  r'\bbefore we (dive in|begin|start),? let(\'s| us) (understand|define) what\b',
  r'\bwhat (is|are) (a )?(pod|container|namespace|deployment|service)s?\?',
]
```

Concept-density heuristic:
```python
tier_a_tokens_per_1000w = 1000 * count_distinct(TIER_A ∪ TIER_B, body) / max(words,1)
if tier_a_tokens_per_1000w < 4 and item.kind not in ("release","reddit","hn"): drop("beginner")
```

Demo-only code heuristic: if every code block matches only
`r'kubectl (run|create deployment|expose) .*(nginx|hello-world|busybox|httpd)'` or
`r'FROM (node|python):\d'`-style toy Dockerfiles, and no manifest contains a CRD/`apiVersion:` outside
`v1|apps/v1` → drop.

Exception: `iximiuz`, `learnk8s`, `jvns` are pedagogical *by design* and often deep. Whitelist their
feed ids from the concept-density check (keep the title regexes).

### 3.4 Reposts and recycled news — HARD DROP (`repost`)

- `url_hash` present in `state/emitted.sqlite` within 8 weeks → drop.
- `norm_title_hash` present within 8 weeks → drop (catches syndication under a new URL).
- Cluster simhash within Hamming distance 3 of a cluster emitted last week → `PENALTY += 30`; emitted
  only if `has_new_facts` (new version number, new named entity, or new numeric claim not in the prior
  item) → then rendered with the `[развитие темы]` flag.
- "Best of / most read this year", `r'\b(revisit(ed|ing)|from the archives|reader favou?rites|
  most[- ]read|year in review|20\d\d in review)\b'` → drop.

### 3.5 AI-generated content farms — HARD DROP (`ai_slop`)

Phrase list (count distinct hits in body; **≥ 3 → drop**, `== 2 → PENALTY += 15`):

```
"in today's fast-paced", "ever-evolving landscape", "ever-changing landscape", "delve into",
"it's important to note that", "it's worth noting that", "game-changer", "game changer",
"unlock the power", "harness the power", "in the world of", "revolutioniz",
"seamlessly integrat", "robust and scalable", "cutting-edge solution", "leverage the power",
"navigate the complexities", "in conclusion,", "let's dive in", "buckle up",
"the landscape of", "paradigm shift", "at the end of the day,", "tapestry of",
"stands as a testament", "plays a crucial role", "a myriad of"
```

Structural fingerprints (each +1 slop point, ≥ 2 points behaves as one phrase hit):
- `r'\bnot (just|only) \w+[,]? but\b'` occurring ≥ 2 times;
- every H2 is Title Case and the section count is 5–8 with variance of section length < 25 %;
- zero outbound links to a primary source, or all outbound links are to the same domain;
- no author byline **and** domain has published > 15 items in this crawl window;
- summary/description field is a verbatim prefix of the body's first paragraph AND the title is a
  question that the first paragraph restates.

Suspect surfaces get a stricter threshold (`≥ 2 phrase hits → drop`): `dev.to`, `hashnode.dev`,
`medium.com` non-publication URLs, `*.hashnode.dev`, `dzone.com`, `geeksforgeeks.org`,
`simplilearn.com`, `k21academy.com`, `edureka.co`, `tutorialspoint.com`, `javatpoint.com`,
`baeldung.com` (K8s section only), `linkedin.com/pulse`.

### 3.6 Reddit help/support, career, memes — HARD DROP

```python
REDDIT_DROP_FLAIR = {"help","question","support","troubleshooting","career","hiring",
                     "meme","humor","rant","shitpost","survey","poll","showoff","homelab pics"}

REDDIT_DROP_TITLE = [
  r'^\s*(help|question|q|advice|support)\b\s*[:!,\-–]',
  r'\bhow (do|can|would|should) (i|we|you)\b',
  r'\bwhy (is|are|does|do|won\'t|can\'t) (my|our|this|the)\b',
  r'\b(is (this|it|that) (normal|expected|a bug))\b',
  r'\bneed (help|advice|guidance|opinions?)\b',
  r'\b(any(one|body)) (else )?(know|have|using|tried|experienced|seeing)\b',
  r'\b(what|which) (is|are) the best\b.*\?',
  r'\brecommend(ation)?s?\b.*\?\s*$',
  r'\b(cka|ckad|cks|kcna|certification|exam|resume|cv|interview|salary|compensation|
      job (hunt|search)|hiring|laid off|layoff|career (advice|change|path))\b',
  r'\b(rate my|roast my|my first|just finished my)\b',
  r'\bhomelab (tour|update|build)\b',
]
```

Structural: `is_self == True` **and** `outbound_url is None` **and** `score < 80` → drop
(`reddit_selfpost`).
**Exception that must exist:** `is_self` + `flair == discussion` + `num_comments >= 120` → keep and
route to `community`. Those threads ("почему все уходят с Helm", "кто-нибудь реально использует
Gateway API в проде") are prime podcast material and the naive filter would kill them.

Also drop Reddit items whose `outbound_url` domain is in `PR_DOMAINS`, is a YouTube Short, or is an
image host (`i.redd.it`, `imgur.com`, `i.imgur.com`).

### 3.7 Releases: real release vs. noise (`release_noise`)

**Asset count is a bad signal — do not use it.** A Go project publishes 25 cross-compiled binaries for
a one-character typo fix, and a Java project publishes none for a major rewrite. Use bump class +
notes structure + change markers.

```python
def release_verdict(rel, repo_cfg):
    if rel.draft: return DROP("release_draft")

    # 0. tags that are never news
    if re.match(r'^(nightly|daily|canary|snapshot|latest|edge)\b', rel.tag, re.I): return DROP
    if re.match(r'^v?\d{8}(\.\d+)?$', rel.tag):        return DROP   # date tags
    if not semver_parseable(rel.tag) and len(rel.body) < 1500: return DROP("unparseable_tag")

    bump = classify_bump(rel.tag, previous_tag_of(repo))   # major|minor|patch|prerelease

    # 1. always keep
    if re.search(r'\b(CVE-\d{4}-\d{4,}|GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4})\b', rel.body):
        return KEEP(security_flag=True)
    if re.search(r'\b(breaking change|action required|backwards[- ]incompatible|'
                 r'no longer supported|removed in this release|migration required)\b', rel.body, re.I):
        return KEEP(breaking_change_flag=True)
    if bump in ("major",): return KEEP()

    # 2. prereleases
    if rel.prerelease or bump == "prerelease":
        # only .0 RCs of core repos are newsworthy (k8s 1.35.0-rc.1 is a story; grafana rc is not)
        if repo in CORE_RC_REPOS and re.search(r'\.0-(rc|beta|alpha)', rel.tag): return KEEP()
        return DROP("prerelease")

    # 3. dependency-bump detection  (the main patch-release killer)
    lines   = [l for l in rel.body.splitlines() if re.match(r'\s*[-*]\s+\S', l)]
    dep_re  = re.compile(r'^\s*[-*]\s*(build|chore|deps)?\(?deps\)?[: ]|'
                         r'^\s*[-*]\s*(bump|update|upgrade)\s+[\w./@-]+\s+from\s+v?[\d.]+\s+to\s+v?[\d.]+|'
                         r'dependabot|renovate\[bot\]', re.I)
    if lines and sum(bool(dep_re.search(l)) for l in lines) / len(lines) > 0.70:
        return DROP("dependency_bump")
    if re.fullmatch(r'\s*(bug ?fixes?|maintenance|patch) release\.?\s*', strip_md(rel.body), re.I):
        return DROP("boilerplate_notes")

    # 4. patch releases must earn their slot
    if bump == "patch":
        substantial = (len(strip_md(rel.body)) >= 600
                       and count_headings(rel.body) >= 2
                       and count_distinct(TIER_A|TIER_B, rel.body) >= 2)
        if not substantial: return DROP("patch_bump")
        return KEEP()

    # 5. minor
    if bump == "minor":
        if len(strip_md(rel.body)) < 400 and count_headings(rel.body) < 2:
            return DROP("thin_minor")
        return KEEP()
    return DROP("unclassified")
```

Additional release rules:
- **Cadence collapse:** if a repo published > 2 releases inside the window, keep only the highest
  version; attach the others as `Ещё: v1.2.3, v1.2.4` in the comment. Reason code `release_cadence`.
- **Backport fan-out:** k8s-style repos publish 1.32.x / 1.33.x / 1.34.x on the same day. Group by
  minor line, keep the newest minor line only, mention the rest inline.
- **Mirror/duplicate repos** (`kubernetes/kubectl` mirrors `kubernetes/kubernetes`): maintain a
  `mirror_of:` map in `releases.yaml` and drop the mirror.
- **Release ↔ blog post duplication:** a release and the project's own announcement blog post are the
  same cluster (§2.10c/d will usually catch it via the version entity); prefer the **blog post** as
  canonical when it exists and has `words > 600`, with the release as an `Ещё:` link.
- `min_bump` per repo replaces the current inert `tier:` — see §7.12.

### 3.8 Job posts — HARD DROP (`job_post`)

```python
JOB_DROP = [
  r'\bwe(\'| a)re hiring\b', r'\bnow hiring\b', r'\bjob (opening|opportunity|posting|alert)\b',
  r'\b(apply now|join our team|open (roles?|positions?)|career opportunities)\b',
  r'^ask hn:\s*who (is hiring|wants to be hired)',
  r'^\s*\[hiring\]', r'^\s*\[for hire\]',
  r'\b(remote|onsite|hybrid)\b.{0,25}\b(full[- ]time|contract|c2c|w2)\b',
  r'\b(usd|eur|\$)\s?\d{2,3}[kк]\b.{0,20}\b(salary|comp|per year)\b',
]
```

### 3.9 Paywalls and non-articles

- Paywall domains (`wsj.com`, `bloomberg.com`, `ft.com`, `theinformation.com`, `businessinsider.com`,
  `nytimes.com`, `economist.com`) → drop unless `SRC == 1.0`.
- Soft paywall detection on fetch: extracted `words < 400` **and** body matches
  `r'\b(member[- ]only story|continue reading|subscribe to (read|continue)|create a free account to
  (read|continue)|this article is for subscribers)\b'` → drop (`paywall`).
- Non-article URL shapes → drop (`not_an_article`):
  `r'/(tag|tags|category|categories|topics?|author|search|page)/'`, `r'/page/\d+/?$'`,
  bare domain root, `r'/(events?|webinars?|training|courses?|pricing|about|careers?|jobs?)(/|$)'`.
- Podcast/video landing page with `words < 200` and no transcript → drop unless `kind == "talk"` and
  duration metadata exists.
- PDF: keep, but require `pages <= 60`; set `kind = "paper"`, route to `longform`.

### 3.10 Language and encoding sanity

- Detect language with a real detector (`lingua`/`fasttext`) over the body, not the feed's `lang`
  field — many "Japanese" corporate blogs publish English. `item.lang` = detected; the feed's `lang`
  is only a prior used when detection confidence < 0.7.
- Mojibake guard: if the title contains `Ð|Ñ|â€|ï¿½` sequences → re-decode; if it still fails, drop
  (`encoding_error`).

---

## 4. The comment

### 4.1 Language decision: **comments in Russian, titles in the original language.** 

Justification, since this is the one irreversible product decision in the file:

1. The comment is the **scanning surface**. A host scanning 100 entries reads ~100 comments and maybe
   30 titles. Native-language comments cut scan time roughly in half and, more importantly, remove the
   micro-hesitation that makes people skip items. The whole product is "reduce the cost of triage";
   translating the triage layer is the highest-value translation available.
2. The title is the **identifier**, not prose. It is what gets typed into a search box, pasted into the
   show notes, and pronounced on air. Translating "Gateway API 1.4 promotes Mesh conformance to GA"
   into Russian destroys its searchability and makes the host say a product name that does not exist.
   Product names, version strings and CVE ids must never be translated.
3. The output is a Russian-language podcast. Russian comments mean the host can lift a phrase from the
   digest straight into the episode script; English comments would need re-writing anyway, so the
   translation cost is paid regardless — better paid once, by the generator.
4. Cost of the decision is asymmetric: if a host prefers English, they read the English title and the
   linked article and lose little. If a host cannot fast-read English at 100-items-per-sitting pace,
   an English digest is unusable.

**Corollary rules:**
- Titles are reproduced **verbatim** in the source language, including CJK. Every non-Latin-script
  title (zh/ja/ko) gets a Russian gloss on the following line in italics and parentheses. Russian
  titles obviously need no gloss; German titles get a gloss too (few hosts read German fluently).
- Never translate inside a comment: project names, version numbers, CVE/GHSA ids, flag names,
  CRD kinds, commands. Keep them in Latin script inline.
- Technical terms stay in the accepted Russian-infra jargon register (нода, под, деплой, апстрим),
  not academic calques. The audience speaks that way.

### 4.2 Length and required content

- **Comment length: 200–420 characters** (roughly 30–60 Russian words), two labelled parts.
  Below 200 it is a stub; above 420 the host reads the article instead, and 100 × 500 chars is a
  50 KB wall of text.
- **`Что внутри` — 1–2 sentences, facts only.** Must contain at least one *concrete noun*: a version,
  a number, a component name, a percentage, a CVE id. A comment with no proper noun and no digit is
  automatically rejected by the renderer and regenerated (`assert re.search(r'\d', comment_what)`).
- **`Почему важно` — exactly 1 sentence: the consequence for someone running this in production.**
  Answers "что мне с этим делать / о чём тут спорить", not "это интересно".
- **Banned in comments** (renderer-level lint, regenerate on hit): `важный`, `интересный`,
  `значительный`, `революционн`, `меняет правила игры`, `нельзя пропустить`, `must-have`,
  `в современном мире`, `как известно`, plus any adjective of magnitude unaccompanied by a number.
- **Flags** (0–3 per item, from a closed set), rendered inline after the title:
  `[breaking]` `[CVE]` `[постмортем]` `[бенчмарк]` `[спорно]` `[обновлено]` `[догоняющее]`
  `[развитие темы]` `[платно]` `[видео]` `[длинное]`.
  `[спорно]` is set when the discussion has `comments/points > 0.8` — i.e. an argument, not applause.
- Every entry carries a machine-readable footer line: tags, score, and discussion links. The score is
  there so the hosts can calibrate and complain about the ranker — that feedback loop is the only way
  the weights get tuned.

### 4.3 Exact markdown format

Entry template (the renderer must produce exactly this shape):

```markdown
### <N>. <Title verbatim in source language> <flags>
*(<Russian gloss — only for zh/ja/ko/de titles>)*
`<kind>` · `<section>` · <source title> · <YYYY-MM-DD> · **[<display-domain>](<canonical-url>)**
**Что внутри:** <1–2 sentences, Russian, facts and numbers.>
**Почему важно:** <1 sentence, Russian, the production consequence.>
<optional> **Ещё:** [<label>](<url>) · [<label>](<url>)
`теги: <tag>, <tag>, <tag>` · `score <NN>` · <discussion links>
```

`kind ∈ {release, blog, discussion, news, postmortem, advisory, talk, paper}`.

### 4.4 Five worked examples

```markdown
### 3. Cilium 1.19.0 [breaking]
`release` · `Релизы, которые важны` · cilium/cilium · 2026-09-03 · **[github.com/cilium/cilium](https://github.com/cilium/cilium/releases/tag/v1.19.0)**
**Что внутри:** netkit включён по умолчанию вместо veth, kube-proxy replacement объявлен стабильным на всех поддерживаемых ядрах, добавлен BGP graceful restart; CRD `CiliumBGPPeeringPolicy` удалён после двух релизов в deprecated.
**Почему важно:** апгрейд ломает всех, кто остался на старом BGP-CRD, и меняет профиль latency на дата-плейне — это не «накатили и забыли», а окно техработ с проверкой eBPF-тулинга, который ходил в veth-пары.
**Ещё:** [анонс в блоге](https://cilium.io/blog/2026/09/03/cilium-119/) · [upgrade notes](https://docs.cilium.io/en/v1.19/operations/upgrade/)
`теги: cni, ebpf, bgp, breaking` · `score 91` · [HN 340↑/212💬](https://news.ycombinator.com/item?id=00000000) · [r/kubernetes 260↑](https://reddit.com/r/kubernetes/comments/xxxxx/)

### 11. etcd is not the bottleneck: 40k-node clusters and where the apiserver actually dies [спорно] [бенчмарк]
`discussion` · `Дискуссии` · Hacker News · 2026-09-05 · **[bytesized.dev](https://bytesized.dev/posts/etcd-not-the-bottleneck)**
**Что внутри:** автор гоняет синтетику на 40k нод и утверждает, что до 25k нод упирается не etcd, а watch-кэш и сериализация в kube-apiserver; в треде спорят инженеры из SIG-Scalability и приводят контрпримеры на реальных кластерах с CRD-heavy нагрузкой.
**Почему важно:** готовый конфликт для эфира — тезис «etcd виноват» держится в индустрии годами, а тут его публично ломают люди, которые эти лимиты и писали.
`теги: scalability, etcd, apiserver` · `score 88` · [HN 512↑/389💬](https://news.ycombinator.com/item?id=00000000)

### 24. How we cut p99 image pull latency from 90s to 4s across 12k nodes
`blog` · `Глубокие технические тексты` · Mercari Engineering · 2026-09-02 · **[engineering.mercari.com](https://engineering.mercari.com/en/blog/entry/20260902-image-pull/)**
**Что внутри:** переход с обычного pull на Spegel + lazy-pulling через stargz, замеры по 12k нод, разбор того, где ломается P2P-раздача при rollout всего кластера, и почему пришлось патчить containerd-конфиг под свой registry.
**Почему важно:** цифры и грабли по слою, который у всех есть и который никто не измеряет; сразу переносится на любой кластер, где деплой упирается в реестр.
`теги: containerd, registry, spegel, performance` · `score 79`

### 41. Kubernetes 1.35 release schedule and the SIG-Node freeze
`news` · `Экосистема, деньги и управление` · Kubernetes Contributors · 2026-09-04 · **[kubernetes.dev](https://www.kubernetes.dev/blog/2026/09/04/1-35-schedule/)**
**Что внутри:** объявлены даты 1.35 (enhancements freeze 2026-10-08, релиз 2026-12-09), SIG-Node закрывает приём новых KEP на цикл раньше обычного из-за нагрузки на ревью DRA.
**Почему важно:** определяет, какие фичи вообще успеют в декабрьский релиз — если ждали чего-то из in-place resize или DRA, календарь только что сдвинулся.
`теги: kubernetes, release-cycle, sig-node` · `score 71`

### 57. 我们如何用 KubeVirt 承载 20 万台虚拟机
*(«Как мы держим 200 000 виртуалок на KubeVirt»)*
`blog` · `Не на английском` · CloudWeGo (ByteDance) · 2026-09-01 · **[cloudwego.io](https://www.cloudwego.io/blog/2026/09/01/kubevirt-200k/)**
**Что внутри:** ByteDance описывает шардирование control plane на 200k ВМ, свой планировщик поверх KubeVirt, отказ от live migration в пользу быстрого перезапуска и цифры по времени старта ВМ до/после.
**Почему важно:** это единственная публичная инсталляция KubeVirt такого масштаба, и выводы прямо противоположны рекомендациям апстрима — материал, которого нет ни в одном англоязычном источнике.
`теги: kubevirt, virtualization, scale, china` · `score 74`
```

### 4.5 Header and footer of the file

```markdown
# Дайджест за 2026-09-01 — 2026-09-07
Окно: 2026-09-01T00:00Z — 2026-09-07T23:59Z · собрано 4 118 кандидатов · отобрано 100
Источники: 184 RSS (живых 176), 28 subreddit, HN, Lobsters, 231 репозиторий
Отброшено по фильтрам: seo_listicle 214, vendor_pr 188, patch_bump 173, beginner 141, …

## ⭐ Топ-10 недели
1. [Cilium 1.19.0](#3-cilium-1190) — ...
...
```

Footer lists dead feeds (§7.11) and links `digest/<date>-rejected.md`.

---

## 5. Freshness

Window definition, fixed and printed in the header:
`window = [now_utc − 7 days, now_utc]`, `now_utc` = digest generation timestamp, inclusive on both ends.
All timestamps normalised to UTC before comparison. Naive (offset-less) timestamps are assumed UTC and
get a ±12 h tolerance at the window boundary only.

### 5.1 Missing or broken dates

Date resolution chain, first non-null wins:

```
1. atom:published / rss:pubDate
2. dc:date
3. atom:updated / rss:lastBuildDate on the *item* (not the channel)
4. <meta property="article:published_time"> from the fetched page
5. JSON-LD  datePublished
6. URL date pattern:  /(20\d\d)/(\d{2})/(\d{2})/  or  /(20\d\d)-(\d{2})-(\d{2})-
7. HTTP Last-Modified of the article URL
8. first_seen  (our crawler's first observation)
```

Rules:
- If resolution lands on step 8 (`first_seen` only), the item is `provisional`. Admit it **only if the
  source has been polled continuously for ≥ 14 days** — otherwise the first run of the collector would
  admit a source's entire back catalogue as "new". On a cold start, every source is quarantined for 14
  days for date-less items; dated items are unaffected.
- Never use the **channel-level** `lastBuildDate` as an item date. Several feeds in the list
  (`opennet`, some Hugo `index.xml`) put a build timestamp there and it will mark the whole feed fresh
  every run.

### 5.2 Future and absurd dates

```python
if published > now + 6h:   published = now; flag("clamped_future")
if published > now + 7d:   drop("bogus_future_date")
if published < 2000-01-01: fall through to next resolution step
```

### 5.3 `updated` vs `published`

- Window membership is decided by **`published`**, always.
- An item whose `published` is outside the window but `updated` is inside enters **only if** the change
  is substantial: title changed, **or** body length changed by ≥ 30 %, **or** a new version/CVE id
  appeared. Rendered with `[обновлено]` and `REC` computed from `updated`.
- An item already emitted in a previous digest is never re-emitted for a timestamp change alone.
  Exception: a postmortem that gains a root-cause section (`incident_flag` + body grew ≥ 50 %) —
  re-emit with `[обновлено]`, cap 2 such items per digest.
- Feeds that touch `updated` on every rebuild (common with Hugo `index.xml`, and `deckhouse`,
  `higress`, `karmada`, `kubesphere` all publish Hugo index feeds) must be marked
  `updated_unreliable: true` in `feeds.yaml` and have step 3 removed from their resolution chain.

### 5.4 Late arrivals

Real case: a blog publishes on day D but its feed only exposes the item on D+4; or the collector was
down.

```python
if published in window:                      normal
elif (now - published) <= 10d and first_seen in window and not previously_emitted:
        admit as late_arrival:  REC = 0.45,  flag "[догоняющее]",  MAX 5 per digest
else:   drop("stale")
```

The 10-day grace with a hard cap of 5 prevents an outage in the collector from turning next week's
digest into a two-week archive.

### 5.5 Reddit "top of week"

- The `top?t=week` listing is ranked by score, and **routinely contains posts older than 7 days**
  (Reddit's `t=week` boundary is fuzzy and crossposts carry old content). Filter on `created_utc`
  inside the window. Do not trust the listing.
- **Old link, new discussion:** if `outbound_url`'s own published date is > 30 days before the window,
  the *article* is not fresh. Admit only when the *discussion* is the story:
  `num_comments >= 100`, route to `community`, canonical = the Reddit thread, flag
  `[обсуждение старого материала]`, and state the article's original date in the comment. Max 3 per digest.
- Crossposts: dedupe by `outbound_url`; keep the instance with the highest score, list the others as
  `Ещё:`.
- Deleted/removed posts (`author == "[deleted]"`, `removed_by_category` set) → drop.

### 5.6 Hacker News

- Algolia `created_at_i` is the **submission** time, not the article's publication time. Same
  old-link rule as 5.5: fetch the target's own date; if > 30 days old, require
  `num_comments >= 120` and treat as `community`.
- HN reposts of a story we already emitted: cluster dedup (§6) handles it; the new HN thread is merged
  as an extra discussion link on the existing entry only if that entry is in *this* digest, otherwise
  it is a `repost` drop.
- `front_page_min_points: 150` in `community.yaml` is a *daily* front-page threshold; over a 7-day
  window this will pull ~200 items. Apply the topic gate (`TOP >= 0.20`) **before** the points
  threshold, not after, or the HN general-tech firehose dominates the candidate pool.

### 5.7 GitHub releases

- Use **`published_at`** from the REST/GraphQL release object. Never `tag.created_at`, never the commit
  date. A tag created six months ago and released today is legitimately this week's news (this happens
  with security backports and with projects that tag then wait for artefact builds).
- Conversely: a release **edited** this week but published two months ago has an old `published_at` —
  correct behaviour, it stays out.
- Draft → published transition sets `published_at` to the flip moment. Correct, keep.
- Guard against re-tagging: identity key is `(repo, tag)`. If `(repo, tag)` is in `emitted.sqlite`,
  drop regardless of `published_at` changes.
- Repos with no GitHub Releases (`torvalds/linux`, `ceph/ceph`, `nginx/nginx`, `openstack/nova`,
  `proxmox/pve-manager`, `apache/*` in part) must fall back to **tags** + an explicit changelog URL,
  configured per repo. Otherwise those ~20 entries in `releases.yaml` silently produce nothing forever
  — a failure that is invisible without §7.11 feed-health reporting.

### 5.8 Backdating blogs

Symptom: `published` is 5 days old but the item never appeared in any prior poll of a feed we poll hourly.

```python
if source.polled_continuously and (first_seen - published) > 4d:
    flag("backdated")
    effective_date = first_seen        # for REC and ordering
    admit only if published >= now - 14d
```

Do **not** simply trust `first_seen` for all sources — feeds we poll rarely, or that paginate, would
be mislabelled. The rule applies only where `poll_gap_max < 6h` over the last 7 days.

### 5.9 Timezone and DST specifics

- `RFC 822` feeds with `EST`/`PST`/`CEST` alphabetic zones: map explicitly; unknown abbreviation → UTC.
- Chinese and Japanese feeds commonly emit `+08:00`/`+09:00` correctly but some emit local time with
  `Z`. If a feed's items cluster suspiciously at 16:00–17:00 UTC (= 00:00–01:00 local), flag
  `tz_suspect` and widen the boundary tolerance to ±24 h for that feed.

### 5.10 Identity, not position

Item identity = `guid`/`id` if stable, else `canonical_url_hash`. Never identify by feed position or
title alone — Habr hub feeds re-emit items on edit, and `opennet` reuses ids across sections.

---

## 6. De-duplication

### 6.1 URL normalisation pipeline (ordered)

```
 1. Follow redirects, max 5 hops, 8s timeout. Record the final URL.
    Known shorteners/wrappers to always resolve:
    t.co, lnkd.in, buff.ly, bit.ly, ow.ly, dlvr.it, trib.al, ift.tt,
    feedproxy.google.com, feeds.feedburner.com, *.feedsportal.com,
    link.medium.com, open.substack.com, click.<anything>, r.<domain>,
    news.google.com/rss/articles/*, redirect.viglink.com
 2. If the fetched HTML has <link rel="canonical"> pointing to the same registrable domain,
    ADOPT IT. It overrides everything below. (Cross-domain canonicals are ignored — they are
    frequently wrong on syndication farms.)
 3. Scheme -> https. Host -> lowercase, strip default port, strip trailing dot.
 4. Host prefixes stripped: www., m., mobile., amp., www2.
 5. AMP: strip path segments /amp/ and trailing /amp, /amp.html; strip query amp=1, output=amp;
    handle google AMP cache: cdn.ampproject.org/c/s/<real-host>/<path>  ->  https://<real-host>/<path>
 6. Query params: DROP anything matching
    ^(utm_.*|ref|referer|referrer|source|src|fbclid|gclid|dclid|msclkid|mc_cid|mc_eid|
      _hs.*|hsa_.*|igshid|si|share|sh|s_cid|cmp|at_.*|__twitter.*|trk|trkCampaign|linkId|
      sc_channel|sc_campaign|sc_.*|spm|scm|from|ncid|CNDID|WT\..*|yclid|_openstat|
      guccounter|guce_.*|ck_subscriber_id|rss|feed)$
    KEEP everything else, EXCEPT: per-host allowlists for hosts where params are load-bearing
    (youtube.com: keep v,t,list ; github.com: keep nothing ; docs sites: keep version)
    Remaining params sorted alphabetically for a stable key.
 7. Fragment: drop, UNLESS the path is a docs/spec page and the fragment is the only content id
    (heuristic: path matches /(docs|spec|reference|api)/ and fragment length > 3).
 8. Path: strip trailing '/', strip '/index.html', '/index.php', '/default.aspx';
    collapse duplicate slashes; percent-decode unreserved characters.
 9. Host aliases (config table `dedup_aliases.yaml`), e.g.
    youtu.be/<id>            == youtube.com/watch?v=<id>
    <user>.medium.com/<slug> == medium.com/@<user>/<slug>
    old.reddit.com           == reddit.com == np.reddit.com
    <project>.github.io/blog == <project>.io/blog     (per-project, hand-maintained)
10. Medium-family: two URLs whose last path segment ends with the same 12-hex-char id
    (r'-([0-9a-f]{12})$') are the same article regardless of domain (custom Medium domains).
11. url_hash = sha256(normalized_url)
```

### 6.2 Title similarity

```python
def norm_title(t):
    t = unicodedata.normalize('NFKC', t).lower()
    t = strip_emoji(t)
    t = re.sub(r'^\s*(show|ask|tell) hn:\s*', '', t)
    t = re.sub(r'^\s*\[[^\]]{1,20}\]\s*', '', t)                 # [Release], [Blog], [OC]
    t = re.split(r'\s+[|–—]\s+', t)[0] if len(t) > 45 else t      # trailing site name
    t = re.sub(r'[^\w\s.]', ' ', t)
    t = ' '.join(w for w in t.split() if w not in STOPWORDS_EN|STOPWORDS_RU)
    return t

shingles = set of word 3-grams of norm_title (2-grams if len < 5 words)
MinHash 128 perms -> LSH 16 bands x 8 rows -> candidate pairs -> exact Jaccard
match if jaccard >= 0.55
```

Version-blind variant for the release/announcement pairing: `re.sub(r'v?\d+(\.\d+)+', '§', norm_title)`
compared with `jaccard >= 0.70` — catches "Cilium 1.19 released" vs "Announcing Cilium 1.19".

### 6.3 Cross-language duplicates

The same announcement appears on `cncf.io` (en) and `cloudnative.to` (zh). Title similarity fails.
Rule: if `entity_tuple` matches (same project + same version) **and** `|Δpublished| <= 96h` **and**
one is a translation-shaped item (detected: contains ≥ 3 Latin-script tokens from the other's title),
they are the same cluster. **However**, the non-English member is *not* suppressed — it competes in
its own reserved `nonenglish` quota (§1.3.5), where it is allowed to be a cluster sibling. This is a
deliberate exception: a Chinese-language write-up of a CNCF announcement is only worth a slot when it
adds local content, so require `words >= 800` and `ORIG != "coverage"` for it to survive.

### 6.4 Merging surfaces into one entry

```python
cluster = {
  "cluster_id": simhash64(canonical.norm_title),
  "canonical":  <item>,
  "surfaces": [
     {"kind":"hn",       "url":..., "points":512, "comments":389},
     {"kind":"reddit",   "url":..., "sub":"kubernetes", "score":260, "comments":88},
     {"kind":"lobsters", "url":..., "score":41},
     {"kind":"blog",     "url":..., "source":"cilium.io"},      # vendor announcement
     {"kind":"release",  "url":..., "repo":"cilium/cilium"},
  ],
  "ENG":  max(eng of all surfaces),
  "BONUS": min(8, 3.5*(len(surfaces)-1)) + ...
}
```

**Canonical selection priority** (first rule that discriminates):
1. If a `primary` ORIG member exists (project blog, own release, own postmortem) → it is canonical.
2. Else the member with the most body text (`words`), if `words >= 600`.
3. Else the member with the highest `SRC`.
4. Never make an HN/Reddit thread canonical when a reachable article exists — the thread becomes a
   discussion link. **Exception:** `Ask HN` / a self-post / a thread where the top comment is from the
   project maintainer and `comments/points > 1.0`. Then canonical = thread and the comment must say so
   ("ценность в треде, не в ссылке").

Rendering: the canonical URL is the bolded link; every other surface appears either as `Ещё:` (other
articles) or as discussion links in the footer line (`HN 512↑/389💬`, `r/kubernetes 260↑`).

### 6.5 What "credits the discussion links" means concretely

Footer line format, ordered by engagement descending, max 4 links:

```
`теги: …` · `score 91` · [HN 512↑/389💬](url) · [r/kubernetes 260↑/88💬](url) · [Lobsters 41↑](url) · [Ещё 2 треда](url-to-hn-search)
```

If the same article was submitted to HN twice, link the thread with more comments and note
`(+1 тред)`.

### 6.6 Cross-week de-duplication

State store `state/emitted.sqlite`:

```sql
CREATE TABLE emitted (
  url_hash     TEXT PRIMARY KEY,
  norm_title_h TEXT,
  cluster_sim  INTEGER,     -- simhash64
  entity       TEXT,        -- "cilium@1.19"
  digest_date  TEXT,
  section      TEXT,
  score        REAL
);
CREATE INDEX ix_title  ON emitted(norm_title_h);
CREATE INDEX ix_entity ON emitted(entity);
```

Rules:
- `url_hash` seen within 8 weeks → drop (`repost`).
- `norm_title_h` seen within 8 weeks → drop.
- `hamming(cluster_sim, prior) <= 3` within 1 week → `PENALTY += 30`; admit only with `has_new_facts`,
  render `[развитие темы]` and open the comment with what changed since last week.
- Same `entity` emitted last week → allowed (a project can have news twice), but `entity_mult` starts
  at rank 2 instead of rank 1, i.e. the bar is higher.

---

## 7. What is missing from the concept

Ranked by (value to the podcast) ÷ (effort). Effort: **S** ≤ 4 h, **M** = 1–2 days, **L** = 3–5 days.

1. **Security advisories as a first-class source — S.**
   The design reserves 8 slots for `security`, but nothing in the three YAMLs reliably produces
   advisories. A Kubernetes CVE is guaranteed podcast material and guaranteed listener action. Add:
   GitHub GraphQL `securityAdvisories` for the ~230 repos already listed, `kubernetes-announce`
   (groups.google.com feed), the k8s `official-cve-feed` JSON, CISA KEV, and distro advisories
   (Debian DSA, RHSA). Without this the `security` quota fills with generic "supply chain" blog posts.

2. **Incident / outage sources — M.**
   Same structural gap for the `incidents` quota. Add status-page histories and RSS for the providers
   the audience actually runs on (AWS, GCP, Azure, Cloudflare, GitHub, Fastly, DigitalOcean, Hetzner,
   OVH, Yandex Cloud), plus dedicated postmortem publishers. Today the only path to an RCA is
   accidentally, via SRE Weekly. Highest per-item episode value in the whole digest.

3. **Mine the newsletters instead of quoting them — M, and the biggest quality win available.**
   KubeWeekly, LWKD, DevOps'ish, SRE Weekly, CloudSecList, Last Week in AWS are *human-curated link
   lists*. Parse their HTML bodies, extract outbound links, resolve them (§6.1), and use "appeared in
   ≥1 newsletter" as a `+6` precision signal (§2.8) and as a discovery source for items our 184 feeds
   missed. The newsletters themselves should score `ORIG=0.10` and essentially never occupy a slot.
   This buys you a free human editorial layer.

4. **Full-text extraction + LLM comment generation with a cache — L, and non-optional.**
   The requirement "short comment on why it deserves attention and what is inside" is unimplementable
   from RSS summaries alone, and `FORM`, `ORIG`, the beginner filter and the AI-slop filter all need
   body text. Pipeline: fetch → `trafilatura`/`readability` → store `(url_hash, text, words,
   code_blocks, headings)` in a content cache → generate comments only for the ~150 survivors, not for
   4 000 candidates. Budget it: ~150 items × ~1.5k tokens in ≈ 1 LLM call each is trivially cheap; the
   fetching is the slow part, so cache aggressively and run it concurrently.

5. **Carry-over state and story arcs — M.**
   `state/emitted.sqlite` (§6.6) is required for repost detection anyway; once it exists, it unlocks
   the two most editorially valuable additions: `[развитие темы]` continuity ("на прошлой неделе
   анонсировали, на этой сломали") and a `## Чего ждём` block (known dates: release schedules, CFP
   deadlines, KubeCon, freeze dates) that turns the digest into a planning tool rather than a rear-view
   mirror.

6. **CNCF project-lifecycle and governance tracking — S/M.**
   Sandbox/incubation/graduation votes, project archival, maintainer departures, licence changes and
   forks live in the `cncf/toc` repo issues and in project GOVERNANCE commits, not in any blog feed.
   These are the loudest, most opinion-generating stories in the ecosystem and the current source list
   catches them only after someone writes about them.

7. **Funding, acquisitions and relicensing watch — S.**
   "Vendor X relicenses to BSL" and "Vendor Y acquired" are the stories the audience talks about for a
   month. Implement as a keyword watch across all surfaces
   (`relicens|BSL|Business Source|SSPL|Elastic License|acquir|acquisition|fork of|to sunset|
   end of life|shutting down`) routed to `ecosystem`, plus a couple of dedicated feeds.

8. **Conference talk drops — M.**
   KubeCon/SREcon/FOSDEM/USENIX publish batches of talks weekly during season; a good talk is a
   ready-made episode segment. Add YouTube playlist feeds + USENIX paper feeds, `kind = "talk"`,
   route to `longform`, and require a description ≥ 200 chars to avoid empty video pages.

9. **A "подкаст-угол" line on the top 20 — S (given #4).**
   One extra line per top-20 item: *в чём спор, кто оппонент, что спросить у гостя*. This is the actual
   product the hosts want; the other 80 items are the archive. Cheap once the LLM pass exists, and it
   is what will make the hosts open the file every week.

10. **Second output: `digest/<date>-short.md` — S.**
    15 items with a one-line comment each, ready to paste into show notes. 100-item files do not get
    read on a phone before recording.

11. **Feed health reporting — S.**
    184 feeds will rot: at any time expect 5–15 % dead, redirected, or empty. Track per feed:
    `last_success`, `items_last_30d`, `http_status`, and report in the digest footer
    "мёртвые источники: N". Add ETag / If-Modified-Since to avoid re-parsing unchanged feeds. Also
    catches the silent `releases.yaml` failures noted in §5.7.

12. **Fix `releases.yaml` schema — S.**
    Replace the inert `tier:` with per-repo policy:
    `{repo: prometheus/prometheus, min_bump: minor}`, `{repo: kubernetes/kubernetes, min_bump: patch, rc: true}`,
    plus `mirror_of:` and `changelog_url:` for the ~20 repos with no GitHub Releases. Without this,
    §3.7's rules have nothing repo-specific to consult and the Releases section will be dominated by
    whichever project happens to ship most often (Grafana, Traefik, Talos, k9s).

13. **`feeds.yaml` schema additions — S.**
    `updated_unreliable: bool` (§5.3), `full_text: bool` (does the feed carry the whole body — saves a
    fetch), `paywall: bool`, `poll: hourly|daily`, `include:`/`exclude:` regex overrides per feed
    (e.g. `phoronix` needs `exclude: /(gaming|gpu driver benchmark)/`, `simonwillison` needs an
    LLM-topic filter, `hatena-it` is a general IT hot-entry feed and needs a hard `TOP` gate).

14. **Rejected log — S.**
    `digest/<date>-rejected.md` with the top 50 near-misses (score 35–45) and the 20 highest-scoring
    hard-drops with their reason codes. This is the only mechanism by which filter mistakes ever get
    found; without it, a regex that accidentally kills every LWN item goes unnoticed for months.

15. **Pronunciation / name hints — S.**
    For the top 20, a `произносится:` hint on non-obvious names (Kyverno, Talos, Vitess, 字节跳动).
    Trivial to generate, saves on-air embarrassment.

16. **Say it plainly: 100 is probably the wrong number.**
    The valuable part of this artefact is the top 20–30. Items 60–100 will be read by nobody and their
    only real function is archival completeness. If the number is fixed by the requirement, keep 100 —
    but the tiering in §1.3.4 and the short file in #10 are what make it usable. If the number is
    negotiable, propose **40 items with better comments** and the same section structure. That is a
    strictly better weekly product for the same collector.

---

## Appendix A — reason codes

`off_topic` `seo_listicle` `vendor_pr` `beginner` `repost` `ai_slop` `reddit_help`
`reddit_selfpost` `job_post` `paywall` `not_an_article` `encoding_error` `stale`
`bogus_future_date` `release_draft` `prerelease` `dependency_bump` `boilerplate_notes`
`patch_bump` `thin_minor` `release_cadence` `unparseable_tag` `mirror_repo`
`entity_cap` `domain_cap` `cluster_sibling` `below_threshold`

## Appendix B — config additions required by this spec

```yaml
# feeds.yaml (per feed)
updated_unreliable: bool     # default false
full_text: bool              # default false
paywall: bool                # default false
poll: hourly | daily         # default hourly
include: [regex, ...]        # optional whitelist applied to title
exclude: [regex, ...]        # optional blacklist applied to title

# releases.yaml (per repo, replaces `tier`)
min_bump: patch | minor | major
rc: bool                     # emit .0 release candidates
mirror_of: <repo>            # suppress, credit the parent
changelog_url: <url>         # for repos without GitHub Releases
stars_hint: int              # cached, refreshed monthly

# new files
dedup_aliases.yaml           # host alias table (§6.1 step 9)
blocklists.yaml              # SEO/PR/slop regexes and domain lists (§3)
state/emitted.sqlite         # cross-week dedup (§6.6)
state/feed_health.json       # §7.11
```
