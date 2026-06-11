---
id: LS.FORM.004
type: register
name: Регистр handoff (исполнитель)
name_en: Handoff register
status: draft
created: 2026-06-11
valid_from: 2026-06-11
wp: WP-412
lang: ru
role: canon
context_key:
  reader_meta_class: agent
  reader_role: executor
  channel: handoff
  domain: "*"
content_source: LS.agent-agent
stance: neutral
explicitness: max
projection: read-only
---

# [LS.FORM.004] Регистр handoff

> Передача контекста агент→агент. Позиция нейтральная, точность максимальная. Источник правил: агент-агентная база (LS.D.003). Жанровые секции FACT/TODO/BLOCKER/ACCEPTED приходят жанровым наложением (`overlays/genre/handoff`): FACT = текущее состояние, TODO = следующие шаги, BLOCKER = препятствия, ACCEPTED = договорённости.
