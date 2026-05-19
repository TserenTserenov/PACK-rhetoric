# PACK-rhetoric — Риторические приёмы

**Домен:** структурированная коммуникация с интенцией  
**Статус:** active  
**Версия:** v0.3.0 (2026-05-19)

## Что это

Библиотека риторических приёмов: аналогий, кейсов, метафор, примеров и контрпримеров для создания руководств, постов и презентаций. Каждый приём — карточка с источником, структурным ядром (structural_core) и привязкой к концептам из PACK-personal.

**Текущий объём:** 70 active + 2 pending карточек

## Для кого

| Потребитель | Зачем |
|-------------|-------|
| Автор руководства/поста | Подобрать иллюстрацию под концепт и уровень аудитории |
| Навигатор-агент (R27) | Аналогия/метафора для ступеней 1-2 |
| R15 Экстрактор (М-RM) | Пополнять из клуба и руководств каждую ночь |

## Структура

```
pack/rhetoric/
├── 00-pack-manifest.md         — скоп, граница домена
├── 01-domain-contract/
│   ├── 01A-domain-contract.md  — bounded context
│   └── 01B-distinctions.md     — 7 ключевых различений
├── 02-domain-entities/
│   ├── RHE.D.001-illustration.md   — сущность «карточка»
│   └── RHE.D.002-trope-taxonomy.md — 5 типов тропов
├── 05-formalizations/
│   ├── RHE.FORM.001-illustration-card-schema.md  — 14 полей
│   └── RHE.FORM.002-trope-validation.md          — критерии по типу
├── 06-sota/
│   └── RHE.SOTA.001-modern-rhetoric.md           — SOTA риторика + ИИ
└── 08-service-clauses/         — через PACK-digital-platform DP.SC.149

illustrations/                  — хранилище карточек
├── analogy/                    — аналогии (structural_core обязателен)
├── metaphor/                   — метафоры (property transfer)
├── example/                    — примеры (concrete details)
├── case/                       — кейсы (conflict + resolution)
├── counter_example/            — контрпримеры (failure mechanism)
└── pending/                    — на проверке (quality_score < 0.6)

scripts/                        — M-RM майнинг
├── rhetoric-miner.py           — основной скрипт (DP.SC.149)
├── rhetoric-miner.sh           — bash обёртка (lock + git)
├── com.iwe.rhetoric-miner.plist — launchd Mac (02:00 МСК)
├── rhetoric-miner.service      — systemd tsekh-1
├── rhetoric-miner.timer        — systemd timer (23:00 UTC)
└── prompts/extract-illustration.md — промпт M-RM

templates/illustration-card.md  — шаблон для ручного добавления
```

## Как найти иллюстрацию

```bash
# По типу тропа
ls illustrations/analogy/

# По концепту
grep -r "PD.CHR.006" illustrations/ --include="*.md" -l

# По теме
grep -r "экзоскелет" illustrations/ --include="*.md" -l
```

## Как добавить иллюстрацию вручную

1. Скопируй `templates/illustration-card.md`
2. Заполни все обязательные поля (id, trope_type, source_text, structural_core, illustrates)
3. Проверь по RHE.FORM.002 (тест для своего типа тропа)
4. Если quality_score ≥ 0.6 → `illustrations/{type}/`; иначе → `illustrations/pending/`

**Обязательные поля по типу:**

| Тип | Обязательные доп. поля |
|-----|----------------------|
| analogy | structural_core (реляционный), breaks_when |
| case | конфликт в source_text, breaks_when |
| metaphor | property transfer, breaks_when |
| example | concrete details, source_domain |
| counter_example | failure_mechanism, audience_level ≥ 3 |

## Ночной майнинг (M-RM)

Скрипт запускается автоматически в 02:00 МСК через launchd (Mac) или systemd (tsekh-1).

**Запустить вручную:**
```bash
python3 scripts/rhetoric-miner.py --source club --since 2026-01-01
```

**Установить launchd:**
```bash
cp scripts/com.iwe.rhetoric-miner.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.iwe.rhetoric-miner.plist
```

## Схема связей

```
PACK-rhetoric ←── DP.SC.149 ←── DP.AISYS.013 §4.9 (M-RM)
     ↑                              (R15 Extractor)
     └── PACK-personal (illustrates.concept_id: PD.CHR.*, PD.ROLE.*, PD.STATE.*)
```
