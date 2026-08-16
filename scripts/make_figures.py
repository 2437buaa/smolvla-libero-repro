#!/usr/bin/env python3
"""Generate deterministic, dependency-free SVG figures from tracked results."""

from __future__ import annotations

import csv
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
BLUE = "#2563EB"
ORANGE = "#F97316"
INK = "#172033"
MUTED = "#667085"
GRID = "#E4E7EC"


def grouped_bars(path: Path, title: str, subtitle: str, labels: list[str], base: list[float], adapted: list[float], base_label: str, adapted_label: str) -> None:
    width, height = 920, 520
    left, right, top, bottom = 82, 28, 105, 82
    plot_w, plot_h = width - left - right, height - top - bottom
    group_w = plot_w / len(labels)
    bar_w = min(34, group_w * 0.28)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">{escape(subtitle)}</desc>',
        '<rect width="100%" height="100%" fill="#FFFFFF" rx="16"/>',
        f'<text x="{left}" y="42" font-family="sans-serif" font-size="24" font-weight="700" fill="{INK}">{escape(title)}</text>',
        f'<text x="{left}" y="70" font-family="sans-serif" font-size="14" fill="{MUTED}">{escape(subtitle)}</text>',
    ]
    for tick in range(0, 101, 20):
        y = top + plot_h * (1 - tick / 100)
        out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="{GRID}"/>')
        out.append(f'<text x="{left - 14}" y="{y + 5:.1f}" text-anchor="end" font-family="sans-serif" font-size="12" fill="{MUTED}">{tick}%</text>')
    for i, label in enumerate(labels):
        center = left + group_w * (i + 0.5)
        for offset, value, color in [(-bar_w / 2, base[i], BLUE), (bar_w / 2, adapted[i], ORANGE)]:
            value_text = f"{value:.1f}".rstrip("0").rstrip(".")
            h = plot_h * value / 100
            x = center + offset - bar_w / 2
            y = top + plot_h - h
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" rx="5" fill="{color}"/>')
            out.append(f'<text x="{x + bar_w / 2:.1f}" y="{max(top + 12, y - 7):.1f}" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="600" fill="{INK}">{value_text}%</text>')
        out.append(f'<text x="{center:.1f}" y="{top + plot_h + 27}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="{INK}">{escape(label)}</text>')
    legend_y = height - 25
    for x, color, text in [(left, BLUE, base_label), (left + 210, ORANGE, adapted_label)]:
        out.append(f'<rect x="{x}" y="{legend_y - 12}" width="14" height="14" rx="3" fill="{color}"/>')
        out.append(f'<text x="{x + 22}" y="{legend_y}" font-family="sans-serif" font-size="13" fill="{INK}">{escape(text)}</text>')
    out.append('</svg>')
    path.write_text("\n".join(out) + "\n")


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    suite_order = ["libero_spatial", "libero_object", "libero_goal"]
    benchmark_rates = []
    for filename, episode_key in [("quick90_seed10.csv", "n_episodes"), ("short300_seed0.csv", "episodes")]:
        with (ROOT / "results" / filename).open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        rates = []
        for suite in suite_order:
            selected = [row for row in rows if row["suite"] == suite]
            rates.append(100 * sum(int(row["successes"]) for row in selected) / sum(int(row[episode_key]) for row in selected))
        rates.append(100 * sum(int(row["successes"]) for row in rows) / sum(int(row[episode_key]) for row in rows))
        benchmark_rates.append(rates)
    grouped_bars(
        ASSETS / "benchmark_success.svg",
        "SmolVLA LIBERO benchmark",
        "Closed-loop success rates on 30 tasks; Quick-90 uses seed 10 and Short-300 uses seed 0.",
        ["Spatial", "Object", "Goal", "Overall"],
        benchmark_rates[0],
        benchmark_rates[1],
        "Quick-90 (3 episodes/task)",
        "Short-300 (10 episodes/task)",
    )

    with (ROOT / "results" / "task3_multiseed_summary.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    grouped_bars(
        ASSETS / "task3_multiseed.svg",
        "Target task across reset seeds",
        "LIBERO-Goal task 3, 10 episodes per model and seed; seed 0 was used for validation.",
        [f"Seed {row['seed']}" for row in rows],
        [10 * int(row["base_successes"]) for row in rows],
        [10 * int(row["r4_successes"]) for row in rows],
        "Official checkpoint",
        "Rank-4 LoRA",
    )

    with (ROOT / "results" / "goal_forgetting_summary.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    grouped_bars(
        ASSETS / "goal_suite_retention.svg",
        "LIBERO-Goal performance redistribution",
        "Seed 0, 10 episodes per task. Task 3 is the fine-tuning target; all other tasks are controls.",
        [f"Task {row['task_id']}" for row in rows],
        [10 * int(row["base_successes"]) for row in rows],
        [10 * int(row["r4_successes"]) for row in rows],
        "Official checkpoint",
        "Rank-4 LoRA",
    )
    print(f"Wrote figures to {ASSETS}")


if __name__ == "__main__":
    main()
