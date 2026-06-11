#!/usr/bin/env python3
# see DP.SC.173. Тесты компилятора реестра (WP-412 Ф5).
"""Проверяет инварианты DP.SC.173: детерминизм, режим отказа, каскад, нормализация хэша,
свежесть манифеста. Каждый тест утверждает наблюдаемый результат (P1), не «не упало»."""

import unittest

import compiler as c

PILOT_KEY = {"reader_meta_class": "human", "reader_role": "pilot", "channel": "ide", "domain": "*"}
DEV_KEY = {"reader_meta_class": "human", "reader_role": "developer", "channel": "code", "domain": "*"}


class TestDeterminism(unittest.TestCase):
    def test_same_key_same_fragment(self):
        a = c.compile_key(PILOT_KEY, use_cache=False)
        b = c.compile_key(PILOT_KEY, use_cache=False)
        self.assertEqual(a.fragment, b.fragment)
        self.assertEqual(a.key_hash, b.key_hash)
        self.assertGreater(len(a.fragment), 0)

    def test_platform_hash_overlay_order_independent(self):
        slots = c.load_slots(c.load_index())
        pilot = next(s for s in slots if s.slot_id == "LS.FORM.001")
        h1 = c.platform_layer_hash(pilot, ["domain:personal-development", "market:ru"])
        h2 = c.platform_layer_hash(pilot, ["market:ru", "domain:personal-development"])
        self.assertEqual(h1, h2)  # сортировка наложений → один хэш


class TestFallback(unittest.TestCase):
    def test_unknown_key_uses_base(self):
        alien = {"reader_meta_class": "human", "reader_role": "alien", "channel": "smoke", "domain": "*"}
        res = c.compile_key(alien, use_cache=False)
        self.assertTrue(res.fallback_used)
        self.assertIn("slot:LS.FORM.000", [r["source_id"] for r in res.source_refs])

    def test_known_key_not_fallback(self):
        res = c.compile_key(PILOT_KEY, use_cache=False)
        self.assertFalse(res.fallback_used)
        self.assertIn("content:DP.SC.050", [r["source_id"] for r in res.source_refs])


class TestCascadeDifference(unittest.TestCase):
    """Каскад на разнице двух регистров (Т5): доменное наложение домешивается к разговорному,
    но не к инженерному коду (applies_to не пускает роль developer / канал code)."""

    def test_domain_overlay_applies_to_pilot(self):
        key = {**PILOT_KEY, "domain": "personal-development"}
        res = c.compile_key(key, use_cache=False)
        self.assertIn("domain:personal-development", res.applied_layers)
        self.assertIn("Домен: personal-development", res.fragment)

    def test_domain_overlay_skips_developer(self):
        key = {**DEV_KEY, "domain": "personal-development"}
        res = c.compile_key(key, use_cache=False)
        self.assertNotIn("domain:personal-development", res.applied_layers)

    def test_market_overlay_applies(self):
        key = {**PILOT_KEY, "market": "ru"}
        res = c.compile_key(key, use_cache=False)
        self.assertIn("market:ru", res.applied_layers)
        self.assertIn("Рынок: ru", res.fragment)

    def test_two_registers_have_different_owners(self):
        pilot = c.compile_key(PILOT_KEY, use_cache=False)
        dev = c.compile_key(DEV_KEY, use_cache=False)
        self.assertNotEqual(pilot.fragment, dev.fragment)
        self.assertIn("content:DP.SC.050", [r["source_id"] for r in pilot.source_refs])
        self.assertIn("content:DP.SC.172", [r["source_id"] for r in dev.source_refs])


class TestResolveSlot(unittest.TestCase):
    """Tie-break: два слота равной специфичности → выбор по slot_id, не по порядку индекса."""

    def _slot(self, sid):
        ck = {"reader_meta_class": "human", "reader_role": "pilot", "channel": "ide", "domain": "*"}
        return c.Slot(slot_id=sid, path=None, context_key=ck,
                      content_source="inline", fallback_text="", slot_sha="x")

    def test_tie_break_index_order_independent(self):
        key = {"reader_meta_class": "human", "reader_role": "pilot", "channel": "ide", "domain": "*"}
        fb, a, b = self._slot("LS.FORM.000"), self._slot("LS.FORM.AAA"), self._slot("LS.FORM.BBB")
        r1, _ = c.resolve_slot([fb, a, b], "LS.FORM.000", key)
        r2, _ = c.resolve_slot([fb, b, a], "LS.FORM.000", key)
        self.assertEqual(r1.slot_id, r2.slot_id)   # не зависит от порядка
        self.assertEqual(r1.slot_id, "LS.FORM.AAA")  # лексикографически меньший


class TestMaterialize(unittest.TestCase):
    def test_developer_fragment_strips_inject_markers(self):
        res = c.compile_key(DEV_KEY, use_cache=False)
        self.assertNotIn("INJECT-START", res.fragment)
        self.assertNotIn("INJECT-END", res.fragment)
        self.assertGreater(len(res.fragment), 50)  # регион между маркерами непустой


class TestCache(unittest.TestCase):
    def test_cache_records_compiler_version(self):
        import json
        res = c.compile_key(PILOT_KEY, use_cache=True)
        data = json.loads((c.COMPILED_DIR / f"{res.key_hash}.json").read_text("utf-8"))
        self.assertEqual(data["compiler_version"], c.COMPILER_VERSION)


class TestManifestFreshness(unittest.TestCase):
    def test_lock_matches_live_sources(self):
        # Генерируем lock и сразу проверяем — должен быть свеж.
        c.write_lock()
        fresh, changes = c.verify_lock()
        self.assertTrue(fresh, f"lock устарел сразу после генерации: {changes}")

    def test_manifest_hash_stable(self):
        idx, cs = c.load_index(), c.load_content_sources()
        self.assertEqual(c.compute_manifest(idx, cs)["manifest_hash"],
                         c.compute_manifest(idx, cs)["manifest_hash"])

    def test_manifest_spans_both_repos(self):
        m = c.compute_manifest(c.load_index(), c.load_content_sources())
        ids = {s["id"] for s in m["sources"]}
        self.assertIn("content:DP.SC.050", ids)   # из PACK-digital-platform
        self.assertTrue(any(i.startswith("slot:") for i in ids))  # из PACK-rhetoric


if __name__ == "__main__":
    unittest.main(verbosity=2)
