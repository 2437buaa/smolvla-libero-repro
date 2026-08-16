#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path


DEFAULT_SEEDS = [0, 20, 30, 40, 50]


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Summarize paired base-vs-LoRA LIBERO Goal task-3 evaluations."
    )
    parser.add_argument("--project-root", type=Path, default=project_root)
    parser.add_argument("--seeds", type=int, nargs="+", default=DEFAULT_SEEDS)
    return parser.parse_args()


def log_path(project_root: Path, model: str, seed: int) -> Path:
    historical = {
        ("base", 0): "libero_goal_task-3_n-10_seed-0",
        ("r4", 0): "lora_task3_r4_1ep_bs4",
        ("base", 20): "holdout_seed20_base_task3",
        ("r4", 20): "holdout_seed20_r4_task3",
    }
    run_name = historical.get((model, seed), f"task3_multiseed_{model}_seed-{seed}")
    return project_root / "outputs" / "eval" / run_name / "run.log"


def parse_successes(path: Path) -> list[bool]:
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(errors="replace")
    if "End of eval" not in text:
        raise RuntimeError(f"Evaluation is incomplete: {path}")
    matches = re.findall(r"'successes': \[([^\]]*)\]", text)
    if not matches:
        raise RuntimeError(f"No per-episode successes found: {path}")
    values = re.findall(r"True|False", matches[-1])
    if len(values) != 10:
        raise RuntimeError(f"Expected 10 episodes in {path}, found {len(values)}")
    return [value == "True" for value in values]


def wilson_interval(successes: int, episodes: int, z: float = 1.959963984540054) -> tuple[float, float]:
    proportion = successes / episodes
    denominator = 1 + z * z / episodes
    center = (proportion + z * z / (2 * episodes)) / denominator
    margin = z * math.sqrt(
        proportion * (1 - proportion) / episodes + z * z / (4 * episodes * episodes)
    ) / denominator
    return center - margin, center + margin


def exact_mcnemar_p(gains: int, losses: int) -> float:
    discordant = gains + losses
    if discordant == 0:
        return 1.0
    tail = sum(math.comb(discordant, k) for k in range(min(gains, losses) + 1))
    return min(1.0, 2.0 * tail / (2**discordant))


def summarize(rows: list[dict[str, object]], seeds: set[int]) -> dict[str, object]:
    selected = [row for row in rows if int(row["seed"]) in seeds]
    episodes = sum(int(row["episodes"]) for row in selected)
    base_successes = sum(int(row["base_successes"]) for row in selected)
    r4_successes = sum(int(row["r4_successes"]) for row in selected)
    gains = sum(int(row["base_failure_to_r4_success"]) for row in selected)
    losses = sum(int(row["base_success_to_r4_failure"]) for row in selected)
    base_ci = wilson_interval(base_successes, episodes)
    r4_ci = wilson_interval(r4_successes, episodes)
    return {
        "seeds": sorted(seeds),
        "episodes_per_model": episodes,
        "base": {
            "successes": base_successes,
            "rate_percent": 100 * base_successes / episodes,
            "wilson_95_percent": [100 * base_ci[0], 100 * base_ci[1]],
        },
        "r4": {
            "successes": r4_successes,
            "rate_percent": 100 * r4_successes / episodes,
            "wilson_95_percent": [100 * r4_ci[0], 100 * r4_ci[1]],
        },
        "paired_difference_percentage_points": 100 * (r4_successes - base_successes) / episodes,
        "base_failure_to_r4_success": gains,
        "base_success_to_r4_failure": losses,
        "mcnemar_exact_two_sided_p": exact_mcnemar_p(gains, losses),
    }


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    seeds = list(dict.fromkeys(args.seeds))
    rows: list[dict[str, object]] = []

    for seed in seeds:
        base = parse_successes(log_path(project_root, "base", seed))
        r4 = parse_successes(log_path(project_root, "r4", seed))
        rows.append(
            {
                "seed": seed,
                "episodes": len(base),
                "base_successes": sum(base),
                "r4_successes": sum(r4),
                "base_success_indices": [i for i, success in enumerate(base) if success],
                "r4_success_indices": [i for i, success in enumerate(r4) if success],
                "base_failure_to_r4_success": sum(not a and b for a, b in zip(base, r4)),
                "base_success_to_r4_failure": sum(a and not b for a, b in zip(base, r4)),
            }
        )

    result = {
        "task": "libero_goal/task_3",
        "episodes_per_seed_per_model": 10,
        "per_seed": rows,
        "heldout": summarize(rows, set(seeds) - {0}),
        "all_reported_seeds": summarize(rows, set(seeds)),
        "notes": [
            "Seed 0 was used during model selection and is excluded from the held-out aggregate.",
            "The exact McNemar test uses paired per-episode binary outcomes.",
            "Wilson intervals describe each model rate; they are not paired-difference intervals.",
        ],
    }

    results_dir = project_root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    json_path = results_dir / "task3_multiseed_summary.json"
    csv_path = results_dir / "task3_multiseed_summary.csv"
    json_path.write_text(json.dumps(result, indent=2) + "\n")

    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "seed",
                "episodes",
                "base_successes",
                "r4_successes",
                "base_success_indices",
                "r4_success_indices",
                "base_failure_to_r4_success",
                "base_success_to_r4_failure",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "base_success_indices": json.dumps(row["base_success_indices"]), "r4_success_indices": json.dumps(row["r4_success_indices"])})

    for label in ("heldout", "all_reported_seeds"):
        summary = result[label]
        print(f"{label}: seeds={summary['seeds']}")
        print(
            f"  base: {summary['base']['successes']}/{summary['episodes_per_model']} "
            f"({summary['base']['rate_percent']:.1f}%)"
        )
        print(
            f"  r4:   {summary['r4']['successes']}/{summary['episodes_per_model']} "
            f"({summary['r4']['rate_percent']:.1f}%)"
        )
        print(f"  paired difference: {summary['paired_difference_percentage_points']:+.1f} pp")
        print(
            f"  paired transitions: gain={summary['base_failure_to_r4_success']}, "
            f"loss={summary['base_success_to_r4_failure']}"
        )
        print(f"  exact McNemar p={summary['mcnemar_exact_two_sided_p']:.6f}")
    print(f"wrote: {csv_path}")
    print(f"wrote: {json_path}")


if __name__ == "__main__":
    main()
