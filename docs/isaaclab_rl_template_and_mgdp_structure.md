# Isaac Lab RL模板与MGDP项目结构梳理

本文档分两部分：

1. 以 `Graduation-Project` 为例，梳理 Isaac Lab 风格 RL 项目的模板结构、任务注册链路、环境构造链路，以及各脚本职责。
2. 梳理 `MGDP` 项目的结构，说明各目录、各脚本分别负责什么。

文档组织方式统一为：

- 先给整体架构
- 再给运行调用链
- 最后逐个脚本/文件解释职责

---

## 一、Isaac Lab RL模板梳理：以 Graduation-Project 为例

### 1.1 整体架构

当前主线 RL 工作区位于：

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
- `docs/rl_training_route.md`
  - 训练策略路线文档。
  - 它不是程序入口，而是研究/工程路线说明，定义当前阶段优先级。
- `docs/tensorboard_reading_guide.md`
  - TensorBoard 标量的离线阅读与诊断说明。
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
