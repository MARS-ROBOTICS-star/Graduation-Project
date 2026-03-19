# Isaac RL TensorBoard Reading Guide

## 适用范围

本说明面向当前完整车 Isaac Lab + RSL-RL 训练项目，目标是统一以下工作：

- 查看 Isaac Lab 日志
- 查看 Hydra / env / agent 配置
- 查看 TensorBoard 图表
- 查看自动导出的 `csv/json`
- 输出结构化训练诊断报告

## 先区分 4 类文件

### 1. Isaac Lab 模拟器日志

典型路径：

```text
/tmp/isaaclab/logs/isaaclab_YYYY-MM-DD_HH-MM-SS.log
```

作用：

- 判断 Isaac Sim / Isaac Lab 是否成功启动
- 判断 articulation、actuator、manager term 是否成功解析
- 判断是否存在 OOM、asset 加载失败、joint 名不匹配、PhysicsScene 复制问题

### 2. Hydra 配置快照

典型路径：

```text
outputs/YYYY-MM-DD/HH-MM-SS/.hydra/config.yaml
outputs/YYYY-MM-DD/HH-MM-SS/.hydra/overrides.yaml
```

作用：

- 确认本次 run 的解析后配置
- 重点检查 `device`、`num_envs`、`dt`、scene、reward、termination 等

### 3. 训练产物目录

典型路径：

```text
logs/rsl_rl/complete_car_rl_training/YYYY-MM-DD_HH-MM-SS/
```

作用：

- 保存 checkpoint
- 保存 TensorBoard event 文件
- 保存 `params/env.yaml` 与 `params/agent.yaml`

关键文件：

- `events.out.tfevents.*`
- `model_0.pt`
- `model_50.pt`
- `model_100.pt`
- `model_149.pt`

### 4. TensorBoard 离线导出目录

典型路径：

```text
logs/rsl_rl/complete_car_rl_training/YYYY-MM-DD_HH-MM-SS/tensorboard_export/
```

作用：

- 不依赖网页直接分析训练结果
- 为后续会话和诊断报告提供稳定输入

关键文件：

- `summary.json`
- `latest_values.csv`
- `scalars/*.csv`

## TensorBoard 网页如何看

启动：

```bash
tensorboard --logdir /home/ubuntu/Graduation-Project/src/rl_lab/complete_car_rl_training/logs/rsl_rl/complete_car_rl_training
```

浏览器地址通常是：

```text
http://localhost:6006
```

常用操作：

- 打开 `Scalars`
- 先把 `Smoothing` 调低，避免误判
- 横轴优先看 `step`
- 多个 run 同时勾选时比较不同时间戳曲线

## 本项目核心图表与含义

### A. 训练总体健康度

#### `Train/mean_reward`

含义：

- 平均总奖励

判断：

- 持续上升通常是好现象
- 长期不升或大幅振荡说明 reward 设计、动作尺度或观测存在问题

#### `Train/mean_episode_length`

含义：

- 平均 episode 长度

判断：

- 对当前完整车任务非常关键
- 上升说明 rollout 更能活下来
- 如果接近 `episode_length_s / dt / decimation` 对应上限，通常说明大量 episode 已正常活到 timeout

### B. 终止原因

#### `Episode_Termination/time_out`

含义：

- 因为正常超时结束的比例

判断：

- 上升到接近 `1.0`，通常说明环境存活性较好

#### `Episode_Termination/root_too_low`

含义：

- 车体过低、倒地或陷地导致终止的比例

判断：

- 应下降并尽量接近 `0.0`

#### `Episode_Termination/bad_orientation`

含义：

- 姿态越界导致终止的比例

判断：

- 应下降并尽量接近 `0.0`

#### `Episode_Termination/ball_joint_out_of_bounds`

含义：

- 球铰越过人工限制导致终止

判断：

- 在第 1 阶段 baseline 下通常应接近 `0.0`

### C. 任务目标相关奖励

#### `Episode_Reward/track_lin_vel_xy_exp`

含义：

- 线速度跟踪奖励

判断：

- 越高越好
- 如果 episode 长度在涨，但这条不涨，说明“只是活下来了”，不一定真的学会跟踪

#### `Episode_Reward/track_ang_vel_z_exp`

含义：

- 偏航角速度跟踪奖励

判断：

- 越高越好

### D. 稳定性与平顺性惩罚

#### `Episode_Reward/flat_orientation`

含义：

- 姿态稳定相关项

判断：

- 若为负项，越接近 `0` 越好

#### `Episode_Reward/lin_vel_z`

含义：

- 竖直方向速度惩罚

判断：

- 越接近 `0` 越好

#### `Episode_Reward/ang_vel_xy`

含义：

- 横滚 / 俯仰角速度惩罚

判断：

- 越接近 `0` 越好

#### `Episode_Reward/action_rate_l2`

含义：

- 动作变化过快惩罚

判断：

- 太负说明控制抖动大

### E. 误差指标

#### `Metrics/base_velocity/error_vel_xy`

含义：

- 线速度跟踪误差

判断：

- 越低越好

#### `Metrics/base_velocity/error_vel_yaw`

含义：

- 偏航跟踪误差

判断：

- 越低越好

### F. PPO 数值状态

#### `Loss/value`

含义：

- value 网络损失

判断：

- 一般希望下降或保持稳定
- 爆炸式增长通常不正常

#### `Loss/surrogate`

含义：

- PPO surrogate loss

判断：

- 会波动，但不应明显发散

#### `Loss/entropy`

含义：

- 策略随机性

判断：

- 太高说明仍很随机
- 太低可能探索不足

#### `Policy/mean_std`

含义：

- 策略动作分布标准差

判断：

- 越大表示策略更随机

### G. 性能指标

#### `Perf/total_fps`

- 训练吞吐速度

#### `Perf/collection_time`

- 数据采样耗时

#### `Perf/learning_time`

- 学习更新耗时

说明：

- 这些用于看速度，不用于判断策略质量

## 看图时的核心判断顺序

1. 先看 `Train/mean_episode_length`
2. 再看 `Episode_Termination/*`
3. 再看 `Train/mean_reward`
4. 再看 `Metrics/base_velocity/error_*`
5. 再拆开看 `Episode_Reward/*`
6. 最后检查 `Loss/*` 与 `Policy/mean_std`

原因：

- 先确认是不是“活着”
- 再确认是不是“正常结束”
- 再确认是不是“真的在学任务目标”
- 最后再看数值训练是否稳定

## 如何只靠本地导出文件做诊断

### `latest_values.csv`

用途：

- 快速看最后一步的所有核心指标

适合回答：

- 本次 run 最终是 `time_out` 主导，还是 `root_too_low` 主导
- 最终 reward 和 episode length 大概是多少

### `scalars/*.csv`

用途：

- 看完整趋势

字段：

- `wall_time`
- `step`
- `value`

适合回答：

- 某条曲线是持续改善、平台化，还是后期退化

### `summary.json`

用途：

- 汇总每个 tag 的首值、末值、步数和 CSV 路径

适合回答：

- 快速抓取本次 run 的全局概览

## 标准诊断报告模板

### 1. Run 概况

- 日志路径
- 对应 run 目录
- 设备
- `num_envs`
- `max_iterations`
- 是否成功生成 checkpoint

### 2. 环境启动结论

- articulation 是否成功初始化
- actuator / observation / reward / termination 是否成功解析
- 是否存在 asset、PhysicsScene、OOM、CUDA、driver、引用丢失问题

### 3. 核心训练结论

- `Train/mean_reward` 起点和终点
- `Train/mean_episode_length` 起点和终点
- 主要终止原因
- 当前是“活下来了”还是“开始学会跟踪了”

### 4. 奖励与误差解读

- 线速度跟踪奖励变化
- 偏航跟踪奖励变化
- 误差指标是否下降
- 惩罚项是否过大

### 5. 数值稳定性

- `Loss/value`
- `Loss/surrogate`
- `Loss/entropy`
- `Policy/mean_std`

### 6. 诊断结论

- 当前最主要进展
- 当前最主要问题
- 下一步最优先调整项

## 给 Codex 的最小输入

后续只需要提供：

- Isaac Lab 日志路径，例如 `/tmp/isaaclab/logs/isaaclab_2026-03-19_13-13-03.log`

Codex 应自动完成：

- 定位对应 run
- 读取日志、Hydra 配置、训练参数
- 如无 `tensorboard_export/`，先自动导出
- 读取 `latest_values.csv` 与关键 `scalars/*.csv`
- 输出训练诊断报告
