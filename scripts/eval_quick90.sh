#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SEED="${1:-10}"

for suite in libero_spatial libero_object libero_goal; do
  for task_id in $(seq 0 9); do
    bash "${PROJECT_ROOT}/scripts/eval_one.sh" "${suite}" "${task_id}" 3 "${SEED}"
  done
done
