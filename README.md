# SmolVLA × LIBERO Low-VRAM Reproduction

在 Ubuntu 22.04 和 RTX 3060 Laptop 6GB 上复现 SmolVLA 的 LIBERO 闭环评测，并逐步扩展到 Quick-90、Short-300 和低显存微调。

## 当前状态

- [x] CUDA 版 PyTorch 可用
- [x] LeRobot 与 LIBERO 安装完成
- [x] `HuggingFaceVLA/smolvla_libero` 单回合闭环评测成功
- [x] `libero_spatial/task_0` 三回合基线：1/3，成功率 33.33%
- [x] Quick-90：30 tasks × 3 episodes，64/90（71.11%）
- [x] Short-300：30 tasks × 10 episodes，205/300（68.33%）
- [x] `libero_goal/task_3` 低显存 LoRA 定向微调
- [x] LoRA rank 消融、留出 seed 测试与邻近任务遗忘检查

## 已验证环境

| 组件 | 版本 |
|---|---|
| Ubuntu | 22.04 |
| GPU | RTX 3060 Laptop，5.65 GiB 可用显存 |
| Python | 3.12 |
| PyTorch | 2.11.0+cu128 |
| LeRobot | 0.6.2，commit `6adf51511b7625090eade8d82d9f61a1846ebe56` |
| MuJoCo | 3.8.1 |
| 渲染后端 | OSMesa（CPU 渲染） |

## 快速运行

激活已经配置好的环境：

```bash
conda activate smolvla-libero
cd ~/projects/smolvla-libero-repro
```

单任务、3 回合：

```bash
bash scripts/eval_one.sh libero_spatial 0 3 1000
```

参数顺序为：`suite task_id episodes seed`。

Quick-90（30 tasks × 3 episodes，默认 reset seed 10）：

```bash
bash scripts/eval_quick90.sh
```

Short-300（30 tasks × 10 episodes，默认 reset seed 0）：

```bash
bash scripts/eval_short300.sh
```

验证并训练 `libero_goal/task_3` 的 rank-4 LoRA：

```bash
python scripts/verify_task3_dataset.py /home/mml/datasets/lerobot/libero
bash scripts/train_task3_lora.sh /home/mml/datasets/lerobot/libero
```

评测训练后的 checkpoint：

```bash
bash scripts/eval_checkpoint.sh \
  outputs/train/task3_lora_r4_s1790_bs4_seed1000/checkpoints/001790/pretrained_model \
  libero_goal 3 10 20 holdout_seed20_r4_task3
```

所有原始日志和视频保存在 `outputs/`，默认不提交 Git。可公开的汇总结果放在 `results/`。

## 为什么使用 OSMesa

低显存机器上，SmolVLA 与 MuJoCo EGL 渲染会竞争 GPU 显存。本项目用 OSMesa 在 CPU 上渲染，将 GPU 显存留给策略模型。代价是仿真速度较慢，但能在 6GB 显存上稳定完成闭环评测。

## 已获得结果

### Short-300

30 tasks × 10 episodes，seed 0：

| Suite | Success | Success rate |
|---|---:|---:|
| LIBERO-Spatial | 64/100 | 64.00% |
| LIBERO-Object | 72/100 | 72.00% |
| LIBERO-Goal | 69/100 | 69.00% |
| **Overall** | **205/300** | **68.33%** |

完整明细见 `docs/short300_results.md`、`results/short300_seed0.csv` 和
`results/short300_seed0.json`。其中最弱任务 `libero_goal/task_3` 的成功率
为 10%，因此被选为后续定向 LoRA 纠正实验的目标。

### Quick-90

30 tasks × 3 episodes，seed 10：

| Suite | Success | Success rate |
|---|---:|---:|
| LIBERO-Spatial | 20/30 | 66.67% |
| LIBERO-Object | 21/30 | 70.00% |
| LIBERO-Goal | 23/30 | 76.67% |
| **Overall** | **64/90** | **71.11%** |

15 个任务为 3/3，5 个任务为 2/3，9 个任务为 1/3，1 个任务为 0/3。完整明细见 `results/quick90_seed10.csv` 和 `results/quick90_seed10.json`。

### Early task-0 baseline

`libero_spatial/task_0`，3 episodes，seed 1000：

| 指标 | 数值 |
|---|---:|
| Success | 1/3 |
| Success rate | 33.33% |
| Average reward | 0.3333 |
| Total evaluation time | 354.84 s |
| Average time / episode | 118.28 s |

单次 100% 成功不代表任务真实成功率，因此项目以多回合结果作为基线。

### Targeted LoRA correction

对 Short-300 中最弱的 `libero_goal/task_3`（语言指令：
`open the top drawer and put the bowl inside`）使用 36 条示范、7157 帧进行
一轮 rank-4 LoRA 微调。训练时仅 294,144 个参数可学习，占 605M 总参数约
0.049%；batch size 4 时峰值显存约 2.27 GiB。

| Evaluation | Official checkpoint | Rank-4 LoRA |
|---|---:|---:|
| Seed 0, 10 episodes | 1/10 (10%) | 2/10 (20%) |
| Held-out seed 20, 10 episodes | 1/10 (10%) | 3/10 (30%) |
| **Combined target task** | **2/20 (10%)** | **5/20 (25%)** |

邻近任务检查未观察到明显遗忘：`libero_goal/task_2` 保持 90%，task 4
从 80% 变为 90%。rank 8 在 seed 0 上同为 20%，未优于参数更少的
rank 4。由于目标任务只有 20 个配对回合，这些结果属于初步证据，不应
表述为统计显著提升。

完整的失败分析、消融与限制见
[`docs/task3_lora_results.md`](docs/task3_lora_results.md)，结构化结果见
[`results/task3_lora_results.csv`](results/task3_lora_results.csv) 和
[`results/task3_lora_results.json`](results/task3_lora_results.json)。
训练生成的 adapter checkpoint 位于 `outputs/`，受 `.gitignore` 排除；仓库
保留可重新生成它的脚本、配置和结构化评测结果。

### Extended paired evaluation

在模型参数冻结后，用三个新 seed 扩展目标任务的配对评测：

```bash
bash scripts/eval_task3_multiseed.sh \
  outputs/train/task3_lora_r4_1ep_bs4/checkpoints/001790/pretrained_model \
  30 40 50

python scripts/summarize_task3_multiseed.py
```

脚本支持断点续跑：已经包含 `End of eval` 的运行会被自动跳过。固定的比较
方案、主指标和报告边界见
[`docs/task3_multiseed_protocol.md`](docs/task3_multiseed_protocol.md)。

固定方案完成后，held-out seeds 20/30/40/50 的结果为：官方模型
4/40（10.0%），rank-4 LoRA 9/40（22.5%），绝对差值 +12.5 个百分点；
配对转移为8次改善、3次退化，双侧精确 McNemar `p=0.226562`。因此结果
表现为跨 seed 的正向趋势，但尚未达到统计显著。逐 seed 结果、Wilson
区间与解释见
[`docs/task3_multiseed_results.md`](docs/task3_multiseed_results.md)。

## 上游项目

- [LeRobot](https://github.com/huggingface/lerobot)
- [SmolVLA LIBERO checkpoint](https://huggingface.co/HuggingFaceVLA/smolvla_libero)
- [LeRobot LIBERO dataset](https://huggingface.co/datasets/lerobot/libero)
- [LIBERO benchmark](https://github.com/Lifelong-Robot-Learning/LIBERO)
- [LeRobot LIBERO documentation](https://huggingface.co/docs/lerobot/libero)

本文档和脚本为独立复现，不复制第三方文章中的未开源脚本或正文。模型、数据集和上游代码分别受其各自许可证约束。

## License

本项目原创脚本与文档采用 Apache License 2.0，见 [LICENSE](LICENSE)。
