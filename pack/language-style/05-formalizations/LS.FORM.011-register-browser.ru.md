---
id: LS.FORM.011
type: register
name: Регистр браузера (пилот)
name_en: Browser register
status: draft
created: 2026-06-11
valid_from: 2026-06-11
wp: WP-412
lang: ru
role: canon
context_key:
  reader_meta_class: human
  reader_role: pilot
  channel: browser
  domain: "*"
content_source: DP.SC.050
voice_ref: LS.D.002
projection: read-only
channel_constraints:        # видимые slot-метаданные
  - "до 7 пунктов, помещается в один экран"
  - "если пользователь знает термины — использовать их, иначе бытовые замены"
  - "не упоминать детали подключения (URL, OAuth) без запроса"
---

# [LS.FORM.011] Регистр браузера

> Ответ агента в браузере (claude.ai / ChatGPT) для пилота. Композиция: разговорный base (DP.SC.050, секция «Браузер»). Канально-условные ограничения — в `channel_constraints` slot-метаданных. Закрывает событие диспетчера browser.
