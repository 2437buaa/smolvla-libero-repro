#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

bash scripts/check_environment.sh

echo "Starting one closed-loop episode (libero_spatial/task_0, seed 1000)."
echo "The first run may download model files."
HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-0}" \
  bash scripts/eval_one.sh libero_spatial 0 1 1000

