---
id: RHE.D.003
name: CorpusSource (источник иллюстраций)
type: domain-entity
status: active
created: 2026-05-20
---

# [RHE.D.003] CorpusSource — источник иллюстраций

> Где могут жить материалы для майнинга карточек RHE.ILL. Определяет интерфейс адаптера и правила доступа.

## Зачем

M-RM майнер должен работать с разными источниками единообразно: клуб, руководства, книги, посты в Telegram. Без описания источника адаптер пишется ad-hoc → дрейф контрактов.

## Типы источников

### club — Discourse-форум systemsworld.club

- **Доступ:** REST API (`/posts.json`, `/latest.json`, `/t/{id}.json`)
- **Аутентификация:** `~/.secrets/club_api_token` (Discourse Api-Key)
- **Гранулярность:** пост внутри топика (`club/t/{topic_id}/p/{post_id}`)
- **Сигналы engagement:** `views`, `like_count`, `quote_count`, `incoming_link_count` (post-level), `posts_count` (topic-level)
- **Адаптер:** `scripts/rhetoric-miner.py` режим `topics` (рекомендуемый) или `posts` (legacy)
- **Rate limit:** 1.2 сек между запросами (≤50 req/min)
- **PII-гейт:** анонимизация имён в `extract-illustration.md` промпте

### guide — Руководства PACK-* и DS-principles-curriculum

- **Доступ:** локальные `.md` файлы в `~/IWE/DS-principles-curriculum/`, `~/IWE/PACK-personal/`, `~/IWE/PACK-systems-art/`
- **Гранулярность:** секция/параграф файла
- **Сигнал «годное»:** ручное курирование (нет automated engagement-сигнала)
- **Адаптер:** `rhetoric-miner.py --source guide --file path/to/guide.md`
- **Применение:** Ф3.5 — extraction из готовых руководств перед автомайнингом

### book — Книги (planned)

- **Доступ:** PDF/EPUB через предобработку в plain text
- **Гранулярность:** глава/параграф
- **Сигнал:** ручное курирование + reference из других иллюстраций
- **Адаптер:** не реализован (planned)

### telegram — Каналы и чаты Telegram (planned)

- **Доступ:** через Telegram Bot API или экспорт chat.json
- **Гранулярность:** сообщение в треде
- **Сигнал:** reactions, replies
- **Адаптер:** не реализован (planned)

## Интерфейс адаптера (контракт)

Каждый адаптер `mine_<source>(...)` должен:

1. **Получить корпус** — итератор по единицам (постам/секциям) с rate-limit
2. **Применить engagement-фильтр** — отсечь шум по правилам типа источника
3. **Подать в M-RM экстрактор** — `extract_illustrations_from_text(text, next_id)` → cards
4. **Сохранить через `write_card(card, origin_source=...)`** — origin_source = stable URL/path
5. **Чекпойнт** — `.checkpoint-<source>-<spec>.json` для resume

## Поля карточки, зависимые от источника

| Поле | Источник определяет |
|------|---------------------|
| `origin_source` | формат stable-URL (например, `club/t/{tid}/p/{pid}`) |
| `audience_level` | подразумеваемый уровень читателя (клуб ≥3, гайды ≥1) |
| `canonical` | сигнал «независимых источников» (incoming_link_count для клуба, ручная установка для гайдов) |

## Связи

- **RHE.D.001 (Illustration):** carrier — что хранится в карточке
- **RHE.FORM.002:** валидация — что критично для каждого типа тропа
- **DP.SC.149 (Corpus Mining SC):** обещание майнера — partial-first, PII-gate, engagement-sorted
- **DP.AISYS.013 §4.9 (M-RM метод):** реализация метода
- **scripts/rhetoric-miner.py:** код всех существующих адаптеров
