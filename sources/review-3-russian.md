# Review #3 — Russian-language coverage

Reviewer: #3 (RU sources). Date of verification: **2026-09-07 / 2026-09-08**.

Every URL below was fetched with `curl -sSL --compressed` from a **US IP** (same egress class as a
GitHub Actions runner). Recorded: HTTP status, number of `<item>`/`<entry>` elements, and the
**newest item-level date** (not the channel-level `lastBuildDate`, which on Habr is always "now"
and is a trap — see Objections).

Headline: **5 of the 13 existing Russian entries in `feeds.yaml` are broken** (one of them at the
DNS level). Fix those first; the additions are secondary.

---

## Additions

76 feeds verified. Paste into the `# ── Russian-language ─` section of `feeds.yaml`.

### A. Fixes for broken existing entries (replace in place)

```yaml
- {id: flant,           title: "Флант — блог",                   url: "https://flant.ru/rss",                                             lang: ru, category: vendor,    weight: 5}
- {id: flant-habr,      title: "Флант — Habr",                   url: "https://habr.com/ru/rss/companies/flant/articles/",                lang: ru, category: vendor,    weight: 5}
- {id: deckhouse-rel,   title: "Deckhouse — релизы",             url: "https://github.com/deckhouse/deckhouse/releases.atom",             lang: ru, category: project,   weight: 4}
- {id: deckhouse-virt,  title: "Deckhouse Virtualization — релизы", url: "https://github.com/deckhouse/virtualization/releases.atom",      lang: ru, category: project,   weight: 4}
- {id: slurm,           title: "Слёрм — блог",                   url: "https://slurm.io/rss.xml",                                         lang: ru, category: vendor,    weight: 2}
- {id: slurm-habr,      title: "Слёрм — Habr",                   url: "https://habr.com/ru/rss/companies/slurm/articles/",                lang: ru, category: vendor,    weight: 3}
- {id: yandexcloud,     title: "Yandex Cloud & Infra — Habr",    url: "https://habr.com/ru/rss/companies/yandex_cloud_and_infra/articles/", lang: ru, category: cloud,   weight: 4}
- {id: vkcloud,         title: "VK Tech — Habr",                 url: "https://habr.com/ru/rss/companies/vktech/articles/",               lang: ru, category: cloud,    weight: 3}
```

| id | evidence |
|---|---|
| `flant` | `blog.flant.ru` **does not resolve** (`curl: (6) Could not resolve host`). Correct feed is `flant.ru/rss` — HTTP 200, 10 items, newest **2026-09-04**. Weight up from 4→5: Флант is the single most relevant RU source for this podcast (Deckhouse, KubeVirt, k8s ops). |
| `flant-habr` | HTTP 200, 40 items, newest **2026-09-03** ("Дорогая, я улучшил KubeVirt! Сделали классическую виртуализацию на рельсах"). Overlaps `flant.ru/rss` but is not identical (Habr gets the long-form; the site gets news + releases). Dedupe by title if the collector supports it. |
| `deckhouse-rel` | Original `https://deckhouse.io/blog/index.xml` → **HTTP 404** (Hugo "Page not found" body). `deckhouse.ru/blog/rss.xml`, `/blog/feed.xml`, `/blog/index.xml` all 404; the site exposes **no `<link rel=alternate>` at all**. The only live, machine-readable Deckhouse channel is GitHub releases: HTTP 200, 10 entries, newest **2026-09-01 (v1.77.0)**. `blog.deckhouse.io/feed` (Medium) also returns 200 but is EN-only and last posted **2025-11-13** — skip it. |
| `deckhouse-virt` | HTTP 200, 10 entries, newest **2026-09-07 (v1.10.5-rc.3)**. Deckhouse Virtualization is the direct VMware-replacement product line — highest-signal release feed in RU k8s. |
| `slurm` | `https://slurm.io/rss/` → **HTTP 404**. The `<link rel=alternate>` on slurm.io points at `https://slurm.io/rss.xml` — HTTP 200, 325 items, newest **2026-09-02**. Caveat: this feed mixes blog posts with course landing pages, hence weight 2. |
| `slurm-habr` | HTTP 200, 40 items, newest **2026-09-07**. Cleaner than the site feed (articles only), so higher weight than `slurm`. |
| `yandexcloud` | `https://yandex.cloud/ru/blog/rss` → **HTTP 404** (returns a 560 KB SPA shell, which will silently parse as "0 entries" in a lax parser — worse than a hard failure). `yandex.cloud/ru/blog` exposes **no RSS link tag**. Yandex Cloud's technical content goes to Habr under `yandex_cloud_and_infra`: HTTP 200, 40 items, newest **2026-09-04**. |
| `vkcloud` | `https://cloud.vk.com/blog/rss/` → **HTTP 404**. `vk.cloud` does not even complete a TLS handshake from a US IP. VK's infra content is on Habr under `vktech` (VK Tech — the B2B/cloud arm): HTTP 200, 40 items, newest **2026-09-01**. |

### B. Habr hubs (new)

```yaml
- {id: habr-virt,       title: "Habr — Виртуализация",           url: "https://habr.com/ru/rss/hubs/virtualization/articles/?fl=ru",         lang: ru, category: community, weight: 4}
- {id: habr-itinfra,    title: "Habr — IT-инфраструктура",       url: "https://habr.com/ru/rss/hubs/it-infrastructure/articles/?fl=ru",      lang: ru, category: community, weight: 4}
- {id: habr-gpgpu,      title: "Habr — GPGPU",                   url: "https://habr.com/ru/rss/hubs/gpgpu/articles/?fl=ru",                  lang: ru, category: community, weight: 4}
- {id: habr-distsys,    title: "Habr — Распределённые системы",  url: "https://habr.com/ru/rss/hubs/distributed_systems/articles/?fl=ru",    lang: ru, category: community, weight: 3}
- {id: habr-net,        title: "Habr — Сетевые технологии",      url: "https://habr.com/ru/rss/hubs/network_technologies/articles/?fl=ru",   lang: ru, category: community, weight: 3}
- {id: habr-storages,   title: "Habr — Хранение данных",         url: "https://habr.com/ru/rss/hubs/storages/articles/?fl=ru",               lang: ru, category: community, weight: 3}
- {id: habr-pgsql,      title: "Habr — PostgreSQL",              url: "https://habr.com/ru/rss/hubs/postgresql/articles/?fl=ru",             lang: ru, category: community, weight: 3}
- {id: habr-oss,        title: "Habr — Open source",             url: "https://habr.com/ru/rss/hubs/open_source/articles/?fl=ru",            lang: ru, category: community, weight: 3}
- {id: habr-cloudcomp,  title: "Habr — Облачные вычисления",     url: "https://habr.com/ru/rss/hubs/cloud_computing/articles/?fl=ru",        lang: ru, category: community, weight: 3}
- {id: habr-devcloud,   title: "Habr — Облачные сервисы для разработки", url: "https://habr.com/ru/rss/hubs/devcloud/articles/?fl=ru",       lang: ru, category: community, weight: 3}
- {id: habr-hosting,    title: "Habr — Хостинг",                 url: "https://habr.com/ru/rss/hubs/hosting/articles/?fl=ru",                lang: ru, category: community, weight: 2}
- {id: habr-micro,      title: "Habr — Микросервисы",            url: "https://habr.com/ru/rss/hubs/microservices/articles/?fl=ru",          lang: ru, category: community, weight: 2}
- {id: habr-dbadmin,    title: "Habr — Администрирование БД",    url: "https://habr.com/ru/rss/hubs/db_admins/articles/?fl=ru",              lang: ru, category: community, weight: 2}
- {id: habr-nginx,      title: "Habr — Nginx",                   url: "https://habr.com/ru/rss/hubs/nginx/articles/?fl=ru",                  lang: ru, category: community, weight: 2}
- {id: habr-backup,     title: "Habr — Резервное копирование",   url: "https://habr.com/ru/rss/hubs/backup/articles/?fl=ru",                 lang: ru, category: community, weight: 2}
- {id: habr-srvopt,     title: "Habr — Серверная оптимизация",   url: "https://habr.com/ru/rss/hubs/server_side_optimization/articles/?fl=ru", lang: ru, category: community, weight: 2}
- {id: habr-career,     title: "Habr — Карьера в IT",            url: "https://habr.com/ru/rss/hubs/career/articles/?fl=ru",                 lang: ru, category: community, weight: 1}
```

All 17: **HTTP 200, 40 items each.** Newest item-level dates observed:
`virtualization` 2026-09-03 · `it-infrastructure` 2026-09-07 · `gpgpu` 2026-08-31 ·
`distributed_systems` 2026-09-06 · `network_technologies` 2026-09-07 · `storages` 2026-09-07 ·
`postgresql` 2026-09-07 · `open_source` 2026-09-07 · `cloud_computing` 2026-09-04 ·
`devcloud` 2026-08-20 · `hosting` 2026-09-06 · `microservices` 2026-09-07 ·
`db_admins` 2026-09-07 · `nginx` 2026-09-07 · `backup` 2026-09-04 ·
`server_side_optimization` 2026-09-02 · `career` 2026-09-07.

Justifications for the top ones:
- **virtualization** — the VMware-replacement hub. Newest item at check time was Флант's KubeVirt post. Non-negotiable for this podcast.
- **it-infrastructure** — the actual RU equivalent of `#platform-engineering`; note the slug is **hyphenated**, unlike every other hub in this list.
- **gpgpu** — GPU-cloud signal (newest item at check: "Встречаем RTX PRO 6000 BSE: достойная ли это альтернатива H100 NVL"). Directly on-brief for the GPU-as-a-Service work.
- **distributed_systems** — newest item at check: "K3s на колёсах: HA-кластер для автопарка с ARM-агентами, WireGuard…". Genuinely technical hub, low PR density.
- **devcloud** — small hub, but it is where RU providers publish platform internals (newest at check: "Простые сложные сети: как устроена сеть в MWS Cloud Platform").
- **career** at weight 1 — RU hiring/market posts occasionally carry real market signal (newest at check: "Разработчик в Казахстане стоит на 22% дороже, если он ИП"), but it is 90 % noise. Include only if the scorer can be trusted to suppress it.

### C. Vendor / provider Habr blogs

```yaml
- {id: selectel-habr,   title: "Selectel — Habr",                url: "https://habr.com/ru/rss/companies/selectel/articles/",             lang: ru, category: vendor, weight: 4}
- {id: orionsoft,       title: "Orion soft (zVirt) — Habr",      url: "https://habr.com/ru/rss/companies/orion_soft/articles/",           lang: ru, category: vendor, weight: 4}
- {id: yadro,           title: "YADRO — Habr",                   url: "https://habr.com/ru/rss/companies/yadro/articles/",                lang: ru, category: vendor, weight: 4}
- {id: mws,             title: "MWS (MTS Web Services) — Habr",  url: "https://habr.com/ru/rss/companies/mws/articles/",                  lang: ru, category: cloud,  weight: 3}
- {id: mts,             title: "МТС — Habr",                     url: "https://habr.com/ru/rss/companies/ru_mts/articles/",               lang: ru, category: vendor, weight: 3}
- {id: cloudru,         title: "Cloud.ru — Habr",                url: "https://habr.com/ru/rss/companies/cloud_ru/articles/",             lang: ru, category: cloud,  weight: 3}
- {id: timeweb,         title: "Timeweb Cloud — Habr",           url: "https://habr.com/ru/rss/companies/timeweb/articles/",              lang: ru, category: cloud,  weight: 3}
- {id: hostkey,         title: "HOSTKEY — Habr",                 url: "https://habr.com/ru/rss/companies/hostkey/articles/",              lang: ru, category: cloud,  weight: 3}
- {id: rtdc,            title: "Ростелеком ЦОД — Habr",          url: "https://habr.com/ru/rss/companies/rt-dc/articles/",                lang: ru, category: cloud,  weight: 3}
- {id: ispsystem,       title: "ISPsystem — Habr",               url: "https://habr.com/ru/rss/companies/ispsystem/articles/",            lang: ru, category: vendor, weight: 3}
- {id: h3llo,           title: "H3LLO.CLOUD — Habr",             url: "https://habr.com/ru/rss/companies/h3llo_cloud/articles/",          lang: ru, category: cloud,  weight: 3}
- {id: chislitel,       title: "Числитель (Графиня) — Habr",     url: "https://habr.com/ru/rss/companies/chislitellab/articles/",         lang: ru, category: vendor, weight: 3}
- {id: basis,           title: "Базис — Habr",                   url: "https://habr.com/ru/rss/companies/basis/articles/",                lang: ru, category: vendor, weight: 3}
- {id: itsumma,         title: "ITSumma — Habr",                 url: "https://habr.com/ru/rss/companies/itsumma/articles/",              lang: ru, category: vendor, weight: 3}
- {id: vk-habr,         title: "VK — Habr",                      url: "https://habr.com/ru/rss/companies/vk/articles/",                   lang: ru, category: vendor, weight: 2}
- {id: astralinux,      title: "Astra Linux — Habr",             url: "https://habr.com/ru/rss/companies/astralinux/articles/",           lang: ru, category: vendor, weight: 2}
- {id: redsoft,         title: "РЕД СОФТ (RED OS) — Habr",       url: "https://habr.com/ru/rss/companies/redsoft/articles/",              lang: ru, category: vendor, weight: 2}
- {id: cloud4y,         title: "Cloud4Y — Habr",                 url: "https://habr.com/ru/rss/companies/cloud4y/articles/",              lang: ru, category: cloud,  weight: 2}
- {id: k2tech,          title: "К2Тех — Habr",                   url: "https://habr.com/ru/rss/companies/k2tech/articles/",               lang: ru, category: vendor, weight: 2}
- {id: croc,            title: "КРОК — Habr",                    url: "https://habr.com/ru/rss/companies/croc/articles/",                 lang: ru, category: vendor, weight: 2}
- {id: beelinecloud,    title: "beeline cloud — Habr",           url: "https://habr.com/ru/rss/companies/beeline_cloud/articles/",        lang: ru, category: cloud,  weight: 2}
- {id: ruvds,           title: "RUVDS — Habr",                   url: "https://habr.com/ru/rss/companies/ruvds/articles/",                lang: ru, category: cloud,  weight: 2}
```

Why the ones above 2:
- **orion_soft** — makes **zVirt**, the loudest RU commercial VMware replacement. Direct competitive intel. Newest at check 2026-08-31: "Свой протокол удаленного доступа: почему Open Source недостаточно и как мы…".
- **yadro** — the only RU vendor doing real hardware + OpenSource engineering write-ups. Newest 2026-09-03: "Protestware: как идейные злоумышленники атакуют ваш код".
- **selectel** — best signal-to-PR ratio of the RU providers by a distance; duplicate of the existing `selectel` site feed but the Habr one is the technical stream.
- **rt-dc** (Ростелеком ЦОД) — datacenter capacity/power economics, which is exactly the GPU-cloud constraint story. Newest 2026-08-26: "Гигаватты на бумаге: ИИ-бум упирается не в чипы, а в розетку".
- **hostkey** — bare-metal + GPU rental; publishes actual GPU-serving how-tos. Newest 2026-09-02: "JupyterLab на GPU-сервере…".
- **chislitellab** — "Графиня", a RU Grafana fork/alternative. Small blog, very on-topic. Newest 2026-09-07.
- **h3llo_cloud** — small independent RU cloud; unusually candid postmortem-style writing. Newest 2026-09-01: "Что там с последним коммерческим облаком в России (и как мы лажали этот год)".
- **ispsystem** — hosting control panels + their own k8s platform.

Marketing-heavy, hence capped at 2–3: `cloud_ru`, `k2tech`, `croc`, `cloud4y`, `beeline_cloud`, `astralinux`, `redsoft`. `ruvds` is high-volume but is mostly **translations of EN posts** — it will duplicate what the EN half of the digest already catches; weight 2 and consider a title-dedupe rule.

### D. Big-tech RU engineering blogs

```yaml
- {id: ozontech,        title: "Ozon Tech — Habr",               url: "https://habr.com/ru/rss/companies/ozontech/articles/",             lang: ru, category: vendor, weight: 3}
- {id: avito,           title: "Avito — Habr",                   url: "https://habr.com/ru/rss/companies/avito/articles/",                lang: ru, category: vendor, weight: 3}
- {id: tbank,           title: "Т-Банк — Habr",                  url: "https://habr.com/ru/rss/companies/tbank/articles/",                lang: ru, category: vendor, weight: 3}
- {id: 2gis,            title: "2ГИС — Habr",                    url: "https://habr.com/ru/rss/companies/2gis/articles/",                 lang: ru, category: vendor, weight: 3}
- {id: hh,              title: "hh.ru — Habr",                   url: "https://habr.com/ru/rss/companies/hh/articles/",                   lang: ru, category: vendor, weight: 3}
- {id: skbkontur,       title: "СКБ Контур — Habr",              url: "https://habr.com/ru/rss/companies/skbkontur/articles/",            lang: ru, category: vendor, weight: 2}
- {id: x5tech,          title: "X5 Tech — Habr",                 url: "https://habr.com/ru/rss/companies/x5tech/articles/",               lang: ru, category: vendor, weight: 2}
- {id: lamoda,          title: "Lamoda Tech — Habr",             url: "https://habr.com/ru/rss/companies/lamoda/articles/",               lang: ru, category: vendor, weight: 2}
- {id: sberbank,        title: "Сбер — Habr",                    url: "https://habr.com/ru/rss/companies/sberbank/articles/",             lang: ru, category: vendor, weight: 2}
- {id: ontico,          title: "Онтико / HighLoad++ — Habr",     url: "https://habr.com/ru/rss/companies/oleg-bunin/articles/",           lang: ru, category: community, weight: 3}
```

- **hh** newest at check 2026-08-26: "Redis — история одного падения" — exactly the postmortem genre the podcast wants.
- **2gis** newest 2026-08-26: "Помогите, FLAKY" — strong infra/testing engineering culture.
- **ontico** (`oleg-bunin`) is the HighLoad++/DevOpsConf organiser blog: transcripts of conference talks. Currently AI-heavy, but it is the single best proxy for "what RU infra engineers are talking about on stage". Note it **cross-posts** — one article was simultaneously live in `cloud_ru`; expect duplicates.
- **sberbank / x5tech / lamoda** at 2: real engineering, but cadence is slow and the infra share is small.

### E. Data / database vendors

```yaml
- {id: arenadata,       title: "Arenadata — Habr",               url: "https://habr.com/ru/rss/companies/arenadata/articles/",            lang: ru, category: vendor, weight: 3}
- {id: tantor,          title: "Tantor Labs — Habr",             url: "https://habr.com/ru/rss/companies/tantor/articles/",               lang: ru, category: vendor, weight: 3}
- {id: postgrespro-habr,title: "Postgres Professional — Habr",   url: "https://habr.com/ru/rss/companies/postgrespro/articles/",          lang: ru, category: vendor, weight: 3}
- {id: postgrespro,     title: "Postgres Professional — блог",   url: "https://postgrespro.ru/rss",                                       lang: ru, category: vendor, weight: 2}
```

`arenadata` newest 2026-09-04 ("Плагины в Picodata"); `tantor` newest 2026-09-05 (open-source `pg_anon`
walkthrough); `postgrespro` Habr newest 2026-09-07. The **site** feed `postgrespro.ru/rss` is HTTP 200 /
20 items but sparse — newest **2026-08-17**, then 2026-05-03, 2026-04-13. Keep at weight 2; the Habr
stream is the live one.

### F. Security (RU)

```yaml
- {id: pt,              title: "Positive Technologies — Habr",   url: "https://habr.com/ru/rss/companies/pt/articles/",                   lang: ru, category: vendor, weight: 3}
- {id: securelist-ru,   title: "Securelist (Kaspersky GReAT)",   url: "https://securelist.ru/feed/",                                      lang: ru, category: vendor, weight: 3}
- {id: kaspersky-habr,  title: "Kaspersky — Habr",               url: "https://habr.com/ru/rss/companies/kaspersky/articles/",            lang: ru, category: vendor, weight: 2}
```

`pt` HTTP 200 / 40 items / newest 2026-09-07 — **use the Habr feed, not `ptsecurity.com`, which is
TLS-broken from US runners (see Dead or blocked)**. `securelist.ru/feed/` HTTP 200 / 10 items /
newest 2026-09-04. `kaspersky` Habr newest 2026-09-04 ("Гетерогенный lookup: как одна фича C++
сделала драйвер проще…") — surprisingly low-level, worth keeping at 2.

### G. Media / news (RU)

```yaml
- {id: servernews,      title: "ServerNews — новости",           url: "https://servernews.ru/news/rss",                                   lang: ru, category: media, weight: 4}
- {id: habr-news,       title: "Хабр — Новости",                 url: "https://habr.com/ru/rss/news/?fl=ru",                              lang: ru, category: media, weight: 3}
- {id: cnews,           title: "CNews",                          url: "https://www.cnews.ru/inc/rss/news.xml",                            lang: ru, category: media, weight: 2}
```

- **servernews** is the best RU infra-news source, full stop: servers, DC, storage, GPU, RU cloud market.
  HTTP 200, 10 items, newest **2026-09-07 15:50 MSK** ("«Базис» приобрёл 70 % разработчика ИИ-платформы
  наблюдаемости Proto Observability"). **Use `/news/rss`, not `/rss`** — the bare `/rss` is the
  long-form review feed and only publishes a few times a month (newest item there was 2026-08-12).
- **habr-news** HTTP 200 / 40 items / newest 2026-09-07 18:20 — short RU-market news items.
- **cnews** HTTP 200 / **200 items** / newest 2026-09-07 19:30. Very high volume and heavily
  press-release-driven; weight 2 and expect the scorer to do the filtering. It is nonetheless the
  place where RU cloud/DC market moves get reported first.

### H. Education / consultancy

```yaml
- {id: otus,            title: "OTUS — Habr",                    url: "https://habr.com/ru/rss/companies/otus/articles/",                 lang: ru, category: vendor, weight: 2}
```

OTUS HTTP 200 / 40 items / newest **2026-09-07 19:17** ("Задача взяла lock() и остановила весь
рантайм: пять ошибок с блокировками…"). Course-marketing framing but the articles themselves are
technical. `otus.ru/nest/rss/` returns HTTP 200 but **zero `<item>` elements** — not a feed; use Habr.

(Слёрм is in section A. Southbridge, Nixys, Rebrain, Экспресс 42 → see Dead or blocked.)

---

## Habr company blogs

Pattern confirmed: `https://habr.com/ru/rss/companies/<slug>/articles/` — HTTP 200 + 40 items when
the slug exists, hard **HTTP 404** when it does not. No `?fl=ru` needed (company blogs are already RU).

Discovery trick worth recording: `https://habr.com/ru/hubs/<hub>/companies/` lists every company
posting into a hub. That is how the non-obvious slugs below were found — guessing brand names has a
~50 % miss rate (`deckhouse`, `vk_cloud`, `wildberries`, `tinkoff`, `sbercloud`, `basealt`, `mts`
all 404).

| slug | company | what they publish | verified? |
|---|---|---|---|
| `flant` | Флант | k8s ops, Deckhouse, KubeVirt, migrations | ✅ 200 / 40 / 2026-09-03 |
| `selectel` | Selectel | infra, hardware, k8s, cost | ✅ 200 / 40 / 2026-09-07 |
| `yandex_cloud_and_infra` | Yandex Cloud & Infra | cloud internals, IDM, networking | ✅ 200 / 40 / 2026-09-04 |
| `yandex` | Yandex (general) | mostly product/AI, little infra | ✅ 200 / 40 / 2026-09-04 |
| `cloud_ru` | Cloud.ru (ex-SberCloud) | cloud + AI, marketing-heavy | ✅ 200 / 40 / 2026-09-07 |
| `mws` | MWS (MTS Web Services) | cloud platform internals | ✅ 200 / 40 / 2026-08-27 |
| `ru_mts` | МТС | broad tech, some infra | ✅ 200 / 40 / 2026-09-07 |
| `vktech` | VK Tech | VK's B2B cloud/platform | ✅ 200 / 40 / 2026-09-01 |
| `vk` | VK | ranking, algorithms, some infra | ✅ 200 / 40 / 2026-09-03 |
| `timeweb` | Timeweb Cloud | networking, protocols, hosting | ✅ 200 / 40 / 2026-09-07 |
| `slurm` | Слёрм | k8s/DevOps training content | ✅ 200 / 40 / 2026-09-07 |
| `orion_soft` | Orion soft | zVirt virtualization, VMware replacement | ✅ 200 / 40 / 2026-08-31 |
| `basis` | Базис | RU virtualization platform | ✅ 200 / 23 / 2026-09-03 |
| `astralinux` | Astra Linux | ALD Pro, OS, mostly corporate | ✅ 200 / 40 / 2026-09-07 |
| `redsoft` | РЕД СОФТ (RED OS) | immutable OS, RU Linux distro | ✅ 200 / 26 / 2026-08-18 |
| `yadro` | YADRO | hardware, OSS, supply chain | ✅ 200 / 40 / 2026-09-03 |
| `k2tech` | К2Тех | enterprise integration, networking | ✅ 200 / 40 / 2026-08-25 |
| `croc` | КРОК | integration, virtualization | ✅ 200 / 40 / 2026-08-25 |
| `rt-dc` | Ростелеком ЦОД | datacenter power/capacity economics | ✅ 200 / 40 / 2026-08-26 |
| `hostkey` | HOSTKEY | bare-metal + GPU rental how-tos | ✅ 200 / 40 / 2026-09-02 |
| `cloud4y` | Cloud4Y | RU cloud, compliance | ✅ 200 / 40 / 2026-09-02 |
| `ispsystem` | ISPsystem | control panels, own k8s platform | ✅ 200 / 40 / 2026-08-30 |
| `h3llo_cloud` | H3LLO.CLOUD | small indie RU cloud, candid | ✅ 200 / 23 / 2026-09-01 |
| `chislitellab` | Числитель | "Графиня" (RU Grafana alternative) | ✅ 200 / 24 / 2026-09-07 |
| `beeline_cloud` | beeline cloud | cloud market commentary | ✅ 200 / 40 / 2026-07-15 |
| `ruvds` | RUVDS | high volume, mostly EN translations | ✅ 200 / 40 / 2026-09-07 |
| `ozontech` | Ozon Tech | scale, testing, platform | ✅ 200 / 40 / 2026-08-26 |
| `avito` | Avito | platform engineering, LLM | ✅ 200 / 40 / 2026-09-04 |
| `tbank` | Т-Банк | JVM, digests, platform | ✅ 200 / 40 / 2026-09-07 |
| `sberbank` | Сбер | Platform V, broad | ✅ 200 / 40 / 2026-09-07 |
| `sberdevices` | SberDevices | devices/AI, little infra | ✅ 200 / 40 / 2026-08-20 |
| `x5tech` | X5 Tech | retail platform | ✅ 200 / 40 / 2026-08-20 |
| `2gis` | 2ГИС | strong engineering culture | ✅ 200 / 40 / 2026-08-26 |
| `hh` | hh.ru | postmortems, backend | ✅ 200 / 40 / 2026-08-26 |
| `skbkontur` | СКБ Контур | engineering process, backend | ✅ 200 / 40 / 2026-08-28 |
| `lamoda` | Lamoda Tech | data platform, Spark | ✅ 200 / 40 / 2026-08-27 |
| `domclick` | Домклик | supply-chain security, backend | ✅ 200 / 40 / 2026-09-01 |
| `alfa` | Альфа-Банк | fintech platform | ✅ 200 / 40 / 2026-09-01 |
| `itsumma` | ITSumma | ops outsourcing, incidents | ✅ 200 / 40 / 2026-09-02 |
| `oleg-bunin` | Онтико (HighLoad++) | conference talk write-ups | ✅ 200 / 40 / 2026-09-07 |
| `pt` | Positive Technologies | offensive security research | ✅ 200 / 40 / 2026-09-07 |
| `kaspersky` | Kaspersky | low-level C++, drivers, security | ✅ 200 / 40 / 2026-09-04 |
| `solarsecurity` | Солар | security ops | ✅ 200 / 40 / 2026-09-01 |
| `jetinfosystems` | Инфосистемы Джет | DFIR, integration | ✅ 200 / 40 / 2026-08-17 |
| `arenadata` | Arenadata | RU data platform, Picodata | ✅ 200 / 40 / 2026-09-04 |
| `tantor` | Tantor Labs | RU PostgreSQL distro | ✅ 200 / 40 / 2026-09-05 |
| `postgrespro` | Postgres Professional | PostgreSQL internals | ✅ 200 / 40 / 2026-09-07 |
| `otus` | OTUS | technical, course-marketing framing | ✅ 200 / 40 / 2026-09-07 |
| `lanit` | ЛАНИТ | integration, broad | ✅ 200 / 40 / 2026-09-01 |
| `nexign` | Nexign | telco software | ⚠️ 200 / 40 / **2026-07-30** — slowing |
| `regionsoft` | RegionSoft | SMB IT, opinion pieces | ⚠️ 200 / 40 / 2026-07-30 |
| `mclouds` | mClouds | cloud, hardware news reposts | ⚠️ 200 / 40 / 2026-07-30 |
| `nubes` | NUBES | cloud, sparse | ⚠️ 200 / 40 / **2026-05-21** |
| `linx` | Linx Cloud | cloud migration, sparse | ⚠️ 200 / 40 / **2026-01-25** |
| `nixys` | Nixys | CI/CD, DevOps | ❌ dead — newest **2025-01-10** |
| `aquarius` | Аквариус | hardware | ❌ dead — newest **2025-04-24** |
| `t1_cloud` | T1 Cloud | cloud | ❌ dead — newest **2022-10-26** |
| `express42` | Экспресс 42 | IaC, DevOps | ❌ dead — 7 posts, newest **2015-05-18** |
| `netangels` | NetAngels | hosting | ❌ dead — 10 posts, newest **2017-04-13** |
| `dcmiran` | DataLine / Miran | DC | ❌ dead — newest **2023-07-04** |
| `deckhouse` / `deckhouse_io` | Deckhouse | — | ❌ **404** — no Habr blog; content posts under `flant` |
| `vk_cloud` / `vkcloud` | VK Cloud | — | ❌ **404** — use `vktech` |
| `yandex_cloud` | Yandex Cloud | — | ❌ **404** — use `yandex_cloud_and_infra` |
| `sbercloud` | SberCloud | — | ❌ **404** — renamed, use `cloud_ru` |
| `mts` / `mts_cloud` | МТС | — | ❌ **404** — use `ru_mts` / `mws` |
| `tinkoff` | Тинькофф | — | ❌ **404** — renamed, use `tbank` |
| `wildberries` / `wb_tech` / `wb` | Wildberries | — | ❌ **404** — no company blog; their infra posts appear as guest articles under `oleg-bunin` |
| `southbridge` / `southbridge_io` | Southbridge | — | ❌ **404** — blog removed; the HTML page `habr.com/ru/companies/southbridge/articles/` is also 404. Southbridge's content now ships as Слёрм |
| `rebrain` | Rebrain | — | ❌ **404** |
| `basealt` / `altlinux` | Базальт СПО / ALT | — | ❌ **404** — no Habr blog |
| `red_soft` / `redos` | РЕД СОФТ | — | ❌ **404** — the working slug is `redsoft` |
| `dodopizza` | Додо | — | ❌ **404** (slug changed at some point) |
| `gigacloud`, `dataline`, `servercore`, `first_vds`, `vk_team`, `basistech`, `astra_linux`, `orionsoft` | — | — | ❌ **404**, listed so nobody re-guesses them |

---

## Telegram + YouTube

### Telegram — needs a scraper, not RSS

Telegram has **no RSS**. The public web preview at `https://t.me/s/<channel>` renders the last ~20
posts as static HTML and is scrapeable from a US IP without auth (verified). Parse
`div.tgme_widget_message_wrap`; post timestamps live in `time[datetime]` (ISO-8601).

Important distinction found while checking: `t.me/s/<x>` returns **HTTP 200 in all three cases** —
a real channel with posts, a *group chat* (0 posts, but a real `og:title`), and a *nonexistent
handle* (0 posts, `og:title` = "Telegram: Contact @x"). The collector must treat "HTTP 200 with
zero message wrappers" as a failure, not as an empty week.

| handle | name | subs | last post seen | why |
|---|---|---|---|---|
| `flant_ru` | Флант \| Специалисты по DevOps и Kubernetes | 2.19K | **2026-09-07** | Announcements + OSS releases from the most relevant RU vendor. Highest-priority scrape. |
| `devopsina` | ДЕВОПСИНА \| DevOps \| Linux | 23.6K | **2026-09-07** | Largest genuinely technical RU DevOps channel. |
| `bashdays` | Bash Days \| Linux \| DevOps | 23.7K | **2026-09-04** | Practical Linux/DevOps, high engagement. |
| `devsecops_weekly` | DevSecOps Talks | 8.02K | **2026-09-07** | Podcast + curated DevSecOps links; RU-language commentary on upstream CVEs. |
| `selectel` | Selectel | 63.4K | **2026-09-07** | Provider channel; marketing-heavy but flags RU infra market moves early. |
| `mws_cloud` | МWS Cloud | 11.4K | **2026-09-07** | MTS cloud platform announcements. |
| `servernewsru` | ServerNews | 2.55K | **2026-09-07** | Mirrors the RSS feed above — scrape only if you skip the RSS. |
| `linkmeup_podcast` | linkmeup | 17.4K | **2026-09-07** | The RU networking podcast/community. Networking depth the rest of the list lacks. |
| `habr_com` | Хабр | 132K | **2026-09-07** | Redundant with the Habr RSS feeds; skip unless you want editor-picked signal. |
| `tadviser` | TAdviser | 13.4K | **2026-09-07** | RU IT-market/procurement news. Business signal, not engineering. |
| `avitotech` | AvitoTech | 25.4K | **2026-09-07** | Engineering culture + talk announcements. |
| `orangedevops` | OrangeDevOps | 934 | 2026-08-12 | Small but on-topic sysadmin/DevOps. Low priority. |
| `kubernetes_news` | Kubernetes News | 246 | 2026-09-05 | Tiny, but 100 % on-topic k8s news. |
| `itsumma` | ITSumma | 252 | 2026-09-04 | Redundant with their Habr blog. |
| `aenix_io` | Ænix.io | 544 | 2026-09-03 | The host's own company — include only as a self-check, not as digest input. |

**Not scrapeable (chats, not channels — 200 OK but zero posts in the web preview):** `cozystack`,
`deckhouse`, `deckhouse_ru`, `kubernetes_ru`, `devops_ru`, `sre_ru`, `cozystack_ru`, `terraform_ru`,
`pro_ansible`, `ru_gitlab`, `RU_Docker`, `gitops_ru`, `rebrainme`, `vk_cloud`.
Reading those needs a Telegram user account via MTProto, which is out of scope for a GitHub Actions
collector.

**Dead or wrong handle:** `opennetru` (last post 2025-10-21), `devops_mops` (2.42K subs, last post
2026-02-18 — dormant), `yandex_cloud` (last post 2022), `vkteam` (2022), `ontico` (unrelated Spanish
channel), `zapiskiadmina` (squatted — now a Marvel/DC channel), `cnews` (unrelated), `tbank_tech`
(handle for sale). Nonexistent: `flantcom`, `slurm_io`, `slurm_channel`, `devopsdeflope`,
`cloud_ru_official`, `nixys_io`, `devopsru`, `k8s_ru`, `otus_ru`, `pgcql_ru`, `basis_tech`,
`astra_linux_official`, `yadro_tech`, `cloud_ru_tech`, `selectel_cloud`, `vkcloud_official`.

### YouTube — real RSS, works today

Pattern `https://www.youtube.com/feeds/videos.xml?channel_id=<UC…>` — HTTP 200, up to 15 `<entry>`.
Two gotchas: the channel_id must be the `externalId` from the channel page HTML (handles are **not**
accepted by the feed endpoint), and the **first `<published>` in the document is the channel's
creation date**, not the newest video — take the second one.

```yaml
- {id: yt-flant,        title: "Флант — YouTube",                url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCjmwHCZ-qh3ro7hHTQhqYQg", lang: ru, category: vendor,    weight: 4}
- {id: yt-slurm,        title: "Слёрм — YouTube",                url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCK5MedKoNJ5aRahfGOIGx6g", lang: ru, category: vendor,    weight: 3}
- {id: yt-highload,     title: "HighLoad Channel (Онтико)",      url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCwHL6WHUarjGfUM_586me8w", lang: ru, category: community, weight: 4}
- {id: yt-deflope,      title: "DevOps Deflope (подкаст)",       url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCuf3hhmkOnx2wsWjm3DteDQ", lang: ru, category: newsletter, weight: 3}
- {id: yt-selectel,     title: "Selectel — YouTube",             url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCVU0Ml1l_Y90wmy5EjWTSng", lang: ru, category: vendor,    weight: 2}
- {id: yt-avitotech,    title: "AvitoTech — YouTube",            url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCO2w0cpl1wxygHjQH6eEfEg", lang: ru, category: vendor,    weight: 2}
```

| channel | handle | channel_id | verified |
|---|---|---|---|
| Флант | `@flant` | `UCjmwHCZ-qh3ro7hHTQhqYQg` | ✅ 200 / 15 entries / newest **2026-09-06** ("Виртуалка мимикрирует под POD #devops #deckhouse #kubernetes") |
| Слёрм | `@slurm_io` | `UCK5MedKoNJ5aRahfGOIGx6g` | ✅ 200 / 15 / newest **2026-09-03** |
| HighLoad Channel | `@HighLoadChannel` | `UCwHL6WHUarjGfUM_586me8w` | ✅ 200 / 15 / newest **2026-08-11**. Conference talks — the deepest RU technical video source; publishes in bursts after each conference. |
| DevOps Deflope | `@DevOpsDeflope` | `UCuf3hhmkOnx2wsWjm3DteDQ` | ✅ 200 / 9 / newest **2026-08-01** (ep. 061). The RU DevOps podcast — direct format peer. |
| Selectel | `@selectel` | `UCVU0Ml1l_Y90wmy5EjWTSng` | ✅ 200 / 15 / newest **2026-09-07**. High cadence, much of it short-form marketing → weight 2. |
| AvitoTech | `@avitotech` | `UCO2w0cpl1wxygHjQH6eEfEg` | ✅ 200 / 15 / newest **2026-09-07** |
| Cloud.ru | `@cloudru` | `UCFYQnzpYxiLUGprz56EHXqg` | ⚠️ 200 / 15 / newest 2026-09-04, but the content skews gamedev/AI-consumer. Not recommended. |
| Deckhouse | — | — | ❌ `@deckhouse` on YouTube is an unrelated channel (`UCM7OP_mY0xA_8gxZvnn5gjA`, "Tennis Today", last upload 2024-01). Deckhouse video lives on the Флант channel. |
| Positive Technologies | `@PositiveTechnologies` | `UCMRHe8zQBip9SPEunw02lVQ` | ❌ feed returns 200 with **0 entries** |
| Rebrain | `@rebrain` | `UC3zcAfcTvYJqokxtAHJ8w7w` | ❌ 1 entry, 2006 — squatted/abandoned handle |
| Ozon Tech | `@ozontech` | `UCkclCEdA7H-JME9TERpJbPQ` | ❌ wrong channel (Arabic-language, last upload 2022) |
| Yandex Cloud, linkmeup, VK Cloud, MWS, T-Bank | — | — | ❌ handle did not resolve under any variant tried |

---

## Dead or blocked

**Hard blocker — TLS.** `www.ptsecurity.com` presents a certificate issued by
`C=RU, O=The Ministry of Digital Development and Communications, CN=Russian Trusted Sub CA`.
That root is not in the Ubuntu/GitHub-runner trust store, so `curl` fails with
`SSL certificate problem: unable to get local issuer certificate` and any fetch will fail. **Do not
add any `ptsecurity.com` URL** — use the Habr blog `pt` instead. I swept the issuer for every other
RU host proposed here (`habr.com`, `selectel.ru`, `opennet.ru`, `servernews.ru`, `cnews.ru`,
`flant.ru`, `slurm.io`, `astralinux.ru`, `basealt.ru`, `basistech.ru`, `orionsoft.ru`, `securelist.ru`,
`yandex.cloud`, `cloud.ru`, `mws.ru`, `rt.ru`, `t1-cloud.ru`) — all Let's Encrypt / GlobalSign /
Sectigo. Only Positive Technologies is affected. This is worth re-checking periodically; RU vendors
migrating to the national CA is an ongoing trend.

**Requires a `Referer` header.** `https://3dnews.ru/news/rss/` returns HTTP 200 with a **20-byte
body** unless `-e https://3dnews.ru/` is sent, at which point it returns a valid 79 KB / 61-item feed
(newest 2026-09-07). Rejected anyway on content: it is consumer gadget news (Sony headphones, Huawei
watches, PS3 emulators). There is no separate server/DC RSS — `3dnews.ru/servers/rss/` is 404.
If the collector ever wants it, note the header requirement.

**Reachable but rejected on content:**
- `tadviser.ru/xml/tadviser.xml` — HTTP 200 / 50 items / newest 2026-09-07, but the feed is generic
  RU business news: sugar production, tram procurement, beauty salons in Kazakhstan. The IT items
  are procurement announcements. Note the URL in the brief (`?title=Special:Rss`) is 404; the working
  one is `/xml/tadviser.xml`. Not worth a slot; the Telegram channel is the better cut of it.
- `securitylab.ru` — the URL in the brief (`/news/export/rss.php`) is **404**. The working feed is
  `https://www.securitylab.ru/_services/export/rss/news/` (200 / 100 items / newest 2026-09-07), but
  the content is clickbait-adjacent pop-science and consumer security ("Физики дошли до квантового
  предела…"). Almost no infra signal. Rejected.
- `comnews.ru/rss.xml` — 200 / 13 items / newest 2026-09-07. Telecom-industry trade press. Adjacent
  to the DC/cloud market but almost entirely press releases. Rejected.
- `kaspersky.ru/blog/feed/` — 200 / 10 / newest 2026-09-04, but consumer-facing. Use `securelist.ru`
  and the `kaspersky` Habr blog instead.

**Dead feeds (200 but stale, or gone):**
- `anti-malware.ru/rss.xml` — HTTP 200, 10 items, newest item **2019-03-21**. The feed is
  abandoned even though the site is alive. **Do not add.**
- `nixys.io/blog/rss` — HTTP 200, 10 items, newest **2025-02-28**, and English-language. Their
  Habr blog stopped at 2025-01-10. Nixys has effectively stopped publishing.
- `express42.com/feed.xml` — 404. Their Habr blog has 7 posts, newest **2015**. Экспресс 42 is dead
  as a content source.
- `rebrain.ru/blog` — 404 (142-byte error body). No blog, no feed, no Habr blog, YouTube handle
  squatted. Rebrain publishes only into a private Telegram community. Nothing to collect.
- `otus.ru/nest/rss/` — 200 but zero `<item>` elements; not a feed. Habr blog works.
- `red-soft.ru` — HTTP 307 then **connection timeout** from a US IP (20 s, 0 bytes). Possibly
  geo-throttled. Use the `redsoft` Habr blog instead, which works fine.
- `deckhouse.io/blog/*` — every RSS/Atom path 404s and the site publishes no feed link tag at all.
- `basealt.ru`, `altlinux.org` — no RSS link tags; the ALT wiki `action=feed` endpoint returns a
  "Making sure you're not a bot!" interstitial. **No usable Базальт/ALT feed exists.** Say so rather
  than shipping a URL that will silently yield nothing.
- `opennet.ru/opennews/opennews_sec_utf.rss` — 404. Only the `_all_` feed exists (already in the draft).

**404 slug guesses** (recorded so nobody re-tries): see the bottom of the Habr table.

---

## Objections to the existing Russian entries

1. **Five of thirteen are broken.** `flant` (DNS does not resolve), `deckhouse` (404), `slurm` (404),
   `yandexcloud` (404), `vkcloud` (404). That is a 38 % failure rate in the section, and it has
   presumably been silently producing zero Russian vendor items for however long the draft has been
   running. Fixes are in section A.

2. **Three of those 404s return a 200-shaped body.** `yandex.cloud/ru/blog/rss` returns a 563 KB
   SPA HTML shell with a 404 status; `deckhouse.io/blog/index.xml` returns a 262 KB styled Hugo
   error page. A collector that only checks "did I get bytes?" or that swallows non-200 will treat
   these as empty feeds forever. **Recommend the collector hard-fail on non-200 and on
   "200 with zero entries", and surface that in CI.** This is the single most valuable process fix
   in this review.

3. **The `weight` on Флант is wrong.** It sits at 4, below `habr-k8s` at 5. For a podcast whose host
   works on Cozystack and VMware replacement, Флант is the highest-signal Russian source that
   exists. It should be 5, and it should be present twice (site + Habr) because the two streams do
   not fully overlap.

4. **`deckhouse` is filed as `lang: ru` but `deckhouse.io/blog` was the English site.** If the intent
   was RU Deckhouse coverage, the Habr `flant` blog plus the two GitHub release feeds cover it. If
   the intent was EN Deckhouse coverage, it belongs in the vendor section, not the Russian one.

5. **`habr-nix` (weight 2) is the weakest hub in the set** — newest items at check were 2026-09-07,
   then a gap to 2026-08-30 and 2026-08-25. Low volume and mostly desktop-Linux. `habr-virt`,
   `habr-itinfra` and `habr-gpgpu` all deserve a slot ahead of it.

6. **`habr-infosec` at weight 2 is under-weighted relative to what it produces** — it is one of the
   highest-volume hubs on Habr (four items on the check day alone). Either raise the min-score
   threshold for it or leave the weight; but do not raise the weight without a filter, or it will
   flood the RU section.

7. **No news source in the RU section.** OpenNET is there, which is upstream-OSS news, but there is
   nothing covering the Russian infra *market* — who bought whom, which DC got built, which cloud
   changed pricing. `servernews.ru/news/rss` fills that hole and should be weight 4.

8. **`selectel` is listed with its site feed only.** `selectel.ru/blog/feed/` works (200 / 10 items /
   newest 2026-09-07) but it is "Академия Selectel" — tutorials and light content. The Habr blog is
   the technical stream. Keep both, or switch to Habr.

9. **Category inconsistency.** The Habr hubs are `category: community` while `opennet` is `media` —
   fine — but `slurm` is `vendor` when it is really an education/media source, and `yandexcloud`/
   `vkcloud` are `cloud` while `selectel` is `vendor` despite all three being IaaS providers. Not
   load-bearing unless the scorer keys off category, but worth normalising.

10. **No dedupe strategy for the RU section, and it now needs one.** Habr articles will arrive
    through up to three paths simultaneously: the hub feed, the company feed, and `habr-news`. The
    `oleg-bunin`/`cloud_ru` cross-post found during verification proves company feeds overlap each
    other too. Dedupe on the Habr article ID (present in every `<link>` as
    `/articles/<id>/`) before scoring, or the RU section will double- and triple-count.
