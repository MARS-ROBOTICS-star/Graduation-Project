# 当前状态

## 当前总目标
- 将完整车 RL 主线收口到 `RL_Training/` 下的新 Isaac Lab direct workflow 架构。
- 让训练入口、任务注册、共享环境主类、共享配置主干、Stage0/1/2 分阶段配置在同一套新结构下统一工作。

## 当前阶段
- 已完成 `RL_Training/` 原地重构。
- 已按用户要求把旧 `IK/FK`、本地 `rsl_rl` 本体、旧辅助脚本重新迁入新架构内部。
- 当前进入“等待真实 Isaac Lab 环境做运行态冒烟验证”的阶段。

## 当前 RL 主线位置
- 当前活跃 RL 工作区：
  - `RL_Training/`
- 当前 Python 扩展包入口：
  - `RL_Training/source/complete_car_lab/complete_car_lab/__init__.py`
- 当前 direct task 注册入口：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/__init__.py`
- 当前训练 / 回放脚本：
  - `RL_Training/scripts/train.py`
  - `RL_Training/scripts/play.py`

## 当前代码结构
- 共享 direct 环境主类：
  - `base/env.py`
- 共享基础配置主干：
  - `base/complete_car_cfg.py`
- 分阶段配置：
  - `baseline/complete_car_stage0_cfg.py`
  - `baseline/complete_car_stage1_cfg.py`
  - `environment_adaptive/complete_car_stage2_cfg.py`
  - terrain / sensor 的阶段差异已下放到各 stage cfg 内部显式定义，不再由 base cfg 自动绑定
- MDP 拆分：
  - `mdp/commands.py`
  - `mdp/actions.py`
  - `mdp/observations.py`
  - `mdp/rewards.py`
  - `mdp/terminations.py`
  - `mdp/resets.py`
  - `mdp/randomization.py`
- terrain 拆分：
  - `terrain/terrain_cfg.py`
  - `terrain/terrain_builder.py`
  - `terrain/terrain_runtime.py`
- sensors 拆分：
  - `sensors/sensor_cfg.py`
  - `sensors/imu.py`
  - `sensors/lidar.py`
  - `sensors/stereo_camera.py`
- kinematics 拆分：
  - `kinematics/fk_solver.py`
  - `kinematics/ik_solver.py`
  - `kinematics/wheel_speed_allocator.py`
- kinematics 保留的旧资料：
  - `kinematics/legacy_fk/`
  - `kinematics/legacy_ik/`
- 本地 PPO 本体：
  - `rsl_rl/`
- 本地辅助脚本：
  - `utils/list_envs.py`
  - `utils/random_agent.py`
  - `utils/zero_agent.py`
  - `utils/export_training_stage.py`
  - `utils/tensorboard_export.py`
  - `utils/validate_wheel_speed_allocator.py`

## 本轮已确认
- `RL_Training/` 已不再保留旧的：
  - `complete_car_rl_training/`
  - `config/`
  - `docs/`
  - `kinematics/`
  - `scripts/rsl_rl/`
  - `setup.py`
  - `skills/`
- 当前 `RL_Training/` 根目录已经收口为：
  - `README.md`
  - `pyproject.toml`
  - `scripts/train.py`
  - `scripts/play.py`
  - `source/complete_car_lab/...`
- 旧 `RL_Training/rsl_rl/` 的 PPO 实现已迁到：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/`
- 旧 `RL_Training/scripts/` 下除 `train.py` / `play.py` 以外的辅助脚本已迁到：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/`
- 旧 `RL_Training/utils/` 下的 IK/FK 已迁到：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/`
  其中：
  - `IK_model.py` 的求解逻辑已经并入 `ik_solver.py`
  - 旧推导资料保留在 `legacy_ik/` 和 `legacy_fk/`
- 3 个 Gym task id 已统一改为：
  - `CompleteCar-Stage0`
  - `CompleteCar-Stage1`
  - `CompleteCar-Stage2`
- 3 个任务统一指向：
  - `base/env.py` 中的 `CompleteCarDirectEnv`
- `base/complete_car_cfg.py` 已按独立配置块实现：
  - `CommandRangesCfg`
  - `CommandCfg`
  - `ControlCfg`
  - `ObservationScalesCfg`
  - `ObservationNoiseCfg`
  - `ObservationCfg`
  - `RewardScalesCfg`
  - `RewardCfg`
  - `TerminationCfg`
  - `ResetCfg`
  - `RandomizationCfg`
  - `TerrainBindingCfg`
  - `SensorBindingCfg`
  - `DebugCfg`
  - `SceneCfg`
  - `CompleteCarEnvCfg`
- 当前 `RL_Training/` 下全部 Python 文件已通过：
  - `python3 -m py_compile $(find RL_Training -name '*.py' | sort)`
- 最近已补充 `base/complete_car_cfg.py` 中 `CommandCfg` 与 `ControlCfg` 的中文工程注释，便于后续阅读配置语义与单位。

## 当前默认设计选择
- 当前默认 runnable 起点：
  - `CompleteCar-Stage0`
- 当前默认动作语义：
  - policy 输出 6 维球铰目标
  - 车轮轮速由 env 内部依据 command 和 wheel allocator 自动生成
- 当前默认命令语义：
  - `lin_vel_x / lin_vel_y / ang_vel_yaw / heading`
- 当前默认观测语义：
  - base 线速度 + base 角速度 + 重力投影 + 球铰位置/速度 + commands + last_action
  - Stage2 在此基础上追加 `imu / stereo_camera / lidar` 特征

## 当前阻塞 / 风险
- 当前机器没有 Isaac Lab 运行环境，因此本轮只能完成代码重构和静态语法检查。
- 尚未在真实 Isaac Lab 环境中验证：
  - 任务注册能否被 Isaac Lab 正常发现
  - `scripts/train.py` 能否正常启动 `CompleteCar-Stage0` 并优先导入项目内 `complete_car/rsl_rl`
  - `scripts/play.py` 能否正常加载 checkpoint 并优先导入项目内 `complete_car/rsl_rl`
- 当前 `RL_Training/` 结构已切换为新架构，后续不要再把旧的历史路径当作默认入口。

## 下一步优先级
- 在有 Isaac Lab 环境的机器上进入：
  - `/home/ubuntu/Graduation-Project/RL_Training`
- 先做一轮 Stage0 冒烟：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --num_envs 64 --max_iterations 5`
- 再做一轮 checkpoint 回放：
  - `python scripts/play.py --task CompleteCar-Stage0 --checkpoint <model.pt>`
- Stage0 正常后继续验证：
  - `CompleteCar-Stage1`
  - `CompleteCar-Stage2`
