---
id: RHE.ILL.262
trope_type: example
source_text: |
  A general entity-attribute pattern is used to construct entity type patterns (staff member, car), 
  which in turn construct individual patterns. For instance, a car entity type provides a 
  framework for constructing patterns for specific cars like "my car" with attributes 
  such as "3.5 metres" (length) and "red" (colour).
structural_core: "Hierarchical reuse of pattern structure: [General pattern] → [Type level patterns] → [Individual level patterns]"
illustrates:
  - concept_id: TBD
    concept_description: "How abstract patterns are recursively applied at lower levels of abstraction to maintain consistency and enable efficient generation of new instances"
    pack_ref: PACK-personal
source_domain: "Object-oriented design, taxonomy"
audience_level: 3
effect: scaffold
canonical: true
breaks_when: "When new entity types emerge that don't fit existing type-level patterns, requiring new abstraction levels"
origin_source: "book:part_ad"
quality_score: 0.85
status: draft
created: 2026-05-20
---

# [RHE.ILL.262] How abstract patterns are recursively applied at lower levels of abstraction to maintain consistency and enable efficient generation of new instances

## Source

A general entity-attribute pattern is used to construct entity type patterns (staff member, car), 
which in turn construct individual patterns. For instance, a car entity type provides a 
framework for constructing patterns for specific cars like "my car" with attributes 
such as "3.5 metres" (length) and "red" (colour).

## Structural Core

Hierarchical reuse of pattern structure: [General pattern] → [Type level patterns] → [Individual level patterns]

## Boundaries (breaks_when)

When new entity types emerge that don't fit existing type-level patterns, requiring new abstraction levels

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
