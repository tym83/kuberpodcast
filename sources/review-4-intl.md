# Review #4 — non-English / non-Russian coverage (zh · ja · ko · EU locals)

Reviewer scope: Chinese (priority), Japanese, Korean, European local scenes.
Date of verification run: **2026-09-08**.

## How everything below was verified

* Every URL was fetched with a real browser UA (`Chrome/124`), gzip, 25 s timeout, redirects followed,
  then parsed with `feedparser` — the same library `digestbot/collect.py` uses. Recorded per URL:
  HTTP status, content-type, byte size, entry count, newest entry date.
* **Egress caveat, read this first.** This machine egresses from **Frankfurt, DE**
  (`204.62.120.40`, AS205719) — *not* from a US GitHub Actions runner. Chinese WAFs generally
  discriminate CN vs. non-CN rather than DE vs. US, so a DE result is a good but not perfect proxy.
  For the doubtful Chinese endpoints I ran a **second vantage** through `r.jina.ai` (third-party
  datacenter IP, different ASN and continent). Results agreed in every case, including the one
  hard block (openEuler 403 from both). Where the two vantages agree I treat the verdict as solid;
  the only source I cannot fully de-risk for US egress is anything already borderline
  (`ridicorp.com`, `imasters.com.br` — both flagged below).
* Nothing in "Additions" is unverified. Entry counts and newest-entry dates are from the final
  consolidated run, one pass, same timestamp.

---

## Additions

### Chinese (zh) — projects and vendors

```yaml
# ── Chinese-language: projects & vendors ─────────────────────────────
- {id: cloudwego,       title: "CloudWeGo (ByteDance)",        url: "https://www.cloudwego.io/index.xml",                         lang: zh, category: vendor, weight: 3}
- {id: dragonfly-cn,    title: "Dragonfly (阿里/CNCF)",          url: "https://d7y.io/blog/rss.xml",                                lang: en, category: project, weight: 2}
- {id: openkruise,      title: "OpenKruise 博客",               url: "https://openkruise.io/zh/blog/rss.xml",                      lang: zh, category: project, weight: 2}
- {id: kubevela,        title: "KubeVela Blog",                url: "https://kubevela.io/blog/rss.xml",                           lang: en, category: project, weight: 2}
- {id: koordinator,     title: "Koordinator 博客 (阿里)",         url: "https://koordinator.sh/zh-Hans/blog/rss.xml",                lang: zh, category: project, weight: 2}
- {id: apisix-cn,       title: "Apache APISIX 中文博客",         url: "https://apisix.apache.org/zh/blog/rss.xml",                  lang: zh, category: project, weight: 2}
- {id: doris-cn,        title: "Apache Doris 博客",             url: "https://doris.apache.org/zh-CN/blog/rss.xml",                lang: zh, category: project, weight: 2}
- {id: seatunnel-cn,    title: "Apache SeaTunnel 博客",         url: "https://seatunnel.apache.org/zh-CN/blog/rss.xml",            lang: zh, category: project, weight: 1}
- {id: volcano,         title: "Volcano (华为, batch/AI)",      url: "https://volcano.sh/blog/rss.xml",                            lang: en, category: project, weight: 3}
- {id: hami,            title: "HAMi (GPU sharing)",           url: "https://project-hami.io/blog/rss.xml",                       lang: en, category: project, weight: 3}
- {id: greptime,        title: "GreptimeDB Blog",              url: "https://greptime.com/blogs/rss.xml",                         lang: en, category: vendor, weight: 2}
- {id: databend,        title: "Databend Blog",                url: "https://www.databend.com/blog/rss.xml",                      lang: en, category: vendor, weight: 2}
- {id: starrocks,       title: "StarRocks Blog",               url: "https://www.starrocks.io/blog/rss.xml",                      lang: en, category: vendor, weight: 2}
- {id: sealos,          title: "Sealos Blog",                  url: "https://sealos.io/rss.xml",                                  lang: en, category: vendor, weight: 2}
- {id: rainbond,        title: "Rainbond 博客",                 url: "https://www.rainbond.com/blog/rss.xml",                      lang: zh, category: vendor, weight: 1}
```

| id | why an English-only digest misses it | evidence (2026-09-08) |
|---|---|---|
| cloudwego | ByteDance's RPC/microservice stack (Kitex, Hertz, Volo, netpoll) — release notes and design posts that never reach the English ecosystem. This is the host's named example. | 200, feed, 50 entries, newest 2026-05-08. **Note:** `/blog/index.xml` in the draft is 404; only the site-wide `/index.xml` exists. Blog items are prefixed `Blog: ` and their links contain `/blog/` — filterable. |
| dragonfly-cn | Alibaba-originated CNCF P2P image distribution; the operational posts (registry offload at 10k-node scale) are written by Alibaba/Ant SREs. | 200, 20 entries, newest 2026-07-29 |
| openkruise | Alibaba's advanced workload controllers (sidecar upgrade, in-place update) — the zh feed carries the same posts with Chinese-only operational detail. | 200, 16 entries, newest 2026-06-21 |
| kubevela | OAM/app-delivery model that is mainstream in CN platform teams and almost invisible in US discourse. | 200, 20 entries, newest 2026-07-22 |
| koordinator | Colocation/QoS scheduling from Alibaba — the real production answer to "batch + online on one cluster". zh version is more detailed than en. | 200, 17 entries, newest 2026-04-16 |
| apisix-cn | Chinese-language monthly community reports and gateway internals from API7/Apache. | 200, 20 entries, newest 2026-08-31 |
| doris-cn | Chinese OLAP engine with heavy production usage; zh blog is ahead of the en one. | 200, 20 entries, newest 2026-09-01 |
| seatunnel-cn | Data-integration engine, WhaleOps-driven; low volume, keep weight 1. | 200, 20 entries, newest 2026-08-08 |
| volcano | Huawei's batch/AI scheduler — gang scheduling, DRA queue quota. Directly relevant to GPU-cluster episodes. | 200 (`/en/blog/rss.xml` 301s here), 20 entries, newest 2026-05-30 |
| hami | Chinese-led CNCF sandbox for GPU sharing/vGPU — the topic Western vendors sell as proprietary. | 200, 20 entries, newest 2026-08-26 |
| greptime | Chinese TSDB vendor shipping observability-storage work (native histograms, service graphs) rarely covered in EN media. | 200, 330 entries, newest 2026-08-31 |
| databend | Chinese Snowflake-alternative, Rust; posts are engineering-deep. Content is EN, company/scene is CN. | 200, 20 entries, newest 2026-09-02 |
| starrocks | Chinese-origin OLAP with real-world lakehouse migrations. | 200, 10 entries, newest 2026-04-29 |
| sealos | CN "cloud OS" on k8s, big domestic adoption, near-zero EN coverage. | 200, 156 entries, newest 2026-07-28 (feed lives at `/rss.xml`, not `/blog/rss.xml`) |
| rainbond | CN app-platform/PaaS on k8s; interesting as a non-Western platform-engineering take. | 200, 20 entries, newest 2026-09-02 |

### Chinese (zh) — people and community

```yaml
# ── Chinese-language: people & community ────────────────────────────
- {id: jimmysong,       title: "Jimmy Song (云原生社区创始人)",     url: "https://jimmysong.io/blog/index.xml",                        lang: zh, category: person, weight: 3}
- {id: atbug,           title: "Addo Zhang (乱世浮生)",           url: "https://atbug.com/index.xml",                                lang: zh, category: person, weight: 3}
- {id: tonybai,         title: "TonyBai (Go / 云原生)",           url: "https://tonybai.com/feed/",                                  lang: zh, category: person, weight: 2}
- {id: arthurchiao,     title: "ArthurChiao (eBPF/Cilium 深度)",  url: "https://arthurchiao.art/feed.xml",                           lang: zh, category: person, weight: 3}
- {id: colobu,          title: "鸟窝 (Colobu)",                  url: "https://colobu.com/atom.xml",                                lang: zh, category: person, weight: 2}
- {id: moelove,         title: "MoeLove — K8S 生态周报 (张晋涛)",   url: "https://moelove.info/rss.xml",                               lang: zh, category: person, weight: 3}
- {id: bestblogs-cn,    title: "BestBlogs.dev — 软件编程",        url: "https://www.bestblogs.dev/feeds/rss?category=programming",   lang: zh, category: community, weight: 2}
- {id: v2ex-tech,       title: "V2EX — 技术节点",                 url: "https://www.v2ex.com/feed/tab/tech.xml",                     lang: zh, category: community, weight: 2}
- {id: hellogithub,     title: "HelloGitHub 月刊",               url: "https://hellogithub.com/rss",                                lang: zh, category: community, weight: 1}
- {id: gitee-blog,      title: "Gitee 官方博客",                  url: "https://blog.gitee.com/feed/",                               lang: zh, category: vendor, weight: 1}
- {id: ruanyifeng,      title: "阮一峰 — 科技爱好者周刊",           url: "https://www.ruanyifeng.com/blog/atom.xml",                   lang: zh, category: newsletter, weight: 2}
```

| id | why | evidence (2026-09-08) |
|---|---|---|
| jimmysong | Founder of 云原生社区 and the Istio/service-mesh translator for the whole CN scene; currently the most reliable live successor to the dead `cloudnative.to`. Recent post: "Why GPU Scheduling Matters". | 200, 50 entries, newest 2026-08-28 |
| atbug | Addo Zhang — service mesh, eBPF gateway, k8s networking, in Chinese, high frequency. | 200, 317 entries, newest 2026-09-03 |
| tonybai | Go + cloud-native systems writing with a large CN following; frequently first to analyse Go runtime/infra changes for a CN audience. | 200, 20 entries, newest 2026-09-06 |
| arthurchiao | Deep Cilium/eBPF/GPU-cluster teardowns (often translations *plus* original annotation) that Western readers never see. | 200, 10 entries, newest 2026-07-05 |
| colobu | Long-running Go/infra blog, benchmark-heavy. | 200, 20 entries, newest 2026-07-04 |
| moelove | 张晋涛's "K8S 生态周报" is the Chinese equivalent of KubeWeekly — direct competitor/complement to the digest itself. **Caveat: newest entry 2026-02-23**, i.e. the RSS has been quiet ~6 months (he has been publishing to WeChat). Keep at weight 3 but expect low volume. | 200, 259 entries, newest 2026-02-23 |
| bestblogs-cn | Aggregator with LLM-generated Chinese summaries of CN+intl engineering posts; the `?category=programming` variant filters out the site's general-news noise (the unfiltered `/feeds/rss` mixes in politics — do not use it). | 200, 100 entries, newest 2026-09-07 |
| v2ex-tech | Where CN engineers actually argue about infra/pricing/outages; a sentiment source with no Western equivalent. | 200, 40 entries, newest 2026-09-07 |
| hellogithub | Monthly OSS-discovery issue — good for "new Chinese project nobody has heard of" segments. | 200, 125 entries, newest 2026-08-28 |
| gitee-blog | Gitee is the CN GitHub alternative; its platform/DevOps announcements matter for the domestic-stack story. | 200, 10 entries, newest 2026-09-07 |
| ruanyifeng | Weekly tech roundup with the largest CN developer readership; occasionally the only Chinese-language framing of a Western infra story. | 200, 3 entries, newest 2026-09-03 (feed keeps only latest few) |

### Replacement lines for broken zh entries already in the draft

```yaml
# replaces the 404 URLs currently in feeds.yaml
- {id: karmada,         title: "Karmada 博客 (华为)",             url: "https://karmada.io/zh/blog/rss.xml",                         lang: zh, category: project, weight: 3}
- {id: kubeedge,        title: "KubeEdge Blog",                url: "https://kubeedge.io/blog/rss.xml",                           lang: en, category: project, weight: 2}
```

* `karmada`: draft URL `…/blog/index.xml` → 404. `…/blog/rss.xml` → 200, 20 entries, newest 2026-06-06.
  The `/zh/` variant carries the same posts in Chinese (verified 200, 20 entries).
* `kubeedge`: the **English section** entry also points at the dead `…/blog/index.xml` → 404.
  `…/blog/rss.xml` → 200, 37 entries, newest 2026-04-21.

### Japanese (ja)

```yaml
# ── Japanese ─────────────────────────────────────────────────────────
- {id: publickey,       title: "Publickey (新野淳一)",            url: "https://www.publickey1.jp/atom.xml",                         lang: ja, category: media, weight: 4}
- {id: zenn-k8s,        title: "Zenn — Kubernetes",             url: "https://zenn.dev/topics/kubernetes/feed",                    lang: ja, category: community, weight: 3}
- {id: zenn-sre,        title: "Zenn — SRE",                    url: "https://zenn.dev/topics/sre/feed",                           lang: ja, category: community, weight: 3}
- {id: qiita-k8s,       title: "Qiita — kubernetes タグ",        url: "https://qiita.com/tags/kubernetes/feed",                     lang: ja, category: community, weight: 2}
- {id: qiita-tf,        title: "Qiita — terraform タグ",         url: "https://qiita.com/tags/terraform/feed",                      lang: ja, category: community, weight: 2}
- {id: hatena-k8s,      title: "はてブ — kubernetes 検索",         url: "https://b.hatena.ne.jp/q/kubernetes?mode=rss",              lang: ja, category: community, weight: 2}
- {id: sreake,          title: "3-shake Sreake (SRE/k8s)",      url: "https://sreake.com/feed/",                                   lang: ja, category: vendor, weight: 3}
- {id: mercari,         title: "メルカリエンジニアリング",            url: "https://engineering.mercari.com/blog/feed.xml",              lang: ja, category: vendor, weight: 3}
- {id: iij,             title: "IIJ Engineers Blog",            url: "https://eng-blog.iij.ad.jp/feed",                            lang: ja, category: vendor, weight: 3}
- {id: sakura-knowledge,title: "さくらのナレッジ",                  url: "https://knowledge.sakura.ad.jp/feed/",                       lang: ja, category: vendor, weight: 2}
- {id: nttcom-eng,      title: "NTT docomo Business Engineers", url: "https://engineers.ntt.com/feed",                             lang: ja, category: vendor, weight: 3}
- {id: zozo,            title: "ZOZO TECH BLOG",                url: "https://techblog.zozo.com/feed",                             lang: ja, category: vendor, weight: 2}
- {id: dena,            title: "DeNA Engineering",              url: "https://engineering.dena.com/index.xml",                     lang: ja, category: vendor, weight: 2}
- {id: cookpad,         title: "クックパッド開発者ブログ",            url: "https://techlife.cookpad.com/feed",                          lang: ja, category: vendor, weight: 2}
- {id: hatena-dev,      title: "Hatena Developer Blog",         url: "https://developer.hatenastaff.com/feed",                     lang: ja, category: vendor, weight: 2}
- {id: smarthr,         title: "SmartHR Tech Blog",             url: "https://tech.smarthr.jp/feed",                               lang: ja, category: vendor, weight: 1}
- {id: moneyforward,    title: "Money Forward Developers",      url: "https://moneyforward-dev.jp/feed",                           lang: ja, category: vendor, weight: 1}
- {id: pepabo,          title: "Pepabo Tech Portal",            url: "https://tech.pepabo.com/feed.xml",                           lang: ja, category: vendor, weight: 2}
- {id: gmo-dev,         title: "GMO Developers",                url: "https://developers.gmo.jp/feed/",                            lang: ja, category: vendor, weight: 2}
- {id: mixi-dev,        title: "MIXI DEVELOPERS",               url: "https://medium.com/feed/mixi-developers",                    lang: ja, category: vendor, weight: 1}
- {id: lycorp-en,       title: "LY Corporation Tech (EN)",      url: "https://techblog.lycorp.co.jp/en/feed/index.xml",            lang: en, category: vendor, weight: 2}
```

| id | why | evidence (2026-09-08) |
|---|---|---|
| publickey | The single highest-signal Japanese infra-news site (one editor, no wire copy). Original reporting on cloud/k8s/DB moves, often with Japanese vendor angles absent in EN. | 200, 15 entries, newest 2026-09-08 |
| zenn-k8s | Zenn topic feeds are real per-topic feeds. Sample entry today: "Cluster Autoscaler のさくらクラウド provider を自作する" — a domestic-cloud CAS provider, exactly the kind of thing EN feeds never carry. | 200, 20 entries, newest 2026-09-07 |
| zenn-sre | Same mechanism for SRE; today's top item is about staged human-in-the-loop gates. | 200, 20 entries, newest 2026-09-07 |
| qiita-k8s / qiita-tf | Qiita tag feeds work (`/tags/<tag>/feed`) but are thin — 4 entries each. Cheap to poll, useful as a long tail. | 200, 4 entries each, newest 2026-09-06 / 2026-09-07 |
| hatena-k8s | `b.hatena.ne.jp/q/<kw>?mode=rss` is a keyword search feed — surfaces *what Japanese engineers are bookmarking* about k8s, i.e. an editorial signal, not just publication. | 200, 40 entries, newest 2026-09-05 |
| sreake | 3-shake's Sreake team is the most k8s/SRE-dense Japanese consultancy blog (Platform Engineering Kaigi sponsor, deep k8s posts). | 200, 100 entries, newest 2026-09-04 |
| mercari | Fixes the dead draft entry. Live example in the feed: "メルカリにおけるTiDB改善の取り組み" — TiDB index-incompatibility at Mercari scale, not published in English. | 200, 100 entries, newest 2026-08-20 |
| iij | Japanese ISP with genuinely low-level networking/infra writing. | 200, 10 entries, newest 2026-08-31 |
| sakura-knowledge | SAKURA internet's technical knowledge base — the domestic-cloud (sovereign cloud) angle. | 200, 30 entries, newest 2026-08-18 |
| nttcom-eng | NTT's engineering blog (moved from `engineering.ntt.com`, which is now NXDOMAIN) — carrier-scale infra. | 200, 30 entries, newest 2026-09-07 |
| zozo / dena / cookpad / hatena-dev / pepabo / gmo-dev | Large JP engineering orgs that publish k8s/platform migration write-ups in Japanese only. | all 200; newest 2026-09-07 / 2026-08-26 / 2026-09-02 / 2026-09-04 / 2026-09-01 / 2026-09-07 |
| smarthr / moneyforward | Weight 1 — mostly org/product content, occasional infra. | 200, 30 entries each, newest 2026-09-07 / 2026-09-01 |
| mixi-dev | Publishes JP conference reports incl. "KubeCon + CloudNativeCon Japan 2026 参加レポート". | 200, 10 entries, newest 2026-08-17 |
| lycorp-en | The draft already has the ja feed; the en feed is a distinct, smaller selection worth having for quotability. | 200, 50 entries, newest 2026-08-25 |

### Korean (ko)

```yaml
# ── Korean ───────────────────────────────────────────────────────────
- {id: toss,            title: "토스 테크 (Toss Tech)",           url: "https://toss.tech/rss.xml",                                  lang: ko, category: vendor, weight: 3}
- {id: woowahan,        title: "우아한형제들 기술블로그",            url: "https://techblog.woowahan.com/feed/",                        lang: ko, category: vendor, weight: 3}
- {id: daangn,          title: "당근 (Karrot) 기술 블로그",         url: "https://medium.com/feed/daangn",                             lang: ko, category: vendor, weight: 2}
- {id: socar,           title: "쏘카 테크 블로그",                  url: "https://tech.socar.kr/rss.xml",                              lang: ko, category: vendor, weight: 2}
```

| id | why | evidence (2026-09-08) |
|---|---|---|
| toss | Korea's fintech super-app; the most technically serious KR blog (platform, DB, reliability), zero EN syndication. | 200, 20 entries, newest 2026-09-07 |
| woowahan | Baemin — the largest KR k8s/JVM-platform publisher; today's item is about enforcing architecture rules in tests. | 200, 10 entries, newest 2026-09-07 |
| daangn | Karrot — infra/identity/platform posts in Korean on Medium (feed is Medium-hosted, so no KR-WAF risk). | 200, 10 entries, newest 2026-08-20 |
| socar | Mobility platform; note the canonical host moved to `tech.socar.kr` (`tech.socarcorp.kr` 301s there). | 200, 30 entries, newest 2026-07-26 |

### European local scenes

```yaml
# ── European local scenes ────────────────────────────────────────────
- {id: heise-dev,       title: "heise developer",               url: "https://www.heise.de/developer/feed.xml",                    lang: de, category: media, weight: 3}
- {id: linux-magazin,   title: "Linux-Magazin (DE)",            url: "https://www.linux-magazin.de/feed/",                         lang: de, category: media, weight: 2}
- {id: netways,         title: "NETWAYS Blog (Icinga/Foreman)", url: "https://blog.netways.de/feed/",                              lang: de, category: vendor, weight: 2}
- {id: inovex,          title: "inovex Blog",                   url: "https://www.inovex.de/blog/feed/",                           lang: de, category: vendor, weight: 2}
- {id: linuxfr,         title: "LinuxFr.org — dépêches",        url: "https://linuxfr.org/news.atom",                              lang: fr, category: community, weight: 2}
- {id: srobert,         title: "Stéphane Robert — DevSecOps",   url: "https://blog.stephane-robert.info/rss.xml",                  lang: fr, category: person, weight: 3}
- {id: octo,            title: "OCTO Talks !",                  url: "https://blog.octo.com/feed",                                 lang: fr, category: vendor, weight: 2}
- {id: ippon,           title: "Blog Ippon",                    url: "https://blog.ippon.fr/rss/",                                 lang: fr, category: vendor, weight: 2}
- {id: silicon-fr,      title: "Silicon.fr",                    url: "https://www.silicon.fr/feed",                                lang: fr, category: media, weight: 1}
- {id: paradigma,       title: "Paradigma Digital",             url: "https://www.paradigmadigital.com/feed/",                     lang: es, category: vendor, weight: 2}
- {id: 4linux,          title: "Blog 4Linux (BR)",              url: "https://blog.4linux.com.br/feed/",                           lang: pt, category: vendor, weight: 2}
- {id: zup,             title: "Zup Innovation (BR)",           url: "https://zup.com.br/blog/feed/",                              lang: pt, category: vendor, weight: 1}
- {id: sekurak,         title: "Sekurak (PL, security)",        url: "https://sekurak.pl/feed/",                                   lang: pl, category: media, weight: 2}
- {id: devstyle,        title: "devstyle (PL)",                 url: "https://devstyle.pl/feed",                                   lang: pl, category: person, weight: 1}
- {id: itwiz,           title: "ITwiz (PL)",                    url: "https://itwiz.pl/feed/",                                     lang: pl, category: media, weight: 1}
- {id: tweakers,        title: "Tweakers (NL)",                 url: "https://tweakers.net/feeds/mixed.xml",                       lang: nl, category: media, weight: 1}
- {id: xebia,           title: "Xebia Blog",                    url: "https://xebia.com/feed/",                                    lang: en, category: vendor, weight: 1}
```

| id | why | evidence (2026-09-08) |
|---|---|---|
| heise-dev | heise's *developer* desk does original German reporting on toolchains/cloud, distinct from the general news feed the draft already has. | 200, 20 entries, newest 2026-09-07 (`/developer/rss/news-atom.xml` 301s to this) |
| linux-magazin | Original German Linux/infra journalism, not a translation shop. | 200, 15 entries, newest 2026-09-07 |
| netways | German Icinga/Foreman/monitoring shop — writes about the European monitoring stack the US ignores. | 200, 10 entries, newest 2026-08-27 (canonical host is `blog.netways.de`) |
| inovex | German consultancy with real k8s/data-platform engineering posts. | 200, 9 entries, newest 2026-08-26 (`www.inovex.de/de/blog/feed/` 301s to `/de/feed/`) |
| linuxfr | The French FOSS community's own editorial pipeline (community-reviewed dépêches); genuinely original. | 200, 15 entries, newest 2026-09-07 |
| srobert | Best French-language DevSecOps documentation blog — Terraform/Ansible/k8s/supply-chain hardening, all original. Sample: "Chainguard Actions". | 200, 100 entries, newest 2026-07-28 (`index.xml` 301s to `rss.xml`) |
| octo | OCTO (Accenture FR) — architecture/craft posts in French. | 200, 10 entries, newest 2026-09-04 (`/rss.xml` is HTML; use `/feed`) |
| ippon | French consultancy, Java/cloud/data engineering in French. | 200, 15 entries, newest 2026-09-07 (`/feed/` 301s to `/rss/`) |
| silicon-fr | French enterprise-IT news; weight 1, mostly market/vendor news with a European regulatory angle (sovereignty, Cloud de confiance). | 200, 50 entries, newest 2026-09-07 |
| paradigma | Spanish consultancy, genuinely technical Spanish-language posts (Angular/cloud/architecture). | 200, 15 entries, newest 2026-09-04 |
| 4linux | Brazilian Linux/DevOps training company; original Portuguese content on containers/OSS. | 200, 10 entries, newest 2026-09-04 |
| zup | Brazilian engineering org, occasional platform/infra posts. | 200, 10 entries, newest 2026-09-04 |
| sekurak | The Polish security scene's reference site — original research and Polish-language incident write-ups. | 200, 10 entries, newest 2026-09-07 |
| devstyle / itwiz | PL developer-culture and PL enterprise-IT market respectively; weight 1, national-scene colour. | 200, 20/10 entries, newest 2026-09-07 both |
| tweakers | Dutch original tech journalism (their own benchmarks/reviews). Use `tweakers.net/feeds/mixed.xml` — the old FeedBurner URL is frozen at 2025-04. | 200, 40 entries, newest 2026-09-07 |
| xebia | NL-origin consultancy; content is English but the delivery/platform practice is European. Weight 1. | 200, 10 entries, newest 2026-08-26 |

**Total verified additions: 68** (Chinese: 26 of them + 2 replacement fixes → Chinese share ≥ half of new zh/ja/ko material as requested).

---

## Geo-blocked / unreachable from US runners

Verdicts from DE egress; `r.jina.ai` used as a second, different-continent datacenter vantage where it mattered.

| Source | URL | Status | Verdict / workaround |
|---|---|---|---|
| openEuler (Huawei) | `https://www.openeuler.org/en/blog/`, `/zh/blog/`, `/en/news/` | **403** from DE with browser UA and with `curl/8`; **403 also via r.jina.ai** (different ASN/continent) | Hard block — Huawei WAF rejects datacenter egress, not just US. No mirror found (site is a Vue SPA; no GitHub Pages copy). **Workaround: none automated.** Huawei's k8s output is covered instead by karmada / kubeedge / volcano / kmesh feeds. |
| CSDN | `https://blog.csdn.net/rss/list` | **521** | Origin refuses; no working RSS. None. |
| SegmentFault | `https://segmentfault.com/feeds/blogs` → **410 Gone**; `/feeds/news` → **403** (JSON) | dead + blocked | Feeds retired. None. |
| RSSHub public instance | `https://rsshub.app/*` | **403** to datacenter IPs (root and any route) | Self-host RSSHub in the workflow (docker) if you want juejin/WeChat/Zhihu bridges. Public instance is unusable from CI. |
| Wechat2RSS | `https://wechat2rss.bestblogs.dev/list` | 200 but `{"err":"k param is empty, set it as RSS_TOKEN"}` | WeChat 公众号 (字节跳动技术团队, 阿里巴巴云原生, 腾讯云原生, 美团技术团队) need a paid token or a self-hosted wechat2rss. This is the real reason ByteDance/Alibaba "tech team" content is hard to automate. |
| Kubernetes 中文社区 | `https://www.kubernetes.org.cn/feed` | **timeout** (>25 s, twice) | Site effectively unreachable from outside CN. None. |
| RIDI (KR) | `https://ridicorp.com/feed/` | **200 once, then 403 twice** in the same session | Cloudflare bot-scoring; flaky. Excluded from additions. Retry with a longer interval if wanted. |
| Kurly (KR) | `https://helloworld.kurly.com/feed.xml` | **403** | Excluded. |
| LINE Engineering (KR) | `https://engineering.linecorp.com/ko/feed/index.xml` | **403** | Content moved to LY Corp — use `techblog.lycorp.co.jp` (already proposed). |
| iMasters (BR) | `https://imasters.com.br/feed/` | **429** on every attempt | Rate-limited/blocked for datacenter IPs. Excluded. |
| linux.cn (Linux 中国) | `https://linux.cn/rss.xml` | **NXDOMAIN** (confirmed via Cloudflare DoH, Status 3) | Domain no longer resolves globally. Not geo — gone. |
| DaoCloud blog | `blog.daocloud.io` | **NXDOMAIN** (`www.daocloud.io` resolves, `/blogs` → 404) | No blog feed anymore. |
| DiDi tech | `tech.didiglobal.com` | **NXDOMAIN** | Blog shut down; DiDi publishes on WeChat only. |
| Sealer | `sealer.sh` | **NXDOMAIN** | Project effectively dead — do not add. |
| ServiceMesher | `www.servicemesher.com` | **NXDOMAIN** | Merged into 云原生社区, which is itself dead (see Objections). |
| NTT Communications | `engineering.ntt.com` | **NXDOMAIN** | Replaced by `engineers.ntt.com` (proposed above). |

**Reachable from both vantages (no geo problem):** `infoq.cn`, `oschina.net`, `v2ex.com`, `api.juejin.cn`, `tech.meituan.com`, `kubesphere.io`, `bestblogs.dev`, `hellogithub.com`, `gitee.com`, plus every project site (`karmada.io`, `kubeedge.io`, `volcano.sh`, `d7y.io`, `openkruise.io`, `koordinator.sh`, `kubevela.io`, `project-hami.io`, `sealos.io`, `rainbond.com`, `greptime.com`, `databend.com`, `starrocks.io`) — those are on global CDNs (Cloudflare/AWS/GitHub Pages) and carry no CN-only restriction.

---

## Needs scraping, not RSS

### 1. Juejin (掘金) — the single highest-value non-RSS Chinese source

Juejin's JSON API is **open, unauthenticated, and reachable from this vantage and via r.jina.ai**. This is how you get the big-company "技术团队" accounts the host asked for.

* **List a company's posts** — `POST https://api.juejin.cn/content_api/v1/article/query_list`
  `Content-Type: application/json`, body `{"user_id":"<uid>","sort_type":2,"cursor":"0","limit":20}`
  Response: `data[].article_info` → `article_id`, `title`, `brief_content`, `ctime` (unix seconds), `mtime`.
  Item URL = `https://juejin.cn/post/<article_id>`. Verified 200 with JSON payload.
* **Resolve an account id** — `GET https://api.juejin.cn/search_api/v1/search?query=<名称>&id_type=1&cursor=0&limit=3` (verified, `err_no: 0`).
* **Site-wide recommended feed** — `POST https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed?aid=2608`, body `{"id_type":2,"client_type":2608,"sort_type":200,"cursor":"0","limit":20}` → 200, ~95 KB JSON.

Verified account ids and freshness (2026-09-08):

| Account | user_id | latest post | recommend? |
|---|---|---|---|
| 美团技术团队 | `3509296845313741` | 2026-08-27 | **yes** — this is the working substitute for the broken tech.meituan.com dates |
| 腾讯云开发者 | `3456520257538830` | 2026-09-04 | **yes** — substitute for the SPA-only Tencent Cloud community |
| 京东云开发者 | `2634854380340008` | 2026-09-03 | yes |
| vivo互联网技术 | `993614243303053` | 2026-09-03 | yes |
| 得物技术 | `2392954206960247` | 2026-09-03 | yes |
| 百度Geek说 | `4186596000416094` | 2026-09-04 | yes |
| 快手技术 | `3736571181793721` | 2026-06-16 | marginal |
| 字节跳动技术团队 | `1838039172387262` | 2025-07-21 | **stale** — ByteDance stopped posting to juejin; they publish to WeChat 公众号 now |
| 阿里云开发者 | `407250135423447` | 2024-09-13 | stale |
| 小红书技术REDtech | `899824537578279` | 2024-07-02 | stale |
| 网易云音乐技术团队 | `4265760847567016` | 2026-03-31 | marginal |
| 携程技术 | `149189310818861` | 2023-12-21 | dead |

Implementation note: this needs a small `fetch_juejin()` collector alongside `fetch_reddit()` — it cannot go into `feeds.yaml` as-is because `fetch_feeds()` only does GET+feedparser.

### 2. SPA sites with no feed and no server-rendered HTML

Verified: the HTML returned contains no article links and no `__NEXT_DATA__`/JSON island, so these need a headless browser or a reverse-engineered XHR.

| Source | URL to poll | What to extract | Note |
|---|---|---|---|
| Volcano Engine 火山引擎 开发者社区 | `https://developer.volcengine.com/articles` | article cards → title, `/articles/<id>` link, date | SPA. Every unknown path (incl. `/rss`, `/articles/rss`) returns the 200 app shell — do not mistake that for a feed. |
| ByteDance Open Source | `https://opensource.bytedance.com/` | blog list | 1,395-byte shell; JS on `lf-opensource.bytetos.com`. Headless required. |
| Tencent Cloud 开发者社区 | `https://cloud.tencent.com/developer/column` | article list | Every path returns 200 HTML shell (`/developer/rss` included). **Prefer the juejin 腾讯云开发者 account instead.** |
| 阿里云开发者社区 | `https://developer.aliyun.com/` | feed cards (`.feed-item-content-title`) | No RSS anywhere: `/rsspage.htm`, `/rss`, `/rss/all`, `/feed` all 404. Only class names contain "feed". |
| 美团技术团队 | `https://tech.meituan.com/` | post list + dates | The RSS at `/feed/` (→ `/rss.xml`) parses, but **items carry no `<pubDate>`** — only the channel does. `fetch_feeds()` drops every dated-less entry, so this feed silently yields 0 items. Scrape the index or use juejin. |
| KubeSphere | `https://kubesphere.io/zh/blogs/` | post list + dates | RSS parses (179 entries) but **every `<pubDate>` is `Mon, 01 Jan 0001`** → all entries dropped by the collector. |
| Higress | `https://higress.io/blog/` (and `higress.cn`) | post list | No feed at any of `/blog/index.xml`, `/blog/rss.xml`, `/rss.xml`, `/{zh-cn,en}/blog/rss.xml` — all 404. HTML has no `rel=alternate`. |
| JuiceFS | `https://juicefs.com/en/blog/` | post list | Next.js, no feed at `feed.xml`/`rss.xml` in either locale; no `__NEXT_DATA__` in the HTML. |
| Zilliz / Milvus | `https://zilliz.com/blog`, `https://milvus.io/blog/` | post list | `zilliz.com/blog/{rss.xml,feed}` 404; `milvus.io/blog/*` returns a 302 with an empty Location (redirect loop). |
| StreamNative | `https://streamnative.io/blog` | post list | `/blog/rss.xml`, `/blog/feed` 404; no `rel=alternate`. |
| SmartX | `https://www.smartx.com/blog/` | post list | `/blog/feed` 404; no `rel=alternate`. Chinese HCI vendor — relevant to the VMware-replacement thread. |
| CubeFS | `https://cubefs.io/blog/` | post list | `/blog/rss.xml` returns 200 **text/html** (SPA shell); TLS also flaky from here. |
| Kube-OVN (Alauda) | `https://www.kube-ovn.io/` | post list | `/blog/` 404s; docs-only site. |
| Huawei Cloud 博客 | `https://bbs.huaweicloud.com/blogs` | `href="/blogs/<id>"` + titles | **Server-rendered** — plain HTML scraping works (verified article hrefs present). No RSS. Reachable (unlike openeuler.org). |
| openGauss | `https://opengauss.org/zh/blogs/` | post list | VitePress; content lives in `assets/*.md.js` chunks. Messy but possible. |
| Kmesh (Huawei eBPF mesh) | `https://kmesh.net/` | blog list | Page advertises "RSS"/`rss.xml` in markup but `/rss.xml`, `/blog/index.xml`, `/en/blog/index.xml` all 404. Scrape `/blog/`. |
| 51CTO | `https://blog.51cto.com/` | post list | `/rss` returns the HTML shell. |
| KakaoPay (KR) | `https://tech.kakaopay.com/` | post list | `rss.xml` returns a **valid but empty** RSS channel (238 bytes, zero items) — a silent no-op if added. |

---

## Objections — problems with the existing zh/ja/ko entries in the draft

All 18 existing entries were tested. **8 of 11 Chinese entries and 1 of 7 JP/KR entries are broken.**

| # | Entry | Problem | Fix |
|---|---|---|---|
| 1 | `alibaba-cn` → `developer.aliyun.com/rsspage.htm` | **HTTP 404.** Aliyun retired RSS entirely (`/rss`, `/rss/all`, `/feed` all 404 too). | Delete. Replace with the Alibaba project feeds proposed above (dragonfly / openkruise / kubevela / koordinator) + optionally the juejin scraper. |
| 2 | `cloudwego` → `cloudwego.io/blog/index.xml` | **HTTP 404.** Hugo site publishes only a site-wide feed. | `https://www.cloudwego.io/index.xml` (200, 50 entries, newest 2026-05-08); filter items whose link contains `/blog/`. |
| 3 | `bytedance-oss` → `opensource.bytedance.com/blog/rss.xml` | **HTTP 200 but it is the SPA HTML shell** (1,395 bytes, 0 entries). Worst kind of failure: the collector logs no error and silently contributes nothing. Same for `/feed` and `/index.xml`. | Delete from `feeds.yaml`; move to the scraping list. |
| 4 | `kubesphere` → `kubesphere.io/blogs/index.xml` | Parses (47 entries) but **all `<pubDate>` are `0001-01-01`** → `fetch_feeds()` drops every item (`if pub is None or not (start <= pub <= end)`). Contributes zero, forever. The `/zh/blogs/index.xml` variant has 179 entries with the same broken dates. | Either scrape, or special-case the feed with position-based freshness. Do not leave as-is. |
| 5 | `cloudnative-to` → `cloudnative.to/index.xml` | **Dead.** The domain now serves a 114-byte JS redirect stub to `/lander` — it is a parked/landing page. 云原生社区's own site is gone. | Delete. Closest live replacements: `jimmysong.io` (community founder) and `atbug.com`, both proposed above. |
| 6 | `higress` → `higress.io/blog/index.xml` | **HTTP 404** — and so are `/blog/rss.xml`, `/rss.xml`, `/zh-cn/blog/rss.xml`, `/en/blog/rss.xml`, plus every equivalent on `higress.cn`. No feed exists. | Delete; scrape `https://higress.io/blog/` if the project matters. |
| 7 | `karmada` → `karmada.io/blog/index.xml` | **HTTP 404** (Docusaurus, not Hugo). | `https://karmada.io/zh/blog/rss.xml` (zh) or `https://karmada.io/blog/rss.xml` (en) — 200, 20 entries, newest 2026-06-06. |
| 8 | `tencentcloud` → `cloud.tencent.com/developer/rss` | **HTTP 200 but HTML** (29 KB SPA shell, 0 entries). Another silent zero. Note every path under `/developer/` returns 200 HTML, so path-probing will not find a feed. | Delete; use the juejin 腾讯云开发者 account (fresh, 2026-09-04). |
| 9 | `pingcap` | Works (200, 10 entries, newest 2026-09-03) but the content is **English**, and it is tagged `lang: zh`. That mislabels every item for `detect_lang()`'s default and for any per-language section in the digest. | Change to `lang: en` (keep the entry). Same issue applies if you add databend/starrocks/greptime — I tagged those `en` above. |
| 10 | `infoq-cn` | Works (200, 20 entries, newest 2026-09-07). **But** `/feed/topic/<anything>` returns the identical site-wide feed — do not add topic variants thinking they are filtered; you would just duplicate items. | Keep as-is; do not add topic feeds. |
| 11 | `oschina` | Works: 200, 50 entries, newest 2026-09-07. High churn (50 items over ~4 days) — consider weight 2 as set, and rely on filters. | Keep. |
| 12 | `hatena-it` | Works: 200, 30 entries, newest 2026-09-07. It is the general IT hotentry, so mostly non-infra. | Keep at weight 3, but add the keyword feed (`hatena-k8s`) which is far more targeted. |
| 13 | `cybozu` | Works: 200, 30 entries, newest 2026-09-04. | Keep. |
| 14 | `mercari` → `engineering.mercari.com/en/blog/feed.xml` | **HTTP 200 with a zero-byte body.** Third silent zero in the draft. The English section of Mercari's blog no longer emits a feed. | `https://engineering.mercari.com/blog/feed.xml` (ja) — 200, 100 entries, newest 2026-08-20. `lang: ja`. |
| 15 | `cyberagent` | Works: 200, 6 entries, newest 2026-09-07. | Keep. |
| 16 | `linegoogle` (LY Corp) | Works: 200, 50 entries, newest 2026-09-03. The **id is misleading** (`linegoogle` — there is no Google involvement; it is LINE + Yahoo Japan). | Rename id to `lycorp`; optionally add the EN feed as a separate entry. |
| 17 | `kakao` | Works: 200, 10 entries, newest 2026-09-06, but the feed is mostly corporate/conference announcements, not engineering. | Keep at weight 2; Toss and Woowahan (proposed) carry the actual engineering. |
| 18 | `naverd2` | Works: 200, 20 entries, newest 2026-09-03. | Keep. |

### Bonus objections found in the English sections while checking overlaps

| Entry | Problem |
|---|---|
| `kubeedge` (English section) → `kubeedge.io/blog/index.xml` | **HTTP 404** — same Docusaurus mistake as `karmada`. Use `https://kubeedge.io/blog/rss.xml` (200, 37 entries, newest 2026-04-21). |
| `api7` (English section) → `api7.ai/blog/rss.xml` | **HTTP 404** (so is `/blog/feed.xml`). Replace with `https://apisix.apache.org/blog/rss.xml` (200, 20 entries, newest 2026-08-31) or the zh variant proposed above. |
| `hetzner` (English section) → `hetzner.com/blog/feed/` | **HTTP 200 but HTML** (36 KB, 0 entries) — silent zero. |
| `heise-open` (English section) → `heise.de/rss/heise-atom.xml` | Works (200, 151 entries) but that URL is heise's **general news** feed, not the open-source rubric (`heise-Rubrik-Open-Source.rdf` is 404). The title promises filtering the feed does not do — expect a lot of consumer-tech noise at weight 2. |

### Cross-cutting recommendation

Two failure modes account for most of the dead weight above: **404s** (loud, easy to catch) and **"200 with HTML or with unusable dates"** (silent). Add a CI assertion to the collector — for each feed, fail the run if `feedparser` yields 0 entries **or** if no entry has a parsable date — otherwise these entries sit in `feeds.yaml` for months contributing nothing. Three of the draft's 18 zh/ja/ko entries fail silently today.

### Verified-but-stale (checked, deliberately not proposed)

`sofastack.tech/blog/index.xml` (200, 512 entries, newest 2025-02-18) · `icloudnative.io/index.xml` (2024-07) ·
`qikqiak.com/index.xml` (2025-03) · `nacos.io/blog/rss.xml` (2023-12) · `openyurt.io/blog/rss.xml` (2022-06) ·
`chaos-mesh.org/blog/rss.xml` (2022-06) · `kcl-lang.io/blog/rss.xml` (2024-12) · `kuasar.io/blog/index.xml` (2024-03) ·
`openelb.io/blog/index.xml` (2021) · `byconity.github.io/blog/rss.xml` (2023-09) · `opendal.apache.org/blog/rss.xml` (2025-09) ·
`xuanwo.io/index.xml` (2026-01) · `alibabatech.medium.com/feed` (2023-03) · `medium.com/feed/coupang-engineering` (2024-10) ·
`tech.kakaoenterprise.com/rss` (2023-05) · `blog.banksalad.com/rss.xml` (2026-01) · `hyperconnect.github.io/feed.xml` (2026-04) ·
`medium.com/feed/29cm` (2025-06) · `medium.com/feed/naver-place-dev` (2025-11) · `genbeta.com/feedburner.xml` (2025-12) ·
`feeds.feedburner.com/tweakers/mixed` (2025-04, superseded by `tweakers.net/feeds/mixed.xml`).
