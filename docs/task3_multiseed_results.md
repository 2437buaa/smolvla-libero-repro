# Task-3 Multi-Seed Evaluation Results

## Evaluation status

The rank-4 checkpoint and reporting protocol were frozen before running the
new reset seeds 30, 40, and 50. Seed 20 had already been inspected in the
initial experiment; seed 0 was used during model selection and is excluded
from the held-out aggregate.

Each model was evaluated for 10 episodes per seed on `libero_goal/task_3` with
an episode horizon of 300. Base and LoRA evaluations used matching reset seeds
and episode indices.

## Per-seed outcomes

| Seed | Role | Official | Rank-4 LoRA | Base success indices | LoRA success indices | Gain / loss transitions |
|---:|---|---:|---:|---|---|---:|
| 0 | Validation | 1/10 | 2/10 | 8 | 6, 9 | 2 / 1 |
| 20 | Held-out | 1/10 | 3/10 | 5 | 3, 5, 8 | 2 / 0 |
| 30 | Held-out, new | 1/10 | 0/10 | 1 | none | 0 / 1 |
| 40 | Held-out, new | 1/10 | 3/10 | 4 | 0, 3, 5 | 3 / 1 |
| 50 | Held-out, new | 1/10 | 3/10 | 1 | 0, 2, 8 | 3 / 1 |

Here, a gain is an episode where the official checkpoint failed and LoRA
succeeded; a loss is the reverse transition.

The official checkpoint achieved exactly one success under every tested seed.
Rank-4 LoRA improved three of four held-out seeds and regressed on seed 30. On
the three newly evaluated seeds alone, the official checkpoint scored 3/30 and
LoRA scored 6/30.

## Aggregate results

### Held-out aggregate

This is the primary aggregate defined by the locked protocol.

| Metric | Official | Rank-4 LoRA |
|---|---:|---:|
| Successes | 4/40 | 9/40 |
| Success rate | 10.0% | 22.5% |
| Wilson 95% interval | 3.96%–23.05% | 12.32%–37.50% |

- Absolute difference: **+12.5 percentage points**.
- Relative success-rate ratio: **2.25×**.
- Paired transitions: 8 gains and 3 losses.
- Two-sided exact McNemar p-value: **0.226562**.

### All reported seeds

This exploratory aggregate includes the seed-0 validation result.

| Metric | Official | Rank-4 LoRA |
|---|---:|---:|
| Successes | 5/50 | 11/50 |
| Success rate | 10.0% | 22.0% |
| Wilson 95% interval | 4.35%–21.36% | 12.75%–35.24% |

- Absolute difference: **+12.0 percentage points**.
- Paired transitions: 10 gains and 4 losses.
- Two-sided exact McNemar p-value: **0.179565**.

## Interpretation

The extended evaluation preserves the direction and approximate magnitude of
the initial result: the adapter is roughly twice as successful on the selected
task, and the held-out absolute difference is 12.5 percentage points. The
improvement is not confined to the original seed-20 evaluation because seeds
40 and 50 also improve from 1/10 to 3/10.

The result is not uniform. Seed 30 falls from 1/10 to 0/10, and on seeds 30,
40, and 50 the two models have no overlapping successful episode indices. This
supports the behavioral-distribution interpretation: LoRA changes which
initial states the policy can solve rather than monotonically improving every
rollout.

The exact McNemar p-value is above 0.05, and the Wilson intervals overlap.
Therefore the defensible conclusion is a positive but statistically
inconclusive trend. The full outcomes are reported rather than extending the
experiment until a preferred significance threshold is reached.

## Reproducibility artifacts

- Frozen protocol: [`task3_multiseed_protocol.md`](task3_multiseed_protocol.md)
- Per-seed CSV: [`../results/task3_multiseed_summary.csv`](../results/task3_multiseed_summary.csv)
- Aggregate JSON: [`../results/task3_multiseed_summary.json`](../results/task3_multiseed_summary.json)
- Runner: [`../scripts/eval_task3_multiseed.sh`](../scripts/eval_task3_multiseed.sh)
- Summarizer: [`../scripts/summarize_task3_multiseed.py`](../scripts/summarize_task3_multiseed.py)

The next experiment should expand the forgetting control from two neighboring
tasks to all nine non-target tasks in LIBERO-Goal while keeping this adapter
fixed.
