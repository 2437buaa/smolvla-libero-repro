#!/usr/bin/env python3
"""Download the complete LeRobot-format LIBERO training dataset."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


REPO_ID = "lerobot/libero"
REVISION = "a1aaacb"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.home() / "datasets" / "lerobot" / "libero",
    )
    parser.add_argument("--max-workers", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "600")
    os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "600")

    from huggingface_hub import snapshot_download

    print("Downloading training dataset to:", root)
    snapshot_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        revision=REVISION,
        local_dir=root,
        max_workers=args.max_workers,
    )

    info_path = root / "meta" / "info.json"
    if not info_path.is_file():
        raise SystemExit(f"Dataset metadata is missing: {info_path}")
    info = json.loads(info_path.read_text(encoding="utf-8"))
    print("codebase_version:", info.get("codebase_version"))
    print("episodes:", info.get("total_episodes"))
    print("frames:", info.get("total_frames"))
    print("tasks:", info.get("total_tasks"))
    print("dataset revision:", REVISION)
    print("Dataset download: OK")


if __name__ == "__main__":
    main()
