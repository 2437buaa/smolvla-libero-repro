#!/usr/bin/env python3
"""Verify and decode the LIBERO Goal task-3 subset used for LoRA training."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("ARROW_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import pyarrow.compute as pc
import pyarrow.parquet as pq


TARGET = "open the top drawer and put the bowl inside"


def find_task_index(root: Path) -> int:
    rows = pq.read_table(root / "meta/tasks.parquet", use_threads=False).to_pylist()
    matches = [row for row in rows if TARGET in row.values()]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one task match, found {len(matches)}: {matches}")
    return int(matches[0]["task_index"])


def find_episodes(root: Path, task_index: int) -> tuple[list[int], int]:
    episodes: set[int] = set()
    frames = 0
    files = sorted(root.glob("data/chunk-*/*.parquet"))
    if not files:
        raise FileNotFoundError(f"No data Parquet files under {root}")

    for path in files:
        table = pq.read_table(
            path,
            columns=["episode_index", "task_index"],
            use_threads=False,
        )
        selected = table.filter(pc.equal(table["task_index"], task_index))
        frames += selected.num_rows
        episodes.update(selected["episode_index"].combine_chunks().to_pylist())
    return sorted(episodes), frames


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="Local root of lerobot/libero")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()

    task_index = find_task_index(root)
    episodes, frames = find_episodes(root, task_index)

    print(f"task: {TARGET}")
    print(f"task_index: {task_index}")
    print(f"episodes: {len(episodes)}")
    print(f"frames: {frames}")
    print(f"episode_list: {episodes}")

    if len(episodes) != 36 or frames != 7157:
        raise RuntimeError("Target subset does not match the verified 36 episodes / 7157 frames")

    from lerobot.datasets.lerobot_dataset import LeRobotDataset

    dataset = LeRobotDataset(repo_id="lerobot/libero", root=root, episodes=episodes)
    sample = dataset[0]
    print("decoded_sample:")
    for key, value in sample.items():
        shape = tuple(value.shape) if hasattr(value, "shape") else repr(value)
        print(f"  {key}: {shape}")


if __name__ == "__main__":
    main()
