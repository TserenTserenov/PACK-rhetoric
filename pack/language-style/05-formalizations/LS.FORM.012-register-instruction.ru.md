---
id: LS.FORM.012
type: register
name: Регистр пошаговой инструкции (от имени автора)
name_en: Step-by-step instruction register
status: draft
created: 2026-11-11
valid_from: 2026-11-11
wp: WP-619
lang: ru
role: canon
context_key:
  reader_meta_class: human
  reader_role: author
  channel: instruction
  domain: "*"
content_source: DP.SC.050
voice_ref: LS.D.002
projection: read-only
---

# [LS.FORM.012] Регистр пошаговой инструкции

> Инструкция от имени автора для человека, который делает это впервые и не видит экрана автора (тестировщик, новичок, участник). Композиция: разговорный base (DP.SC.050, в нём раздел «Пошаговая инструкция для человека») + жанр инструкции (`overlays/genre/instruction.yaml`, источники — LS.SOTA.003) + голос автора (L1.voice) + авторская адаптация 2.3 (L1.instruction-style). Ключ `reader_role: author` — как у поста: голос автора, а не регистр «агент → пилот».
