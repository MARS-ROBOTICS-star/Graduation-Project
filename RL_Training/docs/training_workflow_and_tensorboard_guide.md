# 完整车 RL 训练操作说明

## 适用范围

本说明面向当前完整车 Isaac Lab + RSL-RL 训练项目，覆盖以下内容：

- 训练脚本启动指令
- TensorBoard 查看指令
- 策略回放指令
- 训练结果本地保存位置
- TensorBoard 图表读法

当前 direct 任务 ID 为：

```text
Complete-Car-Stage0-Flat-Direct-v0
Complete-Car-Stage1-Terrain-Direct-v0
Complete-Car-Stage2-Perception-Direct-v0
```

当前训练项目根目录为：

```text
/home/ubuntu/Graduation-Project/RL_Training
```

---

## 1. 训练前准备

先进入环境并切到训练项目目录：

```bash
conda activate env_isaacLab
cd /home/ubuntu/Graduation-Project/RL_Training
export OMNI_KIT_ACCEPT_EULA=YES
```

如果本项目还没有做 editable install，先执行一次：

```bash
python -m pip install -e . --no-build-isolation
```

---

## 2. 训练启动指令

### 2.1 最常用训练指令

```bash
cd /home/ubuntu/Graduation-Project/RL_Training
python scripts/rsl_rl/train.py \
  --task Complete-Car-Stage0-Flat-Direct-v0 \
  --num_envs 100 \
  --headless
```

含义：

- `--task Complete-Car-Stage0-Flat-Direct-v0`
  - 启动当前 direct Stage0 平地 baseline
- `--headless`
  - 不开可视化窗口
- `--device cuda:0`
  - 使用第 1 张 GPU 跑训练

### 2.2 冒烟测试训练指令

如果只想先确认训练链路能否启动，不想直接跑满默认轮数：

```bash
python scripts/rsl_rl/train.py --task Complete-Car-Stage0-Flat-Direct-v0 --headless --device cuda:0 --num_envs 100 --max_iterations 10
```

### 2.3 常用可调参数

训练脚本支持的常见参数可通过以下命令查看：

```bash
python scripts/rsl_rl/train.py --help
```

当前常用参数包括：

- `--num_envs`
  - 指定并行环境数量
- `--max_iterations`
  - 指定 PPO 训练轮数
- `--seed`
  - 指定随机种子
- `--resume`
  - 从已有 checkpoint 继续训练
- `--load_run`
  - 指定已有 run 目录
- `--checkpoint`
  - 指定恢复的 checkpoint 文件

---

## 3. 本地结果保存在哪里

每次训练的本地结果默认保存在：

```text
logs/rsl_rl/complete_car_stage0_flat_direct/YYYY-MM-DD_HH-MM-SS/
```

一个典型 run 目录中常见文件如下：

- `events.out.tfevents.*`
  - TensorBoard 原始事件文件
- `model_0.pt`
- `model_50.pt`
- `model_100.pt`
- `model_149.pt`
  - 训练保存的 checkpoint
- `params/env.yaml`
  - 本次 run 的环境配置快照
- `params/agent.yaml`
  - 本次 run 的 PPO 配置快照
- `git/Graduation-Project.diff`
  - 本次 run 对应的工作区代码差异快照
- `tensorboard_export/summary.json`
  - TensorBoard 离线导出总览
- `tensorboard_export/latest_values.csv`
  - 各标量的最新值
- `tensorboard_export/scalars/*.csv`
  - 每条曲线对应的本地 CSV

也就是说：

- TensorBoard 数据已经存到本地
- 网页 TensorBoard 只是读取这些本地 event 文件并可视化
- 即使不开网页，也可以直接分析导出的 `csv/json`

---

## 4. 查看 TensorBoard 的指令

### 4.1 最常用查看命令

```bash
tensorboard --logdir /home/ubuntu/Graduation-Project/RL_Training/logs/rsl_rl/complete_car_stage0_flat_direct
```

启动后浏览器通常访问：

```text
http://localhost:6006
```

### 4.2 远程机器常用命令

如果需要从其他机器访问：

```bash
tensorboard --logdir /home/ubuntu/Graduation-Project/RL_Training/logs/rsl_rl/complete_car_stage0_flat_direct --bind_all
```

### 4.3 如果 TensorBoard 启动报 `pkg_resources` 错误

当前 `env_isaacLab` 中，`tensorboard 2.20.0` 需要 `setuptools < 81`。

如果再次出现如下报错：

```text
ModuleNotFoundError: No module named 'pkg_resources'
```

可使用本机已有缓存离线修复：

```bash
conda install -n env_isaacLab --offline -y /home/ubuntu/miniconda3/pkgs/setuptools-80.10.2-py311h06a4308_0.conda
```

---

## 5. 策略回放指令

### 5.1 最简单的回放命令

```bash
python scripts/rsl_rl/play.py --task Complete-Car-Stage0-Flat-Direct-v0 
```

这条命令适合快速验证当前任务的播放链路是否正常。

### 5.2 指定某次 run 和某个 checkpoint 回放

例如回放一次指定 run 的最终模型：

```bash
python scripts/rsl_rl/play.py --task Complete-Car-Stage0-Flat-Direct-v0 --load_run 2026-04-06_17-40-38 --checkpoint model_149.pt
```

如果希望少开一些并行环境，便于观察：

```bash
python scripts/rsl_rl/play.py --task Complete-Car-Stage0-Flat-Direct-v0 --num_envs 32 --load_run 2026-04-06_17-40-38 --checkpoint model_149.pt
```

如需查看完整参数：

```bash
python scripts/rsl_rl/play.py --help
```

---

## 6. 键盘控制脚本指令

### 6.1 最简单的键盘控制启动命令

```bash
cd /home/ubuntu/Graduation-Project
python scripts/isaac_sim/control_keyboard.py
```

这条命令会启动完整车键盘控制脚本，不额外注入地形。
该脚本默认走 Isaac Sim 的 GPU 运行路径，不提供单独的 CPU 运行模式。

### 6.2 在指定地形上启动键盘控制

在训练同款 `stage1` 大地图上启动：

```bash
cd /home/ubuntu/Graduation-Project
python scripts/isaac_sim/control_keyboard.py --terrain stage1
```


### 6.3 当前可选地形

当前 `control_keyboard.py` 支持的 `--terrain` 选项包括：

- `none`
- `stage1`

如需查看完整参数：

```bash
python scripts/isaac_sim/control_keyboard.py --help
```

补充说明：

- 当前仓库状态下，键盘控制脚本只保留 `none` 和 `stage1`
- 之前脚本里暴露过的 `gap`、`stage2`、`both` 等选项依赖旧的 `scripts/isaac_sim/terrain_preview/` 源码；这些源码当前不在工作区内，因此不再作为可用入口写入文档
- 如果只是想看单块或分离画廊地形，请改用下面的地形查看脚本

---

## 7. 地形查看脚本指令

### 7.1 查看整张 stage1 大地图

```bash
cd /home/ubuntu/Graduation-Project
python scripts/isaac_sim/preview_stage1_terrain.py
```

常见用法：

- 查看指定焦点 tile：

```bash
python scripts/isaac_sim/preview_stage1_terrain.py --row 0 --col 0
```

- 在焦点 tile 上同时放车：

```bash
python scripts/isaac_sim/preview_stage1_terrain.py --row 0 --col 0 --spawn-car
```


### 7.2 查看 stage1 单块或全部 tile 分离画廊

默认查看当前 `20 x 10` 全部 tile 分离画廊：

```bash
cd /home/ubuntu/Graduation-Project
python scripts/isaac_sim/preview_stage1_tile.py
```

只看一块指定 tile：

```bash
python scripts/isaac_sim/preview_stage1_tile.py --single-tile --row 0 --col 0
```

只看某一类地形：

```bash
python scripts/isaac_sim/preview_stage1_tile.py --single-tile --terrain-name gap
```

列出当前支持的地形名：

```bash
python scripts/isaac_sim/preview_stage1_tile.py --list-terrains
```

### 7.3 查看 stage1 后六类地形

默认查看后六类地形组成的 `20 x 10` gallery：

```bash
cd /home/ubuntu/Graduation-Project
python scripts/isaac_sim/preview_stage1_last_six.py
```

只看其中某一类：

```bash
python scripts/isaac_sim/preview_stage1_last_six.py --single-tile --terrain-name pit
```

列出“后六类地形”名字：

```bash
python scripts/isaac_sim/preview_stage1_last_six.py --list-terrains
```

### 7.4 地形查看脚本的使用建议

当前建议这样选入口：

- 想看训练时整张大地图：`preview_stage1_terrain.py`
- 想看全部 tile 的分离几何：`preview_stage1_tile.py`
- 想重点看后六类复杂地形：`preview_stage1_last_six.py`
- 想边看车边做手动联调：`control_keyboard.py --terrain stage1`

---

## 8. TensorBoard 图怎么读

### 8.1 先看横轴和纵轴

在 `Scalars` 页面里，默认重点看：

- 横轴：`step`
  - 对当前训练基本可理解为第几次 PPO iteration
- 纵轴：该指标在该 iteration 记录时的数值

不建议一上来就把平滑开太高。  
先把 `Smoothing` 调低，再看原始趋势。

### 8.2 先看哪几张图

对当前第 1 阶段 `flat-only` baseline，优先看这 6 条：

- `Train/mean_reward`
- `Train/mean_episode_length`
- `Episode_Termination/time_out`
- `Episode_Termination/root_too_low`
- `Episode_Reward/track_lin_vel_xy`
- `Episode_Reward/track_ang_vel_z`

---

## 9. 这 6 条图分别是什么意思

### 9.1 `Train/mean_reward`

含义：

- 平均总奖励

横轴：

- PPO iteration

纵轴：

- 当前统计窗口下的平均总 reward

怎么判断：

- 持续上升通常是好现象
- 长期不升或大幅震荡通常说明策略没有稳定学到目标行为

### 9.2 `Train/mean_episode_length`

含义：

- 平均 episode 长度

横轴：

- PPO iteration

纵轴：

- 平均每个 episode 持续了多少个控制步

怎么判断：

- 对当前任务非常关键，越长通常越好
- 上升说明策略更能稳定活下来

当前配置中：

- `episode_length_s = 8.0`
- `dt = 1/120`
- `decimation = 2`

所以单回合理论上限约为：

```text
8 / (1/120 * 2) = 480 步
```

如果这条曲线接近 `480`，通常说明大部分 episode 已经能正常活到超时。

### 9.3 `Episode_Termination/time_out`

含义：

- 因为“正常跑满时长”而结束的比例

横轴：

- PPO iteration

纵轴：

- 当前统计窗口内因 `time_out` 结束的 episode 比例

怎么判断：

- 越接近 `1.0` 越好
- 上升说明提前失败越来越少

### 9.4 `Episode_Termination/root_too_low`

含义：

- 因根部高度过低而终止的比例

横轴：

- PPO iteration

纵轴：

- 当前统计窗口内因 `root_too_low` 结束的 episode 比例

怎么判断：

- 越接近 `0.0` 越好
- 高说明车体经常趴地、翻倒或姿态崩坏

### 9.5 `Episode_Reward/track_lin_vel_xy`

含义：

- 线速度跟踪奖励

横轴：

- PPO iteration

纵轴：

- 当前统计窗口内该奖励项的平均值

怎么判断：

- 越高越好
- 如果 `mean_episode_length` 在涨，但这条不涨，说明策略可能只是学会了“活着”，还没真正学会执行速度命令

### 9.6 `Episode_Reward/track_ang_vel_z`

含义：

- 偏航角速度跟踪奖励

横轴：

- PPO iteration

纵轴：

- 当前统计窗口内该奖励项的平均值

怎么判断：

- 越高越好
- 如果这条明显低于 `track_lin_vel_xy`，通常说明策略“会走，但转向学得还不够好”

---

## 10. 推荐的读图顺序

建议按下面顺序判断一次训练是否正常：

1. 先看是否能活下来
   - `Train/mean_episode_length`
   - `Episode_Termination/time_out`
   - `Episode_Termination/root_too_low`
2. 再看是否学会任务
   - `Episode_Reward/track_lin_vel_xy`
   - `Episode_Reward/track_ang_vel_z`
   - `Train/mean_reward`
3. 最后再看更细的稳定性和优化项
   - `Episode_Reward/body_orientation`
   - `Episode_Reward/lin_vel_z`
   - `Episode_Reward/ang_vel_xy`
   - `Episode_Reward/action_rate`
   - `Loss/value`
   - `Loss/surrogate`

---

## 11. 一个最短操作流程

### 11.1 跑训练

```bash
conda activate env_isaacLab
cd /home/ubuntu/Graduation-Project/RL_Training
export OMNI_KIT_ACCEPT_EULA=YES
python scripts/rsl_rl/train.py --task Complete-Car-Stage0-Flat-Direct-v0 --headless --device cuda:0
```

### 11.2 开 TensorBoard

```bash
tensorboard --logdir /home/ubuntu/Graduation-Project/RL_Training/logs/rsl_rl/complete_car_stage0_flat_direct
```

### 11.3 回放某次训练结果

```bash
python scripts/rsl_rl/play.py --task Complete-Car-Stage0-Flat-Direct-v0 --device cuda:0 --num_envs 32 --load_run 2026-04-06_17-40-38 --checkpoint model_149.pt
```

### 11.4 用键盘控制做联调

```bash
cd /home/ubuntu/Graduation-Project
python scripts/isaac_sim/control_keyboard.py --terrain stage1
```

### 11.5 查看地形

```bash
cd /home/ubuntu/Graduation-Project
python scripts/isaac_sim/preview_stage1_terrain.py
python scripts/isaac_sim/preview_stage1_tile.py --list-terrains
python scripts/isaac_sim/preview_stage1_last_six.py --list-terrains
```

### 11.6 直接看本地离线结果

先看：

- `tensorboard_export/summary.json`
- `tensorboard_export/latest_values.csv`

再按需要看：

- `tensorboard_export/scalars/*.csv`

---

## 12. 相关文档

- [RL 训练策略](./rl_training_route.md)
- [TensorBoard 读图说明](./tensorboard_reading_guide.md)
