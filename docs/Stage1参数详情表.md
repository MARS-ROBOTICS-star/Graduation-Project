# Stage1参数详情表

本文档记录 `RL_Training/` 工作区内 `CompleteCar-Stage1` 当前实际生效的 RL 环境配置、PPO 配置、warm-start 方式、地形课程、目标点、观测、高度图、奖励和终止逻辑。

本文档不展开底层运动学模型公式，不重复说明轮速分配、low-slip 平面命令整形或车轮牵引力矩分配内部推导。2026-05-10 新修改：由于 Stage0 与 Stage1 必须使用同一套机器人底层运动学和驱动配置，本文保留当前 Stage1 与 Stage0 统一后的底层执行参数摘要；当前球铰控制链已取消旧的一阶位置规划器，policy 输出的 $q^d$ 直接进入 PhysX position drive，公式仍以 `docs/stage0_baseline参数详情表.md` 和 `docs/底层运动学轮速分配球铰规划与力矩分配.md` 为准。

当前 Stage1 定义为：history4 terrain curriculum fine-tune 阶段；2026-05-07 起，Stage1 actor 已从直接输入完整 height patch 改为输入 28 维确定性低维地形特征，critic 保留完整 height patch 作为 privileged information。2026-05-14 hardcols 实验后，当前 reward 权重已回退到上一轮 reward-retarget 口径，后续重点转为检查 reward 激活相位和物理定义；当前源码地图已按用户要求恢复为原 `model_50.pt` 对应的 10 列分布：`flat 10% / slope 20% / rough 20% / stairs 30% / obs 20%`。

当前 `complete_car_stage1_cfg.py` 采用本阶段显式配置风格，但只保留 Stage1 直接相关或当前 active 的参数。terrain-column target 不再在 Stage1 配置中显式写入自由 waypoint 采样参数，例如 `commands.goal_distance` 和 `commands.goal_direction_max_deg`。

当前详表以当前源码配置为准。下列 run 是最近记录的 headless Stage1 warm-start 训练快照，用于说明当时的启动命令和日志位置：

- run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-04-29_07-37-58_stage1_warmstart_best_baseline_2_32env_best_per_terrain_chase_700iter`
- env 参数快照：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-04-29_07-37-58_stage1_warmstart_best_baseline_2_32env_best_per_terrain_chase_700iter/params/env.yaml`
- agent 参数快照：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-04-29_07-37-58_stage1_warmstart_best_baseline_2_32env_best_per_terrain_chase_700iter/params/agent.yaml`
- warm-start checkpoint：`RL_Training/logs/rsl_rl/complete_car_stage1/warmstart_best_baseline_2/model_0.pt`
- runtime log：`RL_Training/logs/runtime/stage1_32env_best_per_terrain_chase_setsid.log`

该 run 使用 `32` env、headless、`700` iterations、`best_baseline_2` warm-start，并启用按地形选择最佳 env 后依次录制 `120 s` chase 视频。2026-04-28 的 GUI run `2026-04-28_18-17-55_stage1_warmstart_best_baseline_2_32env_view_700iter` 已按用户要求在 PPO iteration `18/700` 后停止，只作为历史启动验证记录；当前默认 warm-start 已在 2026-05-10 改为 `best_baseline5/model_75.pt` 的 Stage1 转换版。

注意：上述 run 的 `env.yaml` 是启动时快照。2026-05-02 起，当前源码中的 Stage1 terrain column 映射已调整为第 `0` 列 `flat`，Stage1 源码默认动作映射也已调整为与 Stage0 相同的底盘物理速度输出范围；2026-05-13 起，当前源码中的 Stage1 观测结构已开启 4 帧历史堆叠，actor `328` 维、critic `906` 维；2026-05-14 hardcols 实验后，当前源码的 Stage1 10 列映射恢复为 `0 flat`、`1 slope down`、`2 slope up`、`3-4 uneven rough`、`5-7 stairs down`、`8-9 discrete obstacles`。2026-05-16 起，当前源码将 `slope down / slope up` 的坡度系数从 `0.4` 提高到 `0.65`。此前已经启动的 run 的 `params/env.yaml` 不会因源码修改自动改变，新启动的 Stage1 run 才会使用下文当前源码配置。

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
| 低维地形特征 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terrain_features.py` |
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
| `observation_space.actor` | `328` | actor 观测维度，即 `82` 维单帧 actor 观测做 4 帧历史堆叠 |
| `observation_space.critic` | `906` | critic 观测维度，即 4 帧 actor 观测加 `578` 维完整 height patch |
| `state_space` | `0` | 当前不使用额外 privileged state |
| `episode_length_s` | `40.0 s` | 单个 episode 最大时长 |
| `control.sim_dt` | `1 / 120 s` | PhysX 仿真步长 |
| `decimation` | `4` | 每 4 个 sim step 执行一次 RL action |
| `control.control_dt` | `1 / 30 s` | RL 控制周期 |
| `sim.physx.max_position_iteration_count` | `8` | 场景级 PhysX 位置约束求解迭代次数 |
| `sim.physx.max_velocity_iteration_count` | `4` | 场景级 PhysX 速度约束求解迭代次数，用于轮地摩擦、碰撞冲击等速度层约束 |
| `robot.articulation.solver_position_iteration_count` | `8` | 机器人 articulation root 位置约束求解迭代次数 |
| `robot.articulation.solver_velocity_iteration_count` | `4` | 机器人 articulation root 速度约束求解迭代次数；已与 Stage1 场景级 velocity iteration 对齐 |
| `control.terrain_speed_limit_mps` | `0.50 m/s` | 【本轮修改】保留为 legacy / fallback 速度值；Stage1 主执行链路已改为下方地形 + 相位速度字段 |
| `control.terrain_speed_step_up_approach_mps` | `0.45 m/s` | 【本轮新增】正高度突变 approach 阶段前进速度上限 |
| `control.terrain_speed_step_up_climb_mps` | `0.75 m/s` | 【本轮修改】正高度突变 climb 阶段前进速度上限，允许有限牵引爬升 |
| `control.terrain_speed_step_down_mps` | `0.35 m/s` | 【本轮新增】下台阶 / drop 阶段前进速度上限 |
| `control.terrain_speed_obstacle_mps` | `0.40 m/s` | 【本轮新增】离散障碍 / gap approach 阶段前进速度上限 |
| `max_episode_length` | `1200` | `40 s * 30 Hz` |
| `is_finite_horizon` | `False` | timeout 作为 RSL-RL time-limit，可做 bootstrap |
| `terrain.enabled` | `True` | 启用地形 |
| `terrain.mode` | `generator` | 使用 Stage1 terrain generator |
| `curriculum.enabled` | `True` | 启用地形课程 |
| `terrain.measure_heights` | `True` | 生成完整 height patch；actor 使用由 patch 提取的低维地形特征，critic 额外保留完整 patch |
| `observations.noise.enabled` | `False` | 当前默认关闭观测噪声 |
| `randomization.enable_action_randomization` | `False` | 当前默认关闭 action noise / bias |
| `sensors.imu.enabled` | `False` | IMU 不参与策略输入 |
| `sensors.stereo_camera.enabled` | `False` | 双目相机不参与策略输入 |
| `sensors.lidar.enabled` | `False` | 激光雷达不参与策略输入 |
| `sensors.enable_height_scanner` | `False` | 不用 RayCaster 传感器生成高度图 |
| `debug.enable_debug_draw` | `True` | 开启目标点 marker 等 debug draw |
| `debug.visualize_goal_heading` | `True` | 绘制目标方向箭头 |
| `debug.visualize_wheel_slip` | `True` | 源码默认绘制 wheel-slip 箭头，训练命令可临时关闭 |
| `debug.visualize_height_patch` | `False` | 源码默认不绘制局部高度图 patch；回放时可用 `--show_height_patch_vis` 开启 |
| `debug.height_patch_visualization_env_indices` | `(0,)` | 局部高度图 patch 可视化默认只显示 `env_0`，空元组表示显示全部 env |
| `debug.height_patch_marker_radius` | `0.035 m` | 高度 patch 采样点球形 marker 半径 |
| `debug.height_patch_marker_height_offset` | `0.035 m` | 采样点 marker 相对真实采样地形高度的上抬量，避免与地形表面重合 |
| `debug.height_patch_color_range_m` | `0.30 m` | 高度 patch 颜色映射范围；以当前 patch 平均高度为中心，低处偏蓝，高处偏红 |
| `debug.create_follow_views` | `True` | 创建 top / chase 跟踪视角 |

## 2. PPO 与 warm-start

### 2.1 PPO runner

| 参数 | 当前值 | 含义 |
|---|---:|---|
| runner | `OnPolicyRunner` | RSL-RL on-policy runner |
| `experiment_name` | `complete_car_stage1` | 日志根目录名 |
| `run_name` | `""` | Stage1 PPO cfg 默认 run 名；当前 headless 命令用 `--run_name` 覆盖 |
| 当前命令 `run_name` 覆盖 | `stage1_h4_m50_stronger_rear_support_antidive_96env_200iter_20260513` | 当前 `model_50.pt` stronger rear-support / anti-dive fine-tune run 名 |
| `load_run` | `warmstart_best_baseline5_model75_terrain_features` | Stage1 PPO cfg 默认 warm-start run 选择器 |
| `load_checkpoint` | `model_0.pt` | Stage1 PPO cfg 默认 warm-start checkpoint |
| `seed` | `1` | 随机种子 |
| `device` | `cuda:0` | 训练设备 |
| `num_steps_per_env` | `512` | 每次 PPO rollout 的每环境步数 |
| `max_iterations` | `700` | 计划 PPO iteration 数 |
| `save_interval` | `25` | checkpoint 保存间隔 |
| `logger` | `tensorboard` | 日志后端 |
| `obs_groups` | `actor: ["actor"], critic: ["critic"]` | actor / critic 分别读取同名观测组 |
| `clip_actions` | `None` | wrapper 层不再额外 clip action |
| `check_for_nan` | `True` | PPO 检查 NaN |

当前 Stage1 PPO 默认配置已按最新训练口径改为 `learning_rate = 5.0e-5`；Stage0 仍继承 Base PPO 默认 `learning_rate = 1.0e-4`。

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
| `learning_rate` | `5.0e-5` |
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
| Stage0 来源 run | `RL_Training/logs/rsl_rl/complete_car_stage0/best_baseline5` |
| Stage0 来源 checkpoint | `model_75.pt` |
| Stage0 actor / critic obs dim | `54` |
| Stage1 actor obs dim | `82` |
| Stage1 critic obs dim | `660` |
| Stage1 warm-start checkpoint | `RL_Training/logs/rsl_rl/complete_car_stage1/warmstart_best_baseline5_model75_terrain_features/model_0.pt` |
| Stage1 warm-start 加载方式 | `--warmstart` |
| checkpoint source iter | `75` |
| orderfix_io | `False` |

Stage0 checkpoint 不能直接作为 Stage1 resume 使用，因为 actor / critic 第一层输入维度和 obs normalizer 维度不同。当前转换方式是：

- actor 第一层从 `54` 维扩展到 `82` 维。
- critic 第一层从 `54` 维扩展到 `660` 维。
- 前 `54` 维继承 Stage0 权重。
- actor 新增 `28` 维低维地形特征的第一层权重初始化为 `0`。
- critic 新增 `28` 维低维地形特征和 `578` 维完整 height patch 的第一层权重初始化为 `0`。
- obs normalizer 的新增维度均值为 `0`，方差和标准差为 `1`。
- `--warmstart` 只加载 actor / critic，不加载 optimizer 和 iteration。

当前推荐使用 `warmstart_best_baseline5_model75_terrain_features/model_0.pt`。该 checkpoint 来源于当前 `preserve_order=True` 和 direct-target 球铰控制口径下选出的 `best_baseline5/model_75.pt`，因此转换时只扩展 Stage1 观测维度，不应用旧 `best_baseline_2` 的 ball joint / wheel joint 输入、输出和 obs normalizer 通道重排。旧 `warmstart_best_baseline_2/model_0.pt` 是 `632` 维结构，不能用于当前新观测结构；旧 `warmstart_best_baseline_2_terrain_features/model_0.pt` 未修正 joint 通道顺序，不建议继续作为当前 Stage1 默认 warm-start；`warmstart_best_baseline_2_terrain_features_orderfix_io/model_0.pt` 和 `warmstart_best_baseline4_model375_terrain_features/model_0.pt` 仅保留为历史稳定性对照。

2026-05-13 当前 stronger rear-support / anti-dive fine-tune 采用上一轮 history4 同维 checkpoint warm-start：

- 来源 run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-13_16-16-08_stage1_h4_m625_reward_retarget_rear_finetune_96env_200iter_20260513`
- 来源 checkpoint：`model_50.pt`
- 加载方式：`--resume --warmstart --load_run 2026-05-13_16-16-08_stage1_h4_m625_reward_retarget_rear_finetune_96env_200iter_20260513 --checkpoint model_50.pt`
- 语义：只加载 actor / critic，不加载 optimizer 和旧 iteration；用于保留上一轮 `model_50.pt` 中 stairs 与 obstacles 同时处于较高 row 的行为，再以较小学习率强化后车支撑、抗俯冲和边缘减速。

当前 headless warm-start 训练命令口径：

```bash
python scripts/train.py --task CompleteCar-Stage1 --headless --device cuda:0 --num_envs 128 --resume --warmstart --load_run warmstart_best_baseline5_model75_terrain_features --checkpoint model_0.pt --max_iterations 700 --run_name stage1_warmstart_best_baseline5_model75_128env_700iter
```

当前 `model_50.pt` stronger rear-support / anti-dive fine-tune 训练命令口径：

```bash
python scripts/train.py --task CompleteCar-Stage1 --headless --device cuda:0 --num_envs 96 --resume --warmstart --load_run 2026-05-13_16-16-08_stage1_h4_m625_reward_retarget_rear_finetune_96env_200iter_20260513 --checkpoint model_50.pt --max_iterations 200 --learning_rate 5e-5 --run_name stage1_h4_m50_stronger_rear_support_antidive_96env_200iter_20260513
```

### 2.5 Stage1 回放列选择

当前 `scripts/play.py` 已支持 Stage1 按地形列回放。新增参数为：

| 参数 | 默认值 | 含义 |
|---|---|---|
| `--terrain_replay_columns` | `all` | Stage1 回放出生地形列选择；可取 `all`、单列编号、列编号列表或地形名 |
| `--show_height_patch_vis` | `False` | 在 Isaac Sim 视口中显示局部高度图 patch 的采样点 |
| `--height_patch_vis_envs` | `0` | 指定显示哪些 env 的高度 patch，可取 `0`、`0,7` 或 `all` |
| `--height_patch_vis_radius` | `0.035` | 高度 patch 采样点 marker 半径 |
| `--height_patch_vis_height_offset` | `0.035` | marker 相对采样地形高度的上抬量 |
| `--height_patch_vis_color_range_m` | `0.30` | 颜色映射范围；以当前 patch 平均高度为中心，低处偏蓝，高处偏红 |

当前地形列编号仍为：

| 列编号 | 地形 |
|---:|---|
| `0` | `flat` |
| `1` | `slope down` |
| `2` | `slope up` |
| `3-4` | `uneven rough` |
| `5-7` | `stairs down` |
| `8-9` | `discrete obstacles` |

使用 `all` 时，回放会按 env id 轮转分配到所有 `0-9` 列；因此 `--num_envs` 至少需要为 `10`。指定单列时，所有 env 都出生在该列；指定重复地形名时，会覆盖该地形对应的所有列，例如 `stairs_down` 对应 `5,6,7`，`discrete_obstacles` 对应 `8,9`。

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
python scripts/play.py --task CompleteCar-Stage1 --device cuda:0 --num_envs 4 --load_run 2026-05-03_02-17-59_stage1_resume_from125_ppo_guard_to700 --checkpoint model_699.pt --terrain_replay_columns discrete_obstacles --create_follow_views
```

显示 `env_0` 局部高度图 patch 的回放示例：

```bash
python scripts/play.py --task CompleteCar-Stage1 --device cuda:0 --num_envs 4 --load_run <stage1_run_name> --checkpoint <model_checkpoint.pt> --terrain_replay_columns stairs_down --create_follow_views --follow_view_chase_env 0 --show_height_patch_vis --height_patch_vis_envs 0
```

可视化语义：

- 采样点位置：显示在当前策略实际使用的局部高度 patch 采样点世界坐标处，z 坐标来自 `terrain_runtime.sample_heights_world_xy(...)` 的地形高度，并额外上抬 `height_patch_vis_height_offset`。
- 采样点范围：当前 Stage1 为 `34 * 17 = 578` 个点，对应 actor / critic 观测中 `54` 维本体观测之后的高度图部分。
- 颜色：以当前 patch 平均地形高度为中心，低处偏蓝，高处偏红；颜色只用于观察局部地形起伏，不改变 policy 输入。

## 3. 场景与仿真

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `scene.num_envs` | `32` | Stage1 源码默认环境数，训练入口可用 `--num_envs` 覆盖 |
| `scene.env_spacing` | `2.0 m` | 克隆环境间距 |
| `scene.replicate_physics` | `True` | 克隆环境复用物理配置 |
| `scene.clone_in_fabric` | `True` | 使用 Fabric clone |
| `sim.device` | `cuda:0` | 仿真设备 |
| `sim.dt` | `0.008333333333333333 s` | 120 Hz 仿真步长 |
| `sim.render_interval` | `4` | 每 4 个 sim step 渲染一次 |
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

Stage1 当前显式允许倒车，底盘前向速度物理输出范围为：

$$
v_x^d = a_0 \cdot 2.0
$$

因此当 actor 输出 $a_0 \in [-1, 1]$ 时，$v_x^d \in [-2.0, 2.0]\ \mathrm{m/s}$。

yaw rate 映射为：

$$
\omega_z^d = a_1 \cdot 2.0
$$

因此 $\omega_z^d \in [-2.0, 2.0]\ \mathrm{rad/s}$。

球铰动作按默认零位、action lower limit、action upper limit 映射成目标姿态。当前受控球铰顺序为：

| 序号 | 关节名 | lower | upper |
|---:|---|---:|---:|
| 1 | `spm1_platform_joint_z` | `-0.7` | `0.7` |
| 2 | `spm1_platform_joint_y` | `-0.8` | `0.5` |
| 3 | `spm1_platform_joint_x` | `-0.5` | `0.5` |
| 4 | `spm2_platform_joint_z` | `-0.7` | `0.7` |
| 5 | `spm2_platform_joint_y` | `-1.0` | `0.8` |
| 6 | `spm2_platform_joint_x` | `-0.5` | `0.5` |

本文档到这里为止只记录 policy 输出接口。当前 `spm2_platform_joint_y` 的 action 映射上限为 `0.8 rad`，终止上限为 `0.9 rad`；二者仍保留独立配置字段。动作进入底层执行链后的具体运动学和力矩分配公式不在本文档范围内。

### 4.1 与 Stage0 统一的底层执行参数

2026-05-15 当前：Stage0 和 Stage1 的底层球铰、车轮控制参数重新统一为 `20.0 N*m` 车轮力矩上限。球铰执行链已按用户要求改回 direct target：`q_target = clamp(q_desired)`；轮速分配所需姿态变化率使用实际球铰角速度低通 `qdot_alloc`。

| 参数 | 当前值 | 说明 |
|---|---:|---|
| `control.ball_joint_stiffness` | `120.0 N*m/rad` | PhysX 球铰 position drive 刚度；来自 MATLAB 真实轨迹扩展扫参推荐 |
| `control.ball_joint_damping` | `10.0 N*m*s/rad` | PhysX 球铰 position drive 阻尼 |
| `control.ball_joint_effort_limit_sim` | `60.0 N*m` | 球铰驱动力矩上限；本次由 `20.0` 提高到 `60.0` |
| `control.ball_joint_velocity_limit_sim` | `2.0 rad/s` | 球铰驱动速度上限 |
| `control.ball_joint_qdot_alloc_filter_tau_s` | `0.04 s` | 轮速分配使用的实际球铰角速度低通时间常数 |
| `control.wheel_joint_stiffness` | `0.0` | 车轮 position drive 刚度，当前不使用 |
| `control.wheel_joint_damping` | `0.0` | 车轮 velocity drive 阻尼，当前不使用 direct velocity drive |
| `control.wheel_joint_effort_limit_sim` | `20.0 N*m` | 车轮 torque target 限幅 |
| `control.wheel_joint_velocity_limit_sim` | `20.0 rad/s` | 车轮关节速度限制 |
| `control.low_slip_lambda_tracking` | `1.0` | 保持接近 policy 平面命令的权重 |
| `control.low_slip_lambda_lateral` | `5.0` | 压低接地轮侧向名义速度的权重 |
| `control.contact_force_off_threshold` | `0.01` | 接触权重为 0 的归一化法向力阈值 |
| `control.contact_force_on_threshold` | `0.08` | 接触权重为 1 的归一化法向力阈值 |
| `control.wheel_torque_tracking_gain` | `2.0` | 轮速误差转车轮力矩的比例增益 |
| `control.wheel_slip_feedback_gain` | `4.0` | 纵滑率反馈增益 |
| `control.wheel_slip_velocity_epsilon` | `0.1 m/s` | 纵滑率和侧滑角低速保护分母 |

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
| `commands.terrain_goal_lateral_offset_excluded_names` | `stairs down`, `discrete obstacles` | 这些地形目标 x / y 直接取下一行同列 tile origin，不做 y 偏移 |

Stage1 目标点逻辑：

1. 读取当前 env 的 terrain level 作为当前 row。
2. 读取当前 env 的 terrain type 作为当前 column。
3. 目标 row 固定取当前 row 的 `+1`；若该目标会超过最大 row，视为环境逻辑错误，不再夹紧到当前最后 row。
4. 目标 column 保持不变。
5. 目标世界坐标的 x / y 先取目标 tile origin。
6. 除 `stairs down`、`discrete obstacles` 外，目标 y 再加上 `[-3 m, 3 m]` 均匀随机扰动。
7. `stairs down`、`discrete obstacles` 的目标 x / y 保持目标 tile origin 原值。
8. 目标 z 由 terrain heightfield 在目标 x / y 处采样。
9. 目标 heading 固定为 `0 rad`，即世界系 `+x`。

目标点在 Stage1 的作用是提供沿地形列向前的运动引导，不作为必须完成的 episode 终点。terrain-column 目标不使用 `commands.resampling_time` 的计时重采样；目标推进由事件触发：

- 当前目标距离小于 `target_position_tolerance = 0.5 m` 时，所有地形列都按普通 terrain row 逻辑推进；`stairs_down` 和 `discrete obstacles` 不再需要通过 `quality_advance_score` 才能升 row。
- 目标重采样后仍保持同列，目标 row 继续取当前 row 的 `+1`。
- hard terrain 命中目标但质量不合格时，不再触发 `low_quality_terrain_hit` 终止；质量只进入 reward / diagnostics。
- 若本次推进会进入没有合法下一目标的最高 row 区域，则按普通 terrain-column completed 逻辑完成该列，不再额外要求质量合格。
- 目标命中不会触发 Stage1 success termination。

### 5.3 继承但当前不参与 Stage1 terrain-column 目标采样的 command 字段

| 字段 | 继承值 | 当前作用 |
|---|---:|---|
| `commands.goal_distance` | `20 m` | 不用于 Stage1 terrain-column 目标采样 |
| `commands.goal_direction_max_deg` | `18.43 deg` | 不用于 Stage1 terrain-column 目标采样 |
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
| `7` | `stairs down` | `step` |
| `8` | `discrete obstacles` | `step` |
| `9` | `discrete obstacles` | `step` |

当前恢复后的 `terrain_dict` 保留实际采样地形：`flat`、`slope down`、`slope up`、`uneven rough`、`stairs down`、`discrete obstacles`，对应比例为 `10% / 10% / 10% / 20% / 30% / 20%`。`stairs up`、`hurdle`、`gap`、`ramp`、`beam`、`new stairs down`、`pit` 不进入当前 Stage1 默认训练列；对应 tile 生成函数仍保留为手动实验入口。

当前 `slope down / slope up` 坡度公式为：

$$
s_{\mathrm{slope}} = 0.65 \cdot \frac{row}{num\_rows}
$$

其中 `slope down` 使用负号，`slope up` 使用正号。在 `num_rows = 20` 下，最高 `row 19` 的坡度约为 `0.6175`，对应坡角约 `31.7°`；旧源码系数为 `0.4`，最高 `row 19` 坡角约 `20.8°`。

当前 `stairs down` 单级台阶高度公式为：

$$
h_{\mathrm{step}} = 0.05 + 0.13 \cdot \frac{row}{num\_rows - 1}
$$

在 `num_rows = 20`、`vertical_scale = 0.005 m` 口径下，最高 `row 19` 的实际单级台阶高度为 `0.18 m`。

`discrete obstacles` 最大障碍高度公式历史上曾使用：

$$
h_{\mathrm{obs,max}} = 0.05 + 0.17 \cdot \mathrm{difficulty}
$$

2026-05-15 为降低 obs 高 row 难度，当前源码已改为：

$$
h_{\mathrm{obs,max}} = 0.05 + 0.1159 \cdot \mathrm{difficulty}
$$

其中 `difficulty = row / 20`。在 `vertical_scale = 0.005 m` 量化后，最高 `row 19` 的实际最大障碍高度 / 坑深为 `0.16 m`。

## 7. Curriculum 与 reset

### 7.1 初始课程分配

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `curriculum.enabled` | `True` | 启用课程 |
| `curriculum.max_init_terrain_level` | `5` | 默认初始 row 从 `0-5` 随机 |
| `curriculum.initial_min_terrain_level_by_name["stairs down"]` | `0` | `stairs down` 初始 row 不低于 `0` |
| `curriculum.initial_min_terrain_level_by_name["discrete obstacles"]` | `0` | `discrete obstacles` 初始 row 不低于 `0` |
| `curriculum.initial_max_terrain_level_by_name["stairs down"]` | `4` | `stairs down` 初始 row 不高于 `4` |
| `curriculum.initial_max_terrain_level_by_name["discrete obstacles"]` | `4` | `discrete obstacles` 初始 row 限制为 `4` |
| `curriculum.default_terrain_name` | `flat` | 默认地形名，仅用于初始化检查和默认类型索引 |
| `curriculum.terrain_column_recycle_completed_envs` | `True` | 最高 row 完成后的 env 不永久闲置，而是回收到剩余未完成地形列 |
| `curriculum.terrain_column_completed_retention_ratio` | `0.20` | 已完成 / retired 列保留采样目标比例；普通 completed 列按初始 row 采样，hard-window completed 列按 completed hard-window 起点采样 |
| `curriculum.terrain_column_stop_when_all_completed` | `False` | 所有列达到 completed-column 判定后不自动停止训练 |
| `curriculum.terrain_column_hard_completion_names` | `stairs down`, `discrete obstacles` | 需要重复 max-row success 才标记为 completed-column 的 hard 地形名 |
| `curriculum.terrain_column_hard_completion_success_count` | `100` | hard column 累计 `100` 次 max-row success 后才标记为 completed-column |

初始化时：

- `flat`、`slope down`、`slope up`、`uneven rough` 仍按默认 `0-5` 均匀随机采样。
- `stairs down` 初始从 row `0-4` 均匀随机开始，保留从低 row 逐步爬到高 row 的学习阶段。
- `discrete obstacles` 初始从 row `0-4` 均匀随机开始，之后由 hard-window recycle 继续集中训练从指定 obs 起点推进到高 row 的窗口。
- `terrain_types` 按 env id 均匀分配到 `0-9` 全部地形列。
- `scene.env_origins` 同步到每个 env 当前 row / column 对应 tile origin。

### 7.2 Episode 内 terrain row 推进

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `curriculum.terrain_column_move_down_progress_ratio` | `0.30` | reset 时若当前目标段进度低于 30%，允许回退到本 env 的 row 地板，但不允许低于已命中过目标后的最高 row |
| `curriculum.terrain_column_recycle_completed_envs` | `True` | 完成 env 动态回收到剩余未完成列 |
| `curriculum.terrain_column_completed_retention_ratio` | `0.20` | 完成列不再完全退出训练；回收候选中优先补足约 20% env 到 completed / retired 列低 row |
| `curriculum.terrain_column_stop_when_all_completed` | `False` | 即使所有 column 都满足 completed-column 计数，也继续训练到 PPO 指定 iteration |
| `curriculum.terrain_column_hard_completion_success_count` | `100` | `stairs down` / `discrete obstacles` 每列累计 `100` 次最高 row 通过后才进入 completed-column；该值只是课程暴露门槛，不等价于稳定习得 |
| `curriculum.terrain_column_full_pass_completion_columns` | `(8, 9)` | 历史字段名；当前表示默认 hard-window repeat completion 列，对应 `discrete obstacles` 两列 |
| `curriculum.terrain_column_full_pass_start_level` | `4` | 默认 hard-window recycle 起点 row，当前用于 `col08/col09` |
| `curriculum.terrain_column_full_pass_success_count` | `100` | 默认 hard-window success 次数，当前用于 `col08/col09` |
| `curriculum.terrain_column_full_pass_start_level_by_name["stairs down"]` | `14` | `stairs down` 第一次高 row success 后的 hard-window recycle 起点 row |
| `curriculum.terrain_column_full_pass_success_count_by_name["stairs down"]` | `100` | `stairs down` hard-window success 次数覆盖值 |
| `curriculum.terrain_column_completed_hard_window_start_level` | `4` | hard-window completed 列完成后继续训练时的默认起点 row，当前用于 obs completed 后保持 `row4+` |
| `curriculum.terrain_column_completed_hard_window_start_level_by_name["stairs down"]` | `14` | `stairs down` completed 后继续保持 `row14+` 训练 |
| `curriculum.terrain_column_completed_hard_window_start_level_by_name["discrete obstacles"]` | `4` | `discrete obstacles` completed 后从 `row4+` retention window 继续反复训练 |
| `curriculum.move_up_distance_ratio` | `0.50` | 继承自共享配置；普通 waypoint curriculum 使用，Stage1 terrain-column 不使用该字段判断升级 |
| `curriculum.move_up_uses_forward_x` | `False` | 继承自共享配置；Stage1 terrain-column 不使用该字段判断升级 |
| `curriculum.move_down_command_ratio` | `0.50` | 继承自共享配置；普通 waypoint curriculum 使用，Stage1 terrain-column 不使用该字段判断降级 |

Stage1 terrain-column 目标的 row 推进发生在 episode 内，而不是 reset 前计时重采样或 reset-time curriculum update：

- 若当前目标点被命中，所有地形的 terrain level 加 `1`；`stairs_down` 和 `discrete obstacles` 不再由 quality gate 阻止 row 推进。
- row 推进后，`scene.env_origins` 同步到新 row / 同 column 的 tile origin。
- row 推进后立刻重采样下一目标点。
- row 推进后同步更新该 env 的 `terrain_level_floor`。后续如果新 row 失败，reset 只能回到这个地板 row，不能退回命中目标前的旧 row。
- 若推进会进入没有合法下一目标的最高 row 区域，本段记为 `terrain_column_completed`，本 step 作为终止结束；reset 时进入 completed-column recycle，而不是把一次连续 attempt 的成败作为额外判据。
- 若 hard terrain 低质量命中目标，本步仍按普通命中逻辑触发 row 推进；`row_advance_without_quality_rate` 用于记录这种“低质量但已晋级”的比例。
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

- 若 `terrain_column_completed=True`，该 env 会作为回收候选进入 completed-column recycle；新的 row 由回收目标列决定，而不是固定保持在最高 row。
- 若由于旧状态或手动设置导致当前 row 已超过最高有效 source row，则只夹紧到最高有效 source row，不进行低 row 重采样。
- 若 episode 因 `far_from_target`、`ball_joint_out_of_bounds`、`time_out` 或 `stuck_timeout` 结束，且没有命中目标，同时 $p_{\mathrm{row}} < 0.30$，则 terrain level 只在高于 `terrain_level_floor` 时减 `1`。
- `terrain_level_floor` 初始化为该地形的最小初始 row；每次命中目标并推进 row 后更新为新 row。也就是说，已经吃到目标点证明通过的 row 不再被 reset 逻辑撤销。
- 若 reset 尝试降级但当前 row 已等于 `terrain_level_floor`，记录 `terrain/move_down_suppressed_by_floor_ratio`，terrain level 保持不变。
- 若 episode 失败/超时但 $p_{\mathrm{row}} \ge 0.30$，保持当前 row 不变，让策略继续在当前难度练习。

最高 row 完成后的训练样本处理：

- 当 env 触发 `terrain_column_completed=True` 时，该完成 step 仍作为当前 episode 的 terminal transition 写入一次训练样本。
- 每个 terrain column 维护完成计数。普通列的完成目标数仍等于训练初始化时该列分到的 env 数；`stairs down` 与 `col08/col09 discrete obstacles` 每个 hard column 统一需要 `100` 次最高 row success。某列累计完成次数达到该目标数后，该列才标记为已完成。
- reset 时，完成 env 不再永久 retired；若仍存在未完成 terrain column，回收候选会先检查 completed / retired 列上的 active env 数是否达到 `ceil(num_envs * 0.20)`。
- 若 completed / retired 列 active env 数低于 20% 目标，新的回收候选优先分配回已完成列。普通 completed 列用 `sample_initial_terrain_levels()` 继续采样；hard-window completed 列不再回低 row，而是从 completed hard-window 起点采样。
- 若 completed / retired 列 active env 数已经达到 20% 目标，其余回收候选继续按当前 active env 数均衡分配到剩余未完成列；恢复原地图后，hard 地形列为 `5-7 stairs down` 和 `8-9 discrete obstacles`。
- 回收到未完成列的 env，默认从目标列当前 active env 的 row 分布中采样，使新增样本加入该列当前训练难度附近；该 sampled row 同时成为该 env 的新 `terrain_level_floor`。
- 对 hard-window completion 列有两个窗口：
  - 未完成时的 hard-window 起点：如果该列已经有过至少 `1` 次最高 row success，后续回收到该列的 env 会固定回到窗口起点；`stairs down` 为 `row14`，`col08/col09 discrete obstacles` 为 `row4`。
  - 完成后的 hard-window 起点：该列达到 completed-column 后，后续 retention / recycle 不再回普通低 row；`stairs down` 从 `row14` 继续采样，`discrete obstacles` 从 `row4` 继续采样。
- 因此当前 `stairs down` 的语义是：先从 `row0-4` 随机低 row 学到第一次最高 row success；之后该列反复从 `row14` 训练到最高 row，累计 `100` 次后 completed；completed 后仍从 `row14` 继续保持训练。中途 reset 不会把一条连续 chain 判废，只会按 row floor / move-down / recycle 规则继续采样。
- 当前 `discrete obstacles` 的语义是：初始从 `row0-4` 随机开始；hard-window repeat 和 completed 后 retention 都从 `row4` 起步，累计 `100` 次 max-row success 后 completed。
- 2026-05-15 之后，日志额外记录 max-row 稳定性指标：`max_row_attempt_count`、`recent_max_row_attempt_count`、`recent_max_row_success_rate`、`success_per_attempt`、`recent_success_per_attempt`、`consecutive_max_row_success`、`max_row_success_with_quality_count`。其中 recent 窗口为最近 `100` 次 max-row attempt，用于区分“时间堆出的累计成功”和“近期稳定通过能力”。
- 若已经没有任何未完成 terrain column，当前默认不再把 env park 成 inactive，也不再让 runner 自动停止；reset 出来的 env 会继续分配到 completed columns。普通列优先从同类 active env 的 row 分布采样，hard-window completed 列强制回到 completed hard-window 起点，从而保持 hard terrain 训练窗口。
- `Stage1Eval/*` 默认只统计 `train_mask=True` 的 active env，并额外输出 `Stage1Eval/global/train_active_rate`、`train_retired_rate`、`train_sample_rate`、`completed_column_rate`、`unfinished_column_count`、`recycled_env_ever_rate`、`completed_column_retention_target_rate`、`completed_column_active_rate`、`completed_column_active_ratio_of_active`、`active_envs_per_completed_column_mean` 和 `active_envs_per_unfinished_column_mean`。

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

当前 `stairs down`、`discrete obstacles` 均属于 `step` class，因此 reset 时都会出生在当前 tile origin 的 xy 坐标上。

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

Stage1 actor 和 critic 使用不同观测维度。当前源码开启 4 帧历史堆叠：

$$
\mathrm{actor} = (54 + 28) \times 4 = 328
$$

$$
\mathrm{critic} = 328 + 34 \times 17 = 906
$$

其中：

- `54` 是 Stage0 继承来的 proprioception / command / last action 基础观测。
- `28` 是从完整 height patch 中确定性提取的低维地形特征 `z_terrain`。
- `82` 是单帧 actor 观测维度，当前 actor 使用 4 帧历史堆叠。
- `34 * 17 = 578` 是 Stage1 完整 height patch，只追加到 critic 观测中，不做历史堆叠。

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
| `terrain_features` | `28` | 内部缩放 | actor 使用的确定性低维地形特征 |
| `terrain_height_patch` | `578` | 原始米制值 | 仅 critic 额外使用的完整 Stage1 地形高度 patch |

单帧 actor 观测包含表中前 `11` 项，即 `54 + 28 = 82` 维；当前 actor 观测为 4 帧历史堆叠，即 `328` 维。critic 观测为 4 帧 actor 观测再追加当前完整 `terrain_height_patch`，即 `906` 维。当前配置类中仍存在 `projected_gravity`、`ball_joint_target_error`、`module_roll_pitch` 等 scale 字段，但当前 `build_observation_descriptor()` 和 `compute_actor_observation_from_raw_terms()` 不把这些项拼入 actor / critic 观测。

### 8.3 观测裁剪与噪声

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `observations.clip_observations` | `100.0` | actor / critic 观测输出后统一 clip 到 `[-100, 100]` |
| `observations.use_history` | `True` | 使用 actor 观测历史堆叠 |
| `observations.history_length` | `4` | 4 帧 actor 观测历史 |
| `observations.terrain_feature_height_scale_m` | `0.25 m` | 地形高度类特征进入 actor 前的归一化尺度 |
| `observations.noise.enabled` | `False` | 当前默认关闭观测噪声 |
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

该值保持米制单位，不额外乘 scale，不额外 clip 到 `[-1, 1]`。当前 actor 不再直接输入完整 height patch；环境先将该 patch 转换为相对地形高度：

$$
H_{\mathrm{rel}} = D_{\mathrm{ref}} - D_{\mathrm{patch}}
$$

其中 `D_patch = z_root - terrain_height`，`D_ref` 使用中车附近支撑区域的中位数。转换后，地形越高，`H_rel` 越大。actor 输入的低维 `terrain_features` 中，高度类特征会除以 `observations.terrain_feature_height_scale_m = 0.25 m` 后 clip 到 `[-1, 1]`；critic 则额外保留原始完整 `D_patch`。

当前已通过回放可视化确认：patch 局部 `+Y` 位于车体左侧。因此 `left_track` 使用 `y > 0`，`right_track` 使用 `y < 0`，`left_right_height_diff_m > 0` 表示左侧轮路径预瞄地形更高。

### 9.3 28 维低维地形特征计算

低维地形特征由 `mdp/terrain_features.py::compute_terrain_features()` 确定性计算。输入为完整 height patch：

$$
D_{\mathrm{patch}} = z_{\mathrm{root}} - h_{\mathrm{terrain}}(x, y)
$$

其中 $D_{\mathrm{patch}}$ 的形状为 `num_envs * 34 * 17`。由于该值是“root 高度减地形高度”，不能直接把数值越大解释为地形越高。因此第一步先用中车附近支撑区域作为参考面，将其转换为相对地形高度：

$$
D_{\mathrm{ref}}
=
\mathrm{median}
\left(
D_{\mathrm{patch}}[x \in [-0.30,0.30], |y| \le 0.20]
\right)
$$

$$
H_{\mathrm{rel}} = D_{\mathrm{ref}} - D_{\mathrm{patch}}
$$

转换后：

- $H_{\mathrm{rel}} > 0$：该采样点地形高于车体中心附近支撑面。
- $H_{\mathrm{rel}} < 0$：该采样点地形低于车体中心附近支撑面。
- $H_{\mathrm{rel}} \approx 0$：该采样点与当前支撑面高度接近。

高度类 actor 特征使用：

$$
f_h(v) =
\mathrm{clip}
\left(
\frac{v}{h_{\mathrm{scale}}},
-1,
1
\right)
$$

其中：

$$
h_{\mathrm{scale}} = 0.25\ \mathrm{m}
$$

`0.25 m` 不是物理最大地形高度，而是网络输入缩放尺度。它的作用是把米制高度压到 `[-1, 1]` 附近：例如 `0.05 m` 会变成 `0.2`，`0.125 m` 会变成 `0.5`，`0.25 m` 及以上会被截断到 `1.0`。

当前特征提取使用以下局部 mask。注意：`center_track` 和 `support_y` 只是 y 方向带状 mask，不是完整二维区域；它们需要和 x 方向范围组合后，才形成实际参与计算的 patch 区域。

当前示意图和几何解释采用以下车辆实测尺寸。该尺寸只用于解释 patch 与车辆几何关系；除非另外修改 `terrain_features.py`，实际训练中的 `left_track` / `right_track` mask 仍保持下表的源码定义。

| 参数 | 数值 / 计算 | 含义 |
|---|---:|---|
| 整车总长 | `1.884419 m` | 完整 STL 包围盒 x 向尺寸 |
| 整车总宽 | `0.560747 m` | 完整 STL 包围盒 y 向尺寸 |
| 车辆半宽 | `0.2803735 m` | `patch_half_width = 0.280374 m` 的几何来源 |
| 前 / 后车长度 | `0.665721 m` | head / tail chassis x 向尺寸 |
| 中车长度 | `0.35 m` | body chassis x 向尺寸 |
| 前 / 后悬 | `0.389232 m` | 车端到对应轴中心线的距离 |
| 前 / 中 / 后轮距 | `0.539059 / 0.538220 / 0.539059 m` | 左右轮关节中心横向距离 |
| 前 / 中 / 后左轮中心 y | `+0.2695295 / +0.269110 / +0.2695295 m` | `+Y` 为车体左侧 |
| 前 / 中 / 后右轮中心 y | `-0.2695295 / -0.269110 / -0.2695295 m` | `-Y` 为车体右侧 |
| 前 / 中 / 后轴中心 x | `+0.552977 / 0 / -0.552977 m` | 以前后轴距 `0.552977 m` 计算 |

因此，当前 `left_track = [0.15, 0.45]` 和 `right_track = [-0.45, -0.15]` 不是“轮胎实体宽度”，而是围绕左右轮中心线的纵向地形预览带。以左轮为例，真实轮中心约在 $y = +0.2695\ \mathrm{m}$，位于 `left_track` 内；`left_track` 向外扩展到 $y = +0.45\ \mathrm{m}$，是为了让 actor 看到轮路径外侧一定范围内的高度变化。

低层 wheel allocator 中用于轮心横向位置计算的 `d1 / d2 / d3` 已统一修正为 `0.539 m`。这三个值参与轮心位置、轮速分配、侧向速度和低滑移控制计算；此前旧值约 `0.447 m` 与当前实测轮距不一致，后续 Stage1 训练默认按 `0.539 m` 口径执行。

| 名称 | x 条件 | y 条件 | 实际用途 |
|---|---|---|---|
| `center_x` / `center_y` | $x \in [-0.30,0.30]$ | $|y| \le 0.20$ | 两者组合后构成中车附近支撑参考面，用于计算 $D_{\mathrm{ref}}$ |
| `front_preview` | $x > \mathrm{patch\_front\_extent}$ | 全部 y | 车体前端之外的前方预览区，用于计算前方高度均值、最大值、最小值和粗糙度 |
| `x_nonnegative` | $x \ge 0$ | 需与具体 y mask 组合 | 车体中心前方区域，用于计算前方整体坡度和 gap 宽度 |
| `center_track` | 全部 x | $|y| \le 0.20$ | 中央纵向带状 mask；与全部 x 组合成中央高度剖面 $p(x)$，再在 $x \ge 0$ 的未来段检测台阶和下落 |
| `left_track` | 全部 x | $0.15 \le y \le 0.45$ | 左轮路径纵向带状 mask，已确认局部 `+Y` 为车体左侧 |
| `right_track` | 全部 x | $-0.45 \le y \le -0.15$ | 右轮路径纵向带状 mask |
| `support_y` | 需与 `rear_mask` / `mid_mask` / `front_mask` 组合 | $|y| \le \mathrm{patch\_half\_width} + 0.05$ | 车体支撑宽度 y 向 mask；单独不代表某一段车体区域 |
| `rear_mask` | $-\mathrm{patch\_rear\_extent} \le x < -0.30$ | 与 `support_y` 组合 | 后车支撑区域 |
| `mid_mask` | $-0.30 \le x \le 0.30$ | 与 `support_y` 组合 | 中车支撑区域 |
| `front_mask` | $0.30 < x \le \mathrm{patch\_front\_extent}$ | 与 `support_y` 组合 | 前车支撑区域 |

若某个 mask 因采样网格或参数变化为空，代码会回退到最近的中心采样点，避免产生空张量或 NaN。

#### 9.3.1 前方区域特征

前方预览高度集合为：

$$
H_{\mathrm{front}} = H_{\mathrm{rel}}[x > \mathrm{patch\_front\_extent}, :]
$$

对应特征：

| 特征名 | 计算方式 | actor 输入 |
|---|---|---|
| `h_front_mean_m` | $\mathrm{mean}(H_{\mathrm{front}})$ | $f_h(\cdot)$ |
| `h_front_max_m` | $\max(H_{\mathrm{front}})$ | $f_h(\cdot)$ |
| `h_front_min_m` | $\min(H_{\mathrm{front}})$ | $f_h(\cdot)$ |
| `front_roughness_m` | $\mathrm{std}(H_{\mathrm{front}})$ | $f_h(\cdot)$ |

中央纵向剖面使用中间轮迹区域的中位数：

$$
p(x_i) =
\mathrm{median}
\left(
H_{\mathrm{rel}}[x_i, |y| \le 0.20]
\right)
$$

相邻 x 点高度差为：

$$
\Delta p_i = p(x_{i+1}) - p(x_i)
$$

只在 $x \ge 0$ 的未来区域中检测台阶和下落：

$$
\Delta p_i^+ = \max(\Delta p_i, 0)
$$

$$
\Delta p_i^- = \max(-\Delta p_i, 0)
$$

对应特征：

| 特征名 | 计算方式 | actor 输入 |
|---|---|---|
| `step_up_height_m` | $\max(\Delta p_i^+)$ | $f_h(\cdot)$ |
| `drop_depth_m` | $\max(\Delta p_i^-)$ | $f_h(\cdot)$ |
| `step_up_distance_norm` | 最近满足 $\Delta p_i^+ > 0.02\ \mathrm{m}$ 的边缘距离，除以前方最大检测距离 | 原值，范围 `[0,1]` |
| `drop_distance_norm` | 最近满足 $\Delta p_i^- > 0.02\ \mathrm{m}$ 的边缘距离，除以前方最大检测距离 | 原值，范围 `[0,1]` |
| `gap_width_norm` | $x \ge 0$ 的中央剖面中 $p(x) < -0.06\ \mathrm{m}$ 的比例 | 原值，范围 `[0,1]` |
| `front_slope` | $(p(x_{\max}) - p(x_{\min})) / (x_{\max} - x_{\min})$ | clip 到 `[-1,1]` |

其中 `step_up_distance_norm` 和 `drop_distance_norm` 越小，表示边缘越靠近车体；越接近 `1`，表示没有检测到明显边缘或边缘在预览区最远处。

#### 9.3.2 左右轮路径特征

左右轮路径分别取局部 `+Y` 和 `-Y` 的纵向轨迹：

$$
p_L(x_i) =
\mathrm{mean}
\left(
H_{\mathrm{rel}}[x_i, 0.15 \le y \le 0.45]
\right)
$$

$$
p_R(x_i) =
\mathrm{mean}
\left(
H_{\mathrm{rel}}[x_i, -0.45 \le y \le -0.15]
\right)
$$

对应特征：

| 特征名 | 计算方式 | actor 输入 |
|---|---|---|
| `left_track_height_mean_m` | $\mathrm{mean}(p_L(x))$，只取前方预览区 | $f_h(\cdot)$ |
| `right_track_height_mean_m` | $\mathrm{mean}(p_R(x))$，只取前方预览区 | $f_h(\cdot)$ |
| `left_track_step_height_m` | 左轮路径未来区域最大正高度跳变 | $f_h(\cdot)$ |
| `right_track_step_height_m` | 右轮路径未来区域最大正高度跳变 | $f_h(\cdot)$ |
| `left_track_drop_depth_m` | 左轮路径未来区域最大负高度跳变 | $f_h(\cdot)$ |
| `right_track_drop_depth_m` | 右轮路径未来区域最大负高度跳变 | $f_h(\cdot)$ |
| `left_right_height_diff_m` | `left_track_height_mean_m - right_track_height_mean_m` | $f_h(\cdot)$ |

由于回放已确认局部 `+Y` 位于车体左侧，因此：

- `left_right_height_diff_m > 0` 表示左侧轮路径更高。
- `left_right_height_diff_m < 0` 表示右侧轮路径更高。

#### 9.3.3 三车体支撑区域特征

前、中、后三段支撑高度分别为：

$$
h_F =
\mathrm{mean}
\left(
H_{\mathrm{rel}}[0.30 < x \le \mathrm{patch\_front\_extent},\ |y| \le \mathrm{patch\_half\_width}+0.05]
\right)
$$

$$
h_M =
\mathrm{mean}
\left(
H_{\mathrm{rel}}[-0.30 \le x \le 0.30,\ |y| \le \mathrm{patch\_half\_width}+0.05]
\right)
$$

$$
h_R =
\mathrm{mean}
\left(
H_{\mathrm{rel}}[-\mathrm{patch\_rear\_extent} \le x < -0.30,\ |y| \le \mathrm{patch\_half\_width}+0.05]
\right)
$$

对应特征：

| 特征名 | 计算方式 | actor 输入 |
|---|---|---|
| `front_support_height_m` | $h_F$ | $f_h(\cdot)$ |
| `middle_support_height_m` | $h_M$ | $f_h(\cdot)$ |
| `rear_support_height_m` | $h_R$ | $f_h(\cdot)$ |
| `front_middle_height_diff_m` | $h_F - h_M$ | $f_h(\cdot)$ |
| `middle_rear_height_diff_m` | $h_M - h_R$ | $f_h(\cdot)$ |
| `support_height_std_m` | $\mathrm{std}(h_F,h_M,h_R)$ | $f_h(\cdot)$ |

这些特征用于让 actor 看到三段车体即将面对的支撑高度关系，例如前车是否将先上台阶、中车是否处在高低过渡区、后车是否仍在低处支撑。

#### 9.3.4 28 维输出顺序

最终 actor 接收的 `terrain_features` 顺序如下：

| index | 特征名 | 物理含义 | 输入形式 |
|---:|---|---|---|
| 0 | `h_front_mean_m` | 前方预览区平均相对高度 | $f_h$ |
| 1 | `h_front_max_m` | 前方预览区最高相对高度 | $f_h$ |
| 2 | `h_front_min_m` | 前方预览区最低相对高度 | $f_h$ |
| 3 | `front_slope` | 前方整体坡度 | 原值 clip |
| 4 | `front_roughness_m` | 前方高度粗糙度 | $f_h$ |
| 5 | `step_up_height_m` | 中央轨迹最大上台阶高度 | $f_h$ |
| 6 | `drop_depth_m` | 中央轨迹最大下落深度 | $f_h$ |
| 7 | `step_up_distance_norm` | 最近上台阶边缘归一化距离 | 原值 |
| 8 | `drop_distance_norm` | 最近下台阶边缘归一化距离 | 原值 |
| 9 | `gap_width_norm` | 前方低洼区域宽度比例 | 原值 |
| 10 | `left_track_height_mean_m` | 左轮路径平均高度 | $f_h$ |
| 11 | `right_track_height_mean_m` | 右轮路径平均高度 | $f_h$ |
| 12 | `left_track_step_height_m` | 左轮路径上台阶高度 | $f_h$ |
| 13 | `right_track_step_height_m` | 右轮路径上台阶高度 | $f_h$ |
| 14 | `left_track_drop_depth_m` | 左轮路径下落深度 | $f_h$ |
| 15 | `right_track_drop_depth_m` | 右轮路径下落深度 | $f_h$ |
| 16 | `left_right_height_diff_m` | 左右轮路径高度差 | $f_h$ |
| 17 | `front_support_height_m` | 前车支撑区域高度 | $f_h$ |
| 18 | `middle_support_height_m` | 中车支撑区域高度 | $f_h$ |
| 19 | `rear_support_height_m` | 后车支撑区域高度 | $f_h$ |
| 20 | `front_middle_height_diff_m` | 前车相对中车高度差 | $f_h$ |
| 21 | `middle_rear_height_diff_m` | 中车相对后车高度差 | $f_h$ |
| 22 | `support_height_std_m` | 三车体支撑高度不均匀程度 | $f_h$ |
| 23 | `g_step_up` | 上台阶 soft gate | 原值 |
| 24 | `g_step_down` | 下台阶 soft gate | 原值 |
| 25 | `g_gap` | gap / 坑 soft gate | 原值 |
| 26 | `g_rough` | 粗糙地形 soft gate | 原值 |
| 27 | `g_flat` | 平地 soft gate | 原值 |

TensorBoard 中 `TerrainFeature/*` 和 `TerrainGate/*` 记录的是诊断值。诊断中的高度项保留米制物理量，便于解释；actor 实际输入中的高度项已经按 $h_{\mathrm{scale}} = 0.25\ \mathrm{m}$ 缩放并截断。

### 9.4 地形 gate 计算

地形 gate 是上述 28 维特征中的最后 5 维。它们不是离散地形标签，而是连续 soft gate，范围均为 `[0,1]`。

#### 9.4.1 上台阶 gate

上台阶 gate 使用中央轨迹未来区域的最大正高度跳变：

$$
g_{\mathrm{step\_up}}
=
\sigma
\left(
\frac{h_{\mathrm{step\_up}} - 0.05}{0.02}
\right)
$$

其中：

- $h_{\mathrm{step\_up}}$ 对应 `step_up_height_m`。
- $0.05\ \mathrm{m}$ 是上台阶激活中心阈值。
- $0.02\ \mathrm{m}$ 是 sigmoid 过渡宽度。

解释：

- `step_up_height_m` 明显小于 `0.05 m` 时，`g_step_up` 接近 `0`。
- `step_up_height_m` 接近 `0.05 m` 时，`g_step_up` 约为 `0.5`。
- `step_up_height_m` 明显大于 `0.05 m` 时，`g_step_up` 接近 `1`。

#### 9.4.2 下台阶 gate

下台阶 gate 使用中央轨迹未来区域的最大负高度跳变：

$$
g_{\mathrm{step\_down}}
=
\sigma
\left(
\frac{d_{\mathrm{drop}} - 0.08}{0.02}
\right)
$$

其中 $d_{\mathrm{drop}}$ 对应 `drop_depth_m`。它表示前方是否存在明显下落边缘。

#### 9.4.3 gap gate

gap gate 同时要求存在下落边缘和一定宽度的低洼区域：

$$
g_{\mathrm{gap}}
=
g_{\mathrm{step\_down}}
\cdot
\sigma
\left(
\frac{w_{\mathrm{gap}} - 0.15}{0.05}
\right)
$$

其中：

- $w_{\mathrm{gap}}$ 对应 `gap_width_norm`。
- `gap_width_norm` 是前方中央剖面中 $p(x) < -0.06\ \mathrm{m}$ 的采样比例。

因此，单个很窄的下落边缘更像 `step_down`，有一定低洼宽度的下落区域才更像 `gap`。

#### 9.4.4 粗糙地形 gate

粗糙地形 gate 使用前方预览区高度标准差：

$$
g_{\mathrm{rough}}
=
\sigma
\left(
\frac{r_{\mathrm{front}} - 0.03}{0.01}
\right)
$$

其中 $r_{\mathrm{front}}$ 对应 `front_roughness_m`。当前阈值含义是：前方高度起伏接近 `0.03 m` 时开始明显激活粗糙地形 gate。

#### 9.4.5 平地 gate

平地 gate 使用剩余量计算：

$$
g_{\mathrm{flat}}
=
1
-
\mathrm{clip}
\left(
g_{\mathrm{step\_up}}
+ g_{\mathrm{step\_down}}
+ g_{\mathrm{gap}}
+ g_{\mathrm{rough}},
0,
1
\right)
$$

因此，`g_flat` 表示“当前前方区域不像台阶、下落、gap 或粗糙地形的程度”。它不是 terrain generator 中的 `flat` column 标签，而是根据局部 patch 几何实时计算出的平地倾向。

#### 9.4.6 gate 的使用边界

当前 gate 有两类用途：

1. 作为 actor 观测的一部分，让 policy 获得低维地形语义。
2. 作为 Stage1 reward / control 的调制因子，例如 terrain-gated speed hard clamp 和 gate-aware contact support。

gate 本身不是 reward 目标。训练并不奖励“识别出台阶”，而是借助 gate 在不同地形条件下强调不同运动行为：台阶前减速、下台阶防俯冲、gap 前保守、粗糙地形保持支撑和平稳。

## 10. Reward 配置

Stage1 当前 reward 计算仍复用共享 reward 主干。按照 `docs/优化方案.md` 第 `14` 节，本轮已经把七个建议全部落地到 Stage1 默认配置中：stuck/no-progress、地形 + 相位速度、相位化爬升、轻量 spin penalty、progress quality multiplier、quality row advance reward、离散障碍 recovery 现在都已经进入当前训练口径。

2026-05-10 曾追加修改：基于上一轮 `700` iteration 的实际奖励量级，将 hard terrain 的 row / level 晋级改为质量门控。2026-05-11 复盘 `96 env / 1315` iteration 长训后确认该 gate 难度过高，`stairs_down` 和 `discrete obstacles` 长期卡在低 row。因此当前默认已关闭 hard terrain 质量晋级机制：`quality_advance_score` 不再决定能否升 row / completed，只保留为 reward / diagnostics 信号。

当前非零权重项：

1. `distance_to_target`
2. `progress_to_target`
3. `reached_target`
4. `angle_diff`
5. `slip_penalty`
6. `action_rate_penalty`
7. `contact_support_penalty`
8. `terrain_aware_edge_speed_penalty`
9. `stuck_penalty`
10. `no_progress_penalty`
11. `airborne_spin_penalty`
12. `hard_terrain_spin_penalty`
13. `step_up_front_posture_penalty`
14. `step_up_module_progress_reward`
15. `rear_follow_reward`
16. `rear_follow_penalty`
17. `quality_row_advance_reward`
18. `recovery_reward`
19. `drop_anti_dive_penalty`

2026-05-14 已删除三个不再提供有效训练信号的 reward 项：`far_from_target` 不再作为 reward，只保留终止保护；旧版 `edge_speed_penalty` 已由 `terrain_aware_edge_speed_penalty` 替代；`action_soft_limit_penalty` 在动作已有 hard clamp 后删除。

`reached_target` 已启用，参数与 Stage0 相同。`action_rate_penalty` 已在 Stage1 启用，用 episode 最大步数归一化。`slip_penalty` 当前使用底层接触权重 mask。`contact_support_penalty` 使用 terrain gate 在平地 / 粗糙、上台阶、下台阶 / gap 之间切换支撑约束。`terrain_aware_edge_speed_penalty` 与执行链路中的 terrain-gated speed hard clamp 配套，用于惩罚台阶 / gap 前的原始命令超速和实际车速超速。

【本轮新增 / 修改标记】

- 【修改】`terrain_aware_edge_speed_penalty` 与控制链路都不再只使用统一 `0.50 m/s`，而是共享地形 + 相位速度上限。
- 【修改】`stuck_speed_threshold_mps` 从 `0.05` 提高到 `0.10`，`stuck_penalty_grace_s` 从 `1.0 s` 提前到 `0.5 s`，`stuck_penalty` 不再除以 `max_episode_length`，而是按 `control_dt` 计入。
- 【新增】`no_progress_penalty` 从 hard terrain 一开始约束“目标还在前方但几乎没有推进”的样本。
- 【新增】轻量 `airborne_spin_penalty` 和 `hard_terrain_spin_penalty`，用于压制离地空转和卡住时高轮速硬顶。
- 【修改】`step_up_progress_quality_min_multiplier` 从 `0.5` 继续降到 `0.2`，hard terrain 中低质量推进只能保留更小比例的正向 progress reward。
- 【新增】`step_up_module_progress_reward`，用前 / 中 / 后模块支撑高度变化鼓励相位化爬升。
- 【新增】`rear_follow_reward` / `rear_follow_penalty`，专门约束前中车已上台阶但后车未形成跟随支撑的状态。
- 【新增】`quality_row_advance_reward`，只奖励有质量地推进到下一 row。
- 【新增】`recovery_reward` 和 recovery 状态机，允许离散障碍卡住后短时倒车调整，成功重新推进时给正反馈。
- 【修改】`quality_gated_terrain_advance` 当前默认关闭，hard terrain 命中目标后按普通逻辑 row advance / completed；质量相关指标只作为 reward / diagnostics，不再作为课程晋级硬门槛。
- 【修改】`step_up_module_progress_reward` 从单步高度差改为“当前 row 内累计新增模块进展”；2026-05-14 已将权重回退到上一轮 reward-retarget 口径 `40.0`，模块进展比例回退为 `front=0.15, middle=0.35, rear=0.50`。当前判断是问题主要在 reward 激活和设计，而不是继续加大该权重。
- 【修改】上台阶支撑缺失惩罚回退到 `-20.0`，支撑缺失比例回退为 `mid=0.4, rear=0.6`。
- 【修改】`step_up_front_posture_penalty_weight` 从 `-5.0` 提高到 `-12.0`。
- 【修改】2026-05-14 根据 replay trace 诊断，`step_up_posture_weight` 去掉 `target_ahead` 强门槛，不再由 `commands[:,0] > 0.5 m` 决定前车是否需要抬升；当前前车姿态约束只由 `g_step_up` 和地形距离相位窗口决定。
- 【修改】2026-05-14 根据 replay trace 诊断，`rear_follow_reward` 去掉 `target_ahead` 强门槛，并拆成“后车追赶高度进展奖励”和“后车已跟上且有后轮支撑的保持奖励”；追赶奖励不再要求 rear support，保持奖励仍要求后轮支撑；新增诊断 `rear_follow_progress_reward_raw`、`rear_follow_hold_reward_raw` 和 `rear_follow_hold_score`。
- 【修改】2026-05-14 根据 replay trace 诊断，将 recovery 从“卡住后倒退轻罚 + 距离减少 `0.10 m` 才成功”改为三段式恢复动作链：检测卡住后进入 recovery；激活后 `1.0 s` 内的小幅倒退给正奖励；已经倒退过并且 no-progress 解除、重新产生前向进展或目标距离下降时给明显成功奖励。
- 【修改】`terrain_aware_edge_speed_penalty` 中 actual overspeed 系数从固定 `0.5` 改为可配置项；2026-05-14 已回退到上一轮 reward-retarget 口径：`terrain_actual_overspeed_penalty_ratio = 3.0`，总权重为 `-80.0`。
- 【修改】2026-05-13 reward fine-tune 将 `progress_to_target_relax_radius_m` 收紧为 `0.6 m`，并提高 `distance_to_target_weight = 10.0`、`angle_diff_weight = 14.0`，用于减少 obstacles 目标附近绕弯 / 倒退后再吃点的行为。
- 【修改】`drop_anti_dive_penalty` 增加下坑 latch，相位激活后直到前轮稳定接触并满足 pitch rate / 下落速度释放条件才退出；2026-05-14 权重回退到 `-40.0`。
- 【修改】quality 评价拆成严格的 `quality_gate_score` 和加权型 `motion_quality_score`；`quality_gated_terrain_advance` 仍保持关闭。

### 10.1 reward 参数

| 参数 | 当前值 |
|---|---:|
| `target_position_tolerance` | `0.5 m` |
| `distance_to_target_denominator_scale` | `0.01` |
| `distance_to_target_weight` | `10.0` |
| `nominal_goal_distance_m` | `8.0 m` |
| `progress_to_target_clip_m` | `0.25 m` |
| `progress_to_target_relax_radius_m` | `0.6 m` |
| `progress_to_target_weight` | `8.0` |
| `reached_target_base_reward` | `2.0` |
| `reached_target_weight` | `6.0` |
| `far_from_target_margin` | `3.0 m` |
| `angle_diff_weight` | `14.0` |
| `slip_penalty_weight` | `-2.0` |
| `slip_longitudinal_penalty_ratio` | `2.0` |
| `slip_angle_penalty_ratio` | `1.0` |
| `action_rate_penalty_weight` | `-10.0` |
| `action_rate_base_ratio` | `0.5` |
| `action_rate_joint_ratio` | `1.0` |
| `contact_support_penalty_weight` | `-20.0` |
| `contact_support_min_weight` | `0.3` |
| `contact_support_lr_balance_ratio` | `0.15` |
| `step_up_support_mid_ratio` | `0.4` |
| `step_up_support_rear_ratio` | `0.6` |
| `edge_height_low_threshold_m` | `0.04 m` |
| `edge_height_high_threshold_m` | `0.10 m` |
| `terrain_aware_edge_speed_penalty_weight` | `-80.0` |
| `stuck_penalty_weight` | `-3.0` |
| `stuck_gate_threshold` | `0.3` |
| `stuck_speed_threshold_mps` | `0.10 m/s` |
| `stuck_goal_ahead_threshold_m` | `0.5 m` |
| `stuck_penalty_grace_s` | `0.5 s` |
| `stuck_timeout_s` | `4.0 s` |
| `no_progress_penalty_weight` | `-1.0` |
| `no_progress_min_delta_m` | `0.003 m` |
| `no_progress_hard_gate_threshold` | `0.3` |
| `airborne_spin_penalty_weight` | `-1.0` |
| `airborne_spin_velocity_scale_radps` | `20.0 rad/s` |
| `hard_terrain_spin_penalty_weight` | `-1.0` |
| `hard_terrain_spin_speed_threshold_mps` | `0.40 m/s` |
| `hard_terrain_spin_slip_threshold` | `3.0` |
| `hard_terrain_spin_slip_scale` | `3.0` |
| `step_up_front_posture_penalty_weight` | `-12.0` |
| `front_pitch_height_gain_rad_per_m` | `3.0` |
| `front_pitch_max_ref_rad` | `0.30 rad` |
| `front_pitch_sigma_rad` | `0.20 rad` |
| `step_up_approach_distance_min_m` | `0.20 m` |
| `step_up_approach_distance_max_m` | `1.20 m` |
| `step_up_posture_front_gap_start_m` | `0.90 m` |
| `step_up_posture_front_gap_full_m` | `0.25 m` |
| `step_up_goal_ahead_threshold_m` | `0.5 m`，当前不再控制 `step_up_posture_weight` / `rear_follow_reward` |
| `step_up_progress_quality_min_multiplier` | `0.2` |
| `progress_quality_slip_scale` | `4.0` |
| `progress_quality_pitch_rate_sigma_radps` | `1.0 rad/s` |
| `progress_quality_stuck_time_scale_s` | `2.0 s` |
| `step_up_module_progress_reward_weight` | `40.0` |
| `step_up_module_height_progress_scale_m` | `0.05 m` |
| `step_up_module_progress_front_ratio` | `0.15` |
| `step_up_module_progress_middle_ratio` | `0.35` |
| `step_up_module_progress_rear_ratio` | `0.50` |
| `rear_follow_reward_weight` | `8.0` |
| `rear_follow_penalty_weight` | `-36.0` |
| `rear_follow_progress_scale_m` | `0.03 m` |
| `rear_follow_deficit_scale_m` | `0.05 m` |
| `rear_follow_front_middle_threshold_m` | `0.03 m` |
| `rear_follow_hold_min_score` | `0.70` |
| `rear_follow_hold_reward_ratio` | `0.25` |
| `quality_row_advance_reward_weight` | `1.0` |
| `quality_row_advance_min_score` | `0.3` |
| `quality_gated_terrain_advance` | `False` |
| `quality_advance_min_score` | `0.35` |
| `quality_advance_actual_overspeed_margin_mps` | `0.10 m/s` |
| `quality_advance_contact_min` | `0.70` |
| `quality_advance_module_progress_min` | `0.35` |
| `quality_advance_front_progress_threshold_m` | `0.03 m` |
| `quality_advance_middle_progress_threshold_m` | `0.03 m` |
| `quality_advance_rear_progress_threshold_m` | `0.02 m` |
| `terrain_actual_overspeed_penalty_ratio` | `3.0` |
| `recovery_stuck_time_threshold_s` | `0.5 s` |
| `recovery_reverse_cmd_threshold_mps` | `0.05 m/s` |
| `recovery_reverse_reward_window_s` | `1.0 s` |
| `recovery_min_reverse_time_s` | `0.10 s` |
| `recovery_success_step_progress_m` | `0.005 m` |
| `recovery_success_progress_m` | `0.03 m` |
| `recovery_success_forward_speed_mps` | `0.08 m/s` |
| `recovery_reverse_reward_weight` | `0.2` |
| `recovery_success_reward_weight` | `1.0` |
| `drop_anti_dive_penalty_weight` | `-40.0` |
| `drop_guard_gate_threshold` | `0.3` |
| `drop_guard_release_front_support` | `0.7` |
| `drop_guard_release_pitch_rate_radps` | `0.5 rad/s` |
| `drop_guard_release_vz_down_mps` | `0.15 m/s` |
| `drop_guard_release_time_s` | `0.20 s` |
| `drop_guard_latch_penalty_ratio` | `1.5` |
| `drop_theta_safe_rad` | `0.0 rad` |
| `drop_pitch_sigma_rad` | `0.20 rad` |
| `drop_pitch_rate_sigma_radps` | `1.0 rad/s` |
| `drop_vz_down_sigma_mps` | `0.5 m/s` |
| `progress_gate_longitudinal_k` | `3.0` |
| `progress_gate_slip_angle_scale_rad` | `1.5 rad` |
| `progress_gate_min_multiplier` | `0.25` |
| `progress_gate_max_multiplier` | `1.5` |
| `progress_pitch_gate_deadband_deg` | `1.0 deg` |
| `progress_pitch_gate_k_rad` | `0.0` |
| `low_slip_longitudinal_threshold` | `1.0` |
| `low_slip_angle_threshold_rad` | `0.35 rad` |
| `only_positive_rewards` | `False` |

说明：`step_up_front_posture_penalty_weight = -12.0` 继续保留。2026-05-14 hard fine-tune 复盘后，reward 权重回退到上一轮 reward-retarget 口径；当前重点转为检查 `contact_support`、`rear_follow`、`drop_anti_dive`、`front_pitch_ref` 等项的激活相位、释放条件和物理定义是否正确。`drop_anti_dive_penalty_weight = -40.0` 必须结合 drop latch 理解；只有检测到下坑 / gap 相位并进入 guard 后才持续约束，释放条件是前轮接触稳定、pitch rate 和下落速度回到安全范围。

2026-05-13 新修改说明：`front_pitch_ref` 的显式姿态惩罚不再使用裸 `step_up_approach_distance_min_m/max_m` 作为激活窗口，而是使用 `front_gap_m = step_up_distance_m - terrain.patch_front_extent`。其中 `terrain.patch_front_extent = 0.942209 m` 表示中车参考点到整车前端的真实覆盖长度。当前前车姿态权重在 `front_gap_m = 0.90 -> 0.25 m` 逐渐激活；达到满激活后，只要 `g_step_up` 仍存在且目标仍在前方，就不再因为车头已经接近或压上台阶而提前释放。原 `step_up_approach_distance_min_m/max_m` 仍用于已有相位速度限制和模块爬升 phase 逻辑，不再用于 `step_up_front_posture_penalty`。

2026-05-10 新修改说明：Stage1 显式保持 `progress_pitch_gate_k_rad = 0.0`，即不启用 Stage0 新增的中车 pitch-progress gate。`progress_pitch_gate_deadband_deg` 随 Stage0 参数表同步为 `1.0 deg` 只是配置一致性记录，在 `k = 0.0` 时不会参与实际 reward 计算。原因是 Stage1 的 stairs down / discrete obstacles 等复杂地形需要允许中车姿态随地形变化；若直接继承 Stage0 的平地中车水平 gate，会把必要的地形适应姿态误判为低质量推进。

### 10.2 主要 reward 计算

设当前相对目标平面距离为 $D_t$，上一帧距离为 $D_{t-1}$，最大 episode 步数为 $N = 1200$。

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

【本轮修改】hard terrain 下的正向 progress 还会再乘一个质量系数。这个系数不是简单看“有没有向前”，而是同时看滑移、超速、姿态角速度、接触支撑和 stuck 时间：

$$
q
=
\min(q_{\mathrm{slip}},q_{\mathrm{overspeed}},q_{\mathrm{pitch}},q_{\mathrm{contact}},q_{\mathrm{not\_stuck}})
$$

$$
m_{\mathrm{quality}}
=
0.5+(1-0.5)q
$$

$$
m_{\mathrm{hard}}
=
1-g_{\mathrm{hard}}(1-m_{\mathrm{quality}})
$$

最终只有正向 progress 会被质量系数折减：

$$
r_{\mathrm{progress,final}}
=
\begin{cases}
r_{\mathrm{progress}}m_{\mathrm{hard}}, & r_{\mathrm{progress}}>0\\
r_{\mathrm{progress}}, & r_{\mathrm{progress}}\le 0
\end{cases}
$$

通俗理解：车如果是高滑移、姿态剧烈、支撑不好或已经 stuck，即使距离目标略微变近，也不能拿到完整 progress 奖励；但最小 multiplier 保留 `0.5`，避免奖励过稀疏。

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

其中 `contact_support_min_weight = 0.3`。该阈值作用在 $c_i$ 这种接触权重上，不是直接作用在原始法向力上。$c_i=0.3$ 对应归一化法向力约为：

$$
n_i =
0.01 + 0.3(0.08-0.01)
=
0.031
$$

即某个车轮承受约 `3.1%` 整车重量时，该轮接触权重达到 `0.3`。平地六轮均匀静载时，单轮归一化法向力约为 $1/6=0.167$，代入后会被 clamp 到 $c_i=1.0$，所以正常接触轮的接触权重通常接近 `1.0`。

当前模块支撑惩罚按 terrain gate 分三种支撑要求：

$$
P_{\mathrm{all}}
=
\frac{
d_{\mathrm{front}}^2
d_{\mathrm{mid}}^2
d_{\mathrm{rear}}^2
}{3}
$$

$$
P_{\mathrm{up}}
=
\frac{
d_{\mathrm{mid}}^2
0.5d_{\mathrm{rear}}^2
}{1.5}
$$

$$
P_{\mathrm{drop}}
=
\frac{
d_{\mathrm{mid}}^2
d_{\mathrm{rear}}^2
}{2}
$$

其中 $P_{\mathrm{all}}$ 用于平地 / 粗糙地形，要求前、中、后三段都尽量有支撑；$P_{\mathrm{up}}$ 用于上台阶，重点约束中车和后车支撑，允许前车接触发生变化；$P_{\mathrm{drop}}$ 用于下台阶 / gap，重点约束中车和后车支撑，避免整车俯冲。

令：

$$
g_{\mathrm{support}}
=
\max(g_{\mathrm{flat}},g_{\mathrm{rough}})
$$

$$
g_{\mathrm{drop}}
=
\max(g_{\mathrm{step\_down}},g_{\mathrm{gap}})
$$

$$
S_g =
g_{\mathrm{support}}
+g_{\mathrm{step\_up}}
+g_{\mathrm{drop}}
$$

归一化 gate 权重为：

$$
w_{\mathrm{all}} =
\frac{g_{\mathrm{support}}}{S_g},
\quad
w_{\mathrm{up}} =
\frac{g_{\mathrm{step\_up}}}{S_g},
\quad
w_{\mathrm{drop}} =
\frac{g_{\mathrm{drop}}}{S_g}
$$

左右支撑不平衡项为：

$$
P_{\mathrm{lr}}
=
g_{\mathrm{edge}}
\left(
0.2|c_2-c_3|
+0.5|c_0-c_1|
+0.3|c_4-c_5|
\right)
$$

其中：

$$
g_{\mathrm{edge}}
=
\max(g_{\mathrm{step\_up}},g_{\mathrm{step\_down}},g_{\mathrm{gap}})
$$

最终模块支撑惩罚为：

$$
r_{\mathrm{contact}} =
-20.0 \cdot
\frac{
\left(
w_{\mathrm{all}}P_{\mathrm{all}}
+w_{\mathrm{up}}P_{\mathrm{up}}
+w_{\mathrm{drop}}P_{\mathrm{drop}}
+0.15P_{\mathrm{lr}}
\right)
}{N}
$$

旧版 `edge_speed_penalty` 已从 reward 链路删除。当前实际生效的是 `terrain_aware_edge_speed_penalty`，它与执行链路共用同一个地形 + 相位速度函数，不再使用统一 `0.50 m/s` 作为所有 hard terrain 的唯一上限。`edge_height_low_threshold_m` / `edge_height_high_threshold_m` 仍保留，用于构造边缘强度诊断和 terrain-aware 速度链。

$$
v_{\mathrm{fallback}}
=
0.50\ \mathrm{m/s}
$$

四个相位速度为：

$$
v_{\mathrm{up,approach}}=0.45,\quad
v_{\mathrm{up,climb}}=0.75,\quad
v_{\mathrm{down}}=0.35,\quad
v_{\mathrm{obstacle}}=0.40
$$

其中速度单位都是 `m/s`。正高度突变的 approach / climb 由 `step_up_distance_m` 区分：

$$
g_{\mathrm{up,approach}}
=
g_{\mathrm{step\_up}}
\mathbb I(0.20 < d_{\mathrm{step\_up}} < 1.20)
$$

$$
g_{\mathrm{up,climb}}
=
g_{\mathrm{step\_up}}
\mathbb I(d_{\mathrm{step\_up}}\le 0.20)
$$

离散障碍 approach gate 只在未进入正高度突变 climb 时生效，避免障碍列中真正需要爬升牵引时仍被 `0.40 m/s` 压住：

$$
g_{\mathrm{obstacle,approach}}
=
g_{\mathrm{obstacle}}
\left(1-g_{\mathrm{up,climb}}\right)
$$

安全速度从平地速度上限 $2.0\ \mathrm{m/s}$ 开始，分别被各相位 gate 拉低，最后取最严格值：

$$
v_{\mathrm{safe}}
=
\min\left(
\begin{aligned}
&2.0-g_{\mathrm{up,approach}}(2.0-0.45),\\
&2.0-g_{\mathrm{up,climb}}(2.0-0.75),\\
&2.0-g_{\mathrm{step\_down}}(2.0-0.35),\\
&2.0-g_{\mathrm{gap}}(2.0-0.40),\\
&2.0-g_{\mathrm{obstacle,approach}}(2.0-0.40)
\end{aligned}
\right)
$$

执行链路会把 policy 原始前进命令 $v^{\mathrm{raw}}_x$ 的正向部分夹到 $v_{\mathrm{safe}}$ 以内，倒车命令不被这个限速裁剪。reward 中额外惩罚两种超速：

$$
e_{\mathrm{cmd}}
=
\max(v^{\mathrm{raw}}_x-v_{\mathrm{safe}},0)
$$

$$
e_{\mathrm{act}}
=
\max(v^{\mathrm{actual}}_x-v_{\mathrm{safe}},0)
$$

$$
r_{\mathrm{terrain\_speed}}
=
-20.0 \cdot
g_{\mathrm{edge}}
\left(
\left(
\frac{e_{\mathrm{cmd}}}{2.0}
\right)^2
+0.5
\left(
\frac{e_{\mathrm{act}}}{2.0}
\right)^2
\right)
\frac{1}{N}
$$

上台阶前车姿态惩罚当前已启用，权重为 `-12.0`。该项只在上台阶 gate 明显、车头相对台阶边缘进入前车姿态窗口、且目标仍在前方时生效。前车实际 pitch 使用 `spm1_platform_joint_y` 对应的球铰 pitch 位置：

$$
\theta_{\mathrm{front}}
=
q_{\mathrm{spm1,y}}
$$

用户已确认 `spm1_platform_joint_y > 0` 表示前车低头，因此前车抬头参考角取负方向：

$$
\theta_{\mathrm{front,ref}}
=
-
\mathrm{clip}
\left(
3.0h_{\mathrm{step\_up}},
0,
0.30
\right)
$$

前车姿态窗口权重为：

$$
M_{\mathrm{posture}}
=
\mathrm{clip}
\left(
\frac{0.90 - d_{\mathrm{front\_gap}}}{0.90 - 0.25},
0,
1
\right)
\cdot
\mathbb I
\left(
x_{\mathrm{goal,rel}} > 0.5
\right)
$$

姿态误差为：

$$
e_{\theta}
=
\theta_{\mathrm{front}}
-
\theta_{\mathrm{front,ref}}
$$

最终惩罚为：

$$
r_{\mathrm{step\_posture}}
=
-12.0
\cdot
M_{\mathrm{posture}}
\cdot
g_{\mathrm{step\_up}}
\cdot
\left(
\frac{e_{\theta}}{0.20}
\right)^2
\cdot
\frac{1}{N}
$$

该项的物理含义是：在上台阶前车姿态窗口内，如果当前 patch 越像上台阶，前车实际姿态越偏离“适度抬头”的参考角，惩罚越大。它不奖励原地抬头，只惩罚接近和爬升台阶相位的明显姿态偏差。

【本轮新增】相位化模块爬升 reward 不再只看前车 pitch，而是看前 / 中 / 后三个模块支撑区域高度是否真的向上推进。环境会缓存上一 control step 的三个支撑高度：

$$
H_t =
\left[
h_{\mathrm{front}},
h_{\mathrm{middle}},
h_{\mathrm{rear}}
\right]_t
$$

只取正向高度变化：

$$
\Delta H^+
=
\max(H_t-H_{t-1},0)
$$

模块爬升进展分数为：

$$
q_{\mathrm{module}}
=
\mathrm{clip}
\left(
\frac{
0.2\Delta h^+_{\mathrm{front}}
+0.5\Delta h^+_{\mathrm{middle}}
+0.3\Delta h^+_{\mathrm{rear}}
}{0.05},
0,
1
\right)
$$

中后车支撑质量为：

$$
q_{\mathrm{support,phase}}
=
\mathrm{clip}
\left(
\frac{C_{\mathrm{mid}}+C_{\mathrm{rear}}}{2},
0,
1
\right)
$$

当前实现中，`g_climb` 对应 `step_up_distance_m <= 0.20 m` 的正高度突变近距离爬升相位，`g_crest` 对应 `step_up_distance_m > 0.20 m` 的正高度突变通过 / 跟随相位。

最终模块爬升 reward 为：

$$
r_{\mathrm{module\_progress}}
=
1.0
\cdot
\max(g_{\mathrm{climb}},0.5g_{\mathrm{crest}})
\cdot
q_{\mathrm{module}}
\cdot
q_{\mathrm{support,phase}}
\cdot
\Delta t
$$

通俗理解：前车抬头只是准备姿态，真正有价值的是“车身模块确实跨上去了”。所以本轮让中车、后车高度推进和支撑状态也进入奖励。

下台阶 / gap anti-dive 惩罚当前已启用，权重为 `-10.0`。先定义：

$$
g_{\mathrm{drop}}
=
\max(g_{\mathrm{step\_down}},g_{\mathrm{gap}})
$$

前车俯冲量为：

$$
e_{\mathrm{dive}}
=
\max(\theta_{\mathrm{front}}-0,0)
$$

由于 `spm1_platform_joint_y > 0` 表示前车低头，$e_{\mathrm{dive}}$ 越大表示前车越向下扎。整车 pitch 角速度和向下速度分别为：

$$
\omega_{\mathrm{pitch}}
=
|\omega_{b,y}|
$$

$$
v_{z,\mathrm{down}}
=
\max(-v_{w,z},0)
$$

最终惩罚为：

$$
r_{\mathrm{anti\_dive}}
=
-10.0
\cdot
g_{\mathrm{drop}}
\cdot
\left[
0.5
\left(
\frac{e_{\mathrm{dive}}}{0.20}
\right)^2
+0.2
\left(
\frac{\omega_{\mathrm{pitch}}}{1.0}
\right)^2
+0.5
\left(
\frac{v_{z,\mathrm{down}}}{0.5}
\right)^2
\right]
\cdot
\frac{1}{N}
$$

该项的物理含义是：下台阶或 gap 前，不强迫车辆“永远抬头”，只惩罚前车明显低头俯冲、整车 pitch 变化过快和车体快速向下砸落。

stuck penalty / reset 当前在源码中已启用，并且本轮已经增强：

| 参数 | 当前 Stage1 值 | 含义 |
|---|---:|---|
| `stuck_penalty_weight` | `-3.0` | 卡住后的 reward 惩罚权重 |
| `stuck_gate_threshold` | `0.3` | 只在复杂地形 gate 明显激活时判断 stuck |
| `stuck_speed_threshold_mps` | `0.10 m/s` | 【本轮修改】车体前进速度低于该值，认为几乎不动 |
| `stuck_goal_ahead_threshold_m` | `0.5 m` | 目标仍在前方至少 `0.5 m`，才认为是卡住而不是已经到达 |
| `stuck_penalty_grace_s` | `0.5 s` | 【本轮修改】stuck 持续超过该时间后开始扣 reward |
| `stuck_timeout_s` | `4.0 s` | stuck 持续超过该时间后触发 reset |

先定义复杂地形 hard gate：

$$
g_{\mathrm{hard}}
=
\max(g_{\mathrm{step\_up}},g_{\mathrm{step\_down}},g_{\mathrm{gap}})
$$

当前 step 满足以下条件时，记为 `stuck_now=True`：

$$
g_{\mathrm{hard}} > 0.3
$$

$$
|v_x| < 0.10\ \mathrm{m/s}
$$

$$
x_{\mathrm{goal,rel}} > 0.5\ \mathrm{m}
$$

并且该 env 仍是 active training env。若 `stuck_now=True`，stuck 时间累加；否则清零：

$$
t_{\mathrm{stuck},t+1}
=
\begin{cases}
t_{\mathrm{stuck},t}+\Delta t, & \mathrm{stuck\_now}\\
0, & \mathrm{otherwise}
\end{cases}
$$

reward 惩罚为：

$$
r_{\mathrm{stuck}}
=
w_{\mathrm{stuck}}
\mathbb I(t_{\mathrm{stuck}}>0.5)
\Delta t
$$

其中当前默认 $w_{\mathrm{stuck}}=-3.0$。旧实现会再除以最大 episode 步数，实际惩罚几乎不可见；本轮改为乘 $\Delta t$，让 stuck penalty 对 PPO 更新产生可见影响。若 `stuck_timeout_s > 0` 且：

$$
t_{\mathrm{stuck}} >
t_{\mathrm{timeout}}
$$

则触发 `stuck_timeout=True`。在 Stage1 terrain-column reset curriculum 中，`stuck_timeout` 会被视为失败终止，并且只要当前 row 高于该地形允许的最小 row，就直接退一级：

$$
\mathrm{row}_{\mathrm{next}}
=
\max(\mathrm{row}_{\mathrm{current}}-1,\mathrm{row}_{\mathrm{min}})
$$

这与普通 timeout / far-from-target 的退级略有区别：普通失败还会看当前目标段进度是否低于 `terrain_column_move_down_progress_ratio = 0.30`，而 `stuck_timeout` 会直接触发 stuck move-down。

【本轮新增】no-progress penalty 从 hard terrain 一开始就约束“没有有效推进”的样本：

$$
d_{\mathrm{no\_progress}}
=
\frac{
\max(0,0.003-\Delta D)
}{0.003}
$$

$$
r_{\mathrm{no\_progress}}
=
-1.0
\cdot
\mathbb I(g_{\mathrm{hard}}>0.3)
\cdot
\mathbb I(x_{\mathrm{goal,rel}}>0.5)
\cdot
\mathrm{clip}(d_{\mathrm{no\_progress}},0,2)
\cdot
\Delta t
$$

通俗理解：以前必须等到“卡住一段时间”才开始扣分，现在只要复杂地形前目标还在前方、这一步几乎没向目标靠近，就会有小惩罚。它不是强迫高速冲刺，而是减少“顶着不动也继续采样”的低效样本。

【本轮新增】轻量 spin penalty 分两层：

1. `airborne_spin_penalty` 惩罚离地轮空转，权重 `-1.0`。
2. `hard_terrain_spin_penalty` 惩罚 hard terrain 中低速 / no-progress 状态下的高滑移高轮速硬顶，权重 `-1.0`。

hard terrain spin 的 gate 使用：

$$
g_{\mathrm{hard}}
=
\max(g_{\mathrm{step\_up}},g_{\mathrm{step\_down}},g_{\mathrm{gap}})
$$

并乘上低速或 no-progress gate：

$$
r_{\mathrm{hard\_spin}}
=
-1.0
\cdot
g_{\mathrm{hard}}
\cdot
\max(g_{\mathrm{low\_speed}},g_{\mathrm{no\_progress}})
\cdot
q_{\mathrm{spin}}
$$

通俗理解：不是禁止轮子转，而是重点惩罚“车没走、轮子还在拼命转”的情况。

【本轮新增】quality row advance reward 奖励“有质量地通过一行”：

$$
r_{\mathrm{quality\_row}}
=
1.0
\cdot
\mathbb I(\mathrm{row\_advance})
\cdot
g_{\mathrm{hard}}
\cdot
\mathbb I(q\ge 0.3)
\cdot
q
$$

2026-05-10 追加修改后，terrain-column 路径中实际使用的事件奖励改为同一套 hard terrain 晋级门控：

$$
r_{\mathrm{quality\_row}}
=
1.0
\cdot
\mathbb I(\mathrm{hard\_quality\_advance})
\cdot
q_{\mathrm{advance}}
$$

其中 $q_{\mathrm{gate}}$ 是严格质量 gate 分数，仍采用最差项逻辑，适合判断“是否安全通过”，但当前默认不再阻止 row advance：

$$
q_{\mathrm{gate}}
=
\min(
q_{\mathrm{speed}},
q_{\mathrm{contact}},
q_{\mathrm{not\_stuck}},
q_{\mathrm{module}},
q_{\mathrm{rear\_follow}}
)
$$

本轮新增 `motion_quality_score` 作为整体运动质量诊断，使用加权平均而不是最差项：

$$
q_{\mathrm{motion}}
=
0.25q_{\mathrm{speed}}
+0.25q_{\mathrm{contact}}
+0.15q_{\mathrm{not\_stuck}}
+0.20q_{\mathrm{module}}
+0.15q_{\mathrm{rear\_follow}}
$$

`stairs_down` 和 `discrete obstacles` 现在都会统计模块进展与 rear follow 质量，不再只让 `discrete obstacles` 参与 module quality。hard terrain 命中目标后，当前仍按普通逻辑 row advance / completed；只有未来重新开启 `quality_gated_terrain_advance` 时，`q_gate >= 0.35` 且 row 内支撑质量不低于 `0.70` 才会成为晋级条件。

它比直接增大 `progress_to_target_weight` 更安全，因为它奖励的是“跨过一行并且质量合格”，不是奖励原地高滑移硬顶。

【本轮新增】离散障碍 recovery 状态机：

1. 当 `stuck_time_s >= 0.5 s` 且 hard gate、目标仍在前方时，进入 recovery。
2. recovery 中允许小幅倒车；`vx_cmd_limited < -0.05 m/s` 或实际 $v_x < -0.05\ \mathrm{m/s}$ 会记为 `recovery_reverse_now`。
3. recovery 激活后的 `1.0 s` 内，短时倒退不再惩罚，而是按 `+0.2 * Δt` 给小奖励。
4. 当已经有至少 `0.10 s` 倒退 / 姿态调整，并且 no-progress 解除，同时出现单步目标距离下降 `0.005 m`、累计目标距离下降 `0.03 m` 或前向速度恢复到 `0.08 m/s` 以上时，记为 `recovery_success`。
5. `recovery_success` 给 `+1.0` 奖励并清空 stuck 时间；若没有恢复成功，最后仍会受 `stuck_timeout_s = 4.0 s` reset 约束。

通俗理解：障碍前卡住后，策略不再因为“倒一点”被扣分，而是被鼓励先短时让出姿态空间，再重新向前出坑；长期倒退没有额外收益，仍会被 stuck timeout 约束。

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
| `orientation_out_of_bounds` | middle/root roll 绝对值超过 `35.0 deg` |
| `stuck_timeout` | 复杂地形前连续卡住超过 `4.0 s` |
| `terrain_column_completed` | 已推进到该地形列最高有效 source row 后结束该 env 训练 |
| `low_quality_terrain_hit` | 当前默认不会触发；仅在重新开启 `quality_gated_terrain_advance` 时，表示 hard terrain 命中目标但 quality gate 不合格 |
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
\lor
\mathrm{orientation\_out\_of\_bounds}
\lor
\mathrm{stuck\_timeout}
\lor
\mathrm{terrain\_column\_completed}
\lor
\mathrm{low\_quality\_terrain\_hit}
$$

`time_out` 单独作为 truncation 返回。由于 `is_finite_horizon = False`，RSL-RL 会把 timeout 当作 time-limit 处理。

### 11.2 球铰限制

| 关节名 | lower | upper |
|---|---:|---:|
| `spm1_platform_joint_z` | `-0.7` | `0.7` |
| `spm1_platform_joint_y` | `-0.8` | `0.5` |
| `spm1_platform_joint_x` | `-0.5` | `0.5` |
| `spm2_platform_joint_z` | `-0.7` | `0.7` |
| `spm2_platform_joint_y` | `-1.0` | `0.9` |
| `spm2_platform_joint_x` | `-0.5` | `0.5` |

### 11.3 当前非 active termination 字段

Stage1 当前只启用 middle/root roll 的 `orientation_out_of_bounds`，阈值为 `35.0 deg`。目标 yaw tolerance、head/tail roll、head/tail pitch 和 camera collision 仍未纳入 active termination。

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
| `observations.noise.enabled` | `False` |
| `observations.noise.level` | `0.0` |
| `observations.noise.base_lin_vel` | `0.0` |
| `observations.noise.base_ang_vel` | `0.0` |
| `observations.noise.projected_gravity` | `0.0` |
| `observations.noise.ball_joint_pos` | `0.0 rad` |
| `observations.noise.ball_joint_vel` | `0.0 rad/s` |
| `observations.noise.ball_joint_target_error` | `0.01 rad` |
| `observations.noise.module_roll_pitch` | `0.02 rad` |
| `observations.noise.wheel_joint_vel` | `0.0 rad/s` |
| `observations.noise.wheel_longitudinal_slip` | `0.0` |
| `observations.noise.wheel_slip_angle` | `0.0` |
| `observations.noise.wheel_normal_contact_force` | `0.02` |
| `observations.noise.commands` | `0.0` |
| `resets.ball_joint_pos_range` | `(-0.02, 0.02) rad` |
| `resets.ball_joint_vel_range` | `(-0.05, 0.05) rad/s` |
| `resets.wheel_joint_pos_range` | `(0.0, 0.0) rad` |
| `resets.wheel_joint_vel_range` | `(-0.5, 0.5) rad/s` |
| `randomization.enable_action_randomization` | `True` |
| `randomization.joint_position_noise_scale` | `0.0` |
| `randomization.action_noise_std` | `0.015` |
| `randomization.action_bias_std` | `0.005` |
| `randomization.enable_actuator_scale_randomization` | `True` |
| `randomization.ball_joint_stiffness_scale_range` | `(0.80, 1.20)` |
| `randomization.ball_joint_damping_scale_range` | `(0.80, 1.20)` |
| `randomization.ball_joint_effort_limit_scale_range` | `(0.85, 1.15)` |
| `randomization.ball_joint_velocity_limit_scale_range` | `(0.90, 1.10)` |
| `randomization.wheel_joint_effort_limit_scale_range` | `(0.85, 1.15)` |
| `randomization.enable_wheel_friction_randomization` | `True` |
| `randomization.wheel_static_friction_range` | `(0.80, 1.20)` |
| `randomization.wheel_dynamic_friction_range` | `(0.70, 1.10)` |

当前默认开启全部已实现的 Stage1 域随机化：观测噪声、动作噪声 / bias、reset 小扰动、执行器 scale 随机化和车轮接触摩擦随机化均开启；仍不随机地形 mesh 材质、质量 / 质心。

执行器 scale 随机化会在 reset 时改变 PhysX 中的球铰 stiffness、damping、effort limit、velocity limit 和车轮 effort limit；车轮接触摩擦随机化会在 reset 时改变每个 wheel shape 的静 / 动摩擦。

车轮接触摩擦随机化代码路径仍保留，但当前 `enable_wheel_friction_randomization=False` 且静 / 动摩擦 range 均为 `(1.0, 1.0)`，不会按 env reset 改动车轮 collision shapes 的 material properties。

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

【2026-05-11 当前修改】Stage1 默认 `logging.step_metrics_interval = 64`。也就是 `Stage1Eval/*` 和 `extras["metrics"]` 中的大量 step metrics 每 `64` 个 env step 采样一次，不再每步采样；这只降低日志 / 统计的 CPU-GPU 同步频率，不改变 observation、reward、termination、action、curriculum 或 PPO 样本。

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
| `Debug/Stage1/Stuck/*` | 【本轮新增】stuck、no-progress、recovery 的 step 级全局诊断 |
| `Debug/Stage1/HardTerrainSpin/*` | 【本轮新增】hard terrain spin gate、低速 / no-progress gate、空转均值与 spin penalty raw |
| `Debug/Stage1/Posture/*` | 【本轮新增】progress quality、row-level 模块高度推进、quality advance gate、低质量 hit 和 actual overspeed 等 step 级诊断 |
| `Stage1Eval/global/*` | Stage1 全局地形列评价指标，包括 max-row reached、valid-target masked、active / retired 训练样本比例、completed-env recycling、completed-column retention、速度限幅、stuck/no-progress、spin、quality row、quality advance gate 和 recovery 指标 |
| `Stage1Eval/colXX/*` | 各地形列评价指标，包括 `max_row_reached_rate`、`valid_target_masked`、`stuck_penalty_active_rate`、`stuck_timeout_rate`、`vx_cmd_raw`、`vx_cmd_limited`、`vx_actual`、`front_pitch_ref`、`front_pitch_actual`、`rear_pitch_actual`、`wheel_spin_airborne_mean`、`quality_row_advance_rate`、`hard_quality_advance_rate`、`low_quality_hit_rate`、`phase_module_progress_score`、`front_climb_success_rate`、`middle_climb_success_rate`、`rear_follow_success_rate`、`actual_overspeed_near_edge_rate` 和 recovery 相关指标 |

其中 `Action/*`、`LowLevel/*`、`PerWheel/*` 中会出现底层执行摘要指标，但本文档不解释其底层运动学计算过程。

说明：共享 curriculum 代码仍能在普通 waypoint 路径中输出小写 `terrain/*` reset 指标；当前 Stage1 terrain-column 目标路径额外输出 reset-time 的 `terrain/row_progress_at_reset`、`terrain/move_down_ratio`、`terrain/terrain_column_completed_ratio`、`terrain/recycle_candidate_ratio`、`terrain/recycled_env_ratio`、`terrain/recycled_to_retired_column_ratio`、`terrain/recycled_to_unfinished_column_ratio`、`terrain/retired_no_recycle_target_ratio`、`terrain/completed_column_rate`、`terrain/unfinished_column_count`、`terrain/completed_column_active_env_count`、`terrain/clamp_to_last_source_ratio` 和 `terrain/level_after_reset`，用于检查 row 退级、最高 row 完成、completed-env recycling 与 20% completed-column retention 逻辑。

本轮新增后，重点看这些列级日志：

- `Stage1Eval/col05_stairs_down/stuck_penalty_active_rate`
- `Stage1Eval/col06_stairs_down/stuck_penalty_active_rate`
- `Stage1Eval/col07_stairs_down/stuck_penalty_active_rate`
- `Stage1Eval/col08_obstacles/stuck_penalty_active_rate`
- `Stage1Eval/col09_obstacles/stuck_penalty_active_rate`
- `Stage1Eval/col05_stairs_down/stuck_timeout_rate`
- `Stage1Eval/col08_obstacles/stuck_timeout_rate`
- `Stage1Eval/col09_obstacles/stuck_timeout_rate`
- `Stage1Eval/col05_stairs_down/vx_cmd_raw`
- `Stage1Eval/col05_stairs_down/vx_cmd_limited`
- `Stage1Eval/col05_stairs_down/vx_actual`
- `Stage1Eval/col08_obstacles/front_pitch_ref`
- `Stage1Eval/col08_obstacles/front_pitch_actual`
- `Stage1Eval/col09_obstacles/rear_pitch_actual`
- `Stage1Eval/col05_stairs_down/wheel_spin_airborne_mean`
- `Stage1Eval/col08_obstacles/wheel_spin_airborne_mean`
- `Stage1Eval/col09_obstacles/quality_row_advance_rate`
- `Stage1Eval/col08_obstacles/hard_quality_advance_rate`
- `Stage1Eval/col08_obstacles/low_quality_hit_rate`
- `Stage1Eval/col08_obstacles/phase_module_progress_score`
- `Stage1Eval/col08_obstacles/front_climb_success_rate`
- `Stage1Eval/col08_obstacles/middle_climb_success_rate`
- `Stage1Eval/col08_obstacles/rear_follow_success_rate`
- `Stage1Eval/col08_obstacles/actual_overspeed_near_edge_rate`
- `Stage1Eval/col05_stairs_down/low_quality_hit_rate`
- `Stage1Eval/col05_stairs_down/actual_overspeed_near_edge_rate`
- `Stage1Eval/col08_obstacles/recovery_reverse_rate`
- `Stage1Eval/col09_obstacles/recovery_success_rate`

2026-05-11 日志修正：

- 上述 hard-quality 指标在 `stage1_eval.py` 中已经计算，但此前 `rsl_rl/utils/logger.py` 的 Stage1 TensorBoard 白名单未完整包含这些字段，导致部分 `Stage1Eval/global/*` 和 `Stage1Eval/colXX/*` CSV 没有导出。
- 当前已将以下字段补入 `STAGE1_GLOBAL_EVAL_FIELDS`、`STAGE1_FLAT_EVAL_FIELDS` 和 `STAGE1_PER_COLUMN_EVAL_FIELDS`：`hard_quality_advance_rate`、`low_quality_hit_rate`、`raw_hard_hit_rate`、`row_advance_without_quality_rate`、`quality_advance_score`、`phase_module_progress_score`、`front_climb_success_rate`、`middle_climb_success_rate`、`rear_follow_success_rate`、`actual_overspeed_near_edge_rate`、`row_contact_support_min`、`row_stuck_time_max`。
- 同时将这些字段的 global 版本加入 Stage1 控制台优先显示列表，便于长训中途判断质量门控是否真正产生事件。
- 该修正只改变日志写出范围，不改变 reward、termination、curriculum 或策略输入输出。
