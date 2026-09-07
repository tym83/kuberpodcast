# Review #2 — English-language coverage gaps

Reviewer: #2 (English coverage). Date of verification: **2026-09-07/08**.

Every URL below was fetched with `curl -sSL` (browser UA, 25s timeout). Recorded evidence =
HTTP status + entry count in the document + newest `<pubDate>/<updated>` seen. Anything whose
newest item is older than ~6 months is explicitly flagged `LOW-FREQ`.

> **Read the Objections section first.** 68 of the 184 URLs in the `feeds.yaml` draft I was
> given (37%) did not resolve to a feed. That is a bigger problem than any gap.

> **Overlap note.** My sweep ran against the original 184-entry draft, before reviewers 1/3/4
> were merged (302 feeds, 44 URLs repaired, 17 dead feeds removed). Sections marked below may
> therefore already be handled — reconcile before applying:
> - **Objections §1** (broken URLs + verified replacements): likely overlaps the 44 repairs.
>   Apply only the rows still broken in the merged file; the replacement URLs and their
>   evidence are independently verified either way.
> - **API sources**: the k8s CVE feed, GitHub advisories, oss-security, CNCF TOC and KEP
>   polling rows are already implemented per the coordinator — skip those five and take the
>   remaining rows (landscape `full.json`, sig-release directory, endoflife.date, Artifact Hub,
>   FOSDEM/Sched, cloud release-note feeds, the zero-auth `releases.atom` fallback).
> - **Additions / releases.yaml additions / Objections §2–4**: the core of my brief, no known
>   overlap.

---

## Additions

### foundation — foundations, consortia, standards bodies

```yaml
- {id: letsencrypt,     title: "Let's Encrypt / ISRG",           url: "https://letsencrypt.org/feed.xml",                          lang: en, category: foundation, weight: 4}
- {id: ietf-blog,       title: "IETF Blog",                       url: "https://www.ietf.org/blog/feed/",                           lang: en, category: foundation, weight: 3}
- {id: apnic,           title: "APNIC Blog",                      url: "https://blog.apnic.net/feed/",                              lang: en, category: foundation, weight: 4}
- {id: ripe-labs,       title: "RIPE Labs",                       url: "https://labs.ripe.net/rss/",                                lang: en, category: foundation, weight: 3}
- {id: cisa-advisories, title: "CISA Advisories",                 url: "https://www.cisa.gov/cybersecurity-advisories/all.xml",     lang: en, category: foundation, weight: 3}
- {id: ccc,             title: "Confidential Computing Consortium", url: "https://confidentialcomputing.io/feed/",                  lang: en, category: foundation, weight: 3}
- {id: spdx,            title: "SPDX (SBOM standard)",            url: "https://spdx.dev/feed/",                                    lang: en, category: foundation, weight: 2}
- {id: bytecodealliance,title: "Bytecode Alliance",               url: "https://bytecodealliance.org/feed.xml",                     lang: en, category: foundation, weight: 3}
- {id: ocp,             title: "Open Compute Project",            url: "https://www.opencompute.org/blog/rss",                      lang: en, category: foundation, weight: 3}
- {id: lfnetworking,    title: "LF Networking",                   url: "https://www.lfnetworking.org/feed/",                        lang: en, category: foundation, weight: 2}
- {id: lfaidata,        title: "LF AI & Data",                    url: "https://lfaidata.foundation/feed/",                         lang: en, category: foundation, weight: 3}
- {id: osi,             title: "Open Source Initiative",          url: "https://opensource.org/feed",                               lang: en, category: foundation, weight: 2}
- {id: conservancy,     title: "Software Freedom Conservancy",    url: "https://sfconservancy.org/feeds/news/",                     lang: en, category: foundation, weight: 2}
- {id: csa,             title: "Cloud Security Alliance",         url: "https://cloudsecurityalliance.org/blog/feed",               lang: en, category: foundation, weight: 2}
- {id: cisecurity,      title: "CIS (Benchmarks)",                url: "https://www.cisecurity.org/feed",                           lang: en, category: foundation, weight: 2}
- {id: lf-events,       title: "Linux Foundation Events (CFP/schedules)", url: "https://events.linuxfoundation.org/feed/",          lang: en, category: foundation, weight: 3}
- {id: planet-kernel,   title: "Planet Kernel (kernel devs)",     url: "https://planet.kernel.org/rss20.xml",                       lang: en, category: foundation, weight: 3}
- {id: cncf-tag-sec,    title: "CNCF TAG Security",               url: "https://tag-security.cncf.io/index.xml",                    lang: en, category: foundation, weight: 3}
```

| id | why it matters | evidence |
|---|---|---|
| `letsencrypt` | ACME/cert-automation policy changes (short-lived certs, IP certs, profile changes) break k8s cert-manager pipelines. Nobody else announces them. | 200, 121 entries, newest 2026-08-11 |
| `ietf-blog` | The only official channel for protocol-level news your audience runs on (HTTP/3, QUIC, MoQ, post-quantum TLS). | 200, 597 entries, newest 2026-09-01 |
| `apnic` | Best free source of deep networking analysis (BGP, DNS, routing security, IPv6). Vendor-neutral. | 200, 30 entries, newest 2026-09-04 |
| `ripe-labs` | European counterpart of APNIC; measurement/RPKI/DNS work. | 200, 15 entries, newest 2026-09-04 |
| `cisa-advisories` | Authoritative ICS/enterprise advisories; the ones that matter to infra teams show up here first. | 200, 30 entries, newest 2026-09-04 |
| `ccc` | The standards body for confidential computing — SEV-SNP/TDX/attestation news that no vendor blog covers neutrally. Explicitly requested. | 200, 10 entries, newest 2026-09-02 |
| `spdx` | SBOM format governance. LOW-FREQ but a spec change is a whole segment. | 200, 10 entries, newest 2026-06-30 — LOW-FREQ |
| `bytecodealliance` | Wasm component model / WASI governance; the source for `wasmtime`, WASI 0.3 news. | 200, 10 entries, newest 2026-07-27 |
| `ocp` | Open Compute Project = bare-metal/DC hardware standards (rack power, 800VDC for AI racks, NIC specs). Directly feeds the AI-infra segment. | 200, 582 entries, newest 2026-09-01 |
| `lfnetworking` | Missing sibling of LF Edge which you already have. | 200, 10 entries, newest 2026-08-26 |
| `lfaidata` | Where AI-infra projects (Milvus, Flyte, Kubeflow-adjacent) get graduation/incubation news. | 200, 10 entries, newest 2026-09-03 |
| `osi` | Licence fights (OSI AI definition, source-available relicensing) are recurring podcast material. | 200, 10 entries, newest 2026-08-17 |
| `conservancy` | The other side of the same fights (Vizio/GPL, funding of infra projects). | 200, 10 entries, newest 2026-08-31 |
| `csa` | Cloud-security guidance and CCM updates; occasionally the first mover on k8s posture standards. | 200, 20 entries, newest 2026-09-02 |
| `cisecurity` | CIS Benchmarks for Kubernetes/Docker/Linux — every hardening conversation starts here. | 200, 50 entries, newest 2026-09-01 |
| `lf-events` | CFP openings + schedule releases for KubeCon/OSS Summit/Open Source Summit. This is your conference-calendar feed. | 200, 10 entries, newest 2026-08-05 |
| `planet-kernel` | Aggregate of kernel maintainers' own blogs (Brauner, Konstantin, Kroah-Hartman contributors). Cheap way to catch kernel/container-runtime posts without 20 feeds. | 200, 60 entries, newest 2026-08-26 |
| `cncf-tag-sec` | TAG Security outputs (assessments, whitepapers, supply-chain guidance). LOW-FREQ but high authority — you asked specifically for CNCF TAG output. | 200, 11 entries, newest 2025-10-05 — LOW-FREQ |

### person — individual engineers / visionaries

```yaml
- {id: cks,             title: "Chris Siebenmann (utcc)",         url: "https://utcc.utoronto.ca/~cks/space/blog/?atom",            lang: en, category: person, weight: 4}
- {id: brauner,         title: "Christian Brauner (kernel/containers)", url: "https://people.kernel.org/brauner/feed/",             lang: en, category: person, weight: 4}
- {id: ariadne,         title: "Ariadne Conill",                  url: "https://ariadne.space/feed/",                               lang: en, category: person, weight: 3}
- {id: lorinh,          title: "Lorin Hochstein (Surfing Complexity)", url: "https://surfingcomplexity.blog/feed/",                 lang: en, category: person, weight: 4}
- {id: allspaw,         title: "John Allspaw / Adaptive Capacity Labs", url: "https://adaptivecapacitylabs.com/blog/feed/",         lang: en, category: person, weight: 4}
- {id: ferd,            title: "Fred Hebert (ferd.ca)",           url: "https://ferd.ca/feed.rss",                                  lang: en, category: person, weight: 4}
- {id: lethain,         title: "Will Larson (Irrational Exuberance)", url: "https://lethain.com/feeds/",                            lang: en, category: person, weight: 3}
- {id: eatonphil,       title: "Phil Eaton",                      url: "https://notes.eatonphil.com/rss.xml",                       lang: en, category: person, weight: 4}
- {id: muratbuffalo,    title: "Murat Demirbaş (Metadata)",       url: "https://muratbuffalo.blogspot.com/feeds/posts/default",     lang: en, category: person, weight: 4}
- {id: smalldatum,      title: "Mark Callaghan (Small Datum)",    url: "https://smalldatum.blogspot.com/feeds/posts/default",       lang: en, category: person, weight: 3}
- {id: jackvanlightly,  title: "Jack Vanlightly",                 url: "https://jack-vanlightly.com/blog?format=rss",               lang: en, category: person, weight: 4}
- {id: bgrant,          title: "Brian Grant (Kubernetes co-founder)", url: "https://medium.com/feed/@bgrant0607",                   lang: en, category: person, weight: 4}
- {id: adrianco,        title: "Adrian Cockcroft",                url: "https://adrianco.medium.com/feed",                          lang: en, category: person, weight: 3}
- {id: ipspace,         title: "Ivan Pepelnjak (ipSpace)",        url: "https://blog.ipspace.net/index.xml",                        lang: en, category: person, weight: 4}
- {id: berthub,         title: "Bert Hubert",                     url: "https://berthub.eu/articles/index.xml",                     lang: en, category: person, weight: 3}
- {id: filippo,         title: "Filippo Valsorda",                url: "https://words.filippo.io/rss/",                             lang: en, category: person, weight: 4}
- {id: xeiaso,          title: "Xe Iaso",                         url: "https://xeiaso.net/blog.rss",                               lang: en, category: person, weight: 3}
- {id: lemire,          title: "Daniel Lemire",                   url: "https://lemire.me/blog/feed/",                              lang: en, category: person, weight: 3}
- {id: drewdevault,     title: "Drew DeVault",                    url: "https://drewdevault.com/blog/index.xml",                    lang: en, category: person, weight: 2}
- {id: davetf,          title: "David Anderson (Tailscale)",      url: "https://blog.dave.tf/index.xml",                            lang: en, category: person, weight: 3}
- {id: matduggan,       title: "Mathew Duggan",                   url: "https://matduggan.com/rss/",                                lang: en, category: person, weight: 3}
- {id: nickjanetakis,   title: "Nick Janetakis",                  url: "https://nickjanetakis.com/atom.xml",                        lang: en, category: person, weight: 2}
- {id: vickiboykis,     title: "Vicki Boykis",                    url: "https://vickiboykis.com/index.xml",                         lang: en, category: person, weight: 3}
- {id: antirez,         title: "Salvatore Sanfilippo (antirez)",  url: "https://antirez.com/rss",                                   lang: en, category: person, weight: 3}
- {id: majorhayden,     title: "Major Hayden",                    url: "https://major.io/index.xml",                                lang: en, category: person, weight: 2}
- {id: nelhage,         title: "Nelson Elhage",                   url: "https://blog.nelhage.com/atom.xml",                         lang: en, category: person, weight: 3}
- {id: alexellis,       title: "Alex Ellis (OpenFaaS)",           url: "https://blog.alexellis.io/rss/",                            lang: en, category: person, weight: 3}
- {id: travisdowns,     title: "Travis Downs (performance)",      url: "https://travisdowns.github.io/feed.xml",                    lang: en, category: person, weight: 2}
- {id: easyperf,        title: "Denis Bakhvalov (Easyperf)",      url: "https://easyperf.net/feed.xml",                             lang: en, category: person, weight: 2}
```

| id | why it matters | evidence |
|---|---|---|
| `cks` | Chris Siebenmann has posted near-daily sysadmin/Linux/systemd/ZFS field notes for 20 years. Single highest-volume source of "actually operating things" writing in English. | 200, 100 entries, newest 2026-09-07 |
| `brauner` | Linux VFS/namespaces/`pidfd` co-maintainer, ex-LXC. His posts *are* the container-runtime roadmap (mount API, `idmapped mounts`, `openat2`). Note: `brauner.io/feed.xml` is stale since 2024-12; the live one is on people.kernel.org. | 200, 6 entries, newest 2026-09-07 |
| `ariadne` | Alpine/musl and supply-chain internals; writes the uncomfortable posts about distro packaging and OSS sustainability. | 200, 25 entries, newest 2026-09-01 |
| `lorinh` | The most cited working writer on incident analysis and resilience engineering. Direct fit for the SRE segment; you currently have Charity Majors and nobody else. | 200, 10 entries, newest 2026-09-02 |
| `allspaw` | The other half of that field (Etsy, "how complex systems fail" school). Slower cadence, always a talking point. | 200, 30 entries, newest 2026-08-25 |
| `ferd` | Fred Hebert — resilience, on-call, "the review is the work". Erlang/BEAM ops background. | 200, 5 entries, newest 2026-08-10 |
| `lethain` | Will Larson (ex-Stripe/Calm/Carta CTO) — infra strategy, platform-team org design, LLM-infra economics. | 200, 10 entries, newest 2026-08-11 |
| `eatonphil` | Databases/distributed systems internals, writes 2–4×/month and runs the largest DB-internals reading group. | 200, 202 entries, newest 2026-09-06 |
| `muratbuffalo` | Distributed-systems professor who reviews every important paper (Raft/Paxos/spanner-likes) in plain English. Feeds the "why" segments. | 200, 25 entries, newest 2026-09-07 |
| `smalldatum` | Mark Callaghan (ex-Meta/MySQL/RocksDB) — the only person publishing rigorous, reproducible storage-engine benchmarks. | 200, 25 entries, newest 2026-09-07 |
| `jackvanlightly` | Streaming/log storage internals (Kafka, object-storage-backed brokers, S3 Express). The reference for "why is Kafka moving to S3". | 200, 20 entries, newest 2026-08-28 |
| `bgrant` | Kubernetes co-founder / original API lead. Writes the retrospectives on why k8s APIs, config and Borg heritage are shaped the way they are. Nearest thing you'll get to a Hockin/Coleman feed. | 200, 10 entries, newest 2026-08-17 |
| `adrianco` | Netflix-cloud-architecture originator, now writing on sustainability + AI-infra capacity. | 200, 10 entries, newest 2026-09-02 |
| `ipspace` | Ivan Pepelnjak — the network-engineering conscience of the cloud world; regularly demolishes k8s networking marketing. Very high volume (1024 entries). | 200, 1024 entries, newest 2026-09-04 |
| `berthub` | PowerDNS author; DNS, EU tech policy, protocol internals. | 200, 372 entries, newest 2026-09-06 |
| `filippo` | Go cryptography lead (ex-Google), age/mkcert author. Supply-chain + Go module security news lands here first. | 200, 10 entries, newest 2026-07-26 |
| `xeiaso` | Practical infra writing (Nix, Tailscale, self-hosting, anti-scraper infra); frequent HN front page. | 200, 10 entries, newest 2026-09-06 |
| `lemire` | Performance engineering / SIMD / parsing throughput. Your Brendan-Gregg complement on the userspace side. | 200, 40 entries, newest 2026-09-05 |
| `drewdevault` | Opinionated OSS-infrastructure and sourcehut operations; reliably generates discussion. | 200, 32 entries, newest 2026-07-23 |
| `davetf` | David Anderson, ex-Google SRE, built Tailscale's networking. Deep NAT-traversal/L3 posts. | 200, 14 entries, newest 2026-08-08 |
| `matduggan` | Working platform engineer; sharp, contrarian takes on k8s/cloud tooling that get picked up widely. | 200, 15 entries, newest 2026-08-28 |
| `nickjanetakis` | Weekly, practical Docker/deployment content — good for the "hands-on tip" slot. | 200, 25 entries, newest 2026-09-01 |
| `vickiboykis` | ML-infra pragmatism (embeddings, vector DBs, "what actually runs in prod"). Bridges your AI-infra beat. | 200, 20 entries, newest 2026-09-01 |
| `antirez` | Redis creator, back to writing on Redis/Valkey internals and vector sets. Directly relevant to the Redis/Valkey licence storyline. | 200, 100 entries, newest 2026-07-28 |
| `majorhayden` | Red Hat kernel/infra engineer; Linux ops and hardware notes. | 200, 25 entries, newest 2026-08-05 |
| `nelhage` | Ex-Stripe, systems/performance/debugging essays. LOW-FREQ but every post is a segment. | 200, 98 entries, newest 2026-03-23 — LOW-FREQ |
| `alexellis` | OpenFaaS/arkade/inlets author; writes on self-hosted CI, arm64 build farms, actual OSS-funding economics. | 200, 15 entries, newest 2026-06-17 — LOW-FREQ |
| `travisdowns` | Micro-architecture and CPU performance measurement. Rare posts, canonical when they appear. | 200, 10 entries, newest 2026-04-01 — LOW-FREQ |
| `easyperf` | Denis Bakhvalov, author of *Performance Analysis and Tuning on Modern CPUs*. | 200, 10 entries, newest 2025-11-10 — LOW-FREQ, keep at weight 2 |

**Individuals I looked for and could NOT add (no working feed — do not chase these):**
Tim Hockin, Kelsey Hightower, Clayton Coleman, Jordan Liggitt, Aaron Crickenberger — none
publish a blog with a feed; they publish in GitHub/X only (see API sources for a substitute).
Andrii Nakryiko (`nakryiko.com`) — site has no discoverable feed (`/rss.xml`, `/index.xml`,
`/feed.xml`, `/rss/` all 404). Liz Rice — `lizrice.com` has no feed. Michael Hausenblas —
no feed. Cindy Sridharan (`medium/@copyconstruct`) — feed works but newest post 2022-04, dead.
Ahmet Alp Balkan (`https://ahmet.im/blog/feed/rss.xml`, 200, newest 2025-07-09) — stale, skip.
Dan Slimmon — feed 200 but newest 2025-06-25, stale.

### vendor — infrastructure, database, security, observability engineering blogs

```yaml
# Databases / storage / streaming internals
- {id: confluent,       title: "Confluent Blog",                  url: "https://www.confluent.io/rss.xml",                          lang: en, category: vendor, weight: 3}
- {id: warpstream,      title: "WarpStream Blog",                 url: "https://www.warpstream.com/blog/rss.xml",                   lang: en, category: vendor, weight: 3}
- {id: redpanda,        title: "Redpanda Blog",                   url: "https://www.redpanda.com/blog/rss.xml",                     lang: en, category: vendor, weight: 3}
- {id: scylladb,        title: "ScyllaDB Blog",                   url: "https://www.scylladb.com/feed/",                            lang: en, category: vendor, weight: 3}
- {id: crunchydata,     title: "Crunchy Data (Postgres)",         url: "https://www.crunchydata.com/blog/rss.xml",                  lang: en, category: vendor, weight: 3}
- {id: supabase,        title: "Supabase Blog",                   url: "https://supabase.com/rss.xml",                              lang: en, category: vendor, weight: 2}
- {id: tigerbeetle,     title: "TigerBeetle Blog",                url: "https://tigerbeetle.com/blog/atom.xml",                     lang: en, category: vendor, weight: 3}
- {id: materialize,     title: "Materialize Blog",                url: "https://materialize.com/rss.xml",                           lang: en, category: vendor, weight: 2}
- {id: questdb,         title: "QuestDB Blog",                    url: "https://questdb.com/rss.xml",                               lang: en, category: vendor, weight: 2}
- {id: tigris,          title: "Tigris Data Blog",                url: "https://www.tigrisdata.com/blog/rss.xml",                   lang: en, category: vendor, weight: 2}
- {id: dbos,            title: "DBOS Blog",                       url: "https://www.dbos.dev/blog/rss.xml",                         lang: en, category: vendor, weight: 2}
- {id: mongodb,         title: "MongoDB Blog",                    url: "https://www.mongodb.com/blog/rss",                          lang: en, category: vendor, weight: 2}
# Storage / hardware / bare metal
- {id: backblaze,       title: "Backblaze Blog (Drive Stats)",    url: "https://www.backblaze.com/blog/feed/",                      lang: en, category: vendor, weight: 3}
- {id: storagereview,   title: "StorageReview",                   url: "https://www.storagereview.com/feed",                        lang: en, category: vendor, weight: 2}
- {id: veeam,           title: "Veeam Blog",                      url: "https://www.veeam.com/blog/feed/",                          lang: en, category: vendor, weight: 2}
- {id: amd-rocm,        title: "AMD ROCm Blogs",                  url: "https://rocm.blogs.amd.com/blog/atom.xml",                  lang: en, category: vendor, weight: 3}
- {id: collabora,       title: "Collabora (kernel/Mesa)",         url: "https://www.collabora.com/feed",                            lang: en, category: vendor, weight: 2}
# Virtualization
- {id: qemu,            title: "QEMU Blog",                       url: "https://www.qemu.org/feed.xml",                             lang: en, category: vendor, weight: 3}
- {id: vmware-vcf,      title: "VMware Cloud Foundation Blog",    url: "https://blogs.vmware.com/cloud-foundation/feed/",           lang: en, category: vendor, weight: 3}
- {id: opennebula,      title: "OpenNebula Blog",                 url: "https://www.opennebula.io/feed/",                           lang: en, category: vendor, weight: 2}
- {id: proxmox-forum,   title: "Proxmox Forum (releases)",        url: "https://forum.proxmox.com/forums/-/index.rss",              lang: en, category: community, weight: 2}
# Security / supply chain
- {id: dd-seclabs,      title: "Datadog Security Labs",           url: "https://securitylabs.datadoghq.com/rss/feed.xml",           lang: en, category: vendor, weight: 4}
- {id: trailofbits,     title: "Trail of Bits Blog",              url: "https://blog.trailofbits.com/feed/",                        lang: en, category: vendor, weight: 4}
- {id: socketdev,       title: "Socket.dev Blog",                 url: "https://socket.dev/api/blog/feed.atom",                     lang: en, category: vendor, weight: 3}
- {id: endorlabs,       title: "Endor Labs Blog",                 url: "https://www.endorlabs.com/blog/rss.xml",                    lang: en, category: vendor, weight: 2}
- {id: gitguardian,     title: "GitGuardian Blog",                url: "https://blog.gitguardian.com/rss/",                         lang: en, category: vendor, weight: 2}
- {id: unit42,          title: "Unit 42 (Palo Alto)",             url: "https://unit42.paloaltonetworks.com/feed/",                 lang: en, category: vendor, weight: 3}
- {id: prismacloud,     title: "Prisma Cloud Blog",               url: "https://www.paloaltonetworks.com/blog/prisma-cloud/feed/",  lang: en, category: vendor, weight: 2}
- {id: portswigger,     title: "PortSwigger Research",            url: "https://portswigger.net/research/rss",                      lang: en, category: vendor, weight: 2}
- {id: projectzero,     title: "Google Project Zero",             url: "https://googleprojectzero.blogspot.com/feeds/posts/default", lang: en, category: vendor, weight: 3}
- {id: google-security, title: "Google Online Security Blog",     url: "https://security.googleblog.com/feeds/posts/default",       lang: en, category: vendor, weight: 4}
- {id: jfrog,           title: "JFrog Blog",                      url: "https://jfrog.com/blog/feed/",                              lang: en, category: vendor, weight: 2}
# Observability / incident response / FinOps
- {id: groundcover,     title: "groundcover (eBPF observability)", url: "https://www.groundcover.com/blog/rss.xml",                 lang: en, category: vendor, weight: 2}
- {id: dynatrace,       title: "Dynatrace News",                  url: "https://www.dynatrace.com/news/feed/",                      lang: en, category: vendor, weight: 2}
- {id: newrelic,        title: "New Relic Blog",                  url: "https://newrelic.com/blog/feed",                            lang: en, category: vendor, weight: 2}
- {id: rootly,          title: "Rootly Blog (incident mgmt)",     url: "https://rootly.com/blog/rss.xml",                           lang: en, category: vendor, weight: 2}
- {id: vantage,         title: "Vantage Blog (cloud cost)",       url: "https://www.vantage.sh/blog/rss.xml",                       lang: en, category: vendor, weight: 4}
- {id: castai,          title: "CAST AI Blog (k8s cost)",         url: "https://cast.ai/feed/",                                     lang: en, category: vendor, weight: 3}
# CI / build / platform
- {id: namespace,       title: "Namespace Blog (CI runners)",     url: "https://www.namespace.so/blog/rss.xml",                     lang: en, category: vendor, weight: 2}
- {id: circleci,        title: "CircleCI Blog",                   url: "https://circleci.com/blog/feed.xml",                        lang: en, category: vendor, weight: 2}
- {id: sentry,          title: "Sentry Engineering",              url: "https://blog.sentry.io/feed.xml",                           lang: en, category: vendor, weight: 2}
- {id: container-sol,   title: "Container Solutions Blog",        url: "https://blog.container-solutions.com/rss.xml",              lang: en, category: vendor, weight: 2}
- {id: rhel,            title: "Red Hat Enterprise Linux Blog",   url: "https://www.redhat.com/en/rss/blog/channel/red-hat-enterprise-linux", lang: en, category: vendor, weight: 3}
# AI infrastructure
- {id: pytorch,         title: "PyTorch Blog",                    url: "https://pytorch.org/blog/feed.xml",                         lang: en, category: vendor, weight: 3}
- {id: huggingface,     title: "Hugging Face Blog",               url: "https://huggingface.co/blog/feed.xml",                      lang: en, category: vendor, weight: 3}
- {id: llmd,            title: "llm-d Blog",                      url: "https://llm-d.ai/blog/rss.xml",                             lang: en, category: project, weight: 4}
- {id: togetherai,      title: "Together AI Blog",                url: "https://www.together.ai/blog/rss.xml",                      lang: en, category: vendor, weight: 2}
# Large-scale engineering blogs
- {id: lyft,            title: "Lyft Engineering",                url: "https://eng.lyft.com/feed",                                 lang: en, category: vendor, weight: 3}
- {id: airbnb,          title: "Airbnb Engineering",              url: "https://medium.com/feed/airbnb-engineering",                lang: en, category: vendor, weight: 2}
- {id: pinterest,       title: "Pinterest Engineering",           url: "https://medium.com/feed/pinterest-engineering",             lang: en, category: vendor, weight: 2}
- {id: yelp,            title: "Yelp Engineering",                url: "https://engineeringblog.yelp.com/feed.xml",                 lang: en, category: vendor, weight: 2}
```

| id | why it matters | evidence |
|---|---|---|
| `confluent` | Kafka's commercial home; KIP explainers + the diskless/S3 storyline. | 200, 10 entries, newest 2026-08-27 |
| `warpstream` | Object-storage-native Kafka; publishes real cost/latency engineering write-ups. | 200, 62 entries, newest 2026-09-02 |
| `redpanda` | The other Kafka-protocol engine; C++/Seastar/io_uring internals. | 200, 100 entries, newest 2026-09-03 |
| `scylladb` | Shard-per-core database engineering — best free source on NUMA/io scheduling in practice. | 200, 20 entries, newest 2026-08-31 |
| `crunchydata` | Postgres-on-Kubernetes (PGO) and Postgres internals; you have Percona/Neon/PlanetScale but no Crunchy. | 200, 5 entries, newest 2026-09-02 |
| `supabase` | Postgres-at-scale ops posts; frequent HN traffic. | 200, 422 entries, newest 2026-08-24 |
| `tigerbeetle` | Deterministic-simulation testing, io_uring, LSM design — a favourite among distributed-systems listeners. | 200, 31 entries, newest 2026-08-20 |
| `materialize` | Streaming-SQL/differential-dataflow internals. | 200, 181 entries, newest 2026-08-03 |
| `questdb` | Time-series ingestion benchmarks; observability-adjacent. | 200, 218 entries, newest 2026-09-04 |
| `tigris` | S3-compatible object storage built on FoundationDB; edge/object-store engineering. | 200, 20 entries, newest 2026-09-01 |
| `dbos` | Durable-execution/workflow runtime — the Temporal competitor; you carry Temporal already. | 200, 67 entries, newest 2026-09-02 |
| `mongodb` | Fills a gap (you have no document-DB vendor). Lower cadence than the rest. | 200, 50 entries, newest 2026-06-25 |
| `backblaze` | Quarterly Drive Stats is a guaranteed segment; also B2/object-storage economics. | 200, 9 entries, newest 2026-09-03 |
| `storagereview` | Hands-on NVMe/array/DPU testing; nothing else in the draft covers storage hardware. | 200, 30 entries, newest 2026-09-05 |
| `veeam` | Backup/DR is a persistent k8s gap; Veeam publishes on Kasten/k8s backup regularly. | 200, 5 entries, newest 2026-09-03 |
| `amd-rocm` | The only credible non-NVIDIA GPU-software source; you have NVIDIA's blog and no counterweight. | 200, 10 entries, newest 2026-09-03 |
| `collabora` | Upstream kernel/Mesa/virtualization consultancy — publishes actual kernel-patch narratives. | 200, 736 entries, newest 2026-08-26 |
| `qemu` | You track KubeVirt/Firecracker/Cloud-Hypervisor but not the hypervisor underneath all of them. | 200, 10 entries, newest 2026-08-27 |
| `vmware-vcf` | The VMware-exit storyline is the single biggest commercial driver in this market; you need the source side of it, not only the migrators. | 200, 10 entries, newest 2026-09-07 |
| `opennebula` | European VMware-replacement alternative; relevant to sovereign-cloud stories. | 200, 10 entries, newest 2026-09-01 |
| `proxmox-forum` | Proxmox has no blog feed; the forum RSS is where releases/PVE 9 news actually appears. You already poll r/Proxmox. | 200, 20 entries, newest 2026-09-07 |
| `dd-seclabs` | Best current container/k8s/cloud attack research being published openly. | 200, 30 entries, newest 2026-08-31 |
| `trailofbits` | Cryptography + supply-chain (sigstore, PyPI, TUF) audit write-ups. | 200, 20 entries, newest 2026-08-26 |
| `socketdev` | npm/PyPI supply-chain attack disclosures — usually first to name a compromised package wave. | 200, 10 entries, newest 2026-09-04 |
| `endorlabs` | SCA/reachability analysis; publishes on CVE-noise and EOL open source. | 200, 100 entries, newest 2026-09-07 |
| `gitguardian` | Secrets sprawl in CI/CD and k8s; annual report is a segment. | 200, 15 entries, newest 2026-09-07 |
| `unit42` | Cloud/container threat intel at scale. | 200, 15 entries, newest 2026-09-03 |
| `prismacloud` | The k8s-posture side of the same vendor. | 200, 10 entries, newest 2026-09-01 |
| `portswigger` | Web/proxy/gateway attack research — hits your ingress/API-gateway beat. | 200, 40 entries, newest 2026-08-25 |
| `projectzero` | Kernel/hypervisor escape research; low volume, maximum weight when it lands. | 200, 10 entries, newest 2026-09-01 |
| `google-security` | Where sigstore, SLSA, memory-safety, OSS-Fuzz and Go-vuln announcements originate. Big miss. | 200, 25 entries, newest 2026-09-07 |
| `jfrog` | Artifactory/registry + regular malicious-package research. | 200, 10 entries, newest 2026-09-02 |
| `groundcover` | eBPF-based observability engineering write-ups (no agents, kernel-level tracing). | 200, 100 entries, newest 2026-09-07 |
| `dynatrace` | Fills out observability vendor coverage; OTel contributions. | 200, 24 entries, newest 2026-09-01 |
| `newrelic` | Same; also the OTel-pricing storyline. | 200, 10 entries, newest 2026-09-03 |
| `rootly` | Incident-management practice content; complements the SRE person-feeds. | 200, 100 entries, newest 2026-09-04 |
| `vantage` | The FinOps commentary gap. Vantage publishes cloud-cost reports and the Cloud Cost Handbook — hard numbers, not marketing. | 200, 395 entries, newest 2026-09-03 |
| `castai` | Kubernetes-specific cost optimisation/autoscaling data. | 200, 5 entries, newest 2026-08-11 |
| `namespace` | Remote CI/build-runner infrastructure engineering (a live topic given GH Actions cost). | 200, 49 entries, newest 2026-09-02 |
| `circleci` | You have Buildkite/Depot/Dagger but no mainstream CI vendor. | 200, 10 entries, newest 2026-09-01 |
| `sentry` | Genuine engineering posts (Rust ingestion pipeline, Clickhouse at scale) plus the OSS-licensing angle. | 200, 30 entries, newest 2026-09-01 |
| `container-sol` | Cloud-native consultancy with real migration post-mortems. LOW cadence. | 200, 10 entries, newest 2026-07-02 |
| `rhel` | RHEL 10 / image-mode / bootc is the base OS storyline for OpenShift and bootable containers; the generic Red Hat feed buries it. | 200, 9 entries, newest 2026-08-28 |
| `pytorch` | Distributed training/inference infra changes (FSDP, torch.compile, NCCL) drive GPU-cluster design. | 200, 10 entries, newest 2026-09-07 |
| `huggingface` | Model serving, quantisation, TGI — the layer directly above your k8s inference beat. | 200, 859 entries, newest 2026-09-03 |
| `llm-d` | The Red Hat/Google/IBM distributed-inference-on-Kubernetes project; the most important new AI-infra k8s project not in your list. | 200, 20 entries, newest 2026-08-31 |
| `togetherai` | Inference-stack engineering (kernels, speculative decoding, cluster ops). | 200, 100 entries, newest 2026-09-03 |
| `lyft` | Envoy's birthplace; still publishes infra/platform posts. | 200, 10 entries, newest 2026-08-31 |
| `airbnb` | Service-mesh/data-platform migrations at scale. | 200, 10 entries, newest 2026-08-25 |
| `pinterest` | Large k8s + Kafka + Flink fleet write-ups. | 200, 10 entries, newest 2026-09-01 |
| `yelp` | Long-running k8s/PaaSTA operational content. | 200, 10 entries, newest 2026-08-20 |

### cloud — provider sub-blogs and release-note feeds

```yaml
- {id: aws-whatsnew,    title: "AWS What's New (launches)",       url: "https://aws.amazon.com/about-aws/whats-new/recent/feed/",   lang: en, category: cloud, weight: 4}
- {id: aws-net,         title: "AWS Networking & Content Delivery", url: "https://aws.amazon.com/blogs/networking-and-content-delivery/feed/", lang: en, category: cloud, weight: 3}
- {id: aws-storage,     title: "AWS Storage Blog",                url: "https://aws.amazon.com/blogs/storage/feed/",                lang: en, category: cloud, weight: 3}
- {id: aws-security,    title: "AWS Security Blog",               url: "https://aws.amazon.com/blogs/security/feed/",               lang: en, category: cloud, weight: 3}
- {id: aws-devops,      title: "AWS DevOps & Developer Productivity", url: "https://aws.amazon.com/blogs/devops/feed/",             lang: en, category: cloud, weight: 3}
- {id: aws-database,    title: "AWS Database Blog",               url: "https://aws.amazon.com/blogs/database/feed/",               lang: en, category: cloud, weight: 2}
- {id: aws-hpc,         title: "AWS HPC Blog",                    url: "https://aws.amazon.com/blogs/hpc/feed/",                    lang: en, category: cloud, weight: 3}
- {id: gcp-relnotes,    title: "Google Cloud Release Notes",      url: "https://cloud.google.com/feeds/gcp-release-notes.xml",      lang: en, category: cloud, weight: 4}
- {id: gke-relnotes,    title: "GKE Release Notes",               url: "https://cloud.google.com/feeds/gke-release-notes.xml",      lang: en, category: cloud, weight: 5}
- {id: aks-releases,    title: "Azure AKS Releases",              url: "https://github.com/Azure/AKS/releases.atom",                lang: en, category: cloud, weight: 5}
- {id: gcp-devs,        title: "Google Cloud — Developers & Practitioners", url: "https://cloudblog.withgoogle.com/topics/developers-practitioners/rss/", lang: en, category: cloud, weight: 3}
- {id: gcp-systems,     title: "Google Cloud — Systems & Infrastructure", url: "https://cloudblog.withgoogle.com/topics/systems/rss/", lang: en, category: cloud, weight: 4}
- {id: ovhcloud,        title: "OVHcloud Blog",                   url: "https://blog.ovhcloud.com/feed/",                           lang: en, category: cloud, weight: 2}
- {id: ms-opensource,   title: "Microsoft Open Source Blog",      url: "https://opensource.microsoft.com/blog/feed/",               lang: en, category: cloud, weight: 2}
```

| id | why it matters | evidence |
|---|---|---|
| `aws-whatsnew` | Every AWS launch, one feed. Noisy, but it is *the* primary source; the AWS News Blog only covers a curated slice. | 200, 100 entries, newest 2026-09-07 |
| `aws-net` | VPC/ALB/CloudFront/Global Accelerator changes — the layer under EKS networking. | 200, 20 entries, newest 2026-09-04 |
| `aws-storage` | EBS/EFS/S3 Express/FSx behaviour changes that break CSI assumptions. | 200, 20 entries, newest 2026-09-03 |
| `aws-security` | IAM/IRSA/Pod Identity/GuardDuty-for-EKS. | 200, 20 entries, newest 2026-09-04 |
| `aws-devops` | CodeBuild/CodePipeline/GitHub-Actions-on-AWS. | 200, 20 entries, newest 2026-09-04 |
| `aws-database` | Aurora/DSQL/RDS engineering posts. | 200, 20 entries, newest 2026-09-03 |
| `aws-hpc` | GPU cluster / EFA / Slurm-on-AWS — direct AI-infra material. | 200, 20 entries, newest 2026-08-25 |
| `gcp-relnotes` | Machine-readable, dated change log across all GCP products. Far higher signal than the marketing blog. | 200, 30 entries, newest 2026-09-07 |
| `gke-relnotes` | GKE channel/version/feature changes — arguably the single most useful cloud feed for this podcast. | 200, 30 entries, newest 2026-08-18 |
| `aks-releases` | AKS ships its release notes as GitHub releases; this is the canonical feed. Azure Updates (already listed) does not carry them. | 200, 10 entries, newest 2026-08-31 |
| `gcp-devs` | The technical half of `cloudblog.withgoogle.com/rss/`, which you already carry undifferentiated. | 200, 20 entries, newest 2026-09-04 |
| `gcp-systems` | Google's own datacenter/network/TPU-infrastructure writing (Jupiter, Borg papers, Titanium). | 200, 20 entries, newest 2026-08-26 |
| `ovhcloud` | European sovereign-cloud + bare metal; relevant to your Cozystack/Hidora/FlokiNET audience. | 200, 20 entries, newest 2026-09-03 |
| `ms-opensource` | Where Microsoft announces CNCF/upstream contributions. LOW-FREQ. | 200, 10 entries, newest 2026-07-16 |

### media

```yaml
- {id: nextplatform,    title: "The Next Platform",               url: "https://www.nextplatform.com/feed/",                        lang: en, category: media, weight: 4}
- {id: blocksandfiles,  title: "Blocks & Files (storage)",        url: "https://blocksandfiles.com/feed/",                          lang: en, category: media, weight: 3}
- {id: servethehome,    title: "ServeTheHome",                    url: "https://www.servethehome.com/feed/",                        lang: en, category: media, weight: 3}
- {id: dcd,             title: "Data Center Dynamics",            url: "https://www.datacenterdynamics.com/en/rss/",                lang: en, category: media, weight: 3}
- {id: devopsdotcom,    title: "DevOps.com",                      url: "https://devops.com/feed/",                                  lang: en, category: media, weight: 2}
- {id: cloudnativenow,  title: "Cloud Native Now",                url: "https://cloudnativenow.com/feed/",                          lang: en, category: media, weight: 2}
- {id: packetpushers,   title: "Packet Pushers",                  url: "https://packetpushers.net/feed/",                           lang: en, category: media, weight: 3}
- {id: runtime,         title: "Runtime (Tom Krazit)",            url: "https://www.runtime.news/latest/rss/",                      lang: en, category: media, weight: 3}
- {id: itnext,          title: "ITNEXT",                          url: "https://itnext.io/feed",                                    lang: en, category: media, weight: 2}
```

| id | why it matters | evidence |
|---|---|---|
| `nextplatform` | The only outlet doing serious analysis of AI-datacenter economics, interconnects, and silicon. Fills your biggest media gap. | 200, 83 entries, newest 2026-09-03 |
| `blocksandfiles` | Storage-industry news of record (vendor moves, NVMe/object storage, Ceph-adjacent). | 200, 70 entries, newest 2026-09-07 |
| `servethehome` | Bare metal, NICs/DPUs, homelab-to-datacenter hardware. Complements your r/homelab polling. | 200, 6 entries, newest 2026-09-07 |
| `dcd` | Datacenter capacity, power, GPU buildouts — the business context behind AI-infra. | 200, 20 entries, newest 2026-09-07 |
| `devopsdotcom` | High volume, mixed quality — set weight 2 and let the scorer filter. Catches vendor/funding news the technical feeds skip. | 200, 10 entries, newest 2026-09-04 |
| `cloudnativenow` | Same publisher, k8s-focused. | 200, 10 entries, newest 2026-09-04 |
| `packetpushers` | Networking podcasts + written analysis; the only serious network-engineering media in the list. | 200, 1805 entries, newest 2026-09-04 |
| `runtime` | Tom Krazit (ex-Protocol/GigaOm) on enterprise infrastructure business. Weekly-ish. | 200, 15 entries, newest 2026-06-13 |
| `itnext` | Medium publication that is overwhelmingly k8s/platform practitioners. Noisy, weight 2. | 200, 10 entries, newest 2026-09-07 |

### newsletter — weeklies, podcasts, conference video

```yaml
- {id: tldrsec,         title: "tl;dr sec",                       url: "https://rss.beehiiv.com/feeds/xgTKUmMmUm.xml",              lang: en, category: newsletter, weight: 3}
- {id: cloudcast,       title: "The Cloudcast",                   url: "https://www.thecloudcast.net/feeds/posts/default",          lang: en, category: newsletter, weight: 3}
- {id: sedaily,         title: "Software Engineering Daily",      url: "https://softwareengineeringdaily.com/feed/",                lang: en, category: newsletter, weight: 2}
- {id: oxidefriends,    title: "Oxide and Friends",               url: "https://oxide-and-friends.transistor.fm/rss",               lang: en, category: newsletter, weight: 3}
- {id: consoledev,      title: "Console.dev",                     url: "https://console.dev/rss.xml",                               lang: en, category: newsletter, weight: 2}
- {id: yt-cncf,         title: "YouTube — CNCF (KubeCon talks)",  url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCvqbFHwN-nwalWPjPUKpvTA", lang: en, category: newsletter, weight: 4}
- {id: yt-k8s-community,title: "YouTube — Kubernetes (SIG meetings)", url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCZ2bu0qutTOM0tHYa_jkIwg", lang: en, category: newsletter, weight: 3}
- {id: yt-lf,           title: "YouTube — Linux Foundation",      url: "https://www.youtube.com/feeds/videos.xml?channel_id=UC5gLmcFuvdGbajs4VL-WU3g", lang: en, category: newsletter, weight: 2}
- {id: yt-devopstoolkit,title: "YouTube — DevOps Toolkit (Viktor Farcic)", url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCOSojkwOYL-9q9LzzERAihA", lang: en, category: newsletter, weight: 3}
- {id: yt-kubesimplify, title: "YouTube — Kubesimplify",          url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCi-1nnN0eC9nRleXdZA6ncg", lang: en, category: newsletter, weight: 2}
- {id: yt-platformeng,  title: "YouTube — PlatformCon / Platform Engineering", url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCKjVI0LawDxHaXSBMBOK1tA", lang: en, category: newsletter, weight: 3}
- {id: yt-ato,          title: "YouTube — All Things Open",       url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCBhXFK70DbOU15N2BhDQVTg", lang: en, category: newsletter, weight: 2}
- {id: platformeng-org, title: "PlatformEngineering.org Blog",    url: "https://platformengineering.org/blog/rss.xml",              lang: en, category: newsletter, weight: 3}
```

| id | why it matters | evidence |
|---|---|---|
| `tldrsec` | Clint Gibler's weekly. The single best supply-chain/cloud-security digest; you have CloudSecList but not this. | 200, 20 entries, newest 2026-08-27 |
| `cloudcast` | Longest-running cloud-infrastructure podcast; Aaron Delp + Brian Gracely set the industry framing. | 200, 25 entries, newest 2026-09-06 |
| `sedaily` | Daily technical interviews, frequently infra/k8s. | 200, 100 entries, newest 2026-09-03 |
| `oxidefriends` | Bryan Cantrill / Adam Leventhal — hardware, kernels, on-call war stories. You already carry the Oxide blog; the podcast has different content. | 200, 186 entries, newest 2026-09-03 |
| `consoledev` | Weekly new-tool digest; good source for "tool of the week". | 200, 6 entries, newest 2026-09-03 |
| `yt-cncf` | KubeCon session uploads land here in batches — a whole episode's worth of material after each event. Non-RSS-native but YouTube publishes real Atom. | 200, 15 entries, newest 2026-09-04 |
| `yt-k8s-community` | SIG meeting recordings and office hours; earliest visibility into upstream direction. | 200, 15 entries, newest 2026-09-07 |
| `yt-lf` | Open Source Summit / OSS security talks. | 200, 15 entries, newest 2026-09-02 |
| `yt-devopstoolkit` | Viktor Farcic reviews new k8s tooling weekly and has genuine reach. | 200, 15 entries, newest 2026-09-04 |
| `yt-kubesimplify` | Live sessions with maintainers, often on brand-new projects. | 200, 15 entries, newest 2026-09-05 |
| `yt-platformeng` | PlatformCon talks — your platform-engineering beat has no video source. | 200, 15 entries, newest 2026-09-04 |
| `yt-ato` | All Things Open recordings (you asked for it specifically). | 200, 15 entries, newest 2026-09-07 |
| `platformeng-org` | The written arm of the same community; publishes the maturity-model and IDP survey work. | 200, 100 entries, newest 2026-09-04 |

**Total verified additions: 103.**

Checked and *rejected* as dead/stale, so nobody re-proposes them:
`changelog.com/shipit/feed` (last episode 2024-12), `semianalysis.com/feed/` (last public
item 2025-09-16, moved behind paywall), `medium.com/feed/@copyconstruct` (2022),
`blog.px.dev/rss.xml` (2022), `glasskube.dev/blog/rss.xml` (2025-10),
`medium.com/feed/@danielepolencic` (2024-09), `medium.com/feed/envoyproxy` (2023-08),
`bravenewgeek.com/feed/` (2025-05), `samwho.dev/rss.xml` (2025-12),
`blog.danslimmon.com/feed/` (2025-06), `huyenchip.com/feed.xml` (2025-01),
`www.mgasch.com/index.xml` (2023-02), `mattklein123.dev/atom.xml` (2024-04 — see Objections).
Blocked to non-browser clients (403/406, don't add without a fetcher workaround):
`akamai.com/blog/*`, `vultr.com/news/rss`, `techatbloomberg.com/blog/feed/`,
`doordash.engineering/feed/`, `usenix.org/blog/feed`, `developers.redhat.com/blog/feed/`,
`weave.works/blog/rss.xml`.

---

## API sources (non-RSS, high signal)

| Source | Exact endpoint | Returns | Poll cadence | Notes |
|---|---|---|---|---|
| **Kubernetes official CVE feed** | `GET https://kubernetes.io/docs/reference/issues-security/official-cve-feed/index.json` | JSON array of k8s CVEs: `id`, `summary`, `url`, `date_published`, `external_url` | daily | Verified 200, `application/json`. Canonical source; anything here is headline-worthy. |
| **GitHub Security Advisories (ecosystem)** | `GET https://api.github.com/advisories?ecosystem=go&severity=high&published=YYYY-MM-DD..YYYY-MM-DD&per_page=100` (repeat for `ecosystem=npm`, `pip`, `rust`, `maven`) | GHSA records with CVSS, affected ranges, patched versions | daily | Verified 200. Needs a token for sane rate limits. Filter to repos in `releases.yaml` to cut noise. |
| **GitHub advisories for one project** | `GET https://api.github.com/repos/{owner}/{repo}/security-advisories` | Repo-scoped advisories | weekly | Use for `cilium/cilium`, `argoproj/argo-cd`, `traefik/traefik`, `containerd/containerd`. |
| **OSV.dev** | `POST https://api.osv.dev/v1/query` with `{"package":{"name":"k8s.io/kubernetes","ecosystem":"Go"}}` | Vulns per package/version | daily | Cross-ecosystem, no auth, no rate limit worth worrying about. |
| **CISA KEV** | `GET https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json` | Known-exploited CVE catalogue (~1.7 MB) | daily | Verified 200. Diff against previous fetch; a k8s/infra CVE entering KEV is a lead story. |
| **NVD CVE API 2.0** | `GET https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=kubernetes&pubStartDate=<ISO>&pubEndDate=<ISO>` | CVE records with CVSS/CPE | weekly | Verified 200. Rate-limited to 5 req/30s without an API key; request a free key. |
| **oss-security mailing list** | `GET https://seclists.org/rss/oss-sec.rss` | Upstream disclosure threads (often before vendor blogs) | daily | Verified 200, `application/rss+xml`. Technically RSS but treat as a firehose to filter. |
| **KEPs merged in the window** | `GET https://api.github.com/search/issues?q=repo:kubernetes/enhancements+is:pr+is:merged+merged:>=YYYY-MM-DD&sort=updated&per_page=100` | Merged KEP PRs with title/labels (`sig/*`, `stage/alpha|beta|stable`) | weekly | Verified 200. Parse `sig/` labels for topic routing; `stage/` label tells you graduation news. |
| **KEP repo commit feed (no auth)** | `GET https://github.com/kubernetes/enhancements/commits/master.atom` | Atom of commits to the KEP repo | weekly | Verified 200, 20 entries, newest 2026-09-03. Zero-auth fallback for the above. |
| **k8s release-note drafts / release schedule** | `GET https://api.github.com/repos/kubernetes/sig-release/contents/releases/release-1.<N>` then fetch `README.md` / `release-notes-draft.md` from that dir | Milestone dates (code freeze, RC, GA) and the draft note text | weekly | Verified 200 for `release-1.35`. Note: there is **no** top-level `releases/schedule.yaml` (404) — enumerate the directory. |
| **k8s releases (published)** | `GET https://github.com/kubernetes/kubernetes/releases.atom` | Atom of tagged releases incl. patch releases | daily | Verified 200. Cheaper than the REST API and needs no token. |
| **CNCF landscape (project status changes)** | `GET https://landscape.cncf.io/data/full.json` | Full landscape as JSON (~3.8 MB): every item with `project` field = `graduated`/`incubating`/`sandbox`, plus GitHub stats | weekly | Verified 200, `application/json`. `https://landscape.cncf.io/data.json` returns the SPA HTML — **do not use it**. Diff `project` per item to detect graduations/archivals. |
| **CNCF landscape source of truth** | `GET https://raw.githubusercontent.com/cncf/landscape/master/landscape.yml` | The YAML the landscape is built from (1.1 MB) | weekly | Verified 200. Use if you prefer diffing the source over the build artefact. |
| **CNCF TOC activity (graduation/incubation votes)** | `GET https://api.github.com/repos/cncf/toc/pulls?state=all&sort=updated&per_page=50` and the directory `GET https://api.github.com/repos/cncf/toc/contents/projects` | Open/closed TOC PRs — moves to incubation/graduation happen as PRs here before the blog post | weekly | Verified 200. `gitvote` bot comments carry the vote outcome. |
| **CNCF TOC commit feed (no auth)** | `GET https://github.com/cncf/toc/commits/main.atom` | Atom of TOC repo commits | weekly | Verified 200, newest 2026-09-03. |
| **Kubernetes version EOL** | `GET https://endoflife.date/api/kubernetes.json` | Per-minor release date, EOL date, latest patch | weekly | Verified 200. Also `/api/{postgresql,nodejs,ubuntu,rhel,docker-engine}.json`. Good for "your cluster goes EOL in N weeks" segments. |
| **Artifact Hub (new/updated Helm charts & operators)** | `GET https://artifacthub.io/api/v1/packages/search?kind=0&sort=last_updated&limit=60&offset=0` | Helm chart packages, newest first | weekly | Verified 200. **`sort` must be one of `relevance|stars|last_updated`** — `sort=updated` returns 400. `kind=0` Helm, `kind=3` OLM operators. |
| **FOSDEM schedule** | `GET https://fosdem.org/<year>/schedule/xml` | Full pentabarf XML of every talk incl. the Containers/Kubernetes and SRE devrooms | once per year (Dec–Jan) | Verified 200, 3.9 MB for 2026. Also `/schedule/ical`. Use for the CFP/schedule dump you asked for. |
| **LF / KubeCon events + CFPs** | `GET https://events.linuxfoundation.org/feed/` (RSS, listed above) plus per-event Sched: `https://<event>.sched.com/all.ics` | Event announcements, CFP opens, full schedules as iCal | weekly | RSS verified 200. Sched `.ics` is public per event once the schedule is live; no key needed for the iCal export. |
| **Cloud provider changes** | `https://cloud.google.com/feeds/gke-release-notes.xml`, `.../gcp-release-notes.xml`, `https://github.com/Azure/AKS/releases.atom`, `https://aws.amazon.com/about-aws/whats-new/recent/feed/` | Dated change entries | daily | All verified (see cloud additions). These are structurally release-note feeds, not blogs — score them separately. |
| **GitHub release Atom (any repo, no token)** | `https://github.com/{owner}/{repo}/releases.atom` | Last 10 releases as Atom | as needed | Verified across ~70 repos. Use this as the zero-auth fallback for `releases.yaml` when the REST rate limit bites — I hit `403` on the REST API after ~70 calls, and the Atom endpoint kept working. |

Sources I checked and could **not** make work — do not spend time on them:
`groups.google.com/forum/feed/kubernetes-announce/msgs/rss.xml` (404 — Google Groups killed
public feeds), `relnotes.k8s.io` (SPA, no JSON API exposed), `usenix.org/*/feed`
(403 to non-browser clients — SREcon schedules must be scraped),
`raw.githubusercontent.com/cncf/toc/main/PROJECTS.md` (404 — file moved into `projects/`).

---

## releases.yaml additions

Grouped by your existing group names. All repo paths verified to resolve (HTTP 200 on
`https://github.com/{repo}/releases.atom`, checked 2026-09-07).

**core_kubernetes**
```
kubernetes-sigs/external-dns
kubernetes-sigs/secrets-store-csi-driver
kubernetes-sigs/node-feature-discovery
kubernetes-sigs/scheduler-plugins
kubernetes-sigs/jobset
kubernetes-sigs/lws
kubernetes-sigs/kwok
kubernetes-sigs/cri-tools
kubernetes-sigs/gateway-api-inference-extension
kubernetes-sigs/kro
```
`gateway-api-inference-extension`, `lws` and `jobset` are the three SIG projects driving
inference and batch workloads on k8s — bigger news value right now than half the devtools
list. `kro` (was `kro-run/kro`, **now `kubernetes-sigs/kro`**) is the AWS/Google/Azure joint
resource-orchestration project.

**runtime**
```
containerd/nerdctl
containers/crun
lima-vm/lima
rancher-sandbox/rancher-desktop
nestybox/sysbox
```
`crun` is a glaring omission next to `runc` and `youki` — it is the default OCI runtime on
Fedora/RHEL/OpenShift.

**distros**
```
rancher/rke2
gardener/gardener
kubermatic/kubermatic
siderolabs/omni
labring/sealos
eksctl-io/eksctl
flatcar/scripts
```
`rke2` (the FIPS/CIS-hardened Rancher distro) missing while `k3s` and `rancher` are present is
an inconsistency. `flatcar/scripts` is where Flatcar releases are cut.

**networking**
```
tailscale/tailscale
netbirdio/netbird
kube-vip/kube-vip
cilium/ebpf
spidernet-io/spiderpool
frrouting/frr
osrg/gobgp
cloudflare/pingora
```
You carry the Tailscale *blog* but not the repo. `kube-vip` is in nearly every bare-metal
cluster. `cilium/ebpf` (the Go library) has its own release cadence and consumers.

**gitops_cd**
```
fluxcd/flagger
argoproj/argo-events
helmfile/helmfile
carvel-dev/kapp
stefanprodan/timoni
werf/werf
radius-project/radius
devtron-labs/devtron
woodpecker-ci/woodpecker
concourse/concourse
jenkinsci/jenkins
```
`jenkinsci/jenkins` matters despite the eye-roll: its weekly security advisories are recurring
news. `flagger` missing while `flux2` is present is an oversight.

**observability**
```
grafana/alloy
grafana/k6
prometheus-operator/prometheus-operator
prometheus/node_exporter
kubernetes/kube-state-metrics
open-telemetry/opentelemetry-ebpf-profiler
perses/perses
k8sgpt-ai/k8sgpt
greptimeteam/greptimedb
influxdata/influxdb
```
`prometheus-operator` and `kube-state-metrics` are the two most widely deployed observability
components in Kubernetes and neither is listed. `grafana/alloy` replaced the Grafana Agent —
listing `beyla` but not `alloy` is backwards.

**security**
```
sigstore/rekor
sigstore/fulcio
anchore/syft
aquasecurity/tracee
spiffe/spire
getsops/sops
FiloSottile/age
guacsec/guac
gitleaks/gitleaks
trufflesecurity/trufflehog
kubernetes-sigs/security-profiles-operator
inspektor-gadget/inspektor-gadget
notaryproject/notation
kubearmor/KubeArmor
stackrox/stackrox
stackrox/kube-linter
```
`grype` without `syft` makes no sense — syft generates the SBOM grype scans. `cosign` without
`rekor`/`fulcio` likewise. `spiffe/spire` is the workload-identity substrate everyone is
converging on and is entirely absent. `sops` is in more repos than most things on your list.

**storage_data**
```
juicedata/juicefs
seaweedfs/seaweedfs
cubefs/cubefs
topolvm/topolvm
piraeusdatastore/piraeus-operator
openzfs/zfs
postgres/postgres
elastic/elasticsearch
opensearch-project/OpenSearch
apecloud/kubeblocks
dragonflydb/dragonfly
milvus-io/milvus
qdrant/qdrant
apache/iceberg
duckdb/duckdb
rclone/rclone
```
`postgres/postgres` is the big one — you track five Postgres *operators* and not Postgres.
Same for `elasticsearch`/`OpenSearch` while the Elastic blog is in `feeds.yaml`.
`topolvm` and `piraeus` are the two local-storage CSI stacks people actually run on bare metal.

**virtualization**
```
qemu/qemu
libvirt/libvirt
xen-project/xen
OpenNebula/one
```
KubeVirt is listed but not the hypervisor and toolchain it wraps.

**iac_platform**
```
runatlantis/atlantis
aws/aws-cdk
cue-lang/cue
kcl-lang/kcl
```

**devtools**
```
GoogleCloudPlatform/kubectl-ai
kagent-dev/kagent
chaos-mesh/chaos-mesh
litmuschaos/litmus
FairwindsOps/pluto
```
Chaos engineering is entirely missing from the whole file. `pluto` (deprecated-API detection)
is the tool people reach for at every k8s upgrade — perpetually newsworthy.

**ai_infra**
```
ai-dynamo/dynamo
vllm-project/aibrix
vllm-project/production-stack
llm-d/llm-d
skypilot-org/skypilot
NVIDIA/nvidia-container-toolkit
kubernetes-sigs/dra-driver-nvidia-gpu
ROCm/k8s-device-plugin
bentoml/BentoML
kubeflow/katib
```
Notes: `NVIDIA/k8s-dra-driver-gpu` now redirects to **`kubernetes-sigs/dra-driver-nvidia-gpu`**
— use the new path. `nvidia-container-toolkit` is the component that actually breaks clusters
on upgrade and is missing while `gpu-operator` is listed. `llm-d`, `dynamo` and `aibrix` are
the three distributed-inference stacks that appeared since your list was written.

**serverless_edge**
```
wasmCloud/wasmCloud
spinframework/spin-operator
```
(`spinkube/spin-operator` redirects to `spinframework/spin-operator` — use the new path.)

**linux_base**
```
openzfs/zfs
openssh/openssh-portable
```

---

## Objections

### 1. 68 of 184 URLs in `feeds.yaml` are not feeds (37%)

This is the finding. I fetched every URL in the file; the following return 404/406/empty or
serve HTML with zero `<item>`/`<entry>` elements. Several look like they were guessed from a
pattern rather than checked. Corrected URLs below are all verified 200 + parseable.

**English-language breakage with a verified fix:**

| id | broken URL | working replacement | evidence for replacement |
|---|---|---|---|
| `istio` | `istio.io/latest/blog/index.xml` | `https://istio.io/latest/blog/feed.xml` | 200, 165 entries, newest 2026-08-24 |
| `linkerd` | `linkerd.io/blog/index.xml` | `https://linkerd.io/blog/feed.xml` | 200, 10 entries, newest 2026-06-24 |
| `falco` | `falco.org/blog/index.xml` | `https://falco.org/blog/feed.xml` | 200, 50 entries, newest 2026-05-26 |
| `opentofu` | `opentofu.org/blog/index.xml` | `https://opentofu.org/blog/rss.xml` | 200, 20 entries, newest 2026-09-03 |
| `openbao` | `openbao.org/blog/index.xml` | `https://openbao.org/blog/rss.xml` | 200, 20 entries, newest 2026-08-18 |
| `opa` | `blog.openpolicyagent.org/feed` | `https://blog.openpolicyagent.org/rss.xml` | 200, 20 entries, newest **2025-08-20** — feed works but the blog is dormant; consider dropping to weight 1 |
| `kubeedge` | `kubeedge.io/blog/index.xml` | `https://kubeedge.io/blog/rss.xml` | 200, 37 entries, newest 2026-04-21 |
| `vllm` | `blog.vllm.ai/feed.xml` | `https://vllm.ai/blog/rss.xml` | 200, 50 entries, newest 2026-09-07 |
| `ceph` | `ceph.io/en/news/blog/index.xml` | `https://ceph.io/en/news/blog/feed.xml` | 200, 20 entries, newest 2026-08-19 |
| `clickhouse` | `clickhouse.com/blog/rss.xml` | `https://clickhouse.com/rss.xml` | 200, 869 entries, newest 2026-09-07 |
| `modal` | `modal.com/blog/feed.xml` | `https://modal.com/blog/atom.xml` | 200, 132 entries, newest 2026-09-07 |
| `temporal` | `temporal.io/blog/rss.xml` | `https://temporal.io/blog/feed.xml` | 200, 423 entries, newest 2026-09-04 |
| `tetrate` | `tetrate.io/feed/` | `https://tetrate.io/rss.xml` | 200, 25 entries, newest 2026-08-30 |
| `traefik` | `traefik.io/blog/feed/` | `https://traefik.io/rss.xml` | 200, 100 entries, newest 2026-08-20 |
| `kong` | `konghq.com/blog/feed` | `https://konghq.com/feed` | 200, 10 entries, newest 2026-09-03 |
| `spacelift` | `spacelift.io/blog/rss.xml` | `https://spacelift.io/rss` | 200, 10 entries, newest 2026-09-04 |
| `buildkite` | `buildkite.com/blog/feed.xml` | `https://buildkite.com/blog.atom` | 200, 10 entries, newest **2025-12-03** — dormant, drop or weight 1 |
| `depot` | `depot.dev/blog/rss.xml` | `https://depot.dev/rss.xml` | 200, 219 entries, newest 2026-08-26 |
| `render` | `render.com/blog/rss.xml` | `https://render.com/blog/feed.xml` | 200, 105 entries, newest 2026-09-05 |
| `digitalocean` | `digitalocean.com/blog/rss.xml` | `https://www.digitalocean.com/rss/blog.atom` | 200, 100 entries, newest 2026-09-07 |
| `fastly` | `fastly.com/blog/feed` | `https://www.fastly.com/blog_rss.xml` | 200, 25 entries, newest 2026-09-03 |
| `honeycomb` | `honeycomb.io/blog/feed` | `https://www.honeycomb.io/feed` | 200, 50 entries, newest 2026-09-07 |
| `nutanix` | `nutanix.com/blog/rss.xml` | `https://www.nutanix.com/blog.rssfeed.xml` | 200, 30 entries, newest 2026-09-03 |
| `talos` | `siderolabs.com/blog/rss/` | `https://www.siderolabs.com/feed/` | 200, 50 entries, newest 2026-08-19 |
| `wiz` | `wiz.io/feed.xml` | `https://www.wiz.io/blog/rss.xml` | 200, 681 entries, newest 2026-09-03 |
| `mirantis` | `mirantis.com/feed/` | `https://www.mirantis.com/blog/feed/` | 200, 710 entries, newest 2026-08-26 |
| `hetzner` | `hetzner.com/blog/feed/` | `https://www.hetzner.com/blog/rss.xml` | 200, 19 entries, newest 2026-09-02 |
| `iximiuz` | `iximiuz.com/en/feed.xml` | `https://iximiuz.com/feed.rss` | 200, 82 entries, newest 2026-01-19 — LOW-FREQ now |
| `mattklein` | `mattklein123.dev/feed.xml` | `https://mattklein123.dev/atom.xml` | 200, 9 entries, newest **2024-04-24** — dead, drop the entry |
| `bitfieldconsult` | `bitfieldconsulting.com/rss.xml` | `https://bitfieldconsulting.com/feed` | 200, 20 entries, newest 2026-08-25 |
| `cloudflarelearn` | `agwa.name/blog/rss` (returns empty) | `https://www.agwa.name/blog/feed` | 200, 30 entries, newest 2026-04-29. Also: the `id` is wrong — this is Andrew Ayer, nothing to do with Cloudflare Learning. Rename to `agwa`. |
| `cloudseclist` | `cloudseclist.com/issues/index.xml` | `https://cloudseclist.com/feed.xml` | 200, 354 entries, newest 2026-09-07 |
| `elastic` | `elastic.co/blog/feed` (listed, works) | — | 200, 40 entries, newest 2026-09-07 — fine, but weight 2 is too low for a feed that carries Elasticsearch release engineering |

**English-language breakage with NO working replacement found** (I tried the obvious patterns
plus `<link rel=alternate>` discovery on the site itself):

- `kyverno` — `kyverno.io/blog/index.xml` 404; `/blog/feed.xml`, `/index.xml`, `/rss.xml` all
  404 and the site advertises no feed. **Kyverno has no RSS.** Track via
  `github.com/kyverno/kyverno/releases.atom` instead.
- `dapr` — `blog.dapr.io/feed` 404; `/rss/`, `/feed.xml`, `dapr.io/blog/index.xml` all 404.
  No feed. Track the repo.
- `dagger` — `dagger.io/blog.rss` 404; `/rss.xml`, `/blog/rss` 404, no `<link rel=alternate>`.
  No feed. Track `dagger/dagger` releases.
- `loft` (vCluster) — `vcluster.com/blog/rss.xml` 404; `/rss.xml`, `/blog/feed.xml`,
  `loft.sh/blog/rss.xml` all 404. No feed.
- `robusta` — `home.robusta.dev/blog/rss.xml` 404; `/rss.xml` 404. No feed.
- `k8s-gateway` — `gateway-api.sigs.k8s.io/feed_rss_created.xml` 404 (the mkdocs RSS plugin is
  not enabled). Use `kubernetes-sigs/gateway-api` releases + the KEP API instead.
- `knative` — `knative.dev/blog/index.xml` 404; the page advertises `../feed_rss_created.xml`
  which is also 404. No working feed.
- `devopsish` — `devopsish.com/index.xml` 404 and every variant (`/feed/`, `/rss/`,
  `/feed.xml`, `/archive/index.xml`) 404. The site is Hugo 0.163.2 with issues at
  `devopsish.com/325/` etc. but RSS output appears disabled. **Currently weighted 4 and
  fetching nothing.** Either scrape `devopsish.com/sitemap.xml` (verified 200, `lastmod`
  2026-09-05) or drop it.
- `kubeweekly` — `cncf.io/kubeweekly/feed/` 404; `/category/kubeweekly/feed/` 404. Weighted 4,
  fetching nothing. KubeWeekly content overlaps `lwkd` anyway.
- `openinfra` — `openinfra.org/feed` 404; `/blog/feed/`, `/news/feed`, `openinfra.dev/feed`
  all 404.
- `apache` — `news.apache.org/foundation/entry/feed.rss` 404. The ASF news feed moved; I could
  not find a live replacement.
- `envoy` — `blog.envoyproxy.io/feed` times out entirely (no TCP response after 40s from two
  attempts). The Medium mirror `medium.com/feed/envoyproxy` resolves but is dead since
  2023-08. **Envoy's blog is effectively gone**; use `envoyproxy/envoy` releases + the
  `envoyproxy.io` docs changelog.
- `minio` — `blog.min.io/rss/` returns 200 HTML with zero entries; `/feed`, `/index.xml`,
  `min.io/blog/rss.xml` all fail. MinIO's blog no longer emits RSS.
- `openebs` — `openebs.io/blog/rss.xml` returns 200 HTML, zero entries; `/index.xml`,
  `/rss.xml` same. No feed.
- `anyscale` — `anyscale.com/blog/rss.xml` returns 200 HTML, zero entries.
  `anyscale.com/rss.xml` parses but contains **one** item dated 2025-11-03. Effectively dead —
  and since you already have `ray-project/ray` releases and the new vLLM/llm-d feeds, drop it.
- `chronosphere` — `chronosphere.io/feed/` returns a well-formed but **empty** RSS document
  (zero items). Same for `/blog/feed/` and `/learn/feed/`. Drop.
- `timescale` (`tigerdata`) — `tigerdata.com/blog/rss.xml` 200 HTML zero entries;
  `/rss.xml`, `/blog/feed.xml` fail. No feed.
- `api7` — `api7.ai/blog/rss.xml` 404, no discoverable feed.
- `figma` — `figma.com/blog/feed.xml` 404.
- `linkedin-eng` — `linkedin.com/blog/engineering/rss` 404.
- `uber` — `uber.com/blog/engineering/rss/` returns **406** to any non-browser client (also
  with `/en-US/` prefix). Needs a real browser fetch or drop.
- `rachelbythebay` — the URL is correct but the server returns **429** under any concurrent
  fetching. Rate-limit your fetcher to 1 request per host per run for this domain, or it will
  silently disappear from digests.

**Non-English breakage** (out of my scope but found while sweeping, flagging for reviewer #1/#3):
`blog.flant.ru/rss/` (connection failure), `deckhouse.io/blog/index.xml` (404),
`slurm.io/rss/` (404), `cloud.vk.com/blog/rss/` (404), `yandex.cloud/ru/blog/rss` (200 HTML,
0 entries), `developer.aliyun.com/rsspage.htm` (404), `cloudwego.io/blog/index.xml` (404),
`opensource.bytedance.com/blog/rss.xml` (200 HTML, 0 entries), `cloud.tencent.com/developer/rss`
(404), `karmada.io/blog/index.xml` (404), `higress.io/blog/index.xml` (404),
`cloudnative.to/index.xml` (200 HTML, 0 entries).

### 2. Stale feeds that are live but effectively abandoned

- `aquasec` (`blog.aquasec.com/rss.xml`) — parses fine, **newest post 2025-05-06**. Aqua moved
  their content; the feed is a fossil. Weighted 3 for a year of nothing.
- `opa` — newest 2025-08-20 (see above).
- `buildkite` — newest 2025-12-03.
- `mattklein` — newest 2024-04-24.
- `iximiuz` — newest 2026-01-19 on the corrected URL. Ivan now publishes primarily to
  iximiuz Labs; weight 4 is too high for the current cadence, drop to 2–3.

### 3. Miscategorisation and weighting

- `jepsen` (`jepsen.io/analyses.atom`) is a **404** and is also a duplicate of `aphyr`
  (`aphyr.com/posts.atom`, which works) — Kyle Kingsbury cross-posts every Jepsen report to
  aphyr.com. Delete the `jepsen` entry outright rather than fixing it.
- `kubernetes-sigs/kubespray` appears **twice** in `releases.yaml`, in both `core_kubernetes`
  and `devtools`. Remove one.
- `cloudflarelearn` is Andrew Ayer's personal blog, not anything Cloudflare. The `id` and any
  downstream grouping by it are wrong.
- `simonwillison` at weight 3 in `person` is the wrong beat for this show — it is
  overwhelmingly LLM-application content, not infrastructure. Either drop to 1 or accept that
  it will crowd out infra items in the person bucket. (Contrast: `vickiboykis` and `chip`-style
  ML-*infra* writing is what you actually want, hence my `vickiboykis` proposal.)
- `heise-open` uses `https://www.heise.de/rss/heise-atom.xml`, which is heise's **whole-site**
  feed, not the open-source section. It will flood the digest with consumer-tech German news
  at weight 2. Either narrow it or drop it.
- `register-cloud` points at `theregister.com/software/headlines.atom` — The Register's
  `/on-prem/` and `/networks/` sections are closer to your beat than `/software/`.
- `changelog` (`changelog.com/news/feed`) is fine, but note the sibling `shipit` podcast feed
  I checked is dead since 2024-12, in case anyone proposes it.
- `oxide` blog at weight 4 plus `Oxide and Friends` podcast (my addition) will double-count the
  same stories in some weeks. Deduplicate on title similarity or keep the podcast at 3.
- `ray` is titled "Anyscale / Ray Blog" but points at Anyscale's marketing feed, which is dead
  (one item, 2025-11). The Ray project's actual news is in `ray-project/ray` releases, already
  in `releases.yaml`. Retitle or drop.

### 4. Structural gaps in `community.yaml`

- The `hackernews` query list has no `kubernetes security`, `cve`, `postmortem` variants and no
  `finops`, `gpu`, `nvidia`, `inference`, `vllm`, `etcd`, `ceph`, `proxmox`, `vmware`,
  `broadcom` — the last two being the dominant migration storyline of the moment.
- `lobsters` tags omit `openbsd`, `nix`, `debugging`, `practices`, `osdev` — minor, but `nix`
  in particular carries infra content that never appears under `devops`.
- No Lobsters/HN dedup key is specified against the RSS feeds; expect the same article three
  times (own blog + HN + Lobsters). Worth stating a canonical-URL dedup rule in the file.
- `reddit` list is missing `r/kubernetes` adjacent: `r/cloudcomputing`, `r/hpc` (GPU cluster
  ops), `r/storage`, `r/vmware` (migration threads), `r/PostgreSQL` (you have `r/postgres`,
  which is the smaller of the two).
