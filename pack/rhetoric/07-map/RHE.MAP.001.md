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
| Контракт домена (BC) | 2 | RHE.BC.001-002 |
| Сущности (D) | 4 | RHE.D.001-004 |
| Формализации (FORM) | 3 | RHE.FORM.001-003 |
| Методы (METHOD) | 11 | RHE.METHOD.001-011 |
| SOTA | 3 | RHE.SOTA.001-003 |
| Service Clause | 1 | RHE.SC.001 |
| Карта | 1 | RHE.MAP.001 |
| Индекс реестра | 1 | registry/memes-index.md |
| Карточки в типовых папках | 541 | illustrations/{type}/*.md |
| Карточки pending | 11 | illustrations/pending/*.md |
| **Карточки всего** | **552** | Фактический подсчёт файлов RHE.ILL.*.md |

> **Примечание (2026-08-08):** карта полностью пересчитана по фактическим файлам. Исторические числа 71 active + 2 pending и перечень RHE.METHOD.001-007 больше не соответствовали диску. «Типовая папка» означает расположение карточки; внутренние legacy-поля `status` не используются для этого счётчика, потому что заполнены непоследовательно.

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
| RHE.FORM.003 | 05-formalizations/RHE.FORM.003-no-bold-headers-under-1000-words.md | Жирные подзаголовки в коротком тексте как структурный шум |
| RHE.METHOD.001 | 05-formalizations/RHE.METHOD.001-and-but-therefore.md | И-Но-Следовательно (Olson, Parker/Stone) |
| RHE.METHOD.002 | 05-formalizations/RHE.METHOD.002-narrative-immersion.md | Погружение в нарратив |
| RHE.METHOD.003 | 05-formalizations/RHE.METHOD.003-through-line.md | Сквозная линия (Anderson, Ogilvy) |
| RHE.METHOD.004 | 05-formalizations/RHE.METHOD.004-bridge-phrase.md | Мост-фраза (контекстный, 1 источник) |
| RHE.METHOD.005 | 05-formalizations/RHE.METHOD.005-finale-sharpen-not-recap.md | Финал без пересказа (контекстный) |
| RHE.METHOD.006 | 05-formalizations/RHE.METHOD.006-thesis-ordering-for-thinking-audience.md | Порядок тезисов для думающей аудитории (контекстный) |
| RHE.METHOD.007 | 05-formalizations/RHE.METHOD.007-adapt-dont-adopt.md | Adapt, don't adopt: форма без тональности (контекстный) |
| RHE.METHOD.008 | 05-formalizations/RHE.METHOD.008-objection-map-skeptic-personas.md | Карта возражений через панель персонажей-скептиков |
| RHE.METHOD.009 | 05-formalizations/RHE.METHOD.009-value-before-mechanics.md | Ценность до механики |
| RHE.METHOD.010 | 05-formalizations/RHE.METHOD.010-two-phrase-tool-limit-hook.md | Двухфразовый хук: утверждение + скрытый предел инструмента |
| RHE.METHOD.011 | 05-formalizations/RHE.METHOD.011-channel-routing-map-before-extraction.md | Карта разбора по каналам до извлечения |

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
| illustrations/*.md | → | Pack-понятия | illustrates[].concept_id + pack_ref |
| RHE.SC.001 | → | illustrations/ | lookup contract |
| DP.SC.149 | → | illustrations/ | produces |
| DP.AISYS.013 §4.9 | → | DP.SC.149 | implements M-RM |

## Типы карточек по типу

| Тип | Кол-во в папке | Ключевое правило |
|-----|--------------|-----------------|
| analogy | 125 | structural_core реляционный + breaks_when |
| metaphor | 105 | property transfer + breaks_when |
| example | 174 | concrete details |
| case | 82 | conflict в source_text |
| counter_example | 55 | failure_mechanism + audience_level ≥ 3 |
| **Всего в типовых папках** | **541** | Не включает 11 карточек pending |

## Update Log

| Дата | Изменение |
|------|-----------|
| 2026-05-19 | Создан. 70 active + 2 pending карточек после Ф1-Ф6 WP-340 |
| 2026-07-10 | Peer-session apply-captures: +RHE.D.004, +RHE.METHOD.004-007, +RHE.SOTA.003, +RHE.ILL.497. Заодно синхронизирована карта с диском (D.003, METHOD.001-003, SOTA.002 существовали, но не были внесены). Pack впервые зарегистрирован в `DS-ai-systems/extractor/config/routing.md`, scope манифеста расширен (не только IWE-концепты — жизнь и мировоззрение созидателя) |
| 2026-08-08 | Полная пересборка по диску, РП-514 Ф3: 552 карточки (541 в типовых папках + 11 pending), FORM.003 и METHOD.008-011 добавлены в навигацию, типовые счётчики пересчитаны без приблизительных значений |
