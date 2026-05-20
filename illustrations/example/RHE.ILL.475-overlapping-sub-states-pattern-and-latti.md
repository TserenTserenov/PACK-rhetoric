---
id: RHE.ILL.475
trope_type: example
source_text: |
  A lepidopteran becomes infected while in caterpillar state and remains infected through metamorphosis into pupa state. The infected state overlaps both the caterpillar and pupa states, creating infected caterpillar and infected pupa sub-states. These overlapping sub-states form a lattice hierarchy, not a tree hierarchy.
structural_core: "Состояние может пересекать несколько других состояний в иерархии, создавая комбинаторные суб-состояния; это требует решётчатой структуры вместо древовидной"
illustrates:
  - concept_id: TBD
    concept_description: "Overlapping sub-states pattern and lattice hierarchy structure (vs distinct states and tree hierarchy)"
    pack_ref: PACK-personal
source_domain: "биология / жизненные циклы"
audience_level: 4
effect: explain
canonical: true
breaks_when: "когда состояния строго упорядочены (объект может находиться только в одном из набора исключающих друг друга состояний)"
origin_source: "book:part_ai"
quality_score: 0.94
status: draft
created: 2026-05-20
---

# [RHE.ILL.475] Overlapping sub-states pattern and lattice hierarchy structure (vs distinct states and tree hierarchy)

## Source

A lepidopteran becomes infected while in caterpillar state and remains infected through metamorphosis into pupa state. The infected state overlaps both the caterpillar and pupa states, creating infected caterpillar and infected pupa sub-states. These overlapping sub-states form a lattice hierarchy, not a tree hierarchy.

## Structural Core

Состояние может пересекать несколько других состояний в иерархии, создавая комбинаторные суб-состояния; это требует решётчатой структуры вместо древовидной

## Boundaries (breaks_when)

когда состояния строго упорядочены (объект может находиться только в одном из набора исключающих друг друга состояний)

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
