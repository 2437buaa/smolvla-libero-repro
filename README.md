# SmolVLA × LIBERO Low-VRAM Reproduction

在 Ubuntu 22.04 和 RTX 3060 Laptop 6GB 上复现 SmolVLA 的 LIBERO 闭环评测，并逐步扩展到 Quick-90、Short-300 和低显存微调。

## 当前状态

- [x] CUDA 版 PyTorch 可用
- [x] LeRobot 与 LIBERO 安装完成
- [x] `HuggingFaceVLA/smolvla_libero` 单回合闭环评测成功
- [x] `libero_spatial/task_0` 三回合基线：1/3，成功率 33.33%
- [x] Quick-90：30 tasks × 3 episodes，64/90（71.11%）
- [x] Short-300：30 tasks × 10 episodes，205/300（68.33%）
- [ ] 低显存微调与弱任务纠正数据实验

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
`results/short300_seed0.json`。当前最弱任务是 `libero_goal/task_3`，成功率
为 10%，后续将优先进行失败分析与纠正数据实验。

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

## 上游项目

- [LeRobot](https://github.com/huggingface/lerobot)
- [SmolVLA LIBERO checkpoint](https://huggingface.co/HuggingFaceVLA/smolvla_libero)
- [LIBERO benchmark](https://github.com/Lifelong-Robot-Learning/LIBERO)
- [LeRobot LIBERO documentation](https://huggingface.co/docs/lerobot/libero)

本文档和脚本为独立复现，不复制第三方文章中的未开源脚本或正文。模型、数据集和上游代码分别受其各自许可证约束。

## License

本项目原创脚本与文档采用 Apache License 2.0，见 [LICENSE](LICENSE)。
