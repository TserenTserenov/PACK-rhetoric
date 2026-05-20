---
id: RHE.ILL.248
trope_type: example
source_text: |
  Assume we are building a model of a money market trading system focusing on $ and £ term deposit deals. We notice these two types have a similar pattern of settlement: principal paid away on agreed date, principal plus interest received back after agreed term.
structural_core: "два типа финансовых инструментов ($ term deposits и £ term deposits) имеют одинаковый структурный паттерн расчёта (дата платежа принципала, возврат с процентами), но переиспользование кода и переиспользование понимания (обобщение паттерна) — разные уровни"
illustrates:
  - concept_id: TBD
    concept_description: "различие между operational re-use (копирование кода) и understanding-level generalization (нахождение общих структурных паттернов); важность различия understanding vs operation"
    pack_ref: PACK-personal
source_domain: "финансовые системы / объектное программирование"
audience_level: 3
effect: scaffold
canonical: true
breaks_when: "если паттерны структурно отличаются (например, один инструмент имеет промежуточные выплаты процентов); если реализационные детали не позволяют обобщить"
origin_source: "book:part_ac"
quality_score: 0.80
status: draft
created: 2026-05-20
---

# [RHE.ILL.248] различие между operational re-use (копирование кода) и understanding-level generalization (нахождение общих структурных паттернов); важность различия understanding vs operation

## Source

Assume we are building a model of a money market trading system focusing on $ and £ term deposit deals. We notice these two types have a similar pattern of settlement: principal paid away on agreed date, principal plus interest received back after agreed term.

## Structural Core

два типа финансовых инструментов ($ term deposits и £ term deposits) имеют одинаковый структурный паттерн расчёта (дата платежа принципала, возврат с процентами), но переиспользование кода и переиспользование понимания (обобщение паттерна) — разные уровни

## Boundaries (breaks_when)

если паттерны структурно отличаются (например, один инструмент имеет промежуточные выплаты процентов); если реализационные детали не позволяют обобщить

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
