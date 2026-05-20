---
id: RHE.ILL.392
trope_type: counter_example
source_text: |
  The weak pattern for classes sees a class as a collection, but does not see that a class 
  is an object—only particular objects are objects. In this scheme of things, the idea of 
  collecting together classes into a class cannot arise because weak classes are not objects.
structural_core: "If [property P is denied to entity E], then [operation O on E becomes impossible] because O presupposes P"
illustrates:
  - concept_id: TBD
    concept_description: "How architectural constraint (treating classes as non-objects) blocks higher-order structuring (meta-classes)"
    pack_ref: PACK-personal
source_domain: "programming language design / logical architecture"
audience_level: 3
effect: persuade|explain
canonical: true
breaks_when: "When treating classes as objects anyway, creating informal or workaround meta-classes in languages that deny them formally"
origin_source: "book:part_ag"
quality_score: 0.80
status: draft
created: 2026-05-20
---

# [RHE.ILL.392] How architectural constraint (treating classes as non-objects) blocks higher-order structuring (meta-classes)

## Source

The weak pattern for classes sees a class as a collection, but does not see that a class 
is an object—only particular objects are objects. In this scheme of things, the idea of 
collecting together classes into a class cannot arise because weak classes are not objects.

## Structural Core

If [property P is denied to entity E], then [operation O on E becomes impossible] because O presupposes P

## Boundaries (breaks_when)

When treating classes as objects anyway, creating informal or workaround meta-classes in languages that deny them formally

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
