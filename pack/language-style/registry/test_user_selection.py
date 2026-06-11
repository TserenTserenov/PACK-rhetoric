#!/usr/bin/env python3
# see DP.SC.175. Тесты-контракты выбора стиля пользователем Ф7 (WP-412).
"""Жёсткие контракты (Кими, ход 3): guardrail (тон только для человеко-регистров),
merge-порядок (пресет→дельты additive→кламп), канонизация note (round-trip). Каждый — наблюдаемый
результат (P1). guardrail — safety-инвариант: один if в компиляторе защищает агент-контракты."""

import unittest

import compiler
import dispatcher
import style_selector as sel


class TestGuardrail(unittest.TestCase):
    """Safety-инвариант: user_override применяется ТОЛЬКО к reader_meta_class=human."""

    UO = {"note": "Тон по выбору пользователя: формальность +1, юмор +0, уважительность +0, энтузиазм +0."}

    def test_agent_register_ignores_override(self):
        # peer-turn = agent-регистр (машинный контракт). Тон пользователя НЕ применяется.
        key = dispatcher.context_key_for("peer-turn")
        res = compiler.compile_key(key, user_override=self.UO, use_cache=False)
        self.assertNotIn("user", res.applied_layers)
        self.assertNotIn("Тон по выбору", res.fragment)

    def test_commit_register_ignores_override(self):
        key = dispatcher.context_key_for("commit-msg")
        res = compiler.compile_key(key, user_override=self.UO, use_cache=False)
        self.assertNotIn("user", res.applied_layers)

    def test_human_register_applies_override(self):
        key = dispatcher.context_key_for("userpromptsubmit-ide")
        res = compiler.compile_key(key, user_override=self.UO, use_cache=False)
        self.assertIn("user", res.applied_layers)
        self.assertIn("Тон по выбору", res.fragment)

    def test_human_miss_still_gets_tone(self):
        # человек с неизвестной ролью/каналом → промах → fallback, но тон ПРИМЕНЯЕТСЯ (гейт по ключу)
        key = {"reader_meta_class": "human", "reader_role": "alien", "channel": "void", "domain": "*"}
        res = compiler.compile_key(key, user_override=self.UO, use_cache=False)
        self.assertTrue(res.fallback_used)
        self.assertIn("user", res.applied_layers)

    def test_agent_miss_no_tone(self):
        # агент с неизвестной ролью → промах → fallback, тон НЕ применяется (safety)
        key = {"reader_meta_class": "agent", "reader_role": "alien", "channel": "void", "domain": "*"}
        res = compiler.compile_key(key, user_override=self.UO, use_cache=False)
        self.assertNotIn("user", res.applied_layers)


class TestMerge(unittest.TestCase):
    def test_preset_plus_delta_additive(self):
        # пресет formality=+1 + дельта formality=-1 → 0 (фиксированный порядок merge)
        self.assertEqual(sel.merge_axes({"formality": 1}, {"formality": -1})["formality"], 0)

    def test_delta_clamped(self):
        self.assertEqual(sel.merge_axes({"formality": 2}, {"formality": 5})["formality"], 2)
        self.assertEqual(sel.merge_axes({"humor": -2}, {"humor": -5})["humor"], -2)

    def test_unknown_axis_ignored(self):
        vec = sel.merge_axes({}, {"loudness": 3})  # не из 4 осей
        self.assertNotIn("loudness", vec)

    def test_parse_clamps_out_of_range(self):
        vec = sel.parse_note("Тон: формальность +9, юмор -9.")  # вне [-2,+2]
        self.assertEqual(vec["formality"], 2)
        self.assertEqual(vec["humor"], -2)

    def test_parse_deltas_garbage_clear_error(self):
        with self.assertRaises(ValueError):
            sel._parse_deltas(["formality=abc"])


class TestCanonicalization(unittest.TestCase):
    def test_round_trip(self):
        vec = {"formality": 1, "humor": -1, "respectfulness": 2, "enthusiasm": 0}
        self.assertEqual(sel.parse_note(sel.canonical_note(vec)), vec)

    def test_note_order_stable(self):
        # одни входы → один note (детерминизм хэша)
        v1 = {"formality": 1, "enthusiasm": -1, "humor": 0, "respectfulness": 0}
        v2 = {"respectfulness": 0, "humor": 0, "enthusiasm": -1, "formality": 1}
        self.assertEqual(sel.canonical_note(v1), sel.canonical_note(v2))


class TestSelector(unittest.TestCase):
    def test_presets_load(self):
        self.assertIn("concise-technical", sel.load_presets())

    def test_build_override_from_preset(self):
        ov = sel.build_user_override(preset="warm-mentor", presets=sel.load_presets())
        self.assertIn("уважительность +2", ov["note"])

    def test_style_from_example_stub_enthusiasm(self):
        vec = sel.style_from_example("Привет! Здорово!!")
        self.assertEqual(vec["enthusiasm"], 2)  # 3 '!' → кламп +2


if __name__ == "__main__":
    unittest.main(verbosity=2)
