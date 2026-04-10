# Complete Car Direct Workflow 项目架构说明

## 1. 项目概述

当前 `RL_Training/` 已经完成从 Isaac Lab manager-based 到 direct workflow 的主线重构。现在的任务定义不再依赖本地 `ObservationsCfg / ActionsCfg / RewardsCfg / EventsCfg` 这一类 manager-based 组合方式，而是改为：

- 用一个共享环境类 `CompleteCarEnv`
- 用一个共享配置主干 `CompleteCarEnvCfg`
- 用多个 stage 配置类做参数覆写
- 用纯函数模块承载观测、奖励、命令、终止逻辑
- 用 runtime helper 承载 terrain 和 sensor 的运行时状态

当前 direct 主线的核心思想是：

- `env` 负责运行时组织与 hook 实现
- `cfg` 负责参数源与默认值
- `runtime helper` 负责有状态的 terrain / sensor 子系统
- `scripts/` 负责训练、回放、枚举、导出等入口
- `gym.register(...)` 负责把 task id 绑定到环境类和配置类

与旧 manager-based 主线相比，当前架构的本质变化是：

- 当前本地任务不再依赖 manager term 图来拼 observation / reward / event / termination
- 当前 `CompleteCarEnv` 直接实现 `DirectRLEnv` 所要求的 hook
- terrain curriculum、spawn offset、sensor 读数聚合都不再放在旧 `envs/base` 或 `utils/terrain.py`
- Stage0 / Stage1 / Stage2 共用同一个 env 类，只靠 cfg 切换阶段差异

代码路径上有一个需要特别澄清的点：

- 当前 terrain runtime 的真实路径是 `tasks/direct/complete_car/terrain/terrain_runtime.py`
- 当前 sensor runtime 的真实路径是 `tasks/direct/complete_car/sensors/sensor_runtime.py`

也就是说，当前主线不是扁平的 `complete_car/terrain_runtime.py`，而是已经拆到 `terrain/` 和 `sensors/` 子目录下。

当前 task id 为：

- `Complete-Car-Stage0-Flat-Direct-v0`
- `Complete-Car-Stage1-Terrain-Direct-v0`
- `Complete-Car-Stage2-Perception-Direct-v0`

## 2. 顶层目录与模块关系

```text
RL_Training/
├── config/
│   └── extension.toml
├── setup.py
├── pyproject.toml
├── README.md
├── complete_car_rl_training/
│   ├── __init__.py
│   ├── paths.py
│   └── tasks/
│       ├── __init__.py
│       └── direct/
│           ├── __init__.py
│           └── complete_car/
│               ├── __init__.py
│               ├── complete_car_env.py
│               ├── complete_car_env_cfg.py
│               ├── stage0_flat_cfg.py
│               ├── stage1_terrain_cfg.py
│               ├── stage2_perception_cfg.py
│               ├── commands.py
│               ├── observations.py
│               ├── rewards.py
│               ├── terminations.py
│               ├── utils.py
│               ├── agents/
│               │   ├── __init__.py
│               │   └── ppo_cfg.py
│               ├── assets/
│               │   ├── __init__.py
│               │   └── robot_cfg.py
│               ├── terrain/
│               │   ├── __init__.py
│               │   ├── terrain_generator.py
│               │   └── terrain_runtime.py
│               └── sensors/
│                   ├── __init__.py
│                   └── sensor_runtime.py
├── scripts/
│   ├── list_envs.py
│   ├── zero_agent.py
│   ├── random_agent.py
│   ├── export_training_stage.py
│   ├── tensorboard_export.py
│   └── rsl_rl/
│       ├── cli_args.py
│       ├── train.py
│       └── play.py
└── docs/
    └── training_workflow_and_tensorboard_guide.md
```

可以把当前项目粗分成四层：

| 层 | 代表文件 | 作用 |
| --- | --- | --- |
| 参数源配置层 | `complete_car_env_cfg.py`、`stage*_cfg.py`、`agents/ppo_cfg.py`、`assets/robot_cfg.py`、`terrain/terrain_runtime.py` 里的 cfg 类、`sensors/sensor_runtime.py` 里的 cfg 类 | 只定义默认参数、开关、尺寸和资源路径 |
| 环境运行时层 | `complete_car_env.py`、`CompleteCarTerrainRuntime`、`CompleteCarSensorRuntime` | 持有机器人、commands、actions、terrain levels、sensor handles、episode log 等运行时状态 |
| 功能逻辑层 | `commands.py`、`observations.py`、`rewards.py`、`terminations.py`、`terrain/terrain_generator.py`、`utils.py` | 纯函数或近似纯函数，负责计算和生成 |
| 训练入口层 | `scripts/rsl_rl/train.py`、`play.py`、`list_envs.py`、`zero_agent.py`、`random_agent.py`、`export_training_stage.py` | 创建 app、解析 task id、加载 cfg、`gym.make()`、训练/回放/导出 |

## 3. 当前任务注册与入口机制

### 3.1 安装与包入口

当前项目通过 `setup.py` 和 `config/extension.toml` 把 `complete_car_rl_training` 安装成一个 Python 包。

关键点是：

- `extension.toml` 中 `[[python.module]]` 指定模块名为 `complete_car_rl_training`
- `setup.py` 用 `find_packages(...)` 安装 `complete_car_rl_training` 及其子包
- 训练脚本里只要执行 `import complete_car_rl_training`，就会触发任务注册链

注册链是：

```text
complete_car_rl_training/__init__.py
-> tasks/__init__.py
-> tasks/direct/__init__.py
-> tasks/direct/complete_car/__init__.py
-> gym.register(...)
```

### 3.2 task ID 如何绑定 env / cfg / agent cfg

`tasks/direct/complete_car/__init__.py` 是当前 direct task 的唯一注册入口。它对三个 task id 都调用了 `gym.register(...)`，并明确写入：

- `entry_point`: `CompleteCarEnv`
- `env_cfg_entry_point`: `Stage0FlatEnvCfg` / `Stage1TerrainEnvCfg` / `Stage2PerceptionEnvCfg`
- `rsl_rl_cfg_entry_point`: `Stage0FlatPPoCfg` / `Stage1TerrainPPoCfg` / `Stage2PerceptionPPoCfg`

映射关系如下：

| Task ID | 环境类 | 环境配置类 | RSL-RL 配置类 |
| --- | --- | --- | --- |
| `Complete-Car-Stage0-Flat-Direct-v0` | `CompleteCarEnv` | `Stage0FlatEnvCfg` | `Stage0FlatPPoCfg` |
| `Complete-Car-Stage1-Terrain-Direct-v0` | `CompleteCarEnv` | `Stage1TerrainEnvCfg` | `Stage1TerrainPPoCfg` |
| `Complete-Car-Stage2-Perception-Direct-v0` | `CompleteCarEnv` | `Stage2PerceptionEnvCfg` | `Stage2PerceptionPPoCfg` |

### 3.3 训练脚本如何把 task ID 变成 cfg 对象

训练主线里，真正把 task id 解析成配置对象的是 Isaac Lab 自带的注册解析工具，而不是本项目手写代码。真实链路是：

```text
scripts/rsl_rl/train.py
-> @hydra_task_config(args_cli.task, args_cli.agent)
-> register_task_to_hydra(...)
-> load_cfg_from_registry(task, "env_cfg_entry_point")
-> load_cfg_from_registry(task, "rsl_rl_cfg_entry_point")
-> Stage*EnvCfg() + Stage*PPoCfg()
```

也就是说：

- task id 的配置来源是 `gym.registry`
- 本项目在 `gym.register(...)` 里登记的是 Python class entry point
- `hydra_task_config(...)` 再从 registry 把这些类实例化出来

`zero_agent.py`、`random_agent.py`、`export_training_stage.py` 不走 Hydra，而是走：

```text
parse_env_cfg(task_name, ...)
-> load_cfg_from_registry(task_name, "env_cfg_entry_point")
-> Stage*EnvCfg()
```

## 4. 核心环境架构

### 4.1 `complete_car_env_cfg.py`：共享 direct 配置主干

`CompleteCarEnvCfg` 继承自 Isaac Lab 的 `DirectRLEnvCfg`，是当前 direct workflow 的统一参数源。

它内部又拆成了几个本地配置块：

| 配置块 | 主要作用 |
| --- | --- |
| `CompleteCarCommandCfg` | 命令维度、重采样周期、曲率采样阈值、命令范围 |
| `CompleteCarControlCfg` | decimation、球铰位置动作缩放、轮速动作缩放、执行器 stiffness / damping / limit |
| `CompleteCarObservationCfg` | 观测缩放、观测裁剪、历史长度、观测噪声 |
| `CompleteCarRewardCfg` | 各 reward scale、tracking std、球铰软限位、姿态阈值 |
| `CompleteCarResetCfg` | 根部位姿扰动、关节 reset 范围、初始速度、最低根高阈值 |
| `CompleteCarRandomizationCfg` | motor strength、joint pos noise、action noise、action bias |
| `CompleteCarTerrainRuntimeCfg` | terrain 开关、模式、材质、curriculum、spawn offset、height scanner 参数 |
| `CompleteCarSensorRuntimeCfg` | IMU / Camera / Lidar 开关与参数 |

`CompleteCarEnvCfg.__post_init__()` 做了三件关键事：

1. 把本地子配置翻译成 `DirectRLEnvCfg` 真正运行需要的字段  
   例如 `self.decimation = self.control.decimation`、`self.action_space = len(CONTROLLED_JOINT_NAMES)`、重新计算 `observation_space`

2. 设置底层仿真参数  
   例如 `sim.dt = 1/120`、`render_interval = decimation`、gravity、PhysX solver 参数、材质摩擦参数

3. 把 reset / control 参数写回 `robot_cfg`  
   例如：
   - `robot_cfg.init_state.pos = self.reset.pos`
   - `robot_cfg.init_state.joint_pos/joint_vel = reset 默认值`
   - `robot_cfg.actuators["ball_joints"]` / `["wheel_joints"]` 的 stiffness、damping、limit 由 `control` 配置覆盖

这意味着：

- `assets/robot_cfg.py` 提供的是“资产模板”
- 真正运行时的执行器参数最终由 `CompleteCarEnvCfg.__post_init__()` 注入

### 4.2 stage cfg 与 base cfg 的关系

当前 stage 配置关系是：

```text
CompleteCarEnvCfg
└── Stage0FlatEnvCfg
    └── Stage1TerrainEnvCfg
        └── Stage2PerceptionEnvCfg
```

每个 stage 类都采用同样的组织方式：

- 先在 `_apply_stage_overrides()` 中修改本阶段参数
- 再在 `__post_init__()` 里显式调用 `CompleteCarEnvCfg.__post_init__()`

这有两个重要后果：

1. stage 覆写会在 base cfg 完成 observation dim、sim、robot actuator 注入之前生效  
   例如 Stage2 打开传感器后，`compute_policy_obs_dim(self)` 会按 Stage2 的 sensor 维度重新计算

2. stage cfg 只做参数差异，不重复 env 逻辑  
   也就是说 Stage0 / Stage1 / Stage2 没有各自的 env 类

### 4.3 `complete_car_env.py`：共享 direct 运行时主类

`CompleteCarEnv` 是三个 stage 共用的唯一环境类。它不自己重写 `step()`，而是给 Isaac Lab 的 `DirectRLEnv.step()` 提供这些 hook：

- `_setup_scene()`
- `_pre_physics_step()`
- `_apply_action()`
- `_get_observations()`
- `_get_rewards()`
- `_get_dones()`
- `_reset_idx()`

因此它的核心职责是：

- 管 scene 里要创建什么
- 管 action 如何转成 joint target
- 管 reward / done / observation 如何在每个 env step 计算
- 管 reset 时 terrain curriculum、spawn、sensor reset、episode log 如何处理

它持有的关键运行时状态包括：

- `self.robot`
- `self._terrain_runtime`
- `self._sensor_runtime`
- `self._ball_joint_ids` / `self._wheel_joint_ids`
- `self.actions` / `self.last_actions` / `self._processed_actions`
- `self.commands` / `self._command_time_left`
- `self._joint_pos_targets` / `self._joint_vel_targets`
- `self._episode_sums`
- `self._root_height_sum` / `self._root_height_min`
- `self._obs_history`

### 4.4 `terrain/terrain_runtime.py`：terrain 运行时状态，不是 terrain 生成规则

`CompleteCarTerrainRuntimeCfg` 只定义 terrain runtime 参数。真正运行时状态在 `CompleteCarTerrainRuntime` 内，包括：

- `_terrain_origins`
- `_terrain_type_map`
- `_terrain_class_map`
- `terrain_levels`
- `terrain_types`
- `terrain_classes`
- `curriculum_ready`

它的职责不是“定义每种 tile 长什么样”，而是：

- 在 scene 中创建 terrain prim 或决定用 ground plane
- 保存 terrain map 对应的 env origin / type / class
- 初始化每个 env 的 `terrain_levels` 和 `terrain_types`
- 在 reset 时更新 curriculum
- 在 reset 时按 terrain class 给 root state 施加 spawn offset

terrain 几何本体来自 `terrain/terrain_generator.py`，terrain runtime 只是把它接入训练环境并维护 episode 间状态。

### 4.5 `sensors/sensor_runtime.py`：传感器运行时与策略特征聚合

`CompleteCarSensorRuntime` 的职责有两层：

1. 在 `_setup_scene()` 阶段把传感器实体挂到 `scene.sensors`
2. 在 `_get_observations()` 阶段把原始传感器数据聚合成 policy feature

当前已支持的传感器配置类有：

- `CompleteCarImuSensorCfg`
- `CompleteCarCameraSensorCfg`
- `CompleteCarLidarSensorCfg`

当前策略侧看到的不是原始高维感知，而是低维聚合特征：

- IMU：`lin_vel_b + ang_vel_b + lin_acc_b + ang_acc_b`，共 12 维
- Camera：对每个 `data_type` 做均值池化  
  当前 Stage2 使用 `["rgb", "distance_to_image_plane"]`，因此相机 policy feature 维度为 4
- Lidar：把 ray distance 按 bin 分块均值池化  
  当前默认 `policy_num_bins = 16`，因此 lidar policy feature 为 16 维

这意味着当前 Stage2 的 perception 仍然是“低维统计特征输入”，不是“原始图像 + CNN”或“原始点云 + 点云编码器”。

还有一个容易忽略的边界：

- `height_scanner` 不是 `sensors cfg` 里的一个独立子配置
- 它由 `terrain.measure_heights` 触发
- `RayCasterCfg` 由 `CompleteCarTerrainRuntimeCfg.build_height_scanner_cfg(...)` 提供
- 但真正实例化是在 `CompleteCarSensorRuntime.build_scene_entities(...)` 里完成

### 4.6 参数源配置、运行时状态、训练入口、功能模块的边界

| 类别 | 当前主文件 | 应该放什么 |
| --- | --- | --- |
| 参数源配置 | `complete_car_env_cfg.py`、`stage*_cfg.py`、`agents/ppo_cfg.py`、`assets/robot_cfg.py` | 默认值、开关、维度、阈值、资源路径 |
| 环境运行时状态 | `complete_car_env.py`、`terrain/terrain_runtime.py`、`sensors/sensor_runtime.py` | buffers、commands、sensor handles、terrain levels、episode logs |
| 训练入口 | `scripts/rsl_rl/train.py`、`play.py`、`list_envs.py`、`zero_agent.py`、`random_agent.py`、`export_training_stage.py` | App 启动、cfg 解析、`gym.make()`、runner 包装 |
| 功能模块 | `commands.py`、`observations.py`、`rewards.py`、`terminations.py`、`terrain/terrain_generator.py`、`utils.py` | 纯计算逻辑、tile 生成、张量工具 |

### 4.7 已完成的模板残余清理

当前 direct 主线已完成以下收口，相关残余不应再按“当前仍存在的技术债”理解：

| 位置 | 处理结果 | 当前状态 |
| --- | --- | --- |
| `scripts/rsl_rl/train.py`、`play.py` 里的 manager-based / MARL 类型联合 | 已移除 | 当前训练与回放脚本只接受 `DirectRLEnvCfg` |
| `train.py` 的 `--export_io_descriptors` 分支 | 已移除 | 当前脚本不再保留 manager-based 专用导出参数 |
| `CompleteCarCommandCfg.heading_command`、`rel_heading_envs`、`ranges.ang_vel_z`、`ranges.heading`、`debug_vis` | 已移除 | 当前命令配置只保留真实接线的 `lin_vel_x / lin_vel_y / curvature / turn_lin_vel_threshold` |
| `CompleteCarRewardCfg.base_height_target` | 已移除 | 当前 reward / termination 配置不再保留未使用字段 |
| `DirectRLEnvCfg.action_noise_model`、`observation_noise_model` | 已接线 | 当前 `CompleteCarEnvCfg.__post_init__()` 会把本地噪声参数翻译为 Isaac Lab 基类 noise model |

需要注意：

- `randomization.action_noise_std`、`randomization.action_bias_std` 仍然保留在本地 cfg 中，但它们现在是 `action_noise_model` 的参数源，而不再由 `CompleteCarEnv` 手写注入。
- `observations.add_noise / noise_level / noise_scales` 仍然保留在本地 cfg 中，但它们现在是 `observation_noise_model` 的参数源，而不再由 `observations.py` 手写加噪。
- 当前默认 stage 都是 `use_history = False`。如果后续打开 observation history，需要重新核对“历史堆叠后的观测噪声语义”是否满足实验意图。

## 5. 分阶段配置说明

### 5.1 Stage0 Flat

文件：`stage0_flat_cfg.py`

目标：

- 提供最短可运行的 flat baseline
- 用最少子系统验证 `reset -> step -> reward -> done -> train`

相对 base trunk 的主要修改：

- `terrain.enabled = False`
- `terrain.mode = "plane"`
- `terrain.curriculum = False`
- `terrain.flat_only_reset = True`
- `sensors.imu.enabled = False`
- `sensors.camera.enabled = False`
- `sensors.lidar.enabled = False`

当前阶段特征：

- 使用 ground plane，不生成 stage1 mesh
- 不启用 perception sensor
- 当前 observation 维度为 42
- 当前 action 维度为 12  
  即 6 个球铰位置目标 + 6 个车轮轮速目标

### 5.2 Stage1 Terrain

文件：`stage1_terrain_cfg.py`

目标：

- 在 Stage0 的 direct 主线之上引入 terrain 和 curriculum
- 仍保持纯本体观测，不把 perception 混入 Stage1

相对 Stage0 的主要新增：

- `terrain.enabled = True`
- `terrain.mode = "generator"`
- `terrain.curriculum = True`
- `terrain.flat_only_reset = False`
- `terrain.max_init_terrain_level = 5`
- `terrain.default_terrain_name = "flat"`
- `terrain.measure_heights = False`

当前阶段特征：

- 使用 `terrain_generator.py` 生成的固定地图 mesh
- curriculum 通过 `terrain_runtime.update_curriculum(...)` 在 reset 时更新
- 当前依然不启用 IMU / Camera / Lidar
- 当前 observation 仍然是 42 维
- 虽然 terrain runtime 支持 `height_scanner`，但 Stage1 默认没有打开

### 5.3 Stage2 Perception

文件：`stage2_perception_cfg.py`

目标：

- 在 Stage1 terrain 主线上开启 perception 通道
- 不新增 env 类，仍然复用 `CompleteCarEnv`

相对 Stage1 的主要新增：

- `sensors.imu.enabled = True`
- `sensors.camera.enabled = True`
- `sensors.camera.data_types = ["rgb", "distance_to_image_plane"]`
- `sensors.lidar.enabled = True`
- `scene.num_envs = 256`

当前阶段特征：

- 仍然保留 Stage1 的 terrain generator + curriculum
- 新增 perception feature，但当前是低维聚合特征，不是原始高维感知编码
- 按当前配置，Stage2 新增的 policy feature 维度是：
  - IMU 12
  - Camera 4
  - Lidar 16
  - 合计 32
- 因此当前 Stage2 observation 维度为 74

## 6. 训练流程 / 调用链

### 6.1 从训练脚本启动到环境创建

按真实调用链，训练过程可以写成：

```text
python scripts/rsl_rl/train.py --task Complete-Car-StageX-...-v0
-> AppLauncher(args_cli)
-> import complete_car_rl_training
-> complete_car_rl_training/__init__.py
-> tasks/__init__.py
-> tasks/direct/__init__.py
-> tasks/direct/complete_car/__init__.py
-> gym.register(task_id, entry_point=CompleteCarEnv, kwargs={env_cfg_entry_point=Stage*EnvCfg, rsl_rl_cfg_entry_point=Stage*PPoCfg})
-> @hydra_task_config(args_cli.task, "rsl_rl_cfg_entry_point")
-> load_cfg_from_registry(task, "env_cfg_entry_point")
-> load_cfg_from_registry(task, "rsl_rl_cfg_entry_point")
-> Stage*EnvCfg() + Stage*PPoCfg()
-> CLI 覆写 env_cfg / agent_cfg
-> gym.make(task, cfg=env_cfg)
-> CompleteCarEnv(cfg)
-> DirectRLEnv.__init__()
-> CompleteCarEnv._setup_scene()
-> RslRlVecEnvWrapper(env)
-> OnPolicyRunner(...).learn(...)
```

### 6.2 `gym.make(...)` 之后环境如何被构造

`gym.make(task, cfg=env_cfg)` 最终会实例化 `CompleteCarEnv`。随后：

1. `CompleteCarEnv.__init__()` 先把 `_terrain_runtime` 和 `_sensor_runtime` 置空，然后调用 `DirectRLEnv.__init__()`
2. `DirectRLEnv.__init__()` 创建 `SimulationContext`、`InteractiveScene`，并调用 `CompleteCarEnv._setup_scene()`
3. `_setup_scene()` 做这些事：
   - 创建 `Articulation(self.cfg.robot_cfg)`
   - 注册到 `scene.articulations["robot"]`
   - 创建 `CompleteCarTerrainRuntime(...)`
   - 调 `terrain_runtime.setup_scene()`  
     返回 ground prim path
   - 如果不是 generator 模式，就 `spawn_ground_plane(...)`
   - 创建 `CompleteCarSensorRuntime(...)`
   - 调 `sensor_runtime.build_scene_entities(self.scene)`
   - `scene.clone_environments(copy_from_source=False)`
   - generator 模式下调用 `terrain_runtime.initialize_after_scene_clone(self.scene)`
   - plane 模式下调用 `terrain_runtime.initialize_plane_after_scene_clone(self.scene)`
   - 加 dome light
4. `DirectRLEnv.__init__()` 继续初始化 base buffers、gym spaces、viewer、noise/event manager 等
5. `CompleteCarEnv.__init__()` 在 `super().__init__()` 返回后，再：
   - 找球铰和车轮 joint id
   - 分配 commands / actions / target / log buffer
   - 建立 `_episode_sums`
   - 根据 `observations.use_history` 分配历史缓冲区

### 6.3 `step()` 主循环的真实顺序

当前项目没有重写 `step()`。真实顺序来自 Isaac Lab `DirectRLEnv.step()`，本地 env 只实现 hook。

顺序如下：

1. PPO / policy 输出动作
2. `RslRlVecEnvWrapper` 把动作传给 `env.step(actions)`
3. `DirectRLEnv.step()` 先调用 `CompleteCarEnv._pre_physics_step(actions)`
4. `_pre_physics_step(...)` 内部做：
   - 复制 `last_actions`
   - 按 `cfg.observations.clip_actions` 裁剪动作
   - 施加本地 action noise / action bias / motor strength
   - 更新 `command_time_left`
   - 对到期 env 调 `resample_velocity_commands(...)`
   - 把前 6 维动作转成球铰位置目标
   - 把后 6 维动作转成轮速目标
5. `DirectRLEnv.step()` 按 `decimation` 重复 physics loop  
   当前默认 `decimation = 2`
6. 每个 physics 子步里：
   - 调 `CompleteCarEnv._apply_action()`
   - `scene.write_data_to_sim()`
   - `sim.step(render=False)`
   - 需要时 `sim.render()`
   - `scene.update(dt=self.physics_dt)`
7. physics loop 结束后：
   - `episode_length_buf += 1`
   - `common_step_counter += 1`
8. 调 `CompleteCarEnv._get_dones()`
9. 调 `CompleteCarEnv._get_rewards()`
10. 对终止 env 调 `CompleteCarEnv._reset_idx(reset_env_ids)`
11. 如有 event manager，执行 interval event  
    当前项目没有自定义 event 配置，通常为空
12. 调 `CompleteCarEnv._get_observations()`
13. 返回：
   - `obs`
   - `reward`
   - `reset_terminated`
   - `reset_time_outs`
   - `extras`

### 6.4 `_get_observations()` 里发生了什么

`CompleteCarEnv._get_observations()` 的真实顺序是：

1. 若存在 `sensor_runtime`，先读：
   - `get_height_features()`
   - `get_policy_features()`
2. 调 `compute_policy_observation(...)`
3. 若启用了 history，则调 `update_history(...)`
4. 若存在 `sensor_runtime`，把原始传感器输出放进 `extras["sensors"]`
5. 返回 `{"policy": policy_obs}`

`obs_groups` 在 `agents/ppo_cfg.py` 中被固定为：

- actor 用 `["policy"]`
- critic 也用 `["policy"]`

因此当前没有单独的 critic state，也没有 asymmetric critic。

### 6.5 `_get_rewards()` 里发生了什么

`CompleteCarEnv._get_rewards()` 调用 `compute_reward_terms(...)`，计算：

- `tracking_lin_vel`
- `tracking_ang_vel`
- `orientation`
- `lin_vel_z`
- `ang_vel_xy`
- `ball_joint_deviation`
- `ball_joint_swing`
- `action_rate`
- `termination`

然后：

- 累积到 `_episode_sums`
- 额外统计 `root_link_pos_w[:, 2]` 的 mean / min
- 返回总 reward

当前 reward 项日志依赖 `REWARD_TERM_NAMES`。如果你新增 reward term，不只要改公式，还要同步这个常量，否则 episode log 不会完整。

### 6.6 `_get_dones()` 里发生了什么

`compute_dones(...)` 计算：

- `time_out`
- `bad_orientation`
- `ball_joint_out_of_bounds`
- 可选 `root_too_low`

其中：

- `bad_orientation` 由 `projected_gravity` 算 tilt angle
- `ball_joint_out_of_bounds` 看球铰角是否越过软限位
- `root_too_low` 只有 `cfg.reset.minimum_root_height` 非空时才启用
- 返回值是 `(terminated, time_out)`

这里有一个设计上的边界要记住：

- `orientation_limit_deg`
- `soft_ball_joint_pos_limit`

虽然是 termination 阈值，但当前放在 `CompleteCarRewardCfg` 里

而：

- `minimum_root_height`

放在 `CompleteCarResetCfg` 里

所以终止条件阈值目前不是集中放在单独的 termination config 中。

### 6.7 `_reset_idx()` 里发生了什么

`CompleteCarEnv._reset_idx(env_ids)` 的顺序是：

1. 先尝试 `terrain_runtime.update_curriculum(...)`
2. 收集上一回合 episode 日志，写入 `extras["log"]`
3. 调 `super()._reset_idx(env_ids)`  
   这一步会：
   - `scene.reset(env_ids)`
   - 重置 base noise model
   - 清零 `episode_length_buf`
4. `sensor_runtime.reset(env_ids)`
5. 清空根高统计
6. `resample_velocity_commands(...)`
7. 采样并写入 root state：
   - 加 env origin
   - 加 `root_x_range`
   - 加 `root_y_range`
   - 加 `root_yaw_range`
   - 写入 reset 速度
   - 如有 terrain runtime，再调 `apply_spawn_offsets(...)`
8. 采样并写入 joint state：
   - ball joint pos / vel 扰动
   - wheel joint pos / vel 扰动
   - 可选 joint position noise
9. 清零 action / last_action / processed_action
10. 恢复 target buffer
11. 重采样 motor strength / action bias
12. 清空 obs history
13. 清零 `_episode_sums`
14. 把 `terrain_runtime.curriculum_ready = True`

这里要注意两个细节：

- terrain curriculum 是在 reset 时更新，不是在每个 step 内更新
- `curriculum_ready` 只有第一次 reset 结束后才设为 `True`，所以初始化阶段不会错误地对“尚未跑过一回合”的 env 提前做 curriculum 更新

## 7. 各核心脚本功能说明

### 7.1 核心模块职责边界

| 文件 / 类 | 唯一职责 | 不应在这里堆什么 |
| --- | --- | --- |
| `complete_car_rl_training/__init__.py` | 导入 `tasks`，触发任务注册链 | 任务逻辑、训练逻辑 |
| `tasks/__init__.py` | 导入 `direct` 包 | 任何业务逻辑 |
| `tasks/direct/complete_car/__init__.py` | 注册 3 个 task id，并绑定 env cfg / agent cfg | 运行时逻辑、reward 公式 |
| `complete_car_env.py` | 统一组织 direct env 运行时 hook 和 buffer | 大量静态 terrain 生成代码、PPO 参数 |
| `complete_car_env_cfg.py` | 共享参数主干，并把配置写回 sim / robot cfg | 每步张量计算 |
| `stage0_flat_cfg.py` | 定义 Stage0 覆写 | 通用逻辑 |
| `stage1_terrain_cfg.py` | 定义 Stage1 覆写 | terrain 具体生成算法 |
| `stage2_perception_cfg.py` | 定义 Stage2 覆写 | 传感器读数处理细节 |
| `terrain/terrain_generator.py` | 生成 stage1 地图、tile、mesh、env origins | curriculum 状态、episode 级逻辑 |
| `terrain/terrain_runtime.py` | 接入 terrain 到 scene，维护 terrain levels/types/classes，做 curriculum 和 spawn offset | reward、sensor preprocessing |
| `sensors/sensor_runtime.py` | 创建 sensor 实体并生成 policy feature / raw extras | PPO 网络结构、terrain curriculum |
| `observations.py` | 拼 policy observation | reset 顺序、scene 创建 |
| `rewards.py` | 计算 reward 项与总 reward | terrain runtime、sensor 构造 |
| `terminations.py` | 计算 terminated / time_out | reset 写状态 |
| `commands.py` | 采样速度命令并管理命令计时器 | 训练器逻辑 |
| `assets/robot_cfg.py` | 机器人 USD、关节名、actuator 分组模板 | 课程学习、reward 公式 |
| `agents/ppo_cfg.py` | RSL-RL runner / policy / algorithm 默认配置 | 机器人物理参数 |
| `paths.py` | 统一工程根、USD、results 路径解析 | 任务逻辑 |
| `scripts/rsl_rl/train.py` | 启动训练、创建 env、包 RSL-RL、保存 yaml、导出 TensorBoard 标量 | 本体 reward / obs 公式 |
| `scripts/rsl_rl/play.py` | 加载 checkpoint、回放、导出 JIT/ONNX | task 注册 |
| `scripts/list_envs.py` | 列出当前注册的 task | 训练逻辑 |
| `scripts/zero_agent.py` | 零动作冒烟 | PPO 参数 |
| `scripts/random_agent.py` | 随机动作冒烟 | PPO 参数 |
| `scripts/export_training_stage.py` | 实例化训练 env 并导出 USD / prim tree | reward / obs 修改 |
| `scripts/isaac_sim/preview_stage1_terrain.py` | 用同一套 terrain generator 预览 terrain 几何 | 训练主循环 |
| `scripts/isaac_sim/control_keyboard.py` | 用同一套资产和控制缩放做 Isaac Sim 键盘验证 | PPO / gym 注册 |
| `RL_Training/README.md` | 人类使用说明和入口索引 | 运行时实现细节 |

### 7.2 与当前 direct 架构直接相关的辅助脚本

| 脚本 | 当前角色 |
| --- | --- |
| `scripts/list_envs.py` | 检查 task 是否真的注册成功 |
| `scripts/zero_agent.py` | 检查 env 是否能 reset 和稳定 step |
| `scripts/random_agent.py` | 检查 action 管线和物理响应是否跑通 |
| `scripts/export_training_stage.py` | 导出组装后的训练 stage，便于看 prim tree 和 terrain 挂接结果 |
| `scripts/isaac_sim/preview_stage1_terrain.py` | 看 terrain generator 产出的几何是否符合预期 |
| `scripts/isaac_sim/control_keyboard.py` | 用训练同源资产和控制缩放做人工交互验证 |

## 8. 修改接口地图（最重要）

| 需求 | 优先修改位置 | 可能联动位置 | 类型 | 注意事项 |
| --- | --- | --- | --- | --- |
| 1. 新增或修改观测 | `observations.py` | `utils.py` 的 `compute_policy_obs_dim()`、`complete_car_env.py`、对应 stage cfg | 环境逻辑改动 + 配置改动 | 如果观测维度变化，必须同步 `compute_policy_obs_dim()`；如果需要新传感器特征，还要改 `sensor_runtime.py` |
| 2. 新增或修改奖励 | `rewards.py` | `complete_car_env_cfg.py` 的 `CompleteCarRewardCfg`、`REWARD_TERM_NAMES` | 环境逻辑改动 + 配置改动 | 新 reward 项要同时加入 `REWARD_TERM_NAMES`，否则 episode log 不完整 |
| 3. 新增或修改动作空间 | `assets/robot_cfg.py`、`complete_car_env.py` | `complete_car_env_cfg.py`、`utils.py`、`observations.py` | 环境逻辑改动 + 配置改动 | 动作维度目前和 `CONTROLLED_JOINT_NAMES` 强耦合；改动作一定要同步 target split、last_action 观测维度 |
| 4. 修改 command 采样方式 | `commands.py` | `complete_car_env_cfg.py` 的 `CompleteCarCommandCfg` | 环境逻辑改动 + 配置改动 | 当前 yaw 命令来自 `lin_vel_x * curvature`；若想恢复独立 `ang_vel_z` 采样，要显式改 `resample_velocity_commands()` |
| 5. 增加或修改终止条件 | `terminations.py` | `CompleteCarRewardCfg`、`CompleteCarResetCfg`、`complete_car_env.py` | 环境逻辑改动 + 配置改动 | 当前终止阈值分散在 `rewards` 和 `reset` 配置里，修改时不要只看 `terminations.py` |
| 6. 修改 reset 行为 | `complete_car_env.py` 的 `_reset_idx()` | `CompleteCarResetCfg`、`terrain_runtime.py`、`sensor_runtime.py` | 环境逻辑改动 + 配置改动 | 当前 reset 还负责 episode log、curriculum、sensor reset、motor strength randomization，改顺序时要整体看 |
| 7. 修改 terrain curriculum | `terrain/terrain_runtime.py` 的 `update_curriculum()` | `stage1_terrain_cfg.py`、`stage2_perception_cfg.py`、`CompleteCarTerrainRuntimeCfg` | 环境逻辑改动 + 配置改动 | 当前 curriculum 在 reset 时更新，不在 step 时更新；别误改到 `terrain_generator.py` |
| 8. 修改 terrain 生成 / terrain runtime 状态 | `terrain/terrain_generator.py` 或 `terrain/terrain_runtime.py` | `stage1_terrain_cfg.py`、`preview_stage1_terrain.py` | 两者都有 | 改几何形状去 `terrain_generator.py`；改 env origin、level、spawn offset、curriculum 去 `terrain_runtime.py` |
| 9. 新增 camera / lidar / imu 传感器 | `sensors/sensor_runtime.py` | `stage2_perception_cfg.py`、`utils.py` | 环境逻辑改动 + 配置改动 | 需要同时补 `build_scene_entities()`、`policy_feature_dim`、`get_policy_features()` |
| 10. 修改感知数据预处理 | `sensors/sensor_runtime.py` 的 `get_policy_features()` | `utils.py`、`agents/ppo_cfg.py` | 环境逻辑改动 | 当前 camera/lidar 都是低维池化；如果改成高维特征，PPO 网络通常也要一起调整 |
| 11. 在 Stage2 中加入 perception 特征 | `stage2_perception_cfg.py` | `sensors/sensor_runtime.py`、`utils.py`、必要时 `observations.py` | 配置改动为主 | 仅开启传感器不等于策略能用好；若新增新特征维度，要确认 obs dim 自动计算正确 |
| 12. 调整不同 stage 的参数 | `stage0_flat_cfg.py`、`stage1_terrain_cfg.py`、`stage2_perception_cfg.py` | `complete_car_env_cfg.py` | 配置改动 | 公共默认值改 base cfg；只针对某阶段的开关和参数改 stage cfg |
| 13. 新增 Stage3 配置 | 新建 `stage3_*.py` | `agents/ppo_cfg.py`、`tasks/direct/complete_car/__init__.py`、README/文档 | 配置改动 + 注册改动 | 推荐继续复用 `CompleteCarEnv`，只新增 stage cfg 和对应 PPO cfg |
| 14. 新增一个新的 direct task ID | `tasks/direct/complete_car/__init__.py` | 新 stage cfg、新 PPO cfg，必要时新 env 类 | 注册改动 | 如果只是参数变体，不需要新 env 类；如果运行语义变了，再考虑新 env 类 |
| 15. 调整训练超参数 | `agents/ppo_cfg.py` | `scripts/rsl_rl/cli_args.py`、`train.py` | 配置改动 | `--num_envs`、`--max_iterations`、`--seed`、`--experiment_name` 可从 CLI 覆写 |
| 16. 调整 PPO / RSL-RL agent 配置 | `agents/ppo_cfg.py` | `scripts/rsl_rl/train.py`、`play.py` | 配置改动 | 当前 `obs_groups` 固定使用 `policy`；如果 observation key 改名，这里必须同步 |
| 17. 修改 step 内的刷新顺序或 physics loop | 首先看 `complete_car_env.py` 的 hook；若还不够，再看 Isaac Lab `DirectRLEnv.step()` | 可能需要在 `CompleteCarEnv` 本地重写 `step()` | 环境逻辑改动 | 当前项目本地没有重写 `step()`；如果你想改“reward 在 reset 前后顺序”这类全局顺序，只改 helper 不够 |
| 18. 修改机器人资产 / joint / actuator | `assets/robot_cfg.py` | `paths.py`、`complete_car_env_cfg.py`、`complete_car_env.py`、`observations.py`、`rewards.py`、`terminations.py`、Isaac Sim 预览脚本 | 配置改动 + 环境逻辑改动 | 改 joint 名或数量会影响 action split、obs dim、reward/termination 的 joint id 映射 |

## 9. 常见开发场景示例

### 场景 1：想增加一个观测量

1. 先看 `observations.py`，决定这个量应该拼到 observation 的哪个位置。
2. 如果新量来自 robot tensor，通常只改 `compute_policy_observation(...)`。
3. 如果新量来自 terrain height 或 sensor，要同时看 `sensor_runtime.py` 或 terrain height scanner。
4. 观测维度变了，必须同步 `utils.py` 里的 `compute_policy_obs_dim()`。
5. 如果只想某个 stage 使用它，再到对应 `stage*_cfg.py` 打开开关。

### 场景 2：想新增一个奖励项

1. 在 `rewards.py` 里新增 reward term 的计算。
2. 在 `CompleteCarRewardCfg` 里加对应 scale 或阈值参数。
3. 把新项加入 `REWARD_TERM_NAMES`。
4. 确认 `_episode_sums` 能记录它。
5. 如果这个奖励依赖新的观测或 joint 语义，再回看 `observations.py` 或 `robot_cfg.py`。

### 场景 3：想为 Stage2 加一个深度相机

1. 先看 `stage2_perception_cfg.py`，决定是否直接在现有 `camera.data_types` 里追加。
2. 再看 `CompleteCarCameraSensorCfg` 是否已经覆盖所需内参、分辨率和 offset。
3. 最后看 `sensor_runtime.py:get_policy_features()`，确认深度图是如何压缩成 policy feature 的。
4. 如果你不想做均值池化，而是想保留更高维输入，就不能只改 cfg，还要改 policy 网络结构。

### 场景 4：想新增一个 Stage3

1. 新建一个 `stage3_*.py`，继承 `Stage2PerceptionEnvCfg` 或 `CompleteCarEnvCfg`。
2. 在里面只写 stage 差异，不复制整份 base cfg。
3. 如果需要独立实验目录，再在 `agents/ppo_cfg.py` 新增 `Stage3...PPoCfg`。
4. 在 `tasks/direct/complete_car/__init__.py` 新增一条 `gym.register(...)`。
5. 再把 README 和文档里的 task id 列表补上。

### 场景 5：想改 terrain curriculum

1. 先看 `terrain/terrain_runtime.py:update_curriculum()`。
2. 它当前只改 `terrain_levels`，不改 `terrain_types`。
3. 如果你想改地形难度推进规则，优先改这里。
4. 如果你想改地图本身长什么样，去 `terrain_generator.py`，不是 `update_curriculum()`。
5. 改完最好再用 `preview_stage1_terrain.py` 和 `export_training_stage.py` 看结果。

### 场景 6：想改 step 内刷新顺序

1. 先看 `complete_car_env.py` 当前提供的 hook。
2. 如果你的需求只是“动作怎么变 target”，改 `_pre_physics_step()` 或 `_apply_action()` 即可。
3. 如果你的需求是“先 reward 再 reset”或“reset 后再刷新 sensors”，那是 `DirectRLEnv.step()` 的顺序问题。
4. 这时要么本地重写 `CompleteCarEnv.step()`，要么明确接受 Isaac Lab 基类顺序。
5. 这种改动属于高风险改动，最好不要只改局部 helper。

## 10. 当前架构的优点与潜在风险

### 优点

- 一个 env 类覆盖所有 stage，避免 Stage0 / Stage1 / Stage2 复制运行时代码。
- `complete_car_env_cfg.py` 作为统一参数主干，stage 差异清晰。
- terrain 和 sensor 被拆成 runtime helper，边界比旧主线更清楚。
- `commands.py`、`observations.py`、`rewards.py`、`terminations.py` 现在都是纯计算模块，便于长期维护。
- task id 到 env cfg / agent cfg 的绑定非常明确，新增 stage 的成本低。
- 预览脚本、导出脚本、训练脚本都已经对齐到同一套 direct 主线资源。

### 潜在风险

- `CompleteCarEnv` 现在已经承担了较多 orchestration 责任，继续加功能时容易变成“大一统 God object”。
- 当前 termination 相关阈值分散在 `RewardCfg` 和 `ResetCfg`，语义上不够集中。
- action clipping 当前复用了 `observations.clip_actions` 字段，命名容易误导。
- 当前 Stage2 的 perception 仍是低维池化特征，不是高容量视觉编码；如果以后切到原始图像输入，改动会比较大。
- `terrain.measure_heights` 的配置在 terrain cfg，但实际 sensor 由 `sensor_runtime.py` 创建，边界容易第一次看错。
- 当前还保留了一些未接线字段和 Isaac Lab 模板残留，后续如果不清理，容易误导新开发者。

## 11. 维护建议

- 继续把每步张量计算留在 `commands.py`、`observations.py`、`rewards.py`、`terminations.py`，不要重新塞回 cfg 文件。
- `complete_car_env.py` 应继续只做 orchestration，不要在里面堆大量 terrain 生成细节或传感器预处理细节。
- terrain 几何生成继续放在 `terrain_generator.py`，terrain episode 状态继续放在 `terrain_runtime.py`。
- 新增 sensor modality 时，优先沿用 `sensor_runtime.py` 的“cfg + build_scene_entities + get_policy_features + policy_feature_dim”模式。
- 新增 stage 时优先新增 stage cfg，而不是复制整套 env 类。
- 若要改全局 `step()` 顺序，建议在本地显式重写 `CompleteCarEnv.step()`，不要靠零散 helper 间接扭曲顺序。
- 如果某些字段确定不会再用，建议后续在代码里清理或在注释中标明“保留但未接线”，降低误判成本。
- 若终止条件持续增加，建议把 termination 相关阈值从 `RewardCfg` / `ResetCfg` 中收敛成独立配置块，避免配置语义继续漂移。

## 附录：快速修改索引

- 改观测：先看 `observations.py`
- 改观测维度：同时看 `utils.py` 的 `compute_policy_obs_dim()`
- 改奖励：先看 `rewards.py`
- 改 reward 日志项：同时看 `REWARD_TERM_NAMES`
- 改动作：先看 `assets/robot_cfg.py` 和 `complete_car_env.py`
- 改命令采样：先看 `commands.py`
- 改终止：先看 `terminations.py`
- 改 reset：先看 `complete_car_env.py:_reset_idx()`
- 改 curriculum：先看 `terrain/terrain_runtime.py:update_curriculum()`
- 改 terrain 几何：先看 `terrain/terrain_generator.py`
- 改 terrain runtime 状态：先看 `terrain/terrain_runtime.py`
- 加 height scanner：先看 `CompleteCarTerrainRuntimeCfg` 和 `sensor_runtime.py`
- 加 IMU / Camera / Lidar：先看 `sensors/sensor_runtime.py`
- 改感知预处理：先看 `sensor_runtime.py:get_policy_features()`
- 改 Stage0 / Stage1 / Stage2 参数：先看对应 `stage*_cfg.py`
- 新增 Stage3：新建 `stage3_*.py`，再改 `tasks/direct/complete_car/__init__.py`
- 新增 task ID：先看 `tasks/direct/complete_car/__init__.py`
- 改 PPO 超参数：先看 `agents/ppo_cfg.py`
- 改训练入口行为：先看 `scripts/rsl_rl/train.py`
- 改回放行为：先看 `scripts/rsl_rl/play.py`
- 看 task 是否注册成功：先跑 `scripts/list_envs.py`
- 做 env 冒烟：先跑 `scripts/zero_agent.py` 或 `scripts/random_agent.py`
- 导出训练 stage：看 `scripts/export_training_stage.py`
- 改机器人 USD / joint / actuator：先看 `assets/robot_cfg.py` 和 `complete_car_env_cfg.py`
- 做 terrain 几何预览：看 `scripts/isaac_sim/preview_stage1_terrain.py`
- 做手动控车验证：看 `scripts/isaac_sim/control_keyboard.py`
