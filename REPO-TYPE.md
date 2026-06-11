# Тип репозитория

**Тип:** Pack (domain knowledge)

> **Переименование репо `PACK-rhetoric → PACK-language-style` отложено на WP-412 Ф4б** (переезд в IWE-орг, co-deploy с правкой launchd-плиста добытчика иллюстраций). До переезда репо физически называется `PACK-rhetoric`, но primary-пак — `language-style`.

## Два пака в репо

| Pack | Pack ID | Роль | Путь |
|------|---------|------|------|
| **Языковые стили** | `LS` | primary (дисциплина управления стилями) | `pack/language-style/` |
| **Риторические приёмы** | `RHE` | contained (раздел дисциплины: тропы, фигуры, иллюстрации) | `pack/rhetoric/` |

**Fallback chain:** PACK-language-style (LS) → SPF → FPF; риторика (RHE) → language-style → SPF → FPF.

- `language-style` (LS) — source-of-truth для дисциплины языковых стилей IWE (оси, голос/тон, регистры, жанры, наложения). «База стилей» в топологии WP-415 (дом `iwe-platform`).
- `rhetoric` (RHE) — source-of-truth для риторических приёмов. DS-репозитории используют карточки из `illustrations/` как readonly-ресурс. Нумерация RHE.* стабильна, не мигрирует.

## Changelog структуры

- **2026-06-11 (WP-412 Ф4а, peer-сессия 2026-06-11-28):** добавлен пак `language-style` (LS) как primary. Черновик теории регистра/стиля перенесён `pack/rhetoric/06-sota/_draft-register-style-theory.md → pack/language-style/06-sota/LS.SOTA.002-register-style-theory.ru.md` (минт id LS.SOTA.002). Пак `rhetoric` (RHE) нетронут. Физический rename репо — pending Ф4б.
