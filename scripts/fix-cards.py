#!/usr/bin/env python3
"""
fix-cards.py — Комплексное исправление карточек после SOTA-ревью.

Проблемы, которые устраняет:
  1. source_text пустой ("|") — обогащение цитатой из оригинального поста
  2. trope_type неправильный у 4 карточек (135, 151, 188, 138)
  3. canonical: true слишком часто — оставить только quality_score >= 0.80
  4. breaks_when анти-паттерны ("не применяется", "", "не ломается")

Usage:
    python3 fix-cards.py --dry-run      # показать что изменится
    python3 fix-cards.py                # применить все фиксы
    python3 fix-cards.py --step source  # только source_text
    python3 fix-cards.py --step tropes  # только trope_type
    python3 fix-cards.py --step canonical
    python3 fix-cards.py --step breaks
"""

from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

PACK_DIR = Path(__file__).parent.parent
ILLUSTRATIONS_DIR = PACK_DIR / "illustrations"
API_TOKEN_FILE = Path.home() / ".secrets" / "club_api_token"
CLUB_BASE_URL = "https://systemsworld.club"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
RATE_LIMIT_DELAY = 1.2

# Карточки с заведомо неправильным trope_type
TROPE_OVERRIDES = {
    "RHE.ILL.135": "example",    # атрибутивное ядро — не аналогия
    "RHE.ILL.151": "example",    # нет второго домена — не аналогия
    "RHE.ILL.188": "metaphor",   # нет конкретики — не example, есть образ множителя
    "RHE.ILL.138": "analogy",    # остаётся analogy, но structural_core нужно переписать
}

BREAKS_WHEN_ANTIPATTERNS = re.compile(
    r'^(не применяется|не ломается|n/a|none|null|не (имеет|применим)|""|'
    r'не (нужен|требуется)|inapplicable|\s*)$',
    re.IGNORECASE
)


def api_headers() -> dict:
    token = API_TOKEN_FILE.read_text().strip() if API_TOKEN_FILE.exists() else ""
    if not token:
        raise RuntimeError(f"API token not found: {API_TOKEN_FILE}")
    return {"Api-Key": token, "Api-Username": "system"}


def fetch_post_text(topic_id: int, post_id: int) -> str:
    """Fetch raw text of a specific post from club API."""
    url = f"{CLUB_BASE_URL}/t/{topic_id}.json"
    req = urllib.request.Request(url, headers=api_headers())
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            posts = data.get("post_stream", {}).get("posts", [])
            for p in posts:
                if p.get("id") == post_id:
                    raw = p.get("cooked", "") or p.get("raw", "")
                    text = re.sub(r"<[^>]+>", " ", raw)
                    text = re.sub(r"\s+", " ", text).strip()
                    return text[:3000]
    except Exception as e:
        print(f"    [WARN] fetch_post failed t/{topic_id}/p/{post_id}: {e}", file=sys.stderr)
    return ""


def llm_extract_source_text(post_text: str, structural_core: str, trope_type: str) -> str:
    """Ask claude to extract 1-3 sentence quote from post that best represents the illustration."""
    prompt = f"""Из текста поста выбери 1-3 предложения (ДОСЛОВНАЯ ЦИТАТА), которые лучше всего иллюстрируют следующую риторическую иллюстрацию типа {trope_type}.

structural_core: {structural_core}

Текст поста:
{post_text}

Правила:
- Дай ТОЛЬКО цитату (1-3 предложения из текста), без пояснений
- Не перефразируй — только оригинальные слова из поста
- Без имён собственных (если есть — замени на «один из участников», «исследователь»)
- Если подходящей цитаты нет — выведи: NO_QUOTE"""

    cmd = ["claude", "-p", prompt, "--model", CLAUDE_MODEL, "--output-format", "text"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        result = r.stdout.strip()
        if "NO_QUOTE" in result or not result:
            return ""
        # Limit to 3 sentences max
        sentences = re.split(r'(?<=[.!?])\s+', result)
        return " ".join(sentences[:3]).strip()
    except Exception as e:
        print(f"    [WARN] LLM extract failed: {e}", file=sys.stderr)
        return ""


def llm_fix_breaks_when(structural_core: str, trope_type: str, concept: str) -> str:
    """Ask claude to generate a proper breaks_when for a card with anti-pattern value."""
    prompt = f"""Сформулируй breaks_when для риторической иллюстрации типа {trope_type}.

structural_core: {structural_core}
illustrates_concept: {concept}

breaks_when должен описывать КОНКРЕТНОЕ УСЛОВИЕ, при котором перенос/образ/аналогия ломается или вводит в заблуждение.
НЕ «как преодолеть» — а «где модель даёт ошибку».
1-2 предложения максимум. Только текст значения, без кавычек и ключей."""

    cmd = ["claude", "-p", prompt, "--model", CLAUDE_MODEL, "--output-format", "text"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        result = r.stdout.strip().strip('"').strip("'")
        return result if len(result) > 10 else ""
    except Exception:
        return ""


def llm_fix_structural_core_analogy(current_core: str, post_text: str, concept: str) -> str:
    """Fix attributive structural_core for analogy to be relational."""
    prompt = f"""Исправь structural_core аналогии — сделай его РЕЛЯЦИОННЫМ, а не атрибутивным.

Текущий (атрибутивный — перечисляет общие свойства):
{current_core}

illustrates_concept: {concept}

Контекст поста:
{post_text[:1000]}

Правило: structural_core аналогии = «[элемент A] соответствует [элементу B], потому что [общее ОТНОШЕНИЕ между ними, а не общее свойство]».
Тест: убери оба домена — должно остаться утверждение об отношении, а не о свойстве.

Выведи только новый structural_core (1 предложение). Без кавычек, без пояснений."""

    cmd = ["claude", "-p", prompt, "--model", CLAUDE_MODEL, "--output-format", "text"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        result = r.stdout.strip().strip('"').strip("'")
        return result if len(result) > 15 else ""
    except Exception:
        return ""


def parse_card(path: Path) -> dict:
    """Parse frontmatter from a card file."""
    text = path.read_text(encoding="utf-8")
    # Extract frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not fm_match:
        return {}
    fm = fm_match.group(1)

    card = {"_path": str(path), "_raw": text}

    # Parse simple key: value lines
    for line in fm.splitlines():
        if re.match(r'^[a-zA-Z_]+:', line):
            key, _, val = line.partition(":")
            val = val.strip().strip('"').strip("'")
            card[key.strip()] = val

    # Extract multiline source_text
    m = re.search(r'source_text:\s*\|\n((?:  .+\n?)*)', fm)
    if m:
        raw_st = m.group(1)
        lines = [l[2:] if l.startswith("  ") else l for l in raw_st.splitlines()]
        st = "\n".join(lines).strip()
        if st and st != "|":
            card["source_text"] = st
        else:
            card["source_text"] = ""
    elif "source_text" in card and card["source_text"] == "|":
        card["source_text"] = ""

    return card


def update_card_field(path: Path, field: str, new_value: str) -> bool:
    """Update a single frontmatter field in a card file."""
    text = path.read_text(encoding="utf-8")

    if field == "source_text":
        # Replace the entire source_text block
        indented = "\n".join("  " + line for line in new_value.splitlines())
        new_block = f"source_text: |\n{indented}"
        # Match existing source_text block (including multiline)
        pattern = r'source_text:.*?(?=\n[a-zA-Z])'
        new_text = re.sub(pattern, new_block, text, flags=re.DOTALL)
        if new_text == text:
            # Fallback: replace single-line version
            new_text = re.sub(r'source_text:\s*\|?\s*\n  \|', new_block, text)
        # Also update ## Source section
        new_text = re.sub(
            r'(## Source\n\n).*?(\n\n## )',
            rf'\g<1>{new_value}\g<2>',
            new_text,
            flags=re.DOTALL
        )
    elif field == "trope_type":
        new_text = re.sub(r'^trope_type:.*$', f'trope_type: {new_value}', text, flags=re.MULTILINE)
    elif field == "canonical":
        new_text = re.sub(r'^canonical:.*$', f'canonical: {new_value}', text, flags=re.MULTILINE)
    elif field == "breaks_when":
        escaped = new_value.replace('"', '\\"')
        new_text = re.sub(r'^breaks_when:.*$', f'breaks_when: "{escaped}"', text, flags=re.MULTILINE)
        new_text = re.sub(
            r'(## Boundaries \(breaks_when\)\n\n).*?(\n\n---)',
            rf'\g<1>{new_value}\g<2>',
            new_text,
            flags=re.DOTALL
        )
    elif field == "structural_core":
        escaped = new_value.replace('"', '\\"')
        new_text = re.sub(r'^structural_core:.*$', f'structural_core: "{escaped}"', text, flags=re.MULTILINE)
        new_text = re.sub(
            r'(## Structural Core\n\n).*?(\n\n## )',
            rf'\g<1>{new_value}\g<2>',
            new_text,
            flags=re.DOTALL
        )
    else:
        return False

    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def parse_origin(origin_source: str) -> tuple[int, int]:
    """Parse 'club/t/NNNN/p/MMMM' → (topic_id, post_id)."""
    m = re.match(r'club/t/(\d+)/p/(\d+)', origin_source)
    if m:
        return int(m.group(1)), int(m.group(2))
    return 0, 0


def get_all_cards() -> list[dict]:
    cards = []
    for p in ILLUSTRATIONS_DIR.rglob("RHE.ILL.*.md"):
        c = parse_card(p)
        if c:
            cards.append(c)
    return sorted(cards, key=lambda c: c.get("id", ""))


# ── Steps ─────────────────────────────────────────────────────────────────────

def step_source_text(cards: list[dict], dry_run: bool) -> int:
    """Enrich empty source_text fields by fetching original posts."""
    fixed = 0
    needs_fix = [c for c in cards if not c.get("source_text", "").strip()]
    print(f"\n[fix-source] {len(needs_fix)} cards need source_text enrichment")

    for c in needs_fix:
        path = Path(c["_path"])
        origin = c.get("origin_source", "")
        card_id = c.get("id", path.stem)
        tid, pid = parse_origin(origin)

        if not tid or not pid:
            print(f"  [SKIP] {card_id} — no origin_source URL")
            continue

        print(f"  {card_id} (t/{tid}/p/{pid})...", end=" ", flush=True)
        post_text = fetch_post_text(tid, pid)
        time.sleep(RATE_LIMIT_DELAY)

        if not post_text:
            print("no post text")
            continue

        structural_core = c.get("structural_core", "")
        trope_type = c.get("trope_type", "example")
        quote = llm_extract_source_text(post_text, structural_core, trope_type)
        time.sleep(0.5)

        if not quote:
            print("no quote extracted")
            continue

        print(f"✓ ({len(quote)} chars)")
        if not dry_run:
            update_card_field(path, "source_text", quote)
            fixed += 1
        else:
            print(f"    → {quote[:80]}...")

    return fixed


def step_trope_types(cards: list[dict], dry_run: bool) -> int:
    """Fix known trope_type misclassifications."""
    fixed = 0
    print(f"\n[fix-tropes] Checking {len(TROPE_OVERRIDES)} known misclassifications")

    for c in cards:
        card_id = c.get("id", "")
        base_id = card_id.split("-")[0] if "-" in card_id else card_id

        for override_id, correct_type in TROPE_OVERRIDES.items():
            if card_id == override_id or base_id == override_id:
                current = c.get("trope_type", "")
                if current == correct_type:
                    print(f"  {card_id}: already {correct_type} ✓")
                    continue

                path = Path(c["_path"])
                print(f"  {card_id}: {current} → {correct_type}", end=" ")

                # For RHE.ILL.138: fix structural_core too (attributive analogy)
                if card_id == "RHE.ILL.138":
                    origin = c.get("origin_source", "")
                    tid, pid = parse_origin(origin)
                    post_text = fetch_post_text(tid, pid) if tid else ""
                    new_core = llm_fix_structural_core_analogy(
                        c.get("structural_core", ""),
                        post_text,
                        c.get("illustrates", [{}])[0].get("concept_description", "") if isinstance(c.get("illustrates"), list) else c.get("concept_description", "")
                    )
                    if new_core and not dry_run:
                        update_card_field(path, "structural_core", new_core)
                        print(f"(core rewritten)", end=" ")

                if not dry_run:
                    # Move file to correct subdirectory
                    new_dir = ILLUSTRATIONS_DIR / correct_type
                    new_dir.mkdir(parents=True, exist_ok=True)
                    new_path = new_dir / path.name
                    if new_path != path and not new_path.exists():
                        path.rename(new_path)
                        path = new_path
                        print(f"(moved)", end=" ")
                    update_card_field(path, "trope_type", correct_type)
                    fixed += 1

                print("✓")
                break

    return fixed


def step_canonical(cards: list[dict], dry_run: bool) -> int:
    """Reduce canonical: true to only quality_score >= 0.80."""
    fixed = 0
    canonical_true = [c for c in cards if c.get("canonical", "false") == "true"]
    print(f"\n[fix-canonical] {len(canonical_true)} cards have canonical:true (target: ~30% = ~{len(cards)//3})")

    for c in canonical_true:
        score = float(c.get("quality_score", "0.5") or "0.5")
        if score < 0.80:
            card_id = c.get("id", "")
            path = Path(c["_path"])
            print(f"  {card_id} score={score:.2f}: true → false", end=" ")
            if not dry_run:
                update_card_field(path, "canonical", "false")
                fixed += 1
            print("✓")

    return fixed


def step_breaks_when(cards: list[dict], dry_run: bool) -> int:
    """Fix anti-pattern breaks_when values."""
    fixed = 0
    needs_fix = []
    for c in cards:
        # Skip manually created seed cards (no origin_source)
        if not c.get("origin_source", "").startswith("club/"):
            continue
        bw = c.get("breaks_when", "").strip().strip('"').strip("'")
        tt = c.get("trope_type", "")
        # analogy and metaphor MUST have breaks_when; example/case optional but fix bad values
        if tt in ("analogy", "metaphor", "case") and BREAKS_WHEN_ANTIPATTERNS.match(bw):
            needs_fix.append(c)
        elif tt in ("example", "counter_example") and bw and BREAKS_WHEN_ANTIPATTERNS.match(bw):
            needs_fix.append(c)

    print(f"\n[fix-breaks] {len(needs_fix)} cards with anti-pattern breaks_when")

    for c in needs_fix:
        card_id = c.get("id", "")
        path = Path(c["_path"])
        sc = c.get("structural_core", "")
        tt = c.get("trope_type", "")
        # Get concept from nested structure or flat
        concept = ""
        if "illustrates" in c:
            pass  # parsed as string by our simple parser
        concept = c.get("concept_description", "") or c.get("illustrates_concept", "")

        print(f"  {card_id} ({tt})...", end=" ", flush=True)
        new_bw = llm_fix_breaks_when(sc, tt, concept)
        time.sleep(0.5)

        if not new_bw:
            print("could not generate")
            continue

        print(f"✓")
        if not dry_run:
            update_card_field(path, "breaks_when", new_bw)
            fixed += 1
        else:
            print(f"    → {new_bw[:80]}...")

    return fixed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--step", choices=["source", "tropes", "canonical", "breaks", "all"],
                        default="all")
    args = parser.parse_args()

    dry_run = args.dry_run
    if dry_run:
        print("[DRY-RUN mode — no files will be changed]")

    cards = get_all_cards()
    print(f"Loaded {len(cards)} cards")

    total_fixed = 0

    if args.step in ("source", "all"):
        total_fixed += step_source_text(cards, dry_run)

    if args.step in ("tropes", "all"):
        # Re-load cards if source_text was updated
        if args.step == "all" and not dry_run:
            cards = get_all_cards()
        total_fixed += step_trope_types(cards, dry_run)

    if args.step in ("canonical", "all"):
        total_fixed += step_canonical(cards, dry_run)

    if args.step in ("breaks", "all"):
        if args.step == "all" and not dry_run:
            cards = get_all_cards()
        total_fixed += step_breaks_when(cards, dry_run)

    print(f"\n{'[DRY-RUN] Would fix' if dry_run else 'Fixed'}: {total_fixed} changes")


if __name__ == "__main__":
    main()
