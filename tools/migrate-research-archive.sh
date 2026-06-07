#!/usr/bin/env bash
set -euo pipefail

# Fallback local utility.
# Moves the existing TCSW research archive into the protected Weldon research layer.
# Run from the repository root on the tcsw-runtime-os branch if the GitHub API migration has not already been committed.

TARGET_DIR="00-weldon-research"

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Missing $TARGET_DIR. Create it before running this migration."
  exit 1
fi

RESEARCH_DIRS=(
  "data"
  "raw"
  "findings"
  "analysis"
  "event-ops"
  "docs"
  "scripts"
)

echo "Packaging existing research archive into $TARGET_DIR/"

for dir in "${RESEARCH_DIRS[@]}"; do
  if [[ -d "$dir" ]]; then
    if [[ -e "$TARGET_DIR/$dir" ]]; then
      echo "Skipping $dir: $TARGET_DIR/$dir already exists."
    else
      echo "Moving $dir -> $TARGET_DIR/$dir"
      git mv "$dir" "$TARGET_DIR/$dir"
    fi
  else
    echo "Skipping $dir: not found at repo root."
  fi
done

echo "\nMigration staged. Review with: git status"
echo "Expected root after migration: README.md, 00-weldon-research/, 01-runtime-os/, tools/"
