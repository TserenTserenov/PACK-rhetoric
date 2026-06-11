#!/usr/bin/env python3
# see DP.SC.174 (Диспетчер стилей), DP.ROLE.074
"""Диспетчер стилей (WP-412 Ф6). Тонкий слой: событие интерфейса → context_key → вызов компилятора.

Граница (DP.ROLE.074 маршрутизация ≠ DP.ROLE.073 данные): диспетчер знает только «какое событие
интерфейса → какие плоские оси ключа». Никакой стилевой логики — её держит реестр/компилятор.
Про авторский слой L1 диспетчер НЕ знает: он передаёт ключ, author-overlay подмешивает компилятор.

НЕ подменяет живые хуки (это отдельный S-33 шаг с явного согласия пилота). Здесь — вызываемая
библиотека + CLI для будущей проводки и паритет-тестов.

CLI:
  dispatcher.py --event pretooluse-edit [--domain '*'] [--market ru]
"""

from __future__ import annotations

import argparse
import os
import sys

import compiler

# Таблица «событие интерфейса → плоские оси context_key». Рантайм-проводка, не стиль.
# Канал — ось ключа (выбирает слот), задаётся событием. domain/market достраиваются ниже.
EVENT_KEYS = {
    "userpromptsubmit-ide": {"reader_meta_class": "human", "reader_role": "pilot", "channel": "ide"},
    "pretooluse-edit": {"reader_meta_class": "human", "reader_role": "developer", "channel": "code"},
    "bot-telegram": {"reader_meta_class": "human", "reader_role": "novice", "channel": "telegram"},
}


def context_key_for(event: str, domain: str = "*", market: str | None = None) -> dict:
    """Собрать context_key из события интерфейса + рантайм-факты. market-дефолт — из env (конфиг)."""
    base = EVENT_KEYS.get(event)
    if base is None:
        raise KeyError(f"неизвестное событие интерфейса: {event}. Известны: {sorted(EVENT_KEYS)}")
    key = dict(base)
    key["domain"] = domain
    key["market"] = market if market is not None else os.environ.get("IWE_STYLE_MARKET")
    return key


def dispatch(event: str, domain: str = "*", market: str | None = None, use_cache: bool = True):
    """Главная точка: событие → ключ → фрагмент стиля от компилятора.
    Если для события ещё нет слота регистра — компилятор отдаёт базовый fallback;
    делаем деградацию видимой (не молчим, «no silent caps»), а не молча отдаём голый пол."""
    res = compiler.compile_key(context_key_for(event, domain, market), use_cache=use_cache)
    if res.fallback_used:
        print(f"dispatcher: событие {event} → нет слота регистра, отдан базовый fallback", file=sys.stderr)
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description="Диспетчер стилей (WP-412 Ф6)")
    ap.add_argument("--event", required=True, choices=sorted(EVENT_KEYS))
    ap.add_argument("--domain", default="*")
    ap.add_argument("--market", default=None)
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args()

    res = dispatch(args.event, args.domain, args.market, use_cache=not args.no_cache)
    print(f"# event={args.event} key_hash={res.key_hash[:12]} fallback_used={res.fallback_used}")
    print(f"# applied_layers={res.applied_layers}")
    print(f"# source_refs={[r['source_id'] for r in res.source_refs]}")
    print("---")
    print(res.fragment)
    return 0


if __name__ == "__main__":
    sys.exit(main())
