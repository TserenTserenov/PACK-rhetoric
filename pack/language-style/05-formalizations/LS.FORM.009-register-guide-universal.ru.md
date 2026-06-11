---
id: LS.FORM.009
type: register
name: Регистр универсального руководства (ученик)
name_en: Universal guide register
status: draft
created: 2026-06-11
valid_from: 2026-06-11
wp: WP-412
lang: ru
role: canon
context_key:
  reader_meta_class: human
  reader_role: student
  channel: guide
  domain: "*"
content_source: LS.academic-guide
voice_ref: LS.D.002
projection: read-only
genre_template: genre-template/ru/guide.md
personal_hook: WP-300   # персональная подстройка тоном — слой WP-300, здесь не авторится
---

# [LS.FORM.009] Регистр универсального руководства

> Универсальное руководство (метод для всех). Композиция: академический base (LS.D.004) + жанр руководства (скелет `genre-template/ru/guide.md`). **Персональная подстройка** под ступень/bottleneck пилота — отдельный слой из системы персональных руководств (WP-300), здесь НЕ авторится (universal ≠ personal). Hook оставлен для подключения WP-300.
