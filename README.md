# kuberpodcast — еженедельный дайджест

Автоматическая подборка топ-100 ссылок недели по DevOps, Kubernetes, инфраструктуре
и облакам — для подготовки выпусков подкаста.

Готовые дайджесты лежат в [`digest/`](digest/). Каждую неделю туда автоматически
добавляется новый файл `digest/<дата>.md`.

## Что внутри дайджеста

| Файл | Что это |
|---|---|
| `digest/<дата>.md` | Полный выпуск: 100 ссылок по секциям, у каждой — заголовок в оригинале и русский комментарий «Что внутри» / «Почему важно» |
| `digest/<дата>-short.md` | 15 позиций одной строкой — под шоу-ноты |
| `digest/<дата>-rejected.md` | Что фильтры выбросили и почему. Единственный способ заметить, что регулярка убила целый источник |

Секции и их квоты (в сумме 100) заданы в [`sources/editorial.yaml`](sources/editorial.yaml):
главное недели, релизы, глубокие тексты, не на английском (защищённая квота с
подквотами по языкам), дискуссии, безопасность, AI-инфраструктура, экосистема и
деньги, инциденты, слабые сигналы, длинное чтение.

## Источники

| Файл | Что описывает |
|---|---|
| `sources/feeds.yaml` | RSS/Atom: фундации, апстрим-проекты, вендоры, облака, медиа, персональные блоги, ru/zh/ja/ko-источники |
| `sources/community.yaml` | Reddit, Hacker News, Lobsters, dev.to |
| `sources/releases.yaml` | GitHub-репозитории и порог новостности для каждого (`min_bump`) |
| `sources/signals.yaml` | CVE-фиды и GitHub Security Advisories, статус-страницы провайдеров, майнинг ньюслеттеров, CNCF TOC и KEP |
| `sources/blocklists.yaml` | Фильтры шума: SEO-листиклы, пресс-релизы, туториалы для начинающих, AI-слоп, Reddit-хелпдеск, вакансии |
| `sources/editorial.yaml` | Квоты секций, формула скоринга, правила свежести и дедупликации |

Обоснование всех правил — в [`sources/review-5-editorial.md`](sources/review-5-editorial.md).

## Как это работает

```
scripts/collect_raw.py     фидов → сырые кандидаты (data/raw.json)
        ↓
scripts/build_digest.py    дедуп → свежесть → фильтры → скоринг → квоты → markdown
```

Отбор: `base = 26·TOP + 20·SRC + 18·ENG + 14·FORM + 12·ORIG + 10·REC`, дальше
поправки на кластеризацию (одна новость не занимает больше двух слотов), на
домен и на проект. Порог допуска — 45; если материалов на 100 позиций не набралось,
файл выйдет короче, но порог не понижается.

Комментарии пишет Claude по полному тексту статьи (`digestbot/enrich.py`).
Учётка ищется в двух местах: переменная `ANTHROPIC_API_KEY` либо профиль,
созданный `ant auth login` — второй путь не требует статического ключа вообще:

```bash
brew install anthropics/tap/ant
ant auth login          # запускать в обычном терминале: ждёт подтверждения в браузере
ant auth status         # в блоке Credentials должен появиться профиль
```

Без учётки или без кредитов на балансе пайплайн не падает — подставляет
детерминированный комментарий и помечает его как автоматический.
Расход: около 13 запросов и ~53 000 токенов входа на выпуск, то есть примерно
$1 за выпуск на Opus. Модель переключается переменной `DIGEST_MODEL`.

## Запуск вручную

```bash
python -m venv .venv && ./.venv/bin/pip install -r requirements.txt

./.venv/bin/python scripts/collect_raw.py --days 7 --out data/raw.json
./.venv/bin/python scripts/build_digest.py --raw data/raw.json --outdir digest
```

Полезные флаги `build_digest.py`:

- `--limit N` — сколько ссылок в выпуске (по умолчанию из `editorial.yaml`)
- `--no-enrich` — без обращения к модели
- `--comments FILE.json` — подставить готовые комментарии (`id → {what, why, tags, …}`)
- `--selection-out FILE.json` — выгрузить отобранное с разбивкой по компонентам скора
- `--no-state` — не трогать `state/emitted.sqlite` (для первого прогона)

## Расписание

Выпуск собирается двумя путями, основной — локальный.

**Локально (основной).** [`scripts/run_local.sh`](scripts/run_local.sh) делает полный
цикл: собирает, строит, создаёт PR и мёрджит его. Запуск по расписанию — через
launchd, шаблон в [`contrib/io.kuberpodcast.digest.plist`](contrib/io.kuberpodcast.digest.plist):

```bash
sed "s|REPO_DIR|$PWD|g" contrib/io.kuberpodcast.digest.plist \
  > ~/Library/LaunchAgents/io.kuberpodcast.digest.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/io.kuberpodcast.digest.plist
launchctl kickstart -k gui/$(id -u)/io.kuberpodcast.digest   # прогнать сейчас
```

Пятница 09:00 по местному времени. Если машина спала — launchd отработает при
пробуждении. Секреты читаются из `~/.config/kuberpodcast/env` (формат `KEY=value`),
логи пишутся в `~/.local/state/kuberpodcast/`.

**GitHub Actions (резерв).** [`.github/workflows/weekly-digest.yml`](.github/workflows/weekly-digest.yml)
запускается в пятницу в 15:00 UTC и первым делом проверяет, не опубликован ли уже
дайджест за сегодня. Если локальный прогон отработал — джоба выходит, ничего не
делая. Это страховка на случай, если машина была выключена. Ручной запуск — через
`workflow_dispatch` с параметрами окна.

### Секреты

| Секрет | Обязателен | Зачем |
|---|---|---|
| `ANTHROPIC_API_KEY` | нет, но без него комментарии автоматические | Генерация комментариев |
| `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` | практически да | Без них Reddit почти не отдаёт данные — и с раннера, и с локальной машины после нескольких прогонов. Публичный `.rss` не отдаёт ни рейтинг, ни число комментариев, поэтому такие материалы ещё и проигрывают в отборе. OAuth-приложение типа *script* снимает и лимит, и слепоту |
| `GITHUB_TOKEN` | выдаётся автоматически | GitHub Releases и Security Advisories |

## Состояние между запусками

`state/emitted.sqlite` помнит, что уже выходило (8 недель), чтобы одна и та же
новость не появлялась второй раз под другим URL. `state/feed_health.json` считает
подряд идущие отказы каждого фида — мёртвые источники перечислены в подвале
каждого выпуска.
