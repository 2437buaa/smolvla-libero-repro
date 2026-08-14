#!/usr/bin/env python3
"""Summarize LeRobot per-task eval logs produced by scripts/eval_one.sh."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path


def read_overall_metrics(log_path: Path) -> dict:
    candidates = []
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "'pc_success':" not in line or "'n_episodes':" not in line:
            continue
        start = line.find("{")
        if start >= 0:
            try:
                candidates.append(ast.literal_eval(line[start:]))
            except (SyntaxError, ValueError):
                pass
    if not candidates:
        raise RuntimeError(f"No metrics found in {log_path}")
    return candidates[-1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", choices=["libero_spatial", "libero_object", "libero_goal"])
    parser.add_argument("--episodes", type=int, default=3)
    parser.add_argument("--seed", type=int, default=10)
    parser.add_argument("--outputs", type=Path, default=Path("outputs/eval"))
    args = parser.parse_args()

    tasks = []
    for task_id in range(10):
        run_name = f"{args.suite}_task-{task_id}_n-{args.episodes}_seed-{args.seed}"
        metrics = read_overall_metrics(args.outputs / run_name / "run.log")
        successes = round(metrics["pc_success"] * metrics["n_episodes"] / 100)
        tasks.append(
            {
                "task_id": task_id,
                "successes": successes,
                "episodes": metrics["n_episodes"],
                "success_rate_percent": metrics["pc_success"],
            }
        )

    successes = sum(item["successes"] for item in tasks)
    episodes = sum(item["episodes"] for item in tasks)
    result = {
        "suite": args.suite,
        "seed": args.seed,
        "tasks": tasks,
        "overall": {
            "successes": successes,
            "episodes": episodes,
            "success_rate_percent": 100 * successes / episodes,
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
