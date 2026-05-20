---
id: RHE.ILL.291
trope_type: counter_example
source_text: |
  Many-to-many associations (agents work on multiple initiatives; each initiative has multiple agents) cannot be expressed via attribute patterns. Solution: create intermediate pseudo-entity even though no real-world equivalent exists. This forces modeling as if false entities were real.
structural_core: "N-to-M relation + attribute-only paradigm = fabrication of non-existent intermediate entity"
illustrates:
  - concept_id: TBD
    concept_description: "Paradigm weakness forces construction of false ontological entities"
    pack_ref: PACK-personal
source_domain: "database design / conceptual modeling"
audience_level: 3
effect: persuade
canonical: true
breaks_when: "when you need to express many-to-many without inventing ontological falsehoods"
origin_source: "book:part_ae"
quality_score: 0.90
status: draft
created: 2026-05-20
---

# [RHE.ILL.291] Paradigm weakness forces construction of false ontological entities

## Source

Many-to-many associations (agents work on multiple initiatives; each initiative has multiple agents) cannot be expressed via attribute patterns. Solution: create intermediate pseudo-entity even though no real-world equivalent exists. This forces modeling as if false entities were real.

## Structural Core

N-to-M relation + attribute-only paradigm = fabrication of non-existent intermediate entity

## Boundaries (breaks_when)

when you need to express many-to-many without inventing ontological falsehoods

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
