# LIBERO-Goal Forgetting Evaluation Protocol

## Question

Does the selected task-3 rank-4 LoRA adapter degrade performance on the other
nine LIBERO-Goal tasks?

## Frozen comparison

- Base: official `HuggingFaceVLA/smolvla_libero` Short-300 seed-0 results.
- Adapter: the selected rank-4, alpha-4 checkpoint at step 1790.
- Evaluation: 10 episodes per task, reset seed 0, horizon 300.
- Target task: task 3, reported separately.
- Primary control aggregate: all nine non-target Goal tasks.

Task 2 and task 4 adapter results were already collected as neighboring-task
controls. The new run evaluates tasks 0, 1, 5, 6, 7, 8, and 9. The checkpoint,
episode count, and reporting rules are fixed before these seven runs.

## Reporting

Report every task regardless of direction, plus:

1. Base and adapter success counts for the 90 non-target episodes.
2. Absolute success-rate difference in percentage points.
3. Paired failure-to-success and success-to-failure transitions.
4. Two-sided exact McNemar p-value.
5. The target task separately from the forgetting-control aggregate.

This experiment tests retention within LIBERO-Goal at seed 0. It does not prove
retention across the other suites or across unseen reset seeds.

## Execution

```bash
bash scripts/eval_goal_forgetting.sh \
  outputs/train/task3_lora_r4_1ep_bs4/checkpoints/001790/pretrained_model

python scripts/summarize_goal_forgetting.py
```

The runner skips any canonical log that already contains `End of eval`.
