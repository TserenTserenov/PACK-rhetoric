---
id: RHE.ILL.399
trope_type: analogy
source_text: |
  Weak class pattern вынудил считать Minis отдельным объектом, требуя связать его обратно
  к отдельным автомобилям через contrived types-of tuples класс.
  Strong class pattern позволяет признать Minis как класс и одновременно как члена car types.
  Результирующая иерархия более выразительна и имеет более простую, связную структуру.
structural_core: "[Weak] вынужденное неестественное представление + промежуточные связи → усложнение; [Strong] прямое представление + минимум связей → простота и ясность"
illustrates:
  - concept_id: TBD
    concept_description: "мощь выбора парадигмы в моделировании; как парадигматические ограничения принуждают к обходным путям"
    pack_ref: PACK-personal
source_domain: "логика, системное проектирование"
audience_level: 3
effect: persuade
canonical: true
breaks_when: "когда парадигма выбрана и её ограничения некритичны, или когда обе структуры семантически эквивалентны"
origin_source: "book:part_ag"
quality_score: 0.85
status: draft
created: 2026-05-20
---

# [RHE.ILL.399] мощь выбора парадигмы в моделировании; как парадигматические ограничения принуждают к обходным путям

## Source

Weak class pattern вынудил считать Minis отдельным объектом, требуя связать его обратно
к отдельным автомобилям через contrived types-of tuples класс.
Strong class pattern позволяет признать Minis как класс и одновременно как члена car types.
Результирующая иерархия более выразительна и имеет более простую, связную структуру.

## Structural Core

[Weak] вынужденное неестественное представление + промежуточные связи → усложнение; [Strong] прямое представление + минимум связей → простота и ясность

## Boundaries (breaks_when)

когда парадигма выбрана и её ограничения некритичны, или когда обе структуры семантически эквивалентны

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
