---
id: RHE.ILL.306
trope_type: example
source_text: |
  On its left-hand side is a model with no secondary substance hierarchy, where the car and van substances both have a colour attribute. On its right hand side is the same model with a secondary hierarchy. In this model, there is only one colour attribute that belongs to the vehicle substance and is inherited by the car and van substances. Two attributes are compacted into one.
structural_core: "Когда атрибут (COLOUR) определён один раз на верхнем уровне (VEHICLE), он автоматически наследуется подтипами (CAR, VAN), что компактирует информацию: 2 дублирующихся атрибута → 1 общий"
illustrates:
  - concept_id: TBD
    concept_description: "Переиспользование атрибутов через вторичные иерархии вещества для компактации информации"
    pack_ref: PACK-personal
source_domain: "объектно-ориентированное проектирование, наследование в типах данных"
audience_level: 3
effect: scaffold
canonical: true
breaks_when: "если система не поддерживает наследование или требует явного определения каждого атрибута в каждом подклассе"
origin_source: "book:part_af"
quality_score: 0.90
status: draft
created: 2026-05-20
---

# [RHE.ILL.306] Переиспользование атрибутов через вторичные иерархии вещества для компактации информации

## Source

On its left-hand side is a model with no secondary substance hierarchy, where the car and van substances both have a colour attribute. On its right hand side is the same model with a secondary hierarchy. In this model, there is only one colour attribute that belongs to the vehicle substance and is inherited by the car and van substances. Two attributes are compacted into one.

## Structural Core

Когда атрибут (COLOUR) определён один раз на верхнем уровне (VEHICLE), он автоматически наследуется подтипами (CAR, VAN), что компактирует информацию: 2 дублирующихся атрибута → 1 общий

## Boundaries (breaks_when)

если система не поддерживает наследование или требует явного определения каждого атрибута в каждом подклассе

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
