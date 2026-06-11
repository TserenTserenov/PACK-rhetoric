#!/usr/bin/env python3
# see DP.SC.173, DP.SC.174. Тесты человеко-стилей Ф9 (WP-412).
"""Проверяет: 4 новых человеко-регистра (пост, руководство, Telegram, браузер) резолвятся (не fallback);
Telegram/браузер закрывают fallback диспетчера; руководство материализует академический base;
ЦА = рыночное наложение применяется; genre-template канон ru + плейсхолдер en с pending_sync.
Компилятор не правился (находка консенсуса) — старые 37 тестов остаются зелёными отдельно."""

import unittest
from pathlib import Path

import compiler
import dispatcher

PACK = compiler.PACK_DIR


def frontmatter(rel: str) -> dict:
    front, _ = compiler.split_frontmatter((PACK / rel).read_text("utf-8"))
    return front


class TestHumanRegistersResolve(unittest.TestCase):
    def test_post_register(self):
        res = compiler.compile_key(
            {"reader_meta_class": "human", "reader_role": "author", "channel": "post", "domain": "*"},
            use_cache=False)
        self.assertFalse(res.fallback_used)
        self.assertIn("slot:LS.FORM.008", [r["source_id"] for r in res.source_refs])

    def test_guide_materializes_academic_base(self):
        res = compiler.compile_key(
            {"reader_meta_class": "human", "reader_role": "student", "channel": "guide", "domain": "*"},
            use_cache=False)
        self.assertFalse(res.fallback_used)
        self.assertIn("content:LS.academic-guide", [r["source_id"] for r in res.source_refs])
        self.assertIn("Академический", res.fragment)  # тело LS.D.004


class TestDispatcherChannelsClosed(unittest.TestCase):
    def test_telegram_no_longer_fallback(self):
        res = dispatcher.dispatch("bot-telegram", use_cache=False)
        self.assertFalse(res.fallback_used, "Telegram всё ещё в fallback — слот не подхватился")
        self.assertIn("slot:LS.FORM.010", [r["source_id"] for r in res.source_refs])

    def test_browser_resolves(self):
        res = dispatcher.dispatch("browser", use_cache=False)
        self.assertFalse(res.fallback_used)
        self.assertIn("slot:LS.FORM.011", [r["source_id"] for r in res.source_refs])


class TestPersonalTierNoLeak(unittest.TestCase):
    """WP-415 тир совместности: личный L1 автора не течёт в мультитенантный Telegram-канал,
    но остаётся в личных каналах пилота (ide, browser). Сужение гейта в Ф9."""

    def test_telegram_no_personal_author(self):
        refs = {r["source_id"] for r in dispatcher.dispatch("bot-telegram", use_cache=False).source_refs}
        self.assertNotIn("content:L1.communication", refs, "личный L1 протёк в мультитенантный Telegram")

    def test_pilot_browser_keeps_author(self):
        refs = {r["source_id"] for r in dispatcher.dispatch("browser", use_cache=False).source_refs}
        self.assertIn("content:L1.communication", refs)  # личный канал пилота — автор сохраняется

    def test_pilot_ide_keeps_author(self):
        refs = {r["source_id"] for r in dispatcher.dispatch("userpromptsubmit-ide", use_cache=False).source_refs}
        self.assertIn("content:L1.communication", refs)


class TestAudienceMarketOverlay(unittest.TestCase):
    def test_audience_overlay_applies(self):
        res = compiler.compile_key(
            {"reader_meta_class": "human", "reader_role": "author", "channel": "post",
             "domain": "*", "market": "systems-thinkers"},
            use_cache=False)
        self.assertIn("market:systems-thinkers", res.applied_layers)
        self.assertIn("Рынок: systems-thinkers", res.fragment)


class TestGenreTemplates(unittest.TestCase):
    def test_ru_is_canon(self):
        for genre in ("post", "guide"):
            fm = frontmatter(f"genre-template/ru/{genre}.md")
            self.assertEqual(fm["role"], "canon")
            self.assertEqual(fm["lang"], "ru")
            self.assertEqual(fm["en_status"], "pending")

    def test_en_placeholder_pending_sync(self):
        # защита Кими: EN-плейсхолдер явно помечен, не читается как готовый контент.
        for genre in ("post", "guide"):
            fm = frontmatter(f"genre-template/en/{genre}.md")
            self.assertTrue(fm["pending_sync"])
            self.assertIsNone(fm["synced_at"])

    def test_en_body_warns(self):
        body = (PACK / "genre-template/en/post.md").read_text("utf-8")
        self.assertIn("PENDING SYNC", body)
        self.assertIn("WP-415", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
