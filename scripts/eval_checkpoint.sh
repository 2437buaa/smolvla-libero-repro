#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 6 ]]; then
  echo "Usage: $0 POLICY_PATH [SUITE] [TASK_IDS] [EPISODES] [SEED] [RUN_NAME]" >&2
  echo "Example task IDs: 3 or 2,4" >&2
  exit 2
fi

POLICY_PATH="$1"
SUITE="${2:-libero_goal}"
TASK_IDS="${3:-3}"
EPISODES="${4:-10}"
SEED="${5:-0}"
RUN_NAME="${6:-checkpoint_${SUITE}_tasks-${TASK_IDS//,/-}_n-${EPISODES}_seed-${SEED}}"

case "${SUITE}" in
  libero_spatial|libero_object) HORIZON=280 ;;
  libero_goal) HORIZON=300 ;;
  libero_10) HORIZON=520 ;;
  *)
    echo "Unsupported suite: ${SUITE}" >&2
    exit 2
    ;;
esac

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_ROOT}/outputs/eval/${RUN_NAME}"
mkdir -p "${OUTPUT_DIR}"
cd "${PROJECT_ROOT}"

export MUJOCO_GL=osmesa
export PYOPENGL_PLATFORM=osmesa
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-0}"
export TOKENIZERS_PARALLELISM="${TOKENIZERS_PARALLELISM:-false}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"

echo "Run: ${RUN_NAME}"
echo "Policy: ${POLICY_PATH}"
echo "Output: ${OUTPUT_DIR}"

set -o pipefail
lerobot-eval \
  --policy.path="${POLICY_PATH}" \
  --policy.device=cuda \
  --env.type=libero \
  --env.task="${SUITE}" \
  --env.task_ids="[${TASK_IDS}]" \
  --env.episode_length="${HORIZON}" \
  --env.max_parallel_tasks=1 \
  --eval.batch_size=1 \
  --eval.n_episodes="${EPISODES}" \
  --eval.use_async_envs=false \
  --eval.recording=false \
  --seed="${SEED}" \
  --job_name="${RUN_NAME}" \
  --output_dir="${OUTPUT_DIR}" \
  2>&1 | tee "${OUTPUT_DIR}/run.log"
