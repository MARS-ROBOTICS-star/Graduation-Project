# Isaac Lab RL模板与MGDP项目结构梳理

本文档分两部分：

1. 以 `Graduation-Project` 为例，梳理 Isaac Lab 风格 RL 项目的模板结构、任务注册链路、环境构造链路，以及各脚本职责。
2. 梳理 `MGDP` 项目的结构，说明各目录、各脚本分别负责什么。

文档组织方式统一为：

- 先给整体架构
- 再给运行调用链
- 最后逐个脚本/文件解释职责

当前说明：

- 当前仓库真正仍在运行的 RL 主线已经迁到 `RL_Training/`，并且已经切到 direct workflow。
- 当前 active direct 主线保留了项目内 vendored 的 PPO 本体，位置在：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/`
- 原来 `RL_Training/scripts/` 下的辅助脚本已经迁到：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/`
- 原来 `RL_Training/utils/` 下的 IK/FK 内容已经迁到：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/`
  其中 active 接口是：
  - `ik_solver.py`
  - `fk_solver.py`
  旧推导资料保留在：
  - `legacy_ik/`
  - `legacy_fk/`
- 本文档中 `Graduation-Project` 这一部分主要保留“旧 manager-based 模板结构”的梳理价值，后续真正执行命令、找入口、定位当前主线时，应优先看：
  - `README.md`
  - `docs/current_status.md`
  - `docs/isaaclab模板使用指南.md`
  - `RL_Training/README.md`

---

## 一、Isaac Lab RL模板梳理：以 Graduation-Project 为例

### 1.1 整体架构

当前仍在使用的 RL 工作区位于：

```text
RL_Training/
```

但本节下面为了说明旧模板到当前项目的演化关系，仍会引用一次早期 manager-based 结构：

```text
src/rl_lab/complete_car_rl_training/
```

它本质上是一个标准 Isaac Lab 扩展式训练项目，可以分成 6 层：

1. 包装与安装层  
   负责把本项目注册成 Isaac Lab 可识别的 Python 包/扩展。
2. 任务自动发现与注册层  
   负责把任务包导入，并把 Gym task 注册到全局 registry。
3. 任务定义层  
   负责定义 RL 任务本身，包括环境类、环境配置、agent 配置、MDP 项。
4. 训练/回放脚本层  
   负责启动 Isaac Sim、解析命令行、创建环境、调用 RSL-RL。
5. 调试/验证脚本层  
   负责列任务、零动作测试、随机动作测试、导出训练场景等。
6. 项目说明与研究路线层  
   负责说明当前训练目标、阶段设计和阅读方式。

从 RL 模板角度看，这个项目的核心不是单个脚本，而是下面这条链：

```text
setup.py / extension.toml
    -> complete_car_rl_training/__init__.py
    -> complete_car_rl_training/tasks/__init__.py
    -> tasks/manager_based/__init__.py
    -> Gym task id: Complete-Car-Rl-Training-v0
    -> env_cfg / env class / rsl_rl_cfg_entry_point
    -> scripts/rsl_rl/train.py
    -> gym.make(...)
    -> ManagerBasedRLEnv / CompleteCarStage1Env
    -> RslRlVecEnvWrapper
    -> OnPolicyRunner
```

### 1.2 项目结构总览

```text
src/rl_lab/complete_car_rl_training/
├── complete_car_rl_training/
│   ├── __init__.py
│   └── tasks/
│       ├── __init__.py
│       └── manager_based/
│           ├── __init__.py
│           ├── complete_car_env_cfg.py
│           ├── complete_car_stage1_env.py
│           ├── stage1_terrain.py
│           ├── mdp/
│           │   ├── __init__.py
│           │   ├── observations.py
│           │   ├── rewards.py
│           │   ├── events.py
│           │   ├── terminations.py
│           │   └── curriculums.py
│           └── agents/
│               ├── __init__.py
│               └── rsl_rl_ppo_cfg.py
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
├── config/
│   └── extension.toml
├── docs/
│   ├── rl_training_route.md
│   └── tensorboard_reading_guide.md
├── setup.py
├── pyproject.toml
├── README.md
└── tools/
    └── ik/
        ├── IK_model.py
        ├── IK_model_true.py
        ├── README.md
        └── test_ik_keyboard.py
```

### 1.3 从任务注册到 RL 环境的调用链

#### A. 安装与扩展声明

- `config/extension.toml`
  - 定义扩展元信息、依赖和 Python 模块名。
  - 告诉 Isaac Lab：这个扩展提供的模块叫 `complete_car_rl_training`。
- `setup.py`
  - 用 `extension.toml` 里的元信息安装项目。
  - 让 `pip install -e .` 之后，Python 能找到 `complete_car_rl_training` 包。
- `pyproject.toml`
  - 管理构建、ruff、pyright、pytest 等开发工具配置。

#### B. Python 包入口

- `complete_car_rl_training/__init__.py`
  - 包根入口。
  - 导入 `.tasks`，从而触发任务注册。

#### C. 任务自动发现

- `complete_car_rl_training/tasks/__init__.py`
  - 用 `import_packages(...)` 自动导入 `tasks` 下的子包。
  - 目的是在包被 import 时，把实际任务定义模块加载进来。
- `complete_car_rl_training/tasks/manager_based/__init__.py`
  - 调 `gym.register(...)` 注册：
    - task id：`Complete-Car-Rl-Training-v0`
    - entry point：`CompleteCarStage1Env`
    - env config entry point：`CompleteCarRlTrainingEnvCfg`
    - agent config entry point：`PPORunnerCfg`
  - 这是当前 Isaac Lab 任务的真正注册点。

#### D. 环境定义

- `complete_car_env_cfg.py`
  - 定义 manager-based 环境配置。
  - 包括：
    - 机器人资产 `ArticulationCfg`
    - scene
    - commands
    - actions
    - observations
    - reset events
    - rewards
    - terminations
    - curriculum
    - Stage1 runtime 参数
  - 它描述的是“RL 任务语义”，不是训练循环。
- `complete_car_stage1_env.py`
  - 自定义 `ManagerBasedRLEnv` 子类。
  - 在环境初始化后导入 stage1 terrain mesh。
  - 显式维护：
    - `terrain_origins`
    - `terrain_levels`
    - `terrain_types`
    - `terrain_class`
    - `env_class`
  - 在 `_reset_idx()` 里执行 terrain curriculum，并按 terrain class 施加不同的 spawn offset。
  - 这是对 Isaac Lab 通用模板的项目级扩展点。
- `stage1_terrain.py`
  - 负责生成 MGDP 风格的 stage1 mixed terrain：
    - heightfield
    - env origins
    - terrain type
    - terrain class
    - trimesh 顶点/面片
  - 这是环境几何层，不是 RL 算法层。

#### E. MDP 项与 Agent 配置

- `mdp/__init__.py`
  - 统一导出 `commands/actions` 用到的 Isaac Lab 配置类，并把 `observations / rewards / events / terminations / curriculums` 这些 term 模块组织在一起。
- `mdp/observations.py`
  - 放 observation term 的具体实现或别名导出。
  - 当前主要是对 Isaac Lab 通用 observation term 的标准化转发。
- `mdp/rewards.py`
  - 放 reward term 的具体实现或别名导出。
  - 当前除了通用 reward term，还保留项目自定义 reward 函数。
- `mdp/events.py`
  - 放 reset/startup/interval 事件项的具体实现或别名导出。
- `mdp/terminations.py`
  - 放终止项的具体实现或别名导出。
- `mdp/curriculums.py`
  - 放标准 Isaac Lab curriculum manager term 的具体实现或别名导出。
  - 当前 Stage1 的 terrain-level curriculum 仍不在这里，而是在 env 子类里管理。
- `agents/rsl_rl_ppo_cfg.py`
  - 定义 RSL-RL 的 PPO runner 配置：
    - rollout 步数
    - 最大迭代数
    - MLP hidden dims
    - 学习率
    - entropy coef 等
  - 它描述的是“算法超参数层”，不是环境层。

#### F. 训练与回放

- `scripts/rsl_rl/train.py`
  - 启动 Isaac Sim
  - 读取 task 与 agent config
  - `gym.make(task, cfg=env_cfg)`
  - 包装成 `RslRlVecEnvWrapper`
  - 创建 `OnPolicyRunner`
  - 执行 `runner.learn(...)`
- `scripts/rsl_rl/play.py`
  - 从日志目录读取 checkpoint
  - 创建环境
  - 加载训练好的策略
  - 执行推理回放
  - 可导出 JIT / ONNX

### 1.4 Isaac Lab 项目中的文件职责分析

#### 1.4.1 包装与配置层

- `config/extension.toml`
  - 扩展元信息声明文件。
  - 说明这是一个 Isaac Lab 扩展，依赖 `isaaclab`、`isaaclab_rl`、`isaaclab_tasks`。
- `setup.py`
  - 安装脚本。
  - 负责把扩展安装为可 import 的 Python 包。
- `pyproject.toml`
  - 开发工具配置。
  - 和训练逻辑无直接关系，但控制项目构建、格式化、静态检查。

#### 1.4.2 文档与路线层

- `README.md`
  - 项目使用说明。
  - 说明如何安装、列任务、做 smoke test、训练、回放。
- `docs/training_workflow_and_tensorboard_guide.md`
  - 当前训练工作流、TensorBoard 阅读和离线诊断说明。
  - 用于训练后分析，不参与运行时逻辑。

#### 1.4.3 包入口层

- `complete_car_rl_training/__init__.py`
  - 包级入口。
  - 一旦 import，这里会继续 import `tasks`，从而触发任务注册。
- `complete_car_rl_training/tasks/__init__.py`
  - 自动导入任务子包。
  - 负责“发现任务定义”。
- `complete_car_rl_training/tasks/manager_based/__init__.py`
  - manager-based 任务分类包，同时也是当前项目的 Gym 注册入口。
  - 当前重构后，这里不再只是占位包。

#### 1.4.4 任务定义层

- `complete_car_env_cfg.py`
  - 最核心的任务配置文件。
  - 当前已经整理成更标准的 Isaac Lab 模板形态：
    - `CommandsCfg`
    - `ActionsCfg`
    - `ObservationsCfg`
    - `EventCfg`
    - `RewardsCfg`
    - `TerminationsCfg`
    - `CurriculumCfg`
  - 此外还额外保留 `Stage1RuntimeCfg`，用来承载 terrain-level curriculum 和按 terrain class reset 这种
    manager cfg 不方便表达的运行时参数。
  - 如果要改 observation/action/reward/termination，通常先看这里。
- `complete_car_stage1_env.py`
  - 自定义环境类。
  - 现在它不只是“导入 terrain mesh”，还承担运行时 terrain 状态管理：
    - 从 `stage1_terrain.py` 读取 `env_origins / terrain_type / terrain_class`
    - 构建 `terrain_levels / terrain_types / env_class`
    - 在 reset 前更新课程学习结果
    - 在 reset 后按 step/gap/other 三类地形补额外 spawn 偏移
  - 如果要改 terrain 导入、special reset、terrain curriculum，通常看这里。
- `stage1_terrain.py`
  - Stage1 地形生成逻辑。
  - 当前已经把地形“定义层”信息集中到这里，包括 tile 的 `terrain_type` 和更粗粒度的 `terrain_class`。
  - 如果要对齐 MGDP 第一阶段 mixed terrain，这个文件最关键。

#### 1.4.5 MDP 层

- `mdp/__init__.py`
  - MDP 模块总入口。
  - 当前不再把所有 term 平铺在一个文件里，而是拆成按职责分组的子模块。
- `mdp/observations.py`
  - observation term 仓库。
  - 后续真实观测函数优先往这里加。
- `mdp/rewards.py`
  - reward term 仓库。
  - 后续真实奖励函数优先往这里加。
- `mdp/events.py`
  - event term 仓库。
  - 后续 reset/startup/interval 事件函数优先往这里加。
- `mdp/terminations.py`
  - termination term 仓库。
  - 后续真实终止条件优先往这里加。
- `mdp/curriculums.py`
  - curriculum term 仓库。
  - 适合放标准 Isaac Lab manager curriculum；Stage1 地形等级 curriculum 仍由 env 子类管理。

#### 1.4.6 Agent 配置层

- `agents/__init__.py`
  - agent 子包入口。
- `agents/rsl_rl_ppo_cfg.py`
  - PPO 配置文件。
  - 调整网络规模、学习率、迭代数、mini-batch 等时看这里。

#### 1.4.7 训练/回放脚本层

- `scripts/rsl_rl/cli_args.py`
  - 统一管理 RSL-RL 训练/回放脚本的命令行参数更新逻辑。
  - 把 CLI 参数写回 `agent_cfg`。
- `scripts/rsl_rl/train.py`
  - 正式训练入口。
  - 整个 Isaac Lab RL 训练链的主脚本。
- `scripts/rsl_rl/play.py`
  - 正式回放入口。
  - 加载 checkpoint 并执行 policy 推理。

#### 1.4.8 调试与验证脚本层

- `scripts/list_envs.py`
  - 列出当前项目注册到 Gym 的 task。
  - 用于验证任务是否成功注册。
- `scripts/zero_agent.py`
  - 零动作 smoke test。
  - 用于验证：环境能否创建、reset、step，而不依赖策略。
- `scripts/random_agent.py`
  - 随机动作 smoke test。
  - 用于验证：action 管道是否可用、环境是否会立刻崩。
- `scripts/export_training_stage.py`
  - 把训练场景导出成 USD。
  - 主要用于检查 scene、terrain、env origins、prim tree 是否符合预期。
- `scripts/tensorboard_export.py`
  - 导出 TensorBoard scalar 为普通文件。
  - 用于离线分析训练日志。

#### 1.4.9 其他项目脚本

- `tools/ik/IK_model.py`
  - 球绞逆运动学相关脚本。
  - 属于结构控制辅助，不是主训练入口。
- `tools/ik/IK_model_true.py`
  - IK 相关的另一份实现或校核版本。
  - 仍然是机构建模辅助代码。
- `tools/ik/test_ik_keyboard.py`
  - 键盘交互式 IK 验证脚本。
  - 用于单独验证“姿态目标 -> IK -> 关节目标”的链路。

### 1.5 这一套 Isaac Lab 模板的理解方式

如果只记最核心的 4 个文件，可以记为：

- `tasks/manager_based/__init__.py`
  - 注册任务
- `complete_car_env_cfg.py`
  - 装配 Commands/Actions/Observations/Events/Rewards/Terminations/Curriculum
- `complete_car_stage1_env.py`
  - 管理 terrain curriculum、env origins 和按地形类别 reset
- `mdp/*.py`
  - 提供具体 term 实现
- `scripts/rsl_rl/train.py`
  - 启动训练

也就是说，Isaac Lab 模板的设计思想是：

- 环境语义和 term 装配放配置里
- term 的具体计算放 `mdp` 子模块里
- 地形定义放 terrain builder 里
- 特殊运行时行为放 env 子类里
- 算法参数放 agent cfg 里
- 训练/回放放独立脚本里

当前这个项目在 Stage1 上已经进一步向 MGDP 靠拢：

- `stage1_terrain.py` 负责“定义地形和 origin/class 数据”
- `complete_car_env_cfg.py` 负责“装配各类 term，并定义课程学习与 reset 参数”
- `mdp/observations.py`、`mdp/rewards.py`、`mdp/events.py`、`mdp/terminations.py`、`mdp/curriculums.py`
  负责“具体 term 实现”
- `complete_car_stage1_env.py` 负责“维护 level/type/class 状态并在 reset 时更新”

这比最初“只把 mesh 导进来，再调用 terrain importer 的默认 origin 更新”更接近 MGDP 的结构分层。

### 1.6 当前 direct 主线：`complete_car/` 逐文件结构

上面 1.1 到 1.5 主要是在解释早期 manager-based 模板的组织思想。  
但当前仓库真正的 RL 主线已经换成：

```text
RL_Training/complete_car_rl_training/tasks/direct/complete_car/
```

这一套不再依赖 manager term manager 去拼装环境，而是采用 Isaac Lab 的 direct workflow：

- 一个 direct env 主类统一负责 reset / observation / reward / done / command / terrain runtime / sensor runtime
- `*_cfg.py` 负责 direct 环境配置和分阶段覆写
- `commands.py`、`observations.py`、`rewards.py`、`terminations.py` 放纯函数 helper
- `terrain/` 和 `sensors/` 保持为 runtime helper，而不是 manager term
- `agents/ppo_cfg.py` 负责训练超参数

#### 1.6.1 当前 direct 目录总览

```text
RL_Training/complete_car_rl_training/tasks/direct/complete_car/
├── __init__.py
├── commands.py
├── complete_car_env.py
├── complete_car_env_cfg.py
├── local_velocity_tracking_reward.py
├── observations.py
├── rewards.py
├── stage0_flat_cfg.py
├── stage1_terrain_cfg.py
├── stage2_perception_cfg.py
├── terminations.py
├── utils.py
├── agents/
│   ├── __init__.py
│   ├── local_rsl_rl_cfg.py
│   └── ppo_cfg.py
├── assets/
│   ├── __init__.py
│   └── robot_cfg.py
├── sensors/
│   ├── __init__.py
│   └── sensor_runtime.py
└── terrain/
    ├── __init__.py
    ├── terrain_generator.py
    └── terrain_runtime.py
```

#### 1.6.2 当前 direct 运行调用链

当前 direct 主线的典型训练链可以理解为：

```text
RL_Training/scripts/rsl_rl/train.py
    -> import complete_car_rl_training
    -> complete_car_rl_training/tasks/direct/complete_car/__init__.py
    -> gym.register(...)
    -> 选择某个 task id
       - Complete-Car-Stage0-Flat-Direct-v0
       - Complete-Car-Stage1-Terrain-Direct-v0
       - Complete-Car-Stage2-Perception-Direct-v0
    -> env_cfg_entry_point
       - Stage0FlatEnvCfg / Stage1TerrainEnvCfg / Stage2PerceptionEnvCfg
    -> rsl_rl_cfg_entry_point
       - Stage0FlatPPoCfg / Stage1TerrainPPoCfg / Stage2PerceptionPPoCfg
    -> gym.make(...)
    -> CompleteCarEnv
    -> _setup_scene()
       - robot_cfg
       - terrain runtime
       - sensor runtime
    -> step()
       -> _pre_physics_step()
       -> _apply_action()
       -> _get_observations()
       -> _get_rewards()
       -> _get_dones()
       -> _reset_idx()
```

也就是说，当前主线最需要抓住的是 4 个入口：

- `__init__.py`
  - 注册 Gym task
- `complete_car_env_cfg.py`
  - 定义 direct 环境共享配置主干
- `complete_car_env.py`
  - 定义 direct 环境主类
- `agents/ppo_cfg.py`
  - 定义 RSL-RL 训练超参数

#### 1.6.3 顶层入口文件

- `__init__.py`
  - 作用：
    - 当前 direct 任务族的注册入口。
    - 把 3 个 stage 的 env cfg 和 PPO cfg 绑定到 3 个 Gym task id。
  - 本文件没有自定义类和函数。
  - 关键行为：
    - `gym.register(...)`
      - 注册 `Complete-Car-Stage0-Flat-Direct-v0`
      - 注册 `Complete-Car-Stage1-Terrain-Direct-v0`
      - 注册 `Complete-Car-Stage2-Perception-Direct-v0`
    - `entry_point`
      - 都指向 `CompleteCarEnv`
    - `env_cfg_entry_point`
      - 分别指向 `Stage0FlatEnvCfg`、`Stage1TerrainEnvCfg`、`Stage2PerceptionEnvCfg`
    - `rsl_rl_cfg_entry_point`
      - 分别指向 `Stage0FlatPPoCfg`、`Stage1TerrainPPoCfg`、`Stage2PerceptionPPoCfg`

#### 1.6.4 环境配置主干

- `complete_car_env_cfg.py`
  - 作用：
    - 当前 direct env 的共享配置主干。
    - 定义 command、control、observation、reward、reset、randomization、terrain、sensor、scene、sim 等全部任务配置。
    - 它是“当前 complete_car 任务语义”最核心的装配文件。
  - 类：
    - `CompleteCarEnvCfg(DirectRLEnvCfg)`
      - direct 环境的顶层配置类。
      - 负责把 Isaac Lab 的 `DirectRLEnvCfg` 扩展成完整车任务自己的配置语义。
    - `CompleteCarEnvCfg.CommandCfg`
      - 高层命令采样配置。
      - 规定命令维度、重采样时间、是否 heading mode、是否零命令、静止环境比例。
    - `CompleteCarEnvCfg.CommandCfg.ranges`
      - 命令采样范围。
      - 规定 `lin_vel_x / lin_vel_y / ang_vel_yaw / heading` 的最小值和最大值。
    - `CompleteCarEnvCfg.ControlCfg`
      - 控制与执行器配置。
      - 规定 decimation、球铰 action 缩放、球铰/车轮关节的 stiffness、damping、effort limit、velocity limit。
    - `CompleteCarEnvCfg.ObservationCfg`
      - policy observation 配置。
      - 规定是否使用 history、history 长度、观测裁剪、动作裁剪、是否加噪、噪声总倍率。
    - `CompleteCarEnvCfg.ObservationCfg.Scales`
      - observation 各分量缩放系数。
      - 规定 attitude、attitude_rate、ball_joint_pos、ball_joint_vel、commands、last_action 的缩放。
    - `CompleteCarEnvCfg.ObservationCfg.noiseScales`
      - observation 各分量噪声幅度配置。
      - 规定 attitude、attitude_rate、ball_joint_pos、ball_joint_vel、commands 的噪声半幅。
    - `CompleteCarEnvCfg.RewardCfg`
      - reward 总配置。
      - 规定 tracking kernel 的标准差、是否只保留正奖励、球铰软限位、姿态阈值等。
    - `CompleteCarEnvCfg.RewardCfg.Scales`
      - reward term 缩放系数。
      - 规定 tracking、orientation、lin_vel_z、ang_vel_xy、ball_joint_deviation、action_rate、termination 等各项权重。
    - `CompleteCarEnvCfg.ResetCfg`
      - reset 配置。
      - 规定 root 初始位姿、速度、随机平移/yaw、球铰/车轮关节初始状态和随机化范围。
    - `CompleteCarEnvCfg.RandomizationCfg`
      - domain randomization 配置。
      - 规定 motor strength 随机化、关节位置噪声、action 噪声和 bias 噪声。
  - 方法：
    - `_build_action_noise_model_cfg()`
      - 根据 `randomization.action_noise_std` 和 `action_bias_std` 动态构造 Isaac Lab 的 action noise model。
    - `_build_observation_noise_model_cfg()`
      - 根据 observation noise scales 构造 Isaac Lab 的 observation noise model。
    - `__post_init__()`
      - 统一收口配置后的联动逻辑。
      - 主要做 4 件事：
        - 根据 active cfg 重算 action/observation/state space
        - 构建 action/observation noise model
        - 把 terrain/control 参数写回 Isaac Lab sim cfg
        - 把 reset 与 actuator 参数写回 `robot_cfg`

- `stage0_flat_cfg.py`
  - 作用：
    - Stage0 平地 baseline 的 direct 环境配置。
  - 类：
    - `Stage0FlatEnvCfg(CompleteCarEnvCfg)`
      - 在共享主干上做“平地、无传感器、无 terrain curriculum”的 stage 覆写。
  - 方法：
    - `_apply_stage_overrides()`
      - 关闭 terrain generator，改为 plane。
      - 关闭 imu、camera、lidar。
    - `__post_init__()`
      - 先执行 stage 覆写，再调用 `CompleteCarEnvCfg.__post_init__()` 完成联动。

- `stage1_terrain_cfg.py`
  - 作用：
    - Stage1 terrain 训练配置。
  - 类：
    - `Stage1TerrainEnvCfg(Stage0FlatEnvCfg)`
      - 在 Stage0 基础上开启生成式地形和 terrain curriculum。
  - 方法：
    - `_apply_stage_overrides()`
      - 打开 terrain generator。
      - 打开 terrain curriculum。
      - 设置 `default_terrain_name`、`max_init_terrain_level` 等 terrain 运行参数。
    - `__post_init__()`
      - 先 stage override，再走共享主干联动。

- `stage2_perception_cfg.py`
  - 作用：
    - Stage2 感知增强训练配置。
  - 类：
    - `Stage2PerceptionEnvCfg(Stage1TerrainEnvCfg)`
      - 在 Stage1 基础上开启传感器并降低并行环境数。
  - 方法：
    - `_apply_stage_overrides()`
      - 打开 imu、camera、lidar。
      - 指定 camera 输出类型。
      - 把 `scene.num_envs` 调小到 256。
    - `__post_init__()`
      - 先 stage override，再走共享主干联动。

#### 1.6.5 direct 环境主类

- `complete_car_env.py`
  - 作用：
    - 当前完整车 direct workflow 的唯一环境主类。
    - 统一管理：
      - scene 构造
      - command 重采样
      - 球铰 action 到 joint target 的映射
      - wheel-speed allocator 调用
      - observation 组装
      - reward 计算
      - done 判定
      - reset 与 terrain curriculum
  - 类：
    - `CompleteCarEnv(DirectRLEnv)`
      - 3 个 stage 共用的 direct env 实现。
  - 方法：
    - `__init__(...)`
      - 初始化 terrain runtime、sensor runtime、wheel-speed allocator、joint id、commands buffer、obs history、episode 日志缓存等。
    - `step(action)`
      - 对 policy action 做裁剪。
      - 调用父类 `step` 执行完整 direct RL 迭代。
      - 对输出的 policy observation 再做裁剪。
    - `_setup_scene()`
      - 创建机器人 articulation。
      - 创建 terrain runtime，对 plane 或 generator terrain 做场景挂载。
      - 创建 sensor runtime 并把传感器实体挂入 scene。
      - clone environments，初始化 env origins，补光照。
    - `_pre_physics_step(actions)`
      - 在物理步前处理动作和命令。
      - 主要逻辑包括：
        - 记录 `last_actions`
        - 应用 motor strength
        - 推进 command timer
        - 对需要的 env 重采样 command
        - 根据 6 维 policy action 写入球铰位置目标
        - 根据实时球铰状态和 command 调 wheel-speed allocator，生成 6 个车轮速度目标
    - `_apply_action()`
      - 把球铰目标位置和车轮目标速度真正写给模拟器。
    - `_get_observations()`
      - 读取 height features 和其他 sensor features。
      - 调 `compute_policy_observation(...)` 生成 policy observation。
      - 如启用 history，则用 `update_history(...)` 叠帧。
    - `_get_rewards()`
      - 调 `compute_reward_terms(...)` 计算 reward 总值和各分项。
      - 同时累计 episode 级统计量，例如各 reward term 和 root height。
    - `_get_dones()`
      - 调 `compute_dones(...)` 计算 `terminated` 和 `time_out`。
    - `_collect_episode_logs(env_ids, terrain_metrics)`
      - 在 reset 前把 reward 均值、root height、command 均值和 terrain curriculum 指标收集到 `extras["log"]`。
    - `_reset_idx(env_ids)`
      - 完成 direct env 的 reset 主流程。
      - 主要包括：
        - terrain curriculum 更新
        - sensor reset
        - root pose / root velocity 重新采样
        - terrain class 对应的 spawn offset
        - 球铰/车轮关节状态随机化
        - command 重采样
        - action / history / reward 缓冲清零
        - motor strength 随机化

#### 1.6.6 命令、观测、奖励、终止辅助脚本

- `commands.py`
  - 作用：
    - 放 command 采样与 command timer 的纯函数 helper。
  - 函数：
    - `resample_velocity_commands(commands, command_time_left, env_ids, cfg)`
      - 对指定 env 重采样 `lin_vel_x / lin_vel_y / ang_vel_yaw / heading`。
      - 同时处理 standing env 比例和 zero-command 模式，并重置 command 剩余时间。
    - `step_command_timer(command_time_left, step_dt)`
      - 每个 step 递减 command 剩余时间。
      - 返回需要重新采样 command 的 env id。

- `observations.py`
  - 作用：
    - 放 observation 拼接与 observation noise helper。
  - 类：
    - `PerComponentUniformNoiseCfg(NoiseCfg)`
      - 当前项目自定义的“按分量独立设置上下界”的噪声配置类。
      - 用于给 Isaac Lab observation noise model 提供 per-component uniform noise。
  - 函数：
    - `per_component_uniform_noise(data, cfg)`
      - 对输入张量逐分量施加均匀噪声。
      - 支持 `add`、`scale`、`abs` 三种模式。
    - `compute_policy_observation(cfg, robot, ball_joint_ids, commands, last_actions, sensor_features)`
      - 构造 policy observation 主向量。
      - 当前主要拼接：
        - `roll, pitch, yaw`
        - `roll_rate, pitch_rate, yaw_rate`
        - `ball_joint_pos`
        - `ball_joint_vel`
        - `commands`
        - `last_action`
        - 可选 sensor features

- `local_velocity_tracking_reward.py`
  - 作用：
    - 放本地化的 command tracking reward kernel。
  - 函数：
    - `compute_velocity_tracking_terms(cfg, robot, commands)`
      - 计算：
        - `tracking_lin_vel`
        - `tracking_ang_vel`
        - `tracking_heading`
      - 使用指数核把速度误差和 heading 误差映射成 reward 分量。

- `rewards.py`
  - 作用：
    - 放 reward 聚合逻辑。
  - 常量：
    - `REWARD_TERM_NAMES`
      - 规定当前 env 需要维护 episode 累积统计的 reward term 名称列表。
  - 函数：
    - `compute_reward_terms(cfg, robot, ball_joint_ids, commands, actions, last_actions, reset_terminated)`
      - 计算每一项 reward term。
      - 把 tracking、姿态惩罚、竖直速度惩罚、球铰偏离惩罚、action_rate、termination 等项按权重聚合成总 reward。

- `terminations.py`
  - 作用：
    - 放终止判定逻辑。
  - 函数：
    - `compute_dones(cfg, robot, ball_joint_ids, episode_length_buf, max_episode_length)`
      - 判定两类 done：
        - `terminated`
        - `time_out`
      - 当前 failure 主要来自：
        - 姿态倾倒过大
        - 球铰角超过软限位
        - root 高度低于最小阈值

- `utils.py`
  - 作用：
    - 放 direct env 各模块都会复用的小型 tensor / 姿态 / 维度辅助函数。
  - 函数：
    - `sample_uniform_tensor(...)`
      - 在指定范围内采样张量。
    - `wrap_to_pi_tensor(angles)`
      - 把角度包到 `[-pi, pi]`。
    - `quaternion_to_rpy(quat_wxyz)`
      - 把四元数转成 `roll, pitch, yaw`。
    - `body_ang_vel_to_rpy_rates(rpy, ang_vel_b)`
      - 把 body frame 角速度转成欧拉角变化率。
    - `yaw_quaternion(yaw)`
      - 根据 yaw 构造纯 yaw 四元数。
    - `quat_mul(q0, q1)`
      - 四元数乘法。
    - `update_history(history_buffer, current_obs)`
      - 维护 observation history buffer，并输出展平后的 history observation。
    - `compute_policy_obs_noise_magnitudes(cfg)`
      - 从 `observations.noise_scales` 推导当前 observation 每个分量对应的噪声幅度。
    - `compute_policy_obs_dim(cfg)`
      - 根据基础 proprioception 维度和 sensor feature 维度，计算最终 policy observation 维度。

#### 1.6.7 资产配置

- `assets/__init__.py`
  - 作用：
    - 统一导出机器人资产配置相关常量。
  - 本文件没有自定义类和函数。

- `assets/robot_cfg.py`
  - 作用：
    - 定义 direct complete-car 任务共享的机器人 articulation 配置。
  - 本文件没有自定义类和函数。
  - 关键内容：
    - `BALL_JOINT_NAMES`
      - 6 个球铰相关关节名列表。
    - `WHEEL_JOINT_NAMES`
      - 6 个轮关节名列表。
    - `LEFT_WHEEL_JOINT_NAMES` / `RIGHT_WHEEL_JOINT_NAMES`
      - 左右轮子分组。
    - `CONTROLLED_JOINT_NAMES`
      - 当前 policy 直接控制的关节集合，等于球铰关节。
    - `COMPLETE_CAR_ARTICULATION_ROOT_PRIM_PATH`
      - articulation root 对应的 prim path。
    - `COMPLETE_CAR_CFG`
      - 当前完整车资产的 `ArticulationCfg`。
      - 里面定义：
        - USD 路径
        - rigid/articulation 属性
        - joint 初始状态
        - `ball_joints` actuator
        - `wheel_joints` actuator

#### 1.6.8 传感器运行时模块

- `sensors/__init__.py`
  - 作用：
    - 对外导出 sensor runtime 相关类。
  - 本文件没有自定义类和函数。

- `sensors/sensor_runtime.py`
  - 作用：
    - 管理 imu、camera、lidar 以及可选 height scanner 的运行时实例。
    - 把原始传感器输出转成 policy 可以直接拼接的 feature。
  - 类：
    - `CompleteCarImuSensorCfg`
      - IMU 配置类。
      - 负责描述 IMU prim path、update period、gravity bias、是否进 policy。
    - `CompleteCarCameraSensorCfg`
      - Camera 配置类。
      - 负责描述相机分辨率、输出类型、光学参数、相对位姿、是否进 policy。
    - `CompleteCarLidarSensorCfg`
      - Lidar 配置类。
      - 负责描述 FOV、分辨率、量程、offset、policy pooling bin 数。
    - `CompleteCarSensorRuntimeCfg`
      - 传感器总配置。
      - 只是把 imu、camera、lidar 三组 cfg 聚合起来，并提供总 `policy_feature_dim`。
    - `CompleteCarSensorRuntime`
      - 传感器运行时管理器。
      - 负责在 scene 中真正创建传感器对象、reset 传感器、读取 raw output、提取 policy features。
  - 方法：
    - `CompleteCarImuSensorCfg.build_cfg()`
      - 构造 Isaac Lab `ImuCfg`。
    - `CompleteCarImuSensorCfg.policy_feature_dim`
      - 返回 IMU 为 policy 提供的特征维度。
    - `CompleteCarCameraSensorCfg.build_cfg()`
      - 构造 Isaac Lab `CameraCfg`。
    - `CompleteCarCameraSensorCfg.policy_feature_dim`
      - 根据输出类型估算 camera 最终进入 policy 的特征维度。
    - `CompleteCarLidarSensorCfg.build_cfg(ground_prim_path)`
      - 构造 Isaac Lab `RayCasterCfg`。
    - `CompleteCarLidarSensorCfg.policy_feature_dim`
      - 返回 lidar 进入 policy 的特征维度。
    - `CompleteCarSensorRuntimeCfg.policy_feature_dim`
      - 汇总 imu + camera + lidar 的 policy 特征总维度。
    - `CompleteCarSensorRuntime.build_scene_entities(scene)`
      - 按配置把 imu、camera、lidar、height scanner 创建出来并挂到 scene。
    - `CompleteCarSensorRuntime.reset(env_ids)`
      - reset 所有已经启用的传感器。
    - `CompleteCarSensorRuntime.get_height_features()`
      - 读取 height scanner 的 ray hit 结果并转换成相对高度特征。
    - `CompleteCarSensorRuntime.get_policy_features()`
      - 读取 imu、camera、lidar 数据，并提取出适合直接拼进 observation 的低维特征。
    - `CompleteCarSensorRuntime.get_raw_output()`
      - 返回当前缓存的原始传感器输出，方便 debug 或日志使用。

#### 1.6.9 Terrain 生成与运行时模块

- `terrain/__init__.py`
  - 作用：
    - 统一导出 terrain generator 和 terrain runtime 的关键符号。
  - 本文件没有自定义类和函数。

- `terrain/terrain_runtime.py`
  - 作用：
    - 管理 direct env 里 terrain 的运行时状态。
    - 包括：
      - 生成 terrain mesh
      - 管理 env origins
      - 管理 terrain level / type / class
      - terrain curriculum
      - 按 terrain class 调整 reset spawn offset
  - 类：
    - `CompleteCarTerrainRuntimeCfg`
      - terrain runtime 的配置类。
      - 规定 terrain 是否启用、模式是 plane 还是 generator、摩擦参数、height scanner 参数、curriculum 参数、spawn offset 参数，以及底层 `Stage1TerrainCfg`。
    - `CompleteCarTerrainRuntime`
      - terrain 运行时管理器。
      - 负责真正持有 terrain map、origin、curriculum 状态。
  - 函数：
    - `_offset_mesh_to_world_frame(terrain_cfg, terrain_mesh)`
      - 把生成出的 terrain mesh 从局部地图坐标平移到世界坐标。
    - `_sample_uniform(value_range, shape, device)`
      - terrain runtime 内部使用的均匀采样 helper。
  - 方法：
    - `CompleteCarTerrainRuntimeCfg.build_height_scanner_cfg(ground_prim_path)`
      - 构造 height scanner 的 `RayCasterCfg`。
    - `CompleteCarTerrainRuntime.generator_enabled`
      - 判断当前是否启用生成式 terrain。
    - `CompleteCarTerrainRuntime.setup_scene()`
      - 若启用 generator，则构造 terrain mesh 并创建 prim。
      - 同时缓存 terrain origins、terrain type map、terrain class map。
    - `CompleteCarTerrainRuntime.initialize_after_scene_clone(scene)`
      - 在 generator terrain 场景下初始化每个 env 的 level/type/class，并同步 env origins。
    - `CompleteCarTerrainRuntime.initialize_plane_after_scene_clone(scene)`
      - 在 plane 模式下初始化 terrain 相关状态。
    - `CompleteCarTerrainRuntime._build_initial_terrain_levels()`
      - 生成初始 terrain level 分配。
    - `CompleteCarTerrainRuntime._build_initial_terrain_types()`
      - 生成初始 terrain type 分配。
    - `CompleteCarTerrainRuntime.sync_env_origins(scene, env_ids=None)`
      - 把 terrain map 中当前 level/type 对应的 origin 同步回 scene。
    - `CompleteCarTerrainRuntime.update_curriculum(scene, robot, env_ids, commands, episode_length_s)`
      - 按当前 episode 末位移与 command 的关系，决定 terrain level 是升级还是降级。
    - `CompleteCarTerrainRuntime.apply_spawn_offsets(root_state, env_ids)`
      - 针对不同 terrain class，在 reset 时附加不同的 root spawn 偏移。

- `terrain/terrain_generator.py`
  - 作用：
    - 负责 Stage1 terrain 的离线生成逻辑。
    - 它回答的是：
      - 地图怎么铺
      - 每个 tile 是什么地形
      - 每个 tile 对应哪个 terrain class
      - origin 放在哪里
      - heightfield 怎么转 mesh
  - 类：
    - `Stage1TerrainCfg`
      - Stage1 地形生成参数总配置。
      - 规定地图行列数、tile 尺寸、边界、比例尺、地形类型分布、roughness、障碍参数等。
    - `Stage1TerrainData`
      - terrain 生成结果的数据容器。
      - 保存：
        - heightfield
        - env_origins
        - terrain_type
        - terrain_class
        - vertices
        - faces
    - `_SubTerrain`
      - 单个 tile 的临时高程图容器。
  - 函数：
    - `create_empty_stage1_terrain_data(cfg=None)`
      - 创建空的 terrain 数据容器。
    - `_tile_seed(cfg, row, col, terrain_idx)`
      - 为单个 tile 生成稳定随机种子。
    - `_make_subterrain(cfg)`
      - 根据 cfg 创建单 tile 尺寸的 `_SubTerrain`。
    - `get_terrain_class_from_name(terrain_name)`
      - 把 terrain 名称映射成更粗粒度的 terrain class。
    - `_random_uniform_terrain(...)`
      - 生成随机 rough 高程。
    - `_pyramid_sloped_terrain(...)`
      - 生成金字塔坡地。
    - `_pyramid_stairs_terrain(...)`
      - 生成金字塔楼梯地形。
    - `_discrete_obstacles_terrain(...)`
      - 生成离散障碍块地形。
    - `_parkour_step_terrain(...)`
      - 生成台阶/step 类障碍。
    - `_parkour_step_gap_terrain(...)`
      - 生成带 gap 的台阶地形。
    - `_half_sloped_terrain(...)`
      - 生成半边斜坡地形。
    - `_stepping_beams_terrain(...)`
      - 生成窄梁/beam 地形。
    - `_pit_terrain(...)`
      - 生成坑洞地形。
    - `_maybe_add_roughness(...)`
      - 按 cfg 决定是否给 tile 叠加 roughness。
    - `make_flat_tile(cfg)`
      - 生成平地 tile。
    - `make_slope_tile(cfg, difficulty, descending=False)`
      - 生成坡地 tile。
    - `make_slope_down_tile(cfg, difficulty)`
      - 生成下坡 tile。
    - `make_slope_up_tile(cfg, difficulty)`
      - 生成上坡 tile。
    - `make_pyramid_tile(cfg, difficulty, seed)`
      - 生成金字塔坡/台地 tile。
    - `make_stairs_tile(...)`
      - 生成楼梯 tile。
    - `make_discrete_obstacles_tile(cfg, difficulty, seed)`
      - 生成离散障碍 tile。
    - `make_hurdle_tile(cfg, difficulty, seed)`
      - 生成 hurdle/step 类 tile。
    - `make_gap_tile(cfg, difficulty, seed)`
      - 生成沟壑/gap tile。
    - `make_ramp_tile(cfg, difficulty, seed)`
      - 生成斜坡+平台类 tile。
    - `make_beam_tile(cfg, difficulty, seed)`
      - 生成窄梁 tile。
    - `make_new_stairs_down_tile(cfg, difficulty)`
      - 生成新的下楼梯 tile 版本。
    - `make_pit_tile(cfg, difficulty)`
      - 生成坑洞 tile。
    - `get_terrain_idx_from_choice(cfg, choice)`
      - 根据采样 choice 把 tile 分配到某个 terrain index。
    - `get_terrain_name_from_idx(cfg, terrain_idx)`
      - 根据 terrain index 返回 terrain name。
    - `make_tile_by_name(cfg, terrain_name, difficulty, choice, seed)`
      - 按 terrain name 构建 tile。
    - `make_tile_by_col(cfg, row, col)`
      - 按地图列索引规则生成当前 tile，并返回 tile 和 terrain_idx。
    - `get_origin_patch_center(cfg, terrain_name)`
      - 给某类 tile 选 reset origin patch 的中心区域。
    - `get_origin_patch_radius(cfg, terrain_name)`
      - 给某类 tile 选 reset origin patch 的半径/范围。
    - `write_tile_to_map(data, tile, row, col, terrain_idx, cfg)`
      - 把单 tile 写入整张 heightfield 大图。
    - `set_tile_origin(data, row, col, terrain_name, cfg)`
      - 计算并写入当前 tile 对应的 env origin。
    - `set_tile_class(data, row, col, terrain_name)`
      - 写入当前 tile 的 terrain class。
    - `build_stage1_map(cfg=None)`
      - 生成完整的 Stage1 heightfield map、terrain_type、terrain_class、env_origins。
    - `convert_heightfield_to_trimesh(...)`
      - 把 heightfield 转成三角网格顶点和面片。
    - `convert_heightfield_to_mesh(data, cfg)`
      - 把 `Stage1TerrainData` 中的 heightfield 转成 mesh 数据。
    - `build_stage1_terrain_data(cfg=None)`
      - Stage1 地形生成总入口。
      - 先建 map，再转 mesh，最后返回完整的 `Stage1TerrainData`。

#### 1.6.10 Agent 配置模块

- `agents/__init__.py`
  - 作用：
    - 对外导出当前 direct task 使用的 PPO cfg。
  - 本文件没有自定义类和函数。

- `agents/local_rsl_rl_cfg.py`
  - 作用：
    - 放项目本地化的 RSL-RL 配置类定义。
    - 它们本身不是训练逻辑，只是给本地 vendored `rsl_rl` 提供结构化 config。
  - 类：
    - `LocalGaussianDistributionCfg`
      - 高斯策略分布配置。
    - `LocalMlpModelCfg`
      - MLP actor/critic 网络配置。
    - `LocalPpoAlgorithmCfg`
      - PPO 算法超参数配置。
    - `LocalOnPolicyRunnerCfg`
      - on-policy runner 顶层配置。
      - 里面统一挂 `actor / critic / algorithm / logging / resume` 等字段。
  - 本文件没有额外函数。

- `agents/ppo_cfg.py`
  - 作用：
    - 定义 complete-car 当前 direct 任务真正使用的 PPO runner 配置。
  - 类：
    - `CompleteCarPPoCfg(LocalOnPolicyRunnerCfg)`
      - complete-car 任务族共享的 PPO 顶层配置。
      - 里面定义：
        - 全局 seed
        - `num_steps_per_env`
        - `max_iterations`
        - `save_interval`
        - `experiment_name`
        - `obs_groups`
        - `resume/load_run/load_checkpoint`
        - actor 网络
        - critic 网络
        - PPO algorithm 超参数
    - `Stage0FlatPPoCfg(CompleteCarPPoCfg)`
      - Stage0 的 PPO 配置，只覆写 `experiment_name`。
    - `Stage1TerrainPPoCfg(CompleteCarPPoCfg)`
      - Stage1 的 PPO 配置，只覆写 `experiment_name`。
    - `Stage2PerceptionPPoCfg(CompleteCarPPoCfg)`
      - Stage2 的 PPO 配置，只覆写 `experiment_name`。

#### 1.6.11 如何阅读当前 `complete_car/` 主线

如果你现在要真正理解当前 direct 任务，而不是回看旧模板，建议按这个顺序读：

1. `__init__.py`
   - 先确认 task id、env cfg、ppo cfg 的绑定关系。
2. `complete_car_env_cfg.py`
   - 先弄清楚 command、action、observation、reward、reset、terrain、sensor 的配置语义。
3. `complete_car_env.py`
   - 再看 step/reset 主循环到底怎么把这些 cfg 用起来。
4. `commands.py`、`observations.py`、`rewards.py`、`terminations.py`
   - 最后再分别拆开看 command、obs、reward、done 的具体计算。
5. `terrain/`、`sensors/`
   - 如果问题和 terrain curriculum、传感器特征有关，再深入 runtime helper。
6. `agents/ppo_cfg.py`
   - 最后看训练超参数，而不是一开始就盯 PPO。

这样读的原因是：

- 先看 `__init__.py`
  - 才知道当前到底注册了哪些 task
- 先看 `complete_car_env_cfg.py`
  - 才知道 env 的语义约定是什么
- 再看 `complete_car_env.py`
  - 才能看懂这些配置如何进入 step/reset 闭环
- 最后看各 helper
  - 才不会在局部函数里迷路

---

## 二、MGDP 项目结构梳理

### 2.1 整体架构

MGDP 项目可以分成 6 层：

1. `envs/base`
   - 环境骨架层
2. `envs/baseline`
   - 可复用功能模块层
3. `envs/random_dog`
   - 具体任务层
4. `utils`
   - 配置、参数解析、注册、日志、地形工具层
5. `rl/MGDP`
   - 自定义算法层
6. `scripts`
   - 外层启动与可视化层

和 Isaac Lab 最大不同在于：

- MGDP 把很多逻辑写在一个自定义环境体系里
- 自己实现 task registry、runner、PPO、actor-critic、rollout storage
- 环境通过多继承把 terrain/reward/camera 模块拼起来

其核心运行链大致是：

```text
legged_gym/scripts/train.py
    -> legged_gym/legged_gym/scripts/train.py
    -> task_registry.make_env(...)
    -> task_registry.make_alg_runner(...)
    -> envs/__init__.py 中注册的 random_dog_stage1 / random_dog_stage2
    -> Randomdog(CameraMixin, Legged_terrains, Legged_camera, Legged_rewards, LeggedRobot)
    -> rl/MGDP/runners/policy_runner.py
    -> rl/MGDP/algorithms/ppo.py
```

### 2.2 目录结构总览

```text
legged_gym/
├── scripts/
│   ├── train.py
│   ├── resume.py
│   ├── vis_stage1.py
│   ├── vis_stage2.py
│   └── play_terrain.py
├── legged_gym/
│   ├── envs/
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── base_config.py
│   │   │   ├── base_task.py
│   │   │   ├── legged_robot.py
│   │   │   └── legged_robot_config.py
│   │   ├── baseline/
│   │   │   ├── legged_robot_config_baseline.py
│   │   │   ├── legged_robot_terrains.py
│   │   │   ├── legged_robot_rewards.py
│   │   │   └── legged_robot_camera.py
│   │   └── random_dog/
│   │       ├── random_dog.py
│   │       ├── random_dog_config_stage1.py
│   │       └── random_dog_config_stage2.py
│   ├── scripts/
│   │   ├── train.py
│   │   ├── play.py
│   │   ├── play_stage1.py
│   │   ├── play_stage2.py
│   │   ├── play_random_dog.py
│   │   ├── play_joy_45_gap.py
│   │   └── simple_env.py
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py
│       ├── logger.py
│       ├── math.py
│       ├── task_registry.py
│       └── terrain.py
└── rl/MGDP/
    ├── algorithms/ppo.py
    ├── modules/
    │   ├── Network.py
    │   ├── actor_critic.py
    │   └── actor_critic_recurrent_lstm.py
    ├── runners/policy_runner.py
    └── storage/rollout_storage.py
```

### 2.3 MGDP 的层次关系

#### A. `envs/base`

这一层是通用骨架，不关心任务名，也不关心 Stage1 还是 Stage2。

- `base_config.py`
  - 递归初始化配置类的基类工具。
- `base_task.py`
  - 创建 sim、viewer、基础 tensor buffer。
  - 是最底层任务壳子。
- `legged_robot_config.py`
  - 定义通用环境配置槽位：
    - env
    - terrain
    - commands
    - init_state
    - control
    - asset
    - domain_rand
    - rewards
- `legged_robot.py`
  - 负责环境主循环：
    - `step`
    - `post_physics_step`
    - `reset_idx`
    - `compute_reward`
    - `compute_observations`
    - `_create_envs`

这一层回答的是：

- Isaac Gym 仿真怎么跑
- observation/reward/reset 的主循环在哪里

#### B. `envs/baseline`

这一层不是单独任务，而是给具体任务复用的“功能模块”。

- `legged_robot_config_baseline.py`
  - 在 base config 上给出更适合四足 locomotion 的默认配置。
- `legged_robot_terrains.py`
  - 负责 terrain curriculum、height sampling、部分 history/privileged obs、terrain 相关 reset。
- `legged_robot_rewards.py`
  - 提供扩展 reward 项。
- `legged_robot_camera.py`
  - 提供相机、深度图读取、图像预处理能力。

这一层回答的是：

- 地形如何接入
- 奖励如何扩展
- 相机如何接入

#### C. `envs/random_dog`

这一层是具体任务层。

- `random_dog.py`
  - 任务主环境类 `Randomdog`。
  - 通过多继承把：
    - `Legged_terrains`
    - `Legged_camera`
    - `Legged_rewards`
    - `LeggedRobot`
    拼装到一起。
  - 它会覆盖/扩展：
    - `compute_observations`
    - `step`
    - `reset_idx`
    - `_reset_root_states`
- `random_dog_config_stage1.py`
  - Stage1 配置：
    - terrain mix
    - command ranges
    - init state
    - camera/world model
    - domain randomization
    - rewards
    - PPO/encoder 配置
- `random_dog_config_stage2.py`
  - Stage2 配置。
  - 通常基于 Stage1 再改更难地形、恢复策略、加载 world model 等。

这一层回答的是：

- 这次训练到底训练什么任务
- Stage1 和 Stage2 有什么区别

### 2.4 MGDP 的工具与算法层

#### A. `utils`

- `utils/__init__.py`
  - 汇总导出 `helpers`、`task_registry`、`Logger`、`Terrain` 等工具。
- `helpers.py`
  - 配置转字典
  - seed 设置
  - sim 参数解析
  - 命令行参数解析
  - JIT 导出
  - 从 CLI 更新配置
- `logger.py`
  - 训练/回放时的状态记录、奖励打印、绘图工具。
- `math.py`
  - 姿态、角度、随机采样等数学辅助函数。
- `task_registry.py`
  - MGDP 版任务注册器。
  - 负责：
    - 注册 task
    - 创建 env
    - 创建算法 runner
    - resume 加载
    - 训练日志目录管理
    - 备份关键配置脚本
- `terrain.py`
  - 高程图 terrain 生成与 mesh 转换。
  - 包括 `env_origins`、terrain type、heightfield -> trimesh 等逻辑。

#### B. `rl/MGDP`

- `algorithms/ppo.py`
  - 自定义 PPO 更新逻辑。
  - 不是直接用现成库，而是自己实现。
- `modules/Network.py`
  - 编码器/网络模块基础组件。
- `modules/actor_critic.py`
  - 自定义 actor-critic。
  - 会把 `obs + privileged_info + proprio_hist + image_buf` 拼到一起。
- `modules/actor_critic_recurrent_lstm.py`
  - 带 recurrent/memory 的 actor-critic 版本。
- `runners/policy_runner.py`
  - 自定义训练 runner。
  - 负责 rollout、更新、日志、checkpoint、world model 保存。
- `storage/rollout_storage.py`
  - 存 rollout transition，给 PPO update 使用。

这一层回答的是：

- 策略网络怎么定义
- PPO 怎么更新
- rollout 怎么存
- checkpoint 怎么保存

### 2.5 MGDP 中各脚本的职责分析

#### 2.5.1 外层启动脚本：`legged_gym/scripts/`

这些脚本大多是“薄封装”，负责预设参数并调用内层逻辑。

- `scripts/train.py`
  - 启动 Stage1 训练。
  - 预设 `args.task = random_dog_stage1`、设备、seed、输出目录。
- `scripts/resume.py`
  - 从 Stage1 模型恢复，并启动 Stage2 训练。
  - 预设 `args.task = random_dog_stage2`、`resume=True`、checkpoint 路径、world model 路径。
- `scripts/vis_stage1.py`
  - 启动 Stage1 模型的可视化回放。
  - 实际调用内层 `play_stage1.py`。
- `scripts/vis_stage2.py`
  - 启动 Stage2 模型的可视化回放。
  - 实际调用内层 `play_stage2.py`。
- `scripts/play_terrain.py`
  - 只把环境跑起来看地形，不依赖训练策略。
  - 实际调用内层 `simple_env.py`。

#### 2.5.2 内层执行脚本：`legged_gym/legged_gym/scripts/`

这些脚本包含真正的训练/回放逻辑。

- `legged_gym/scripts/train.py`
  - 通用训练入口。
  - 调 `task_registry.make_env()` 和 `task_registry.make_alg_runner()` 后进入学习。
- `legged_gym/scripts/play.py`
  - 通用回放入口。
  - 创建环境、加载 policy、跑推理、记录状态。
- `legged_gym/scripts/play_stage1.py`
  - Stage1 专用回放脚本。
  - 会改 eval 用地形参数、命令范围、world model 加载选项。
- `legged_gym/scripts/play_stage2.py`
  - Stage2 专用回放脚本。
  - 功能与 `play_stage1.py` 类似，但针对 Stage2 配置。
- `legged_gym/scripts/play_random_dog.py`
  - 另一个 random_dog 可视化回放脚本。
  - 和 `play.py/play_stage*.py` 类似，偏实验/调试用途。
- `legged_gym/scripts/play_joy_45_gap.py`
  - ROS 手柄交互回放脚本。
  - 订阅 `/joy`，动态改 command，并把观测发布到 ROS 话题。
  - 用于手柄联调与在线观测。
- `legged_gym/scripts/simple_env.py`
  - 不加载 policy，只给零动作，让环境裸跑。
  - 用于检查 terrain、reset、仿真是否正常。

#### 2.5.3 环境脚本：`envs/`

- `envs/__init__.py`
  - 注册 `random_dog_stage1` 和 `random_dog_stage2` 到 `task_registry`。
- `envs/base/base_config.py`
  - 配置基类工具。
- `envs/base/base_task.py`
  - 仿真与 viewer 最底层壳子。
- `envs/base/legged_robot_config.py`
  - 通用配置模板。
- `envs/base/legged_robot.py`
  - 环境主循环骨架。
- `envs/baseline/legged_robot_config_baseline.py`
  - baseline 默认配置。
- `envs/baseline/legged_robot_terrains.py`
  - 地形模块与 terrain curriculum。
- `envs/baseline/legged_robot_rewards.py`
  - 扩展奖励库。
- `envs/baseline/legged_robot_camera.py`
  - 深度相机与图像处理模块。
- `envs/random_dog/random_dog.py`
  - 具体任务环境实现。
- `envs/random_dog/random_dog_config_stage1.py`
  - Stage1 任务与 PPO 配置。
- `envs/random_dog/random_dog_config_stage2.py`
  - Stage2 任务与 PPO 配置。

#### 2.5.4 工具脚本：`utils/`

- `utils/__init__.py`
  - 工具模块统一出口。
- `utils/helpers.py`
  - 参数解析、配置更新、JIT 导出等杂项工具。
- `utils/logger.py`
  - 状态与奖励日志工具。
- `utils/math.py`
  - 数学辅助函数。
- `utils/task_registry.py`
  - 自定义任务注册与 runner 构造器。
- `utils/terrain.py`
  - terrain 生成和 mesh 转换工具。

#### 2.5.5 算法脚本：`rl/MGDP/`

- `algorithms/ppo.py`
  - PPO 训练算法实现。
- `modules/Network.py`
  - 编码器基础网络模块。
- `modules/actor_critic.py`
  - 非 recurrent actor-critic。
- `modules/actor_critic_recurrent_lstm.py`
  - recurrent actor-critic。
- `runners/policy_runner.py`
  - 训练主循环和 checkpoint 管理。
- `storage/rollout_storage.py`
  - rollout 缓存。

### 2.6 MGDP 的理解方式

如果只记核心主线，可以记为：

- `scripts/train.py`
  - 外层启动
- `utils/task_registry.py`
  - 负责把任务和算法接起来
- `envs/random_dog/random_dog.py`
  - 具体任务环境
- `envs/random_dog/random_dog_config_stage1.py`
  - 具体任务配置
- `rl/MGDP/runners/policy_runner.py`
  - 训练主循环
- `rl/MGDP/algorithms/ppo.py`
  - PPO 更新

也就是说，MGDP 的设计思想是：

- 环境逻辑更多集中在自定义 env 类内部
- 地形/奖励/相机通过多继承拼装
- 算法栈自己实现，不依赖外部 RL 框架

---

## 三、Isaac Lab 模板和 MGDP 的结构差异总结

两者最大的差别不在“有没有 train.py”，而在“职责切分方式”：

- Isaac Lab
  - 倾向配置驱动
  - 环境语义拆到 `env_cfg`
  - 算法运行依赖现成 `RSL-RL`
  - 注册依赖 Gym + Hydra entry point
- MGDP
  - 倾向自定义环境驱动
  - 逻辑集中在 `Randomdog + mixin`
  - 算法栈自定义
  - 注册依赖自写 `task_registry`

如果后续要做迁移，正确思路通常不是“照抄脚本”，而是：

1. 先对齐任务语义
   - observation
   - action
   - reward
   - reset
   - terrain curriculum
2. 再决定哪些部分保留 Isaac Lab 模板写法
3. 只迁 MGDP 中真正必要的项目逻辑，而不是把整套自定义 PPO 和脚本布局硬搬过来



```Text
complete_car_rl_training/
├── README.md
├── pyproject.toml
├── scripts/
│   ├── train.py
│   └── play.py
└── source/
    └── complete_car_lab/
        ├── config/
        │   └── extension.toml
        ├── setup.py
        └── complete_car_lab/
            ├── __init__.py
            └── tasks/
                └── direct/
                    └── complete_car/
                        ├── __init__.py
                        ├── base/
                        │   ├── env.py
                        │   └── complete_car_cfg.py
                        ├── baseline/
                        │   ├── complete_car_stage0_cfg.py
                        │   └── complete_car_stage1_cfg.py
                        ├── environment_adaptive/
                        │   └── complete_car_stage2_cfg.py
                        ├── assets/
                        │   ├── __init__.py
                        │   ├── robot_cfg.py
                        │   └── actuators_cfg.py
                        ├── mdp/
                        │   ├── __init__.py
                        │   ├── commands.py
                        │   ├── actions.py
                        │   ├── observations.py
                        │   ├── rewards.py
                        │   ├── terminations.py
                        │   ├── resets.py
                        │   └── randomization.py
                        ├── terrain/
                        │   ├── __init__.py
                        │   ├── terrain_cfg.py
                        │   ├── terrain_builder.py
                        │   └── terrain_runtime.py
                        ├── sensors/
                        │   ├── __init__.py
                        │   ├── sensor_cfg.py
                        │   ├── imu.py
                        │   ├── lidar.py
                        │   └── stereo_camera.py
                        ├── kinematics/
                        │   ├── __init__.py
                        │   ├── fk_solver.py
                        │   ├── wheel_speed_allocator.py
                        │   └── ik_solver.py
                        ├── utils/
                        │   ├── __init__.py
                        │   ├── math_utils.py
                        │   ├── debug_draw.py
                        │   └── io_descriptors.py
                        └── agents/
                            ├── __init__.py
                            └── rsl_rl_ppo_cfg.py
```
注册任务名称：
CompleteCar-Stage0
CompleteCar-Stage1
CompleteCar-Stage2
