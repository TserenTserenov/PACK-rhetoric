---
id: RHE.ILL.490
trope_type: example
source_text: |
  "A car owned by a garage is then owned by a new owner. The ownership attribute changes. To resolve this in object semantics, divide the car object into states: car-owned-by-garage state before sale, and car-owned-by-new-owner state after sale. Each state constructs a tuple with its respective owner."
structural_core: "Relational-attribute change modeled through state-division: [State-1:object-in-relation-A] —[event]→ [State-2:object-in-relation-B]; tuple-change becomes tuple-sequence of state-objects"
illustrates:
  - concept_id: TBD
    concept_description: "Modeling temporal change in relational attributes through state-objects rather than attribute modification; timeless representation of change"
    pack_ref: PACK-personal
source_domain: "object-semantics/commerce"
audience_level: 3
effect: explain|scaffold
canonical: true
breaks_when: "Ownership is non-transferable, sale is reversible/incomplete, object identity cannot be preserved across sale, or ownership is essential to object-definition rather than relational property"
origin_source: "book:part_ai"
quality_score: 0.87
status: draft
created: 2026-05-20
---

# [RHE.ILL.490] Modeling temporal change in relational attributes through state-objects rather than attribute modification; timeless representation of change

## Source

"A car owned by a garage is then owned by a new owner. The ownership attribute changes. To resolve this in object semantics, divide the car object into states: car-owned-by-garage state before sale, and car-owned-by-new-owner state after sale. Each state constructs a tuple with its respective owner."

## Structural Core

Relational-attribute change modeled through state-division: [State-1:object-in-relation-A] —[event]→ [State-2:object-in-relation-B]; tuple-change becomes tuple-sequence of state-objects

## Boundaries (breaks_when)

Ownership is non-transferable, sale is reversible/incomplete, object identity cannot be preserved across sale, or ownership is essential to object-definition rather than relational property

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
