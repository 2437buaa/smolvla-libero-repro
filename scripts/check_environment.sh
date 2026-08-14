#!/usr/bin/env bash
set -euo pipefail

echo "Python: $(python --version 2>&1)"
echo "LeRobot CLI: $(command -v lerobot-eval)"

MUJOCO_GL=osmesa PYOPENGL_PLATFORM=osmesa python - <<'PY'
import torch
import mujoco
import lerobot

print("torch:", torch.__version__)
print("cuda runtime:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0))
    print("vram GiB:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2))
print("mujoco:", mujoco.__version__)
print("lerobot:", getattr(lerobot, "__version__", "source install"))
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
