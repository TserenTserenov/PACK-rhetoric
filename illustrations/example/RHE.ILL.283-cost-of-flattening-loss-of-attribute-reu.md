---
id: RHE.ILL.283
trope_type: example
source_text: |
  The dependent attributes belonging to substances above the selected layer, such as 
  vehicle's colour, disappear along with their substances. The simplification creates 
  a need for two dependent instances of each colour attribute—one for each entity.
structural_core: "[Shared attribute A] in [multi-level hierarchy] → [Single-level flattening] → [Duplication D: A replicated per entity type]"
illustrates:
  - concept_id: TBD
    concept_description: "Cost of flattening: loss of attribute reusability and creation of duplication"
    pack_ref: PACK-personal
source_domain: "database design, data modeling, normalization theory"
audience_level: 4
effect: explain
canonical: true
breaks_when: "When attributes can truly be shared across all entity types without abstraction penalty"
origin_source: "book:part_ae"
quality_score: 0.87
status: draft
created: 2026-05-20
---

# [RHE.ILL.283] Cost of flattening: loss of attribute reusability and creation of duplication

## Source

The dependent attributes belonging to substances above the selected layer, such as 
vehicle's colour, disappear along with their substances. The simplification creates 
a need for two dependent instances of each colour attribute—one for each entity.

## Structural Core

[Shared attribute A] in [multi-level hierarchy] → [Single-level flattening] → [Duplication D: A replicated per entity type]

## Boundaries (breaks_when)

When attributes can truly be shared across all entity types without abstraction penalty

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
