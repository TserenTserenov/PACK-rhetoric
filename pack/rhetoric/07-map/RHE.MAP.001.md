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
| Сущности (D) | 2 | RHE.D.001-002 |
| Формализации (FORM) | 2 | RHE.FORM.001-002 |
| SOTA | 1 | RHE.SOTA.001 |
| Service Clause | 1 | DP.SC.149 (в PACK-digital-platform) |
| Карточки active | 70 | illustrations/{type}/*.md |
| Карточки pending | 2 | illustrations/pending/*.md |

## Сущности

| ID | Файл | Описание |
|----|------|----------|
| RHE.D.001 | 02-domain-entities/RHE.D.001-illustration.md | Illustration — карточка риторического приёма |
| RHE.D.002 | 02-domain-entities/RHE.D.002-trope-taxonomy.md | TropeTaxonomy — 5 типов тропов |

## Формализации

| ID | Файл | Описание |
|----|------|----------|
| RHE.FORM.001 | 05-formalizations/RHE.FORM.001-illustration-card-schema.md | Схема карточки (14 полей) |
| RHE.FORM.002 | 05-formalizations/RHE.FORM.002-trope-validation.md | Критерии валидации по типу тропа |

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
| analogy | ~12 | structural_core реляционный + breaks_when |
| metaphor | ~22 | property transfer + breaks_when |
| example | ~10 | concrete details |
| case | ~4 | conflict в source_text |
| counter_example | ~10 | failure_mechanism + audience_level ≥ 3 |

## Update Log

| Дата | Изменение |
|------|-----------|
| 2026-05-19 | Создан. 70 active + 2 pending карточек после Ф1-Ф6 WP-340 |
