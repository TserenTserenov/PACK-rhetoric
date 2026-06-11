#!/usr/bin/env python3
# see DP.SC.173, DP.SC.174. Паритет-тесты Ф6 (WP-412).
"""Гарантия миграции: фрагмент диспетчера == то, что впрыскивает живой хук (нормализованно).
Это guard ПЕРЕД подменой хуков (S-33 шаг б). Два слоя проверки:
  (а) containment — фрагмент содержит тело L0 И тело L1 (ничего не потеряли по объёму);
  (б) coverage по авто-якорям — каждый ID правила из источника (P0-P5 / A1-A11) есть во фрагменте."""

import re
import unittest

import compiler
import dispatcher


def materialized(source_id: str) -> str:
    """То же тело владельца, что материализует компилятор (strip frontmatter + регион инъекции)."""
    path = compiler.load_content_sources()[source_id]
    _, body = compiler.split_frontmatter(path.read_text("utf-8"))
    return compiler.extract_inject_region(body)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def rule_ids(text: str, prefix: str) -> set:
    return set(re.findall(rf"\b{prefix}\d+\b", text))


class TestParityConversational(unittest.TestCase):
    """Разговорный регистр (pilot/ide): фрагмент == L0 (DP.SC.050) + L1 автор."""

    def setUp(self):
        self.frag = dispatcher.dispatch("userpromptsubmit-ide", use_cache=False).fragment

    def test_contains_L0_body(self):
        self.assertIn(norm(materialized("DP.SC.050")), norm(self.frag))

    def test_contains_L1_author_body(self):
        self.assertIn(norm(materialized("L1.communication")), norm(self.frag))

    def test_all_author_A_rules_present(self):
        anchors = rule_ids(materialized("L1.communication"), "A")
        self.assertGreater(len(anchors), 0, "источник L1 должен содержать A-правила")
        missing = anchors - rule_ids(self.frag, "A")
        self.assertEqual(missing, set(), f"потеряны правила: {missing}")

    def test_author_layer_in_refs(self):
        refs = dispatcher.dispatch("userpromptsubmit-ide", use_cache=False).source_refs
        self.assertIn("content:L1.communication", [r["source_id"] for r in refs])


class TestParityCode(unittest.TestCase):
    """Инженерный регистр (developer/code): фрагмент == L0-регион (DP.SC.172) + L1 автор."""

    def setUp(self):
        self.frag = dispatcher.dispatch("pretooluse-edit", use_cache=False).fragment

    def test_contains_L0_inject_region(self):
        self.assertIn(norm(materialized("DP.SC.172")), norm(self.frag))

    def test_contains_L1_author_body(self):
        self.assertIn(norm(materialized("L1.code-style")), norm(self.frag))

    def test_all_P_rules_present(self):
        anchors = rule_ids(materialized("DP.SC.172"), "P")
        self.assertGreater(len(anchors), 0, "источник L0 должен содержать P-правила")
        missing = anchors - rule_ids(self.frag, "P")
        self.assertEqual(missing, set(), f"потеряны правила: {missing}")

    def test_no_inject_markers_leak(self):
        self.assertNotIn("INJECT-START", self.frag)
        self.assertNotIn("INJECT-END", self.frag)


class TestDispatcher(unittest.TestCase):
    def test_event_to_key_mapping(self):
        key = dispatcher.context_key_for("pretooluse-edit")
        self.assertEqual(key["reader_role"], "developer")
        self.assertEqual(key["channel"], "code")

    def test_unknown_event_raises(self):
        with self.assertRaises(KeyError):
            dispatcher.context_key_for("no-such-event")

    def test_market_default_from_env(self):
        import os
        os.environ["IWE_STYLE_MARKET"] = "ru"
        try:
            self.assertEqual(dispatcher.context_key_for("bot-telegram")["market"], "ru")
        finally:
            del os.environ["IWE_STYLE_MARKET"]


class TestAuthorOverlayCascade(unittest.TestCase):
    def test_author_optional_skipped_for_unmatched_role(self):
        # alien-роль не матчит ни один author-overlay → author не применяется, ошибки нет.
        res = compiler.compile_key(
            {"reader_meta_class": "human", "reader_role": "alien", "channel": "ide", "domain": "*"},
            use_cache=False)
        self.assertFalse(any(layer.startswith("author:") for layer in res.applied_layers))

    def test_author_applied_for_developer(self):
        res = dispatcher.dispatch("pretooluse-edit", use_cache=False)
        self.assertIn("author:L1.code-style", res.applied_layers)

    def test_cascade_order_author_after_base(self):
        res = dispatcher.dispatch("userpromptsubmit-ide", use_cache=False)
        self.assertEqual(res.applied_layers[0], "base")
        self.assertEqual(res.applied_layers[-1], "author:L1.communication")


if __name__ == "__main__":
    unittest.main(verbosity=2)
