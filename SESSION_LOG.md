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
