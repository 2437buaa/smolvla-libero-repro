# Experiment Log

## 2026-08-14 — Environment bring-up

- Ubuntu 22.04
- Python 3.12 Conda environment: `smolvla-libero`
- PyTorch 2.11.0+cu128; CUDA available
- LeRobot 0.6.2 at `6adf51511b7625090eade8d82d9f61a1846ebe56`
- MuJoCo 3.8.1
- OSMesa rendering selected to avoid EGL/GPU-memory contention

## 2026-08-14 — First successful rollout

- Policy: `HuggingFaceVLA/smolvla_libero`
- Suite/task: `libero_spatial/0`
- Episodes: 1
- Result: 1/1 success
- Evaluation time: 56.80 s
- Approximate success step: 72/280

Interpretation: validates the full observation → policy → action → simulator loop, but is not a reliable success-rate estimate.

## 2026-08-14 — Three-episode task baseline

- Policy: `HuggingFaceVLA/smolvla_libero`
- Suite/task: `libero_spatial/0`
- Episodes: 3
- Seed: 1000
- Result: 1/3 success, 33.33%
- Evaluation time: 354.84 s

Interpretation: the model is sensitive to initialization; multi-episode evaluation is required.

## 2026-08-15 — Quick-90

- Policy: `HuggingFaceVLA/smolvla_libero`
- Suites: `libero_spatial`, `libero_object`, `libero_goal`
- Tasks: 10 per suite, 30 total
- Episodes: 3 per task, 90 total
- Seed: 10
- Renderer: OSMesa

| Suite | Success | Success rate |
|---|---:|---:|
| Spatial | 20/30 | 66.67% |
| Object | 21/30 | 70.00% |
| Goal | 23/30 | 76.67% |
| Overall | 64/90 | 71.11% |

Task distribution: 15 tasks at 3/3, 5 tasks at 2/3, 9 tasks at 1/3, and 1 task at 0/3. The only 0/3 task is `libero_goal/task_3`.

Interpretation: one-reset smoke evaluation was optimistic. Multi-initialization evaluation exposes substantial task and reset sensitivity.

## 2026-08-15 — Short-300

- Policy: `HuggingFaceVLA/smolvla_libero`
- Suites: `libero_spatial`, `libero_object`, `libero_goal`
- Tasks: 10 per suite, 30 total
- Episodes: 10 per task, 300 total
- Seed: 0
- Renderer: OSMesa

| Suite | Success | Success rate |
|---|---:|---:|
| Spatial | 64/100 | 64.00% |
| Object | 72/100 | 72.00% |
| Goal | 69/100 | 69.00% |
| Overall | 205/300 | 68.33% |

The weakest task is `libero_goal/task_3` at 1/10. Other low-performing tasks
include `libero_spatial/task_0`, `libero_object/task_0`, and
`libero_goal/task_9`, each at 4/10.

Compared with Quick-90, the overall estimate changed from 71.11% to 68.33%.
The runs use different seeds and episode counts, so this is not evidence of
model regression. Short-300 is retained as the more stable local baseline for
future experiments.

## 2026-08-16 — Target-task dataset verification

- Target suite/task: `libero_goal/task_3`
- Language instruction: `open the top drawer and put the bowl inside`
- Dataset: local `lerobot/libero`, LeRobotDataset v3.0
- Task index: 12
- Selected demonstrations: 36 episodes, 7157 frames
- Decoded features: two `(3, 256, 256)` RGB views, state `(8,)`, action `(7,)`

An older image-in-Parquet conversion was rejected after its episode metadata
did not match the episode indices stored in the data shards. Training uses only
the verified `lerobot/libero` copy.

## 2026-08-16 — Failure analysis of `libero_goal/task_3`

The Short-300 baseline achieved 1/10. Manual review found:

- Episodes 0, 1, 2, 3, 4, 5, and 7: drawer not opened and bowl not grasped.
- Episode 6: missed the drawer handle, later grasped the bowl, then released it
  on the table because the drawer remained closed.
- Episode 8: successful open-drawer, grasp-bowl, place-bowl sequence.
- Episode 9: opened the drawer but missed the bowl during grasping.

The main observed bottlenecks are end-effector alignment during handle/bowl
contact and error propagation between subtasks.

## 2026-08-16 — Low-VRAM LoRA training

- Starting policy: `HuggingFaceVLA/smolvla_libero`
- Training data: the 36 target-task episodes only
- Selected configuration: rank 4, alpha 4, batch size 4, 1790 steps
- Coverage: approximately one epoch (about 7160 sampled frames)
- Automatic mixed precision: enabled through `policy.use_amp`
- Trainable parameters: 294,144 / 605,228,320 (approximately 0.049%)
- Peak reported GPU memory: 2.27 GiB
- Runtime: 9 minutes 29 seconds on RTX 3060 Laptop 6GB

A 500-microbatch pilot with gradient accumulation reproduced the 10% baseline
and emitted a scheduler-order warning, so the selected run uses real batch size
4 with gradient accumulation disabled.

## 2026-08-16 — LoRA evaluation and ablation

| Evaluation | Official | Rank-4 LoRA | Rank-8 LoRA |
|---|---:|---:|---:|
| Seed 0, 10 episodes | 10% | 20% | 20% |
| Held-out seed 20, 10 episodes | 10% | 30% | not selected |
| Combined target-task result | 2/20 (10%) | 5/20 (25%) | — |

Rank 8 changed which seed-0 episodes succeeded but did not improve aggregate
success over rank 4. Rank 4 was retained because it matched rank 8 with fewer
trainable parameters.

On held-out seed 20, rank 4 preserved the original successful episode and added
two successes. Across seed 0 and seed 20, the paired outcomes contain four
base-failure to LoRA-success transitions and one base-success to LoRA-failure
transition.

## 2026-08-16 — Neighbor-task control

The selected rank-4 checkpoint was evaluated on two neighboring Goal tasks
using the same seed-0, 10-episode protocol as Short-300.

| Task | Official Short-300 | Rank-4 LoRA |
|---|---:|---:|
| `libero_goal/task_2` | 9/10 (90%) | 9/10 (90%) |
| `libero_goal/task_4` | 8/10 (80%) | 9/10 (90%) |
| Combined | 17/20 (85%) | 18/20 (90%) |

No obvious catastrophic forgetting was observed on these two controls. The
sample remains small, and the task-4 increase should not be interpreted as
proven positive transfer.

## 2026-08-16 — Fixed multi-seed extension

The selected rank-4 checkpoint was frozen before evaluating new reset seeds
30, 40, and 50. Together with the existing held-out seed 20, the primary
held-out aggregate contains 40 paired episodes per model. Seed 0 remains a
validation/model-selection result and is reported separately.

| Seed | Official | Rank-4 LoRA | Gain / loss transitions |
|---:|---:|---:|---:|
| 20 | 1/10 | 3/10 | 2 / 0 |
| 30 | 1/10 | 0/10 | 0 / 1 |
| 40 | 1/10 | 3/10 | 3 / 1 |
| 50 | 1/10 | 3/10 | 3 / 1 |
| **Held-out total** | **4/40 (10.0%)** | **9/40 (22.5%)** | **8 / 3** |

The held-out absolute difference is +12.5 percentage points. The two-sided
exact McNemar p-value is 0.226562, so the positive trend is not statistically
conclusive. Including seed 0, the official checkpoint scores 5/50 and LoRA
scores 11/50, with 10 gain and 4 loss transitions (`p=0.179565`).

The new evaluation strengthens the evidence that the adapter changes
closed-loop behavior across reset seeds, but it also exposes a regression on
seed 30. Full details are in `docs/task3_multiseed_results.md`.

## 2026-08-16 — Full LIBERO-Goal forgetting control

The selected adapter was evaluated on all nine non-target Goal tasks using the
seed-0 Short-300 protocol. The official checkpoint scored 68/90 (75.6%) and
rank-4 LoRA scored 71/90 (78.9%), a +3.3 percentage-point difference. Paired
outcomes contain 13 gains and 10 losses (`p=0.677639`, exact McNemar).

No aggregate catastrophic forgetting is observed, but performance is
redistributed: task 6 changes from 8/10 to 5/10 and task 0 from 8/10 to 6/10,
while task 9 changes from 4/10 to 7/10. The result does not establish positive
transfer or retention outside Goal at seed 0.
