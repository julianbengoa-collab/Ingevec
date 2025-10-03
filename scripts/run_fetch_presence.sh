#!/usr/bin/env bash
set -euo pipefail

# Determine repository root (the directory of this script's parent).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "$REPO_ROOT"

python -m ingevec_presence.scripts.fetch_presence "$@"
