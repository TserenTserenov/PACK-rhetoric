# CHANGELOG

## [v0.3.0] — 2026-05-19

### Добавлено
- `scripts/rhetoric-miner.py` — M-RM экстрактор (DP.SC.149): paginated club API, фильтр engagement, headless claude-haiku, checkpoint
- `scripts/rhetoric-miner.sh` — bash обёртка с lock-файлом, git pull/commit/push
- `scripts/com.iwe.rhetoric-miner.plist` — launchd plist (02:00 МСК)
- `scripts/rhetoric-miner.service` + `.timer` — systemd units для tsekh-1
- `scripts/prompts/extract-illustration.md` — промпт шаблон M-RM
- ~30 карточек из smoke test (2026-05-17 клуб, 11 постов прошли фильтр)
- `pack/rhetoric/07-map/RHE.MAP.001.md` — навигационная карта Pack

### Изменено
- `README.md` — финальная документация (v0.3.0)
- `ROADMAP.md` — Ф5, Ф6 помечены done; версия v0.3.0

---

## [v0.2.0] — 2026-05-19

### Добавлено
- `pack/rhetoric/05-formalizations/RHE.FORM.002-trope-validation.md` — критерии валидации по типу тропа
- `pack/rhetoric/01-domain-contract/01B-distinctions.md` — 7 ключевых различений
- 19 карточек из DS-principles-curriculum (Ф3.5 extraction)

---

## [v0.1.1] — 2026-05-19

### Добавлено
- `pack/rhetoric/06-sota/RHE.SOTA.001-modern-rhetoric.md` — SOTA риторика + Structure-Mapping Theory

---

## [v0.1.0] — 2026-05-19

### Добавлено
- Онтология: RHE.D.001 (Illustration), RHE.D.002 (TropeTaxonomy)
- RHE.FORM.001 — схема карточки (14 полей)
- RHE.SC.001 — Service Clause Pack'а
- 3 seed-карточки: bolide-pilot-machine, asepsis-surgeon, semmelweis-effect
- `templates/illustration-card.md`
- `REPO-TYPE.md`, `ROADMAP.md`, `README.md`
