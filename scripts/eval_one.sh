#!/usr/bin/env bash
set -euo pipefail

SUITE="${1:-libero_spatial}"
TASK_ID="${2:-0}"
EPISODES="${3:-1}"
SEED="${4:-1000}"

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
RUN_NAME="${SUITE}_task-${TASK_ID}_n-${EPISODES}_seed-${SEED}"
OUTPUT_DIR="${PROJECT_ROOT}/outputs/eval/${RUN_NAME}"
mkdir -p "${OUTPUT_DIR}"

export MUJOCO_GL=osmesa
export PYOPENGL_PLATFORM=osmesa
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-0}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"

echo "Run: ${RUN_NAME}"
echo "Output: ${OUTPUT_DIR}"

set -o pipefail
lerobot-eval \
  --policy.path=HuggingFaceVLA/smolvla_libero \
  --env.type=libero \
  --env.task="${SUITE}" \
  --env.task_ids="[${TASK_ID}]" \
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
