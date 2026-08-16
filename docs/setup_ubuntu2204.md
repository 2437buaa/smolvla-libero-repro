# Ubuntu 22.04 从零复现指南

这份文档面向一台刚装好 Ubuntu 22.04、带 NVIDIA 显卡的新机器。目标是先跑通
一个最小闭环评测，再按需下载训练数据和运行 LoRA 微调。

“闭环评测”指模型不断看到机器人当前画面、给出下一步动作、让模拟器执行，
再根据新画面继续决定动作。它比只在已有数据上算一次答案更接近真实机器人运行。

## 0. 机器要求

- Ubuntu 22.04；
- NVIDIA 显卡与可用驱动，先用 `nvidia-smi` 确认；
- 建议至少 6GB 显存；本项目已在 RTX 3060 Laptop 6GB 上验证；
- 最小测试建议预留 20GB 磁盘，完整评测和训练建议预留 50GB 以上；
- 稳定网络。所有下载脚本都可以重复运行，已完成的文件通常不会重新下载。

PyTorch 安装包自带所需的 CUDA 运行库，因此本复现不要求另外安装完整的系统级
CUDA Toolkit。真正必须的是可用的 NVIDIA 驱动。

## 1. 获取仓库

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/2437buaa/smolvla-libero-repro.git
cd smolvla-libero-repro
```

## 2. 安装 Ubuntu 系统工具

```bash
bash scripts/install_system_dependencies.sh
```

这里安装 Git、Git LFS、FFmpeg、编译工具和 MuJoCo 的离屏渲染依赖。Git LFS
用于下载体积较大的模型或数据文件；FFmpeg 用于生成和检查评测视频；OSMesa
让 MuJoCo 在 CPU 上画仿真画面，把有限的 GPU 显存留给模型。

## 3. 创建独立 Python 环境

先确保已经安装 Miniconda 或 Anaconda，然后运行：

```bash
conda env create -f environment.yml
conda activate smolvla-libero
```

独立环境相当于给这个项目准备一个单独的工具箱，不会把其他 Python 项目的包弄乱。

## 4. 安装固定版本的 PyTorch、LeRobot 和 LIBERO

```bash
bash scripts/setup_lerobot.sh
```

脚本会完成以下事情：

1. 安装已验证的 CUDA 12.8 版 PyTorch；
2. 把 LeRobot 下载到 `~/projects/lerobot-smolvla-libero`；
3. 固定到 commit `6adf51511b7625090eade8d82d9f61a1846ebe56`；
4. 安装 LIBERO、SmolVLA、LoRA 训练和相应 Python 依赖；
5. 运行依赖冲突检查。

固定 commit 的作用类似“指定使用同一版实验说明书”。即使 LeRobot 以后更新，
本项目仍然使用实验时验证过的代码，避免命令或默认行为悄悄变化。

如果想把 LeRobot 放到别处：

```bash
LEROBOT_DIR=/你想使用的路径 bash scripts/setup_lerobot.sh
```

脚本不会覆盖路径中已有的其他 LeRobot 版本；发现版本不一致时会停止并提示换路径。

## 5. 下载 LIBERO 仿真素材

```bash
python scripts/download_libero_assets.py
```

这些素材包含桌子、抽屉、碗等物体的模型。没有它们，模拟器只能知道任务名字，
却找不到要加载的场景文件。脚本固定到实验使用的资源版本，并在结束时检查关键场景。

## 6. 预先缓存模型

```bash
python scripts/prefetch_models.py
```

这会缓存官方 SmolVLA、它使用的视觉语言模型以及本项目发布的 rank-4 LoRA adapter。
Hugging Face 账号不是公开文件下载的必要条件，但登录后通常有更高的下载限额：

```bash
hf auth login
```

不要把 Hugging Face token 写进脚本、README、Git 提交或终端截图。

## 7. 检查环境并运行最小实验

```bash
bash scripts/check_environment.sh
bash scripts/smoke_test.sh
```

`check_environment.sh` 检查 Python、CUDA、PyTorch、MuJoCo、LeRobot 和关键场景文件。
`smoke_test.sh` 会运行 `libero_spatial/task_0` 的一个回合。出现 `End of eval` 表示
整条链路已经跑通；单回合成功或失败都不能代表模型的稳定成功率。

日志和视频位于：

```text
outputs/eval/libero_spatial_task-0_n-1_seed-1000/
```

## 8. 运行公开基线

单任务多个回合：

```bash
bash scripts/eval_one.sh libero_spatial 0 3 1000
```

Quick-90：

```bash
bash scripts/eval_quick90.sh
```

Short-300：

```bash
bash scripts/eval_short300.sh
```

这些实验耗时明显更长。建议先完成一个回合的最小测试，再开始批量运行。

## 9. 下载训练数据并复现定向 LoRA

只做官方模型评测时不需要训练数据。要复现 `libero_goal/task_3` 的微调时再运行：

```bash
python scripts/download_libero_dataset.py
python scripts/verify_task3_dataset.py "${HOME}/datasets/lerobot/libero"
bash scripts/train_task3_lora.sh "${HOME}/datasets/lerobot/libero"
```

数据检查的预期结果是 36 个目标任务示范、7157 帧。LoRA 是一种省显存的训练方法：
它不重写全部 6.05 亿个模型参数，只训练约 29.4 万个小型附加参数。本项目的 rank-4
设置在 6GB 显存机器上峰值约 2.27GiB。

下载脚本把数据固定到 revision `a1aaacb`，该版本修正了元数据中的 episode 编号，
可避免“元数据说需要 382 号示范，但对应数据文件里却是 61 号”之类的不一致。

训练结束后，checkpoint 位于类似下面的目录：

```text
outputs/train/task3_lora_r4_s1790_bs4_seed1000/checkpoints/001790/pretrained_model
```

可用下面的命令评测：

```bash
bash scripts/eval_checkpoint.sh \
  outputs/train/task3_lora_r4_s1790_bs4_seed1000/checkpoints/001790/pretrained_model \
  libero_goal 3 10 20 holdout_seed20_r4_task3
```

## 10. 联网与离线模式

评测和训练脚本现在默认允许联网，以便新机器在缺少缓存时自动下载文件。确认模型与
资源均已缓存后，可主动禁止联网：

```bash
HF_HUB_OFFLINE=1 bash scripts/eval_one.sh libero_spatial 0 1 1000
```

如果一开始就设置 `HF_HUB_OFFLINE=1`，本地又没有模型缓存，程序一定会报找不到文件。

## 常见问题

### `apt update` 返回 403 或“没有数字签名”

通常是当前 Ubuntu 镜像站拒绝连接或配置失效。把 `/etc/apt/sources.list` 中失效的
镜像换成可访问的 HTTPS 官方源或其他可信镜像，再运行 `sudo apt update`。不要用
“忽略签名检查”来绕过，因为那会失去软件来源验证。

### `dpkg/lock-frontend` 被 `unattended-upgr` 占用

系统正在自动更新。等待它完成后重试即可。不要直接删除锁文件；强行删除可能让软件包
数据库处于半安装状态。

### 代理地址报 `Unknown scheme for proxy URL('socks://...')`

把代理协议写成 HTTPX 能识别的形式，例如：

```bash
export HTTPS_PROXY=socks5://127.0.0.1:7897
export HTTP_PROXY=socks5://127.0.0.1:7897
```

脚本会安装 SOCKS 支持。如果不需要代理，可临时 `unset HTTP_PROXY HTTPS_PROXY
ALL_PROXY`。端口要按自己的代理软件设置填写。

### 下载中出现 `SSL UNEXPECTED_EOF`、Xet token 错误或断线

本项目下载脚本默认关闭 Xet、把并发数降到 1，并把超时延长到 600 秒。重新执行原命令
即可续传。也可以先换稳定的代理节点，再重跑；不要删除已经下载的目录。

### 找不到 `libero_tabletop_base_style.xml`

说明 LIBERO 仿真素材未完整放进运行时目录。重新运行：

```bash
python scripts/download_libero_assets.py
bash scripts/check_environment.sh
```

### CUDA 显存不足

确认评测脚本使用 `MUJOCO_GL=osmesa`、并行环境数为 1、评测 batch size 为 1。关闭浏览器
或其他占用显存的程序。训练时先使用默认 rank 4、batch size 4；仍不足可把 batch size
降为 2 或 1，但要在实验记录中注明改变。

### 视频提示缺少 H.264 High Profile 解码器

先尝试命令行播放器：

```bash
ffplay -autoexit outputs/你的运行目录/videos/任务目录/eval_episode_0.mp4
```

如桌面播放器仍不能打开，可转成兼容性更好的 H.264 版本：

```bash
ffmpeg -i input.mp4 -c:v libx264 -profile:v baseline -pix_fmt yuv420p output_compatible.mp4
```

### GitHub 网页能打开，但 `git push` 的 TLS 或 SSH 连接失败

浏览器和 Git 不一定使用同一套代理设置。优先修复 Git 的 HTTPS 证书链，或配置 Git SSH
通过自己的 SOCKS5 代理连接。不要关闭 SSL 证书验证，也不要把 token 或私钥提交到仓库。

## 可复现边界

`constraints-repro.txt` 记录实验中最重要的已验证版本，但没有冻结每一个间接依赖包。
GPU 型号、驱动版本、下载到的上游模型文件以及模拟器随机初始状态也可能影响运行时间或
单次结果。因此应比较多回合成功率，而不是把一次成功当作稳定结论。
