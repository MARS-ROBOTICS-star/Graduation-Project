# Stage1参数详情表

本文档记录 `RL_Training/` 工作区内 `CompleteCar-Stage1` 当前实际生效的 RL 环境配置、PPO 配置、warm-start 方式、地形课程、目标点、观测、高度图、奖励和终止逻辑。

本文档不记录底层运动学模型，不展开轮速分配、low-slip 平面命令整形、车轮牵引力矩分配或球铰规划器内部公式。本文只记录 policy 与环境交互层面的配置。

当前 Stage1 定义为：`best_baseline_2` warm-start terrain curriculum 阶段。

当前 `complete_car_stage1_cfg.py` 采用本阶段显式配置风格，但只保留 Stage1 直接相关或当前 active 的参数。terrain-column target 不再在 Stage1 配置中显式写入自由 waypoint 采样参数，例如 `commands.goal_distance` 和 `commands.goal_direction_max_deg`。

当前详表以当前源码配置为准。下列 run 是最近记录的 headless Stage1 warm-start 训练快照，用于说明当时的启动命令和日志位置：

- run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-04-29_07-37-58_stage1_warmstart_best_baseline_2_32env_best_per_terrain_chase_700iter`
- env 参数快照：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-04-29_07-37-58_stage1_warmstart_best_baseline_2_32env_best_per_terrain_chase_700iter/params/env.yaml`
- agent 参数快照：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-04-29_07-37-58_stage1_warmstart_best_baseline_2_32env_best_per_terrain_chase_700iter/params/agent.yaml`
- warm-start checkpoint：`RL_Training/logs/rsl_rl/complete_car_stage1/warmstart_best_baseline_2/model_0.pt`
- runtime log：`RL_Training/logs/runtime/stage1_32env_best_per_terrain_chase_setsid.log`

该 run 使用 `32` env、headless、`700` iterations、`best_baseline_2` warm-start，并启用按地形选择最佳 env 后依次录制 `120 s` chase 视频。2026-04-28 的 GUI run `2026-04-28_18-17-55_stage1_warmstart_best_baseline_2_32env_view_700iter` 已按用户要求在 PPO iteration `18/700` 后停止，只作为历史启动验证记录。

注意：上述 run 的 `env.yaml` 是启动时快照。2026-05-02 起，当前源码中的 Stage1 terrain column 映射已调整为第 `0` 列 `flat`，Stage1 源码默认动作映射也已调整为与 Stage0 相同的底盘物理速度输出范围；此前已经启动的 run 的 `params/env.yaml` 不会因源码修改自动改变，新启动的 Stage1 run 才会使用下文当前源码配置。

本文档中的“当前值”默认表示当前源码配置；若某个值来自训练命令覆盖或历史 run 快照，会在说明中单独标明。

## 0. 对应源码

| 模块 | 路径 |
|---|---|
| gym task 注册 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/__init__.py` |
| Stage1 配置覆盖 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py` |
| 共享配置主干 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py` |
| 环境主类 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py` |
| 动作映射 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py` |
| 目标点采样 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py` |
| 观测拼接 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py` |
| reward 计算 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py` |
| termination 计算 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py` |
| curriculum 更新 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/curriculum.py` |
| reset 逻辑 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/resets.py` |
| terrain 配置 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py` |
| terrain 生成 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_builder.py` |
| terrain runtime | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_runtime.py` |
| sensor 配置 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py` |
| PPO 配置 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py` |
| Stage0 到 Stage1 warm-start 转换 | `RL_Training/scripts/convert_stage0_to_stage1_warmstart.py` |
| 训练入口 | `RL_Training/scripts/train.py` |

## 1. Stage1 总览

| 参数 | 当前值 | 含义 |
|---|---:|---|
| task id | `CompleteCar-Stage1` | Stage1 地形课程任务 |
| `stage_name` | `stage1` | 环境内部阶段名 |
| `scene.num_envs` | `32` | Stage1 源码默认并行环境数，训练入口可用 `--num_envs` 覆盖 |
| `scene.env_spacing` | `2.0 m` | 环境克隆间距 |
| `action_space` | `8` | policy 动作维度 |
| `observation_space.actor` | `632` | actor 观测维度 |
| `observation_space.critic` | `632` | critic 观测维度 |
| `state_space` | `0` | 当前不使用额外 privileged state |
| `episode_length_s` | `40.0 s` | 单个 episode 最大时长 |
| `control.sim_dt` | `1 / 120 s` | PhysX 仿真步长 |
| `decimation` | `2` | 每 2 个 sim step 执行一次 RL action |
| `control.control_dt` | `1 / 60 s` | RL 控制周期 |
| `max_episode_length` | `2400` | `40 s * 60 Hz` |
| `is_finite_horizon` | `False` | timeout 作为 RSL-RL time-limit，可做 bootstrap |
| `terrain.enabled` | `True` | 启用地形 |
| `terrain.mode` | `generator` | 使用 Stage1 terrain generator |
| `curriculum.enabled` | `True` | 启用地形课程 |
| `terrain.measure_heights` | `True` | 向 actor / critic 拼入地形高度 patch |
| `observations.noise.enabled` | `False` | 当前不注入观测噪声 |
| `randomization.enable_action_randomization` | `False` | 当前不注入 action 随机化 |
| `sensors.imu.enabled` | `False` | IMU 不参与策略输入 |
| `sensors.stereo_camera.enabled` | `False` | 双目相机不参与策略输入 |
| `sensors.lidar.enabled` | `False` | 激光雷达不参与策略输入 |
| `sensors.enable_height_scanner` | `False` | 不用 RayCaster 传感器生成高度图 |
| `debug.enable_debug_draw` | `True` | 开启目标点 marker 等 debug draw |
| `debug.visualize_goal_heading` | `True` | 绘制目标方向箭头 |
| `debug.visualize_wheel_slip` | `True` | 源码默认绘制 wheel-slip 箭头，训练命令可临时关闭 |
| `debug.create_follow_views` | `True` | 创建 top / chase 跟踪视角 |

## 2. PPO 与 warm-start

### 2.1 PPO runner

| 参数 | 当前值 | 含义 |
|---|---:|---|
| runner | `OnPolicyRunner` | RSL-RL on-policy runner |
| `experiment_name` | `complete_car_stage1` | 日志根目录名 |
| `run_name` | `""` | Stage1 PPO cfg 默认 run 名；当前 headless 命令用 `--run_name` 覆盖 |
| 当前命令 `run_name` 覆盖 | `stage1_warmstart_best_baseline_2_32env_best_per_terrain_chase_700iter` | 最近记录的 headless warm-start run 名 |
| `seed` | `1` | 随机种子 |
| `device` | `cuda:0` | 训练设备 |
| `num_steps_per_env` | `512` | 每次 PPO rollout 的每环境步数 |
| `max_iterations` | `700` | 计划 PPO iteration 数 |
| `save_interval` | `25` | checkpoint 保存间隔 |
| `logger` | `tensorboard` | 日志后端 |
| `obs_groups` | `actor: ["actor"], critic: ["critic"]` | actor / critic 分别读取同名观测组 |
| `clip_actions` | `None` | wrapper 层不再额外 clip action |
| `check_for_nan` | `True` | PPO 检查 NaN |

### 2.2 网络结构

| 网络 | 当前值 |
|---|---|
| actor class | `MLPModel` |
| critic class | `MLPModel` |
| actor hidden dims | `[256, 256]` |
| critic hidden dims | `[256, 256]` |
| activation | `relu` |
| actor obs normalization | `True` |
| critic obs normalization | `True` |
| actor distribution | `SquashedGaussianDistribution` |
| actor `init_std` | `0.20` |
| actor `log_std_min` | `-4.0` |
| actor `log_std_max` | `0.0` |

### 2.3 PPO algorithm 参数

| 参数 | 当前值 |
|---|---:|
| `num_learning_epochs` | `5` |
| `num_mini_batches` | `16` |
| `learning_rate` | `1.0e-4` |
| `adam_eps` | `1.0e-5` |
| `schedule` | `adaptive` |
| `gamma` | `0.99` |
| `lam` | `0.95` |
| `entropy_coef` | `5.0e-4` |
| `desired_kl` | `0.008` |
| `max_grad_norm` | `0.5` |
| `value_loss_coef` | `0.5` |
| `use_clipped_value_loss` | `True` |
| `clip_param` | `0.2` |

### 2.4 warm-start 来源

| 项目 | 值 |
|---|---|
| Stage0 来源 run | `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-28_15-28-38_best_baseline_2` |
| Stage0 来源 checkpoint | `model_699.pt` |
| Stage0 actor / critic obs dim | `54` |
| Stage1 actor / critic obs dim | `632` |
| Stage1 warm-start checkpoint | `RL_Training/logs/rsl_rl/complete_car_stage1/warmstart_best_baseline_2/model_0.pt` |
| Stage1 warm-start 加载方式 | `--warmstart` |

Stage0 checkpoint 不能直接作为 Stage1 resume 使用，因为 actor / critic 第一层输入维度和 obs normalizer 维度不同。当前转换方式是：

- actor / critic 第一层从 `54` 维扩展到 `632` 维。
- 前 `54` 维继承 Stage0 权重。
- 新增高度图维度的第一层权重初始化为 `0`。
- obs normalizer 的新增维度均值为 `0`，方差和标准差为 `1`。
- `--warmstart` 只加载 actor / critic，不加载 optimizer 和 iteration。

当前 `convert_stage0_to_stage1_warmstart.py` 的默认 `target_obs_dim` 已同步为 `632`。按当前 Stage1 环境重新生成 warm-start checkpoint 时，不再需要额外传入 `--target_obs_dim 632`。若后续 Stage1 观测维度再次变化，必须同步修改转换脚本默认值和本文档。

当前 headless warm-start 训练命令口径：

```bash
python scripts/train.py --task CompleteCar-Stage1 --headless --device cuda:0 --num_envs 32 --resume --warmstart --load_run warmstart_best_baseline_2 --checkpoint model_0.pt --max_iterations 700 --run_name stage1_warmstart_best_baseline_2_32env_best_per_terrain_chase_700iter --record_terrain_chase_videos --terrain_chase_video_length_s 120 --terrain_chase_video_mode per_name --terrain_chase_selection_steps 600 --follow_all_envs --hide_goal_heading --hide_wheel_slip_vis
```

### 2.5 Stage1 回放列选择

当前 `scripts/play.py` 已支持 Stage1 按地形列回放。新增参数为：

| 参数 | 默认值 | 含义 |
|---|---|---|
| `--terrain_replay_columns` | `all` | Stage1 回放出生地形列选择；可取 `all`、单列编号、列编号列表或地形名 |

当前地形列编号仍为：

| 列编号 | 地形 |
|---:|---|
| `0` | `flat` |
| `1` | `slope down` |
| `2` | `slope up` |
| `3-4` | `uneven rough` |
| `5-6` | `stairs down` |
| `7-8` | `stairs up` |
| `9` | `discrete obstacles` |

使用 `all` 时，回放会按 env id 轮转分配到所有 `0-9` 列；因此 `--num_envs` 至少需要为 `10`。指定单列时，所有 env 都出生在该列；指定重复地形名时，会覆盖该地形对应的所有列，例如 `stairs_up` 对应 `7,8`。

`--checkpoint model_699.pt` 这类裸 checkpoint 文件名会结合 `--load_run` 在对应 run 目录下解析；如果传入绝对路径、带目录的相对路径或 URI，则仍按显式 checkpoint 路径读取。

全地形回放示例：

```bash
python scripts/play.py --task CompleteCar-Stage1 --device cuda:0 --num_envs 10 --load_run 2026-05-03_02-17-59_stage1_resume_from125_ppo_guard_to700 --checkpoint model_699.pt --terrain_replay_columns all --create_follow_views
```

指定单列回放示例：

```bash
python scripts/play.py --task CompleteCar-Stage1 --device cuda:0 --num_envs 4 --load_run 2026-05-03_02-17-59_stage1_resume_from125_ppo_guard_to700 --checkpoint model_699.pt --terrain_replay_columns 7 --create_follow_views
```

按地形名回放示例：

```bash
python scripts/play.py --task CompleteCar-Stage1 --device cuda:0 --num_envs 4 --load_run 2026-05-03_02-17-59_stage1_resume_from125_ppo_guard_to700 --checkpoint model_699.pt --terrain_replay_columns stairs_up --create_follow_views
```

## 3. 场景与仿真

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `scene.num_envs` | `32` | Stage1 源码默认环境数，训练入口可用 `--num_envs` 覆盖 |
| `scene.env_spacing` | `2.0 m` | 克隆环境间距 |
| `scene.replicate_physics` | `True` | 克隆环境复用物理配置 |
| `scene.clone_in_fabric` | `True` | 使用 Fabric clone |
| `sim.device` | `cuda:0` | 仿真设备 |
| `sim.dt` | `0.008333333333333333 s` | 120 Hz 仿真步长 |
| `sim.render_interval` | `2` | 每 2 个 sim step 渲染一次 |
| `sim.gravity` | `(0.0, 0.0, -9.81)` | 重力 |
| `sim.use_fabric` | `True` | 启用 Fabric |
| `sim.physics_material.static_friction` | `1.0` | 全局静摩擦 |
| `sim.physics_material.dynamic_friction` | `1.0` | 全局动摩擦 |
| `sim.physics_material.restitution` | `0.0` | 恢复系数 |
| `sim.physx.solver_type` | `1` | TGS solver |
| `sim.physx.max_position_iteration_count` | `8` | 位置迭代数 |
| `sim.physx.max_velocity_iteration_count` | `4` | 速度迭代数 |
| `sim.physx.bounce_threshold_velocity` | `0.2` | 低速接触反弹阈值 |
| `sim.physx.friction_offset_threshold` | `0.04` | 摩擦接触生成距离阈值 |
| `sim.physx.friction_correlation_distance` | `0.025` | 近邻接触点摩擦关联距离 |
| `sim.physx.enable_stabilization` | `True` | 物理稳定化 |

## 4. 动作空间

总动作维度为 `8`。

| 动作分量 | 维度 | 环境层语义 |
|---|---:|---|
| `actions[:, 0]` | `1` | 底盘前向速度归一化命令 |
| `actions[:, 1]` | `1` | 底盘 yaw rate 归一化命令 |
| `actions[:, 2:8]` | `6` | 两组等效球铰目标姿态归一化命令 |

Stage1 当前与 Stage0 保持相同的底盘物理速度输出范围，并允许倒车：

$$
v_x^d = a_0 \cdot 2.0
$$

因此当 actor 输出 $a_0 \in [-1, 1]$ 时，$v_x^d \in [-2.0, 2.0]\ \mathrm{m/s}$。

yaw rate 映射为：

$$
\omega_z^d = a_1 \cdot 2.0
$$

因此 $\omega_z^d \in [-2.0, 2.0]\ \mathrm{rad/s}$。

球铰动作按默认零位、lower limit、upper limit 映射成目标姿态。当前受控球铰顺序为：

| 序号 | 关节名 | lower | upper |
|---:|---|---:|---:|
| 1 | `spm1_platform_joint_z` | `-0.7` | `0.7` |
| 2 | `spm1_platform_joint_y` | `-1.6` | `0.5` |
| 3 | `spm1_platform_joint_x` | `-0.5` | `0.5` |
| 4 | `spm2_platform_joint_z` | `-0.7` | `0.7` |
| 5 | `spm2_platform_joint_y` | `-1.6` | `0.5` |
| 6 | `spm2_platform_joint_x` | `-0.5` | `0.5` |

本文档到这里为止只记录 policy 输出接口。动作进入底层执行链后的具体运动学和力矩分配逻辑不在本文档范围内。

## 5. 目标点与 command

### 5.1 command 维度

`commands.num_commands = 4`，actor / critic 中的目标命令为车体系相对目标：

| 分量 | 含义 |
|---|---|
| `goal_rel_x` | 当前 active waypoint 相对车体的 x 坐标 |
| `goal_rel_y` | 当前 active waypoint 相对车体的 y 坐标 |
| `goal_rel_z` | 当前 active waypoint 相对车体的高度差 |
| `goal_rel_heading` | 当前 waypoint 的视线方向，计算为 `atan2(goal_rel_y, goal_rel_x)` |

### 5.2 Stage1 目标点采样

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `commands.num_waypoints_per_episode` | `1` | 每个 episode 只有一个 active waypoint |
| `commands.use_terrain_column_targets` | `True` | 使用 terrain row / column 目标点 |
| `commands.resampling_time` | `5.0 s` | 继承自共享配置；terrain-column 目标路径不使用该计时重采样 |
| `commands.terrain_goal_min_row_offset` | `1` | 目标至少在前方 1 行 |
| `commands.terrain_goal_max_row_offset` | `1` | 目标最多在前方 1 行 |
| `commands.terrain_goal_lateral_range_m` | `3.0 m` | 目标 y 坐标在同列 tile origin 左右随机偏移 |
| `commands.terrain_goal_lateral_offset_excluded_names` | `stairs down`, `stairs up`, `discrete obstacles` | 这些地形目标 x / y 直接取下一行同列 tile origin，不做 y 偏移 |

Stage1 目标点逻辑：

1. 读取当前 env 的 terrain level 作为当前 row。
2. 读取当前 env 的 terrain type 作为当前 column。
3. 目标 row 固定取当前 row 的 `+1`；若该目标会超过最大 row，视为环境逻辑错误，不再夹紧到当前最后 row。
4. 目标 column 保持不变。
5. 目标世界坐标的 x / y 先取目标 tile origin。
6. 除 `stairs down`、`stairs up`、`discrete obstacles` 外，目标 y 再加上 `[-3 m, 3 m]` 均匀随机扰动。
7. `stairs down`、`stairs up`、`discrete obstacles` 的目标 x / y 保持目标 tile origin 原值。
8. 目标 z 由 terrain heightfield 在目标 x / y 处采样。
9. 目标 heading 固定为 `0 rad`，即世界系 `+x`。

目标点在 Stage1 的作用是提供沿地形列向前的运动引导，不作为必须完成的 episode 终点。terrain-column 目标不使用 `commands.resampling_time` 的计时重采样；目标推进由事件触发：

- 当前目标距离小于 `target_position_tolerance = 0.5 m` 时，触发 terrain row 推进。
- 目标重采样后仍保持同列，目标 row 继续取当前 row 的 `+1`。
- 若本次推进会进入没有合法下一目标的最高 row 区域，则本段记为完成，通过 reset 回到新的低 row，不再采样被夹紧到同一最后 row 的假目标。
- 目标命中不会触发 Stage1 success termination。

### 5.3 继承但当前不参与 Stage1 terrain-column 目标采样的 command 字段

| 字段 | 继承值 | 当前作用 |
|---|---:|---|
| `commands.goal_distance` | `20 m` | 不用于 Stage1 terrain-column 目标采样 |
| `commands.goal_direction_max_deg` | `18.43 deg` | 不用于 Stage1 terrain-column 目标采样；转向惩罚角度尺度由 `rewards.params.turn_speed_angle_scale_deg` 指定 |
| `commands.goal_heading_delta_max_deg` | `9.215 deg` | 不用于 Stage1 terrain-column 目标采样，目标 heading 固定为 `0 rad` |
| `commands.zero_command` | `False` | terrain-column 目标路径不使用自由 waypoint 的 zero-command 逻辑 |
| `commands.rel_standing_envs` | `0.0` | terrain-column 目标路径不使用自由 waypoint 的 standing-env 逻辑 |

## 6. Stage1 地形配置

### 6.1 terrain runtime

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `terrain.enabled` | `True` | 启用 terrain runtime |
| `terrain.mode` | `generator` | 使用生成式 heightfield terrain |
| `terrain.prim_path` | `/World/terrain/stage1` | 地形 prim 路径 |
| `terrain.diffuse_color` | `(0.0, 0.0, 0.0)` | 地形可视颜色 |
| `terrain.static_friction` | `1.0` | 地形静摩擦 |
| `terrain.dynamic_friction` | `1.0` | 地形动摩擦 |
| `terrain.restitution` | `0.0` | 地形恢复系数 |

### 6.2 heightfield generator

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `horizontal_scale` | `0.1 m` | heightfield 水平分辨率 |
| `vertical_scale` | `0.005 m` | heightfield 垂直分辨率 |
| `border_size` | `25.0 m` | 地图外边界 |
| `terrain_length` | `8.0 m` | 单个 tile 沿 x 方向长度 |
| `terrain_width` | `8.0 m` | 单个 tile 沿 y 方向宽度 |
| `num_rows` | `20` | 地形难度行数 |
| `num_cols` | `10` | 地形类型列数 |
| `slope_threshold` | `0.75` | heightfield 转 mesh 的斜率修正阈值 |
| `add_roughness` | `False` | 当前不额外添加 roughness |
| `roughness_height_range` | `(0.01, 0.04)` | roughness 参数，当前 inactive |
| `roughness_downsampled_scale` | `0.2` | roughness 参数，当前 inactive |

每个 tile 的 difficulty 为：

$$
\mathrm{difficulty} = \frac{\mathrm{row}}{20}
$$

tile origin：

$$
x_{\mathrm{origin}} = (\mathrm{row} + 0.5) \cdot 8
$$

$$
y_{\mathrm{origin}} = (\mathrm{col} + 0.5) \cdot 8
$$

origin 的 z 坐标取 tile 中心区域高度的非负最大值，用于 reset 时把机器人放在合适高度。

### 6.3 当前实际 terrain column 映射

当前源码按 `choice = col / num_cols + 0.001` 和 `terrain_dict` 的累积权重选择地形类型。以 `num_cols = 10` 计算，实际列映射为：

| column | terrain name | terrain class |
|---:|---|---|
| `0` | `flat` | `other` |
| `1` | `slope down` | `other` |
| `2` | `slope up` | `other` |
| `3` | `uneven rough` | `other` |
| `4` | `uneven rough` | `other` |
| `5` | `stairs down` | `step` |
| `6` | `stairs down` | `step` |
| `7` | `stairs up` | `step` |
| `8` | `stairs up` | `step` |
| `9` | `discrete obstacles` | `step` |

`terrain_dict` 中还保留 `hurdle`、`gap`、`ramp`、`beam`、`new stairs down`、`pit` 等条目；但在当前 `num_cols = 10` 且 `choice < 1.0` 的列选择方式下，这些类型不会被当前 10 列实际采到。

## 7. Curriculum 与 reset

### 7.1 初始课程分配

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `curriculum.enabled` | `True` | 启用课程 |
| `curriculum.max_init_terrain_level` | `5` | 默认初始 row 从 `0-5` 随机 |
| `curriculum.initial_max_terrain_level_by_name["stairs down"]` | `1` | `stairs down` 初始 row 限制为 `0-1` |
| `curriculum.initial_max_terrain_level_by_name["stairs up"]` | `1` | `stairs up` 初始 row 限制为 `0-1` |
| `curriculum.initial_max_terrain_level_by_name["discrete obstacles"]` | `2` | `discrete obstacles` 初始 row 限制为 `0-2` |
| `curriculum.default_terrain_name` | `flat` | 默认地形名，仅用于初始化检查和默认类型索引 |

初始化时：

- `flat`、`slope down`、`slope up`、`uneven rough` 仍按默认 `0-5` 均匀随机采样。
- `stairs down`、`stairs up` 按 `0-1` 均匀随机采样。
- `discrete obstacles` 按 `0-2` 均匀随机采样。
- `terrain_types` 按 env id 均匀分配到 `0-9` 全部地形列。
- `scene.env_origins` 同步到每个 env 当前 row / column 对应 tile origin。

### 7.2 Episode 内 terrain row 推进

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `curriculum.terrain_column_move_down_progress_ratio` | `0.30` | reset 时若当前目标段进度低于 30%，则当前 row 退一级 |
| `curriculum.move_up_distance_ratio` | `0.50` | 继承自共享配置；普通 waypoint curriculum 使用，Stage1 terrain-column 不使用该字段判断升级 |
| `curriculum.move_up_uses_forward_x` | `False` | 继承自共享配置；Stage1 terrain-column 不使用该字段判断升级 |
| `curriculum.move_down_command_ratio` | `0.50` | 继承自共享配置；普通 waypoint curriculum 使用，Stage1 terrain-column 不使用该字段判断降级 |

Stage1 terrain-column 目标的 row 推进发生在 episode 内，而不是 reset 前计时重采样或 reset-time curriculum update：

- 若当前目标点被命中，terrain level 加 `1`。
- row 推进后，`scene.env_origins` 同步到新 row / 同 column 的 tile origin。
- row 推进后立刻重采样下一目标点。
- 若推进会进入没有合法下一目标的最高 row 区域，本段记为 `terrain_column_completed`，本 step 通过 time-limit reset 回到按当前地形类别重新采样的低 row。
- 若 episode 因 far、球铰越界或 timeout 结束，本步不会触发 row 推进。

Stage1 terrain-column 的 row 退级发生在 episode reset 时。当前目标段进度定义为：

$$
p_{\mathrm{row}}
=
\mathrm{clip}
\left(
\frac{d_{\mathrm{start}} - d_{\mathrm{now}}}{d_{\mathrm{start}}},
0,
1
\right)
$$

其中 $d_{\mathrm{start}}$ 是当前目标段刚采样时车辆到目标点的水平距离，$d_{\mathrm{now}}$ 是 episode 结束时车辆到当前目标点的水平距离。

reset 时的 terrain level 更新逻辑为：

- 若 `terrain_column_completed=True` 或当前 row 已没有合法下一目标，则按当前地形类别重新采样低 row。
- 若 episode 因 `far_from_target`、`ball_joint_out_of_bounds` 或 `time_out` 结束，且没有命中目标，同时 $p_{\mathrm{row}} < 0.30$，则 terrain level 减 `1`。
- 若 episode 失败/超时但 $p_{\mathrm{row}} \ge 0.30$，保持当前 row 不变，让策略继续在当前难度练习。

### 7.3 reset 初值

| 参数 | 当前值 |
|---|---:|
| `resets.root_pos` | `(0.0, 0.0, 0.30)` |
| `resets.root_lin_vel` | `(0.0, 0.0, 0.0)` |
| `resets.root_ang_vel` | `(0.0, 0.0, 0.0)` |
| `resets.root_x_range` | `(-1.0, 1.0)` |
| `resets.root_y_range` | `(-1.0, 1.0)` |
| `resets.root_yaw_range` | `(0.0, 0.0)` |
| `resets.ball_joint_pos_range` | `(0.0, 0.0)` |
| `resets.ball_joint_vel_range` | `(0.0, 0.0)` |
| `resets.wheel_joint_pos_range` | `(0.0, 0.0)` |
| `resets.wheel_joint_vel_range` | `(0.0, 0.0)` |

reset 位置先加当前 terrain tile origin，再加 `root_x_range` / `root_y_range` 随机扰动。随后 terrain runtime 根据地形类别处理 spawn：

| terrain class | offset 逻辑 |
|---|---|
| `step` | 直接覆盖 xy 到当前 tile origin，不再在 tile start 前 `0.3-0.8 m` 出生 |
| `gap` | x 方向向后随机 `0.0-0.4 m` |
| `other` | x / y 各随机 `-0.5-0.5 m` |

当前 `stairs down`、`stairs up`、`discrete obstacles` 均属于 `step` class，因此 reset 时都会出生在当前 tile origin 的 xy 坐标上。

step 类 spawn 公式为：

$$
x_{\mathrm{spawn}} = x_{\mathrm{tile\_origin}}
$$

$$
y_{\mathrm{spawn}} = y_{\mathrm{tile\_origin}}
$$

$$
z_{\mathrm{spawn}} = h(x_{\mathrm{spawn}}, y_{\mathrm{spawn}}) + 0.30
$$

其中 $h(\cdot)$ 来自 heightfield 世界坐标采样。step 类不再使用 tile start 前 approach spawn，也不再使用 tile center height 设置 spawn z。`flat`、`slope`、`rough` 等 `other` class 保留原 reset 逻辑。

当前 reset yaw 固定为 `0 rad`，即默认朝世界系 `+x`。

## 8. 观测空间

### 8.1 总维度

Stage1 actor 和 critic 使用同一份观测：

$$
632 = 54 + 34 \times 17
$$

其中：

- `54` 是 Stage0 继承来的 proprioception / command / last action 观测。
- `34 * 17 = 578` 是 Stage1 地形高度 patch。

### 8.2 观测分量顺序

| 分量 | 维度 | scale | 说明 |
|---|---:|---:|---|
| `ball_joint_pos` | `6` | `1.0` | 6 个球铰当前角度 |
| `ball_joint_vel` | `6` | `1.0` | 6 个球铰当前角速度 |
| `base_lin_vel` | `3` | `1.0` | chassis body 坐标系线速度 |
| `base_ang_vel` | `3` | `1.0` | chassis body 坐标系角速度 |
| `wheel_joint_vel` | `6` | `1.0` | 6 个车轮关节角速度 |
| `wheel_longitudinal_slip` | `6` | `1.0` | 6 个车轮纵向滑移率 |
| `wheel_slip_angle` | `6` | `1.0` | 6 个车轮侧滑角，已 clip 到 `[-pi/2, pi/2]` |
| `wheel_normal_contact_force` | `6` | `1.0` | 6 个车轮归一化法向接触力 |
| `goal_relative_command` | `4` | `1.0` | 车体系相对目标命令 |
| `last_action` | `8` | `1.0` | 上一控制步已经执行的 policy action |
| `terrain_height_patch` | `578` | 原始米制值 | Stage1 地形高度 patch |

当前配置类中仍存在 `projected_gravity`、`ball_joint_target_error`、`module_roll_pitch` 等 scale 字段，但当前 `build_observation_descriptor()` 和 `compute_actor_observation_from_raw_terms()` 不把这些项拼入 actor / critic 观测。

### 8.3 观测裁剪与噪声

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `observations.clip_observations` | `100.0` | actor / critic 观测输出后统一 clip 到 `[-100, 100]` |
| `observations.use_history` | `False` | 不使用观测历史堆叠 |
| `observations.history_length` | `1` | 单帧观测 |
| `observations.noise.enabled` | `False` | 当前不注入观测噪声 |
| `observations.wheel_slip_epsilon` | `0.1` | 纵滑 / 侧滑计算的低速分母保护 |
| `observations.wheel_slip_angle_clip_rad` | `pi / 2` | 侧滑角 clip 范围 |

## 9. 高度图 patch

### 9.1 patch 几何

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `terrain.patch_front_extent` | `0.942209 m` | 中车参考点到整车前端覆盖长度 |
| `terrain.patch_rear_extent` | `0.942209 m` | 中车参考点到整车后端覆盖长度 |
| `terrain.patch_half_width` | `0.280374 m` | 半车宽 |
| `terrain.patch_preview_length` | `1.0 m` | 车头前方 preview 长度 |
| `terrain.patch_rear_margin` | `0.40 m` | 车尾后方额外余量 |
| `terrain.patch_side_margin` | `0.5 m` | 左右额外余量 |
| `terrain.patch_origin_offset_xy` | `(0.0, 0.0)` | patch 相对中车参考点平移 |
| `terrain.patch_resolution_x` | `0.10 m` | x 方向目标采样间距 |
| `terrain.patch_resolution_y` | `0.10 m` | y 方向目标采样间距 |

由当前参数计算得到：

| 轴 | 范围 | 点数 |
|---|---:|---:|
| local x | `[-1.342209, 1.942209] m` | `34` |
| local y | `[-0.780374, 0.780374] m` | `17` |

因此高度图总维度为：

$$
34 \times 17 = 578
$$

### 9.2 patch 数值语义

当前高度 patch 不通过 `sensors.enable_height_scanner` 的 RayCaster 生成，而是直接用 terrain runtime 在 heightfield 上按世界系 x / y 双线性插值采样。

每个采样点流程：

1. 在 chassis yaw 对齐的局部 patch 网格中生成 local x / y 点。
2. 根据当前 root position 和 yaw 转到世界系 x / y。
3. 从 Stage1 heightfield 采样 terrain height。
4. 写入观测的是：

$$
h_{\mathrm{patch}} = z_{\mathrm{root}} - h_{\mathrm{terrain}}(x, y)
$$

该值保持米制单位，不额外乘 scale，不额外 clip 到 `[-1, 1]`。actor 和 critic 使用同一份 height patch。PPO 的 obs normalizer 负责训练过程中的统计归一化。

## 10. Reward 配置

Stage1 当前 reward 计算项与共享 reward 主干一致，共 `10` 项：

1. `distance_to_target`
2. `progress_to_target`
3. `reached_target`
4. `far_from_target`
5. `angle_diff`
6. `turn_speed_penalty`
7. `slip_penalty`
8. `action_rate_penalty`
9. `contact_support_penalty`
10. `edge_speed_penalty`

其中 `turn_speed_penalty_weight = 0.0`，所以 `turn_speed_penalty` 当前只作为计算/日志分量存在，不贡献总 reward。`reached_target` 已启用，参数与 Stage0 相同。`action_rate_penalty` 已在 Stage1 启用，用 episode 最大步数归一化。`slip_penalty` 当前使用底层接触权重 mask，`contact_support_penalty` 用于惩罚前、中、后三段模块支撑丢失，`edge_speed_penalty` 用局部高程图前方预览区域惩罚高度突变前高速冲击。

### 10.1 reward 参数

| 参数 | 当前值 |
|---|---:|
| `target_position_tolerance` | `0.5 m` |
| `distance_to_target_denominator_scale` | `0.01` |
| `distance_to_target_weight` | `6.0` |
| `nominal_goal_distance_m` | `8.0 m` |
| `turn_speed_angle_scale_deg` | `0.0 deg` |
| `progress_to_target_clip_m` | `0.25 m` |
| `progress_to_target_relax_radius_m` | `4.0 m` |
| `progress_to_target_weight` | `8.0` |
| `reached_target_base_reward` | `2.0` |
| `reached_target_weight` | `6.0` |
| `far_from_target_margin` | `3.0 m` |
| `far_from_target_weight` | `-2.0` |
| `angle_diff_weight` | `6.0` |
| `turn_speed_penalty_weight` | `0.0` |
| `slip_penalty_weight` | `-2.0` |
| `slip_longitudinal_penalty_ratio` | `5.0` |
| `slip_angle_penalty_ratio` | `1.0` |
| `action_rate_penalty_weight` | `-10.0` |
| `action_rate_base_ratio` | `0.5` |
| `action_rate_joint_ratio` | `1.0` |
| `contact_support_penalty_weight` | `-4.0` |
| `contact_support_min_weight` | `0.3` |
| `edge_speed_penalty_weight` | `-6.0` |
| `edge_height_low_threshold_m` | `0.04 m` |
| `edge_height_high_threshold_m` | `0.10 m` |
| `edge_speed_limit_mps` | `0.5 m/s` |
| `progress_gate_longitudinal_k` | `3.0` |
| `progress_gate_slip_angle_scale_rad` | `1.5 rad` |
| `progress_gate_min_multiplier` | `0.25` |
| `progress_gate_max_multiplier` | `1.5` |
| `low_slip_longitudinal_threshold` | `1.0` |
| `low_slip_angle_threshold_rad` | `0.35 rad` |
| `only_positive_rewards` | `False` |

### 10.2 主要 reward 计算

设当前相对目标平面距离为 $D_t$，上一帧距离为 $D_{t-1}$，最大 episode 步数为 $N = 2400$。

距离项：

$$
r_{\mathrm{dist}} =
6.0 \cdot
\frac{1}{1 + 0.01D_t^2}
\cdot
\frac{1}{N}
$$

progress 原始增量：

$$
\Delta D = \mathrm{clip}(D_{t-1} - D_t, -0.25, 0.25)
$$

若 $D_t \le 4.0\ \mathrm{m}$，负 progress 会被放松为不惩罚。

正向和负向 progress：

$$
p^+ = \frac{\max(\Delta D, 0)}{8.0}
$$

$$
p^- = \frac{\min(\Delta D, 0)}{8.0}
$$

当前源码中 `progress_to_target` 不额外除以 $N$，只按名义目标距离 `8.0 m` 归一化。

纵滑 gate：

$$
G_{\kappa} =
\exp
\left(
-\frac{1}{2}
\sum_i
\left(
\frac{\kappa_i}{3.0}
\right)^2
\right)
$$

侧滑角 gate：

$$
G_{\alpha} =
\prod_i
\left[
0.5 \cos
\left(
\mathrm{clip}
\left(
\frac{\pi |\alpha_i|}{1.5},
0,
\pi
\right)
\right)
+ 0.5
\right]
$$

Stage1 当前 progress gate 使用平均 gate：

$$
G = 0.5(G_{\kappa} + G_{\alpha})
$$

progress multiplier：

$$
m = 0.25 + (1.5 - 0.25)G
$$

progress reward：

$$
r_{\mathrm{progress}} = 8.0 \cdot (m p^+ + p^-)
$$

目标命中奖励已启用，参数与 Stage0 相同：

$$
r_{\mathrm{reached}} =
6.0 \cdot
\mathbb I(D_t < 0.5)
\cdot
2.0
\cdot
\frac{N-l_t}{N}
$$

Stage1 不再用 `commands.goal_distance` 表示目标采样距离；reward 使用 `nominal_goal_distance_m = 8.0 m` 作为 progress 归一化和 far-from-target 的名义尺度。

far-from-target 阈值为：

$$
D_{\mathrm{far}} = 8.0 + 3.0 = 11.0\ \mathrm{m}
$$

若 $D_t > 11.0\ \mathrm{m}$：

$$
r_{\mathrm{far}} = -2.0
$$

heading 项：

$$
r_{\mathrm{angle}} =
6.0 \cdot
\frac{1}{1 + |\theta_{\mathrm{goal}}|}
\cdot
\frac{1}{N}
$$

转向速度惩罚当前会被源码计算，但 Stage1 权重为 `0.0`，因此不贡献总 reward：

$$
r_{\mathrm{turn}} =
0.0 \cdot
I_{\mathrm{turn}}
\cdot
\frac{\|v_{xy}\|}{2.0}
\cdot
\frac{1}{N}
$$

由于 Stage1 当前 `turn_speed_angle_scale_deg = 0.0`，代码内部使用 `1.0e-6` 作为分母保护，因此只要目标 bearing 非零，`I_turn` 很容易被 clip 到 `1`；但该项当前权重为 `0.0`，所以只作为计算分量存在。

底层接触权重：

$$
c_i =
\mathrm{clip}
\left(
\frac{n_i - 0.01}{0.08 - 0.01},
0,
1
\right)
$$

其中 $n_i$ 为第 $i$ 个车轮的接触力模长按整车重量归一化后的值。当前 reward 复用该接触权重，不再额外定义 sigmoid 接触系数。

滑移惩罚当前使用接触权重 mask：

$$
S_c =
\max
\left(
\sum_{i=1}^{6}c_i,
1.0
\right)
$$

$$
r_{\mathrm{slip}} =
-2.0 \cdot
\frac{
5.0 \cdot \frac{\sum_{i=1}^{6}c_i|\kappa_i|}{S_c}
+ 1.0 \cdot \frac{\sum_{i=1}^{6}c_i|\alpha_i|}{S_c}
}{N}
$$

其中 $S_c$ 是有效接触权重和的保护分母。这样离地轮不会贡献滑移惩罚；当只有少数轮有效接地时，仍然评价这些接地轮自身的滑移，而不是因为除以固定 `6` 把惩罚压得过低。

动作变化惩罚：

$$
\rho =
\left[
0.5,\ 0.5,\ 1.0,\ 1.0,\ 1.0,\ 1.0,\ 1.0,\ 1.0
\right]
$$

$$
r_{\Delta a}
=
-10.0 \cdot
\frac{
\frac{1}{8}
\sum_{j=1}^{8}
\rho_j
(a_{j,t}-a_{j,t-1})^2
}{N}
$$

模块支撑惩罚：

$$
C_{\mathrm{front}} = \max(c_2,c_3)
$$

$$
C_{\mathrm{mid}} = \max(c_0,c_1)
$$

$$
C_{\mathrm{rear}} = \max(c_4,c_5)
$$

其中 `0,1` 为中车左右轮，`2,3` 为前车左右轮，`4,5` 为后车左右轮。模块支撑缺口为：

$$
d_m =
\mathrm{clip}
\left(
\frac{0.3-C_m}{0.3},
0,
1
\right)
$$

模块支撑惩罚为：

$$
r_{\mathrm{contact}} =
-4.0 \cdot
\frac{
\frac{1}{3}
\left(
d_{\mathrm{front}}^2
+ d_{\mathrm{mid}}^2
+ d_{\mathrm{rear}}^2
\right)
}{N}
$$

地形突变前速度惩罚使用当前局部高程图的前方预览区域。当前 height patch 从车体前端继续向前预览 `1.0 m`，并在车体左右两侧各保留 `0.5 m` 侧向预览空间。设预览区域内相邻采样点的最大高度跳变为：

$$
E_{\mathrm{raw}}
=
\max
\left(
|\Delta_x H|,
|\Delta_y H|
\right)
$$

其中 $H$ 为局部高程图中的地形高度。源码中 height patch 存的是 `root_z - terrain_height`，但相邻差值取绝对值后与真实地形高度差等价。

根据 Stage1 地形生成函数检查：

- `stairs up/down` 的单级台阶高度约为 `0.05-0.22 m`；
- `discrete obstacles` 的局部相邻高度跳变从约 `0.10 m` 起，高 row 可更大；
- `slope up` 最高 row 的相邻网格高度差约为 `0.04 m`。

因此当前 edge strength 采用：

$$
E
=
\mathrm{clip}
\left(
\frac{E_{\mathrm{raw}}-0.04}{0.10-0.04},
0,
1
\right)
$$

安全前进速度为：

$$
v_{\mathrm{safe}}
=
2.0
-
E
\left(
2.0 - 0.5
\right)
$$

当 $E=0$ 时，$v_{\mathrm{safe}}=2.0\ \mathrm{m/s}$，等于 Stage1 底盘前进速度上限，平地不额外限速；当 $E=1$ 时，$v_{\mathrm{safe}}=0.5\ \mathrm{m/s}$。

只惩罚前进方向上的超速：

$$
v^+
=
\max(v_x,0)
$$

$$
e_v
=
\max
\left(
v^+ - v_{\mathrm{safe}},
0
\right)
$$

$$
r_{\mathrm{edge}}
=
-6.0 \cdot
E
\left(
\frac{e_v}{2.0}
\right)^2
\frac{1}{N}
$$

总 reward 为上述 active 项求和，不做正值裁剪。

## 11. Termination 配置

### 11.1 active termination

当前 active done terms：

| 条件 | 判定 |
|---|---|
| `waypoint_hit` | 当前目标距离 `< 0.5 m`；用于触发 terrain row / target 推进，并为 `reached_target` 提供命中指示 |
| `is_success` | Stage1 terrain-column 目标下固定为 `False` |
| `far_from_target` | 当前目标距离 `> 11.0 m` |
| `ball_joint_out_of_bounds` | 任一受控球铰超过 lower / upper limit |
| `time_out` | episode 到达 `max_episode_length - 1` 且未 success |

`terminated` 返回：

$$
\mathrm{terminated}
=
\mathrm{is\_success}
\lor
\mathrm{far\_from\_target}
\lor
\mathrm{ball\_joint\_out\_of\_bounds}
$$

`time_out` 单独作为 truncation 返回。由于 `is_finite_horizon = False`，RSL-RL 会把 timeout 当作 time-limit 处理。

### 11.2 球铰限制

| 关节名 | lower | upper |
|---|---:|---:|
| `spm1_platform_joint_z` | `-0.7` | `0.7` |
| `spm1_platform_joint_y` | `-1.6` | `0.5` |
| `spm1_platform_joint_x` | `-0.5` | `0.5` |
| `spm2_platform_joint_z` | `-0.7` | `0.7` |
| `spm2_platform_joint_y` | `-1.6` | `0.5` |
| `spm2_platform_joint_x` | `-0.5` | `0.5` |

### 11.3 当前非 active termination 字段

Stage1 cfg 不显式设置目标 yaw tolerance、整车姿态阈值、首尾模块 roll / pitch 阈值。当前 `compute_done_terms()` 没有把这些共享默认字段纳入 Stage1 active termination。

## 12. 传感器、随机化与可视化

### 12.1 传感器

| 传感器 | 当前状态 | 是否进入 policy |
|---|---|---|
| IMU | disabled | 否 |
| Stereo camera | disabled | 否 |
| LiDAR | disabled | 否 |
| Height scanner RayCaster | disabled | 否 |
| Wheel contact force runtime | active | 间接进入观测，作为 `wheel_normal_contact_force` |

`sensors.wheel_contact_max_points_per_env = 128`，用于避免地形接触点较多时接触数据容量不足。

### 12.2 随机化

| 参数 | 当前值 |
|---|---:|
| `randomization.enable_action_randomization` | `False` |
| `randomization.joint_position_noise_scale` | `0.0` |
| `randomization.action_noise_std` | `0.0` |
| `randomization.action_bias_std` | `0.0` |

当前没有 action noise、action bias、joint position noise。

### 12.3 可视化

| 参数 | 当前值 |
|---|---:|
| `debug.enable_debug_draw` | `True` |
| `debug.visualize_goal_heading` | `True`，本次 headless 录制命令用 `--hide_goal_heading` 临时关闭 |
| `debug.visualize_wheel_slip` | `True`，本次 headless 录制命令用 `--hide_wheel_slip_vis` 临时关闭 |
| `debug.create_follow_views` | `True` |
| `debug.follow_view_top_height` | `8.0` |
| `debug.follow_view_chase_env_index` | `0` |
| `debug.follow_view_chase_env_indices` | 源码默认 `()`；录制命令用 `--follow_all_envs` 设置为全部 `32` 个 env |
| `debug.follow_view_chase_offset_b` | `(-4.0, -3.0, 2.4)` |
| `debug.follow_view_chase_target_offset_b` | `(1.0, 0.0, 0.4)` |

当前目标点红色 marker 开启。本次 headless 录制为保留目标点 marker 但关闭目标方向箭头和 wheel-slip 箭头。

## 13. TensorBoard 主要指标

当前环境会通过 `extras["metrics"]` 输出以下主要指标族：

| 指标族 | 含义 |
|---|---|
| `Reward/*` | 当前 step 的各 reward 分量和总 reward |
| `ProgressGate/*` | progress gate、正负 progress、multiplier |
| `Tracking/*` | 当前 waypoint 距离、bearing、段完成度、episode 完成度 |
| `Action/*` | policy action、平面命令、轮侧执行相关摘要 |
| `Command/*` | env 0 的目标相对命令和目标方向 offset |
| `Observation/*` | 关键观测原始值摘要 |
| `LowSlip/*` | 纵滑、侧滑角通过率和 margin |
| `PerWheel/*` | 每个车轮的速度、滑移、接触、执行摘要 |
| `Terrain/*` | 当前 terrain level、tile start / origin / end、root x、target x、forward x 诊断，以及 active goal start distance / progress |
| `Termination/*` | success、timeout、far、ball-joint-limit 等终止率 |
| `Stage1Eval/global/*` | Stage1 全局地形列评价指标，包括 max-row reached、valid-target masked、tile x 调试值 |
| `Stage1Eval/colXX/*` | 各地形列评价指标，包括 `max_row_reached_rate` 和 `valid_target_masked` |

其中 `Action/*`、`LowLevel/*`、`PerWheel/*` 中会出现底层执行摘要指标，但本文档不解释其底层运动学计算过程。

说明：共享 curriculum 代码仍能在普通 waypoint 路径中输出小写 `terrain/*` reset 指标；当前 Stage1 terrain-column 目标路径额外输出 reset-time 的 `terrain/row_progress_at_reset`、`terrain/move_down_ratio`、`terrain/reset_to_low_ratio` 和 `terrain/level_after_reset`，用于检查 row 退级逻辑。
