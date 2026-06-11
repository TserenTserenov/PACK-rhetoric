#!/usr/bin/env python3
# see WP-392, DP.SC.173. Тесты-инварианты границы и метрик Ф10 (WP-412).
"""Граница платформа/интерфейс (контракт 01C) + метрики. Каждый тест — наблюдаемый результат (P1).
Инварианты: один ключ→один фрагмент; разные каналы при одном читателе→фрагменты отличаются только
рынком; диспетчер тонкий (нет стилевой логики); покрытие защищено от пустых слотов."""

import re
import unittest
from pathlib import Path

import compiler
import dispatcher
import style_metrics as sm

DISPATCHER_SRC = (Path(__file__).resolve().parent / "dispatcher.py").read_text("utf-8")


class TestBoundaryInvariant(unittest.TestCase):
    def test_one_key_one_fragment(self):
        # детерминизм границы: один полный ключ → байт-в-байт один фрагмент
        key = dispatcher.context_key_for("userpromptsubmit-ide")
        a = compiler.compile_key(key, use_cache=False).fragment
        b = compiler.compile_key(key, use_cache=False).fragment
        self.assertEqual(a, b)
        self.assertGreater(len(a), 0)

    def test_channel_does_not_leak_into_fragment(self):
        # обратный инвариант: pilot/ide и pilot/browser (без рынка) → идентичные фрагменты.
        # Канал выбирает слот, но в сам фрагмент не течёт (WP-392).
        ide = dispatcher.dispatch("userpromptsubmit-ide", use_cache=False).fragment
        browser = dispatcher.dispatch("browser", use_cache=False).fragment
        self.assertEqual(ide, browser)


class TestDispatcherThin(unittest.TestCase):
    """Структурный тест границы: диспетчер не содержит стилевой логики (контракт 01C)."""

    def test_no_style_logic_in_dispatcher(self):
        forbidden = ["render_overlay", "materialize_content", "materialize_base", "select_overlays"]
        leaked = [name for name in forbidden if name in DISPATCHER_SRC]
        self.assertEqual(leaked, [], f"стилевая логика протекла в диспетчер: {leaked}")

    def test_no_file_ops_in_dispatcher(self):
        # контракт 01C: диспетчер не читает слот-файлы/реестр. Никаких файловых операций.
        for op in ["read_text", "open(", "Path(", "load_index", "load_slots"]:
            self.assertNotIn(op, DISPATCHER_SRC, f"диспетчер делает файловую операцию: {op}")

    def test_dispatcher_calls_only_compile_key(self):
        # единственный вызов компилятора — compile_key (плюс context_key_for локально)
        compiler_calls = set(re.findall(r"compiler\.(\w+)", DISPATCHER_SRC))
        self.assertEqual(compiler_calls, {"compile_key"})


class TestCoverage(unittest.TestCase):
    def test_all_events_covered_now(self):
        # сейчас все 9 событий резолвятся в непустые регистры
        r = sm.coverage_report()
        self.assertEqual(r["coverage"], 1.0, f"не покрыто: {r['uncovered']}")
        self.assertEqual(r["unmapped"], [])

    def test_empty_slot_not_counted_covered(self):
        # защита от ложного 100%: пустой/короткий фрагмент → не покрытие
        self.assertFalse(sm.is_covered("", False))
        self.assertFalse(sm.is_covered("коротко", False))           # < 20 символов
        self.assertFalse(sm.is_covered("х" * 100, True))            # fallback → не покрытие
        self.assertTrue(sm.is_covered("х" * 100, False))            # длинный непустой → покрытие


class TestCompliance(unittest.TestCase):
    def test_mechanical_catches_machine_marker(self):
        v = sm.mechanical_compliance_check("Проверка прошла, exit 0, всё хорошо.")
        self.assertTrue(any(x["match"] == "exit 0" for x in v))

    def test_mechanical_clean_text(self):
        self.assertEqual(sm.mechanical_compliance_check("Развернули на сервер, всё хорошо."), [])

    def test_semantic_is_stub_with_interface(self):
        r = sm.semantic_compliance_check("любой текст")
        self.assertEqual(r["status"], "not_implemented")
        self.assertIn("interface", r)


if __name__ == "__main__":
    unittest.main(verbosity=2)
