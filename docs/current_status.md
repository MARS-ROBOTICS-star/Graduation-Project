# 当前状态

## 当前总目标
- 在 Isaac Lab 中维持一条可复现、可继续迭代的完整车 RL 主线。
- 当前代码主线已经按用户要求彻底切到 Isaac Lab direct workflow，后续不再沿用 manager-based 架构。

## 当前阶段
- 阶段 0 的 flat baseline 仍是后续真实运行时的最短冒烟入口。
- 本轮已完成 direct 架构重构与一轮结构性迁移，当前进入“动作/观测/命令语义已切换，等待真实 Isaac Lab 环境做运行态验证”的阶段。

## 当前 RL 主线位置
- 当前唯一活跃的 Isaac Lab RL 工作区已经从旧的 `src/rl_lab/complete_car_rl_training/` 迁到：
  - `RL_Training/`
- 当前 Python 包入口：
  - `RL_Training/complete_car_rl_training/__init__.py`
- 当前训练脚本入口：
  - `RL_Training/scripts/rsl_rl/train.py`
  - `RL_Training/scripts/rsl_rl/play.py`
  - `RL_Training/scripts/list_envs.py`

## 当前代码结构
- 当前 direct task 主目录：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/`
- 当前 terrain runtime：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terrain/`
- 当前 sensor runtime：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/sensors/`
- Isaac Sim 预览和键盘控制脚本仍保留在仓库根目录：
  - `scripts/isaac_sim/`

## 本轮已确认
- RL 主线已经从 manager-based 彻底切换到 Isaac Lab direct workflow。
- 本地旧的 `src/rl_lab/complete_car_rl_training/` 残留目录已清理，不再作为任何默认入口保留在工作树中。
- 已新增长期查阅用的 direct workflow 架构说明文档：
  - `docs/complete_car_direct_workflow_architecture.md`
- 当前 direct 任务注册入口：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/__init__.py`
- 当前 direct env 主类：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
- 当前 direct 共享配置主干：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- 当前分阶段配置：
  - `stage0_flat_cfg.py`
  - `stage1_terrain_cfg.py`
  - `stage2_perception_cfg.py`
- 当前 direct Gym task id 已改为：
  - `Complete-Car-Stage0-Flat-Direct-v0`
  - `Complete-Car-Stage1-Terrain-Direct-v0`
  - `Complete-Car-Stage2-Perception-Direct-v0`
- 旧的：
  - `envs/base/complete_car_config.py`
  - `envs/base/manager_helpers.py`
  - `envs/base/complete_car_env.py`
  - `envs/baseline/complete_car_config_baseline.py`
  - `utils/terrain.py`
  已从当前主线删除，不应再作为默认入口。
- terrain 逻辑现已拆为：
  - `terrain/terrain_generator.py`
  - `terrain/terrain_runtime.py`
- sensor 逻辑现已拆为：
  - `sensors/sensor_runtime.py`
- 根目录 Isaac Sim 预览和键盘脚本已改为读取新的：
  - `tasks/direct/complete_car/assets/robot_cfg.py`
  - `tasks/direct/complete_car/terrain/terrain_generator.py`
- `complete_car.usd` 的 articulation root 已调整到：
  - `/World/complete_car_alternative/body_car_chassis`
- 当前 direct 资产配置已通过 `ArticulationCfg.articulation_root_prim_path = "/body_car_chassis"` 显式对齐这个新 root。
- direct 主线的 command / observation / action 已完成一轮结构性迁移：
  - command 改为 4 维：
    - `lin_vel_x`
    - `lin_vel_y`
    - `ang_vel_yaw`
    - `heading`
  - policy action 改为 6 维，仅保留 6 个球铰姿态关节目标角
  - 车轮不再由 policy 直接输出轮速，改为在 env 内按 command 派生左右轮速度目标
  - policy observation 的核心本体输入改为：
    - `roll, pitch, yaw`
    - `roll_rate, pitch_rate, yaw_rate`
    - `ball_joint_pos(6)`
    - `ball_joint_vel(6)`
    - `commands(4)`
    - `last_action(6)`
  - 当前基础 proprioceptive observation 维度为：
    - `28`
  - Stage2 若开启 `imu / camera / lidar`，当前会在上述 28 维基础上追加传感器特征
- PPO 配置已不再直接继承 Isaac Lab 的旧 `RslRlOnPolicyRunnerCfg / RslRlPpoActorCriticCfg / RslRlPpoAlgorithmCfg` 模板类：
  - 当前项目本地副本位于：
    - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents/local_rsl_rl_cfg.py`
  - 当前 `ppo_cfg.py` 已切到本地 `actor / critic / distribution_cfg` 结构
- 速度跟踪 reward 的核心 tracking kernel 已下沉到项目本地文件：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/local_velocity_tracking_reward.py`
- 论文章节：
  - `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
  已完成一次面向编译恢复的格式清理，移除了损坏的伪 Markdown / 伪公式标记，并统一改回合法 LaTeX 写法。
- `chapter03.tex` 中“前后模块线速度推导”小节已进一步按“先引入惯性坐标系 ${W}$，再从绝对位置求导推出牵连速度项”的逻辑重写。
- 当前前、后模块线速度表达式不再直接给出，而是通过：
  - 绝对位置关系
  - 乘积求导
  - 旋转坐标系中的速度变换
  顺序推出：
  - `${}^{2}\mathbf v_1={}^2\mathbf v_2+{}^2\boldsymbol\omega_2\times{}^2\mathbf p_1+{}^2\dot{\mathbf p}_1`
  - `${}^{2}\mathbf v_3={}^2\mathbf v_2+{}^2\boldsymbol\omega_2\times{}^2\mathbf p_3+{}^2\dot{\mathbf p}_3`
- 论文主入口：
  - `毕业论文/毕业论文模板/LaTeX/main.tex`
  当前已可重新通过 `latexmk -xelatex` 完整生成 `main.pdf`。

## 当前默认设计选择
- 当前默认 runnable 起点：
  - `Complete-Car-Stage0-Flat-Direct-v0`
- 当前默认动作语义：
  - policy 只输出 6 个球铰位置目标
  - 车轮轮速由 env 按 command 自动派生，不再属于 policy action 维度
- 当前默认 command 语义：
  - `lin_vel_x / lin_vel_y / ang_vel_yaw / heading`
- 当前默认 observation 语义：
  - 基础 28 维本体观测以姿态角和姿态角变化率为主
  - Stage2 才在这套基础 observation 上追加 `camera / lidar / imu`
- `train.py / play.py` 已完成 direct 主线收口，不再保留 manager-based 或 MARL 模板类型联合。
- direct 主线的动作噪声与观测噪声已收口到 Isaac Lab 基类 `action_noise_model / observation_noise_model`，不再由本地 env / observation helper 手写注入。
- 当前与资产根节点相关的直接脚本默认使用新的 articulation root：
  - `scripts/isaac_sim/control_keyboard.py`
  - `scripts/isaac_sim/rover_control.py`
- direct 组织原则已经固定：
  - env 主类直接负责 reset / observation / reward / done / command / terrain runtime / sensor runtime
  - 纯函数 helper 单独放在 `rewards.py / observations.py / commands.py / terminations.py`
  - terrain 和 sensor 保持 runtime helper，不回退成 manager term

## 当前阻塞 / 风险
- 当前电脑没有 Isaac Lab 运行环境，因此本轮只能完成代码级重构与静态语法检查，不能做真实环境注册和仿真冒烟。
- 新 direct 架构尚未在真实 Isaac Lab 环境中执行：
  - `list_envs.py`
  - `train.py`
  - `play.py`
- 新 6 维 policy action 方案下，车轮驱动已经改为 env 内的 command 派生控制；这部分仍需在真实 Isaac Lab 中验证：
  - 平地前进是否正常
  - 左右轮差速带来的 yaw 控制是否稳定
  - 速度跟踪 reward 是否与新的 wheel-drive 映射一致
- `docs/conversation_history.md` 中仍保留大量旧 `src/rl_lab/...` 路径，它们属于历史记录，不代表当前主线位置。
- 论文编译当前仍保留 2 条非阻塞参考文献警告：
  - `fang2015survey`
  - `MATSUMURA2017566`
  它们在 `reference/ref.bib` 中缺失，但不影响 `main.pdf` 生成。

## 下一步优先级
- 在有 Isaac Lab 环境的机器上，从 `/home/ubuntu/Graduation-Project/RL_Training` 目录优先执行一轮：
  - `python scripts/list_envs.py --keyword Complete-Car`
  - `python scripts/rsl_rl/train.py --task Complete-Car-Stage0-Flat-Direct-v0 --headless --num_envs 100 --max_iterations 10`
- Stage0 冒烟时重点先核对：
  - 6 维 action space 是否正确注册
  - observation 维度是否为 `28`
  - 车轮 command 派生驱动后机器人是否能正常前进
- 如果 Stage0 direct 冒烟正常，再继续：
  - `Complete-Car-Stage1-Terrain-Direct-v0`
  - `Complete-Car-Stage2-Perception-Direct-v0`
