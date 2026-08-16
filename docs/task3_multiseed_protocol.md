# Task-3 Multi-Seed Evaluation Protocol

## Purpose

The first targeted LoRA experiment improved the combined success rate on
`libero_goal/task_3` from 2/20 to 5/20 across seeds 0 and 20. This follow-up
tests whether that difference persists across additional reset seeds.

The model is frozen before running the new seeds. No further training or
hyperparameter selection is performed using seeds 30, 40, or 50.

## Fixed comparison

- Base policy: `HuggingFaceVLA/smolvla_libero`
- Adapted policy: rank-4, alpha-4 LoRA checkpoint at training step 1790
- Task: `libero_goal/task_3`
- Episodes per seed and model: 10
- Episode horizon: 300
- New reset seeds: 30, 40, 50
- Existing held-out seed: 20
- Validation/model-selection seed: 0

Both models use the same reset seed and episode indices, so outcomes are
analyzed as paired binary observations.

## Reporting rule

The primary held-out aggregate contains seeds 20, 30, 40, and 50. Seed 0 is
reported separately because it was observed during model selection. An
exploratory all-seed aggregate may also be shown, but it must not be presented
as a fully untouched test result.

Report all of the following regardless of whether the adapter improves:

1. Per-seed successes for each model.
2. Aggregate successes and success rates.
3. Wilson 95% intervals for each model rate.
4. Paired failure-to-success and success-to-failure counts.
5. The two-sided exact McNemar p-value.

The sample remains modest even after this extension. A non-significant result
does not prove equivalence, and a lower p-value does not measure effect size.

## Execution

```bash
bash scripts/eval_task3_multiseed.sh \
  outputs/train/task3_lora_r4_1ep_bs4/checkpoints/001790/pretrained_model \
  30 40 50

python scripts/summarize_task3_multiseed.py
```

The evaluation script skips runs whose log already contains `End of eval`, so
the sequence can be restarted safely after interruption.
