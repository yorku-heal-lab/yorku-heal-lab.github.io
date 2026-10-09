#!/usr/bin/env bash
# Pull spreadsheets from Google Drive, regenerate _data/*.yml, commit and push if anything changed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="$REPO_ROOT/scripts/data"
ENV_FILE="${DRIVE_SYNC_ENV:-$SCRIPT_DIR/drive-sync.env}"
LOG_DIR="${LOG_DIR:-$SCRIPT_DIR/logs}"
LOG_FILE="$LOG_DIR/cron-sync.log"
LOCK_FILE="$SCRIPT_DIR/.cron_sync_from_drive.lock"

mkdir -p "$LOG_DIR"
# Log to file always; mirror to terminal when run interactively.
if [[ -t 1 ]]; then
  exec > >(tee -a "$LOG_FILE") 2>&1
else
  exec >>"$LOG_FILE" 2>&1
fi

on_exit() {
  local code=$?
  if (( code != 0 )); then
    echo "cron_sync_from_drive failed (exit $code). See $LOG_FILE"
  fi
}
trap on_exit EXIT

echo "=== $(date -Is) cron_sync_from_drive ==="
echo "Log file: $LOG_FILE"

export PYTHONUNBUFFERED=1

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

GIT_BRANCH="${GIT_BRANCH:-main}"
DRIVE_LINKS_YML="${DRIVE_LINKS_YML:-$SCRIPT_DIR/drive-data-links.yml}"

if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  PYTHON="${PYTHON:-$REPO_ROOT/.venv/bin/python}"
else
  PYTHON="${PYTHON:-python3}"
fi

if [[ ! -f "$DRIVE_LINKS_YML" ]]; then
  echo "ERROR: Links manifest not found: $DRIVE_LINKS_YML" >&2
  echo "Copy scripts/drive-data-links.yml.example to scripts/drive-data-links.yml and add share URLs." >&2
  exit 1
fi

if ! command -v flock >/dev/null 2>&1; then
  echo "ERROR: flock not found (install util-linux)." >&2
  exit 1
fi

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "Another sync is already running; exiting."
  exit 0
fi

DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done

cd "$REPO_ROOT"

export GIT_TERMINAL_PROMPT=0
git fetch origin "$GIT_BRANCH"
git checkout "$GIT_BRANCH"
git pull --rebase --autostash origin "$GIT_BRANCH"

echo "Pulling spreadsheets from share links ($DRIVE_LINKS_YML) -> $DATA_DIR"
PULL_OPTS=("$PYTHON" "$SCRIPT_DIR/pull_data_from_drive_links.py" --links "$DRIVE_LINKS_YML" --data-dir "$DATA_DIR")
if $DRY_RUN; then
  PULL_OPTS+=(--dry-run)
fi
"${PULL_OPTS[@]}"

if $DRY_RUN; then
  echo "Dry run: skipping sync scripts and git."
  exit 0
fi

SYNC_SCRIPTS=(
  sync_from_xlsx.py
  sync_publications_from_xlsx.py
  sync_news_from_xlsx.py
  sync_resources_from_xlsx.py
  sync_research_from_xlsx.py
)

for script in "${SYNC_SCRIPTS[@]}"; do
  echo "Running $script"
  "$PYTHON" "$SCRIPT_DIR/$script"
done

if git diff --quiet && git diff --cached --quiet && [[ -z "$(git ls-files --others --exclude-standard)" ]]; then
  echo "No changes after sync; nothing to commit."
  exit 0
fi

git add scripts/data/ _data/ assets/images/team/

if git diff --cached --quiet; then
  echo "No staged changes; nothing to commit."
  exit 0
fi

COMMIT_MSG="Auto-sync site content from Google Drive ($(date -u +%Y-%m-%dT%H:%MZ))"
git commit -m "$COMMIT_MSG"
git push origin "$GIT_BRANCH"

echo "Committed and pushed to origin/$GIT_BRANCH."
