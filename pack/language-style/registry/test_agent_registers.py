#!/usr/bin/env python3
# see DP.SC.173, DP.SC.174, LS.SOTA.002 §4. Тесты агент-агентных регистров Ф8 (WP-412).
"""Проверяет: 5 агент-событий резолвятся в свои слоты (не fallback), материализуют агент-агентную
базу (LS.D.003), жанровые секции приходят для handoff/контракта (с разным смыслом по жанру),
человеческий author-слой НЕ протекает на агент-слоты (оговорка Кими). Каждый тест — наблюдаемый
результат (P1). Компилятор расширен жанровым data-наложением (находка Ф8, см. report §6)."""

import unittest

import compiler
import dispatcher

AGENT_EVENTS = ["peer-turn", "handoff", "task-contract", "commit-msg", "pr-desc"]
HUMAN_AUTHOR_REFS = {"content:L1.communication", "content:L1.code-style"}


class TestAgentSlotsResolve(unittest.TestCase):
    def test_all_agent_events_hit_real_slots(self):
        for ev in AGENT_EVENTS:
            res = dispatcher.dispatch(ev, use_cache=False)
            self.assertFalse(res.fallback_used, f"{ev} ушёл в fallback — нет слота")

    def test_agent_fragment_materializes_base(self):
        res = dispatcher.dispatch("handoff", use_cache=False)
        self.assertIn("content:LS.agent-agent", [r["source_id"] for r in res.source_refs])
        self.assertIn("Грайс", res.fragment)  # база несёт максимы Грайса

    def test_peer_and_executor_different_keys(self):
        peer = dispatcher.context_key_for("peer-turn")
        ex = dispatcher.context_key_for("commit-msg")
        self.assertEqual(peer["reader_role"], "peer")
        self.assertEqual(ex["reader_role"], "executor")


class TestGenreSections(unittest.TestCase):
    def test_handoff_has_genre_sections(self):
        res = dispatcher.dispatch("handoff", use_cache=False)
        self.assertIn("genre:handoff", res.applied_layers)
        for label in ("FACT", "TODO", "BLOCKER", "ACCEPTED"):
            self.assertIn(label, res.fragment)
        # полная фраза, не обрывок: ловит урезание desc на запятой (flow-YAML trap)
        self.assertIn("не план", res.fragment)
        self.assertIn("зафиксированные договорённости", res.fragment)

    def test_task_contract_genre_differs_from_handoff(self):
        handoff = dispatcher.dispatch("handoff", use_cache=False).fragment
        contract = dispatcher.dispatch("task-contract", use_cache=False).fragment
        # одни ярлыки, разный смысл по жанру (Кими, ход 3)
        self.assertIn("текущее состояние", handoff)        # handoff FACT
        self.assertIn("входные данные", contract)          # task-contract FACT
        self.assertNotIn("входные данные", handoff)

    def test_commit_has_light_genre_overlay(self):
        # лёгкий жанр коммита добавлен peer-сессией 2026-06-12-02 (был отложен в Ф8).
        res = dispatcher.dispatch("commit-msg", use_cache=False)
        self.assertIn("genre:commit", res.applied_layers)


class TestNoAuthorLeak(unittest.TestCase):
    """Оговорка Кими: человеческий author-слой (conversational/code) не должен протечь на агент-слоты."""

    def test_agent_slots_have_no_human_author(self):
        for ev in AGENT_EVENTS:
            refs = {r["source_id"] for r in dispatcher.dispatch(ev, use_cache=False).source_refs}
            leaked = refs & HUMAN_AUTHOR_REFS
            self.assertEqual(leaked, set(), f"{ev}: протёк человеческий author {leaked}")

    def test_no_author_layer_on_agent(self):
        res = dispatcher.dispatch("peer-turn", use_cache=False)
        self.assertFalse(any(layer.startswith("author:") for layer in res.applied_layers))


class TestDeterminismAgent(unittest.TestCase):
    def test_agent_register_deterministic(self):
        a = dispatcher.dispatch("task-contract", use_cache=False)
        b = dispatcher.dispatch("task-contract", use_cache=False)
        self.assertEqual(a.fragment, b.fragment)
        self.assertEqual(a.key_hash, b.key_hash)


if __name__ == "__main__":
    unittest.main(verbosity=2)
