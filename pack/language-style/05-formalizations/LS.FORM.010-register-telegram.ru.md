---
id: LS.FORM.010
type: register
name: Регистр Telegram (новичок)
name_en: Telegram register
status: draft
created: 2026-06-11
valid_from: 2026-06-11
wp: WP-412
lang: ru
role: canon
context_key:
  reader_meta_class: human
  reader_role: novice
  channel: telegram
  domain: "*"
content_source: DP.SC.050
voice_ref: LS.D.002
projection: read-only
channel_constraints:        # видимые slot-метаданные (уточнение Кими): что задаёт канал
  - "без markdown-заголовков (# не рендерится → *жирный*)"
  - "таблицы не рендерятся → списки"
  - "до 80 слов в стандартном ответе"
  - "команды (/start) plain text, не в коде"
---

# [LS.FORM.010] Регистр Telegram

> Ответ агента в Telegram (бот). Композиция: разговорный base (DP.SC.050, в нём уже есть секция «Telegram (бот)») для роли новичка. Канально-условные ограничения вынесены в `channel_constraints` slot-метаданных (видимы автору). Закрывает fallback диспетчера на событие bot-telegram.
