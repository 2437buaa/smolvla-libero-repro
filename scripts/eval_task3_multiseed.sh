#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 CHECKPOINT_PATH [SEED ...]" >&2
  echo "Example: $0 outputs/train/task3_lora_r4_1ep_bs4/checkpoints/001790/pretrained_model 30 40 50" >&2
  exit 2
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECKPOINT_PATH="$1"
shift

if [[ "${CHECKPOINT_PATH}" != /* ]]; then
  CHECKPOINT_PATH="${PROJECT_ROOT}/${CHECKPOINT_PATH}"
fi

if [[ ! -d "${CHECKPOINT_PATH}" ]]; then
  echo "Checkpoint directory not found: ${CHECKPOINT_PATH}" >&2
  exit 1
fi

if [[ $# -gt 0 ]]; then
  SEEDS=("$@")
else
  SEEDS=(30 40 50)
fi

for seed in "${SEEDS[@]}"; do
  if [[ ! "${seed}" =~ ^[0-9]+$ ]]; then
    echo "Seed must be a non-negative integer: ${seed}" >&2
    exit 2
  fi
done

BASE_POLICY="${BASE_POLICY:-HuggingFaceVLA/smolvla_libero}"

run_eval() {
  local policy="$1"
  local model_label="$2"
  local seed="$3"
  local run_name="task3_multiseed_${model_label}_seed-${seed}"
  local log_path="${PROJECT_ROOT}/outputs/eval/${run_name}/run.log"

  if [[ -f "${log_path}" ]] && grep -q "End of eval" "${log_path}"; then
    echo "[skip] completed: ${run_name}"
    return
  fi

  echo "[run] ${run_name}"
  bash "${PROJECT_ROOT}/scripts/eval_checkpoint.sh" \
    "${policy}" \
    libero_goal \
    3 \
    10 \
    "${seed}" \
    "${run_name}"
}

echo "Project: ${PROJECT_ROOT}"
echo "Checkpoint: ${CHECKPOINT_PATH}"
echo "Seeds: ${SEEDS[*]}"

for seed in "${SEEDS[@]}"; do
  run_eval "${BASE_POLICY}" base "${seed}"
  run_eval "${CHECKPOINT_PATH}" r4 "${seed}"
done

echo "All requested evaluations completed."
echo "Summarize with: python scripts/summarize_task3_multiseed.py"
