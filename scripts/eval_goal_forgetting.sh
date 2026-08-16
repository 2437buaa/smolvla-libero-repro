#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 CHECKPOINT_PATH" >&2
  exit 2
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECKPOINT_PATH="$1"
if [[ "${CHECKPOINT_PATH}" != /* ]]; then
  CHECKPOINT_PATH="${PROJECT_ROOT}/${CHECKPOINT_PATH}"
fi
if [[ ! -d "${CHECKPOINT_PATH}" ]]; then
  echo "Checkpoint directory not found: ${CHECKPOINT_PATH}" >&2
  exit 1
fi

# Tasks 2 and 4 were already evaluated as neighboring-task controls.
TASKS=(0 1 5 6 7 8 9)

for task_id in "${TASKS[@]}"; do
  run_name="goal_forgetting_r4_task-${task_id}_seed-0"
  log_path="${PROJECT_ROOT}/outputs/eval/${run_name}/run.log"
  if [[ -f "${log_path}" ]] && grep -q "End of eval" "${log_path}"; then
    echo "[skip] completed: ${run_name}"
    continue
  fi

  echo "[run] ${run_name}"
  bash "${PROJECT_ROOT}/scripts/eval_checkpoint.sh" \
    "${CHECKPOINT_PATH}" libero_goal "${task_id}" 10 0 "${run_name}"
done

echo "All missing non-target Goal evaluations completed."
echo "Summarize with: python scripts/summarize_goal_forgetting.py"
