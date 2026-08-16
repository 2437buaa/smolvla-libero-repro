#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path


def parse_successes(path: Path) -> list[bool]:
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(errors="replace")
    if "End of eval" not in text:
        raise RuntimeError(f"Evaluation is incomplete: {path}")
    matches = re.findall(r"'successes': \[([^\]]*)\]", text)
    if not matches:
        raise RuntimeError(f"No successes found: {path}")
    values = re.findall(r"True|False", matches[-1])
    if len(values) != 10:
        raise RuntimeError(f"Expected 10 episodes in {path}, found {len(values)}")
    return [value == "True" for value in values]


def exact_mcnemar_p(gains: int, losses: int) -> float:
    n = gains + losses
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(min(gains, losses) + 1))
    return min(1.0, 2.0 * tail / (2**n))


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    outputs = root / "outputs" / "eval"
    prior = json.loads((root / "results" / "task3_lora_results.json").read_text())
    saved_controls = {
        int(item["task_id"]): item["lora_r4_1ep"]["successful_episode_indices"]
        for item in prior["neighbor_task_controls"]
    }

    rows = []
    for task_id in range(10):
        base = parse_successes(
            outputs / f"libero_goal_task-{task_id}_n-10_seed-0" / "run.log"
        )
        if task_id == 3:
            r4 = parse_successes(outputs / "lora_task3_r4_1ep_bs4" / "run.log")
        elif task_id in saved_controls:
            indices = set(saved_controls[task_id])
            r4 = [index in indices for index in range(10)]
        else:
            r4 = parse_successes(
                outputs / f"goal_forgetting_r4_task-{task_id}_seed-0" / "run.log"
            )
        rows.append({
            "task_id": task_id,
            "role": "target" if task_id == 3 else "control",
            "episodes": 10,
            "base_successes": sum(base),
            "r4_successes": sum(r4),
            "delta_successes": sum(r4) - sum(base),
            "base_success_indices": [i for i, value in enumerate(base) if value],
            "r4_success_indices": [i for i, value in enumerate(r4) if value],
            "base_failure_to_r4_success": sum(not a and b for a, b in zip(base, r4)),
            "base_success_to_r4_failure": sum(a and not b for a, b in zip(base, r4)),
        })

    controls = [row for row in rows if row["role"] == "control"]
    gains = sum(row["base_failure_to_r4_success"] for row in controls)
    losses = sum(row["base_success_to_r4_failure"] for row in controls)
    control_summary = {
        "tasks": 9,
        "episodes_per_model": 90,
        "base_successes": sum(row["base_successes"] for row in controls),
        "r4_successes": sum(row["r4_successes"] for row in controls),
        "base_failure_to_r4_success": gains,
        "base_success_to_r4_failure": losses,
        "mcnemar_exact_two_sided_p": exact_mcnemar_p(gains, losses),
    }
    control_summary["base_rate_percent"] = 100 * control_summary["base_successes"] / 90
    control_summary["r4_rate_percent"] = 100 * control_summary["r4_successes"] / 90
    control_summary["difference_percentage_points"] = (
        control_summary["r4_rate_percent"] - control_summary["base_rate_percent"]
    )
    result = {
        "suite": "libero_goal",
        "seed": 0,
        "per_task": rows,
        "non_target_control_aggregate": control_summary,
        "full_suite": {
            "episodes_per_model": 100,
            "base_successes": sum(row["base_successes"] for row in rows),
            "r4_successes": sum(row["r4_successes"] for row in rows),
        },
    }

    results_dir = root / "results"
    json_path = results_dir / "goal_forgetting_summary.json"
    csv_path = results_dir / "goal_forgetting_summary.csv"
    json_path.write_text(json.dumps(result, indent=2) + "\n")
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({
                **row,
                "base_success_indices": json.dumps(row["base_success_indices"]),
                "r4_success_indices": json.dumps(row["r4_success_indices"]),
            })

    print("Per-task base -> r4:")
    for row in rows:
        print(f"  task_{row['task_id']}: {row['base_successes']}/10 -> {row['r4_successes']}/10 ({row['delta_successes']:+d})")
    print("non-target controls:")
    print(f"  base: {control_summary['base_successes']}/90 ({control_summary['base_rate_percent']:.1f}%)")
    print(f"  r4:   {control_summary['r4_successes']}/90 ({control_summary['r4_rate_percent']:.1f}%)")
    print(f"  difference: {control_summary['difference_percentage_points']:+.1f} pp")
    print(f"  transitions: gain={gains}, loss={losses}")
    print(f"  exact McNemar p={control_summary['mcnemar_exact_two_sided_p']:.6f}")
    print(f"wrote: {csv_path}")
    print(f"wrote: {json_path}")


if __name__ == "__main__":
    main()
