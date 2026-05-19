#!/usr/bin/env python3
"""
rhetoric-miner.py — M-RM: ретроспективный майнинг иллюстраций из корпуса клуба.

# see DP.SC.149, DP.AISYS.013 §4.9 (M-RM)

Usage:
    # Режим topics (рекомендуемый) — отбор по вовлечённости за всё время:
    python3 rhetoric-miner.py --source club --mode topics
    python3 rhetoric-miner.py --source club --mode topics --dry-run

    # Режим posts (устаревший) — хронологическая пагинация с 2026:
    python3 rhetoric-miner.py --source club --mode posts --since 2026-01-01

    python3 rhetoric-miner.py --source guide --file path/to/guide.md

Checkpoint:
    .checkpoint-topics.json        — режим topics
    .checkpoint-club-YYYY-MM-DD.json — режим posts

Topic filter  : views >= 100 OR like_count >= 1 OR posts_count >= 15
Post filter   : like_count >= 1 OR quote_count >= 1 OR incoming_link_count >= 1
Output:
    active (quality_score >= 0.6) → illustrations/{type}/RHE.ILL.NNN-{slug}.md
    draft  (quality_score <  0.6) → illustrations/pending/RHE.ILL.NNN-{slug}.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, date
from pathlib import Path
from typing import Optional

# ── Config ────────────────────────────────────────────────────────────────────

PACK_RHETORIC_DIR = Path(__file__).parent.parent
ILLUSTRATIONS_DIR = PACK_RHETORIC_DIR / "illustrations"
PROMPTS_DIR = Path(__file__).parent / "prompts"
CHECKPOINT_DIR = Path(__file__).parent

CLUB_BASE_URL = "https://systemsworld.club"
API_TOKEN_FILE = Path.home() / ".secrets" / "club_api_token"
RATE_LIMIT_DELAY = 1.2  # seconds between requests (≤50 req/min)
QUALITY_THRESHOLD_ACTIVE = 0.6

# Topic-mode filters
TOPIC_MIN_VIEWS = 100       # тема видна многим участникам
TOPIC_MIN_LIKES = 1         # хотя бы один лайк на тему
TOPIC_MIN_POSTS = 15        # активная дискуссия

# Post-mode filters (внутри темы)
POST_MIN_LIKES = 1          # прямой сигнал «точно подмечено»
POST_MIN_QUOTES = 1         # процитировали в другом посте
POST_MIN_INCOMING_LINKS = 1 # сослались из другого поста

# Legacy post-stream filters (режим posts)
MIN_REACTIONS = 5
MIN_COMMENTS = 3

CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # trivial extraction task
CLAUDE_TIMEOUT = 120  # seconds


# ── ID management ─────────────────────────────────────────────────────────────

def get_next_illustration_id() -> tuple[int, str]:
    """Return (next_int, 'RHE.ILL.NNN') based on existing files."""
    existing = []
    for d in ILLUSTRATIONS_DIR.rglob("RHE.ILL.*.md"):
        m = re.search(r"RHE\.ILL\.(\d+)", d.name)
        if m:
            existing.append(int(m.group(1)))
    nxt = max(existing, default=0) + 1
    return nxt, f"RHE.ILL.{nxt:03d}"


# ── Club API ───────────────────────────────────────────────────────────────────

def _api_headers() -> dict:
    token = API_TOKEN_FILE.read_text().strip() if API_TOKEN_FILE.exists() else ""
    if not token:
        raise RuntimeError(f"Club API token not found at {API_TOKEN_FILE}")
    return {"Api-Key": token, "Api-Username": "system"}


def fetch_posts_page(page: int) -> list[dict]:
    """Fetch one page of /posts.json from Discourse."""
    import urllib.request
    import urllib.error

    url = f"{CLUB_BASE_URL}/posts.json?page={page}"
    req = urllib.request.Request(url, headers=_api_headers())
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data.get("latest_posts", [])
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} on page {page}: {e.reason}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  Error fetching page {page}: {e}", file=sys.stderr)
        return []


def fetch_topic_posts(topic_id: int) -> list[dict]:
    """Fetch posts from a specific topic (for reaction/comment counts)."""
    import urllib.request
    url = f"{CLUB_BASE_URL}/t/{topic_id}.json"
    req = urllib.request.Request(url, headers=_api_headers())
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data.get("post_stream", {}).get("posts", [])
    except Exception:
        return []


def passes_engagement_filter(post: dict) -> bool:
    """True if post has meaningful engagement.
    /posts.json returns 'score' (Discourse composite) but not like_count.
    score ≈ likes * 3.2 + replies * 2 + reads * 0.2 (empirical Discourse formula).
    Threshold score >= 5 ≈ ~1 like + 1 reply, conservative filter.
    """
    score = post.get("score", 0) or 0
    replies = post.get("reply_count", 0) or 0
    return score >= MIN_REACTIONS or replies >= MIN_COMMENTS


def post_text(post: dict) -> str:
    """Extract plain text from post, stripping HTML tags."""
    raw = post.get("cooked", "") or post.get("raw", "")
    # Basic HTML stripping
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:4000]  # truncate to avoid context overflow


# ── Checkpoint ────────────────────────────────────────────────────────────────

def load_checkpoint(source: str, since: str) -> dict:
    cp_file = CHECKPOINT_DIR / f".checkpoint-{source}-{since}.json"
    if cp_file.exists():
        return json.loads(cp_file.read_text())
    return {"last_page": 0, "processed_post_ids": [], "cards_created": 0}


def save_checkpoint(source: str, since: str, state: dict) -> None:
    cp_file = CHECKPOINT_DIR / f".checkpoint-{source}-{since}.json"
    cp_file.write_text(json.dumps(state, indent=2, ensure_ascii=False))


# ── LLM extraction ───────────────────────────────────────────────────────────

def build_prompt(post_text_content: str, next_id: str) -> str:
    template = (PROMPTS_DIR / "extract-illustration.md").read_text()
    prompt = template.replace("{POST_TEXT}", post_text_content)
    prompt = prompt.replace("{NEXT_ILL_ID}", next_id)
    return prompt


def extract_illustrations_from_text(
    text: str, next_id: str, dry_run: bool = False
) -> list[dict]:
    """Call claude -p, parse YAML cards from output."""
    if dry_run:
        print("    [DRY-RUN] Would call claude -p for extraction")
        return []

    prompt = build_prompt(text, next_id)
    cmd = ["claude", "-p", prompt, "--model", CLAUDE_MODEL,
           "--output-format", "text"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=CLAUDE_TIMEOUT)
        output = r.stdout.strip()
    except subprocess.TimeoutExpired:
        print("    TIMEOUT waiting for claude", file=sys.stderr)
        return []
    except FileNotFoundError:
        print("    ERROR: claude CLI not found in PATH", file=sys.stderr)
        return []

    if "NO_ILLUSTRATIONS" in output:
        return []

    return parse_yaml_cards(output)


def parse_yaml_cards(output: str) -> list[dict]:
    """Parse ---separator--- delimited YAML cards from LLM output."""
    cards = []
    blocks = output.split("---separator---")
    for block in blocks:
        block = block.strip()
        if not block or not block.startswith("id:"):
            continue
        card: dict = {}
        for line in block.splitlines():
            line = line.strip()
            if ":" in line and not line.startswith(" ") and not line.startswith("-"):
                key, _, val = line.partition(":")
                card[key.strip()] = val.strip().strip('"').strip("'")
        # Handle multiline source_text (simplified)
        if "source_text" not in card:
            m = re.search(r"source_text:\s*\|\s*\n((?:  .+\n?)+)", block)
            if m:
                card["source_text"] = m.group(1).replace("  ", "").strip()
        if card.get("id") and card.get("trope_type"):
            cards.append(card)
    return cards


# ── Validation (RHE.FORM.002 check) ──────────────────────────────────────────

REQUIRED_BY_TYPE = {
    "analogy": ["structural_core", "breaks_when"],
    "case": ["structural_core", "breaks_when"],
    "metaphor": ["structural_core", "breaks_when"],
    "example": ["structural_core"],
    "counter_example": ["structural_core"],
}


def validate_card(card: dict) -> tuple[bool, list[str]]:
    """Returns (passes, list_of_issues)."""
    issues = []
    tt = card.get("trope_type", "")
    if tt not in REQUIRED_BY_TYPE:
        issues.append(f"unknown trope_type: '{tt}'")
        return False, issues

    for field in REQUIRED_BY_TYPE[tt]:
        val = card.get(field, "").strip()
        if not val or val.lower() in ("n/a", "none", "null", ""):
            issues.append(f"missing/empty required field: {field}")

    # Analogy: structural_core must not be purely attributive
    if tt == "analogy":
        sc = card.get("structural_core", "")
        attributive_patterns = [
            r"оба\s+\w+", r"both\s+\w+", r"похожи по", r"similarly \w+"
        ]
        for pat in attributive_patterns:
            if re.search(pat, sc, re.IGNORECASE):
                issues.append("structural_core appears attributive, not relational")
                break

    return len(issues) == 0, issues


# ── Card writing ──────────────────────────────────────────────────────────────

TROPE_DIRS = {
    "analogy": "analogy",
    "case": "case",
    "metaphor": "metaphor",
    "example": "example",
    "counter_example": "counter_example",
}


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text[:40]


def write_card(card: dict, origin_source: str, post_url: str = "") -> Path:
    """Write card to appropriate directory. Returns path written."""
    score = float(card.get("quality_score", 0.5))
    valid, _ = validate_card(card)
    is_active = valid and score >= QUALITY_THRESHOLD_ACTIVE

    trope_type = card.get("trope_type", "example")
    sub_dir = TROPE_DIRS.get(trope_type, "example")

    if is_active:
        out_dir = ILLUSTRATIONS_DIR / sub_dir
    else:
        out_dir = ILLUSTRATIONS_DIR / "pending"

    out_dir.mkdir(parents=True, exist_ok=True)

    card_id = card.get("id", "RHE.ILL.???")
    concept = card.get("illustrates_concept", "unknown")
    slug = slugify(concept)
    filename = f"{card_id}-{slug}.md"
    out_path = out_dir / filename

    if out_path.exists():
        return out_path  # idempotent

    content = f"""---
id: {card_id}
trope_type: {trope_type}
source_text: |
  {card.get('source_text', '').replace(chr(10), chr(10) + '  ')}
structural_core: "{card.get('structural_core', '')}"
illustrates:
  - concept_id: TBD
    concept_description: "{concept}"
    pack_ref: PACK-personal
source_domain: "{card.get('source_domain', 'unknown')}"
audience_level: {card.get('audience_level', 2)}
effect: {card.get('effect', 'explain')}
canonical: {card.get('canonical', 'false')}
breaks_when: "{card.get('breaks_when', '').replace(chr(34), '')}"
origin_source: "{origin_source}"
quality_score: {score:.2f}
status: {'active' if is_active else 'draft'}
created: {date.today().isoformat()}
---

# [{card_id}] {concept}

## Source

{card.get('source_text', '')}

## Structural Core

{card.get('structural_core', '')}

## Boundaries (breaks_when)

{card.get('breaks_when', 'See frontmatter.')}

---
*Extraction: M-RM corpus mining. concept_id TBD — requires manual binding to PACK-personal.*
"""
    out_path.write_text(content, encoding="utf-8")
    return out_path


# ── Deduplication ─────────────────────────────────────────────────────────────

def get_processed_post_ids_from_cards() -> set[int]:
    """Scan all existing illustration cards for origin_source post IDs.
    Prevents re-processing posts already mined in a previous run, regardless
    of which checkpoint file was used.
    """
    ids: set[int] = set()
    pattern = re.compile(r'origin_source:\s*"?club/t/\d+/p/(\d+)"?')
    for md_file in ILLUSTRATIONS_DIR.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
            for m in pattern.finditer(text):
                ids.add(int(m.group(1)))
        except Exception:
            pass
    return ids


# ── Topic-mode API ────────────────────────────────────────────────────────────

def fetch_topics_page(page: int, order: str = "views") -> list[dict]:
    """Fetch one page of /latest.json sorted by order."""
    import urllib.request, urllib.error
    url = f"{CLUB_BASE_URL}/latest.json?order={order}&page={page}"
    req = urllib.request.Request(url, headers=_api_headers())
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data.get("topic_list", {}).get("topics", [])
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"  429 rate limit on topics page {page}, sleeping 60s", file=sys.stderr)
            time.sleep(60)
        else:
            print(f"  HTTP {e.code} on topics page {page}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  Error fetching topics page {page}: {e}", file=sys.stderr)
        return []


def passes_topic_filter(topic: dict) -> bool:
    return (
        topic.get("views", 0) >= TOPIC_MIN_VIEWS
        or topic.get("like_count", 0) >= TOPIC_MIN_LIKES
        or topic.get("posts_count", 0) >= TOPIC_MIN_POSTS
    )


def fetch_topic_full(topic_id: int) -> dict:
    """Fetch full topic data including per-post metrics."""
    import urllib.request
    url = f"{CLUB_BASE_URL}/t/{topic_id}.json"
    req = urllib.request.Request(url, headers=_api_headers())
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  Error fetching topic {topic_id}: {e}", file=sys.stderr)
        return {}


def get_qualifying_posts_from_topic(topic_data: dict) -> list[dict]:
    """Return posts from topic that pass post-level engagement filter."""
    posts = topic_data.get("post_stream", {}).get("posts", [])
    result = []
    for p in posts:
        if (
            p.get("like_count", 0) >= POST_MIN_LIKES
            or p.get("quote_count", 0) >= POST_MIN_QUOTES
            or p.get("incoming_link_count", 0) >= POST_MIN_INCOMING_LINKS
        ):
            result.append(p)
    return result


# ── Main flows ────────────────────────────────────────────────────────────────

def mine_club_topics(dry_run: bool = False) -> dict:
    """Mine club topics sorted by views, filter by engagement.
    Двухуровневый отбор:
      1. Тема: views>=100 OR like_count>=1 OR posts_count>=15
      2. Пост внутри темы: like_count>=1 OR quote_count>=1 OR incoming_link_count>=1
    """
    cp_file = CHECKPOINT_DIR / ".checkpoint-topics.json"
    checkpoint = json.loads(cp_file.read_text()) if cp_file.exists() else {}
    start_page = checkpoint.get("last_page", 0)
    processed_topic_ids: set = set(checkpoint.get("processed_topic_ids", []))
    processed_post_ids: set = get_processed_post_ids_from_cards()

    stats = {
        "topics_scanned": 0, "topics_qualified": 0,
        "posts_qualified": 0, "cards_created": 0, "cards_pending": 0,
    }

    print(f"[M-RM] Club topics mining (views-sorted), start page {start_page}")
    print(f"  [dedup] {len(processed_post_ids)} post IDs already in cards")
    page = start_page

    while True:
        print(f"  Topics page {page}...", end=" ", flush=True)
        topics = fetch_topics_page(page, order="views")
        time.sleep(RATE_LIMIT_DELAY)

        if not topics:
            print("(empty, done)")
            break

        qualified = [t for t in topics if passes_topic_filter(t)]
        stats["topics_scanned"] += len(topics)
        print(f"{len(topics)} topics, {len(qualified)} qualified")

        for topic in qualified:
            tid = topic["id"]
            if tid in processed_topic_ids:
                continue

            title = topic.get("title", "?")
            views = topic.get("views", 0)
            likes = topic.get("like_count", 0)
            posts_count = topic.get("posts_count", 0)
            print(f"    [{tid}] views={views} likes={likes} posts={posts_count} — {title[:55]}")

            topic_data = fetch_topic_full(tid)
            time.sleep(RATE_LIMIT_DELAY)

            if not topic_data:
                processed_topic_ids.add(tid)
                continue

            qualifying_posts = get_qualifying_posts_from_topic(topic_data)
            stats["topics_qualified"] += 1

            for post in qualifying_posts:
                pid = post.get("id")
                if pid in processed_post_ids:
                    continue

                text = post_text(post)
                if len(text) < 80:
                    processed_post_ids.add(pid)
                    continue

                stats["posts_qualified"] += 1
                origin = f"club/t/{tid}/p/{pid}"
                nxt_int, nxt_id = get_next_illustration_id()
                likes_p = post.get("like_count", 0)
                quotes_p = post.get("quote_count", 0)
                links_p = post.get("incoming_link_count", 0)
                print(f"      post/{pid} likes={likes_p} quotes={quotes_p} links={links_p} ({len(text)} chars)")

                cards = extract_illustrations_from_text(text, nxt_id, dry_run=dry_run)
                time.sleep(0.5)

                for card in cards:
                    out_path = write_card(card, origin_source=origin)
                    is_active = "pending" not in str(out_path)
                    if is_active:
                        stats["cards_created"] += 1
                        print(f"        ✅ {out_path.name}")
                    else:
                        stats["cards_pending"] += 1
                        print(f"        📋 {out_path.name} (pending)")

                processed_post_ids.add(pid)

            processed_topic_ids.add(tid)

        # Checkpoint every page (skip in dry-run to avoid poisoning state)
        if not dry_run:
            cp_file.write_text(json.dumps({
                "last_page": page + 1,
                "processed_topic_ids": list(processed_topic_ids),
            }, indent=2))

        page += 1

    return stats


def mine_club(since_date: str, dry_run: bool = False) -> dict:
    """Mine club posts since given date. Returns stats dict."""
    since_dt = datetime.strptime(since_date, "%Y-%m-%d")
    checkpoint = load_checkpoint("club", since_date)
    # Merge checkpoint IDs with IDs already present in written cards
    card_ids = get_processed_post_ids_from_cards()
    processed_ids: set = set(checkpoint.get("processed_post_ids", [])) | card_ids
    print(f"  [dedup] {len(card_ids)} post IDs already in cards — will skip")
    cards_created = checkpoint.get("cards_created", 0)
    start_page = checkpoint.get("last_page", 0)

    stats = {"posts_scanned": 0, "posts_filtered": 0, "cards_created": 0,
             "cards_pending": 0, "cards_skipped": 0}

    print(f"[M-RM] Club mining since {since_date}, starting page {start_page}")
    page = start_page

    while True:
        print(f"  Page {page}...", end=" ", flush=True)
        posts = fetch_posts_page(page)
        time.sleep(RATE_LIMIT_DELAY)

        if not posts:
            print("(empty, done)")
            break

        # Filter by date
        page_posts_in_range = []
        any_before_since = False
        for post in posts:
            created = post.get("created_at", "")
            if created:
                try:
                    post_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    if post_dt.replace(tzinfo=None) < since_dt:
                        any_before_since = True
                        continue
                except Exception:
                    pass
            page_posts_in_range.append(post)

        print(f"{len(page_posts_in_range)} in range", end=" ", flush=True)
        stats["posts_scanned"] += len(page_posts_in_range)

        for post in page_posts_in_range:
            pid = post.get("id")
            if pid in processed_ids:
                stats["cards_skipped"] += 1
                continue

            if not passes_engagement_filter(post):
                processed_ids.add(pid)
                continue

            text = post_text(post)
            if len(text) < 100:  # too short
                processed_ids.add(pid)
                continue

            stats["posts_filtered"] += 1
            topic_id = post.get("topic_id", 0)
            origin = f"club/t/{topic_id}/p/{pid}"

            # Determine next ID
            nxt_int, nxt_id = get_next_illustration_id()
            print(f"\n    [{nxt_id}] topic={topic_id} post={pid} ({len(text)} chars)")

            cards = extract_illustrations_from_text(text, nxt_id, dry_run=dry_run)
            time.sleep(0.5)

            for card in cards:
                out_path = write_card(card, origin_source=origin)
                is_active = "pending" not in str(out_path)
                if is_active:
                    stats["cards_created"] += 1
                    cards_created += 1
                    print(f"      ✅ {out_path.name}")
                else:
                    stats["cards_pending"] += 1
                    print(f"      📋 {out_path.name} (pending)")

            processed_ids.add(pid)

        # Save checkpoint every page
        save_checkpoint("club", since_date, {
            "last_page": page + 1,
            "processed_post_ids": list(processed_ids),
            "cards_created": cards_created,
        })

        if any_before_since:
            print("  (reached posts before since_date, stopping)")
            break

        page += 1

    return stats


def mine_guide(file_path: str, dry_run: bool = False) -> dict:
    """Mine a single guide file."""
    path = Path(file_path)
    if not path.exists():
        print(f"ERROR: file not found: {file_path}", file=sys.stderr)
        return {}

    text = path.read_text(encoding="utf-8")
    print(f"[M-RM] Guide mining: {path.name} ({len(text)} chars)")

    nxt_int, nxt_id = get_next_illustration_id()
    cards = extract_illustrations_from_text(text[:6000], nxt_id, dry_run=dry_run)

    stats = {"cards_created": 0, "cards_pending": 0}
    for card in cards:
        out_path = write_card(card, origin_source=f"guide:{path.name}")
        if "pending" not in str(out_path):
            stats["cards_created"] += 1
            print(f"  ✅ {out_path.name}")
        else:
            stats["cards_pending"] += 1
            print(f"  📋 {out_path.name} (pending)")

    return stats


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="M-RM: rhetoric corpus miner")
    parser.add_argument("--source", choices=["club", "guide"], default="club")
    parser.add_argument("--mode", choices=["topics", "posts"], default="topics",
                        help="topics=engagement-sorted (recommended); posts=chronological legacy")
    parser.add_argument("--since", default="2026-01-01",
                        help="ISO date cutoff for --mode posts")
    parser.add_argument("--file", help="Guide file path (for --source guide)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Scan and filter without calling LLM")
    args = parser.parse_args()

    started = datetime.now()

    if args.source == "club":
        if args.mode == "topics":
            stats = mine_club_topics(dry_run=args.dry_run)
        else:
            stats = mine_club(args.since, dry_run=args.dry_run)
    elif args.source == "guide":
        if not args.file:
            print("ERROR: --file required for --source guide", file=sys.stderr)
            sys.exit(1)
        stats = mine_guide(args.file, dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)

    elapsed = (datetime.now() - started).total_seconds()
    print(f"\n[M-RM] Done in {elapsed:.0f}s")
    print(f"  Stats: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    main()
