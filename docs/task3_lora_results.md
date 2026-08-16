# Targeted LoRA Correction for LIBERO Goal Task 3

## Question

Can a low-rank adapter trained on demonstrations of the weakest Short-300 task
improve its closed-loop success rate on a 6GB laptop GPU without visibly
damaging neighboring tasks?

The target is `libero_goal/task_3`:

> open the top drawer and put the bowl inside

The official `HuggingFaceVLA/smolvla_libero` checkpoint achieved 1/10 on this
task in the seed-0 Short-300 run.

## Dataset validation

The experiment uses a local copy of `lerobot/libero` in LeRobotDataset v3.0
format. The natural-language task maps to `task_index=12`. Direct inspection of
the frame-level Parquet shards found 36 episodes and 7157 frames. An actual
sample decoded successfully with these policy-facing features:

| Feature | Shape |
|---|---:|
| `observation.images.image` | `(3, 256, 256)` |
| `observation.images.image2` | `(3, 256, 256)` |
| `observation.state` | `(8,)` |
| `action` | `(7,)` |

An earlier `HuggingFaceVLA/libero` download was not used for training because
its episode metadata and data-shard episode indices disagreed. This validation
step prevents silently training on unrelated demonstrations.

## Baseline failure modes

Manual inspection of the ten seed-0 baseline videos showed a hierarchical
failure pattern:

1. Seven rollouts did not open the drawer and did not grasp the bowl.
2. Episode 6 missed the drawer handle, grasped the bowl anyway, and released it
   on the tabletop.
3. Episode 9 opened the drawer but missed the bowl during grasping.
4. Episode 8 completed the full sequence.

This suggests that contact alignment and the lack of recovery after a failed
subtask are more important than language understanding for this task.

## Training configuration

The selected run starts from the official LIBERO checkpoint rather than the
base SmolVLA model.

| Setting | Value |
|---|---:|
| LoRA rank / alpha | 4 / 4 |
| Batch size | 4 |
| Gradient accumulation | 1 |
| Training steps | 1790 |
| Approximate data coverage | 1 epoch |
| Peak learning rate | `1e-4` |
| Trainable parameters | 294,144 |
| Total parameters | 605,228,320 |
| Peak reported VRAM | 2.27 GiB |
| Runtime | 9 min 29 s |

Vision encoder freezing and expert-only training are inherited from the
pretrained checkpoint. AMP is enabled with `policy.use_amp=true`. OSMesa is
used during evaluation so MuJoCo rendering does not consume GPU memory.

## Main results

### Target-task evaluation

| Reset seed | Model | Successes | Rate | Successful episode indices |
|---:|---|---:|---:|---|
| 0 | Official checkpoint | 1/10 | 10% | 8 |
| 0 | Rank-4 LoRA, 500-microbatch pilot | 1/10 | 10% | 8 |
| 0 | Rank-4 LoRA, 1 epoch | 2/10 | 20% | 6, 9 |
| 0 | Rank-8 LoRA, 1 epoch | 2/10 | 20% | 5, 6 |
| 20 | Official checkpoint | 1/10 | 10% | 5 |
| 20 | Rank-4 LoRA, 1 epoch | 3/10 | 30% | 3, 5, 8 |

Combining the two paired seeds, the official checkpoint scores 2/20 (10%) and
the selected rank-4 adapter scores 5/20 (25%). On seed 0 it gained episodes 6
and 9 but lost the original episode-8 success. On held-out seed 20 it preserved
the original episode-5 success and added episodes 3 and 8.

Rank 8 did not improve seed-0 aggregate success over rank 4, so rank 4 is the
more parameter-efficient choice in this experiment.

### Neighbor-task control

| Task | Official checkpoint | Rank-4 LoRA |
|---|---:|---:|
| `libero_goal/task_2` | 9/10 (90%) | 9/10 (90%) |
| `libero_goal/task_4` | 8/10 (80%) | 9/10 (90%) |
| **Combined** | **17/20 (85%)** | **18/20 (90%)** |

These controls do not show obvious catastrophic forgetting. They do not prove
that performance is preserved across the full 40-task training distribution.

## Interpretation

The adapter changes closed-loop behavior rather than uniformly improving every
initial state. The seed-0 success set shifts from `{8}` to `{6, 9}`, while the
held-out seed-20 success set expands from `{5}` to `{3, 5, 8}`. The held-out
result is encouraging because it preserves the baseline success and adds two
new successes.

The experiment supports a narrow conclusion: one epoch of rank-4 LoRA on
verified target-task demonstrations produced a preliminary cross-seed gain on
the selected difficult task, with no visible degradation on two neighboring
tasks.

## Subsequent multi-seed extension

After checkpoint selection, the comparison was extended with new reset seeds
30, 40, and 50 under a fixed reporting protocol. Across held-out seeds 20, 30,
40, and 50, the official checkpoint scored 4/40 (10.0%) and rank-4 LoRA scored
9/40 (22.5%). The paired outcomes contain eight gain transitions and three loss
transitions; the two-sided exact McNemar p-value is 0.226562.

The direction of the initial result persists, but the difference remains
statistically inconclusive. See
[`task3_multiseed_results.md`](task3_multiseed_results.md) for per-seed outcomes
and confidence intervals.

## Limitations

- The initial model-selection stage used 20 paired rollouts; the subsequent
  held-out extension contains 40 paired rollouts and remains modest.
- The difference is not statistically conclusive; confidence intervals are
  wide at this sample size.
- Seed 0 was used during model selection and should be treated as validation,
  not an untouched test set.
- Only two neighboring tasks were used as forgetting controls.
- Hyperparameter search was limited to rank 4 versus rank 8 and a short pilot.
- Raw videos and logs are excluded from Git; structured outcomes are retained.

Future work should expand forgetting controls to all Goal tasks, compare lower
learning rates or rehearsal data, and use larger independently fixed evaluation
sets if stronger statistical claims are required.
