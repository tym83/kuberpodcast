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
