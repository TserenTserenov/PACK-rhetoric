---
id: RHE.ILL.307
trope_type: example
source_text: |
  Consider what happens when we generalise the independent colour attribute connections up a level. We take the connections from car up to vehicle and from sock up to clothes. The colour attribute hierarchy does not have to be rebuilt for each type of vehicle or clothes. The scale of compacting is significant.
structural_core: "Одна иерархия атрибутов (COLOUR) может быть переиспользована на разных ветвях вторичной иерархии вещества (VEHICLE → CAR/VAN и CLOTHES → SOCK), что умножает эффект компактации без дубликатов"
illustrates:
  - concept_id: TBD
    concept_description: "Масштабируемость переиспользования атрибутов через абстракцию на более высокие уровни иерархии"
    pack_ref: PACK-personal
source_domain: "объектно-ориентированное проектирование, универсальные шаблоны"
audience_level: 4
effect: scaffold
canonical: true
breaks_when: "если типы вещества слишком специфичны или имеют несовместимые атрибуты, или если переиспользование создаёт нежелательные связи между доменами"
origin_source: "book:part_af"
quality_score: 0.85
status: draft
created: 2026-05-20
---

# [RHE.ILL.307] Масштабируемость переиспользования атрибутов через абстракцию на более высокие уровни иерархии

## Source

Consider what happens when we generalise the independent colour attribute connections up a level. We take the connections from car up to vehicle and from sock up to clothes. The colour attribute hierarchy does not have to be rebuilt for each type of vehicle or clothes. The scale of compacting is significant.

## Structural Core

Одна иерархия атрибутов (COLOUR) может быть переиспользована на разных ветвях вторичной иерархии вещества (VEHICLE → CAR/VAN и CLOTHES → SOCK), что умножает эффект компактации без дубликатов

## Boundaries (breaks_when)

если типы вещества слишком специфичны или имеют несовместимые атрибуты, или если переиспользование создаёт нежелательные связи между доменами

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
