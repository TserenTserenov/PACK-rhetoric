#!/usr/bin/env bash
# rhetoric-miner.sh — M-RM night scheduler wrapper
#
# see DP.SC.149, DP.AISYS.013 §4.9
#
# Usage:
#   ./scripts/rhetoric-miner.sh              # topics mode (default, engagement-sorted)
#   ./scripts/rhetoric-miner.sh --dry-run    # scan without LLM
#   ./scripts/rhetoric-miner.sh --mode posts --since 2026-05-01  # legacy chronological
#
# Scheduled via:
#   launchd: com.iwe.rhetoric-miner.plist (Mac, 02:00 MSK = 23:00 UTC)
#   systemd: rhetoric-miner.timer (tsekh-1, 02:00 MSK)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
LOCK_FILE="/tmp/rhetoric-miner.lock"

mkdir -p "$LOG_DIR"

# ── Lock: prevent concurrent runs ────────────────────────────────────────────
if [ -f "$LOCK_FILE" ]; then
  LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null || echo "unknown")
  echo "[rhetoric-miner] Already running (PID $LOCK_PID). Exiting."
  exit 0
fi
echo $$ > "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE="$LOG_DIR/$(date +%Y-%m-%d).log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo ""
echo "=== rhetoric-miner $(date '+%Y-%m-%d %H:%M:%S') ==="

# ── Env check ─────────────────────────────────────────────────────────────────
# rhetoric-miner.py использует прямой /v1/messages API через ANTHROPIC_BASE_URL,
# не claude CLI (CLI 2.x несовместим с проксей по валидации моделей).
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "[ERROR] ANTHROPIC_API_KEY not set (см. EnvironmentFile=~/.iwe/.proxy-env)"
  exit 1
fi

if [ ! -f "$HOME/.secrets/club_api_token" ]; then
  echo "[ERROR] ~/.secrets/club_api_token not found"
  exit 1
fi

# ── Git pull ──────────────────────────────────────────────────────────────────
echo "[1/3] git pull PACK-rhetoric..."
cd "$PACK_DIR"
git pull --rebase origin main 2>&1 || echo "  [WARN] git pull failed, working with local copy"

# ── Mine ──────────────────────────────────────────────────────────────────────
echo "[2/3] Running M-RM miner..."
MODE="topics"
SINCE="${RHETORIC_SINCE:-2026-01-01}"
DRY_RUN_FLAG=""
for arg in "$@"; do
  case "$arg" in
    --dry-run)    DRY_RUN_FLAG="--dry-run" ;;
    --mode=*)     MODE="${arg#--mode=}" ;;
    --mode)       shift; MODE="$1" ;;
    --since=*)    SINCE="${arg#--since=}" ;;
    --since)      shift; SINCE="$1" ;;
  esac
done

python3 "$SCRIPT_DIR/rhetoric-miner.py" \
  --source club \
  --mode "$MODE" \
  --since "$SINCE" \
  $DRY_RUN_FLAG

# ── Git commit & push ─────────────────────────────────────────────────────────
echo "[3/3] Committing new illustrations..."
cd "$PACK_DIR"

if git status --short | grep -q "^[?A].*illustrations/"; then
  NEW_COUNT=$(git status --short | grep -c "^[?A].*illustrations/")
  git add illustrations/
  git commit -m "feat(M-RM): ${NEW_COUNT} new illustration cards from club mining $(date +%Y-%m-%d)"
  git push origin main
  echo "  Pushed $NEW_COUNT new cards."
else
  echo "  No new illustrations to commit."
fi

echo "=== Done ==="
