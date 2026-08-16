#!/usr/bin/env python3
"""Download the simulator assets required by LIBERO into its runtime folder."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


REPO_ID = "lerobot/libero-assets"
REVISION = "0b3ea86be5fe169d0fd036ae63d1070ec09e90f6"
REQUIRED_SCENE = Path("scenes/libero_tabletop_base_style.xml")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-workers", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "600")
    os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "600")

    from huggingface_hub import snapshot_download
    import libero

    package_root = Path(libero.__file__).resolve().parent
    nested_runtime = package_root / "libero" / "assets"
    assets_dir = nested_runtime if nested_runtime.parent.exists() else package_root / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    print("Downloading LIBERO assets to:", assets_dir)
    snapshot_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        revision=REVISION,
        local_dir=assets_dir,
        max_workers=args.max_workers,
    )

    required = assets_dir / REQUIRED_SCENE
    if not required.is_file():
        raise SystemExit(f"Download finished but required file is missing: {required}")
    print("Required LIBERO scene: OK")
    print("Assets revision:", REVISION)


if __name__ == "__main__":
    main()

