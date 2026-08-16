# SmolVLA LIBERO Goal Task-3 LoRA

This is the model card template for the rank-4 adapter produced by this
repository. The adapter weights are not redistributed in the GitHub repository.

## Model details

- Base policy: `HuggingFaceVLA/smolvla_libero`
- Method: LoRA, rank 4, alpha 4
- Target instruction: `open the top drawer and put the bowl inside`
- Training data: 36 verified `lerobot/libero` episodes, 7157 frames
- Training: 1790 steps, batch size 4, AMP enabled
- Trainable parameters: 294,144 of 605,228,320 (about 0.049%)
- Hardware: RTX 3060 Laptop GPU with 5.65 GiB usable VRAM
- Reported peak VRAM: 2.27 GiB
- Runtime: approximately 9 minutes 29 seconds

## Evaluation

On held-out reset seeds 20, 30, 40, and 50, the official checkpoint achieved
4/40 successes (10.0%) and the adapter achieved 9/40 (22.5%). The paired exact
McNemar p-value is 0.226562, so the observed positive trend is not statistically
conclusive.

Across nine non-target LIBERO-Goal tasks at seed 0, the official checkpoint
achieved 68/90 (75.6%) and the adapter achieved 71/90 (78.9%). This does not
show aggregate catastrophic forgetting, but tasks 0, 1, and 6 regress locally.

## Intended use

The adapter is intended for reproducibility research and evaluation in the
LIBERO simulator. It is not validated for real-robot deployment, safety-critical
control, or operation outside the documented observation/action interface.

## Limitations

- Target-task evaluation remains modest and is not statistically conclusive.
- Forgetting controls cover LIBERO-Goal at seed 0, not all suites and seeds.
- The adapter redistributes successful initial states and does not improve every
  rollout or task.
- Results depend on the pinned LeRobot revision, assets, reset seeds, and
  simulator configuration documented in the repository.

## Upstream components

The base model, dataset, LeRobot, and LIBERO remain subject to their respective
licenses and terms. See `THIRD_PARTY_NOTICES.md` in the source repository.
