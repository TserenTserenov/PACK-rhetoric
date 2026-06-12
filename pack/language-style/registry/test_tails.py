#!/usr/bin/env python3
# see DP.SC.173. Тесты хвостов WP-412 (peer-сессия 2026-06-12-02).
"""Проверяет: (1) extra-источники (presets, genre-template) в манифесте с префиксом extra:;
(2) канальный gate ЦА-наложения — не применяется в ide, применяется в post; ru.yaml без
applies_to работает как раньше; (3) жанры commit/pr выбираются для своих регистров."""

import unittest

import compiler

KEY_POST = {"reader_meta_class": "human", "reader_role": "author", "channel": "post", "domain": "*"}
KEY_IDE = {"reader_meta_class": "human", "reader_role": "pilot", "channel": "ide", "domain": "*"}


def overlay_names(key: dict) -> set:
    res = compiler.compile_key(key, use_cache=False)
    return {r["source_id"] for r in res.source_refs}


class TestExtraSourcesInManifest(unittest.TestCase):
    def test_extra_prefix_pattern(self):
        index = compiler.load_index()
        content_sources = compiler.load_content_sources()
        ids = [sid for sid, _ in compiler.all_source_paths(index, content_sources)]
        extras = [sid for sid in ids if sid.startswith("extra:")]
        self.assertIn("extra:presets", extras)
        self.assertEqual(len([e for e in extras if "genre-template" in e]), 4)
        # все id манифеста несут класс источника (namespace-инвариант)
        for sid in ids:
            self.assertRegex(sid, r"^(slot|content|overlay|extra):")

    def test_extra_files_exist_and_hashed(self):
        index = compiler.load_index()
        manifest = compiler.compute_manifest(index, compiler.load_content_sources())
        extras = [s for s in manifest["sources"] if s["id"].startswith("extra:")]
        self.assertEqual(len(extras), 5)
        for s in extras:
            self.assertNotEqual(s["sha256"], "MISSING", f"{s['id']} не найден на диске")


class TestMarketChannelGate(unittest.TestCase):
    def test_audience_applies_on_post(self):
        key = {**KEY_POST, "market": "systems-thinkers"}
        self.assertTrue(any("market:systems-thinkers" in sid for sid in overlay_names(key)),
                        "ЦА-наложение не применилось на канале post")

    def test_audience_gated_off_ide(self):
        key = {**KEY_IDE, "market": "systems-thinkers"}
        self.assertFalse(any("market:systems-thinkers" in sid for sid in overlay_names(key)),
                         "ЦА-наложение протекло в ide-чат")

    def test_ru_market_unaffected(self):
        # ru.yaml без applies_to — применяется на любом канале (обратная совместимость)
        key = {**KEY_IDE, "market": "ru"}
        self.assertTrue(any("market:ru" in sid for sid in overlay_names(key)),
                        "ru-наложение перестало применяться в ide — сломана совместимость")


class TestLightGenres(unittest.TestCase):
    def test_commit_genre_selected(self):
        key = {"reader_meta_class": "agent", "reader_role": "executor", "channel": "commit", "domain": "*"}
        res = compiler.compile_key(key, use_cache=False)
        self.assertIn("overlay:genre:commit", {r["source_id"] for r in res.source_refs})
        self.assertIn("SUBJECT", res.fragment)

    def test_pr_genre_selected(self):
        key = {"reader_meta_class": "agent", "reader_role": "executor", "channel": "pr", "domain": "*"}
        res = compiler.compile_key(key, use_cache=False)
        self.assertIn("overlay:genre:pr", {r["source_id"] for r in res.source_refs})
        self.assertIn("RISK", res.fragment)

    def test_genres_do_not_leak_to_handoff(self):
        key = {"reader_meta_class": "agent", "reader_role": "executor", "channel": "handoff", "domain": "*"}
        refs = {r["source_id"] for r in compiler.compile_key(key, use_cache=False).source_refs}
        self.assertNotIn("overlay:genre:commit", refs)
        self.assertNotIn("overlay:genre:pr", refs)


if __name__ == "__main__":
    unittest.main()
