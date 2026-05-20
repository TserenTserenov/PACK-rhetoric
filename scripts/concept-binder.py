#!/usr/bin/env python3
"""
concept-binder.py — Привязка иллюстративных карточек к концептам PACK-personal.

Решает: после M-RM mining карточки имеют `concept_id: TBD`. Без привязки R15
не может найти иллюстрацию по концепту → Pack нерабочий.

Алгоритм:
1. Индексирует все PD.*.md в PACK-personal (id + name + 1-line summary)
2. Для каждой карточки RHE.ILL.* с concept_id=TBD:
   - подаёт LLM: illustrates_concept + structural_core + индекс концептов
   - LLM возвращает best match или NONE
3. Обновляет concept_id в карточке.

Usage:
    python3 concept-binder.py --dry-run
    python3 concept-binder.py
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PACK_RHETORIC = Path(__file__).parent.parent
PACK_PERSONAL = PACK_RHETORIC.parent / "PACK-personal"
ENTITIES_DIR = PACK_PERSONAL / "pack" / "personal-development" / "02-domain-entities"
ILLUSTRATIONS_DIR = PACK_RHETORIC / "illustrations"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"


def index_concepts() -> list[dict]:
    """Index all PD.* concepts from PACK-personal/02-domain-entities/."""
    concepts = []
    for md in ENTITIES_DIR.rglob("PD.*.md"):
        text = md.read_text(encoding="utf-8")
        # Extract frontmatter
        fm = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
        if not fm:
            continue
        fm_text = fm.group(1)

        id_match = re.search(r'^id:\s*(\S+)', fm_text, re.MULTILINE)
        name_match = re.search(r'^name:\s*(.+)$', fm_text, re.MULTILINE)
        if not id_match:
            continue

        cid = id_match.group(1).strip().strip('"').strip("'")
        name = name_match.group(1).strip().strip('"').strip("'") if name_match else ""

        # Get H1 if no name in frontmatter
        if not name:
            h1 = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
            if h1:
                name = h1.group(1).strip()
                name = re.sub(r'^\[' + re.escape(cid) + r'\]\s*', '', name)

        # Get short description: first non-empty paragraph after H1
        body = text[fm.end():]
        # Skip H1
        body = re.sub(r'^#\s+.+\n+', '', body, count=1)
        # Take first paragraph (up to first blank line or H2)
        first_para_match = re.search(r'^([^#\n].+?)(?:\n\n|\n#)', body, re.DOTALL)
        summary = first_para_match.group(1).strip() if first_para_match else ""
        summary = re.sub(r'\s+', ' ', summary)[:200]

        concepts.append({
            "id": cid,
            "name": name,
            "summary": summary,
            "path": str(md.relative_to(PACK_PERSONAL)),
        })
    return concepts


def parse_card_for_binding(path: Path) -> dict:
    """Extract illustrates_concept and structural_core from a card."""
    text = path.read_text(encoding="utf-8")
    card = {"_path": str(path), "_text": text}

    fm = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not fm:
        return card
    fm_text = fm.group(1)

    # concept_id from nested illustrates: structure
    cid_match = re.search(r'concept_id:\s*(\S+)', fm_text)
    if cid_match:
        card["current_concept_id"] = cid_match.group(1).strip().strip('"').strip("'")

    # concept_description from nested or flat
    desc_match = re.search(r'concept_description:\s*"([^"]+)"', fm_text)
    if not desc_match:
        desc_match = re.search(r'illustrates_concept:\s*"([^"]+)"', fm_text)
    card["concept_desc"] = desc_match.group(1).strip() if desc_match else ""

    sc_match = re.search(r'structural_core:\s*"([^"]+)"', fm_text)
    card["structural_core"] = sc_match.group(1).strip() if sc_match else ""

    tt_match = re.search(r'trope_type:\s*(\S+)', fm_text)
    card["trope_type"] = tt_match.group(1).strip() if tt_match else ""

    id_match = re.search(r'^id:\s*(\S+)', fm_text, re.MULTILINE)
    card["id"] = id_match.group(1).strip() if id_match else path.stem

    return card


def llm_bind_concept(card: dict, concepts: list[dict]) -> str:
    """Ask LLM to pick best matching concept_id for a card."""
    # Build compact concept index
    index_lines = []
    for c in concepts:
        line = f"{c['id']} | {c['name']}"
        if c['summary']:
            line += f" — {c['summary'][:80]}"
        index_lines.append(line)
    concept_index = "\n".join(index_lines)

    prompt = f"""Для риторической иллюстрации подбери наиболее подходящий концепт из каталога PACK-personal.

Иллюстрация:
- Что иллюстрирует: {card.get('concept_desc', '')}
- Structural core: {card.get('structural_core', '')}
- Тип тропа: {card.get('trope_type', '')}

Каталог концептов PACK-personal (id | название | описание):
{concept_index}

Правила:
- Выведи ТОЛЬКО ID концепта (например: PD.CHR.002 или PD.ROLE.001), без пояснений
- Если ни один концепт не подходит — выведи: NONE
- Если карточка иллюстрирует общий принцип/метод без чёткой привязки к одному концепту — выведи: NONE"""

    cmd = ["claude", "-p", prompt, "--model", CLAUDE_MODEL, "--output-format", "text"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        result = r.stdout.strip()
        # Extract just the ID
        m = re.search(r'\b(PD\.[A-Z]+(?:\.[A-Z]+)?\.\d{3}(?:[a-zA-Z\-]+)?)\b', result)
        if m:
            return m.group(1)
        if "NONE" in result.upper():
            return "NONE"
        return ""
    except Exception as e:
        print(f"  [WARN] LLM bind failed: {e}", file=sys.stderr)
        return ""


def update_card_concept_id(path: Path, new_concept_id: str, concept_name: str = "") -> bool:
    """Update concept_id in card frontmatter."""
    text = path.read_text(encoding="utf-8")
    new_text = re.sub(
        r'(concept_id:\s*)\S+',
        rf'\g<1>{new_concept_id}',
        text,
        count=1
    )
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Limit cards processed (0=all)")
    args = parser.parse_args()

    print("[concept-binder] Indexing PACK-personal concepts...")
    concepts = index_concepts()
    print(f"  {len(concepts)} concepts loaded")

    # Find cards with TBD concept_id
    cards = []
    for p in ILLUSTRATIONS_DIR.rglob("RHE.ILL.*.md"):
        c = parse_card_for_binding(p)
        if c.get("current_concept_id") == "TBD":
            cards.append(c)

    print(f"[concept-binder] {len(cards)} cards need binding")
    if args.limit:
        cards = cards[:args.limit]
        print(f"  limited to {len(cards)} for this run")

    bound = 0
    none = 0
    failed = 0

    for c in cards:
        card_id = c.get("id", "?")
        desc = c.get("concept_desc", "")[:60]
        print(f"  {card_id}: {desc}...", end=" ", flush=True)

        if not c.get("concept_desc") and not c.get("structural_core"):
            print("no content to bind")
            failed += 1
            continue

        match = llm_bind_concept(c, concepts)
        if not match:
            print("LLM error")
            failed += 1
            continue

        if match == "NONE":
            print("NONE (no match)")
            none += 1
            continue

        # Verify the matched ID exists in our index
        valid_ids = {co["id"] for co in concepts}
        if match not in valid_ids:
            print(f"hallucinated ID {match}")
            failed += 1
            continue

        print(f"→ {match}")
        if not args.dry_run:
            update_card_concept_id(Path(c["_path"]), match)
            bound += 1

    print(f"\n[concept-binder] {'[DRY-RUN] Would bind' if args.dry_run else 'Bound'}: {bound}")
    print(f"  NONE (no match): {none}")
    print(f"  Failed/error: {failed}")


if __name__ == "__main__":
    main()
