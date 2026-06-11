#!/usr/bin/env python3
# see DP.SC.175 (выбор стиля пользователем), DP.ROLE.074
"""Селектор стиля пользователя (WP-412 Ф7).

Превращает выбор пользователя (4 тоновые оси / пресет / образец) в user_override для каскада реестра.
Выбирается ТОН (ситуативная настройка, LS.D.002), не голос (ядро агента) и не регистр (ситуация).

Merge-порядок (фиксирован, peer-сессия 2026-06-11-38):
  (1) платформенный пресет = base-вектор → (2) личные дельты пользователя поверх (additive) →
  (3) канонический note. Register-инвариант (тон не для агент-контрактов) держит ГЕЙТ в компиляторе
  (reader_meta_class==human), не здесь — defense-in-depth.

CLI:
  style_selector.py override [--preset NAME] [--delta formality=+1 ...] [--example "текст"]
  style_selector.py active           # собрать override из личного DS-my-strategy/user-style.yaml
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REGISTRY_DIR = Path(__file__).resolve().parent
PACK_DIR = REGISTRY_DIR.parent
PRESETS_PATH = PACK_DIR / "presets.yaml"

# 4 тоновые оси (LS.D.002), фиксированный порядок для канонизации.
AXES = ("formality", "humor", "respectfulness", "enthusiasm")
AXIS_RU = {"formality": "формальность", "humor": "юмор",
           "respectfulness": "уважительность", "enthusiasm": "энтузиазм"}
RU_AXIS = {v: k for k, v in AXIS_RU.items()}
AXIS_MIN, AXIS_MAX = -2, 2


def _find_iwe_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "DS-my-strategy").is_dir():
            return parent
    raise FileNotFoundError(f"Не нашёл корень IWE (с DS-my-strategy) вверх от {start}")


def load_presets() -> dict:
    if not PRESETS_PATH.exists():
        return {}
    return yaml.safe_load(PRESETS_PATH.read_text("utf-8")).get("presets", {})


def load_user_style() -> dict:
    """Личный выбор пользователя: DS-my-strategy/exocortex/user-style.yaml (preset + deltas)."""
    path = _find_iwe_root(REGISTRY_DIR) / "DS-my-strategy/exocortex/user-style.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text("utf-8")) or {}


def merge_axes(base: dict, deltas: dict) -> dict:
    """Пресет (base) → дельты поверх (additive) → кламп в [-2, +2]. Порядок фиксирован."""
    vec = {ax: int((base or {}).get(ax, 0)) for ax in AXES}
    for ax, d in (deltas or {}).items():
        if ax in AXES:
            vec[ax] = max(AXIS_MIN, min(AXIS_MAX, vec[ax] + int(d)))
    return vec


def canonical_note(vec: dict) -> str:
    """Канонический note: оси в фиксированном порядке, числа {:+d}. Стабилен для хэша."""
    parts = [f"{AXIS_RU[ax]} {vec.get(ax, 0):+d}" for ax in AXES]
    return "Тон по выбору пользователя: " + ", ".join(parts) + "."


def parse_note(note: str) -> dict:
    """Round-trip: note → вектор. Гарантирует, что note однозначно парсится обратно."""
    vec = {ax: 0 for ax in AXES}
    for ru, val in re.findall(r"(формальность|юмор|уважительность|энтузиазм)\s+([+-]\d+)", note):
        vec[RU_AXIS[ru]] = max(AXIS_MIN, min(AXIS_MAX, int(val)))  # кламп: робастность к не-canonical входу
    return vec


def style_from_example(text: str) -> dict:
    """СТАБ + интерфейс (LLM-инференс осей из образца — отложен, WP-412 будущее).
    Детерминированная эвристика для MVP: длинные слова → формальнее; '!' → энтузиазм; '))' → юмор."""
    words = text.split()
    avg_len = sum(len(w) for w in words) / len(words) if words else 0
    return {
        "formality": 1 if avg_len >= 7 else (-1 if avg_len <= 4 and words else 0),
        "enthusiasm": max(AXIS_MIN, min(AXIS_MAX, text.count("!"))),  # симметричный кламп
        "humor": 1 if (")" * 2) in text else 0,
        "respectfulness": 0,
    }


def build_user_override(preset: str = None, deltas: dict = None,
                        example: str = None, presets: dict = None) -> dict:
    """Собрать user_override. example > preset для base; дельты всегда поверх."""
    if example is not None:
        base = style_from_example(example)
    elif preset:
        base = (presets if presets is not None else load_presets()).get(preset, {})
    else:
        base = {}
    return {"note": canonical_note(merge_axes(base, deltas))}


def _parse_deltas(items: list) -> dict:
    out = {}
    for it in items or []:
        k, _, v = it.partition("=")
        try:
            out[k.strip()] = int(v)
        except ValueError as e:  # понятная ошибка вместо криптичного int(), P4-граница (внешний ввод)
            raise ValueError(f"--delta {k.strip()}: ожидалось целое, получено '{v}'") from e
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Селектор стиля пользователя (WP-412 Ф7)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("override", help="собрать override из аргументов")
    o.add_argument("--preset", default=None)
    o.add_argument("--delta", action="append", default=[], help="axis=±N (formality=+1)")
    o.add_argument("--example", default=None)
    sub.add_parser("active", help="собрать override из личного user-style.yaml")
    args = ap.parse_args()

    if args.cmd == "override":
        ov = build_user_override(args.preset, _parse_deltas(args.delta), args.example)
    else:
        us = load_user_style()
        ov = build_user_override(us.get("preset"), us.get("deltas"))
    print(ov["note"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
