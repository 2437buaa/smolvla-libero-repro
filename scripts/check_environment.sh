#!/usr/bin/env bash
set -euo pipefail

for command_name in python lerobot-eval lerobot-train ffmpeg; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "ERROR: required command not found: ${command_name}" >&2
    exit 1
  fi
done

echo "Python: $(python --version 2>&1)"
echo "Python path: $(command -v python)"
echo "LeRobot eval CLI: $(command -v lerobot-eval)"
echo "LeRobot train CLI: $(command -v lerobot-train)"

MUJOCO_GL=osmesa PYOPENGL_PLATFORM=osmesa python - <<'PY'
import sys

import torch
import torchvision
import mujoco
import lerobot
import accelerate
import datasets
import peft

expected = {
    "python": "3.12",
    "torch": "2.11.0+cu128",
    "torchvision": "0.26.0+cu128",
    "mujoco": "3.8.1",
    "lerobot": "0.6.2",
    "peft": "0.20.0",
    "datasets": "4.8.5",
    "accelerate": "1.14.0",
}
actual = {
    "python": f"{sys.version_info.major}.{sys.version_info.minor}",
    "torch": torch.__version__,
    "torchvision": torchvision.__version__,
    "mujoco": mujoco.__version__,
    "lerobot": getattr(lerobot, "__version__", "source install"),
    "peft": peft.__version__,
    "datasets": datasets.__version__,
    "accelerate": accelerate.__version__,
}

for name, expected_version in expected.items():
    value = actual[name]
    print(f"{name}: {value}")
    if value != expected_version:
        raise SystemExit(
            f"Version mismatch for {name}: expected {expected_version}, got {value}"
        )

print("cuda runtime:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())
if not torch.cuda.is_available():
    raise SystemExit("CUDA is not available to PyTorch")
print("gpu:", torch.cuda.get_device_name(0))
print("vram GiB:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2))
PY

ASSET_ROOT="$(python - <<'PY'
from pathlib import Path
import libero

root = Path(libero.__file__).resolve().parent
runtime = root / "libero" / "assets"
print(runtime if runtime.parent.exists() else root / "assets")
PY
)"

echo "LIBERO assets: ${ASSET_ROOT}"
test -f "${ASSET_ROOT}/scenes/libero_tabletop_base_style.xml"
echo "Required LIBERO scene: OK"
