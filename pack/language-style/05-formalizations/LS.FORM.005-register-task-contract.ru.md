---
id: LS.FORM.005
type: register
name: Регистр контракта задачи (исполнитель)
name_en: Task-contract register
status: draft
created: 2026-06-11
valid_from: 2026-06-11
wp: WP-412
lang: ru
role: canon
context_key:
  reader_meta_class: agent
  reader_role: executor
  channel: task-contract
  domain: "*"
content_source: LS.agent-agent
stance: neutral
explicitness: max
projection: read-only
---

# [LS.FORM.005] Регистр контракта задачи

> Контракт задачи в очереди агента (Agent Inbox, WP-324). Позиция нейтральная, точность максимальная: входы, выходы, инвариант явно. Источник правил: агент-агентная база (LS.D.003). Жанровые секции (`overlays/genre/task-contract`): FACT = входные данные/контекст, TODO = требуемый результат, BLOCKER = ограничения/инварианты, ACCEPTED = критерии приёмки.
