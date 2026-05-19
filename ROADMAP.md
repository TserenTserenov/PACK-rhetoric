# Дорожная карта PACK-rhetoric

> Источник: WP-340 (DS-my-strategy/inbox/WP-340/WP-340.md)

## Текущий статус: v0.1.0 draft (19 мая 2026)

Что уже есть: онтология, таксономия тропов, SC, шаблон карточки, 3 seed-иллюстрации.

## Фазы

### Ф1 — Scope & Positioning (✅ в процессе, ~2h)

- [x] Граница домена — `01-domain-contract/01A-bounded-context.md`
- [x] Pack manifest — `00-pack-manifest.md`
- [ ] Различения Pack (01B) — отличие иллюстрации от понятия, от примера в коде
- [ ] Связи с потребителями формализованы

### Ф2 — Онтология & Taxonomy (✅ draft)

- [x] RHE.D.001 Illustration — схема карточки
- [x] RHE.D.002 Trope Taxonomy — 5 типов
- [ ] RHE.D.003 CorpusSource — описание источников (клуб, руководства, книги)

### Ф3 — Formalizations (✅ draft)

- [x] RHE.FORM.001 — формат карточки иллюстрации
- [ ] RHE.FORM.002 — типы тропов с формальными критериями отнесения
- [ ] Тест трёх эталонных иллюстраций через формат — без натяжки

### Ф4 — Расширение R15 Экстрактора (⏳ pending)

IntegrationGate обязателен перед реализацией:
- [ ] DP.SC.NNN в PACK-digital-platform (Service Clause R15 mining mode)
- [ ] Сценарии (SC-A: клуб, SC-B: on-demand, SC-C: embedding-resonance)
- [ ] DP.ROLE.R15 update: добавить метод М-RM, routing target PACK-rhetoric
- [ ] Адаптеры: клуб API/scraper, guide files reader, нормализатор

### Ф5 — Night Mining Scheduler (⏳ pending)

- [ ] Скрипт mining клуба: GET /posts 2026→назад, rate-limited
- [ ] Фильтр: ≥5 reaction или ≥3 комментария
- [ ] Launchd plist (Mac) + systemd unit (tsekh-1), 02:00 МСК
- [ ] Test-run: ≥5 корректных карточек

### Ф6 — Initial Seed (⏳ pending)

- [x] 3 seed-иллюстрации вручную (Болид, Асептика, Земмельвейс)
- [ ] Прогон клуба 2026-01-01 → сегодня (ожидаемо 100-300 постов)
- [ ] top-50 по quality_score
- [ ] Выборочная проверка 10 карточек (≥80% корректность)

### Ф7 — Pack Finalization (⏳ pending)

- [ ] SPF process 09-11: review, README доработать, финальный push
- [ ] CHANGELOG.md
- [ ] v0.2.0 release

## Версии

| Версия | Дата | Что |
|--------|------|-----|
| v0.1.0 | 2026-05-19 | Онтология, SC, шаблон, 3 seed-карточки, пуш в GitHub |
