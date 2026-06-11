#!/usr/bin/env python3
# see DP.SC.173 (реестр языковых стилей), DP.ROLE.073 (Хранитель реестра)
"""Компилятор реестра языковых стилей (WP-412 Ф5).

Двухслойная модель source/compiled (вариант A′, peer-session 2026-06-11-31):
  - source   — слот-файлы (05-formalizations/LS.FORM.*) + указатель content_source
               на владельца правил. OwnerIntegrity: правила живут у владельца, слот ссылается.
  - compiled — derived build-cache в compiled/ (в .gitignore, не коммитится).
               Пересобирается, когда manifest_hash источников изменился → дрейф невозможен.
  - registry-manifest.lock — коммитится, мелкий: отпечатки всех источников из ОБОИХ репо.
               Guard свежести (verify) сверяет .lock с живыми хэшами.

Резолюция каскада — два шага:
  1) ключ контекста (мета-класс, роль, канал, домен) выбирает слот регистра;
  2) наложения base → domain → market → user домешивают контент внутри слота.
Канал — ось ключа (выбирает слот), НЕ слой overlay. Канально-условные правки живут в market.

CLI:
  compiler.py compile --meta-class human --role pilot --channel ide [--domain '*'] [--market ru]
  compiler.py lock      # перегенерировать registry-manifest.lock
  compiler.py verify    # exit 0 если .lock свеж, exit 1 + список изменений если устарел
"""

from __future__ import annotations  # ленивые аннотации: dict|None, list[Slot] работают на 3.7+

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

import yaml

REGISTRY_DIR = Path(__file__).resolve().parent
PACK_DIR = REGISTRY_DIR.parent              # .../pack/language-style
COMPILED_DIR = REGISTRY_DIR / "compiled"
LOCK_PATH = REGISTRY_DIR / "registry-manifest.lock"
WILDCARD = "*"
AXES = ("reader_meta_class", "reader_role", "channel", "domain")
# Бамп при изменении логики материализации/каскада: инвалидирует derived-кэш даже если
# источники не менялись (manifest_hash один, а выход компилятора другой).
COMPILER_VERSION = "f5.1"


def find_iwe_root(start: Path) -> Path:
    """Корень workspace ~/IWE = ближайший предок, содержащий оба пака-соседа."""
    for parent in [start, *start.parents]:
        if (parent / "PACK-rhetoric").is_dir() and (parent / "PACK-digital-platform").is_dir():
            return parent
    raise FileNotFoundError(
        "Не нашёл корень IWE (директорию с PACK-rhetoric и PACK-digital-platform) "
        f"вверх от {start}"
    )


IWE_ROOT = find_iwe_root(REGISTRY_DIR)


def canonical_json(obj) -> str:
    """Каноническая форма для детерминированного хэша: ключи отсортированы, без пробелов."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Разбить файл на (frontmatter-dict, body). Нет frontmatter → ({}, весь текст)."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    front = yaml.safe_load(parts[1]) or {}
    return front, parts[2].lstrip("\n")


def extract_inject_region(body: str) -> str:
    """Если владелец размечен маркерами инъекции (INJECT-START/END) — вернуть только регион
    между ними (это канонический фрагмент, который реально впрыскивает хук; вне региона —
    методичка про сам хук, не стиль). Маркеры-комментарии в выход не попадают.
    Нет маркеров → всё тело."""
    lines = body.splitlines()
    start = end = None
    for i, line in enumerate(lines):
        if "INJECT-START" in line:
            start = i
        elif "INJECT-END" in line:
            end = i
            break
    if start is not None and end is not None and start < end:
        return "\n".join(lines[start + 1:end]).strip()
    return body.strip()


def rel_to_root(path: Path) -> str:
    """Путь относительно корня IWE для манифеста. Источник вне корня → абсолютный путь,
    не роняем lock/verify (defensive: будущий ../-escape в content-sources)."""
    try:
        return str(path.relative_to(IWE_ROOT))
    except ValueError:
        return str(path)


# ---------- загрузка реестра ----------

@dataclass
class Slot:
    slot_id: str
    path: Path
    context_key: dict
    content_source: str
    fallback_text: str
    slot_sha: str


def load_index() -> dict:
    return yaml.safe_load((REGISTRY_DIR / "registry-index.yaml").read_text("utf-8"))


def load_content_sources() -> dict:
    raw = yaml.safe_load((REGISTRY_DIR / "content-sources.yaml").read_text("utf-8"))
    return {sid: (IWE_ROOT / rel) for sid, rel in raw.items()}


def load_slot(rel_path: str) -> Slot:
    path = PACK_DIR / rel_path
    front, _ = split_frontmatter(path.read_text("utf-8"))
    ck = front.get("context_key", {})
    return Slot(
        slot_id=front["id"],
        path=path,
        context_key={ax: ck.get(ax, WILDCARD) for ax in AXES},
        content_source=front.get("content_source", "inline"),
        fallback_text=front.get("fallback_text", ""),
        slot_sha=sha256_file(path),
    )


def load_slots(index: dict) -> list[Slot]:
    return [load_slot(p) for p in index["slots"]]


# ---------- резолюция слота ----------

def slot_matches(slot: Slot, key: dict) -> bool:
    """Слот матчит ключ, если по каждой оси значение совпадает или у слота wildcard."""
    for ax in AXES:
        sv = slot.context_key[ax]
        if sv != WILDCARD and sv != key[ax]:
            return False
    return True


def specificity(slot: Slot) -> int:
    """Чем меньше wildcard-ов, тем специфичнее слот (для most-specific-wins)."""
    return sum(1 for ax in AXES if slot.context_key[ax] != WILDCARD)


def resolve_slot(slots: list[Slot], fallback_id: str, key: dict) -> tuple[Slot, bool]:
    """Вернуть (слот, fallback_used). Промах ключа → fallback-слот + True.
    При равной специфичности tie-break по slot_id → результат не зависит от порядка строк
    в индексе (держит инвариант детерминизма DP.SC.173: один ключ → один фрагмент навсегда)."""
    candidates = [s for s in slots if s.slot_id != fallback_id and slot_matches(s, key)]
    if candidates:
        best = min(candidates, key=lambda s: (-specificity(s), s.slot_id))
        return best, False
    fallback = next(s for s in slots if s.slot_id == fallback_id)
    return fallback, True


# ---------- материализация контента ----------

def materialize_base(slot: Slot, content_sources: dict) -> tuple[str, list[dict]]:
    """Тело базового фрагмента из владельца контента. inline → fallback_text слота.
    Возвращает (фрагмент, source_refs использованных источников)."""
    refs = [{"source_id": f"slot:{slot.slot_id}", "source_hash": slot.slot_sha}]
    if slot.content_source == "inline":
        return slot.fallback_text.rstrip("\n"), refs
    owner = content_sources.get(slot.content_source)
    if owner is None or not owner.exists():
        # Режим отказа уже отработал на уровне резолюции; сюда попадаем только если
        # у валидного слота пропал владелец — честно сообщаем, не молчим (P4).
        raise FileNotFoundError(
            f"Владелец контента {slot.content_source} для слота {slot.slot_id} не найден: {owner}"
        )
    _, body = split_frontmatter(owner.read_text("utf-8"))
    refs.append({"source_id": f"content:{slot.content_source}", "source_hash": sha256_file(owner)})
    return extract_inject_region(body), refs


# ---------- каскад наложений ----------

def domain_applies(ov: dict, slot: Slot, key: dict) -> bool:
    """Доменное наложение применимо, если домен совпал и applies_to пускает роль/канал слота."""
    if ov.get("domain") != key["domain"]:
        return False
    gate = ov.get("applies_to", {})
    role_ok = "reader_role" not in gate or slot.context_key["reader_role"] in gate["reader_role"]
    channel_ok = "channel" not in gate or slot.context_key["channel"] in gate["channel"]
    return role_ok and channel_ok


def select_overlays(index: dict, slot: Slot, key: dict, user_override: dict):
    """Выбрать применимые наложения в порядке каскада. Возвращает (список (имя, путь, data), refs)."""
    chosen, refs = [], []
    for rel in index.get("overlays", {}).get("domain", []):
        path = PACK_DIR / rel
        data = yaml.safe_load(path.read_text("utf-8"))
        if domain_applies(data, slot, key):
            chosen.append((f"domain:{data['domain']}", data))
            refs.append({"source_id": f"overlay:domain:{data['domain']}", "source_hash": sha256_file(path)})
    market = key.get("market")
    if market:
        for rel in index.get("overlays", {}).get("market", []):
            path = PACK_DIR / rel
            data = yaml.safe_load(path.read_text("utf-8"))
            if data.get("market") == market:
                chosen.append((f"market:{data['market']}", data))
                refs.append({"source_id": f"overlay:market:{data['market']}", "source_hash": sha256_file(path)})
    if user_override:
        chosen.append(("user", user_override))
    return chosen, refs


def render_overlay(name: str, data: dict) -> str:
    """Человекочитаемая добавка фрагмента от одного наложения."""
    if name.startswith("domain:"):
        jargon = ", ".join(data.get("jargon_whitelist", [])) or "—"
        concepts = ", ".join(data.get("concepts", [])) or "—"
        return (f"\n\n## Домен: {data['domain']}\n"
                f"Допустимый жаргон без перевода: {jargon}.\n"
                f"Активные понятия (граф WP-415): {concepts}.")
    if name.startswith("market:"):
        seg = data.get("audience_segment", "—")
        tone = ", ".join(f"{k} {v:+d}" if isinstance(v, int) else f"{k} {v}"
                         for k, v in data.get("tone_overrides", {}).items()) or "—"
        return (f"\n\n## Рынок: {data['market']} (сегмент: {seg})\n"
                f"Правки тона: {tone}.")
    # user
    note = data.get("note", "пользовательские правки стиля")
    return f"\n\n## Пользовательский оверрайд\n{note}."


# ---------- хэши и сборка ключа ----------

def platform_layer_hash(slot: Slot, overlay_names: list[str]) -> str:
    payload = {"slot_version": slot.slot_sha, "overlays": sorted(overlay_names)}
    return sha256_text(canonical_json(payload))


def user_override_hash(user_override: dict) -> str:
    return sha256_text(canonical_json(user_override or {}))


def full_key_hash(context_key: dict, uo_hash: str, pl_hash: str) -> str:
    payload = {"context_key": context_key, "user_override_hash": uo_hash, "platform_layer_hash": pl_hash}
    return sha256_text(canonical_json(payload))


# ---------- манифест свежести (оба репо) ----------

def all_source_paths(index: dict, content_sources: dict) -> list[tuple[str, Path]]:
    """Все источники, влияющие на сборку: слоты + владельцы контента + наложения."""
    items: list[tuple[str, Path]] = []
    for rel in index["slots"]:
        items.append((f"slot:{rel}", PACK_DIR / rel))
    for sid, path in content_sources.items():
        items.append((f"content:{sid}", path))
    for cls in ("domain", "market"):
        for rel in index.get("overlays", {}).get(cls, []):
            items.append((f"overlay:{cls}:{rel}", PACK_DIR / rel))
    return items


def compute_manifest(index: dict, content_sources: dict) -> dict:
    sources = []
    for sid, path in all_source_paths(index, content_sources):
        sources.append({
            "id": sid,
            "path": rel_to_root(path),
            "sha256": sha256_file(path) if path.exists() else "MISSING",
        })
    sources.sort(key=lambda s: s["id"])
    manifest_hash = sha256_text(canonical_json([{"id": s["id"], "sha256": s["sha256"]} for s in sources]))
    return {"manifest_hash": manifest_hash, "sources": sources}


# ---------- результат компиляции ----------

@dataclass
class CompiledResult:
    fragment: str
    applied_layers: list[str]
    key_hash: str
    fallback_used: bool
    source_refs: list[dict]


def compile_key(context_key: dict, user_override: dict | None = None, use_cache: bool = True) -> CompiledResult:
    user_override = user_override or {}
    index = load_index()
    content_sources = load_content_sources()
    slots = load_slots(index)
    key = {ax: context_key.get(ax, WILDCARD) for ax in AXES}
    key["market"] = context_key.get("market")

    slot, fallback_used = resolve_slot(slots, index["fallback"], key)
    overlays, ov_refs = select_overlays(index, slot, key, user_override)
    overlay_names = [name for name, _ in overlays]

    pl_hash = platform_layer_hash(slot, overlay_names)
    uo_hash = user_override_hash(user_override)
    key_hash = full_key_hash(key, uo_hash, pl_hash)

    manifest_hash = compute_manifest(index, content_sources)["manifest_hash"]
    cache_path = COMPILED_DIR / f"{key_hash}.json"
    if use_cache and cache_path.exists():
        cached = json.loads(cache_path.read_text("utf-8"))
        if cached.get("manifest_hash") == manifest_hash and cached.get("compiler_version") == COMPILER_VERSION:
            return CompiledResult(**{k: cached[k] for k in
                                     ("fragment", "applied_layers", "key_hash", "fallback_used", "source_refs")})

    base_fragment, refs = materialize_base(slot, content_sources)
    parts = [base_fragment]
    for name, data in overlays:
        parts.append(render_overlay(name, data))
    fragment = "".join(parts)

    result = CompiledResult(
        fragment=fragment,
        applied_layers=["base", *overlay_names],
        key_hash=key_hash,
        fallback_used=fallback_used,
        source_refs=refs + ov_refs,
    )
    if use_cache:
        COMPILED_DIR.mkdir(exist_ok=True)
        cache_path.write_text(json.dumps({**asdict(result), "manifest_hash": manifest_hash,
                                          "compiler_version": COMPILER_VERSION},
                                         ensure_ascii=False, indent=2), "utf-8")
    return result


# ---------- lock / verify ----------

def write_lock() -> dict:
    index = load_index()
    content_sources = load_content_sources()
    manifest = compute_manifest(index, content_sources)
    LOCK_PATH.write_text(
        "# AUTO-GENERATED (registry-manifest.lock) — коммитится как package-lock.\n"
        "# Перегенерация: python3 compiler.py lock. Проверка: python3 compiler.py verify.\n"
        + yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
        "utf-8",
    )
    return manifest


def verify_lock() -> tuple[bool, list[str]]:
    """Сверить .lock с живыми хэшами. Возвращает (свеж, список изменений)."""
    if not LOCK_PATH.exists():
        return False, ["registry-manifest.lock отсутствует — выполни: python3 compiler.py lock"]
    locked = yaml.safe_load(LOCK_PATH.read_text("utf-8"))
    current = compute_manifest(load_index(), load_content_sources())
    if locked.get("manifest_hash") == current["manifest_hash"]:
        return True, []
    locked_by_id = {s["id"]: s["sha256"] for s in locked.get("sources", [])}
    current_by_id = {s["id"]: s["sha256"] for s in current["sources"]}
    changes = []
    for sid in sorted(set(locked_by_id) | set(current_by_id)):
        old, new = locked_by_id.get(sid), current_by_id.get(sid)
        if old != new:
            changes.append(f"{sid}: {(old or 'нет')[:8]} → {(new or 'нет')[:8]}")
    return False, changes


# ---------- CLI ----------

def main() -> int:
    ap = argparse.ArgumentParser(description="Компилятор реестра языковых стилей (WP-412 Ф5)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("compile", help="скомпилировать фрагмент по ключу")
    c.add_argument("--meta-class", default=WILDCARD)
    c.add_argument("--role", default=WILDCARD)
    c.add_argument("--channel", default=WILDCARD)
    c.add_argument("--domain", default=WILDCARD)
    c.add_argument("--market", default=None)
    c.add_argument("--no-cache", action="store_true")

    sub.add_parser("lock", help="перегенерировать registry-manifest.lock")
    sub.add_parser("verify", help="проверить свежесть .lock (exit 1 при дрейфе)")

    args = ap.parse_args()

    if args.cmd == "compile":
        key = {"reader_meta_class": args.meta_class, "reader_role": args.role,
               "channel": args.channel, "domain": args.domain, "market": args.market}
        res = compile_key(key, use_cache=not args.no_cache)
        print(f"# key_hash={res.key_hash[:12]} fallback_used={res.fallback_used}")
        print(f"# applied_layers={res.applied_layers}")
        print(f"# source_refs={[r['source_id'] for r in res.source_refs]}")
        print("---")
        print(res.fragment)
        return 0

    if args.cmd == "lock":
        m = write_lock()
        print(f"registry-manifest.lock записан: manifest_hash={m['manifest_hash'][:12]}, "
              f"источников {len(m['sources'])}")
        return 0

    if args.cmd == "verify":
        fresh, changes = verify_lock()
        if fresh:
            print("registry-manifest.lock свеж — источники совпадают.")
            return 0
        print("registry-manifest.lock устарел. Изменились источники:")
        for ch in changes:
            print(f"  {ch}")
        print("Перегенерируй: python3 compiler.py lock")
        return 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
