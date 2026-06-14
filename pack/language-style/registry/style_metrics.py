#!/usr/bin/env python3
# see DP.SC.173, WP-392, peer-сессии 2026-06-11-42 (модель) + 2026-06-11-43 (сборка)
"""Метрики дисциплины языковых стилей (WP-412 Ф10). Дисциплина измеряет САМА СЕБЯ → метрики
в платформе, не в интерфейсе (иначе интерфейс «знал» бы стиль, нарушая WP-392).

Двусторонние метрики:
  - покрытие (регистр→ситуация): доля событий диспетчера, покрытых НЕПУСТЫМ регистром.
    Защита от пустых слотов (порог) + флаг намеренного базового регистра + алерт «забыли слот».
  - соответствие (выход→регистр): механический поднабор (машинные маркеры A10) сейчас +
    семантический стаб (A1/A5 через LLM — отложено, интерфейс зафиксирован).

Контракт границы: 01-domain-contract/01C-platform-interface-boundary.md.

CLI:
  style_metrics.py coverage          # отчёт покрытия по событиям диспетчера
  style_metrics.py check "<текст>"   # механические нарушения соответствия в тексте
"""

from __future__ import annotations

import argparse
import os
import re
import sys

import compiler
import dispatcher

# Короче порога → пустой/почти-пустой слот, не считается покрытием (улов Кими: ложный 100%).
MIN_FRAGMENT_LENGTH = 20
# Лог детектора кода (контракт WP-388): пишет code-style-hook.sh. Метрика читает его read-only —
# детекция остаётся в WP-408 (code-style-hook.sh), здесь только агрегация (WP-408 Ф6, шов 2).
CODE_VIOLATION_LOG = os.path.expanduser("~/.claude/logs/style-violations.log")
# События, для которых базовый регистр (fallback) — намеренно. Исключаются из знаменателя покрытия.
INTENTIONAL_FALLBACK_EVENTS: set = set()
# Машинные маркеры (A10): запрещены во ВСЕХ человеко-регистрах. Фиксированный набор MVP.
MACHINE_MARKERS = [
    r"\bexit 0\b", r"\bexit code\b", r"\bPASS\b", r"\bFAIL\b", r"\bSHA[:\s]",
]


def is_covered(fragment: str, fallback_used: bool) -> bool:
    """Слот покрывает ситуацию ⟺ не fallback И фрагмент непуст (защита от слота-заглушки)."""
    return (not fallback_used) and len(fragment.strip()) >= MIN_FRAGMENT_LENGTH


def coverage_report() -> dict:
    """Покрытие по событиям диспетчера. covered/uncovered/unmapped + доля."""
    covered, uncovered, unmapped = [], [], []
    for event in dispatcher.EVENT_KEYS:
        if event in INTENTIONAL_FALLBACK_EVENTS:
            continue
        # зовём компилятор напрямую через event→key диспетчера: метрика читает МОЛЧА,
        # не дёргая stderr-предупреждение dispatch при fallback (Кими-ревью).
        res = compiler.compile_key(dispatcher.context_key_for(event), use_cache=False)
        if is_covered(res.fragment, res.fallback_used):
            covered.append(event)
        else:
            uncovered.append(event)
            if res.fallback_used:
                unmapped.append(event)  # упал в fallback без флага → забыли слот
    evaluated = len(covered) + len(uncovered)
    coverage = len(covered) / evaluated if evaluated else 1.0
    return {"coverage": coverage, "covered": sorted(covered),
            "uncovered": sorted(uncovered), "unmapped": sorted(unmapped), "evaluated": evaluated}


def mechanical_compliance_check(text: str) -> list:
    """Выход→регистр, механический поднабор (A10). Машинные маркеры запрещены. Возвращает нарушения."""
    violations = []
    for pat in MACHINE_MARKERS:
        for m in re.finditer(pat, text):
            violations.append({"rule": "A10-machine-marker", "match": m.group(0), "pos": m.start()})
    return violations


def semantic_compliance_check(text: str, register: str | None = None) -> dict:
    """Выход→регистр, семантическое направление (A1 путь-подлежащее, A5 ЧТО-до-КАК).
    СТАБ — нужен LLM. Интерфейс зафиксирован, реализация отложена (как стиль-из-примера Ф7)."""
    return {
        "status": "not_implemented",
        "interface": "(text, register) -> [{rule, span, explanation}]",
        "note": "LLM-семантическая проверка A1/A5 — следующий слой после MVP",
    }


def code_compliance_from_hook_log(log_path: str | None = None) -> dict:
    """Выход→регистр для КОДА: агрегирует нарушения из лога детектора code-style-hook.sh.

    Read-only: детекция P1/P2/P4 живёт в WP-408 (code-style-hook.sh), метрика только считает.
    Контракт строки лога (WP-388): 'TIMESTAMP | agent | rule | desc | context'; rule вида P\\d+ —
    кодовое нарушение, прочие (BASE*, A*) — текстовые, в этот счётчик не входят.
    Лога нет → нарушений по коду не зафиксировано (status no_log, не ошибка).
    """
    path = log_path or CODE_VIOLATION_LOG
    if not os.path.exists(path):
        return {"status": "no_log", "path": path, "total": 0, "by_rule": {}}
    by_rule: dict = {}
    # errors="replace": лог несёт редактированные сниппеты кода, байты могут быть не UTF-8.
    # Поле правила (parts[2]) всегда ASCII (P\d+), битые байты в контексте не должны ронять подсчёт.
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 3:
                continue
            rule = parts[2]
            if re.fullmatch(r"P\d+", rule):
                by_rule[rule] = by_rule.get(rule, 0) + 1
    return {"status": "ok", "path": path, "total": sum(by_rule.values()),
            "by_rule": dict(sorted(by_rule.items()))}


def main() -> int:
    ap = argparse.ArgumentParser(description="Метрики дисциплины стилей (WP-412 Ф10)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("coverage", help="отчёт покрытия по событиям диспетчера")
    c = sub.add_parser("check", help="механические нарушения соответствия в тексте")
    c.add_argument("text")
    sub.add_parser("code-compliance", help="нарушения кода P1/P2/P4 из лога детектора")
    args = ap.parse_args()

    if args.cmd == "coverage":
        r = coverage_report()
        print(f"Покрытие: {r['coverage']:.0%} ({len(r['covered'])}/{r['evaluated']} событий)")
        if r["uncovered"]:
            print(f"Не покрыто: {r['uncovered']}")
        if r["unmapped"]:
            print(f"Забыли слот (unmapped): {r['unmapped']}")
        return 0

    if args.cmd == "code-compliance":
        r = code_compliance_from_hook_log()
        if r["status"] == "no_log":
            print(f"Лог детектора кода не найден ({r['path']}) — нарушений не зафиксировано.")
            return 0
        print(f"Нарушений кода: {r['total']} {r['by_rule'] or '(чисто)'}")
        return 1 if r["total"] else 0

    violations = mechanical_compliance_check(args.text)
    if violations:
        print(f"Нарушения соответствия ({len(violations)}):")
        for v in violations:
            print(f"  {v['rule']}: «{v['match']}» (поз. {v['pos']})")
        return 1
    print("Механических нарушений нет.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
