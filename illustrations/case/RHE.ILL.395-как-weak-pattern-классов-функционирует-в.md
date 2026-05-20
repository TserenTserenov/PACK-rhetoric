---
id: RHE.ILL.395
trope_type: case
source_text: |
  Система с записями типов автомобилей (например, Minis с флагом small=yes) и записями
  конкретных автомобилей (Car #456, Car #789 of type Minis). Система использует weak
  pattern классов, где классы классов не допускаются явно. Система работает интуитивно,
  но важные семантические вопросы о природе type-объектов не задаются.
structural_core: "Условие: система с weak pattern классов + записи типов и экземпляров → Результат: интуитивная работа, но скрытые семантические проблемы при расширении"
illustrates:
  - concept_id: TBD
    concept_description: "Как weak pattern классов функционирует в реальных системах, но маскирует необходимость явной работы с метаклассами при проектировании"
    pack_ref: PACK-personal
source_domain: "системное инженерное проектирование, проектирование баз данных"
audience_level: 2
effect: explain
canonical: true
breaks_when: "когда система растёт и требует явной работы с multiple levels классификации (account types, invoice types, deal types); когда нужно моделировать ограничения на type-объекты"
origin_source: "book:part_ag"
quality_score: 0.78
status: draft
created: 2026-05-20
---

# [RHE.ILL.395] Как weak pattern классов функционирует в реальных системах, но маскирует необходимость явной работы с метаклассами при проектировании

## Source

Система с записями типов автомобилей (например, Minis с флагом small=yes) и записями
конкретных автомобилей (Car #456, Car #789 of type Minis). Система использует weak
pattern классов, где классы классов не допускаются явно. Система работает интуитивно,
но важные семантические вопросы о природе type-объектов не задаются.

## Structural Core

Условие: система с weak pattern классов + записи типов и экземпляров → Результат: интуитивная работа, но скрытые семантические проблемы при расширении

## Boundaries (breaks_when)

когда система растёт и требует явной работы с multiple levels классификации (account types, invoice types, deal types); когда нужно моделировать ограничения на type-объекты

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
