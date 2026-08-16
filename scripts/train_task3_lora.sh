#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 5 ]]; then
  echo "Usage: $0 DATASET_ROOT [RANK] [STEPS] [BATCH_SIZE] [SEED]" >&2
  exit 2
fi

DATASET_ROOT="$1"
RANK="${2:-4}"
STEPS="${3:-1790}"
BATCH_SIZE="${4:-4}"
SEED="${5:-1000}"
ALPHA="${RANK}"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_NAME="task3_lora_r${RANK}_s${STEPS}_bs${BATCH_SIZE}_seed${SEED}"
OUTPUT_DIR="${PROJECT_ROOT}/outputs/train/${RUN_NAME}"
LOG_DIR="${PROJECT_ROOT}/outputs/train_logs"
EPISODES='[382,383,387,409,414,416,449,462,465,489,494,498,523,526,534,538,548,559,560,576,594,614,624,627,684,694,701,711,737,738,742,758,762,782,784,790]'

mkdir -p "${LOG_DIR}"
cd "${PROJECT_ROOT}"

export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
export TOKENIZERS_PARALLELISM="${TOKENIZERS_PARALLELISM:-false}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"

echo "Run: ${RUN_NAME}"
echo "Dataset: ${DATASET_ROOT}"
echo "Output: ${OUTPUT_DIR}"

set -o pipefail
lerobot-train \
  --policy.path=HuggingFaceVLA/smolvla_libero \
  --policy.device=cuda \
  --policy.use_amp=true \
  --policy.push_to_hub=false \
  --dataset.repo_id=lerobot/libero \
  --dataset.root="${DATASET_ROOT}" \
  --dataset.episodes="${EPISODES}" \
  --output_dir="${OUTPUT_DIR}" \
  --job_name="${RUN_NAME}" \
  --batch_size="${BATCH_SIZE}" \
  --accelerator.gradient_accumulation.steps=1 \
  --num_workers=0 \
  --persistent_workers=false \
  --steps="${STEPS}" \
  --log_freq=50 \
  --env_eval_freq=0 \
  --eval_steps=0 \
  --save_checkpoint=true \
  --save_freq=0 \
  --wandb.enable=false \
  --seed="${SEED}" \
  --peft.method_type=LORA \
  --peft.r="${RANK}" \
  --peft.lora_alpha="${ALPHA}" \
  2>&1 | tee "${LOG_DIR}/${RUN_NAME}.log"
