---
id: RHE.ILL.287
trope_type: case
source_text: |
  "When an attribute has a fixed range of values—as the colour attribute does here—
  the substance paradigm's independent attribute hierarchy has to be reconstructed 
  anew as dependent attributes for each of the entity types. This significantly reduces 
  the re-use potential."
structural_core: "[Упрощение парадигмы] (отказ от независимой иерархии) → [потеря переиспользуемости] → [вынужденное дублирование] → [архитектурный трейд-офф]"
illustrates:
  - concept_id: TBD
    concept_description: "Архитектурный трейд-офф между простотой реализации (paper-and-ink technology) и гибкостью систем (переиспользуемость)"
    pack_ref: PACK-personal
source_domain: "информатика, парадигмы данных, архитектура"
audience_level: 4
effect: explain
canonical: true
breaks_when: "если атрибуты редко переиспользуются, или если стоимость дублирования ниже стоимость сложности централизованной иерархии, или если система не требует переиспользования"
origin_source: "book:part_ae"
quality_score: 0.85
status: draft
created: 2026-05-20
---

# [RHE.ILL.287] Архитектурный трейд-офф между простотой реализации (paper-and-ink technology) и гибкостью систем (переиспользуемость)

## Source

"When an attribute has a fixed range of values—as the colour attribute does here—
the substance paradigm's independent attribute hierarchy has to be reconstructed 
anew as dependent attributes for each of the entity types. This significantly reduces 
the re-use potential."

## Structural Core

[Упрощение парадигмы] (отказ от независимой иерархии) → [потеря переиспользуемости] → [вынужденное дублирование] → [архитектурный трейд-офф]

## Boundaries (breaks_when)

если атрибуты редко переиспользуются, или если стоимость дублирования ниже стоимость сложности централизованной иерархии, или если система не требует переиспользования

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
