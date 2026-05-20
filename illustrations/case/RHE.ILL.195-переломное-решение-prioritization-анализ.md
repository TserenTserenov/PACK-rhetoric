---
id: RHE.ILL.195
trope_type: case
source_text: |
  In 1987 a team became involved in a project to re-develop a large investment management system.
  They decided to start by re-engineering the existing system into an O-O business model—a markedly 
  different approach from other O-O projects that mostly used O-O to design and code systems.
  This reverse-engineering approach met two original requirements: documenting the existing system 
  and salvaging investment made in it for re-use in the new system.
structural_core: "[Условие: необходимость переиспользовать существующее знание] + [Условие: документирование существующей системы] → [Решение: reverse engineering в O-O модель] → [Результат: высокие уровни переиспользования, снижение стоимости переразработки]"
illustrates:
  - concept_id: TBD
    concept_description: "Переломное решение: prioritization анализа существующей системы перед greenfield дизайном в O-O проектах"
    pack_ref: PACK-personal
source_domain: "методология разработки ПО, инженерия систем"
audience_level: 3
effect: persuade
canonical: true
breaks_when: "Если существующая система не содержит ценного бизнес-знания или если её архитектура настолько порочна, что переиспользование невозможно или опасно"
origin_source: "book:part_ab"
quality_score: 0.82
status: draft
created: 2026-05-20
---

# [RHE.ILL.195] Переломное решение: prioritization анализа существующей системы перед greenfield дизайном в O-O проектах

## Source

In 1987 a team became involved in a project to re-develop a large investment management system.
They decided to start by re-engineering the existing system into an O-O business model—a markedly 
different approach from other O-O projects that mostly used O-O to design and code systems.
This reverse-engineering approach met two original requirements: documenting the existing system 
and salvaging investment made in it for re-use in the new system.

## Structural Core

[Условие: необходимость переиспользовать существующее знание] + [Условие: документирование существующей системы] → [Решение: reverse engineering в O-O модель] → [Результат: высокие уровни переиспользования, снижение стоимости переразработки]

## Boundaries (breaks_when)

Если существующая система не содержит ценного бизнес-знания или если её архитектура настолько порочна, что переиспользование невозможно или опасно

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
