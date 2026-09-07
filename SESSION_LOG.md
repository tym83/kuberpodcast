# Session log — kuberpodcast weekly digest (started 2026-09-07)

## Цель
Еженедельный автосбор топ-100 ссылок по DevOps/Kubernetes/инфре/облакам в `digest/<date>.md` репозитория `tym83/kuberpodcast`, с автомерджем по расписанию.

## Текущее состояние
- Репозиторий: https://github.com/tym83/kuberpodcast — создан, **public**, пустой (первый пуш не делался)
- Локальная копия: `~/projects/kuberpodcast`, venv `.venv` (feedparser, requests, pyyaml)
- Черновик источников: `sources/feeds.yaml` (~160 фидов), `sources/community.yaml` (Reddit/HN/Lobsters/dev.to), `sources/releases.yaml` (~230 GitHub-репо)
- Написано: `digestbot/util.py`, `digestbot/collect.py`
- Пять ревьюеров запущены: 1 валидация URL, 2 EN-покрытие, 3 RU-покрытие, 4 CN/JP/KR/EU, 5 редакционный дизайн дайджеста

## Следующий шаг
Дождаться отчётов ревьюеров (`sources/review-*.md`), влить правки в конфиги, дописать dedup/score/render, собрать первый дайджест.

## Известные ограничения инфраструктуры
- Reddit блокирует анонимный JSON API из ДЦ (403) и лимитирует .rss (429) → нужен OAuth-app (`REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET`), фолбэк на .rss с ранговым прокси-скором
- InfoQ China отдаёт 451 из US-egress — часть китайских источников может быть недоступна с GitHub-раннеров

## Журнал

### 18:50 — старт
Проверены сеть и эндпоинты: HN Algolia 200, CNCF 200, kubernetes.io 200, GitHub API 200, Habr 200, Lobsters 200, Hatena 200; Reddit JSON 403, InfoQ CN 451, OSChina 403.

### 19:10 — черновик источников
Написаны `sources/feeds.yaml`, `sources/community.yaml`, `sources/releases.yaml`.

### 19:20 — репозиторий
`gh repo create tym83/kuberpodcast --public`. Локально `git init`, remote `origin`, ветка `main`.

### 19:25 — движок
`digestbot/util.py` (HTTP-сессия, канонизация URL, определение языка, окно дат), `digestbot/collect.py` (RSS, HN Algolia, Reddit OAuth+RSS, Lobsters, dev.to, GitHub Releases).

### 19:55 — редакционное ревью (тиммейт №5) принято
Получена спецификация `sources/review-5-editorial.md` (1167 строк). Ключевое:
- 11 секций с квотами на 100 (headline 8 — по промоушену, не отдельными слотами; releases 18; deep 16; nonenglish 12 с подквотами ru5/zh4/ja1/ko1/de1 — заполняется ПЕРВОЙ и защищена от вытеснения)
- формула `base = 26*TOP + 20*SRC + 18*ENG + 14*FORM + 12*ORIG + 10*REC`, порог допуска 45
- жёсткий topic-gate `TOP < 0.20` → off_topic
- `tier:` в releases.yaml инертен (12 из 14 групп tier 1) → заменить на per-repo `min_bump`
- нет ни одного источника, который надёжно даёт CVE и постмортемы, хотя под них зарезервировано 13 слотов
- ньюслеттеры надо майнить на исходящие ссылки, а не публиковать как записи

### 20:10 — движок под спецификацию
Написаны: `digestbot/filters.py` (все reason codes), `score.py` (формула, кластеризация, классификатор секций, отбор по квотам), `freshness.py` (цепочка разрешения дат, late arrivals, old-link для HN/Reddit), `text.py` (trafilatura + дисковый кэш), `state.py` (sqlite emitted + feed health), `signals.py` (CVE-фиды, GitHub advisories, статус-страницы, майнинг ньюслеттеров, CNCF TOC / KEP).
Конфиги: `sources/editorial.yaml`, `sources/blocklists.yaml`, `sources/signals.yaml`.

### 20:30 — пайплайн собран и прогнан
`collect_raw.py` → `build_digest.py` отрабатывает end-to-end на пробных данных.
Найдено и починено:
- URL релизов `…/releases/tag/v1.19.0` попадал под regex листингов → все 55 релизов отбрасывались как `not_an_article`
- дата-теги вида `release-20260831.0` не ловились
- в markdown подставлялся сырой URL с utm-метками вместо канонического
Остаётся мало кандидатов (24 из 100) — потому что 54 фида мертвы и Reddit не отдаёт данные.

### 21:10 — ревью источников влито (тиммейты №1, №3, №4)
- **Валидация (№1):** из 184 фидов 110 живы как есть, 48 URL исправлены и перепроверены, 19 мертвы без замены. Два тихих бага в коде: фиды без таймзоны в pubDate (Grafana) полностью выпадали, и Hugo-шаблоны с датой `0001-01-01` считались валидными. Оба починены.
- **RU (№3):** 5 из 13 русских записей были сломаны (`blog.flant.ru` не резолвится, у Deckhouse нет RSS вообще, `vk.cloud` не отдаёт TLS с не-российских IP). Влито 68 проверенных фидов + 6 YouTube-каналов. Habr-URL нормализуются между хабом, компанией и новостями — иначе одна статья приходила трижды.
- **INT (№4):** влито 66 фидов zh/ja/ko/EU. openEuler, CSDN, SegmentFault, публичный RSSHub блокируют ДЦ-трафик с двух континентов. Добавлен сборщик Juejin через открытый content API — единственный автоматизируемый путь к китайским техкомандам (ByteDance и Alibaba ушли в WeChat, туда нужен платный мост).

Каталог: **302 фида** (en 149, ru 82, ja 24, zh 23, de 6, ko 6, fr 5, pl 3, pt 2, es 1, nl 1), 28 сабреддитов, 228 репозиториев, CVE-фиды, статус-страницы 12 провайдеров.

### 21:20 — блокеры, которые не лечатся кодом
- **Reddit** отдаёт 429 на всё с этого IP и с ДЦ-адресов вообще. Нужен OAuth-app (тип *script*) и секреты `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`. Без них добавлен circuit breaker: после трёх отказов подряд остальные сабреддиты пропускаются, а не выжигают минуты на ретраях.
- **ANTHROPIC_API_KEY** локально отсутствует, поэтому комментарии к первому дайджесту пишутся вручную и подставляются через `--comments`.

### 21:45 — ревью английских источников влито (тиммейт №2)
134 проверенных фида и 109 репозиториев. Каталог: **441 фид** (en 285, ru 82, zh 26, ja 24, de 6, ko 6, fr 5, pl 3, pt 2, es 1, nl 1), **337 репозиториев**.
Что ещё вскрылось и починено:
- Google Groups убил публичные фиды → `kubernetes-announce` и `kubernetes-security-announce` недоступны, остаются CVE-JSON и per-repo GitHub advisories
- фид Anyscale мёртв (одна запись за 2025) → удалён, релизы Ray и так в `releases.yaml`
- REST API GitHub без токена отдаёт 403 после ~70 репозиториев → добавлен фолбэк на `releases.atom`
- некоторые блоги (rachelbythebay) отдают 429 при двух одновременных запросах → добавлена сериализация по хосту, иначе источник молча исчезает из дайджеста

### Что нельзя автоматизировать (проверено с двух континентов)
- openEuler (Huawei WAF), CSDN 521, SegmentFault 410, публичный RSSHub 403 для ДЦ-адресов
- WeChat 公众号 (字节跳动技术团队, 阿里巴巴云原生) — нужен платный мост wechat2rss или self-hosted
- `linux.cn`, `blog.daocloud.io`, `tech.didiglobal.com`, `sealer.sh`, `servicemesher.com` — NXDOMAIN, домены мертвы
