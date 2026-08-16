# SmolVLA LIBERO Short-300 Results

This document records a 300-episode evaluation of the official
`HuggingFaceVLA/smolvla_libero` checkpoint on three LIBERO suites. Each suite
contains 10 tasks and each task is evaluated for 10 episodes with seed 0.

## Aggregate results

| Suite | Successes | Episodes | Success rate |
|---|---:|---:|---:|
| LIBERO-Spatial | 64 | 100 | 64.00% |
| LIBERO-Object | 72 | 100 | 72.00% |
| LIBERO-Goal | 69 | 100 | 69.00% |
| **Overall** | **205** | **300** | **68.33%** |

## Per-task results

| Task ID | Spatial | Object | Goal |
|---:|---:|---:|---:|
| 0 | 40% | 40% | 80% |
| 1 | 90% | 80% | 80% |
| 2 | 70% | 90% | 90% |
| 3 | 70% | 90% | 10% |
| 4 | 70% | 60% | 80% |
| 5 | 60% | 90% | 60% |
| 6 | 60% | 80% | 80% |
| 7 | 60% | 50% | 90% |
| 8 | 60% | 70% | 80% |
| 9 | 60% | 70% | 40% |

## Comparison with Quick-90

The earlier Quick-90 run used three episodes per task with seed 10. It is useful
as a smoke benchmark, but its estimates have substantially higher variance than
the Short-300 run.

| Suite | Quick-90 | Short-300 | Change |
|---|---:|---:|---:|
| LIBERO-Spatial | 66.67% | 64.00% | -2.67 pp |
| LIBERO-Object | 70.00% | 72.00% | +2.00 pp |
| LIBERO-Goal | 76.67% | 69.00% | -7.67 pp |
| **Overall** | **71.11%** | **68.33%** | **-2.78 pp** |

The difference should not be interpreted as model regression because the two
runs use different seeds and episode counts. Short-300 is the more stable local
baseline for subsequent experiments.

## Main observation

`libero_goal/task_3` achieved 1 success in 10 episodes (10%), making it the
clearest candidate for failure analysis and targeted fine-tuning. Other weak
tasks are `libero_spatial/task_0` and `libero_object/task_0` (both 40%), plus
`libero_goal/task_9` (40%).

## Reproducibility scope

- Policy: official pretrained SmolVLA LIBERO checkpoint; no user fine-tuning.
- LeRobot: version 0.6.2, commit
  `6adf51511b7625090eade8d82d9f61a1846ebe56`.
- Runtime: Python 3.12.13, PyTorch 2.11.0+cu128, MuJoCo 3.8.1.
- Hardware: RTX 3060 Laptop GPU with 5.65 GiB usable VRAM.
- Rendering: CPU OSMesa; evaluation batch size 1 and sequential environments.
- Raw logs and videos are intentionally excluded from Git because of their
  size. The structured CSV and JSON results are the version-controlled record.

## Follow-up experiment

The proposed `libero_goal/task_3` failure analysis and low-VRAM fine-tuning
experiment has been completed. See [`task3_lora_results.md`](task3_lora_results.md)
for the targeted LoRA correction, ablation, held-out evaluation, and neighboring
task controls.
