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

Минимальный контракт записи:

```yaml
status: FACT | TODO | BLOCKER | ACCEPTED
subject: кто или что является носителем действия или утверждения
circumstances: где, когда и при каких условиях это верно
expected_result: какой наблюдаемый результат должен появиться
next_work: какую следующую работу открывает результат
precision_mode: wide | explanatory | engineering
```

- `wide` — навигационная запись: допустим контейнерный термин, но `next_work` обязателен.
- `explanatory` — ключевой термин распакован через субъект, отношение и обстоятельства.
- `engineering` — дополнительно указаны проверяемый результат, носитель результата и критерий приёмки.

Статус `ACCEPTED` допустим только после проверки ожидаемого результата принимающей стороной. Исправление после замечания возвращает запись в `TODO`; `ACCEPTED` ставится заново после повторной проверки.
