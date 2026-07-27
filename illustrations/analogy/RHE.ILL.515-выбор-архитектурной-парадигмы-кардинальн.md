---
id: RHE.ILL.515
trope_type: analogy
source_text: |
  when the scope is increased, the overall complexity of the system increases. 
  Business objects handle increases in scope in a very different way. Each new pattern, 
  instead of adding to complexity, provides an opportunity for compacting a number of 
  patterns into a single, more general pattern.
structural_core: "выбор парадигмы [сущности vs объекты] + масштабирование [системы] → динамика сложности [линейный рост vs компактификация]; роль парадигмы = определить траекторию эволюции сложности"
illustrates:
  - concept_id: TBD
    concept_description: "выбор архитектурной парадигмы кардинально влияет на масштабируемость модели при расширении области применения"
    pack_ref: PACK-personal
source_domain: "software engineering / system modeling"
audience_level: 4
effect: persuade
canonical: true
breaks_when: "когда новые паттерны полностью ортогональны и не могут быть обобщены; когда масштабирование физически требует дополнительную сложность (распределённость)"
origin_source: "book:part_ab"
quality_score: 0.90
status: draft
created: 2026-05-20
---

# [RHE.ILL.002] выбор архитектурной парадигмы кардинально влияет на масштабируемость модели при расширении области применения

## Source

when the scope is increased, the overall complexity of the system increases. 
Business objects handle increases in scope in a very different way. Each new pattern, 
instead of adding to complexity, provides an opportunity for compacting a number of 
patterns into a single, more general pattern.

## Structural Core

выбор парадигмы [сущности vs объекты] + масштабирование [системы] → динамика сложности [линейный рост vs компактификация]; роль парадигмы = определить траекторию эволюции сложности

## Boundaries (breaks_when)

когда новые паттерны полностью ортогональны и не могут быть обобщены; когда масштабирование физически требует дополнительную сложность (распределённость)

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
