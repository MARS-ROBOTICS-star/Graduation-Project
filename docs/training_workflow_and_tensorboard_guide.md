# 完整车 RL 训练与 TensorBoard 简明说明

## 适用范围

本文档只针对当前活跃训练主线：

- 训练工程目录：`/home/ubuntu/Graduation-Project/RL_Training`
- 训练脚本：`scripts/train.py`
- 回放脚本：`scripts/play.py`
- 任务 ID：
  - `CompleteCar-Stage0`
  - `CompleteCar-Stage1`
  - `CompleteCar-Stage2`

---

## 1. 训练前准备

进入 Isaac Lab Python 环境后执行：

```bash
cd /home/ubuntu/Graduation-Project/RL_Training
pip install -e source/complete_car_lab
```

---

## 2. 训练

最常用训练命令：

```bash
cd /home/ubuntu/Graduation-Project/RL_Training
python scripts/train.py --task CompleteCar-Stage0 --headless
```

常用变体：

```bash
python scripts/train.py --task CompleteCar-Stage1 --headless
python scripts/train.py --task CompleteCar-Stage2 --headless
python scripts/train.py --task CompleteCar-Stage0 --headless --num_envs 64 --max_iterations 5
```

说明：

- `--headless`
  - 不开可视化窗口
- `--num_envs`
  - 指定并行环境数
- `--max_iterations`
  - 指定训练轮数，适合冒烟测试

---

## 3. 回放

指定 checkpoint 回放：

```bash
cd /home/ubuntu/Graduation-Project/RL_Training
python scripts/play.py --task CompleteCar-Stage0 --checkpoint /path/to/model.pt
```

如果只知道某次 run 目录，也可以这样：

```bash
python scripts/play.py --task CompleteCar-Stage0 --load_run <run_dir_name>
```

---

## 4. 日志与 checkpoint 位置

训练日志默认写入：

```text
RL_Training/logs/rsl_rl/<experiment_name>/<run_dir>/
```

如果从仓库根目录写成绝对路径，就是：

```text
/home/ubuntu/Graduation-Project/RL_Training/logs/rsl_rl/<experiment_name>/<run_dir>/
```

当前各阶段默认实验名为：

- `CompleteCar-Stage0` -> `complete_car_stage0`
- `CompleteCar-Stage1` -> `complete_car_stage1`
- `CompleteCar-Stage2` -> `complete_car_stage2`

因此常见目录例如：

```text
RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_12-00-00/
```

`run_dir` 的命名规则来自 `train.py`：

- 默认就是训练启动时的时间戳：`YYYY-MM-DD_HH-MM-SS`
- 如果命令里额外传了 `--run_name xxx`
  - 实际目录会变成：`YYYY-MM-DD_HH-MM-SS_xxx`

这意味着每次训练结果都会落到一个独立目录里，按“阶段实验名/启动时间戳”分开保存。

例如本次训练 `2026-04-14_20-52-07` 的实际保存位置是：

```text
/home/ubuntu/Graduation-Project/RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_20-52-07/
```

一个 run 目录下通常会有：

- `events.out.tfevents.*`
- `model_*.pt`
- `params/env.yaml`
- `params/agent.yaml`
- `git/Graduation-Project.diff`

---

## 5. TensorBoard

查看全部训练：

```bash
cd /home/ubuntu/Graduation-Project/RL_Training
tensorboard --logdir logs/rsl_rl --port 6006 --bind_all
```

只看 Stage0：

```bash
tensorboard --logdir logs/rsl_rl/complete_car_stage0 --port 6006 --bind_all
```

浏览器地址通常是：

```text
http://localhost:6006
```

如果只想把标量离线导出为 CSV/JSON：

```bash
python -m complete_car_lab.tasks.direct.complete_car.utils.tensorboard_export \
  --run_dir logs/rsl_rl/complete_car_stage0/<run_dir_name>
```

---

## 6. 当前推荐最短流程

```bash
cd /home/ubuntu/Graduation-Project/RL_Training
pip install -e source/complete_car_lab
python scripts/train.py --task CompleteCar-Stage0 --headless --num_envs 64 --max_iterations 5
tensorboard --logdir logs/rsl_rl/complete_car_stage0 --port 6006 --bind_all
python scripts/play.py --task CompleteCar-Stage0 --checkpoint /path/to/model.pt
```
