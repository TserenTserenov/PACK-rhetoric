---
id: RHE.MAP.001
name: PACK-rhetoric Navigation Map
status: active
valid_from: 2026-05-19
schema_version: 1
---

# RHE.MAP.001 — Navigation Map

## Pack Status

| Тип | Кол-во | Статус |
|-----|--------|--------|
| Сущности (D) | 4 | RHE.D.001-004 |
| Формализации (FORM) | 2 | RHE.FORM.001-002 |
| Методы (METHOD) | 7 | RHE.METHOD.001-007 |
| SOTA | 3 | RHE.SOTA.001-003 |
| Service Clause | 1 | DP.SC.149 (в PACK-digital-platform) |
| Карточки active | 71 | illustrations/{type}/*.md (+ RHE.ILL.497, 2026-07-10) |
| Карточки pending | 2 | illustrations/pending/*.md |

> **Примечание (2026-07-10):** до этой правки карта не отражала RHE.D.003, RHE.METHOD.001-003, RHE.SOTA.002 — они существовали на диске с 2026-06-20, но не попали в карту при создании. Обновлено заодно с добавлением 2026-07-10.

## Сущности

| ID | Файл | Описание |
|----|------|----------|
| RHE.D.001 | 02-domain-entities/RHE.D.001-illustration.md | Illustration — карточка риторического приёма |
| RHE.D.002 | 02-domain-entities/RHE.D.002-trope-taxonomy.md | TropeTaxonomy — 5 типов тропов |
| RHE.D.003 | 02-domain-entities/RHE.D.003-corpus-source.md | CorpusSource |
| RHE.D.004 | 02-domain-entities/RHE.D.004-content-system-taxonomy.md | Таксономия личного контент-конвейера созидателя (5 осей) |

## Формализации и методы

| ID | Файл | Описание |
|----|------|----------|
| RHE.FORM.001 | 05-formalizations/RHE.FORM.001-illustration-card.md | Схема карточки (14 полей) |
| RHE.FORM.002 | 05-formalizations/RHE.FORM.002-trope-validation.md | Критерии валидации по типу тропа |
| RHE.METHOD.001 | 05-formalizations/RHE.METHOD.001-and-but-therefore.md | И-Но-Следовательно (Olson, Parker/Stone) |
| RHE.METHOD.002 | 05-formalizations/RHE.METHOD.002-narrative-immersion.md | Погружение в нарратив |
| RHE.METHOD.003 | 05-formalizations/RHE.METHOD.003-through-line.md | Сквозная линия (Anderson, Ogilvy) |
| RHE.METHOD.004 | 05-formalizations/RHE.METHOD.004-bridge-phrase.md | Мост-фраза (контекстный, 1 источник) |
| RHE.METHOD.005 | 05-formalizations/RHE.METHOD.005-finale-sharpen-not-recap.md | Финал без пересказа (контекстный) |
| RHE.METHOD.006 | 05-formalizations/RHE.METHOD.006-thesis-ordering-for-thinking-audience.md | Порядок тезисов для думающей аудитории (контекстный) |
| RHE.METHOD.007 | 05-formalizations/RHE.METHOD.007-adapt-dont-adopt.md | Adapt, don't adopt: форма без тональности (контекстный) |

## Различения (01B)

| Различение | Суть |
|-----------|------|
| Illustration ≠ Concept | Карточка = экземпляр приёма, не сам концепт |
| Illustration ≠ Code example | Объяснение через аналогию, не код |
| Illustration ≠ Assignment | Показывает, не учит делать |
| Structural ≠ Surface transfer | structural_core = реляционное отображение |
| Canonical ≠ Contextual | Canonical = проверен, устойчив |
| Illustration ≠ Metaphor-as-definition | Метафора объясняет, не определяет |
| effect:explain ≠ persuade ≠ scaffold | Показывает / убеждает / направляет мышление |

## SOTA

| ID | Файл | Охват |
|----|------|-------|
| RHE.SOTA.001 | 06-sota/RHE.SOTA.001-modern-rhetoric.md | Современная риторика + Structure-Mapping Theory |
| RHE.SOTA.002 | 06-sota/RHE.SOTA.002-short-enlightenment-format.md | Короткий просветительский формат (видео ~1 мин) |
| RHE.SOTA.003 | 06-sota/RHE.SOTA.003-camera-authenticity-signal.md | Лицо в камере как сигнал подлинности — статус: hypothesis, не лит-обзор |

## Матрица связей

| FORM.001 (схема) | → | D.001 (Illustration) | describes schema |
| FORM.002 (валидация) | → | D.002 (TropeTaxonomy) | validates per type |
| illustrations/*.md | → | FORM.001 | conforms to |
| illustrations/*.md | → | PACK-personal PD.CHR/ROLE/STATE | illustrates concept_id |
| DP.SC.149 | → | illustrations/ | produces |
| DP.AISYS.013 §4.9 | → | DP.SC.149 | implements M-RM |

## Типы карточек по трому

| Тип | Кол-во active | Ключевое правило |
|-----|--------------|-----------------|
| analogy | ~13 | structural_core реляционный + breaks_when |
| metaphor | ~22 | property transfer + breaks_when |
| example | ~10 | concrete details |
| case | ~4 | conflict в source_text |
| counter_example | ~10 | failure_mechanism + audience_level ≥ 3 |

## Update Log

| Дата | Изменение |
|------|-----------|
| 2026-05-19 | Создан. 70 active + 2 pending карточек после Ф1-Ф6 WP-340 |
| 2026-07-10 | Peer-session apply-captures: +RHE.D.004, +RHE.METHOD.004-007, +RHE.SOTA.003, +RHE.ILL.497. Заодно синхронизирована карта с диском (D.003, METHOD.001-003, SOTA.002 существовали, но не были внесены). Pack впервые зарегистрирован в `DS-ai-systems/extractor/config/routing.md`, scope манифеста расширен (не только IWE-концепты — жизнь и мировоззрение созидателя) |
