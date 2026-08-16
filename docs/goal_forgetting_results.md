# LIBERO-Goal Forgetting Evaluation Results

## Setup

The selected task-3 rank-4 LoRA checkpoint was evaluated on every LIBERO-Goal
task at seed 0 with 10 episodes per task. The primary forgetting aggregate
excludes the target task 3 and contains 90 paired episodes across nine control
tasks. Official results reuse the fixed Short-300 baseline.

## Per-task results

| Task | Role | Official | Rank-4 LoRA | Delta | Gain / loss transitions |
|---:|---|---:|---:|---:|---:|
| 0 | Control | 8/10 | 6/10 | -2 | 0 / 2 |
| 1 | Control | 8/10 | 7/10 | -1 | 1 / 2 |
| 2 | Control | 9/10 | 9/10 | 0 | 1 / 1 |
| 3 | Target | 1/10 | 2/10 | +1 | 2 / 1 |
| 4 | Control | 8/10 | 9/10 | +1 | 2 / 1 |
| 5 | Control | 6/10 | 8/10 | +2 | 3 / 1 |
| 6 | Control | 8/10 | 5/10 | -3 | 0 / 3 |
| 7 | Control | 9/10 | 10/10 | +1 | 1 / 0 |
| 8 | Control | 8/10 | 10/10 | +2 | 2 / 0 |
| 9 | Control | 4/10 | 7/10 | +3 | 3 / 0 |

## Aggregate retention

| Scope | Official | Rank-4 LoRA | Difference |
|---|---:|---:|---:|
| Nine non-target controls | 68/90 (75.6%) | 71/90 (78.9%) | +3.3 pp |
| Full Goal suite | 69/100 (69.0%) | 73/100 (73.0%) | +4.0 pp |

Across the non-target controls there are 13 base-failure to LoRA-success
transitions and 10 base-success to LoRA-failure transitions. The two-sided
exact McNemar p-value is 0.677639.

## Interpretation

There is no aggregate evidence of catastrophic forgetting within LIBERO-Goal
at seed 0: the adapter does not reduce the non-target success rate, and the
observed difference is +3.3 percentage points. The high McNemar p-value means
that this experiment does not establish positive transfer or equivalence.

Aggregate retention hides task-level redistribution. Task 6 falls by three
successes and task 0 by two, while tasks 9, 5, and 8 improve. The adapter should
therefore be described as preserving overall Goal-suite performance while
changing the task and initialization states it can solve, not as uniformly
improving every task.

This control is limited to seed 0 and the Goal suite. Claims about Spatial,
Object, unseen seeds, or formal non-inferiority require additional evaluation.

## Artifacts

- Protocol: [`goal_forgetting_protocol.md`](goal_forgetting_protocol.md)
- CSV: [`../results/goal_forgetting_summary.csv`](../results/goal_forgetting_summary.csv)
- JSON: [`../results/goal_forgetting_summary.json`](../results/goal_forgetting_summary.json)
- Runner: [`../scripts/eval_goal_forgetting.sh`](../scripts/eval_goal_forgetting.sh)
- Summarizer: [`../scripts/summarize_goal_forgetting.py`](../scripts/summarize_goal_forgetting.py)
