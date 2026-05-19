# Дорожная карта PACK-rhetoric

> Источник: WP-340 (DS-my-strategy/inbox/WP-340/WP-340.md)

## Текущий статус: v0.2.0 draft (19 мая 2026)

Что уже есть: онтология, таксономия тропов, SC, шаблон карточки, 3 seed-иллюстрации,
SOTA современной риторики (RHE.SOTA.001).

## Фазы

### Ф1 — Scope & Positioning (✅ done)

- [x] Граница домена — `01-domain-contract/01A-bounded-context.md`
- [x] Pack manifest — `00-pack-manifest.md`
- [x] Различения Pack (01B) — 7 различений: иллюстрация≠понятие, структурный≠поверхностный, effect:explain≠persuade≠scaffold
- [x] Связи с потребителями формализованы

### Ф2 — Онтология & Taxonomy (✅ draft)

- [x] RHE.D.001 Illustration — схема карточки
- [x] RHE.D.002 Trope Taxonomy — 5 типов
- [ ] RHE.D.003 CorpusSource — описание источников (клуб, руководства, книги)

### Ф3 — Formalizations (✅ done)

- [x] RHE.FORM.001 — формат карточки иллюстрации
- [x] RHE.FORM.002 — типы тропов с формальными критериями отнесения (обязательные поля, антипаттерны FAIL, процедура валидации)
- [x] Тест трёх эталонных иллюстраций через формат — без натяжки

### Ф3.5 — Extraction из существующих руководств (✅ done, 19-05-2026)

- [x] Grep паттернов в DS-principles-curriculum: SS.F1.01-08 (ячейки), ZP.1-6, book parts 1-4
- [x] Grep паттернов в программах (personal-development-v3, worker-development)
- [x] Заполнить карточки по шаблону: обязательно `structural_core` + `breaks_when`
- [x] Commit: 19 карточек (analogy×4, metaphor×7, example×6, counter_example×2) — RHE.ILL.004-022

### Ф4 — Расширение R15 Экстрактора (✅ IntegrationGate PASS, 2026-05-19)

IntegrationGate PASS:
- [x] DP.SC.149 в PACK-digital-platform — corpus-mining SC, 3 сценария, partial-first, PII-gate
- [x] Сценарии SC-A (ночной batch клуба), SC-B (on-demand), SC-C (embedding-resonance)
- [x] DP.AISYS.013 update: метод М-RM (§4.9), trigger #11, related.sc/methods
- [ ] Адаптеры: клуб API/scraper, guide files reader, нормализатор → Ф5

### Ф5 — Night Mining Scheduler (✅ done 2026-05-19)

- [x] Скрипт mining клуба: GET /posts 2026→назад, rate-limited
- [x] Фильтр: ≥5 reaction или ≥3 комментария (score field)
- [x] Launchd plist (Mac) + systemd unit (tsekh-1), 02:00 МСК
- [x] Test-run: ~30 карточек из 11 постов (2026-05-17)

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
| v0.1.1 | 2026-05-19 | RHE.SOTA.001 современная риторика + ИИ-эпоха |
| v0.2.0 | 2026-05-19 | RHE.FORM.002 критерии валидации + 01B различения + Ф3.5: 19 карточек из DS-principles-curriculum |
| v0.3.0 | 2026-05-19 | Ф5: scripts/ (rhetoric-miner.py + sh + plist + systemd) + ~30 карточек smoke test (RHE.ILL.023-070) |
