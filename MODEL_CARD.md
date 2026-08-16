---
license: apache-2.0
library_name: lerobot
pipeline_tag: robotics
base_model: HuggingFaceVLA/smolvla_libero
datasets:
  - lerobot/libero
tags:
  - robotics
  - embodied-ai
  - vision-language-action
  - lerobot
  - smolvla
  - libero
  - peft
  - lora
  - low-vram
---

# SmolVLA LIBERO Goal Task-3 LoRA (Rank 4)

This repository documents the **PEFT/LoRA adapter** published at
[`marlon777777/smolvla-libero-task3-lora-r4`](https://huggingface.co/marlon777777/smolvla-libero-task3-lora-r4).
It adapts
[`HuggingFaceVLA/smolvla_libero`](https://huggingface.co/HuggingFaceVLA/smolvla_libero)
to the LIBERO-Goal instruction:

> `open the top drawer and put the bowl inside`

## Model details

- Base policy: `HuggingFaceVLA/smolvla_libero`
- Method: LoRA, rank 4, alpha 4
- Training data: 36 verified `lerobot/libero` episodes, 7,157 frames
- Training: 1,790 steps (approximately one epoch), batch size 4, AMP enabled
- Trainable parameters: 294,144 of 605,228,320 (approximately 0.049%)
- Hardware: RTX 3060 Laptop GPU with 5.65 GiB usable VRAM
- Reported peak VRAM: 2.27 GiB
- Training runtime: approximately 9 minutes 29 seconds
- LeRobot version: 0.6.2, commit `6adf51511b7625090eade8d82d9f61a1846ebe56`

## Evaluation

On held-out reset seeds 20, 30, 40, and 50, the official checkpoint achieved
4/40 successes (10.0%), while the adapter achieved 9/40 (22.5%), an absolute
difference of +12.5 percentage points. Paired transitions were eight
improvements and three regressions; the two-sided exact McNemar p-value was
`0.226562`. The observed positive trend is therefore **not statistically
conclusive**.

Across nine non-target LIBERO-Goal tasks at seed 0, the official checkpoint
achieved 68/90 (75.6%) and the adapter achieved 71/90 (78.9%). This evaluation
did not show aggregate catastrophic forgetting, but tasks 0, 1, and 6 regressed
locally. This should not be interpreted as proof of positive transfer or
equivalence across the full benchmark.

Full protocols, per-seed outcomes, structured CSV/JSON results, and plotting
scripts are available in this repository.

## Usage

For a fresh Ubuntu 22.04 machine, first follow
[`docs/setup_ubuntu2204.md`](docs/setup_ubuntu2204.md). With that pinned
LeRobot and LIBERO environment, evaluate the Hub adapter using:

```bash
bash scripts/eval_checkpoint.sh \
  marlon777777/smolvla-libero-task3-lora-r4 \
  libero_goal 3 10 20 hf_task3_r4_seed20
```

The Hub repository contains the LoRA weights together with the LeRobot policy
configuration and preprocessing/postprocessing state required by the saved
checkpoint.

## Intended use

This adapter is intended for reproducibility research and evaluation in the
LIBERO simulator. It is not validated for real-robot deployment,
safety-critical control, or operation outside the documented observation and
action interface.

## Limitations

- Target-task evaluation remains modest and is not statistically conclusive.
- Forgetting controls cover LIBERO-Goal at seed 0, not every suite and seed.
- The adapter redistributes successful initial states and does not improve
  every rollout or task.
- Results depend on the pinned LeRobot revision, simulator assets, reset seeds,
  and rendering/configuration choices documented in this repository.
- Only the adapter is published on Hugging Face; the upstream base model must
  be loaded according to its own license and usage conditions.

## Licenses and attribution

The adapter and original accompanying documentation are released under the
Apache License 2.0. The base model, dataset, LeRobot, and LIBERO remain subject
to their respective licenses and terms. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)
for attribution details.
