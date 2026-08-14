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
