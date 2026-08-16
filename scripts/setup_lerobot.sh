#!/usr/bin/env bash
set -euo pipefail

LEROBOT_COMMIT="6adf51511b7625090eade8d82d9f61a1846ebe56"
LEROBOT_DIR="${LEROBOT_DIR:-${HOME}/projects/lerobot-smolvla-libero}"
PYTORCH_INDEX_URL="${PYTORCH_INDEX_URL:-https://download.pytorch.org/whl/cu128}"

python - <<'PY'
import sys

if sys.version_info[:2] != (3, 12):
    raise SystemExit(
        f"Python 3.12 is required; current interpreter is {sys.version.split()[0]}"
    )
print("Python:", sys.version.split()[0])
PY

python -m pip install --upgrade \
  --timeout 600 --resume-retries 20 \
  pip setuptools wheel "httpx[socks]" PySocks socksio huggingface_hub

python -m pip install \
  --timeout 600 --resume-retries 20 \
  --index-url "${PYTORCH_INDEX_URL}" \
  "torch==2.11.0+cu128" \
  "torchvision==0.26.0+cu128"

if [[ -e "${LEROBOT_DIR}" ]]; then
  if [[ ! -d "${LEROBOT_DIR}/.git" ]]; then
    echo "ERROR: ${LEROBOT_DIR} exists but is not a Git checkout." >&2
    echo "Choose another path with LEROBOT_DIR=/new/path." >&2
    exit 1
  fi
  CURRENT_COMMIT="$(git -C "${LEROBOT_DIR}" rev-parse HEAD)"
  if [[ "${CURRENT_COMMIT}" != "${LEROBOT_COMMIT}" ]]; then
    echo "ERROR: existing LeRobot checkout is at ${CURRENT_COMMIT}." >&2
    echo "Expected ${LEROBOT_COMMIT}. Use a new LEROBOT_DIR to avoid overwriting it." >&2
    exit 1
  fi
else
  mkdir -p "$(dirname "${LEROBOT_DIR}")"
  git clone https://github.com/huggingface/lerobot.git "${LEROBOT_DIR}"
  git -C "${LEROBOT_DIR}" checkout --detach "${LEROBOT_COMMIT}"
fi

python -m pip install \
  --timeout 600 --resume-retries 20 \
  -e "${LEROBOT_DIR}[libero,smolvla,peft]"

python -m pip install \
  --timeout 600 --resume-retries 20 \
  "mujoco==3.8.1" \
  "peft==0.20.0" \
  "datasets==4.8.5" \
  "accelerate==1.14.0"

python -m pip check
echo "LeRobot source: ${LEROBOT_DIR}"
echo "LeRobot commit: $(git -C "${LEROBOT_DIR}" rev-parse HEAD)"
echo "Python environment: OK"
