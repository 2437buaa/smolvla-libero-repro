#!/usr/bin/env python3
"""Put all public model files used by this project into the HF cache."""

from __future__ import annotations

import argparse
import os


MODEL_REPOS = (
    "HuggingFaceVLA/smolvla_libero",
    "HuggingFaceTB/SmolVLM2-500M-Instruct",
    "marlon777777/smolvla-libero-task3-lora-r4",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-workers", type=int, default=1)
    args = parser.parse_args()

    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "600")
    os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "600")

    from huggingface_hub import snapshot_download

    for repo_id in MODEL_REPOS:
        print(f"Downloading model: {repo_id}")
        path = snapshot_download(repo_id=repo_id, max_workers=args.max_workers)
        print("Cached at:", path)
    print("Model cache: OK")


if __name__ == "__main__":
    main()

