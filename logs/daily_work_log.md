# 每日工作日志

## 2026-04-16

已完成：
- 按用户要求整理当前 active Stage0 reward 设计，并输出独立说明文档：
  - `docs/Stage0_reward设计详解.md`
  - 文档已包含：
    - 当前全部 reward 项
    - 每项数学公式
    - 参数含义
    - 当前取值
    - 当前取值理由
  - 随后按用户要求将文档中的公式表达改为数学符号形式
  - 已去掉代码块中的英文公式写法
- 按用户要求清理 `Stage0` TensorBoard 空指标显示：
  - 修改：
    - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
    - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py`
  - 当前对以下 termination 原因指标启用“零值稀疏写入”：
    - `Termination/terminated_rate`
    - `Termination/bad_orientation_rate`
    - `Termination/ball_joint_limit_rate`
  - 若上述指标在整段 run 中始终为 `0`，则后续新 run 默认不再在 TensorBoard 中创建对应 tag。
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py`
  完成静态编译检查，检查通过。
- 先在临时副本验证了事件文件重写逻辑：
  - `/tmp/tb-prune-KC0Msm/2026-04-16_13-20-05`
  - 验证通过后再处理真实 run。
- 运行：
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_13-20-05 --prune-sparse-zero-tags`
  已完成真实 run 事件文件清理与重新导出。
- 当前真实 run
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_13-20-05`
  的 TensorBoard termination 标签现仅保留：
  - `Termination/00_time_out_rate`
  已删除的空指标：
  - `Termination/01_terminated_rate`
  - `Termination/02_bad_orientation_rate`
  - `Termination/03_ball_joint_limit_rate`
- 原始事件文件已备份到：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_13-20-05/tensorboard_export/original_events/events.out.tfevents.1776316811.ubuntu22.20391.0`

- 按用户要求将 Stage0：
  - `goal_distance`
  改为：
  - `12.0`
- 直接启动真实 GPU 训练：
  - `/home/ubuntu/miniconda3/envs/env_isaacLab/bin/python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --run_name goaldist12_v1`
- 本轮 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_13-36-23_goaldist12_v1`
  实际在 `iteration 13/300` 主动停止，因为前期问题已足够明显，无需完整跑完。
- 对新一轮短距离多目标 Stage0 run
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_13-20-05`
  做了一轮完整离线诊断。
- 运行：
  - `python RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_13-20-05`
  成功补齐本次 run 的 TensorBoard 离线导出。
- 按用户要求重构 Stage0 配置维护方式：
  - `baseline/complete_car_stage0_cfg.py` 当前已显式集中维护 Stage0 活跃参数
  - 后续修改 Stage0 默认参数时，不再需要先回到：
    - `base/complete_car_cfg.py`
- 修改命令配置：
  - `episode_length_s = 16.0`
  - `resampling_time = 5.3`
  - `goal_distance = 3.0`
  - `goal_direction_max_deg = 30.0`
  - `goal_heading_delta_max_deg = 12.0`
- 修改基类装配逻辑：
  - `CompleteCarEnvCfg.__post_init__()` 不再强制把：
    - `commands.resampling_time`
    对齐到：
    - `episode_length_s`
- 修改命令采样逻辑：
  - `goal_heading_delta_max_deg` 当前作为独立参数参与采样
  - 不再默认使用：
    - `goal_direction_max_deg / 2`
- 按用户要求调整 TensorBoard step metrics 埋点：
  - `Command/*` 当前不再对全部环境取均值
  - 当前改为只记录：
    - `env_0`
  - 停止输出：
    - `Observation/base_lin_vel_x_raw`
    - `Observation/base_ang_vel_yaw_raw`
  - 旧主线中的：
    - `Tracking/ang_vel_yaw_abs_error`
    - `Tracking/lin_vel_x_abs_error`
    当前 active goal-conditioned Stage0 已不再输出
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  完成静态编译检查，检查通过。
- 按用户要求统一 TensorBoard termination 日志口径：
  - 旧的 `episode_reset/*` 输出已改名并并入：
    - `Termination/*`
  - 原先 step-level 的 `Termination/*` 已停止输出
  - 当前新 run 中将不再出现：
    - `episode_reset/terminated_rate`
    - `episode_reset/time_out_rate`
    - `episode_reset/bad_orientation_rate`
    - `episode_reset/ball_joint_limit_rate`
- 按用户要求继续精简 Observation 埋点：
  - 删除：
    - `Observation/wheel_normal_contact_force_abs_mean_raw`
- 按用户要求调整日志显示优先级：
  - 修改：
    - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  - 当前训练终端日志只输出高频必看的核心项
  - 低频或重复项不再在终端逐轮打印
  - TensorBoard 中高频必看项已加排序前缀：
    - `00_`
    - `01_`
    - `02_`
    用于把重点图放到每个命名空间最前面
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  完成静态编译检查，检查通过。
- 对完整 `300` iteration 真实训练 run
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_10-12-26`
  做了一轮完整离线诊断。
- 已定位并读取：
  - `/tmp/isaaclab/logs/isaaclab_2026-04-16_10-12-26.log`
  - `params/env.yaml`
  - `params/agent.yaml`
  - `tensorboard_export/latest_values.csv`
  - `tensorboard_export/summary.json`
  - 全部 scalar CSV
- 运行：
  - `python RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_10-12-26`
  成功补齐本次 run 的 TensorBoard 离线导出。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py`
- `docs/RL阶段训练参数一览表.md`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 本次 run 不是启动失败，也不是 rollout 不健康。
- 到 `iteration 299/300`：
  - `Train/mean_reward ≈ 55.87`
  - `Train/mean_episode_length ≈ 903 / 959`
  - `Tracking/goal_pos_error ≈ 7.96 m`
  - `Observation/base_lin_vel_x_raw ≈ 1.28 m/s`
  - `Observation/wheel_longitudinal_slip_abs_mean_raw ≈ 0.864`
  - `Observation/wheel_slip_angle_abs_mean_raw ≈ 0.803 rad`
  - `Observation/tilt_deg ≈ 19.89°`
  - `Reward/longitudinal_slip_gate ≈ 0.0099`
  - `Reward/lateral_slip_gate ≈ 0.145`
  - `Reward/force_gate ≈ 0.288`
  - `Loss/value ≈ 0.07`
- 训练中期 `iteration 148 ~ 157` 附近出现一次 critic `value loss` 瞬时尖峰，峰值到 `O(10^2 ~ 10^3)`，后续自行回落。
- 当前主问题已从“能否稳定跑起来”转为：
  - 纵滑仍高
  - 侧滑更差
  - 中后期车体倾斜偏大
  - 轮地法向载荷分布不理想
- 下一步优先方向应转到：
  - 轮速输出结构
  - 侧滑抑制
  - 轮地载荷分布
  而不是继续单纯压 PPO 或压球铰。

下一步：
- 基于本次诊断，优先设计一轮“轮速输出限幅/整形 + 载荷分布约束 + 侧滑抑制”定向实验。

## 2026-04-15

已完成：
- 按用户指定，把 Stage0 默认优化方向改为：
  - 先低纵向滑移
  - 低侧滑
  - 低跳动
  - 球铰速度更平滑
  - 再处理 critic 稳定性
- 将默认训练轮数改为：
  - `300`
- 调整 Stage0 PPO：
  - `save_interval = 100`
  - `actor init_std = 0.35`
  - `learning_rate = 2.0e-4`
  - `num_learning_epochs = 4`
  - `entropy_coef = 0.002`
  - `desired_kl = 0.008`
  - `value_loss_coef = 0.7`
  - `max_grad_norm = 0.7`
- 调整 Stage0 环境参数：
  - 收紧球铰动作范围
  - 球铰阻尼改为 `20.0`
  - 球铰速度上限改为 `0.8 rad/s`
  - 车轮速度上限改为 `12.0 rad/s`
  - `PhysX max_velocity_iteration_count = 1`
  - `enable_external_forces_every_iteration = True`
- 调整 reward：
  - 新增 `vertical_speed_gate`
  - 新增 `ball_joint_speed_gate`
  - `gated_progress` 当前变为：
    - `progress * roll_gate * speed_gate * force_gate * vertical_speed_gate * ball_joint_speed_gate * composite_gate`
- 调整 Stage0 观测 scale：
  - `base_ang_vel = 0.35`
  - `projected_gravity = 1.5`
  - `wheel_longitudinal_slip = 2.0`
  - `wheel_slip_angle = 1.5`
  - `wheel_normal_contact_force = 1.25`
  - `last_action = 1.5`
- 发现并修复一个 Stage0 配置装配问题：
  - `CompleteCarEnvCfg.__post_init__()` 会在末尾重建 `self.robot`
  - 因此 Stage0 在 `super().__post_init__()` 后再修改 actuator 相关 `control` 参数时，必须额外再次执行：
    - `self.robot = build_complete_car_robot_cfg(self.control, self.resets)`
  - 否则 PhysX articulation 实际仍使用 base cfg 的旧驱动参数
- 使用：
  - `python3 -m py_compile`
  完成相关 Python 文件静态编译检查，检查通过。
- 使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --max_iterations 1`
  完成两轮真实 GPU 冒烟验证。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 第一轮冒烟已确认 reward / PPO / Stage0 cfg 改动不会阻塞训练启动。
- 第二轮冒烟进一步确认 actuator 新参数真正下发到了 PhysX：
  - 球铰阻尼 `20.0`
  - 球铰速度上限 `0.8`
  - 车轮速度上限 `12.0`
- 最新通过验证的 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-26-28`
- 当前新的默认 Stage0 起点已经从“progress 优先”切到“稳定性优先”。
- 随后已启动一轮完整 `300` iteration 长跑用于中期趋势判断：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-29-47_stability_v1_iter300`
  - 实际在约 `iteration 85/300` 手动停止
- 当前长跑中期结论：
  - critic 稳定性已明显改善：
    - `Mean value loss` 约 `0.13 ~ 0.18`
  - 球铰速度已明显更平滑：
    - `ball_joint_vel_abs_mean_raw` 约 `0.43 ~ 0.45`
  - 竖向跳动约束有效：
    - `vertical_speed_gate` 约 `0.92 ~ 0.93`
  - 姿态与球铰限位不再是主要问题：
    - `bad_orientation_rate = 0`
    - `ball_joint_limit_rate = 0`
  - 但轮胎 traction 问题仍未解决：
    - `wheel_longitudinal_slip_abs_mean_raw` 约 `0.81 ~ 0.87`
    - `wheel_slip_angle_abs_mean_raw` 约 `0.64 ~ 0.75 rad`
    - 两个 slip gate 长期接近 `0`
- 下一步不应继续优先压球铰，而应转到：
  - 车轮速度目标映射
  - slip gate 结构
  - wheel action 平滑/增量约束

已完成：
- 先做了一轮“只压 wheel cap”的排除实验：
  - 临时将 Stage0 `wheel_joint_velocity_limit_sim` 改到 `8.5 rad/s`
  - 依据是 `speed_limit = 1.6 m/s` 与 `wheel_radius = 0.19 m` 对应角速度约 `8.4 rad/s`
- 使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --max_iterations 1`
  完成真实 GPU 冒烟，并确认 PhysX articulation 中 wheel velocity limit 已变成 `8.5`
- 再使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --max_iterations 40 --run_name slip_cap85_v1`
  做短训练验证
- 该实验结论：
  - 确实压低了 wheel speed
  - 但明显拖慢了前向推进
  - 且纵向滑移没有得到足够改善
  - 因此不保留为默认方案
- 随后回退该临时 wheel cap 改动，改做“slip gate 去饱和”：
  - `longitudinal_slip_gate` 从每轮乘积式 Gaussian 改为：
    - `exp(-mean(abs(longitudinal_slip)) / scale)`
  - `lateral_slip_gate` 从硬裁切余弦乘积改为：
    - `exp(-mean(abs(slip_angle)) / (pi / lateral_slip_gain))`
- 使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --max_iterations 1`
  完成新的真实 GPU 冒烟验证
- 使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --max_iterations 40 --run_name slip_gate_v1`
  完成完整短训练验证

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `8.5 rad/s` 的 wheel cap 方案被否决，不作为默认配置保留。
- `slip_gate_v1` 这轮验证 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-39-33_slip_gate_v1`
- `slip_gate_v1` 到 `iteration 39/40` 的关键信号：
  - `Observation/wheel_longitudinal_slip_abs_mean_raw ≈ 0.821`
  - `Observation/base_lin_vel_x_raw ≈ 1.17`
  - `Observation/wheel_slip_angle_abs_mean_raw ≈ 0.72 rad`
  - `Loss/value ≈ 0.15`
- 这说明：
  - slip gate 不再从一开始就塌到 `0`
  - 纵向滑移与前向推进的折中明显比 `slip_cap85_v1` 更好
  - critic 仍保持稳定
  - 当前剩下的主要 traction 问题已集中到侧滑角，而不是纵向 gate 完全失效

已完成：
- 对真实 Stage0 run
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_21-35-52`
  做了一轮完整离线诊断，重点检查了 `Observation/*_raw` 标量范围。
- 已导出并读取：
  - simulator log
  - Hydra 配置
  - `params/env.yaml`
  - `params/agent.yaml`
  - `tensorboard_export/latest_values.csv`
  - `tensorboard_export/summary.json`
  - 全部 `Observation/*_raw` scalar CSV

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 该 run 已明显学会存活与朝目标推进：
  - `mean_episode_length` 约升至 `941 / 959`
  - `goal_pos_error` 约降至 `8.75 m`
- 当前主要剩余问题是：
  - 高纵向滑移
  - 高侧滑角
  - 动作幅值偏大
  - 回合末球铰限位终止占比抬升
  - critic `value loss` 偏大
- 当前阶段判断更新为：
  - survival/progress 已建立
  - traction quality 与 critic stability 仍待解决

已完成：
- 修正 `RL_Training/scripts/play.py` 的 `--load_run` 路径解析逻辑。
- 当前 `play.py` 已支持以下 `--load_run` 写法：
  - 纯 run 目录名，如 `2026-04-15_21-35-52`
  - 带实验名前缀的相对路径，如 `complete_car_stage0/2026-04-15_21-35-52`
  - 直接指向 run 目录的绝对路径
- 原问题已定位为：
  - 旧脚本把 `--load_run complete_car_stage0/2026-04-15_21-35-52` 原样传给 Isaac Lab `get_checkpoint_path()`
  - 但当时 `log_root_path` 已经是 `.../complete_car_stage0`
  - 因此会错误拼出重复层级并报：
    - `No runs present in the directory ... match ...`
- 使用：
  - `python3 -m py_compile RL_Training/scripts/play.py`
  完成静态编译检查，检查通过。
- 使用以下真实回放命令验证：
  - `python scripts/play.py --task CompleteCar-Stage0 --load_run complete_car_stage0/2026-04-15_21-35-52 --num_envs 1 --headless`
- 验证结果：
  - 已确认回放流程不再卡在 checkpoint 路径解析
  - 当前新的实际阻塞点变为：
    - 运行机器当时无可用 CUDA 设备
    - 报错为：
      - `RuntimeError: No CUDA GPUs are available`

修改文件：
- `RL_Training/scripts/play.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `play.py` 的回放路径解析问题已修复。
- 若后续继续回放失败，应优先检查当前机器 GPU / driver / device 配置，而不是再怀疑 run 目录不存在。

已完成：
- 核对当前局部高程 patch 的真实实现入口，并删除一段无用的旧高度扫描代码。
- 当前 active critic 高程 patch 真实写在：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - 函数：
    - `_compute_critic_height_patch()`
- 删除：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
  中未被主线使用的：
  - `get_height_features()`
- 同时删除 `env._get_observations()` 中对该函数的无效调用。
- 删除原因：
  - 当前 Stage0 / Stage1 / Stage2 都没有启用 `height_scanner`
  - 该函数返回值没有进入 actor / critic 观测
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前局部高程 patch 的 active 主线只保留 `env._compute_critic_height_patch()`。
- 旧的 `height_scanner.get_height_features()` 路径已确认是死代码并已移除。

已完成：
- 将目标命令重采样改为“一个 episode 只保留一个目标”。
- 修改 `base/complete_car_cfg.py`：
  - `commands.resampling_time` 当前会在 env cfg 装配阶段自动对齐到 `episode_length_s`
- 修改 `base/env.py`：
  - 预物理步中的 timer 重采样逻辑已加门控
  - 仅当 `resampling_time < episode_length_s` 时才允许回合内中途重采样
  - 当前默认行为因此变为：
    - reset 时采样一次目标
    - 一个回合内不再切换目标
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 本次 `goaldist12_v1` 早期训练结论：
  - `Tracking/goal_pos_error: 12.02 -> 10.58`
  - `Reward/progress ≈ 0.56`
  - `Reward/gated_progress ≈ 0.008`
  - `longitudinal_slip_gate ≈ 0.011`
  - `lateral_slip_gate ≈ 0.192`
  - `wheel_longitudinal_slip_abs_mean_raw ≈ 0.852`
  - `wheel_slip_angle_abs_mean_raw ≈ 0.692`
  - `tilt_deg ≈ 3.00°`
- 当前判断：
  - 目标距离恢复到 `12m` 后，策略确实重新追求更强 progress
  - 但有效推进几乎仍被 slip gate 吃掉
  - 因此前期已经足以判断：该设置会重新把训练推向“堆 progress、牺牲 traction 质量”的方向
- 本次 `2026-04-16_13-20-05` run 的主要结论：
  - `Train/mean_episode_length = 959 / 959`
  - `Termination/time_out_rate = 1.0`
  - `tilt_deg ≈ 6.6°`
  - `wheel_normal_contact_force_sum_raw ≈ 0.94`
  - `wheel_longitudinal_slip_abs_mean_raw ≈ 0.85`
  - `wheel_slip_angle_abs_mean_raw ≈ 0.70 rad`
  - `Reward/progress` 末段接近 `0`，近 10 轮均值为负
  - `Reward/target_bonus` 成为总回报主导来源
  - `Loss/value` 在后段持续维持高位，末段约 `21`，近 10 轮均值约 `24`
- 当前判断：
  - 新任务定义显著降低了姿态和失载问题
  - 但当前策略更像“稳定存活 + 偶尔吃到 target bonus”
  - 还没有形成持续、高质量的目标推进
- 当前 goal-conditioned 主线已不再在一个 episode 内多次更换目标。
- 后续课程学习可以直接按“单回合对应单目标”的口径设计成功 / 失败判据。

已完成：
- 将轮地法向接触力的 strict 版本补充到真实可用状态，并完成默认 `64` 环境训练启动验证。
- 修正 `sensors/sensor_cfg.py`：
  - wheel-ground filter 不再指向 ground 根 prim 或通配子树
  - 当前运行时先递归解析 `ground_prim_path` 下的真实碰撞 prim
  - 平地对应 `Plane`，generator terrain 对应 `Mesh`
- 保留逐接触点法向聚合实现：
  - `sum(normal_force_scalar * contact_normal_vector)`
- 使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --max_iterations 1`
  完成真实 GPU 启动验证。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 strict 版本轮地法向力实现已可在默认 `64` 环境下正常启动训练。
- 本轮验证 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_21-10-27`
- 当前 `Observation/wheel_normal_contact_force_abs_mean_raw` 已恢复为非零，说明 ground filter 与逐接触点法向聚合链路生效。

已完成：
- 将当前轮地法向接触力实现进一步改为“基于真实接触点法向的严格版本”。
- 修改 `sensors/sensor_cfg.py`：
  - wheel-ground contact view 不再直接调用 `get_net_contact_forces(dt)`
  - 当前改为对 `get_contact_data(dt)` 返回的逐接触点法向标量与接触法向做聚合
  - 每个轮子的世界系法向合力向量按：
    - `sum(normal_force_scalar * contact_normal_vector)`
    重建
- 修改 `mdp/observations.py`：
  - 保持观测接口不变
  - 将“法向接触力”语义更新为上述聚合后法向合力向量的模长，并继续按整车重量归一化
- 同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前轮地法向接触力不再是“直接读取法向合力接口”的实现口径，而是显式基于真实接触点法向重建。
- 当前观测与奖励仍沿用同一 6 维轮载输入接口，但其底层物理定义已经收口为逐接触点法向聚合版本。

已完成：
- 删除当前 critic 显式地形高度 patch 的“三车独立 patch 拼接”方案，不再保留可选分支。
- `terrain/terrain_cfg.py` 已移除：
  - `terrain.height_patch_scheme`
  - 三 patch 总维度计算逻辑
- `base/env.py` 已恢复为：
  - 仅以中车参考系生成单份 patch
  - 仅使用中车 yaw 做 patch 旋转
  - 仅返回单份中车相对高度 patch 给 critic
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 critic 显式高度 patch 已恢复为只保留原始中车单 patch 方案。
- 之后不再使用前 / 中 / 后三 patch 拼接方案。

已完成：
- 为当前 critic 显式地形高度 patch 新增一套可选的三车独立方案。
- 保留原有：
  - `terrain.height_patch_scheme = "body_single"`
- 新增：
  - `terrain.height_patch_scheme = "three_body_separate"`
- 在新方案下：
  - 分别以前车 / 中车 / 后车的质心为 patch 原点
  - 三份 patch 分别跟随各自车体 yaw 旋转
  - 三份 patch 按 `head -> body -> tail` 顺序展平后拼接进 critic 观测
  - 每份 patch 的高度值相对各自车体质心高度计算
- 已同步让：
  - `terrain.get_num_height_points()`
  按当前方案自动返回单 patch 或三 patch 拼接后的总维度
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 critic 显式高度 patch 已支持“中车单 patch”和“前中后三 patch 拼接”两套方案。
- 默认行为仍保持原方案不变；如需启用新方案，只需在配置里切到：
  - `terrain.height_patch_scheme = "three_body_separate"`

已完成：
- 对当前三节关节小车 direct workflow 做了一轮 goal-conditioned 主线重构。
- 当前命令空间已从速度命令改为目标位姿命令：
  - env 内存储为全局目标位姿：
    - `[x_t, y_t, psi_target]`
  - 目标采样规则改为：
    - 固定距离 `12 m`
    - 相对起始航向偏角 `phi ∈ [-18.43°, 18.43°]`
    - 使用 `phi = s * phi_max * sqrt(u)` 的边缘强化二次采样
    - 目标朝向附加偏置 `delta ∈ [-9.215°, 9.215°]`
- 当前观测中的命令项已改为车体系下的相对目标：
  - `[x_rel, y_rel, psi_rel]`
- 当前动作空间已从仅球铰控制改为：
  - `6` 个球铰姿态目标
  - `6` 个车轮速度目标
  - 共 `12` 维
- wheel allocator 已从当前 env 执行链路中移除，车轮速度目标改为由 policy 直接输出并映射到速度上下界。
- 为保持 env 可运行，本轮对 reward/curriculum/metrics 做了最小兼容改动，但完整 goal-conditioned reward 设计尚未展开。
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/assets/robot_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/curriculum.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 direct workflow 的命令与动作接口已经切换到用户指定的 goal-conditioned 口径。
- 当前 Stage0 默认关键维度已变为：
  - 动作 `12`
  - Actor 观测 `52`
  - Critic 观测 `52`

已完成：
- 新增 Zotero 本地补挂脚本：
  - `scripts/literature/attach_local_pdfs_to_zotero_collection.py`
- 针对 Zotero 集合：
  - `核心参考-RL、Sim-to-Real`
  执行了一次本地 PDF 回填
- 因当前 `zotero-mcp` 的 collection 接口受 `Local API is not enabled` 限制，实际采用：
  - 关闭 `zotero-bin`
  - 备份 `zotero.sqlite`
  - 直接写入 Zotero 本地 SQLite 与 `storage/` 附件目录
  - 重开 Zotero
- 本轮从：
  - `docs/literature/`
  成功补挂 `10` 个原本缺 PDF 的条目
- 已核对补挂成功的 parent key：
  - `QFLNKZ2Q`
  - `V7VESQJM`
  - `KXTHNV77`
  - `3NRQAKKS`
  - `LMTJ8X83`
  - `ZNSS2JA8`
  - `5M2SGTER`
  - `XH4XPRC6`
  - `WXIK6J7M`
  - `2TICENYY`

修改文件：
- `scripts/literature/attach_local_pdfs_to_zotero_collection.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `核心参考-RL、Sim-to-Real` 集合里，凡是 `docs/literature/` 已有对应 PDF 且原条目缺 PDF 的项目，本轮已完成自动补挂。
- 已在真实 Zotero 库修改前生成数据库备份：
  - `/home/lbz/Zotero/zotero.sqlite.backup_2026-04-15_00-27-59`

已完成：
- 在 Zotero 桌面端已打开、并选中目标集合的前提下，使用 Google Scholar BibTeX + 本地 Zotero Connector 流程，将上轮筛出的 10 篇核心候选论文导入 Zotero 集合：
  - `核心参考-RL、Sim-to-Real`
- 本轮导入的 10 篇文献包括：
  - `Hybrid Learning for Rough Terrain Navigation of Actively Articulated Wheeled Vehicles`
  - `Control of rough terrain vehicles using deep reinforcement learning`
  - `Simultaneous control of terrain adaptation and wheel speed allocation for a planetary rover with an active suspension system`
  - `Control of robotic vehicles with actively articulated suspensions in rough terrain`
  - `Design and field testing of a rover with an actively articulated suspension system in a Mars analog terrain`
  - `Actively articulated suspension for a wheel-on-leg rover operating on a martian analog surface`
  - `Deep reinforcement learning for safe local planning of a ground vehicle in unknown rough terrain`
  - `A sim-to-real pipeline for deep reinforcement learning for autonomous robot navigation in cluttered rough terrain`
  - `Static force distribution and orientation control for a rover with an actively articulated suspension system`
  - `Predict the rover mobility over soft terrain using articulated wheeled bevameter`
- 导入结果：
  - 10 篇元数据全部导入成功
  - 3 篇 PDF 自动附加成功
  - 5 篇 PDF 因站点重定向或 `403` 被拒绝，未自动附加
  - 其余 2 篇本轮未附带可直接抓取的 PDF 链接
- 自动附加成功的 PDF 对应：
  - `Deep reinforcement learning for safe local planning of a ground vehicle in unknown rough terrain`
  - `A sim-to-real pipeline for deep reinforcement learning for autonomous robot navigation in cluttered rough terrain`
  - `Predict the rover mobility over soft terrain using articulated wheeled bevameter`
- 已同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前课题第一轮核心英文参考文献池已经落入 Zotero 主集合，后续继续做 cited-by 扩展、批注、读书笔记时可以直接从该集合接续。
- 若后续需要完整 PDF，仍需针对未自动附加的 5 篇做单篇补抓。

已完成：
- 重新检查 `USD/complete_car.usd` 的 6 个轮子刚体根节点，确认用户已手动补入 `Contact Report API`。
- 修改 `sensors/sensor_cfg.py`：
  - 为 runtime 手动创建的传感器补上 `{ENV_REGEX_NS}` 显式解析
  - 初始尝试将 wheel contact sensor 的 prim 路径修正为：
    - `{ENV_REGEX_NS}/Robot/complete_car_alternative/(body_car_wheel_left|...|tail_car_wheel_right)`
  - 进一步确认 Isaac Lab `ContactSensor` 在默认 `64` 环境 direct workflow 启动场景下仍会报：
    - `Failed to initialize contact reporter for specified bodies`
  - 最终改为运行时直接创建 6 个 PhysX `rigid_contact_view`，不再依赖 `ContactSensor`
- 修改 `base/env.py`：
  - 将 `_total_vehicle_weight` 显式放到 `self.device`
  - 修复轮地法向接触力归一化时的 CPU / CUDA 设备不一致问题
- 使用以下命令完成真实 GPU 最小训练验证：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless`
- 本轮验证通过并进入持续训练循环的 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_20-57-31`

修改文件：
- `USD/complete_car.usd`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 wheel-ground contact force 主线已经切换为 PhysX 直接 contact view，不再依赖 Isaac Lab `ContactSensor`。
- 当前默认训练命令已在真实 GPU 环境下成功进入持续训练循环。

## 2026-04-13

已完成：
- 按用户要求把当前 Stage0 命令主线从 4 维收口为单一 2 维模式：
  - `lin_vel_x`
  - `ang_vel_yaw`
- 删除 active direct workflow 中的：
  - `lin_vel_y`
  - `heading`
  命令配置入口与对应运行时使用点。
- 修改 `base/complete_car_cfg.py`：
  - `CommandCfg.num_commands` 由 `4` 改为 `2`
  - 删除 `CommandRangesCfg` 中的：
    - `lin_vel_y`
    - `heading`
  - 删除奖励配置中的：
    - `tracking_heading`
    - `tracking_heading_std`
- 修改 `mdp/commands.py`：
  - 命令重采样改为只采样 `Vx / Wz`
  - 当前将二维命令先扩成虚拟三维向量 `[Vx, 0, Wz]`，左乘固定变换矩阵后，再收口回 `[Vx', Wz']`
- 修改 `kinematics/wheel_speed_allocator.py`：
  - allocator 的平面命令入口统一改为 2 维 `[Vx, Wz]`
- 修改 `mdp/rewards.py`：
  - 删除 `tracking_heading`
  - `tracking_lin_vel` 改为只跟踪 `Vx`
- 修改 `base/env.py`：
  - episode 日志移除 `command_heading`
  - `command_ang_vel_yaw` 的索引改为新的二维命令索引
- 修改 `utils/validate_wheel_speed_allocator.py`：
  - 数值验证入口改为使用二维命令
- 更新文档：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `AGENTS.md`
- 在 `AGENTS.md` 中新增维护规则：
  - 之后只要 Stage0 RL 环境设计或训练参数配置发生实质变化，必须同步更新 `docs/RL阶段训练参数一览表.md`
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `AGENTS.md`

产出/结论：
- 当前 Stage0 active command 语义已经正式收口为二维：
  - `Vx`
  - `Wz`
- 当前 Stage0 单帧 actor/critic 观测维度由 `47` 变为 `45`
- 当前 reward 集合已进一步收口为 5 项，不再包含 `tracking_heading`

已完成：
- 对 `docs/RL阶段训练参数一览表.md` 做了一轮数学公式统一整理。
- 当前该文档不再混用：
  - `\[\]`
  - `\(\)`
  两套 LaTeX 分隔符。
- 现统一为：
  - 显示公式使用 `$$ ... $$`
  - 行内公式使用 `$ ... $`
- 已覆盖的部分包括：
  - reset 公式
  - command 变换矩阵
  - observation 拼接公式
  - action 映射公式
  - reward 公式
  - termination 公式
  - PPO / GAE 公式
- 使用 `rg -n '\\\\\\[|\\\\\\]|\\\\\\(|\\\\\\)' docs/RL阶段训练参数一览表.md` 做残留检查，已无旧公式分隔符残留。

修改文件：
- `docs/RL阶段训练参数一览表.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 参数总表的数学公式标记已经统一成更适合 Markdown 渲染的写法。
- 后续继续编辑这份文档时，应保持同一套 `$$ / $` 约定。

已完成：
- 按用户要求删除当前 direct workflow 中的：
  - `terrain.flat_only_reset`
- 修改代码位置：
  - `terrain/terrain_cfg.py`
  - `mdp/curriculum.py`
  - `baseline/complete_car_stage0_cfg.py`
  - `baseline/complete_car_stage1_cfg.py`
  - `environment_adaptive/complete_car_stage2_cfg.py`
- 当前 generator 模式下的初始 terrain type 分配不再通过 `flat_only_reset` 固定到默认地形列，而是统一走 `mdp/curriculum.py` 中的按列分布初始化逻辑。
- 同时修正 `docs/RL阶段训练参数一览表.md` 中两处会导致公式/符号渲染不正确的问题：
  - root reset 位置公式中缺失的两个 `+`
  - command 变换矩阵中的 `\times 10^{-5}` 写法
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/curriculum.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/environment_adaptive/complete_car_stage2_cfg.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/curriculum.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/environment_adaptive/complete_car_stage2_cfg.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active direct workflow 已不再保留 `flat_only_reset` 这个 reset/terrain 特殊开关。
- Stage0 参数总表中的相关数学公式已修正为可正常渲染的写法。

已完成：
- 在 `docs/` 下新增：
  - `RL阶段训练参数一览表.md`
- 该文档当前按 `CompleteCar-Stage0` 的实际代码配置整理了一份完整训练参数总表，内容覆盖：
  - 仿真与 scene
  - 地形
  - 机器人与 actuator
  - reset
  - command
  - observation
  - action
  - reward
  - termination
  - randomization
  - curriculum
  - PPO 超参数
- 文档顺序按 RL 训练流程组织，并补充了当前代码口径下的：
  - Actor / Critic / Action 维度
  - command 变换矩阵
  - 观测拼接公式
  - 逐轴动作映射公式
  - 奖励公式
  - 终止公式
  - GAE / PPO 核心公式
- 同步在 `docs/current_status.md` 中登记了这份 Stage0 参数总表文档。

修改文件：
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 已经有一份可以直接用于查参数、写实验记录和论文任务定义回填的集中式文档。
- 后续只要 Stage0 的 reward、observation、action、命令或 PPO 配置有实质变化，这份文档也需要同步更新。

已完成：
- 按用户要求从当前 direct workflow 奖励主线中删除以下 4 项：
  - `lin_vel_z`
  - `ang_vel_xy`
  - `ball_joint_deviation`
  - `ball_joint_swing`
- 修改 `mdp/rewards.py`：
  - 从 `REWARD_TERM_NAMES` 中移除上述 4 项
  - 从 `compute_reward_terms(...)` 中删除对应张量计算与加权拼接
- 修改 `base/complete_car_cfg.py`：
  - 从 `RewardScalesCfg` 中删除上述 4 个 scale 参数
  - 从 `RewardCfg` 中删除已失效的：
    - `ball_joint_target`
- 保留的当前奖励集合为：
  - `tracking_lin_vel`
  - `tracking_ang_vel`
  - `tracking_heading`
  - `orientation`
  - `action_rate`
  - `termination`
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 direct workflow 奖励集合已经显式简化，不再包含垂向速度、横滚/俯仰角速度和球铰正则项。
- 后续奖励调参与日志分析应以新的 6 项 reward 集合为准。

已完成：
- 按用户要求把 terrain curriculum 从 terrain runtime 中拆出，单独建立：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/curriculum.py`
- 在 `base/complete_car_cfg.py` 中新增：
  - `CurriculumCfg`
  用于统一保存课程学习参数：
  - `enabled`
  - `max_init_terrain_level`
  - `default_terrain_name`
  - `move_up_distance_ratio`
  - `move_down_command_ratio`
- 在 `terrain/terrain_cfg.py` 中移除了原先混在 terrain runtime 配置里的 curriculum 参数，保留 terrain 自身参数与 spawn offset 参数。
- 修改 `terrain/terrain_runtime.py`：
  - 不再内置初始 terrain level/type 采样逻辑
  - 不再内置 `update_curriculum(...)`
  - 当前只负责 terrain 数据、env origin 同步和 spawn offset
- 修改 `base/env.py`：
  - 在 `_setup_scene()` 中显式调用 `mdp/curriculum.py` 完成 terrain curriculum 初始化
  - 在 `_reset_idx()` 中显式调用 `mdp/curriculum.py` 更新 terrain curriculum
- 修改各 stage 配置：
  - `Stage0` 改为 `self.curriculum.enabled = False`
  - `Stage1` 改为 `self.curriculum.enabled = True`
  - `Stage2` 改为 `self.curriculum.enabled = True`
- 本轮额外发现并修正一个旧的运行时问题：
  - `Stage1` 中的 `default_terrain_name = "mix"` 并不是 `terrain_builder.py` 中的合法地形名
  - 当前已改为 `"flat"`
- 使用：
  - `python3 -m py_compile $(find RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car -name '*.py' | sort)`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/curriculum.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/__init__.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_runtime.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/environment_adaptive/complete_car_stage2_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 terrain curriculum 的参数入口和执行入口已经分离：
  - 参数入口：`CurriculumCfg`
  - 执行入口：`mdp/curriculum.py`
- 当前 `terrain_runtime.py` 已经从“terrain + curriculum 混合文件”收口为纯 terrain runtime 文件。
- 当前 stage 覆写 curriculum 时应统一改：
  - `self.curriculum.*`
  而不是再改：
  - `self.terrain.curriculum`

下一步：
- 在真实 Isaac Lab 环境中检查 curriculum 重构后：
  - `_setup_scene()` 是否能正常初始化 terrain levels / terrain types
  - `_reset_idx()` 是否能正常更新 terrain level
  - Stage1 / Stage2 的 terrain origin 是否随课程学习正确变化

已完成：
- 对最近动作映射改造做了一轮残留检查，发现 `actions.py` 和 `env.py` 已经改成依赖：
  - `ball_joint_action_lower_limits`
  - `ball_joint_action_upper_limits`
  但 `ControlCfg` 中一度残留旧的：
  - `ball_joint_action_scale`
  且缺失新的逐轴动作范围字段。
- 已在 `base/complete_car_cfg.py` 中删除旧的统一动作缩放字段，并补齐逐轴动作上下界配置，使运行时动作映射与当前 `actions.py` 的实现一致。
- 当前动作上下界与用户最新修改后的终止上下界保持一致：
  - `yaw in [-0.7, 0.7]`
  - `pitch in [-1.6, 0.5]`
  - `roll in [-0.5, 0.5]`
- 同步更新 `docs/current_status.md`，避免默认设计说明仍停留在旧的 pitch 范围。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前动作映射主线不再残留旧的统一 `ball_joint_action_scale` 配置。
- 当前 `ControlCfg`、`actions.py`、`env.py`、`terminations.py` 四处对球铰动作/范围的口径已经重新对齐。

已完成：
- 按用户要求取消“统一 `ball_joint_action_scale + 统一 clip_actions`”的旧动作映射方式。
- 在 `base/complete_car_cfg.py` 的 `ControlCfg` 中新增逐轴动作上下界：
  - `ball_joint_action_lower_limits`
  - `ball_joint_action_upper_limits`
  当前顺序按 `z, y, x, z, y, x` 对应：
  - `yaw in [-0.7, 0.7]`
  - `pitch in [-1.57, 0.4]`
  - `roll in [-0.5, 0.5]`
- 在 `mdp/actions.py` 中重写 `apply_ball_joint_targets(...)`：
  - policy 动作先按标准化区间 `[-1, 1]` 解释
  - 采用相对于默认关节角的非对称映射
  - 保证：
    - `action = 0` 对应默认位姿
    - `action = 1` 对应上界
    - `action = -1` 对应下界
- 在 `base/env.py` 中移除对统一 `ball_joint_action_scale` 的调用，改为向 `actions.py` 传入逐轴上下界。
- 在 `agents/rsl_rl_ppo_cfg.py` 中把 PPO wrapper 的 `clip_actions` 同步改为 `1.0`，与当前标准化动作语义一致。
- 使用 `python3 -m py_compile` 对相关文件完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前动作映射已经和逐轴球铰范围联动起来，不再依赖统一物理 scale。
- 当前动作语义已经从“统一增量控制”变为“按每个关节独立范围归一化控制”。
- 其中 pitch 的非对称范围现在能够被正确表达，且 `action=0` 不会把目标直接推到区间中心。

下一步：
- 在真实 Isaac Lab 环境中验证 6 个球铰目标是否都严格落在各自上下界内
- 观察策略初期是否更容易学出稳定的 pitch 控制

已完成：
- 按用户要求把球铰终止条件从统一阈值改为按 `yaw / pitch / roll` 分别判断。
- 在 `base/complete_car_cfg.py` 的 `TerminationCfg` 中删除了统一的：
  - `soft_ball_joint_pos_limit`
  并改为显式上下界：
  - `ball_joint_pos_lower_limits`
  - `ball_joint_pos_upper_limits`
- 当前 6 维球铰顺序按：
  - `z, y, x, z, y, x`
  解释为：
  - `yaw, pitch, roll, yaw, pitch, roll`
- 当前启用的关节范围为：
  - `yaw in [-0.7, 0.7]`
  - `pitch in [-1.57, 0.4]`
  - `roll in [-0.5, 0.5]`
  前后两组球铰目前使用同一套范围。
- 在 `mdp/terminations.py` 中把统一的绝对值比较改为逐维上下界比较，并增加了维度不匹配时报错的检查。
- 使用 `python3 -m py_compile` 对相关文件完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前终止条件中的球铰角约束已经不再是一概而论的单一标量阈值。
- 当前任务主线已经开始按轴使用非对称、分维度的球铰角终止范围。

下一步：
- 把 `clip_actions` / `ball_joint_action_scale` 的设计也和这套逐轴角度范围联动起来，避免动作目标轻易推到 pitch 上界附近

已完成：
- 按用户要求为动作随机化增加统一总开关，并保持现阶段默认关闭。
- 在 `base/complete_car_cfg.py` 的 `RandomizationCfg` 中新增：
  - `enable_action_randomization: bool = False`
- 修改 `_build_action_noise_model_cfg()`：
  - 当总开关为 `False` 时直接返回 `None`
  - 因此当前不会启用 action noise / action bias
- 修改 `mdp/randomization.py` 中 `sample_motor_strength(...)`：
  - 只有在：
    - `enable_action_randomization == True`
    - 且 `randomize_motor_strength == True`
    时才会采样随机 `motor_strength`
  - 否则始终返回全 1
- 使用 `python3 -m py_compile` 对相关文件完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/randomization.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前动作随机化已经有统一总开关。
- 当前默认配置下：
  - `enable_action_randomization = False`
  - 不使用动作噪声
  - 不使用动作 bias
  - 不使用 motor strength 动作随机化

下一步：
- 若后续需要做域随机化实验，再在对应 stage cfg 中显式打开 `enable_action_randomization`

已完成：
- 对用户完成的 MGDP 风格显式地形高度 patch 全部 6 步实现做了一轮全链路静态检查，覆盖：
  - `terrain/terrain_cfg.py`
  - `terrain/terrain_runtime.py`
  - `base/env.py`
  - `mdp/observations.py`
  - `base/complete_car_cfg.py`
  - `utils/io_descriptors.py`
  - `utils/math_utils.py`
  - `baseline/complete_car_stage1_cfg.py`
  - `environment_adaptive/complete_car_stage2_cfg.py`
  - `agents/rsl_rl_ppo_cfg.py`
- 发现并修正一个会导致“功能虽然写完但默认不生效”的配置问题：
  - `CompleteCarStage1EnvCfg` 中仍写着 `self.terrain.measure_heights = False`
  - 已改为 `True`
- 结合当前 patch 几何参数重新核对默认网格尺寸：
  - `measured_points_x = 28`
  - `measured_points_y = 7`
  - `num_height_points = 196`
- 因此在当前代码口径下：
  - 单帧 `actor` 观测维度为 `47`
  - 单帧 `critic` 观测维度在 Stage1 中为 `243`
  - Stage0 / Stage2 当前仍为 `47`
- 使用 `python3 -m py_compile` 对上述相关文件完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 6 步主线代码在静态层面已打通。
- 当前真正启用显式高度 patch 的阶段是 `Stage1`。
- 当前 Stage1 观测维度为：
  - `actor = 47`
  - `critic = 243`

下一步：
- 在真实 Isaac Lab 环境中验证 `critic` 张量末尾 196 维是否随 terrain 起伏变化
- 检查 PPO 运行时是否正确接收 `actor/critic` 两组不同维度的观测

已完成：
- 检查并修复 MGDP 风格显式地形高度 patch 迁移中的第三步实现，重点核对：
  - `base/env.py`
  - `mdp/observations.py`
  - `base/complete_car_cfg.py`
- 修正了 `env.py` 中 `_compute_critic_height_patch()` 被错误粘贴到 `_reset_idx()` 内部且语法损坏的问题；当前该函数已恢复为环境类的正式成员方法。
- 在 `env.py` 中补齐了第三步完整链路：
  - 从 `terrain_cfg.py` 生成的局部 patch 点展开到所有环境
  - 只按中车 `yaw` 做旋转
  - 加上中车世界位置得到 patch 世界坐标
  - 调用 `terrain_runtime.sample_heights_world_xy(...)` 查询地形高度
  - 构造相对高度 `base_z - terrain_height`
- 在 `mdp/observations.py` 中新增 `compute_critic_observation(...)`，使当前 critic 观测能在 actor 基础上追加显式高度 patch。
- 在 `base/complete_car_cfg.py` 中把 `observation_space` 恢复为：
  - `{"actor": ..., "critic": ...}`
  以匹配当前 env 与 PPO 的双观测组接口，并使 critic 维度在启用 `measure_heights` 时自动增加 `num_height_points`。
- 使用 `python3 -m py_compile` 对上述 3 个文件完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前第三步“中车 yaw 对齐 patch 世界点生成 + 相对高度构造”已经在 env 主线中落地。
- 当前 critic 观测链路已经具备拼接显式高度 patch 的能力，actor 仍保持原 47 维主观测不变。
- 当前 Stage1 配置仍把 `terrain.measure_heights` 设为 `False`，因此运行时默认还不会真正启用这张 critic 高度图；这属于启用配置问题，不是第三步实现错误。

下一步：
- 在阶段配置中显式打开 `terrain.measure_heights`
- 验证 `critic` 维度是否大于 `actor`
- 在真实 Isaac Lab 环境里检查相对高度 patch 数值是否符合 terrain 起伏

已完成：
- 检查用户为 MGDP 风格显式地形高度 patch 所做的前两步修改，重点核对：
  - `terrain/terrain_cfg.py`
  - `terrain/terrain_runtime.py`
- 确认当前迁移主线已经从旧的 `RayCaster height_scanner` 思路切到：
  - patch 几何参数配置
  - 局部采样点生成
  - `height_field_raw` 运行时缓存
  - 世界坐标高度查询接口
  这条 MGDP 风格链路。
- 直接修正了两处会破坏后续链路的简单错误：
  - `terrain_cfg.py` 中 `num_height_points` 对 `measured_points_y` 的拼写错误
  - `terrain_runtime.py` 中在 `initialize_after_scene_clone()` 错误清空 `_height_field_raw` 的问题
- 同步整理了 `terrain_cfg.py` 中 patch 几何辅助函数与局部 patch 点生成函数的格式与注释，使其更适合后续教学和继续扩展。
- 使用 `python3 -m py_compile` 对上述两个 terrain 文件完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_runtime.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前方案一 patch 的几何定义和局部网格生成接口已经落在 `terrain_cfg.py`。
- 当前训练地形的大高度表已经能在 `terrain_runtime.py` 中保留并提供世界坐标查询入口，不再依赖旧的 `height_scanner` 作为主路线。
- 当前仍未把显式高度 patch 真正拼入 `critic` 观测，下一步应进入 `env.py`。

下一步：
- 在 `env.py` 中实现：
  - 中车 yaw 对齐的 patch 世界点生成
  - 调用 `sample_heights_world_xy(...)`
  - 构造相对高度 patch
  - 只先拼入 `critic`

已完成：
- 检查并修复完整车 RL 主线中 Actor/Critic 观测分组修改后的连锁问题，重点核对了：
  - `base/complete_car_cfg.py`
  - `base/env.py`
  - `mdp/observations.py`
  - `utils/io_descriptors.py`
  - `utils/math_utils.py`
  - `agents/rsl_rl_ppo_cfg.py`
- 修正了 `mdp/observations.py` 中多处因手动改名产生的变量引用错误，包括：
  - `robto`
  - `front_body_id / rear_body_id`
  - `whell_joint_ids`
  - `command`
  这些不一致命名已统一到可运行版本。
- 在 `base/env.py` 中补齐：
  - `head_car_chassis`
  - `tail_car_chassis`
  的 `find_bodies()` 查询，并把环境输出从旧的单组：
  - `policy`
  改为显式双组：
  - `actor`
  - `critic`
- 在 `agents/rsl_rl_ppo_cfg.py` 中将 PPO 输入组映射从：
  - `{"actor": ["policy"], "critic": ["policy"]}`
  改为：
  - `{"actor": ["actor"], "critic": ["critic"]}`
- 在配置和维度计算侧补齐了新增观测项对应的：
  - scale
  - noise
  - descriptor
  - observation_space
  使 actor/critic 单帧观测维度统一为 `47`。
- 使用 `python3 -m py_compile` 对修改后的关键文件以及整个：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/`
  Python 树完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前观测主线已不再依赖旧的单组 `policy` 观测，而是显式区分：
  - `actor`
  - `critic`
- 当前 `critic` 仍与 `actor` 保持完全一致，后续若做 privileged critic，可直接在现有 `critic` 组上扩展。
- Stage2 传感器运行时链路仍保留，但当前默认不再拼入 actor/critic 主观测主干。

下一步：
- 在真实 Isaac Lab 环境中优先做一轮 `CompleteCar-Stage0` 冒烟，确认：
  - actor/critic 双组观测能被 env wrapper 与 PPO 正常接收
  - 观测维度与运行时实际返回张量一致

## 2026-04-12

已完成：
- 按用户要求，为完整车 RL 主线中的 `Vx / Vy / Wz` 命令语义加入固定左乘变换矩阵：
  - `[[1, 0, -0.00614478162640497], [0, 1, -1.07379532542362e-5], [0, 0, 1]]`
- 在 `wheel_speed_allocator.py` 中保留 NumPy 版命令变换 helper：
  - `transform_planar_command_numpy`
- 按用户进一步要求，将 `transform_planar_command_torch` 的实现移动到 `mdp/commands.py` 内部，使 Torch 命令语义逻辑直接放在命令模块中。
- 在 `mdp/commands.py` 的命令重采样出口统一对 `commands[:, :3]` 应用该变换，使 env 内保存的命令直接变成变换后的语义。
- 同步更新 `utils/validate_wheel_speed_allocator.py`，使独立验证脚本与训练主线使用同一命令变换逻辑，并增加对纯 `yaw` 命令变换结果的数值断言。
- 使用 `python3 -m py_compile` 对本轮修改的 Python 文件完成静态语法检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `commands` 张量在 env 内已经不是原始采样值，而是对 `Vx,Vy,Wz` 左乘固定矩阵后的结果；因此观测、奖励、terrain curriculum、轮速分配和日志现在都共享同一套命令语义。
- 当前命令变换逻辑按使用层拆分为：
  - `mdp/commands.py` 中的 Torch 实现，供 env 主线调用
  - `wheel_speed_allocator.py` 中的 NumPy 实现，供独立验证脚本调用
- 当前终端环境中的 `python3` 缺少 `numpy`，因此本轮无法在这里直接跑通 `validate_wheel_speed_allocator.py`，但静态编译已通过。

下一步：
- 在带 `numpy` 的 Python 环境中运行：
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py`
- 在真实 Isaac Lab 环境中继续做 `CompleteCar-Stage0` 冒烟，确认训练主线下该命令变换不会引入新的运行态问题。

已完成：
- 修改毕业论文 `chapter_03` 中速度雅可比矩阵模型推导，将前后侧模块固定偏置从 `${}^{1}\mathbf b_1 / {}^{3}\mathbf b_3` 改为由单一标量 `b` 定义的镜像偏置 `${}^{1}\mathbf b=[-b,0,0]^T`、`${}^{3}\mathbf b=[b,0,0]^T`。
- 按用户更正，明确偏置向量仅保留 `x` 分量，且 `y=z=0`。
- 同步修正文中几何定义、位置关系、速度传播、雅可比展开、章节小结与英文 `Summary` 的相关表述。
- 进一步利用 `\mathbf e_x^T\mathbf S({}^{i}\mathbf b)=0` 对显式轮速行雅可比中的相关项做了化简。
- 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 完成论文主文档编译验证。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `chapter03.tex` 内与该推导相关的公式已统一到单一参数 `b` 的对称偏置建模，不再保留 `b_1 / b_3` 的旧记号，也不再保留 `b_z` 或非零 `y/z` 分量。
- LaTeX 编译通过，输出文件为 `毕业论文/毕业论文模板/LaTeX/main.pdf`。
- 当前仍有未定义引用与排版类 warning，但与本次公式修改无直接关系。

下一步：
- 如需继续收口论文第三章，可进一步统一图注、变量说明表和前后章节中对偏置向量的文字描述。

## 2026-04-11

已完成：
- 清理并重写 `docs/RL环境设计.md` 中的 LaTeX 公式与符号渲染格式。
- 删除文档内残留的私有区引用乱码字符：
  - `filecite...`
- 将原来的：
  - `\\(...\\)`
  - `\\[...\\]`
  数学写法统一改为更适合 Markdown 渲染器的：
  - `$...$`
  - `$$...$$`
- 同步修正了公式内少量文本符号写法，例如：
  - `heading`
  - `command`
  - `body collision`
  以避免被数学渲染器错误当作变量串。
- 已使用 `pandoc` 实际导出验证：
  - `pandoc docs/RL环境设计.md -f markdown+tex_math_dollars -t html5 -s --mathjax -o /tmp/RL环境设计_mathjax.html`
  导出成功。
- 已确认文档内不再存在：
  - 旧 LaTeX 定界符
  - 私有区乱码字符
  - Unicode 替换字符 `�`

修改文件：
- `docs/RL环境设计.md`
- `logs/daily_work_log.md`

产出/结论：
- `docs/RL环境设计.md` 现在已经改成统一的 Markdown 数学公式格式，后续在支持数学渲染的 Markdown 预览器中应能正常显示，不再夹杂引用乱码。

下一步：
- 若还需要，可继续把同类数学格式清洗规则应用到 `docs/` 下其他含公式文档。

已完成：
- 按用户要求新增顶层 RL 重构工程：
  - `complete_car_rl_training/`
- 新工程已改成 Isaac Lab 扩展式目录：
  - `scripts/train.py`
  - `scripts/play.py`
  - `source/complete_car_lab/config/extension.toml`
  - `source/complete_car_lab/setup.py`
  - `source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/...`
- 当前 direct task 已按新要求拆分为：
  - `base/env.py`
  - `base/complete_car_cfg.py`
  - `baseline/complete_car_stage0_cfg.py`
  - `baseline/complete_car_stage1_cfg.py`
  - `environment_adaptive/complete_car_stage2_cfg.py`
- `mdp/` 已拆分出：
  - `commands.py`
  - `actions.py`
  - `observations.py`
  - `rewards.py`
  - `terminations.py`
  - `resets.py`
  - `randomization.py`
- `terrain/`、`sensors/`、`kinematics/`、`utils/` 也已按新结构补齐。
- 新 Gym task id 已统一为：
  - `CompleteCar-Stage0`
  - `CompleteCar-Stage1`
  - `CompleteCar-Stage2`
- 已执行：
  - `python3 -m py_compile $(find complete_car_rl_training -name '*.py' | sort)`
  静态语法检查通过。

修改文件：
- `complete_car_rl_training/README.md`
- `complete_car_rl_training/pyproject.toml`
- `complete_car_rl_training/scripts/train.py`
- `complete_car_rl_training/scripts/play.py`
- `complete_car_rl_training/source/complete_car_lab/config/extension.toml`
- `complete_car_rl_training/source/complete_car_lab/setup.py`
- `complete_car_rl_training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/...`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前活跃 RL 重构主线已经从旧的 `RL_Training/...` 逻辑树迁到新的 `complete_car_rl_training/`。
- 新主线的任务注册、配置主干、stage 配置、训练脚本、回放脚本、模块边界已经统一到同一套 direct workflow 架构下。

下一步：
- 在带 Isaac Lab 环境的机器上优先验证：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless`
  - `python scripts/play.py --task CompleteCar-Stage0 --checkpoint <model.pt>`

已完成：
- 按用户进一步要求，把上一轮错误新建的平行目录重构结果迁回现有：
  - `RL_Training/`
  做原地替换。
- 当前 `RL_Training/` 根目录已清理为：
  - `README.md`
  - `pyproject.toml`
  - `scripts/train.py`
  - `scripts/play.py`
  - `source/complete_car_lab/...`
- 已删除旧结构与残留目录：
  - `RL_Training/complete_car_rl_training/`
  - `RL_Training/config/`
  - `RL_Training/docs/`
  - `RL_Training/kinematics/`
  - `RL_Training/rsl_rl/`
  - `RL_Training/scripts/rsl_rl/`
  - `RL_Training/setup.py`
  - `RL_Training/skills/`
  - `RL_Training/utils/`
- 已删除错误创建的平行目录：
  - `complete_car_rl_training/`
- 已执行：
  - `python3 -m py_compile $(find RL_Training -name '*.py' | sort)`
  静态语法检查通过。

修改文件：
- `RL_Training/README.md`
- `RL_Training/pyproject.toml`
- `RL_Training/scripts/train.py`
- `RL_Training/scripts/play.py`
- `RL_Training/source/complete_car_lab/...`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 这次重构已经不是平行新建项目，而是把现有 `RL_Training/` 原地替换成新架构。
- 后续检查项目时，只需要看 `RL_Training/`，不应再寻找已删除的 `complete_car_rl_training/`。

下一步：
- 在 Isaac Lab 环境中从 `RL_Training/` 根目录执行：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless`
  - `python scripts/play.py --task CompleteCar-Stage0 --checkpoint <model.pt>`

已完成：
- 按用户要求，更新 `docs/isaaclab_rl_template_and_mgdp_structure.md`，为当前 active direct 主线
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/`
  增补了一整节逐文件结构说明。
- 新增内容不再只停留在旧 manager-based 模板梳理，而是补齐了 current `complete_car` 目录下各脚本的：
  - 文件职责
  - 包含的类
  - 包含的函数
  - 类与函数在当前 direct workflow 中的功能含义
- 本轮文档覆盖了：
  - `__init__.py`
  - `complete_car_env_cfg.py`
  - `stage0_flat_cfg.py`
  - `stage1_terrain_cfg.py`
  - `stage2_perception_cfg.py`
  - `complete_car_env.py`
  - `commands.py`
  - `observations.py`
  - `local_velocity_tracking_reward.py`
  - `rewards.py`
  - `terminations.py`
  - `utils.py`
  - `assets/`
  - `sensors/`
  - `terrain/`
  - `agents/`
- 同步更新项目记忆文件，使后续会话能直接继承这次文档化结论。

修改文件：
- `docs/isaaclab_rl_template_and_mgdp_structure.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `docs/isaaclab_rl_template_and_mgdp_structure.md` 现在已经可以作为当前 direct `complete_car` 主线的结构化索引使用，后续阅读时可以先按文档确认“哪个脚本负责什么、类和函数分别做什么”，再进入源码细读。

下一步：
- 若继续补教学文档，可再把 `RL_Training/scripts/rsl_rl/train.py`、`play.py` 以及 `RL_Training/rsl_rl/` 的关键调用链按相同粒度补到结构文档里。

已完成：
- 按用户要求，将 `complete_car_env_cfg.py` 从“文件级多个并列配置类”改为“以 `CompleteCarEnvCfg` 为中心的嵌套配置类”组织。
- 当前嵌套结构包括：
  - `CommandCfg -> ranges`
  - `ObservationCfg -> scales / noise_scales`
  - `RewardCfg -> scales`
  - `ControlCfg / ResetCfg / RandomizationCfg`
  均作为 `CompleteCarEnvCfg` 的内部配置类存在。
- 按用户进一步要求，`CommandCfg`、`ObservationCfg`、`RewardCfg` 的子配置类名已统一改成与字段同名的小写形式，例如：
  - `ranges: ranges = ranges()`
  - `scales: scales = scales()`
  - `noise_scales: noise_scales = noise_scales()`
- 已检查仓库内对旧顶层配置类名的引用，当前 `RL_Training/` 中没有残留外部依赖这些旧类型名的位置。
- 已执行：
  - `python3 -m py_compile RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py RL_Training/complete_car_rl_training/tasks/direct/complete_car/stage0_flat_cfg.py RL_Training/complete_car_rl_training/tasks/direct/complete_car/stage1_terrain_cfg.py RL_Training/complete_car_rl_training/tasks/direct/complete_car/stage2_perception_cfg.py`
  静态校验通过。

修改文件：
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `complete_car_env_cfg.py` 当前已经改为更内聚的嵌套配置结构，后续阅读和维护时应从 `CompleteCarEnvCfg` 向下展开，而不是继续把各组配置类视为文件级平铺对象。

下一步：
- 若继续统一风格，可考虑把 `stage0_flat_cfg.py`、`stage1_terrain_cfg.py`、`stage2_perception_cfg.py` 中针对 `terrain/sensors/scene` 的 stage 覆写也进一步补成更显式的局部说明。

已完成：
- 按用户要求，参考 `complete_car_env_cfg.py` 前两个配置类的注释风格，为其余配置类补齐字段说明与少量方法级说明。
- 本轮注释补充覆盖了：
  - `CompleteCarControlCfg`
  - `CompleteCarObservationScalesCfg`
  - `CompleteCarObservationNoiseScalesCfg`
  - `CompleteCarObservationCfg`
  - `CompleteCarRewardScalesCfg`
  - `CompleteCarRewardCfg`
  - `CompleteCarResetCfg`
  - `CompleteCarRandomizationCfg`
  - `CompleteCarEnvCfg`
- 同步补充了 `CompleteCarEnvCfg` 中噪声模型构建和 `__post_init__` 主流程的简短说明，未改动任何配置值或运行逻辑。
- 已执行：
  - `python3 -m py_compile RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
  静态校验通过。

修改文件：
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `complete_car_env_cfg.py` 中共享 direct cfg 主干的主要字段都已有与现有风格一致的英文注释，后续讲解和维护时不必再反复对照运行逻辑猜字段含义。

下一步：
- 若继续做可读性维护，可按相同风格补齐 `stage0_flat_cfg.py`、`stage1_terrain_cfg.py`、`stage2_perception_cfg.py` 中仍偏稀疏的配置注释。

已完成：
- 按用户最新要求，把上一轮被删掉但仍需保留的旧内容重新迁入当前 `RL_Training/` 新架构内部。
- 已恢复并重定位本地 PPO 本体：
  - 旧位置：`RL_Training/rsl_rl/`
  - 新位置：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/`
- 已修改：
  - `RL_Training/scripts/train.py`
  - `RL_Training/scripts/play.py`
  让训练和回放优先导入项目内的 `complete_car/rsl_rl/`，不再默认依赖外部环境里的 `rsl_rl`。
- 已把旧辅助脚本迁入：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/`
  包括：
  - `list_envs.py`
  - `random_agent.py`
  - `zero_agent.py`
  - `export_training_stage.py`
  - `tensorboard_export.py`
  - `validate_wheel_speed_allocator.py`
- 这些辅助脚本的导入已同步改成：
  - `complete_car_lab`
  - `CompleteCar-Stage0/1/2`
- 已把旧 `RL_Training/utils/` 中的 IK/FK 内容迁入：
  - `kinematics/ik_solver.py`
  - `kinematics/fk_solver.py`
  - `kinematics/legacy_ik/`
  - `kinematics/legacy_fk/`
- `IK_model.py` 的 3RRR 球面并联逆解逻辑已经并入 `ik_solver.py`，并保留旧推导资料作为参考文件。
- 已执行：
  - `python3 -m py_compile $(find RL_Training -name '*.py' | sort)`
  静态校验通过。

修改文件：
- `RL_Training/scripts/train.py`
- `RL_Training/scripts/play.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/...`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/...`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/ik_solver.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/fk_solver.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/legacy_ik/...`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/legacy_fk/...`
- `README.md`
- `RL_Training/README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前新架构并没有丢掉旧 PPO 本体、旧 IK/FK、旧辅助脚本，而是把它们统一收口到了 `tasks/direct/complete_car/` 之下。
- 顶层 `RL_Training/scripts/` 现只保留训练和回放入口，其余辅助脚本已迁入包内 `utils/`。

下一步：
- 在 Isaac Lab 环境中验证：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless`
  - `python scripts/play.py --task CompleteCar-Stage0 --checkpoint <model.pt>`
  - `python -m complete_car_lab.tasks.direct.complete_car.utils.list_envs`

已完成：
- 按用户要求，为 `base/complete_car_cfg.py` 中的 `CommandCfg` 补充了以下字段的中文注释：
  - `heading_command`
  - `zero_command`
  - `rel_standing_envs`
- 同时为 `ControlCfg` 中时间步长、控制周期、球铰/车轮刚度阻尼、力矩上限、速度上限等字段补充了单位注释。
- 本轮未改动任何配置值与运行逻辑，仅提升配置文件可读性。
- 已执行：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `complete_car_cfg.py` 里命令语义和控制参数单位已经更明确，后续阅读和讲解时不需要再额外口头说明这些字段的物理含义。

已完成：
- 按用户要求，修改当前 direct 主线的本体观测定义，不再把车体姿态欧拉角和姿态角速率作为 policy observation。
- 新的基础本体观测改为：
  - `base_lin_vel_b`
  - `base_ang_vel_b`
  - `projected_gravity_b`
  - `ball_joint_pos`
  - `ball_joint_vel`
  - `commands`
  - `last_action`
- 同步修改了：
  - `ObservationScalesCfg`
  - `ObservationNoiseCfg`
  - observation descriptor
  - observation 维度与噪声幅值计算
- 已执行：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active observation 已经从“姿态角 + 姿态角速度”切换成“base 线速度 + base 角速度 + 重力投影”，后续解释环境时应以这套定义为准。

已完成：
- 按用户要求，删除 `CompleteCarEnvCfg` 中按 `stage_name` 自动绑定 terrain / sensor 默认值的 `_bind_stage_defaults()`。
- 同步把原先 Stage0 / Stage1 / Stage2 的 terrain 和 sensor 开关配置，下放到各自的 stage cfg 文件中显式定义：
  - `complete_car_stage0_cfg.py`
  - `complete_car_stage1_cfg.py`
  - `complete_car_stage2_cfg.py`
- `CompleteCarEnvCfg.__post_init__()` 不再隐式修改阶段差异，base cfg 现在只负责共享骨架和统一装配。
- 已执行：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/environment_adaptive/complete_car_stage2_cfg.py`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/environment_adaptive/complete_car_stage2_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 stage 差异已经真正下沉到分阶段配置文件中，后续用户可直接在各 stage cfg 内继续定义 terrain / sensor 方案，而不需要修改 base cfg 中的集中绑定逻辑。

## 2026-04-10

已完成：
- 按用户要求，处理 `complete_car.usd` 中 articulation root 迁移到 `/World/complete_car_alternative/body_car_chassis` 后的联动脚本。
- direct RL 资产配置已显式对齐新的 articulation root：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/assets/robot_cfg.py`
  现在通过 `articulation_root_prim_path = "/body_car_chassis"` 指向新的根节点，而不是继续隐式依赖 USD 自动搜索。
- 与车体挂点相关的默认 prim path 已同步修改：
  - `sensors/sensor_runtime.py`
    - IMU -> `.../body_car_chassis/IMU_body`
    - camera -> `.../head_car_chassis/Stereo_rig/left_camera`
    - lidar -> `.../head_car_chassis/Example_Rotary`
  - `terrain/terrain_runtime.py`
    - height scanner -> `.../body_car_chassis`
- 直接打开 USD 并创建 articulation 的脚本已切到新的 articulation root：
  - `scripts/isaac_sim/control_keyboard.py`
  - `scripts/isaac_sim/rover_control.py`
- `scripts/isaac_sim/check_isaaclab_asset.py` 已补充新的 root 检查，并在最小加载测试里显式写入 `articulation_root_prim_path="/body_car_chassis"`。

修改文件：
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/assets/robot_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/sensors/sensor_runtime.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terrain/terrain_runtime.py`
- `scripts/isaac_sim/check_isaaclab_asset.py`
- `scripts/isaac_sim/control_keyboard.py`
- `scripts/isaac_sim/rover_control.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前项目已经明确区分：
  - 资产挂载根
  - articulation root
- RL 主线继续挂载在 `.../Robot` 下，但 articulation API 会显式落到 `.../Robot/body_car_chassis`。
- 已执行 `python3 -m py_compile`，本轮涉及文件静态校验通过。

下一步：
- 在 Isaac Sim / Isaac Lab 环境中优先验证：
  - `scripts/isaac_sim/control_keyboard.py`
  - `scripts/isaac_sim/check_isaaclab_asset.py`
  - `python scripts/list_envs.py --keyword Complete-Car`

已完成：
- 按用户要求清理当前 direct 主线中的模板残余和未接线字段。
- 收口训练与回放脚本：
  - `RL_Training/scripts/rsl_rl/train.py`
  - `RL_Training/scripts/rsl_rl/play.py`
  现在不再保留 manager-based / MARL 模板类型联合，也移除了 `train.py` 中只对 manager-based 生效的 `--export_io_descriptors` 分支。
- 收口 direct env 配置主干：
  - 删除 `CompleteCarCommandCfg` 中未接线的 `heading_command`、`rel_heading_envs`、`debug_vis`
  - 删除 `CompleteCarCommandRangesCfg` 中未接线的 `ang_vel_z`、`heading`
  - 删除 `CompleteCarRewardCfg` 中未接线的 `base_height_target`
- 将当前 direct 主线的噪声链路切回 Isaac Lab 基类能力：
  - `DirectRLEnvCfg.action_noise_model`
  - `DirectRLEnvCfg.observation_noise_model`
  当前 `randomization.action_noise_std / action_bias_std` 与 `observations.add_noise / noise_level / noise_scales` 仍作为参数源保留，但不再由 `CompleteCarEnv` 和 `observations.py` 手写加噪。
- 同步修正文档中“这些残余仍存在”的旧描述，并纠正架构文档实际路径为：
  - `docs/complete_car_direct_workflow_architecture.md`

修改文件：
- `RL_Training/scripts/rsl_rl/train.py`
- `RL_Training/scripts/rsl_rl/play.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/observations.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/utils.py`
- `README.md`
- `docs/complete_car_direct_workflow_architecture.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 direct 主线已经不再保留用户本轮点名的模板残余和未接线字段。
- 噪声配置现在有了清晰边界：
  - 本地 cfg 负责参数源
  - Isaac Lab 基类负责运行时噪声注入
- 当前默认 stage 仍是 `use_history = False`，因此观测噪声切回基类后不会影响现有主线的历史堆叠语义。
- 已对本轮涉及的训练脚本与 direct 主线核心 Python 文件执行 `python3 -m py_compile`，静态校验通过。

下一步：
- 在具备 Isaac Lab 运行环境的机器上，优先做一次 Stage0 direct 冒烟。

已完成：
- 按用户要求，替换 `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex` 中 `3.1.10`“整车速度雅可比矩阵构造”部分，采用新的长版推导正文。
- 将用户草稿里混入的非法格式全部改回合法 LaTeX，包括：
  - 非法分隔符
  - 损坏的矩阵换行
  - 错误的公式对齐
  - 非法符号拼接
- 保留并整理了该小节的主要公式链：
  - 整车广义速度 `\boldsymbol\xi`
  - 反对称矩阵算子 `\mathbf S(\mathbf x)`
  - 模块刚体速度映射 `\mathbf K_1(\mathbf q), \mathbf K_2, \mathbf K_3(\mathbf q)`
  - 单模块轮速映射 `\mathbf H_i`
  - 整车速度雅可比 `\mathbf J_w(\mathbf q)`
- 在 `毕业论文/毕业论文模板/LaTeX/` 下重新执行：
  - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
  编译成功，`main.pdf` 已更新。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `毕业论文/毕业论文模板/LaTeX/main.pdf`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `3.1.10` 小节已经从用户提供的损坏草稿替换为可编译、符号一致的 LaTeX 版本。
- 当前论文主文档可继续通过 XeLaTeX 生成 PDF。
- 当前仍只剩 2 条旧的非阻塞文献警告：
  - `fang2015survey`
  - `MATSUMURA2017566`

下一步：
- 若继续打磨 chapter03，可再针对这一节里过长的行公式做版面收缩，但这已经不影响编译通过。

已完成：
- 根据用户新的长期主线要求，将完整车 RL 项目从 Isaac Lab manager-based 架构彻底重构为 direct workflow。
- 新增 direct task 主目录：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/`
- 实际新增文件包括：
  - `complete_car_env.py`
  - `complete_car_env_cfg.py`
  - `stage0_flat_cfg.py`
  - `stage1_terrain_cfg.py`
  - `stage2_perception_cfg.py`
  - `rewards.py`
  - `observations.py`
  - `commands.py`
  - `terminations.py`
  - `utils.py`
  - `agents/ppo_cfg.py`
  - `assets/robot_cfg.py`
  - `terrain/terrain_generator.py`
  - `terrain/terrain_runtime.py`
  - `sensors/sensor_runtime.py`
- 新 direct Gym task id 已改为：
  - `Complete-Car-Stage0-Flat-Direct-v0`
  - `Complete-Car-Stage1-Terrain-Direct-v0`
  - `Complete-Car-Stage2-Perception-Direct-v0`
- 已删除旧主线文件：
  - `envs/base/complete_car_config.py`
  - `envs/base/complete_car_env.py`
  - `envs/base/manager_helpers.py`
  - `envs/base/robot_cfg.py`
  - `envs/baseline/complete_car_config_baseline.py`
  - `envs/__init__.py`
  - `utils/terrain.py`
- 已同步修改根目录 Isaac Sim 预览/控车脚本，使其读取新的：
  - `tasks/direct/complete_car/assets/robot_cfg.py`
  - `tasks/direct/complete_car/terrain/terrain_generator.py`
- 已同步更新：
  - `README.md`
  - `RL_Training/README.md`
  - `RL_Training/docs/training_workflow_and_tensorboard_guide.md`
  - `docs/project_file_map.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`

修改文件：
- `README.md`
- `RL_Training/README.md`
- `RL_Training/docs/training_workflow_and_tensorboard_guide.md`
- `docs/project_file_map.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `RL_Training/complete_car_rl_training/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/stage0_flat_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/stage1_terrain_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/stage2_perception_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/rewards.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/observations.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/commands.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terminations.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/utils.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents/ppo_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/assets/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/assets/robot_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terrain/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terrain/terrain_generator.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terrain/terrain_runtime.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/sensors/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/sensors/sensor_runtime.py`
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `scripts/isaac_sim/preview_stage1_tile.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `scripts/isaac_sim/control_keyboard.py`

产出/结论：
- 当前 RL 工程主线已经从“manager term 组装任务”切换为“env 主类直接管理任务语义”的 direct workflow。
- 结构上已经保留了“共享参数模板 + 分阶段继承配置”的思想，但不再保留 `CompleteCarObservationsCfg / CompleteCarActionsCfg / CompleteCarEventsCfg` 这类 manager-based 配置分组。
- 当前机器没有 Isaac Lab 运行环境，因此本轮不做运行态冒烟，只完成代码重构和仓库记忆同步。

下一步：
- 在有 Isaac Lab 环境的机器上，优先执行：
  - `python scripts/list_envs.py --keyword Complete-Car`
  - `python scripts/rsl_rl/train.py --task Complete-Car-Stage0-Flat-Direct-v0 --headless --num_envs 100 --max_iterations 10`

已完成：
- GitHub 同步后，清理了本地未跟踪的旧 `src/` 残留目录，不再保留旧 `src/rl_lab/complete_car_rl_training/` 工作树副本。
- 统一修正后续使用的命令入口和说明文件，明确当前所有可运行命令默认都应从：
  - `/home/ubuntu/Graduation-Project/RL_Training`
  执行。
- 修正文档与技能中的旧路径或失效引用：
  - `AGENTS.md`
  - `RL_Training/README.md`
  - `RL_Training/docs/training_workflow_and_tensorboard_guide.md`
  - `RL_Training/skills/isaac-rl-run-diagnosis/SKILL.md`
  - `docs/isaaclab模板使用指南.md`
  - `docs/isaaclab_rl_template_and_mgdp_structure.md`
  - `docs/current_status.md`

修改文件：
- `AGENTS.md`
- `RL_Training/README.md`
- `RL_Training/docs/training_workflow_and_tensorboard_guide.md`
- `RL_Training/skills/isaac-rl-run-diagnosis/SKILL.md`
- `docs/isaaclab模板使用指南.md`
- `docs/isaaclab_rl_template_and_mgdp_structure.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库已经不再保留本地旧 `src/` 运行入口。
- 后续列环境、训练、回放、TensorBoard 导出等命令，默认都应在 `RL_Training/` 下执行。

下一步：
- 在具备 Isaac Lab 运行环境的机器上，从 `RL_Training/` 执行一次 `list_envs.py` 和 Stage0 小规模 `train.py` 冒烟。

已完成：
- 基于当前 direct workflow 真实代码，新增了完整车 RL 主线的长期架构说明文档：
  - `docs/complete_car_direct_workflow_architecture.md`
- 文档内容已系统整理：
  - task 注册与入口机制
  - env / cfg / terrain runtime / sensor runtime 的职责边界
  - 训练调用链
  - Stage0 / Stage1 / Stage2 的组织关系
  - 后续修改观测、奖励、动作、命令、课程学习、terrain、传感器、stage、agent 配置时应优先修改的位置
- 同步更新仓库说明与项目地图，使新文档可被后续会话直接发现：
  - `README.md`
  - `docs/project_file_map.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`

修改文件：
- `docs/complete_car_direct_workflow_architecture.md`
- `README.md`
- `docs/project_file_map.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库已经有一份可长期保留、可反复检索的 direct workflow 架构说明，不再需要每次从聊天记录临时重建调用链和修改入口。

下一步：
- 如果后续 direct 主线继续演化，优先维护这份文档，而不是只在聊天记录里解释。

## 2026-04-10（GitHub 同步）

已完成：
- 检查当前仓库 Git 状态，确认当前分支为 `main`，远程 `origin` 指向 `git@github.com:MARS-ROBOTICS-star/Graduation-Project.git`。
- 为避免误提交论文编译中间产物，在 `毕业论文/毕业论文模板/LaTeX/.gitignore` 中补充了 `*.xdv` 忽略规则。
- 将当前工作区状态整理后提交，并准备推送到远程 GitHub 仓库。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/.gitignore`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库的 GitHub 同步路径已经明确，后续只需继续在 `main` 分支提交并推送到现有 `origin`。
- `main.xdv` 不再作为未跟踪文件干扰后续提交。

下一步：
- 将本地提交推送到 `origin/main`，完成本次上传。

## 2026-04-09

已完成：
- 按用户新要求继续收敛 RL 训练文件结构，使 `base` 更像通用框架层，`baseline` 更像阶段参数覆写层。
- 实际结构调整：
  - 保留并重写：
    - `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
  - 新增：
    - `RL_Training/complete_car_rl_training/envs/baseline/complete_car_config_baseline.py`
    - `RL_Training/complete_car_rl_training/utils/__init__.py`
  - 将原：
    - `envs/baseline/stage1_terrain.py`
    移动并改为：
    - `RL_Training/complete_car_rl_training/utils/terrain.py`
  - 删除旧 baseline 子文件：
    - `envs/baseline/__init__.py`
    - `envs/baseline/stage1_env.py`
    - `envs/baseline/stage1_env_cfg.py`
    - `envs/baseline/agents/`
    - `envs/baseline/mdp/`
- 新的职责划分：
  - `base/complete_car_config.py`
    - 作为共享 RL 训练框架文件
    - 当前明确包含：
      - `env`
      - `terrain`
      - `perception`
      - `control`
      - `scene`
      - `commands`
      - `observations`
      - `actions`
      - `events`
      - `rewards`
      - `terminations`
      - `curriculum`
      - `CompleteCarRLEnv`
      - `CompleteCarCfgPPO`
  - `baseline/complete_car_config_baseline.py`
    - 只负责 baseline 阶段 reward / terrain / perception / PPO 参数覆写与 Gym 注册
  - `utils/terrain.py`
    - 负责 terrain 生成和 terrain runtime helper
- 同步修复：
  - `envs/__init__.py`
    - 改为直接导入 `baseline/complete_car_config_baseline.py`
  - `scripts/isaac_sim/preview_stage1_terrain.py`
  - `scripts/isaac_sim/preview_stage1_tile.py`
  - `scripts/isaac_sim/preview_stage1_last_six.py`
  - `scripts/isaac_sim/control_keyboard.py`
    的 terrain 模块路径，统一指向 `utils/terrain.py`
- 实际执行静态校验：
  - 对 `RL_Training/complete_car_rl_training`、`RL_Training/scripts`、`scripts/isaac_sim` 执行了 `python3 -m py_compile`
  - 语法检查通过

修改文件：
- `README.md`
- `RL_Training/README.md`
- `docs/current_status.md`
- `docs/project_file_map.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `RL_Training/complete_car_rl_training/envs/__init__.py`
- `RL_Training/complete_car_rl_training/envs/base/__init__.py`
- `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
- `RL_Training/complete_car_rl_training/envs/baseline/complete_car_config_baseline.py`
- `RL_Training/complete_car_rl_training/utils/__init__.py`
- `RL_Training/complete_car_rl_training/utils/terrain.py`
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `scripts/isaac_sim/preview_stage1_tile.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `scripts/isaac_sim/control_keyboard.py`

产出/结论：
- 当前 `base` 已经更接近“MGDP 风格的通用 config trunk”，但仍保持 Isaac Lab manager-based 的组织方式，没有回退到大而全的手写 `base_task` 模式。
- 当前 `baseline` 目录已被压缩成单文件参数覆写层，后续更容易保留阶段配置而不是不断覆盖旧版本。
- 当前 terrain 逻辑已经离开 baseline 目录，后续若拓展 Stage2 / Stage3，不必再复制一份 terrain 生成文件。

下一步：
- 在 `env_isaacLab` 中从 `RL_Training/` 目录执行：
  - `python scripts/list_envs.py --keyword Complete-Car`
  - `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --headless --num_envs 100 --max_iterations 10`
 继续做运行态冒烟。

## 2026-04-09（论文编译修复）

已完成：
- 根据用户要求排查 `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex` 的编译失败问题。
- 确认原 `chapter03.tex` 中混入了大量非法格式内容，包括：
  - 伪 Markdown 分隔线
  - `#` 标记
  - 损坏的矩阵换行
  - 错误的下标和行内数学写法
- 将 `chapter03.tex` 正文重写为干净的 LaTeX 版本，保留章节结构、主要公式标签和整车运动学 / 速度雅可比推导主线。
- 在 `毕业论文/毕业论文模板/LaTeX/` 下执行：
  - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
  现已可成功生成 `main.pdf`。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `chapter03.tex` 的格式性编译错误已清除，整篇论文恢复可编译状态。
- 当前剩余的编译输出里仍有 2 条非阻塞文献警告：
  - `fang2015survey`
  - `MATSUMURA2017566`
  它们来自 `reference/ref.bib` 缺失条目，不影响 `main.pdf` 生成。

下一步：
- 若需要完全清空编译警告，可继续补齐 `reference/ref.bib` 中缺失的 2 条文献。

## 2026-04-09（论文推导重写）

已完成：
- 根据用户要求，重写 `chapter03.tex` 中“前后模块线速度推导”部分。
- 当前改写方式不再直接给出
  - `${}^{2}\mathbf v_1={}^2\mathbf v_2+{}^2\boldsymbol\omega_2\times{}^2\mathbf p_1+{}^2\dot{\mathbf p}_1`
  - `${}^{2}\mathbf v_3={}^2\mathbf v_2+{}^2\boldsymbol\omega_2\times{}^2\mathbf p_3+{}^2\dot{\mathbf p}_3`
  而是先引入惯性坐标系 `${W}`，从模块参考点绝对位置关系出发，经乘积求导与旋转坐标系速度变换，自然推出牵连项与相对位置导数项。
- 同步保留并复用原有主要公式标签，避免破坏后文引用链。
- 再次执行：
  - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
  编译通过，`main.pdf` 已更新。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 这一段推导现在更适合作为论文正文教学型叙述，能直接回答“为什么会多出 `${}^{2}\dot{\mathbf p}_1` / ${}^{2}\dot{\mathbf p}_3` 这一项”。
- 当前仍只剩 2 条旧的文献缺失警告，不影响 PDF 生成。

下一步：
- 若还要继续打磨 chapter03，可再把这一节中的“牵连速度”“相对运动速度”术语与后文雅可比构造部分统一一下表述。

## 2026-04-09（续）

已完成：
- 按用户要求，继续参照 `/MGDP/legged_gym/legged_gym/envs/base/legged_robot_config.py` 重写共享 trunk：
  - `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
- 当前 trunk 现在明确收口为两个主类：
  - `CompleteCarCfg`
  - `CompleteCarPPoCfg`
- `CompleteCarCfg` 已按更接近 MGDP 的方式补齐并重排根配置树，当前显式包含：
  - `env`
  - `env_init_info`
  - `IMU`
  - `camera`
  - `Radar`
  - `terrain`
  - `commands`
  - `init_state`
  - `control`
  - `asset`
  - `domain_rand`
  - `rewards`
  - `evals`
  - `normalization`
  - `noise`
  - `viewer`
  - `sim`
  - `randomization`
  - `privInfo`
- 同时仍保留 Isaac Lab manager-based 运行层：
  - `scene`
  - `observations`
  - `actions`
  - `events`
  - `terminations`
  - `curriculum`
  - `CompleteCarRLEnv`
- 本轮实际实现方式：
  - `camera` 与 `IMU` 使用 Isaac Lab 原生 sensor cfg 风格
  - `sim / sim.physx / viewer / observation scale / observation noise` 沿用 Isaac Lab 原生配置方式
  - `Radar` 先作为标准保留配置槽位写入 trunk，默认关闭，未直接接入当前 scene manager
  - `commands` 与 `rewards` 采用“用户参数树 + `__post_init__` 生成 manager 运行配置”的方式落地
- 同步调整：
  - `RL_Training/complete_car_rl_training/envs/base/__init__.py`
    - 共享 PPO trunk 导出名改为：
      - `CompleteCarPPoCfg`
  - `RL_Training/complete_car_rl_training/envs/baseline/complete_car_config_baseline.py`
    - 改为主要继承共享配置树并覆写 Stage1 baseline 参数
- 实际执行静态校验：
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/base/__init__.py`
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/baseline/complete_car_config_baseline.py`
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/__init__.py`
  - 语法检查通过

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `RL_Training/complete_car_rl_training/envs/base/__init__.py`
- `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
- `RL_Training/complete_car_rl_training/envs/baseline/complete_car_config_baseline.py`

产出/结论：
- 当前共享 trunk 已不再只是“分块式 manager 配置集合”，而是已经变成“MGDP 风格参数树 + Isaac Lab manager-based 运行层”的统一配置入口。
- 之后如果做 baseline、Stage2、传感器阶段或 privileged 信息阶段，优先继承 `CompleteCarCfg` 并覆写嵌套参数，不应再重新拆一份新的共享骨架。
- 当前共享 PPO 主类名称已经固定为：
  - `CompleteCarPPoCfg`

下一步：
- 在 `env_isaacLab` 中从 `RL_Training/` 目录执行：
  - `python scripts/list_envs.py --keyword Complete-Car`
  - 或 `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --headless --num_envs 100 --max_iterations 10`
  继续做运行态冒烟，确认新 trunk 在真实 Isaac Lab 环境里可正常注册和启动。

## 2026-04-09（再续）

已完成：
- 根据用户进一步澄清的文件职责边界，继续收口 `envs/base/`：
  - `complete_car_config.py` 现在只保留两个顶层主类：
    - `CompleteCarCfg`
    - `CompleteCarPPoCfg`
- 将运行环境类移出到：
  - `RL_Training/complete_car_rl_training/envs/base/complete_car_env.py`
  当前包含：
  - `CompleteCarRLEnv`
- 将 command / reward helper 与 Isaac Lab manager 辅助配置移出到：
  - `RL_Training/complete_car_rl_training/envs/base/manager_helpers.py`
  当前包含：
  - `CompleteCarUniformVelocityCommand`
  - `UniformVelocityCommandCfg`
  - `joint_pos_target_l2`
  - `CompleteCarSceneCfg`
  - `CompleteCarObservationsCfg`
  - `CompleteCarActionsCfg`
  - `CompleteCarEventsCfg`
  - `CompleteCarTerminationsCfg`
  - `CompleteCarCurriculumCfg`
- 当前 `CompleteCarCfg.__post_init__` 的职责已经收口为：
  - 读取嵌套参数树
  - 组装 Isaac Lab manager-based 运行配置
  - 不再在本文件中定义 env runtime 类和独立 helper 函数
- 同步更新：
  - `RL_Training/complete_car_rl_training/envs/base/__init__.py`
    - 改为从新拆分文件导出 `CompleteCarRLEnv` 和 `CompleteCarSceneCfg`
- 实际执行静态校验：
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/base/manager_helpers.py`
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/base/complete_car_env.py`
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/base/__init__.py RL_Training/complete_car_rl_training/envs/baseline/complete_car_config_baseline.py RL_Training/complete_car_rl_training/envs/__init__.py`
  - 语法检查通过

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `RL_Training/complete_car_rl_training/envs/base/__init__.py`
- `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
- `RL_Training/complete_car_rl_training/envs/base/complete_car_env.py`
- `RL_Training/complete_car_rl_training/envs/base/manager_helpers.py`

产出/结论：
- 当前 `complete_car_config.py` 已满足“只保留两个顶层类”的结构边界。
- 当前共享主干已经形成：
  - 参数树文件
  - helper 文件
  - runtime env 文件
  三者分离的结构。
- 之后若继续加 reward / command / env runtime 逻辑，不应再回填到 `complete_car_config.py`。

下一步：
- 在 `env_isaacLab` 中从 `RL_Training/` 目录执行：
  - `python scripts/list_envs.py --keyword Complete-Car`
  - 或 `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --headless --num_envs 100 --max_iterations 10`
  继续确认这次拆分后注册和运行态没有被破坏。

## 2026-04-08

已完成：
- 按用户最新要求进一步重构 `RL_Training/complete_car_rl_training/` 的主包结构。
- 实际调整：
  - 删除顶层历史残留目录：
    - `RL_Training/complete_car_rl_training/agents`
    - `RL_Training/complete_car_rl_training/mdp`
  - 删除 `envs/base/agents/` 与 `envs/base/mdp/`
  - 删除旧共享文件：
    - `envs/base/base_env_cfg.py`
    - `envs/base/scene_cfg.py`
  - 新增并作为共享主干收口到：
    - `envs/base/complete_car_config.py`
- 新共享主干当前集中承载：
  - `CompleteCarCfg`
  - `CompleteCarCfgPPO`
  - `CompleteCarSceneCfg`
  - `CompleteCarRLEnv`
  - 共享 command / observation / action / event / termination / reward helper 逻辑
- 同步修复：
  - `complete_car_rl_training/__init__.py`
  - 新增 `complete_car_rl_training/envs/__init__.py`
  - `envs/baseline/stage1_env_cfg.py`
  - `envs/baseline/stage1_env.py`
  - `envs/baseline/agents/rsl_rl_ppo_cfg.py`
  - 根目录 Isaac Sim 脚本对旧 `common/stage1` 路径的引用
- 根目录 Isaac Sim 脚本当前统一改为从：
  - `complete_car_rl_training.envs.base`
  - `complete_car_rl_training.envs.baseline.stage1_terrain`
  读取机器人配置和地形。
- 实际执行静态校验：
  - 对主包、Stage1 包、训练脚本和 Isaac Sim 相关脚本执行了新的 `py_compile`
  - 语法检查通过

修改文件：
- `README.md`
- `RL_Training/README.md`
- `docs/current_status.md`
- `docs/project_file_map.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `RL_Training/complete_car_rl_training/__init__.py`
- `RL_Training/complete_car_rl_training/envs/__init__.py`
- `RL_Training/complete_car_rl_training/envs/base/__init__.py`
- `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
- `RL_Training/complete_car_rl_training/envs/base/robot_cfg.py`
- `RL_Training/complete_car_rl_training/envs/baseline/stage1_env_cfg.py`
- `RL_Training/complete_car_rl_training/envs/baseline/stage1_env.py`
- `RL_Training/complete_car_rl_training/envs/baseline/agents/rsl_rl_ppo_cfg.py`
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `scripts/isaac_sim/preview_stage1_tile.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `scripts/isaac_sim/control_keyboard.py`

产出/结论：
- 当前 RL 主线已经从“`common/ + stage1/` 两层包结构”进一步收敛到“`envs/base + envs/baseline`”结构。
- 当前共享模板不再分散在多个 base 子文件里，而是统一集中到 `complete_car_config.py`。
- 这次调整的重点不是改变任务语义，而是让后续 Stage2 / Stage3 扩展时继续保持“共享主干明确、阶段特化独立”的组织方式。

下一步：
- 在 `env_isaacLab` 中从 `RL_Training/` 目录执行：
  - `python scripts/list_envs.py --keyword Complete-Car`
  - 或小规模 `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --headless --num_envs 100 --max_iterations 10`
  继续做运行态冒烟确认。

## 2026-04-07

已完成：
- 诊断训练 run `2026-04-07_19-42-44`，并整理相对上一轮 `2026-04-07_15-57-27` 的参数变化。
- 实际检查：
  - `/tmp/isaaclab/logs/isaaclab_2026-04-07_19-42-44.log`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_19-42-44/params/env.yaml`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_19-42-44/params/agent.yaml`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_19-42-44/tensorboard_export/summary.json`
  - 与 `2026-04-07_15-57-27` 的 `env.yaml / agent.yaml` 做 diff
- 关键参数变化：
  - `agent.max_iterations: 600 -> 500`
  - `reset_base.velocity_range`
    - `x/y/z/roll/pitch/yaw` 全部改为 `0`
  - `base_velocity` 新增曲率耦合命令：
    - `curvature_range = (-0.5, 0.5)`
    - `turn_lin_vel_threshold = 0.1`
- 关键结果：
  - `Train/mean_episode_length = 960.0`
  - `Episode_Termination/time_out = 1.0`
  - `bad_orientation = 0.0`
  - `ball_joint_out_of_bounds = 0.0`
  - `mean_reward: 48.14 -> 50.92`
  - `error_vel_xy: 0.616 -> 0.613`
  - `error_vel_yaw: 0.676 -> 0.542`
  - `root_height_mean: 0.111 -> 0.139`
  - `root_height_min: 0.051 -> 0.111`
- 结论：
  - 这次 run 继续保持完全健康 rollout，并且 yaw tracking 明显优于 `15-57-27`。
  - 取消初始 root velocity 扰动和引入速度-曲率耦合命令，没有把训练带坏，反而带来了更平衡的 tracking。
  - 但 root frame 仍然偏低，只能说“比上一轮更好”，还不能说“车身高度问题已经解决”。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `2026-04-07_19-42-44` 目前是当日这条基线上的更优参考 run。

下一步：
- 如果继续调参，优先围绕“如何在不破坏当前 tracking 的前提下，进一步改善 root frame 过低”的问题展开。

已完成：
- 按用户要求将 Stage1 车轮动作空间从“3 个车桥轮速”改回“6 个车轮独立轮速”。
- 实际修改：
  - 删除本轮新增的 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/actions.py`
  - 修改 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py`
    - 恢复导出 `JointVelocityActionCfg`
  - 修改 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - `wheel_joint_vel` 改回 6 个轮关节独立 `JointVelocityActionCfg`
  - 修改 `README.md`
    - 恢复 Stage1 baseline 描述为 `6 球铰 + 6 轮速`
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- 结果：
  - 当前动作空间已恢复到先前版本
  - 总动作维度重新回到 `12`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `README.md`

产出/结论：
- 当前 Stage1 baseline 仍按“6 个球铰 + 6 个车轮独立速度”解释。

下一步：
- 若后续还要讨论左右轮是否应耦合，需把它作为新的任务定义变更重新评估，而不是保留两套动作语义并存。

已完成：
- 按用户要求修改 Stage1 `base_velocity` 命令采样逻辑，改为“线速度 + 曲率”生成 yaw 命令。
- 实际修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/commands.py`
    - 为本地 `CompleteCarUniformVelocityCommand` 增加曲率采样分支
    - 当配置了 `curvature_range` 时：
      - 先采样 `lin_vel_x`
      - 再采样 `curvature`
      - 令 `yaw_vel = lin_vel_x * curvature`
      - 若 `|lin_vel_x| < turn_lin_vel_threshold`，则强制 `yaw_vel = 0`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - 当前默认设置为：
      - `curvature_range = (-0.5, 0.5)`
      - `turn_lin_vel_threshold = 0.1`
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/commands.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- 结果：
  - 当前 yaw command 已不再独立于前进速度采样
  - 当前命令语义更接近车辆“速度 + 曲率”的控制方式

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/commands.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 从当前版本开始，Stage1 训练结果中的 yaw tracking 需要按“速度耦合转向命令”解释，不能再直接与旧的独立 `ang_vel_z` 采样 run 混为一类。

下一步：
- 重新训练一轮，再比较新的 command 分布对线速度/yaw 跟踪平衡是否有改善。

已完成：
- 按用户要求修改 Stage1 动作空间，取消 6 个车轮完全独立的轮速控制，改为 3 个车桥轮速自由度。
- 实际修改：
  - 新增 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/actions.py`
    - 实现 `CoupledWheelVelocityAction`
    - 将每个车桥的 1 个动作映射到左右两个轮关节的相同速度目标
  - 修改 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py`
    - 导出 `CoupledWheelVelocityActionCfg`
  - 修改 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - 用 `wheel_groups` 替代原 6 轮独立 `JointVelocityActionCfg`
    - 当前轮速动作顺序为：
      - body axle
      - head axle
      - tail axle
  - 修改 `README.md`
    - 同步 Stage1 baseline 描述为 `6 球铰 + 3 车桥轮速`
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/actions.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- 结果：
  - 当前策略不再能给同一车桥左右轮下相反方向的速度命令
  - 动作总维度从 `12` 变为 `9`
  - 观测中的 `wheel_joint_vel_rel` 仍保留 6 维，便于继续观察左右轮实际执行差异

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/actions.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `README.md`

产出/结论：
- 当前 Stage1 baseline 的车轮控制语义已经变成“按车桥控制”，更符合车辆实际约束。

下一步：
- 用训练启动命令重新跑一次，确认新的 9 维动作空间下 rollout 是否稳定，以及 yaw/线速度 tracking 是否受明显影响。

已完成：
- 诊断训练 run `2026-04-07_15-57-27`，确认移除 `root_too_low` 后 rollout 已恢复为正常走满。
- 实际检查：
  - `/tmp/isaaclab/logs/isaaclab_2026-04-07_15-57-27.log`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-57-27/params/env.yaml`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-57-27/params/agent.yaml`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-57-27/tensorboard_export/summary.json`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-57-27/tensorboard_export/scalars/*.csv`
- 关键结论：
  - `Train/mean_episode_length = 960.0`
  - `Episode_Termination/time_out = 1.0`
  - `Episode_Termination/bad_orientation = 0.0`
  - `Episode_Termination/ball_joint_out_of_bounds = 0.0`
  - `error_vel_xy ≈ 0.62`
  - `error_vel_yaw ≈ 0.68`
  - 说明去掉 `root_too_low` 后，训练已从上一轮“几乎全部早死”的坏状态恢复到完整 episode 存活，并且速度跟踪已正常学起来。
  - 同时根高度日志显示：
    - `root_height_mean` 最近 20 点均值约 `0.132`
    - `root_height_min` 最近 20 点均值约 `0.090`，最小下探到约 `0.017`
  - 因而当前结论是：
    - 上一轮 `2026-04-07_15-29-34` 的主因确实是 `root_too_low`
    - 但移除高度终止后，当前策略会允许 root frame 处在很低的位置，后续若要约束离地间隙，应重新设计更物理的信号，而不是恢复原绝对阈值

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `2026-04-07_15-57-27` 是当前用户这组激进 reward/PPO 配置下第一轮恢复到健康 rollout 的 run。

下一步：
- 继续用回放确认：
  - 小车是否真实稳定跟踪，而不是靠很低的 root frame 姿态“贴地生存”
  - 若确实存在长期低车身姿态，后续应考虑改为更有物理意义的 clearance/relative-height 约束

已完成：
- 按用户决定从当前 Stage1 baseline 中移除 `root_too_low` termination。
- 实际修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - 删除 `TerminationsCfg.root_too_low`
- 保留不变：
  - `root_height_mean / root_height_min` 两个训练日志指标继续输出
  - 其余 termination 保留为：
    - `time_out`
    - `bad_orientation`
    - `ball_joint_out_of_bounds`
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前简单 Stage1 baseline 已不再使用 `root_too_low` 作为硬终止条件，避免尚未标定清楚的 root link 高度阈值直接主导训练结果。

下一步：
- 用相同训练命令重新跑一轮，重点看：
  - `time_out`
  - `bad_orientation`
  - `ball_joint_out_of_bounds`
  - `root_height_mean / root_height_min`
  是否出现更合理的 rollout 行为。

已完成：
- 诊断训练 run `2026-04-07_15-29-34` 的失败原因，并结合新加入的 root 高度日志确认本轮主问题不是启动或 PPO 数值崩溃，而是 `root_too_low` 终止几乎完全主导 rollout。
- 实际检查：
  - `/tmp/isaaclab/logs/isaaclab_2026-04-07_15-29-34.log`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-29-34/params/env.yaml`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-29-34/params/agent.yaml`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-29-34/tensorboard_export/summary.json`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-29-34/tensorboard_export/scalars/*.csv`
- 关键结论：
  - 本轮训练已正常完成到 `model_999.pt`，不是启动失败。
  - 尾段指标显示：
    - `Episode_Termination/root_too_low = 1.0`
    - `Episode_Termination/time_out = 0.0`
    - `Train/mean_episode_length ≈ 10.57`
    - `Metrics/base_velocity/root_height_mean ≈ 0.242`
    - `Metrics/base_velocity/root_height_min ≈ 0.164`
  - 当前 `root_too_low.minimum_height = 0.15` 与 root link 实际高度工作带贴得过近，只剩约 `1.4 cm` 裕量；结合该终止项使用的是瞬时 root link 高度而非 COM，高度阈值 `0.15` 很可能就是本轮 rollout 被卡死的直接主因之一。
  - 同时也确认这轮实验并非只改了高度阈值，还叠加了更强的姿态/速度/球铰惩罚、更严格的 `45°` 姿态终止以及更激进的 PPO 配置，因此后续若要验证高度阈值，需要做单变量对比。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前对 `2026-04-07_15-29-34` 的最稳妥判断是：该 run 的主导失败模式是 `root_too_low`，而 `minimum_height = 0.15` 对当前 root link frame 很可能过高。

下一步：
- 若要验证这一判断，应只改 `root_too_low.minimum_height` 一项，再做新一轮对比训练。

已完成：
- 按用户在 Isaac Sim 地图预览中手动调整得到的新视角，更新 active task 默认 viewer 相机位姿。
- 已修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - `self.viewer.eye` 改为 `(-53.885, 43.696, 64.903)`
    - 新增 `self.viewer.lookat = (-53.054, 43.698, 64.346)`
- 已执行静态校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active task 在 GUI 下默认会从用户挑选后的地图总览视角打开，不再沿用原先的近距离默认视角。

下一步：
- 若还要继续调视角，可重复读取 `/OmniverseKit_Persp` 的 `eye/lookat` 后直接覆盖当前配置。

已完成：
- 按用户要求移除阶段 1 active task 中的底盘碰撞奖励，原因是当前真实小车默认不具备与该仿真 reward 对应的底盘接触传感输入。
- 已修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - 删除 `body_chassis_contact / head_chassis_contact / tail_chassis_contact` 三个 `ContactSensorCfg`
    - 删除 `RewardsCfg.chassis_collision`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`
    - 删除本地 `chassis_collision(...)` helper 与对应导出项
- 已执行静态校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前阶段 1 baseline 的 reward 集合已不再包含底盘碰撞项。
- 先前的底盘碰撞逻辑本质上是在用仿真 contact sensor 检测三个 chassis 与地面或其他物体的接触力是否超过阈值，主要约束的是“底盘擦地/砸地/撞障碍”这类行为，而不是轮地正常接触。
- 当前 active task 不再依赖这类仿真专用信号。

下一步：
- 重新做一次训练冒烟，重点观察移除底盘碰撞项后 episode 稳定性、姿态惩罚和终止项是否足够约束坏行为。

## 2026-04-06

已完成：
- 按用户要求将完整车训练项目中的仓库路径逻辑收敛为统一入口。
- 实际修改：
  - 新增 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/paths.py`
    - 统一提供 `PROJECT_ROOT`、`USD_DIR`、`RESULTS_DIR`、`COMPLETE_CAR_USD`
  - 修改 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - 不再本地拼接 `_THIS_FILE / _PROJECT_ROOT / _COMPLETE_CAR_USD`
    - 改为直接导入 `COMPLETE_CAR_USD`
  - 修改 `src/rl_lab/complete_car_rl_training/tools/ik/test_ik_keyboard.py`
    - 不再单独向上查找 `AGENTS.md`
    - 改为复用统一的 `COMPLETE_CAR_USD` 与 `RESULTS_DIR`
- 实际执行校验：
  - `rg -n "_THIS_FILE|PROJECT_ROOT = next\\(|AGENTS.md\\)\\.exists\\(" src/rl_lab/complete_car_rl_training -S`
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/paths.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py src/rl_lab/complete_car_rl_training/tools/ik/test_ik_keyboard.py`
- 结果：
  - 当前活跃训练项目中的路径逻辑已集中到一个模块维护
  - `complete_car_env_cfg.py` 与 IK 工具脚本不再重复各自写仓库根目录探测
  - 静态编译通过
  - 上述 `rg` 返回空结果，说明当前 `src/rl_lab/complete_car_rl_training/` 下已没有遗留的分散根目录探测写法

已完成：
- 按用户要求将训练环境 `stage1` 地形颜色进一步改为纯黑色。
- 实际修改：
  - `complete_car_stage1_terrain_env.py`
    - `STAGE1_TERRAIN_DIFFUSE_COLOR: (0.10, 0.10, 0.10) -> (0.0, 0.0, 0.0)`
- 保持不变：
  - 地形 mesh 几何
  - physics material
  - reset / curriculum / reward / observation / action 逻辑
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`

已完成：
- 按用户要求更新仓库级代码讲解规则，修改：
  - `AGENTS.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 已固化的新规则：
  - 以后讲解代码时默认不写完整绝对路径
  - 优先先讲脚本整体结构
  - 再按 import / 常量 / 类 / 函数 / 引用关系逐段、逐行分析
  - 默认按“用户 Python 基础较弱”的教学口径解释配置对象、函数引用与数据流
- 结果：
  - 后续会话中的代码教学风格已统一，不再重复口头约定

已完成：
- 按用户确认结果，进一步把“代码讲解的节奏、层次和内容把握方式”固化到仓库规则。
- 实际修改：
  - `AGENTS.md`
    - 新增“Preferred teaching rhythm for code walkthroughs”
    - 明确要求以后默认按以下顺序讲解：
      - 先说明脚本在系统中的角色
      - 再讲整体结构
      - 再按源码顺序逐块展开
      - 每块先讲作用，再讲关键代码行
      - 明确区分“引用/注册”和“真正执行逻辑”
      - 每个大块结束后重新接回 RL 主线
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 结果：
  - 用户认可的这套教学节奏已经从临时口头反馈升级为仓库级默认讲解规范

已完成：
- 按用户要求继续将训练环境 `stage1` 地形颜色调深，改为更偏黑的黑灰色，以提高和周围环境的对比度。
- 实际修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
    - `STAGE1_TERRAIN_DIFFUSE_COLOR: (0.18, 0.18, 0.18) -> (0.10, 0.10, 0.10)`
- 保持不变：
  - 地形 mesh 几何
  - physics material
  - reset / curriculum / reward / observation / action 逻辑
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`

已完成：
- 按用户要求将训练脚本与键盘控制脚本的默认运行语义统一到 GPU。
- 实际修改：
  - `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`
    - 未显式传 `--device` 时默认改为 `cuda:0`
  - `scripts/isaac_sim/control_keyboard.py`
    - `--help` 说明中明确写成默认走 Isaac Sim 的 GPU 路径
  - `src/rl_lab/complete_car_rl_training/docs/training_workflow_and_tensorboard_guide.md`
    - 默认训练命令、冒烟命令、回放命令统一改为 GPU 版
    - 键盘控制章节补充“默认走 GPU，不提供单独 CPU 模式”
  - `docs/current_status.md`
  - `docs/conversation_history.md`
- 实际执行校验：
  - `python src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py --help`
  - `python scripts/isaac_sim/control_keyboard.py --help`
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`
  - `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`
- 结果：
  - 当前仓库默认训练入口已切到 `cuda:0`
  - `control_keyboard.py` 的帮助信息已与 GPU 默认语义保持一致
- 额外说明：
  - 这次修改统一的是仓库默认行为，不代表当前机器的 NVIDIA driver / CUDA 环境已经恢复；本机若无可用 GPU，实际运行仍会受环境阻塞

已完成：
- 按用户要求修复 `scripts/isaac_sim/control_keyboard.py` 当前“无法打开”的仓库级问题。
- 排查结论：
  - `--terrain stage1` 使用的 `stage1_terrain.py` 本地路径写错，导致脚本走到对应分支时无法加载训练同源地形模块。
  - 脚本里同时还暴露了 `gap / stage2 / both` 等旧地形选项，但这些路径依赖的 `scripts/isaac_sim/terrain_preview/` 源码当前不在工作区中，已不属于可靠入口。
- 实际修改：
  - 修正 `scripts/isaac_sim/control_keyboard.py` 中 `STAGE1_TERRAIN_PATH`
  - 将 `--terrain` 选项收窄为 `none / stage1`
  - 默认地形改为 `none`
  - 删除对缺失 `terrain_preview` 模块的旧分支依赖
  - 同步更新 `src/rl_lab/complete_car_rl_training/docs/training_workflow_and_tensorboard_guide.md`、`docs/current_status.md`、`docs/conversation_history.md`
- 实际执行校验：
  - `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`
  - `python scripts/isaac_sim/control_keyboard.py --help`
  - `timeout 90s python -u scripts/isaac_sim/control_keyboard.py --terrain stage1 --headless --frames 1`
- 结果：
  - 脚本级过期路径和缺失模块问题已修复，当前文档与项目记忆也已统一到 `none / stage1` 这组真实支持范围。
  - 本机 headless smoke run 已能完成到 `Headless smoke validation finished successfully.`，说明 `stage1` 导入、机器人初始化、共享摩擦材质绑定与训练同构控制参数应用都能走通。
- 额外说明：
  - 当前这台机器仍无可用 NVIDIA driver / GPU，因此 Isaac Sim 交互窗口是否能真正弹出仍受运行环境限制；这部分不再属于本轮脚本代码错误。

已完成：
- 按用户要求新增训练操作说明文档：
  - `src/rl_lab/complete_car_rl_training/docs/training_workflow_and_tensorboard_guide.md`
- 文档已覆盖：
  - 训练脚本启动指令
  - TensorBoard 查看指令
  - 策略回放指令
  - 键盘控制脚本指令
  - 地形查看脚本指令
  - 本地结果保存位置
  - 核心 TensorBoard 图表的横纵轴、含义与好坏判断
- 已核对 `train.py --help`、`play.py --help`、`control_keyboard.py --help`，并修复 `preview_stage1_tile.py` 与 `preview_stage1_last_six.py` 中过期的 `stage1_terrain.py` 路径，使文档中的地形查看命令恢复可用。
- 修复 `env_isaacLab` 中 `tensorboard` 无法启动的问题。
- 现象：
  - 执行 `tensorboard --logdir ...` 时在 `tensorboard/default.py` 导入 `pkg_resources` 处报错
  - 当前环境中 `setuptools==82.0.1` 可导入 `setuptools`，但已无 `pkg_resources`
- 排查后确认：
  - 本机 conda 缓存已存在 `setuptools-80.10.2-py311h06a4308_0.conda`
  - 离线回退后 `pkg_resources` 恢复，`tensorboard --version` 可正常输出 `2.20.0`
- 实际执行：
  - `conda install -n env_isaacLab --offline -y /home/ubuntu/miniconda3/pkgs/setuptools-80.10.2-py311h06a4308_0.conda`
  - `tensorboard --version`
- 按用户要求将训练环境 `stage1` 地形显示颜色调整为黑灰色。
- 修改 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`：
  - 为 `create_prim_from_mesh("/World/terrain/stage1", ...)` 增加显式视觉材质
  - 使用 `sim_utils.PreviewSurfaceCfg(diffuse_color=(0.18, 0.18, 0.18))`
- 保持原有 physics material、地形 mesh 几何、reset 和 curriculum 逻辑不变。
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
- 按用户要求清理 `src/` 训练脚本中的 `mgdp` 风格函数命名，重点处理：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1_terrain.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_env.py`
- 将地形 helper 和 mesh 偏移 helper 改为中性命名，并同步修正全部本地调用关系，例如：
  - `_mgdp_random_uniform_terrain -> _random_uniform_terrain`
  - `_maybe_add_mgdp_roughness -> _maybe_add_roughness`
  - `_offset_mesh_to_mgdp_frame -> _offset_mesh_to_stage1_frame`
- 本轮只改函数标识符，不改 terrain 生成逻辑、参数、课程分配或训练行为。
- 实际执行校验：
  - `rg -n "def .*mgdp|class .*mgdp|_mgdp|mgdp_" src`
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1_terrain.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_env.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/docs/training_workflow_and_tensorboard_guide.md`
- `scripts/isaac_sim/preview_stage1_tile.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1_terrain.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `src/` 活跃训练代码路径下，函数命名已去掉 `mgdp` 关联前缀。
- 本轮属于命名清理，不涉及行为变更；静态编译通过，且再次搜索未发现 `src/` 中残留的 `mgdp` 风格函数名。

下一步：
- 若还要继续统一命名风格，可再单独清理 `src/` 之外脚本目录中的 `mgdp` 文件名或注释，但这不属于本轮已执行范围。

已完成：
- 按用户要求整理 `stage1_terrain.py` 的代码结构，把公共 `make_*_tile` 地形生成函数整理成连续区块，并按 `terrain_dict` 中的地形顺序重新排列：
  - `flat`
  - `slope down`
  - `slope up`
  - `uneven rough`
  - `stairs down`
  - `stairs up`
  - `discrete obstacles`
  - `hurdle`
  - `gap`
  - `ramp`
  - `beam`
  - `new stairs down`
  - `pit`
- 为了让代码顺序和地形顺序一一对应，补了几个轻量包装函数：
  - `make_slope_down_tile`
  - `make_slope_up_tile`
  - `make_new_stairs_down_tile`
- 保持已有核心函数名不变，例如：
  - `make_pyramid_tile` 仍对应 `uneven rough`
  - `make_stairs_tile` 仍作为 `stairs down / stairs up / new stairs down` 的共享实现
- 顺手清理了同文件里几处格式不整齐的问题，但未改地形生成语义。
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1_terrain.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1_terrain.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `stage1_terrain.py` 的公共地形生成函数阅读顺序已和配置顺序一致，后续查阅和维护会更直接。
- 本轮只做结构整理与可读性优化，不涉及课程分配、地形权重或 mesh 生成逻辑变化。

下一步：
- 若还要继续收敛结构，可再把 `make_tile_by_name` 改成显式的生成器注册表，但这属于后续重构，不是本轮已执行内容。

## 2026-04-03

已完成：
- 针对用户提出的“训练时为什么像加载了好几张地图”，重新检查当前 RL 任务的真实地形导入链路：
  - `Complete-Car-Rl-Training-v0`
  - `complete_car_stage1_env.py`
  - `complete_car_rl_training_env_cfg.py`
  - `stage1_terrain.py`
- 代码层确认当前训练环境的地形导入逻辑为：
  - 先删除 `TerrainImporterCfg(terrain_type="plane")` 自动生成的默认 plane
  - 再把整张 `stage1` 高度图转换得到的单个 trimesh 通过 `import_mesh("stage1", ...)` 只导入一次
  - 再通过 `configure_env_origins(...)` 给不同并行环境分配出生点
- 直接用纯 Python 方式复核 `stage1_terrain.py` 的数据规模，确认当前训练地形生成结果是单张完整大地图，而不是按 env 拆成多张：
  - `height_field_raw.shape == (2100, 1300)`
  - `env_origins.shape == (20, 10, 3)`
  - `vertices.shape == (2730000, 3)`
  - `faces.shape == (5453202, 3)`
  - `terrain_type_unique == [0, 1, 2, 3, 4]`
- 新增训练环境 stage 导出脚本：
  - `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
  - 用途是直接实例化真实训练任务，并尝试把 live RL stage 保存成 USD，同时导出 prim tree 文本
- 根据用户后续提供的 `isaaclab_2026-04-03_11-39-39.log` 与配套 `kit_20260403_113931.log` 继续排查：
  - 日志显示当前启动的是 `export_training_stage.py`，不是 `scripts/rsl_rl/train.py`
  - `Complete-Car-Rl-Training-v0` 的环境构建实际上已经成功完成，机器人 articulation、动作项和观测项都已初始化
  - Kit 日志末尾为 `SimulationApp.close` 正常关闭，没有出现任务包自身的 Python traceback
- 进一步确认这次调用里 `--save-usd` 传入的是目录 `/home/ubuntu/Graduation-Project/results/`，不是具体 USD 文件名。
- 已修改 `export_training_stage.py`：
  - 若 `--save-usd` 是已存在目录，立即抛出清晰 `ValueError`
  - 若 `--save-usd` 不以 `.usd` 或 `.usda` 结尾，也立即报错
- 已执行 `python3 -m py_compile src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`，静态检查通过。
- 在用户随后成功导出 `results/training_stage_num_envs10.usda` 后，直接检查导出的 prim tree：
  - `/World/terrain` 下只有 1 张真实训练地形：
    - `/World/terrain/stage1/mesh`
  - 但每个 `/World/envs/env_i/Robot` 下都存在：
    - `terrain_preview/mix/terrain_surface`
    - `terrain_preview/mix/tile_base`
  - 因而“像有好几张地图”的直接来源不是训练 terrain importer 重复导入多张 `stage1`，而是机器人资产里残留的 preview 地形被每个并行环境复制。
- 按用户要求新增 `scripts/isaac_sim/remove_complete_car_terrain_preview.py`，并对 `USD/complete_car.usd` 执行清理：
  - 自动创建备份 `USD/complete_car.usd.terrain_preview_cleanup.bak`
  - 删除 `/World/terrain_preview` 子树
- 删除后重新打开 `USD/complete_car.usd` 验证：
  - `/World/terrain_preview` 已返回 `IsValid() == False`
  - 当前顶层 prim 只剩 `/World`、`/Render`、`/physicsScene`
- 实际在本机执行：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
  - `python -u scripts/export_training_stage.py --task Complete-Car-Rl-Training-v0 --num_envs 10 --steps 0 --headless --device cpu --save-usd ...`
- 实测结果：
  - 脚本可以进入 Isaac Lab scene creation
  - 但在当前无 NVIDIA driver / 无可用 CUDA 的环境里，进程会在 `gym.make(...)` 场景创建完成后提前退出，没有继续走到脚本自己的 `env.reset()` 与 `save_stage()` 逻辑
  - 因此本轮未能在本机生成真实训练环境的 stage USD 文件

修改文件：
- `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
- `scripts/isaac_sim/remove_complete_car_terrain_preview.py`
- `USD/complete_car.usd`

已完成：
- 新建根目录 `FK_iteration.m`，按用户给出的 Agile Eye 论文口径整理正运动学符号推导脚本。
- 在脚本中明确建立零位姿基座坐标系与平台坐标系，写入：
  - `u1,u2,u3`
  - `v1',v2',v3'`
  - `R = Rz(phi) * Ry(theta) * Rx(psi)`
  - `v_i` 展开式
  - `w_i` 表达式
  - `w_i^T v_i = 0` 三条标量约束
- 在脚本中继续补齐 forward kinematics 的两个分支推导：
  - `cos(theta)=0` 的 trivial branch
  - `phi=theta3` 的 nontrivial branch
  - `p1..p4`、行列式消元、`q1,q2`、`theta/psi` 主值解表达式
- 修正并显式说明第二条支链约束的符号问题：保留 `w2^T v2` 原始展开式，同时保留论文把方程两边同乘 `-1` 后得到的式(9c)写法，避免后续误判为推导错误。
- 用 `sympy` 对脚本对应的公式做了交叉核对，确认 `v_i` 展开、式(9b)(9c)(9d)、分支代回和式(17) 的等价关系都成立。
- 更新 `docs/current_status.md`、`docs/conversation_history.md`、`logs/daily_work_log.md` 与根 `README.md`，把这次正运动学推导脚本和关键结论写入项目记忆。

修改文件：
- `FK_iteration.m`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前训练代码路径本身并没有“按并行环境复制多张完整 stage1 地图”的显式逻辑；它导入的是 1 张全局 `stage1` mesh，再给各 env 分配不同 origin。
- 用户这次提供的日志并不支持“训练环境没拉起来”这个判断；从日志看，环境已经创建成功，关闭点更接近导出脚本参数或脚本执行流程，而不是任务配置本身崩溃。
- 本次最明确的问题是 `--save-usd` 目标写成了目录，后续必须改成具体文件名。
- 当前已经确认并修复：训练导出中每个 `env_i/Robot` 下反复出现的假地形来自 `complete_car.usd` 的 `/World/terrain_preview` 残留，而不是训练 terrain importer 自己重复导入多张 stage1 地图。
- 若窗口里看起来像有多张地图，后续应优先从：
  - `/World/terrain` 下是否存在多个 terrain prim
  - `/World/envs/env_*` 的多环境复制
  - 默认 plane / debug 可视化
  这三类来源排查，而不是先假设 `stage1_terrain.py` 生成了多张地图。
- 当前仓库已经有可复用的训练 stage 导出脚本，但真正导出 live RL stage 仍需放到有正常 GPU/驱动的 Isaac Lab 会话中执行。

下一步：
- 在可正常使用 `cuda:0` 的 Isaac Lab 环境中重新导出一次 `training_stage_num_envs10.usda`，确认每个 `env_i/Robot` 下已不再出现 `terrain_preview` 子树；若仍有异常，再继续排查 `PhysicsScene`、远端传感器引用和训练场景自身的多环境可视化。

产出/结论：
- 当前仓库已不再只有逆运动学推导工作区，根目录同时具备一份可直接查看的 Agile Eye 正运动学符号推导脚本。
- 正运动学脚本当前已经覆盖论文中从坐标系建立、向量约束、分支切分到非平凡解消元的主干推导。
- 第二条约束和论文式(9c)之间的差异仅是整体乘 `-1` 的等价变形，不属于模型或代码错误。
- 本轮尝试用本机 `matlab -batch` 做命令行验证，但当前终端里即使最小 `disp('hi')` 也会空退出且返回码为 `1`；因此本轮有效验证依据是 `sympy` 的符号等价检查，而不是 MATLAB 命令行输出。

下一步：
- 若用户继续推进，可把 `FK_iteration.m` 中已经固化的符号结果同步整理进论文 `chapter03.tex` 的“正运动学模型”小节，或继续补 rotation matrix 形式的 trivial solutions 输出。

## 2026-04-02

已完成：
- 按用户要求实际执行 `preview_stage1_terrain.py`，尝试在当前机器上通过 `--headless --device cpu --frames 1 --save-usd` 导出 preview stage 的 USD 文件，并额外保存完整日志到：
  - `results/preview_save.log`
  - `results/preview_save_unbuffered.log`
- 结果确认：
  - 当前 Isaac Sim 会话能启动到 headless 模式
  - 但在这台无可用 CUDA / 无图形显示环境中，`--save-usd` 仍未实际生成 `results/stage1_preview.usda`
- 直接读取 `USD/complete_car.usd`，导出 prim 树到：
  - `results/complete_car_usd_tree.txt`
- 基于导出的 prim 树确认 `complete_car.usd` 的主要结构：
  - `/World/complete_car_alternative` 为机器人主根
  - 机体/轮子/SPM 机构普遍采用 `visuals + collisions` 双子树
  - `/World/complete_car_alternative/joints` 下集中存放轮子与两组等效球铰相关 `PhysicsRevoluteJoint/PhysicsFixedJoint`
  - 传感器包括 `Imu_Sensor`、双目相机和 `Example_Rotary`
  - 文件末尾仍存在顶层 `/physicsScene`
- 再次通过文件级导入检查 `stage1_terrain.py` 的 `env_origins`：
  - `shape == (20, 10, 3)`，说明逻辑上 20x10 共 200 个 tile 坐标系都已生成
  - `x` 范围为 `4.0 ~ 156.0`
  - `y` 范围为 `4.0 ~ 76.0`
  - 左上角 tile 原点为 `(4, 4, z)`，右下角 tile 原点为 `(156, 76, z)`
- 同时核对 Isaac Lab `TerrainImporter` 源码，确认 `scene.terrain.set_debug_vis(True)` 会在 `/Visuals/TerrainOrigin` 下创建 `VisualizationMarkers`，其本质是 `UsdGeom.PointInstancer`，并将 `env_origins.reshape(-1, 3)` 全部可视化，而不是为每个 tile 手工创建一个独立 Xform。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已经实际验证：preview 导出 USD 文件这一步在本机 headless/CPU 环境里不可靠，不能再默认认为 `--save-usd` 一定会落盘。
- 当前可以明确解释：
  - live preview stage 的主要组成来自 `preview_stage1_terrain.py` 场景配置和 `TerrainImporter`
  - 机器人本体资产的内部 prim 结构可直接参考 `results/complete_car_usd_tree.txt`
  - tile 坐标系逻辑上并不缺列；若窗口里仍看到左侧坐标系缺失，应优先继续从 live stage 对齐或可视化层排查，而不是回到 `env_origins` 生成逻辑

下一步：
- 若用户还要继续精确核对 live preview stage，下一步应优先在可用 GUI 的 Isaac Sim 会话里导出 USD，或直接写一个专门的 stage-tree dump 脚本，绕开当前 `save_stage` 不落盘的问题。

已完成：
- 根据用户补充的窗口观察现象，继续定位 `stage1` 预览中的场景错位问题：用户反馈为“两个相同大地图堆叠、tile 坐标系从右边开始、左边两列没有坐标系”。
- 复核后确认：
  - `preview_stage1_terrain.py` 与 `stage1_terrain.py` 在地形生成参数层本身一致
  - 剩余问题来自 `MGDP` 原版 mesh 放置规则未完整迁移：本地 `env_origins` 按无 border 的 tile 中心计算，但导入 mesh 若不整体减去 `border_size`，会比 marker 网格整体偏右/偏上约 `25 m`
- 将 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py` 补齐与 preview 相同的 mesh 坐标修正：
  - 新增 `_offset_mesh_to_mgdp_frame(...)`
  - 在 `import_mesh("stage1", ...)` 前先把整张 trimesh 的 `x/y` 顶点整体减去 `border_size`
- 继续保留 scene 层默认 plane 清理逻辑，形成最终一致规则：
  - 删默认 plane
  - stage1 mesh 减去 `border_size`
  - 再配置 `env_origins`
- 实际验证：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
  - `python3 -m py_compile scripts/isaac_sim/preview_stage1_terrain.py`
  - `python scripts/isaac_sim/preview_stage1_terrain.py --headless --frames 1`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `preview` 与训练环境在 stage1 场景放置层已经一致，都按 `MGDP` 规则处理了默认 plane 和 `border_size` 坐标偏移。
- 用户在窗口里看到的“左边没坐标系、坐标系从右边开始”现象，已被固化为 mesh/world frame 对齐问题，不应再误判为 preview 和 generator 使用了不同参数。

下一步：
- 直接在 Isaac Sim 窗口里重新打开 `preview_stage1_terrain.py`，优先人工确认是否还存在第二张大地图和左侧 marker 缺失。

已完成：
- 根据用户要求，继续把本项目 `stage1_terrain.py` 与 MGDP 原始 stage1 地形生成代码逐项对齐，重点核对：
  - `/home/ubuntu/MGDP/legged_gym/models/MGDP/stage1/001/random_dog_config_stage1.py`
  - `/home/ubuntu/MGDP/legged_gym/legged_gym/utils/terrain.py`
  - `/home/ubuntu/MGDP/legged_gym/legged_gym/utils/new_terrains/add_mix_terrain.py`
  - `/home/ubuntu/MGDP/isaacgym/python/isaacgym/terrain_utils.py`
- 重写 `src/rl_lab/complete_car_rl_training/.../stage1_terrain.py` 中的主要单块地形生成语义，使其更接近 MGDP 原版：
  - `slope down` 改为 MGDP `pyramid_sloped_terrain`
  - `pyramid` 改为 MGDP `pyramid_sloped_terrain + random_uniform_terrain`
  - `stairs down / stairs up / new stairs down` 改为 MGDP `pyramid_stairs_terrain`
  - `discrete obstacles` 改为 MGDP `discrete_obstacles_terrain`
  - `hurdle / gap / ramp / beam / pit` 改为 MGDP `add_mix_terrain.py` 对应语义
- 将 `env_origin` 计算改回 MGDP `mix` 的中心 `2m x 2m` patch 规则，不再对 `gap/pit/hurdle/beam` 单独做出生点偏移特判。
- 保留并确认 `preview_stage1_terrain.py` 与 `CompleteCarStage1Env` 中默认 plane 清理逻辑，从 scene 层避免 ground plane 与自定义 stage1 mesh 叠加。
- 实际验证：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`
  - 通过文件级导入直接执行 `build_stage1_terrain_data()`
  - `python scripts/isaac_sim/preview_stage1_terrain.py --headless --frames 1`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `preview_stage1_terrain.py` 和 `stage1_terrain.py` 在“地形生成参数与 mesh 来源”层是一致的：preview 直接调用 `Stage1TerrainCfg + build_stage1_terrain_data()`，不存在两套独立地形参数。
- 当前“地形交叠 + 额外 ground”问题已经确认并修复为 scene 导入问题，而不是 `stage1_terrain.py` 和 preview 参数不一致。
- 当前 `stage1_terrain.py` 虽已显著向 MGDP 原版收敛，但由于 `terrain_dict` 权重和 `num_cols = 10` 的组合仍未覆盖全部 terrain index，默认课程地图实际仍只会出现前 5 类地形。

下一步：
- 若要让预览图中真的看到 `gap / ramp / beam / pit` 等后半段 terrain，需要继续调整列分配逻辑或 `terrain_dict` 权重，而不是再去排查 preview 和 stage1 代码是否使用了不同参数。

已完成：
- 核对本项目 `stage1_terrain.py` 与 MGDP 原始 stage1 地形代码，定位 `terrain_dict / terrain_proportions / choice=j/num_cols+0.001 / heightfield->trimesh` 主体逻辑来源。
- 确认当前 Isaac Sim 中“stage1 地形交叠 + 额外 ground/grid 存在”的直接根因不是地形生成公式本身，而是场景导入路径：
  - `scripts/isaac_sim/preview_stage1_terrain.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
  先通过 `TerrainImporterCfg(terrain_type="plane")` 自动创建了 `/World/terrain/terrain`，随后又额外 `import_mesh("stage1", ...)`，导致默认 plane 与自定义地形 mesh 同时存在。
- 在上述两个入口中新增默认 plane 清理逻辑：scene 创建后，先删除 `/World/terrain/terrain` 并从 `terrain_prim_paths` 中移除，再导入 stage1 mesh。
- 实际验证：
  - `python3 -m py_compile scripts/isaac_sim/preview_stage1_terrain.py`
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
  - `python scripts/isaac_sim/preview_stage1_terrain.py --headless --frames 1`

修改文件：
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `preview_stage1_terrain.py` 与 `CompleteCarStage1Env` 都不会再把默认 plane 和 stage1 mesh 叠加到同一场景中。
- 当前“额外 ground/grid”问题已定位为 scene 初始化行为，不应再误判为 MGDP `gap / ramp / beam` 等单块地形函数本身生成了第二层网格。
- 同时确认本项目与 MGDP 原版仍有若干几何层差异，主要集中在 `gap / hurdle / pit / env_origin` 的具体实现语义；这些差异会影响地形形状是否一致，但不是这次 plane 叠加问题的根因。

下一步：
- 若要继续把本项目 stage1 地形形状尽量对齐 MGDP，应优先按原版逐项收敛 `parkour_step_gap_terrain`、`parkour_step_terrain`、`pit_terrain` 和 `env_origin` 计算，而不是继续排查 scene 中是否还有第二张地面。

已完成：
- 修复 `scripts/isaac_sim/preview_stage1_terrain.py` 的启动参数冲突。此前脚本手动声明了 `--headless`，而 `isaaclab.app.AppLauncher.add_app_launcher_args()` 也会注入同名参数，导致脚本一启动就在参数解析阶段抛出 `ValueError`。
- 删除脚本中重复的 `parser.add_argument("--headless", ...)`，保留 `AppLauncher` 注入的标准 `--headless` 参数。
- 实际验证：
  - `python3 -m py_compile scripts/isaac_sim/preview_stage1_terrain.py`
  - `python scripts/isaac_sim/preview_stage1_terrain.py --help`

修改文件：
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `preview_stage1_terrain.py` 现在可以正常完成参数解析，不会再在 `AppLauncher.add_app_launcher_args()` 阶段因为重复定义 `--headless` 而直接报错。
- 后续这个脚本若继续使用 `AppLauncher`，应避免手动重复声明其会自动注入的参数。

下一步：
- 可直接重新执行 `python scripts/isaac_sim/preview_stage1_terrain.py`，若后续再报错，再继续处理运行时层面的场景或资源问题。

已完成：
- 按用户要求撤销上一轮直接落下去的 `MGDP stage1` RL 训练接入代码，不再保留“先写完整实现、再解释”的协作方式。
- 删除任务包内新增的 `mgdp_stage1_terrain.py`、`complete_car_terrain_env.py` 和占位 terrain USDA 文件。
- 将 `Complete-Car-Rl-Training-v0` 的任务注册入口恢复为基础 `ManagerBasedRLEnv`。
- 将 `complete_car_rl_training_env_cfg.py` 恢复到撤销前的基线状态，去掉 `TerrainImporterCfg`、rough-terrain 相关 reset/reward/termination 收敛和运行时地形导入依赖。
- 更新 `docs/current_status.md` 与 `docs/conversation_history.md`，把项目状态改为“阶段 1 方案已确认，但代码实现已回退，后续按教学模式从空白重建”。
- 在教学模式启动时，曾短暂代写一个 `mgdp_stage1_terrain.py` 骨架文件；随后按用户要求立即删除，后续改为只给手敲指导，不再由 Codex 代写教学步骤中的代码。
- 按教学模式继续推进 `stage1_terrain.py`：已完成 `Stage1TerrainCfg/Stage1TerrainData`、`terrain_dict/terrain_proportions`、像素尺寸派生量、空地图分配函数、flat/slope/pit 三种 tile、tile 写入大地图、terrain_type 记录、env_origin 记录，以及 `choice -> terrain_idx -> tile` 的初版调度逻辑。
- 已将 `row` 首次接入难度变量 `difficulty = row / cfg.num_rows`，并验证同一列 slope 在不同 row 上会表现出不同最大高度：第 0 行几乎为平地，第 19 行最大高度约为 18 个高度单位。

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/__init__.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_terrain_env.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/mgdp_stage1_terrain.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/assets/mgdp_stage1_placeholder.usda`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库不再保留任务内 `MGDP stage1` rough-terrain 训练接入代码。
- 研究层面仍保留“阶段 1 目标切到 `MGDP stage1` 混合地形 + 固定球铰 + 速度跟踪”的方向，但工程实现需要重新开始。
- 后续协作方式已明确：先讲清方案，再按教学模式一步一步写；用户自己手敲代码，Codex 只做结构讲解、逐行指导和复查。
- 当前 `stage1_terrain.py` 已经从零搭到“完整二维课程地图骨架 + 初版 row/col 语义”，但还没接入真实 MGDP 多地形完整分支，也还没接入 Isaac Lab terrain importer。

下一步：
- 先向用户讲清楚从当前基线出发时，`MGDP stage1` 接入应拆成哪些代码落点，再从第一步数据结构和参数定义开始，由用户手工敲入。
- 继续在教学模式下扩展 `stage1_terrain.py`：让更多地形函数接入 `difficulty`，再逐步过渡到完整 `MGDP stage1` 地形选择和最终 mesh 导出。

## 2026-04-01

已完成：
- 根据用户新确认的主线，停止沿用“阶段 1 平地 + 目标导向移动”定义，改为“`MGDP stage1` 混合地形 + 固定球铰 + 6 维轮速动作 + 速度跟踪”。
- 在 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/` 下新增任务内 `mgdp_stage1_terrain.py`，把 `MGDP stage1` 的 mixed terrain 生成逻辑直接迁移到当前 Isaac Lab 任务包。
- 新增自定义环境类 `complete_car_terrain_env.py`，通过自定义 `ManagerBasedRLEnv` 子类在环境启动后导入 stage1 mesh，并在 `_reset_idx()` 中执行 terrain curriculum 更新。
- 新增占位文件 `assets/mgdp_stage1_placeholder.usda`，用于先初始化 Isaac Lab `TerrainImporterCfg`，再在运行时导入真实 `MGDP stage1` trimesh。
- 修改 `complete_car_rl_training_env_cfg.py`：
  - scene 从默认平地切到 `TerrainImporterCfg`
  - commands 切到速度跟踪配置
  - actions 收敛为仅 6 维轮速
  - 观测移除球铰动作相关项
  - reset 中将球铰固定为零位
  - reward / termination 切到 rough-terrain velocity tracking 口径
  - episode 长度改为 `20 s`
- 修改任务注册入口 `__init__.py`，将 `Complete-Car-Rl-Training-v0` 的 entry point 从基础 `ManagerBasedRLEnv` 改为新的 `CompleteCarTerrainEnv`。
- 实际执行静态检查：
  - `python3 -m py_compile .../mgdp_stage1_terrain.py`
  - `python3 -m py_compile .../complete_car_terrain_env.py`
  - `python3 -m py_compile .../complete_car_rl_training_env_cfg.py`
  - `python3 -m py_compile .../__init__.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/mgdp_stage1_terrain.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_terrain_env.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/assets/mgdp_stage1_placeholder.usda`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/__init__.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 RL 任务主线已不再是“平地目标导向移动”，而是切到“`MGDP stage1` rough terrain + velocity tracking”。
- 当前代码层已经具备 task-local 的 `MGDP stage1` 地形生成与 terrain curriculum 接口，但尚未在 `env_isaacLab` 里完成一次真实运行时 smoke 验证。
- 当前终端上下文无法直接导入 `isaaclab`，因此本轮只能完成静态改造与语法检查，运行时接口是否完全匹配 Isaac Lab 2.3.x 仍待下轮验证。

下一步：
- 在 `env_isaacLab` 中依次执行 `list_envs`、`zero_agent` 和短程 `train --max_iterations 10`，先确认新任务入口可创建、可 reset、可 step。

## 2026-04-02

已完成：
- 按用户要求停止“逐步教学到每个小步都由用户手敲”的节奏，直接完成 `stage1_terrain.py` 中从 Step 36 到 Step 45 的地形生成层实现。
- 在 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py` 中补齐 MGDP stage1 对应的地形函数与分发表：
  - `stairs down`
  - `stairs up`
  - `new stairs down`
  - `discrete obstacles`
  - `hurdle`
  - `gap`
  - `ramp`
  - `beam`
- 将 `pyramid`、`hurdle`、`gap`、`ramp`、`beam` 等地形加入 roughness 处理，并为随机型地形加入基于 `(row, col, terrain_idx)` 的确定性 seed。
- 将 `make_tile_by_col()` 升级为：
  - `choice -> terrain_idx`
  - `terrain_idx -> terrain_name`
  - `terrain_name -> generator`
  的完整分发结构。
- 将各类关键地形参数接入 `difficulty`：
  - 斜坡高度
  - 台阶高度 / 台阶宽度
  - 离散障碍高度
  - hurdle 高度
  - gap 宽度
  - ramp 坡度
  - beam 长度 / 间距 / 高度
  - pit 深度
- 修正 `stairs` 的初版实现偏差，改为更接近 MGDP 语义的“台阶段 + 中心 platform”结构，避免在整块 8 m tile 上无约束累加导致累计高度过大。
- 完成运行验证：
  - `python3 -m py_compile .../stage1_terrain.py`
  - 逐个 terrain name 调用 `make_tile_by_name(...)`
  - `build_stage1_terrain_data(...)`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `stage1_terrain.py` 已不再是教学骨架，而是完整的 MGDP stage1 地形生成层实现基础。
- 当前 `build_stage1_terrain_data()` 已可同时生成：
  - `height_field_raw`
  - `env_origins`
  - `terrain_type`
  - `vertices`
  - `faces`
  - `x_edge_mask`
- 当前按 MGDP 原 `choice = j / num_cols + 0.001` 与累计 `terrain_proportions` 的列选择逻辑，`20 x 10` 默认课程地图实际只命中前几类 terrain index；这是原配置逻辑的结果，不是本轮移植错误。

下一步：
- 从 Step 46 起恢复教学模式，继续处理 `env_origin` 与特殊地形出生点策略，再接 `TerrainImporter`、自定义 Isaac Lab 环境类和 terrain curriculum。

## 2026-03-31

已完成：
- 修复完整 MGDP 画廊模式下的一个 USD 构建报错：`terrain_builder.py` 中 `create_box()` 之前每次都无条件 `AddTranslateOp()` / `AddScaleOp()`，当同一路径 prim 已存在时会触发 `xformOp:translate already exists`。
- 将 `create_box()` 改为幂等写法：先检查已有 `translate/scale` xform op，存在则直接复用并更新数值，不存在时才新增。
- 实际执行：
  - `python3 -m py_compile scripts/isaac_sim/terrain_preview/terrain_builder.py`
  - `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`
- 修复 `scripts/isaac_sim/control_keyboard.py` 在 Isaac Sim 工具栏执行 `Stop -> Play` 后失去键盘控制的问题。
- 根据本地 `isaacsim_5.1` 手册与脚本现状，确认根因是 articulation 只在启动时初始化了一次，而 timeline 从 `stopped` 重新切回 `playing` 后没有重新 `initialize()`。
- 将脚本中的 articulation 初始化重构为可重复调用的 `initialize_robot_handles(...)` 流程，统一负责重新绑定 DOF 名称、关节索引、控制目标和键盘状态。
- 修改交互主循环：现在会在检测到 timeline 停回第 0 帧后，把下一次 `Play` 视为一次需要 `world.reset()` + articulation 重初始化的状态跳变；对普通 `Pause -> Play` 只恢复物理，不强制 reset。
- 补充懒加载修复：把 `mgdp_gallery_builder` 的导入从模块顶层移到完整画廊分支内部，避免 `--terrain none` 或单块 tile 旧路径被 `pydelatin` 依赖提前打坏。
- 实际执行：
  - `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`
  - `timeout 180s python3 -u scripts/isaac_sim/control_keyboard.py --terrain none --headless --frames 1`
- 新增 `scripts/isaac_sim/terrain_preview/mgdp_gallery_builder.py`，把完整 MGDP `stage1/stage2` 画廊地形的构建逻辑从预览脚本中抽成可复用共享模块。
- 重构 `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`，改为直接调用上述共享模块，不再在脚本内保留一份独立的完整地形构建实现。
- 修改 `scripts/isaac_sim/control_keyboard.py`，使 `--terrain` 除了原有单块 tile 外，还支持完整 `stage1`、`stage2` 与 `both`。
- 为完整画廊模式补充启动环境分流：单块 tile / `none` 仍沿用 conda shell 自动重启到宿主 `/home/ubuntu/isaacsim/python.sh` 的旧路径；当 `--terrain` 为 `stage1/stage2/both` 时，脚本保留在 `env_isaacLab` Python 中运行，以复用 `pydelatin` 等 `terrain_preview` 依赖。
- 修改 `control_keyboard.py` 的地形材质绑定逻辑，使共享物理材质除了绑定六个轮子碰撞体外，也会绑定到 `/World/terrain_preview` 地形根节点。
- 实际执行以下静态检查：
  - `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`
  - `python3 -m py_compile scripts/isaac_sim/terrain_preview/mgdp_gallery_builder.py`
  - `python3 -m py_compile scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
- 实际执行以下 headless 冒烟验证：
  - `conda run -n env_isaacLab python -u scripts/isaac_sim/control_keyboard.py --terrain stage1 --headless --frames 1`
  - `conda run -n env_isaacLab python -u scripts/isaac_sim/control_keyboard.py --terrain stage2 --headless --frames 1`

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `scripts/isaac_sim/terrain_preview/mgdp_gallery_builder.py`
- `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 完整 MGDP `stage1/stage2` 画廊现在不会再因为重复定义同一路径下的 base box 而在 `create_box()` 处抛出 USD xform op 冲突异常。
- `control_keyboard.py` 现在会在 Stop 后重新 Play 时自动重建 teleop 所需的 articulation 句柄和目标状态，不再沿用已经失效的启动期句柄。
- 当前脚本已恢复兼容两条路径：
  - 宿主 `python.sh` 下的 `--terrain none` / 单块 tile
  - `env_isaacLab` 下的完整 MGDP `stage1/stage2` 画廊
- `control_keyboard.py` 现在已经不是只能注入单块 `slope_ramp/gap/corridor` 之类的局部地形，而是可以直接把 `terrain_preview` 中的完整 MGDP `stage1` 或 `stage2` 画廊放进同一个 teleop stage。
- 当前机器上，完整 MGDP 画廊模式不能继续走宿主 `isaacsim/python.sh` 默认路径，因为该路径缺少 `pydelatin`；正确运行方式应为激活 `env_isaacLab` 后执行 `python scripts/isaac_sim/control_keyboard.py --terrain stage1` 或 `--terrain stage2`。
- `stage1` 与 `stage2` 两条新路径都已在本机 headless 1 帧模式下实际跑通并正常退出，说明这次修改不只是静态代码改动。

下一步：
- 若要继续人工联调，可在 `env_isaacLab` 中直接运行 `python scripts/isaac_sim/control_keyboard.py --terrain stage1` 或 `python scripts/isaac_sim/control_keyboard.py --terrain stage2`，再观察车体初始落点、轮地接触与通过性表现。

已完成：
- 检查当前机器的 Conda 启动默认值，确认新开的交互式 `bash` 仍会因为 `auto_activate_base=True` 而默认进入 `base`。
- 将 `~/.condarc` 改为 `auto_activate: false`，关闭 `base` 自动激活。
- 在 `~/.bashrc` 的 `conda init` 之后追加交互式 shell 自动 `conda activate env_isaacLab` 的启动逻辑。
- 实际验证：
  - `conda config --show auto_activate_base`
  - `bash -ic 'printf "%s\n" "CONDA_DEFAULT_ENV=$CONDA_DEFAULT_ENV" "CONDA_PREFIX=$CONDA_PREFIX"'`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前机器新开的交互式 `bash` 终端默认已不再进入 `base`，而是直接进入 `env_isaacLab`。
- 后续在这个工作站里执行本仓库的 Isaac Lab / Isaac Sim 相关命令时，一般不再需要先手动 `conda activate env_isaacLab`。

下一步：
- 若后续更换 shell、用户或机器，需要重新检查对应启动文件是否也继承了这一默认环境设置。

## 2026-03-30

已完成：
- 按“代码与文档改动 + `mgdp_port/` 新源码，排除缓存/输出/备份文件”的范围重新整理本次待上传内容。
- 扩充根目录 `.gitignore`，新增忽略 `.cache/`、`outputs/`、`__pycache__/`、`*.py[cod]`、`*.bak`，避免 Isaac Sim 本地缓存、导出物和备份文件再次混入普通 Git 提交。
- 复核工作区后确认本次未跟踪内容只剩 `scripts/isaac_sim/terrain_preview/mgdp_port/` 源码目录，缓存与生成物已从待提交列表中排除。
- 将这一仓库级提交边界补写进 `docs/conversation_history.md`，作为后续常规 Git 上传默认规则。

修改文件：
- `.gitignore`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库普通 Git 上传的默认范围已进一步收敛为“源码、文档、必要结果”，不再混入本地运行时制品。
- 后续若继续用 Isaac Sim 做联调，生成的 `.cache/`、`outputs/`、`__pycache__` 与 `*.bak` 将默认留在本地，不再干扰正常推送。

下一步：
- 将本次整理后的源码与文档提交并推送到 GitHub `origin/main`。

已完成：
- 将 MGDP 中与地形生成、terrain curriculum 相关的脚本复制到 `scripts/isaac_sim/terrain_preview/mgdp_port/`，包括 `terrain.py`、`terrain_utils.py` 和 `new_terrains/`。
- 新增 `scripts/isaac_sim/terrain_preview/mgdp_port/configs.py` 与 `curriculum.py`，把 MGDP 的 stage1 / stage2 地形参数和课程学习地形分配逻辑独立迁移到本仓库。
- 重写 `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`，改为基于 `isaaclab.app.AppLauncher` 直接在 Isaac Sim 中构建 MGDP 地形网格、转换 mesh，并附带课程学习环境原点标记。
- 修改 `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`，使其默认激活 `conda` 环境 `env_isaacLab` 后直接用 `python` 启动，不再依赖旧的 `isaacsim/python.sh` 包装路径。
- 修复迁移后地形工具在新环境下的兼容问题，包括去掉对 `isaacgym` / `legged_gym` 包结构的硬依赖，以及将 `scipy.interpolate.interp2d` 替换为 `RegularGridInterpolator`。
- 为当前 `env_isaacLab` 修复 Isaac Sim 窗口启动所需的数值栈，将 `numpy` 回滚到 `1.26.0`，并将 `scipy` 调整为 `1.14.1`。
- 实际完成以下验证：
  - `python -m py_compile scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
  - `python -m py_compile scripts/isaac_sim/terrain_preview/mgdp_port/*.py` 相关核心脚本
  - `bash -n scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --headless --frames 1 --gallery stage1`
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --headless --frames 1 --gallery stage2`
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --frames 1 --gallery stage1`
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --frames 1 --gallery stage2`

修改文件：
- `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
- `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`
- `scripts/isaac_sim/terrain_preview/README.md`
- `scripts/isaac_sim/terrain_preview/mgdp_port/__init__.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/configs.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/curriculum.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/terrain.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/terrain_utils.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/new_terrains/__init__.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/new_terrains/add_mix_terrain.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/new_terrains/add_trimesh_terrain.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/new_terrains/add_extreme_gap_terrain.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库中已经有一份可独立于原 MGDP 仓库启动的地形预览迁移版，核心目标是“在 Isaac Sim 中查看 MGDP 地形生成和地形课程学习布局”。
- 当前 `env_isaacLab` 下，MGDP 地形预览已不是仅能 headless 导出 USD，而是可以实际启动 Isaac Sim 窗口查看。
- 当前这条预览链路依赖 `numpy==1.26.0`；若后续又被升级到 `numpy 2.x`，Isaac Sim 扩展加载大概率会再次报二进制兼容错误。

下一步：
- 若需要继续与完整车联调，可在现有 MGDP 地形预览基础上再决定是否把完整车资产放进同一个 stage 做实际通过性观察。

已完成：
- 继续修改 `scripts/isaac_sim/control_keyboard.py`，将此前被固定为零速的 6 个轮子重新接回键盘遥操作。
- 按仓库已有遥操作习惯，将车轮控制设为 `W/S` 前后、`A/D` 差速转向、`SPACE` 将轮速目标清零。
- 保留数字小键盘 `1-9`、`/`、`*`、`-` 对 6 个球铰自由度的正负位置调节。
- 为车轮速度命令与球铰位置命令都加入一阶平滑，避免按键切换时目标突变。
- 对更新后的脚本执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，语法检查通过。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `control_keyboard.py` 现同时支持轮式差速控制和球铰位置控制。
- 当前键位分工为：`W/S/A/D/SPACE` 控轮子，数字小键盘控球铰，二者互不冲突。
- 控制链路已加入基础平滑，更接近可用于手动调试的实际 teleop 形式。

下一步：
- 若需要，可继续在 Isaac Sim 中实际启动脚本，观察平滑系数是否偏软或偏硬，再调 `WHEEL_VELOCITY_SMOOTHING` 与 `BALL_POSITION_SMOOTHING`。

## 2026-03-30

已完成：
- 修改 `scripts/isaac_sim/control_keyboard.py`，将加载的机器人资产从旧的仓库根目录 `complete_car_alternative.usd` 切换为 `USD/complete_car.usd`。
- 将脚本中的机器人根 prim 路径同步改为 `/World/complete_car_final`，与当前 `complete_car.usd` 的实际机器人本体一致。
- 将原先的字母键控制方案改为数字小键盘控制方案，使用 `1-9`、`/`、`*`、`-` 对 6 个球铰自由度进行正负调节。
- 由于这 12 个键已全部用于 6 个自由度的正负控制，当前脚本模式下将 6 个轮子保持为零速度，不再单独提供轮速键盘控制。
- 对修改后的脚本执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，语法检查通过。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `control_keyboard.py` 已与当前主 USD 资产 `USD/complete_car.usd` 和 `/World/complete_car_final` 对齐。
- 新键位方案已经从字符串按键名切换为 `carb.input.KeyboardInput` 的数字小键盘枚举，避免对事件名做字符串猜测。
- 当前脚本更适合做 6 自由度球铰姿态手动调试，不再承担轮式推进键盘遥操作。

下一步：
- 若后续仍需要同时做轮速遥控和球铰遥控，需要重新定义一套不与数字小键盘冲突的轮子控制键位。

## 2026-03-30

已完成：
- 按用户给出的新稿，整体替换 `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`。
- 新版 `chapter03` 现以“运动学模型”为题，覆盖空间位置/姿态/位姿、旋转矩阵、齐次变换矩阵，以及 3-RRR 球面并联机构逆运动学解析推导。
- 由于新稿引入了 `tikzpicture` 插图，在 `毕业论文/毕业论文模板/LaTeX/main.tex` 中补入 `tikz` 与 `arrows.meta` 宏包依赖。
- 在论文主目录下连续执行两次 `xelatex -interaction=nonstopmode -halt-on-error main.tex`，确认替换后的正文可编译。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `毕业论文/毕业论文模板/LaTeX/main.tex`
- `毕业论文/毕业论文模板/LaTeX/main.pdf`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `chapter03.tex` 已切换为用户提供的新版本内容，不再是上一版“球铰等效机构逆运动学建模”文本。
- 新稿引入的 TikZ 插图依赖已经补齐，主文档编译链路可正常通过。
- 当前仍存在两类非阻塞告警：`chapter01` 的历史未定义引用，以及新章节长公式带来的 `Overfull \hbox` 提示。

下一步：
- 若后续需要继续打磨论文排版，可优先处理 `chapter03` 中长公式的断行与版面压缩。

## 2026-03-29

已完成：
- 对整个仓库做了目录级盘点，梳理当前各文件组的职责边界。
- 新增 `docs/project_file_map.md`，把仓库内容归纳为 RL 主线、资产与仿真验证、文献、论文、逆运动学推导与配图、结果输出六大块。
- 重写根 `README.md`，使其与当前阶段主线一致，并补充当前最重要的目录入口说明。
- 将本次仓库文件归纳结果同步写入长期记忆和当前状态，避免后续再次靠聊天临时解释目录用途。

修改文件：
- `README.md`
- `docs/project_file_map.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库已经有一份显式的文件地图，可直接用于后续定位代码、论文、文献和资产文件。
- 根 README 不再停留在早期最小 baseline 描述，而是对齐到当前真实主线和目录结构。

下一步：
- 若后续需要做物理目录重组，可直接以 `docs/project_file_map.md` 的六块职责划分为准继续收敛。

## 2026-03-29

已完成：
- 核对本地 `main` 与 GitHub `origin/main` 的提交关系，确认远端在同步前没有额外新提交。
- 按当前工作区原样整理并提交 Git 变更，包含现有删除项与未跟踪新增内容。
- 将当前仓库快照推送到 GitHub `origin/main`，使远端与本地工作区保持一致。
- 同步更新 `docs/current_status.md`，移除“待同步”状态。

修改文件：
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- GitHub `origin/main` 已更新为当前本地工作区快照。
- 本轮同步后，仓库当前状态与远端主分支已一致。

下一步：
- 回到 RL baseline 收敛、USD 清理与论文写作主线。

## 2026-03-29

已完成：
- 根据 3-RRR 球面并联机构文献与现有符号化推导结果，重写毕业论文 `chapter03` 的球铰逆运动学部分。
- 在章节中补入三维旋转矩阵、齐次变换矩阵、方向向量约束、半角代换以及闭式逆解公式。
- 统一论文符号口径，将动平台姿态写为 `(\phi,\vartheta,\psi)`，将主动关节角保留为 `\theta_i`，避免姿态角与关节角冲突。
- 向论文参考文献库新增 `Sadeqi 等 2017` 的 BibTeX 条目。
- 实际执行 `xelatex -> bibtex -> xelatex -> xelatex` 编译验证，确认新增章节可被模板接受。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `毕业论文/毕业论文模板/LaTeX/reference/ref.bib`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `chapter03.tex` 已从占位模板改写为可直接用于论文正文的中文逆运动学章节。
- 当前章节推导链路已经固定为 方向向量建模 -> 几何约束 -> 半角代换 -> 二次方程闭式求解。
- 编译过程中与本次改动直接相关的引用和交叉引用均已收敛；主文档仍保留 `chapter01` 历史未补的两个旧引用告警，与本次修改无关。

下一步：
- 若需要，可继续在 `chapter04` 或 `chapter05` 中承接本章公式，补写控制映射、仿真验证或实验结果分析内容。

## 2026-03-28

已完成：
- 基于原始 PDF 重新整理 `Learning-based legged locomotion: State of the art and future perspectives` 的阅读笔记。
- 按已安装的 `literature-reading-notes` skill 模板重写了文献笔记结构，补齐论文快照、章节逻辑、mind map、分章节精读、术语表、重要参考文献和可复用 related-work 段落。
- 将该文献的总结重点进一步对齐到当前课题两阶段主线，明确其对 observation / reward / action / training framework / sim-to-real 的可迁移启发。
- 同步更新 `docs/current_status.md`，记录该阅读笔记已完成规范化重写。
- 根据用户新要求，将该笔记再次改写为“重要内容摘录与整理”版本，重点围绕正文中的概念定义、使用方式、该段引用的相关工作，以及对应完整参考文献信息。
- 去除了与当前课题直接绑定的分析内容，回到面向原文内容本身的综述笔记写法。
- 继续按用户给出的示例格式重写整份笔记，结构明确对齐为：论文快照、全文结构、mind map、章节精读笔记、关键知识点、术语表、重要参考文献、可复用综述段落。
- 将 `Section 3.2 Observation` 及其子节改为“核心观点 / 本节作用 / 段落主旨 / 重点概念提炼 / 学术含义 / 完整参考文献”风格，并同步重排 `Reward`、`Action Space`、`Learning Frameworks`、`Sim-to-real`、`Combining control and learning` 等关键章节。

修改文件：
- `docs/literature/mineru_output/Ha 等 - 2025 - Learning-based legged locomotion State of the art and future perspectives/auto/reading_notes.md`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前该文献对应目录下的 `reading_notes.md` 已不再只是首轮高层梳理，而是可直接复用的结构化综述笔记。
- 该综述继续支持当前仓库已固化的阶段化路线：先最小 baseline，再逐步加入复杂 observation、球铰控制、复杂地形和 sim-to-real 设计。
- 当前版本更符合“文献摘录式阅读笔记”用途：可以直接按节查看某个概念在综述中的定义、作用与引用来源。
- 当前版本已更接近“综述型文献精读卡片”，便于后续继续逐段扩写。

下一步：
- 若需要，可继续把 `3.3 Reward`、`3.4 Action space`、`4 Learning frameworks` 进一步扩展成逐段摘录版，并补得更全。

## 2026-03-16

已完成：
- 将仓库重组为更清晰的 `scripts/`、`results/`、`refs/` 和 `src/` 结构。
- 在 `AGENTS.md` 中加入仓库级启动上下文规则。
- 新增持久化会话记录文件 `docs/conversation_history.md`。
- 新增按日期记录的进度日志 `logs/daily_work_log.md`。
- 更新 Isaac Sim 辅助脚本，使其使用仓库相对路径。
- 确认 `.codex/config.toml` 存在且已启用 Web 搜索。
- 新增 `scripts/isaac_sim/check_isaaclab_asset.py` 用于 Isaac Lab 资产验证。
- 对 `USD/complete_car_alternative.usd` 进行了 Isaac Lab headless 验证。
- 识别出当前 USD 包尚不能直接作为 Isaac Lab articulation 生成，原因包括缺失 `configuration/*.usd` 依赖文件以及缺少 default prim。
- 将 Isaac Lab 资产检查入口切换为 `USD/complete_car.usd`。
- 对 `USD/complete_car.usd` 再次进行了 Isaac Lab headless 验证。
- 确认 stage 中实际根节点仍为 `/World/complete_car_alternative`，同时 `USD/complete_car.usd` 仍缺少 default prim，且 `USD/configuration/` 下存在 unresolved references。
- 修复 `USD/complete_car.usd`，将 default prim 设置为 `/World`。
- 清理 `USD/configuration/default_scene_base.usd` 中四个损坏的纯可视化引用。
- 通过 USD 检查确认损坏引用已被移除。
- 通过 Isaac Lab headless 加载确认当前机器人已被识别为 12 关节 articulation。

修改文件：
- `AGENTS.md`
- `README.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `docs/current_status.md`
- `scripts/isaac_sim/check_isaaclab_asset.py`
- `scripts/isaac_sim/inspect_usd_dependencies.py`
- `scripts/isaac_sim/repair_complete_car_usd.py`
- `scripts/isaac_sim/repair_complete_car_usd_v2.py`
- `scripts/isaac_sim/repair_complete_car_usd_v3.py`
- `scripts/isaac_sim/repair_complete_car_usd_v4.py`
- `scripts/isaac_sim/control_keyboard.py`
- `scripts/isaac_sim/validate_sensors.py`
- `refs/isaac_kb/README.md`
- `src/rl_lab/README.md`

下一步：
- 构建最小 Isaac Lab 任务骨架，并为完整车补齐 actuator 配置。

## 2026-03-16

已完成：
- 删除了仓库内手写的 direct-workflow 任务骨架 `src/rl_lab/tasks/`。
- 保留 `src/rl_lab/complete_car_rl_training/` 作为唯一的 Isaac Lab 模板 project。
- 更新仓库状态说明，明确后续 RL 环境开发应继续在模板 project 内进行。

修改文件：
- `src/rl_lab/__init__.py`
- `src/rl_lab/tasks/__init__.py`
- `src/rl_lab/tasks/complete_car_attitude_direct/__init__.py`
- `src/rl_lab/tasks/complete_car_attitude_direct/complete_car_env.py`
- `src/rl_lab/tasks/complete_car_attitude_direct/agents/__init__.py`
- `src/rl_lab/tasks/complete_car_attitude_direct/agents/rsl_rl_ppo_cfg.py`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

下一步：
- 将 `src/rl_lab/complete_car_rl_training/` 中的 cartpole 模板内容替换为完整车的 manager-based 最小任务。

## 2026-03-16

已完成：
- 新增 `docs/isaaclab模板使用指南.md`，整理了当前模板 project 的用途、推荐工作流、具体使用命令以及模板改造位置。
- 将 `docs/current_status.md` 改写为中文。
- 将 `logs/daily_work_log.md` 改写为中文，并明确后续新增日志统一使用中文。
- 在 `AGENTS.md` 中补充规则：`docs/current_status.md` 与 `logs/daily_work_log.md` 统一使用中文维护。

修改文件：
- `AGENTS.md`
- `docs/isaaclab模板使用指南.md`
- `docs/current_status.md`
- `logs/daily_work_log.md`

下一步：
- 按照 `docs/isaaclab模板使用指南.md` 中的顺序，在模板 project 内替换任务名、资产配置、动作配置、观测配置、奖励配置和 PPO 配置。

## 2026-03-17

已完成：
- 修复了 `complete_car_rl_training_env_cfg.py` 中已有的语法和 Isaac Lab API 拼写错误。
- 将模板环境中的 cartpole 资产配置整体替换为完整车 `ArticulationCfg`，入口指向 `USD/complete_car.usd`。
- 为完整车补齐了两组 actuator：
  - 6 个球铰等效关节 `ball_joints`
  - 6 个车轮关节 `wheel_joints`
- 将动作空间改为 12 维：
  - 6 维球铰位置动作
  - 6 维车轮速度动作
- 加入 `UniformVelocityCommandCfg`，使策略可以基于速度指令学习前进/后退。
- 将观测改为完整车版本，包含底盘速度、重力投影、速度指令、球铰状态、车轮速度和上一时刻动作。
- 将 reset、reward、termination 从 cartpole 版本替换为完整车版本。
- 用 `python3 -m py_compile` 对新的环境配置文件做了语法检查，结果通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/source/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前模板环境已经不再依赖 cartpole 关节名。
- 当前基线任务设计已经从“仅球铰姿态控制”升级为“球铰姿态 + 车轮前进/后退”的联合控制版本。
- 目前只完成了静态改写和语法检查，尚未完成 Isaac Lab 运行时验证。

下一步：
- 用 `list_envs.py`、`zero_agent.py` 或 `random_agent.py` 验证完整车环境能否正常创建与 step。
- 根据运行结果继续调节 wheel actuator 参数、奖励权重和终止阈值。

## 2026-03-18

已完成：
- 删除了 `complete_car_rl_training_env_cfg.py` 中 scene 级重复定义的 `ground` 与 `dome_light`。
- 将完整车 RL 环境的默认场景来源明确为 `USD/complete_car.usd` 内部已有场景元素。
- 将 PPO 配置中的 `experiment_name` 从 `cartpole_direct` 改为 `complete_car_rl_training`。
- 在 `AGENTS.md` 中新增“第一性原理”和“方案规范”两组仓库级协作约束。
- 同步更新了项目当前状态和长期会话结论。

修改文件：
- `src/rl_lab/complete_car_rl_training/source/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/source/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/agents/rsl_rl_ppo_cfg.py`
- `AGENTS.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 RL scene 只保留机器人资产定义，不再在配置层重复生成地面和灯光。
- 后续训练日志目录将使用完整车任务名，不再落到 cartpole 模板名下。
- 后续运行时验证需要优先确认 `complete_car.usd` 内置场景在 Isaac Lab 多环境复制下的行为是否稳定。

下一步：
- 运行 `list_envs.py`、`zero_agent.py` 或 `random_agent.py` 做环境创建与 step 验证。

## 2026-03-18

已完成：
- 对 `src/rl_lab/complete_car_rl_training/` 进行了目录整理，移除了重复的模板壳层。
- 将 Python 包从 `source/complete_car_rl_training/complete_car_rl_training/` 收平到项目根下的 `complete_car_rl_training/`。
- 将 `setup.py` 与 `config/extension.toml` 移到训练项目根目录，并将安装方式统一为 `pip install -e .`。
- 将 `setup.py` 改为优先使用标准库 `tomllib`，避免在 Python 3.11 下额外依赖第三方 `toml` 包。
- 删除了训练项目中的嵌套 `.git`、`.vscode`、UI 示例文件和旧 `src/rl_lab/tasks/` 残留。
- 更新了训练项目 README、仓库 README 和 `docs/isaaclab模板使用指南.md`，同步新的目录结构与命令。
- 新增 `src/rl_lab/README.md`，明确 `complete_car_rl_training/` 是唯一保留的训练工作区。

修改文件：
- `src/rl_lab/README.md`
- `src/rl_lab/complete_car_rl_training/setup.py`
- `src/rl_lab/complete_car_rl_training/pyproject.toml`
- `src/rl_lab/complete_car_rl_training/.gitignore`
- `src/rl_lab/complete_car_rl_training/config/extension.toml`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/__init__.py`
- `src/rl_lab/complete_car_rl_training/README.md`
- `src/rl_lab/complete_car_rl_training/scripts/list_envs.py`
- `README.md`
- `docs/isaaclab模板使用指南.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 训练项目后续统一按“项目根 + 单个 Python 包 + scripts”结构维护。
- 后续所有安装、运行、训练、回放命令都应从 `src/rl_lab/complete_car_rl_training/` 项目根执行。
- `python3 setup.py --name` 已能在本机默认 Python 下通过，不再因为缺少 `toml` 包失败。

下一步：
- 在新结构下重新执行 `pip install -e .`，然后做 `list_envs.py`、`zero_agent.py`、`random_agent.py` 验证。

## 2026-03-18

已完成：
- 实际执行了完整车 RSL-RL 训练启动流程，并确认正确任务 ID 为 `Complete-Car-Rl-Training-v0`。
- 确认当前终端会话下默认 GPU 路径不可用，CUDA / NVIDIA driver 未加载，直接按默认配置会在 runner 初始化时失败。
- 修复了 `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`，使 `--device` 同时覆盖环境和 RSL-RL runner 的 device。
- 使用 `PYTHONPATH` 注入训练项目根目录，绕过当前沙箱下 `pip install -e .` 的 build isolation 联网与用户站点只读问题。
- 以 `--headless --device cpu --num_envs 100` 实际跑通了 `reset -> step -> train` 链路。
- 训练已进入稳定学习迭代，并在日志目录中生成了 `model_0.pt` 与 `model_50.pt`。
- 识别出 `USD/complete_car.usd` 仍有离线不可解析的远端引用，以及多环境复制时的 `PhysicsScene` replication 报错。
- 从训练指标确认当前主要行为问题是 `root_too_low` 终止长期为 `1.0`，说明环境虽可训练，但 rollout 质量很差。

修改文件：
- `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 第一条完整训练链路已经在本机 CPU 模式下验证通过，说明任务注册、环境创建、manager 配置、RSL-RL runner 与日志落盘均已打通。
- 最新训练输出目录为 `src/rl_lab/complete_car_rl_training/logs/rsl_rl/complete_car_rl_training/2026-03-18_17-14-07/`。
- 当前真正阻塞点已经从“能否启动训练”切换为“USD 资产离线清理 + replicated physics scene 清理 + root height 相关任务调参”。

下一步：
- 清理 `USD/complete_car.usd` 中的远端引用和内嵌 `PhysicsScene`。
- 结合当前训练日志调整初始高度、`root_too_low` 阈值、reset 范围和奖励权重。
- 如果继续在当前终端会话运行训练，默认使用 `--device cpu`。

## 2026-03-18

已完成：
- 重新在当前 `env_isaacLab` conda 环境中核实了启动方式，确认 `python` 直接可导入 `isaaclab` 与 `isaacsim`。
- 确认旧文档中的 `env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV /home/ubuntu/IsaacLab/isaaclab.sh -p ...` 属于历史工作绕过方式，不再应作为默认启动命令。
- 识别出直接 `python scripts/...` 初始失败的真实原因不是 conda，而是：
  - 首次无交互启动会卡在 Omniverse EULA 确认
  - 当前 conda 环境内尚未安装项目包 `complete_car_rl_training`
- 使用 `python -m pip install -e . --no-build-isolation` 将训练项目安装到 `env_isaacLab`。
- 在安装后重新验证，直接运行 `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --num_envs 4 --headless --device cpu --max_iterations 1` 已可进入完整训练循环并完成 1 次 learning iteration。
- 更新了训练项目 README、模板使用指南、当前状态和长期会话结论，使仓库文档与当前真实启动方式一致。

修改文件：
- `src/rl_lab/complete_car_rl_training/README.md`
- `docs/isaaclab模板使用指南.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前默认启动路径应为：激活 `env_isaacLab` -> `python -m pip install -e . --no-build-isolation` -> 必要时设置 `OMNI_KIT_ACCEPT_EULA=YES` -> 直接运行 `python scripts/...`。
- 直接训练链路已在当前 conda 环境下重新验证通过。

下一步：
- 继续清理 `USD/complete_car.usd` 的远端引用与内嵌 `PhysicsScene`。
- 在直接 `python` 启动路径下继续迭代训练配置与奖励设计。

## 2026-03-18

已完成：
- 根据 Isaac Lab 的资产组织方式，重新明确了 `complete_car.usd` 与 `scene cfg` 的职责分离：
  - `complete_car.usd` 仅保留小车 articulation 本体与车体挂载传感器
  - `scene cfg` 负责地面和灯光
- 修改 `src/rl_lab/complete_car_rl_training/.../complete_car_rl_training_env_cfg.py`，在 `CompleteCarRlTrainingSceneCfg` 中补回 `ground` 与 `dome_light`。
- 识别出当前两个主要远端依赖分别是：
  - scene 层的 `default_environment.usd`
  - 机器人 USD 内的 `Example_Rotary.usda`
- 按当前需求，保留 scene 层 `default_environment.usd`，不再使用临时本地 `CuboidCfg` 地面方案。

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `scene` 层的 ground/light 配置已经重新回到 Isaac Lab 标准职责边界。
- 当前远端依赖分为两类：
  - scene 层继续使用 `default_environment.usd`
  - 机器人 USD 中仍有 `Example_Rotary.usda`

下一步：
- 清理 `USD/complete_car.usd` 中残留的 `Example_Rotary.usda` 远端引用。
- 继续评估 camera / lidar / IMU 是否都需要保留在当前 RL 基线资产里。

## 2026-03-19

已完成：
- 重新整理了仓库级 `AGENTS.md` 结构，将启动上下文、项目背景、优先级、协作规则、记忆规则和规范文件职责重新归类。
- 将 RL 训练路径正式固化到 `AGENTS.md`：
  - 阶段 0 先跑通训练闭环

## 2026-03-28

已完成：
- 读取并整理了根目录草稿 `literature_note_skill.md`。
- 将其安装为可被 Codex 发现的本地 skill：`/home/lbz/.codex/skills/literature-reading-notes/`。
- 新增该 skill 的 `SKILL.md` 与 `agents/openai.yaml`，统一技能名为 `literature-reading-notes`。
- 将本次变更同步写入 `docs/current_status.md` 与 `docs/conversation_history.md`，保证后续会话可继承。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `/home/lbz/.codex/skills/literature-reading-notes/SKILL.md`
- `/home/lbz/.codex/skills/literature-reading-notes/agents/openai.yaml`

产出/结论：
- 当前已可直接使用 `$literature-reading-notes` 触发结构化文献阅读笔记工作流。
- 根目录 `literature_note_skill.md` 现可视为技能草稿源，而不是最终可发现的 skill 入口。

下一步：
- 如需继续完善，可再按实际使用频率补充该 skill 的示例、引用规则细化或与 `docs/literature/` 的仓库内工作流衔接说明。
  - 阶段 1 做平地基础速度跟踪 baseline
  - 阶段 2 再加入球铰控制
  - 更后续阶段再加入运动学先验、地形适应和感知融合
- 明确了第 1 阶段默认 baseline 应优先采用“固定球铰姿态 + 轮式运动控制 + 低维本体观测”的最短路径方案。
- 同步更新了 `docs/current_status.md` 与 `docs/conversation_history.md`，把新的训练主线和当前代码现状之间的差异记录为长期记忆。

修改文件：
- `AGENTS.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 后续会话不应再把“轮子 + 球铰联合控制 + 复杂扩展”默认视为第一阶段主线。
- 当前应先把平地速度跟踪 baseline 做稳定，再逐步恢复机构复杂度。
- `AGENTS.md` 现在已经包含完整且可继承的 RL 训练路线说明，不再依赖单次对话上下文。

下一步：
- 按新的第 1 阶段主线收敛环境配置，优先确认是否需要把当前 12 维联合动作基线简化为固定球铰版本。
- 继续处理 `USD/complete_car.usd` 的远端依赖、复制兼容性和 `root_too_low` 相关训练稳定性问题。

## 2026-03-19

已完成：
- 读取并解释了 `2026-03-19_13-13-03` 训练 run 的 Isaac Lab 日志、Hydra 配置和 TensorBoard 标量项。
- 确认该 run 已生成 `model_0.pt`、`model_50.pt`、`model_100.pt`、`model_149.pt`，属于完整训练完成而非中途终止。
- 新增 `scripts/tensorboard_export.py`，可将单次 run 的 TensorBoard scalar 自动导出为本地 `csv/json`。
- 修改 `scripts/rsl_rl/train.py`，使训练结束后自动生成 `tensorboard_export/summary.json`、`latest_values.csv` 和各 tag 的 `scalars/*.csv`。
- 对 `2026-03-19_13-13-03` 的已有 run 执行了一次导出验证，确认离线分析文件已正常生成。
- 更新训练项目 `README.md`，补充 TensorBoard 离线导出说明。
- 新增 `docs/tensorboard_reading_guide.md`，总结 TensorBoard 读图方法、指标含义和诊断顺序。
- 新增 `skills/isaac-rl-run-diagnosis/` skill，并复制安装到 `~/.codex/skills/isaac-rl-run-diagnosis/`。

修改文件：
- `src/rl_lab/complete_car_rl_training/scripts/tensorboard_export.py`
- `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`
- `src/rl_lab/complete_car_rl_training/README.md`
- `src/rl_lab/complete_car_rl_training/docs/tensorboard_reading_guide.md`
- `src/rl_lab/complete_car_rl_training/skills/isaac-rl-run-diagnosis/SKILL.md`
- `src/rl_lab/complete_car_rl_training/skills/isaac-rl-run-diagnosis/agents/openai.yaml`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 后续每次训练结束后，都可以直接读取 run 目录下的 `tensorboard_export/`，不必依赖 TensorBoard 网页界面。
- 当前 `2026-03-19_13-13-03` run 的关键信号是：
  - `Train/mean_reward` 已明显上升
  - `Train/mean_episode_length` 已到 `480.0`
  - `Episode_Termination/time_out = 1.0`
  - `Episode_Termination/root_too_low = 0.0`
- 这说明当前 run 的 rollout 存活性明显好于此前 `root_too_low` 主导的异常情况。

下一步：
- 基于导出的 `latest_values.csv` 与各 tag CSV，继续逐项分析奖励构成和速度跟踪误差。
- 再按第 1 阶段主线评估是否应将球铰动作从默认 baseline 中收紧或固定。

## 2026-03-20

已完成：
- 为 `docs/literature/` 建立了“原始 PDF 保留 + MinerU 转 Markdown”并存的文献工作流。
- 新增 `scripts/literature/mineru_batch_convert.sh`，用于批量或单篇执行 MinerU PDF 转 Markdown。
- 新增 `scripts/literature/build_literature_manifest.py`，用于自动生成文献 PDF 与 Markdown 对照索引。
- 新增 `docs/literature/README.md`，明确文献目录规范、转换命令和 Codex 的读取顺序。
- 生成了首版 `docs/literature/catalog.md`，当前已列出全部本地 PDF，待 MinerU 转换后自动补齐 Markdown 路径。
- 更新 `AGENTS.md`、`README.md` 和 `docs/current_status.md`，把本地文献优先读 Markdown、PDF 负责核验的规则固化为长期约定。
- 创建仓库级 `.gitignore`，忽略本地 `.venv-mineru/` 文献工具虚拟环境。
- 在当前 `env_isaacLab` 环境中安装完成 `MinerU`。
- 首次单篇转换验证中，确认当前会话继承的本地代理变量会阻塞 MinerU 模型下载；已切换为“清空代理 + `MINERU_MODEL_SOURCE=modelscope`”的首跑方式。

修改文件：
- `.gitignore`
- `AGENTS.md`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `docs/literature/README.md`
- `docs/literature/catalog.md`
- `scripts/literature/mineru_batch_convert.sh`
- `scripts/literature/build_literature_manifest.py`

产出/结论：
- 本仓库后续文献读取默认采用：
  - 先读 `md`
  - 再用 `pdf` 核对图、公式、页码和可疑段落
- 文献目录已经从“仅 PDF 堆放”升级为“可转换、可索引、可被 Codex 稳定读取”的结构。
- 当前机器上 MinerU 的首次模型下载不应直接沿用现有代理环境，而应优先使用 `modelscope`。

下一步：
- 完成至少一篇文献的 MinerU 转换 smoke test，并确认真实输出目录结构。
- 确认 MinerU 的实际输出目录结构后，再按真实产物补齐 catalog 中的 Markdown 链接。


补充完成：
- 阅读并筛选了 `docs/literature/` 下与 RL 环境配置和训练设计相关的文献。
- 按“与本课题形态相似度 + 对 observation/reward/action/termination 的直接借鉴价值 + 与当前阶段主线的贴合度”完成了推荐排序。
- 新增 `docs/literature/rl_env_reading_notes.md`，作为后续持续维护的文献阅读笔记。
- 将当前优先阅读顺序收敛为：
  - `Wiberg 2022`
  - `Wiberg 2024`
  - `Bauer 2025`
  - `Xu 2024`
  - `Salvi 2022`

补充修改文件：
- `docs/literature/rl_env_reading_notes.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

补充产出/结论：
- 已形成一份面向 RL env 设计的本地文献阅读入口，不再需要每次从全部文献重新筛选。
- 当前不应优先把感知综述和 3-RRR 机构学论文作为第 1 阶段 baseline 的主参考。

补充下一步：
- 基于阅读笔记中的前 3 篇文献，进一步提炼可直接映射到 Isaac Lab 的 `observation / action / reward / termination` 草案。

## 2026-03-20

已完成：
- 对 `Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning.pdf` 执行了单篇 MinerU 转换。
- 成功生成对应 Markdown、图片与中间产物目录：
  - `docs/literature/mineru_output/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning/auto/`
- 自动更新 `docs/literature/catalog.md`，将该文献条目标记为 `ready`。
- 基于生成的 Markdown 与原始 PDF，补充了 `docs/literature/rl_env_reading_notes.md` 中该文的精读结论。
- 提炼了该文对本课题的可迁移要点：
  - reward 的主目标项 + 约束项组织方式
  - termination 的危险姿态 / 危险接触 / timeout 框架
  - curriculum 的逐层加难组织方式
  - 不应在第 1 阶段直接照搬高维地形 observation 与联合结构控制

修改文件：
- `docs/literature/catalog.md`
- `docs/literature/mineru_output/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning/auto/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning.md`
- `docs/literature/rl_env_reading_notes.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库已经有这篇论文的本地 Markdown，可直接作为后续阅读入口。
- 这篇论文对本课题最重要的价值不是“平台完全相同”，而是它把 rough-terrain vehicle 的 RL 任务定义拆得很完整。
- 对当前主线最合适的吸收方式是：先借鉴 reward / termination 逻辑，再在后续阶段逐步吸收地形 observation 和结构联合控制。

下一步：
- 继续辅助用户精读该文，并把其 `observation / action / reward / termination / curriculum` 映射到本课题的 Isaac Lab 环境设计上。

## 2026-03-21

已完成：
- 根据用户提出的要求，补充并固化了文献阅读类任务的交互协议。
- 在 `AGENTS.md` 的研究交互部分新增文献阅读辅助规则，明确：
  - 先确认单篇阅读目标
  - 默认按文章写作顺序推进提问
  - 提问逻辑优先遵循“是什么 -> 为什么 -> 联想与反思”
  - 每轮回答后需要进行纠正、补充与整理
  - 若理解不充分，允许围绕同一问题继续二次追问
- 确认当前 `Wiberg 等 - 2022` 的阅读目标为：
  - 主目标：整体掌握文章内容与逻辑
  - 次目标：提炼并学习 RL 环境设计
- 同步更新项目当前状态与长期会话结论，避免后续会话丢失这条协作规则。

修改文件：
- `AGENTS.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 本仓库后续的文献辅助阅读默认采用“教师式带读”而不是直接给结论。
- 对高相关文献，后续应先帮助用户掌握文章整体逻辑，再进入 env 设计细节和与本课题的迁移讨论。

下一步：
- 按新的交互协议，从 `Wiberg 等 - 2022` 的引言开始，依照文章顺序继续带读。
## 2026-03-22

已完成：
- 围绕 `Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning` 开展了一轮问答式精读，重点聚焦 RL 环境设计而非全文泛读。
- 将本轮对话中关于任务定义、observation、action、reward、termination、curriculum、evaluation 的梳理整理为结构化阅读笔记。
- 在该文献的 MinerU 输出目录下新增 `reading_notes.md`，便于后续直接在文献旁复习，不再只依赖聊天记录。
- 同步更新 `docs/current_status.md`，记录该文献目录下已形成可复用阅读笔记这一状态。

修改文件：
- `docs/literature/mineru_output/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning/auto/reading_notes.md`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已将该文献的第一轮精读结论沉淀为本地笔记，核心包括：
  - 任务定义应区分“目标”和“结果表现”
  - observation 可整理为地形感知、本体状态、任务相关信息三组
  - reward 设计应按“主任务 + 行为质量约束 + 终止条件 + 评估指标”来理解
  - curriculum、自然化 reset、训练/评估地形分离是该文献的重要训练组织方法

下一步：
- 继续对比后续 rough-terrain RL 文献，形成跨文献的可迁移设计共识，再回到本课题任务定义收敛。

## 2026-03-22

已完成：
- 安装并配置了独立的 `MinerU` 工作环境 `.venv-mineru`，避免污染现有 Isaac Lab 环境。
- 首次运行中补齐了 MinerU 所需的本地模型缓存，包括主模型、版面分析、阅读顺序、OCR、表格识别等依赖。
- 将 `Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain.pdf` 按仓库既定脚本流程转换为 Markdown。
- 围绕该文献完成了一轮问答式精读，重点提炼其 `observation / action / reward / termination / curriculum` 设计。
- 在该文献对应目录下新增 `reading_notes.md`，沉淀可复用阅读笔记，服务后续跨文献横向对比。

修改文件：
- `docs/literature/mineru_output/Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain/auto/Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain.md`
- `docs/literature/mineru_output/Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain/auto/reading_notes.md`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 该文献提供了一种更轻量的 rough-terrain RL 任务定义：高层 action、简洁 observation、极简 reward、单一维度 curriculum。
- 相比 `Wiberg 2022`，它更适合作为“任务简化、课程推进、goal-directed mobility 设计”的参考，而不是多执行器联合控制模板。
- 当前已具备至少两篇高相关文献的本地 Markdown 与结构化阅读笔记，后续可继续积累 2-3 篇后开展横向对比与本课题方案规划。

下一步：
- 继续精读 2-3 篇高相关文献并整理阅读笔记。
- 在文献样本足够后，系统输出面向本课题的横向对比与方案规划。

## 2026-03-22

已完成：
- 将 `Bouton和Gao - 2023 - MARCEL mobile active rover chassis for enhanced locomotion.pdf` 转换为 Markdown。
- 基于文献内容判断其更适合作为“结构动机与机理解释”参考，而不是当前阶段的 RL 环境配置主文献。
- 按用户要求，将该文献标记为后续撰写论文动机部分时应回看的参考文献。

修改文件：
- `docs/literature/mineru_output/Bouton和Gao - 2023 - MARCEL mobile active rover chassis for enhanced locomotion/auto/Bouton和Gao - 2023 - MARCEL mobile active rover chassis for enhanced locomotion.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `MARCEL` 与当前课题在“主动内部关节提升轮式平台通过能力”的动机层面较高相关。
- 但其不作为当前 RL 环境配置主线文献，后续写动机与结构价值时再重点回看。

下一步：
- 继续把阅读重点收敛到 RL 环境配置相关文献上。


## 2026-03-23

已完成：
- 读取仓库启动上下文，确认当前文献工作应优先围绕 RL 环境与训练设计主线展开。
- 检查 `docs/literature/` 目录、文献目录索引和 `rl_env_reading_notes.md`。
- 按“直接涉及 RL 训练/策略设计”的标准，从现有文献中筛出 17 篇相关 PDF。
- 新建 `docs/literature/rl_training_strategy_pdfs_2026-03-23/`，并将筛选出的 PDF 复制到该目录中，便于后续集中阅读。

修改文件：
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前独立整理出的 RL 训练策略相关 PDF 目录为 `docs/literature/rl_training_strategy_pdfs_2026-03-23/`。
- 该目录当前包含 17 篇文献，覆盖 rough terrain vehicle、articulated robot、curriculum、sim-to-real、state estimator joint training 等主题。

下一步：
- 若需要进一步收敛，可在这 17 篇中再细分出“最贴近本课题完整车 RL baseline”的高优先级子集。

已完成：
- 将本轮讨论确定的两阶段 RL 训练主线写入项目记忆文件。
- 更新 `docs/current_status.md`，把旧的“速度跟踪/平地加入球铰”表述替换为新的两阶段目标。
- 更新 `docs/conversation_history.md`，固化阶段 1 与阶段 2 的职责边界、任务定义和研究含义。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 阶段 1 正式定义为“平地 + 本体感知 + 固定球铰 + 目标导向移动”。
- 阶段 2 正式定义为“球铰纳入控制 + 底层 PID 与逆运动学映射 + 多样地形 + 外部感知与本体感知融合”。

下一步：
- 按新的阶段 1 目标，重写 env 的 observation、reward、termination、reset 与目标采样逻辑。

已完成：
- 将当前项目工作区整理后准备同步到 GitHub 远端 `origin/main`。

修改文件：
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前本地仓库状态已与待推送内容对齐，准备作为最新项目快照上传到 GitHub。

## 2026-03-24

已完成：
- 优化了根目录 `IK_iteration.mlx` 的符号推导脚本。
- 为 `R01`、`u_i`、`R_local`、`R_w`、`w_i`、`R03`、`R_rpy`、`R_v`、`v_i`、约束方程、半角代换结果、分子分母、多项式以及 `A/B/C` 系数补充了命令行输出。
- 为关键表达式统一增加 `expand + simplify` 化简流程，便于将移相三角表达式尽量压缩为更标准的 `sin/cos` 形式后再核对文献公式。
- 重新打包生成更新后的 `IK_iteration.mlx`。

修改文件：
- `IK_iteration.mlx`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 live script 在每一步关键推导后都会显示结果，更适合逐步检查逆运动学推导链路。
- 当前脚本会先做展开再做符号化简，表达式可读性比原版更高。

下一步：
- 在 MATLAB 中实际运行 `IK_iteration.mlx`，确认本机符号工具箱对 `simplify(..., ''Steps'', 100, ''IgnoreAnalyticConstraints'', true)` 的输出形式满足预期。

## 2026-03-26

已完成：
- 对比 `USD/complete_car.usd` 与 `USD/complete_car_equivlent.usd` 的机器人本体层级和关节树。
- 新增 `scripts/isaac_sim/align_complete_car_structure_to_equivalent.py`，用于按 equivalent 主链清理 `complete_car.usd` 机器人子树。
- 按用户要求，仅在 `/World/complete_car_final` 及其 `joints/` 范围内执行结构树收敛。
- 删除了 12 个多余的 SPM 腿部刚体：
  - `spm1_leg1_proximal`、`spm1_leg1_distal`、`spm1_leg2_proximal`、`spm1_leg2_distal`、`spm1_leg3_proximal`、`spm1_leg3_distal`
  - `spm2_leg1_proximal`、`spm2_leg1_distal`、`spm2_leg2_proximal`、`spm2_leg2_distal`、`spm2_leg3_proximal`、`spm2_leg3_distal`
- 删除了 `joints/` 下对应的 12 个 fixed joint，使保留链路收敛为 `base -> virtual_z -> virtual_y -> platform`。
- 生成编辑前备份 `USD/complete_car.usd.spm_leg_cleanup.bak`。
- 复查修改结果，确认 `/World/complete_car_final` 下已不再包含上述腿部刚体，`joints/` 下也只保留 equivalent 主链所需关节。

修改文件：
- `USD/complete_car.usd`
- `USD/complete_car.usd.spm_leg_cleanup.bak`
- `scripts/isaac_sim/align_complete_car_structure_to_equivalent.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `complete_car.usd` 的机器人本体结构树已按 equivalent 主链收敛，不再保留多余的 SPM 腿部层级。
- 这一步只处理机器人本体层级，不涉及场景层 `/Environment`、`/Render`、`/physicsScene` 以及根级 `/visuals`、`/colliders`、`/meshes`。
- 当前资产仍存在未解决问题，包括轮子零速 drive、损坏的 visual 引用、远端 `Example_Rotary` 引用和内嵌 `PhysicsScene` 风险。

下一步：
- 在新的结构树基础上继续清理 `complete_car.usd` 的 drive、损坏引用与 replicated 不兼容项，再重新验证 `Play` 时是否仍出现 transform 爆炸。

已完成：
- 新增 `scripts/isaac_sim/add_wheel_friction_material.py`，用于给 `complete_car.usd` 的 6 个轮子 collision 子树统一绑定 physics material。
- 在 `USD/complete_car.usd` 中新增共享材质 `/World/complete_car_final/Looks/wheel_physics_material`。
- 将该材质参数设置为：`staticFriction=1.0`、`dynamicFriction=1.0`、`frictionCombineMode=multiply`。
- 将该材质绑定到 6 个轮子的 `collisions` 子树。
- 生成编辑前备份 `USD/complete_car.usd.wheel_friction.bak`。
- 复查确认材质属性和 6 个 wheel collision 绑定均已写入 USD。

修改文件：
- `USD/complete_car.usd`
- `USD/complete_car.usd.wheel_friction.bak`
- `scripts/isaac_sim/add_wheel_friction_material.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `complete_car.usd` 的 6 个轮子已不再依赖默认地面摩擦，而是显式使用统一的轮胎 physics material。
- 这一步只增加轮子接触摩擦参数，不处理轮子 drive、visual 引用错误、远端 `Example_Rotary` 引用和 `PhysicsScene` 风险。

已完成：
- 将 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 从原始关节直控脚本改为第一版 Isaac Sim IK 键控验证脚本。
- 将键盘控制对象从“6 个球铰关节角”改为“前后两个平台目标姿态”。
- 接入 `IK_3RRR_Spherical`，实现每帧根据目标姿态解算前后两组 3 电机角，并映射到 6 个球铰关节目标。
- 保留轮子速度控制，并增加周期性调试输出：`rpy_des / q_ik / q_sim / residual`。
- 将资产路径切换到 `USD/complete_car.usd`，机器人根路径切换到 `/World/complete_car_final`。
- 对更新后的脚本执行了 `python3 -m py_compile` 语法检查，结果通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已有一个可用于“姿态目标 -> IK -> 球铰目标 -> Isaac Sim 读回对比”的第一版键控验证脚本。
- 当前脚本仍使用第一轮假设的 `IK -> sim joint` 顺序、`signs` 和 `biases`，后续需要结合实际运动方向做标定。

已完成：
- 为 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 增加 CSV 日志功能。
- 新增日志目录 `results/ik_keyboard_logs/`，脚本启动时会自动创建时间戳日志文件。
- 日志内容包含 `rpy_des`、`q_ik`、`q_sim`、前后球铰残差以及 `ik_error` 字段，并在每次快照打印时同步落盘。
- 在终端调试输出中增加 `log_path` 字段，便于定位本次运行对应的日志文件。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 IK 键控验证脚本除终端快照外，还能把关键结果稳定保存到 CSV，便于后续直接读取和复盘。

## 2026-03-26

已完成：
- 重新梳理了 `test_ik_keyboard.py` 的验证目标，确认用户当前需要的是“静态几何一致性验证”，而不是“姿态命令下发后由 drive 跟踪”的控制执行验证。
- 将 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 改为新的静态一致性验证逻辑：
  - 键盘直接摆动 6 个球铰等效关节角
  - 每帧读取前后 platform 相对各自 base 的当前姿态
  - 将当前姿态送入 `IK_3RRR_Spherical`
  - 将 IK 预测关节角与 Isaac Sim 当前实际关节角直接对比
- 在脚本中新增前后 `base/platform` prim 路径读取、相对旋转矩阵提取，以及 `Rz(yaw) @ Ry(pitch) @ Rx(roll)` 对应的 ZYX 欧拉角反解。
- 保留并适配了 CSV 日志落盘，日志现记录当前平台姿态、手动关节命令、IK 预测关节角、Isaac Sim 实际关节角、残差和 `ik_error`。
- 对修改后的脚本执行了 `python3 -m py_compile` 语法检查，结果通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `test_ik_keyboard.py` 不再把 IK 输出回写给 Isaac Sim 关节执行，而是作为“当前姿态 -> IK 预测关节角”的几何一致性验证脚本使用。
- 之后读取日志时，应把 `q_ik` 与 `q_sim` 的差异理解为静态映射误差、坐标定义误差、零位/符号/偏置标定误差，而不再理解为 drive 跟踪误差。

下一步：
- 运行新的 `test_ik_keyboard.py`，分别做前球铰和后球铰的单轴扫描，进一步标定 `IK_SIGNS_*`、关节顺序和偏置。
## 2026-03-27

已完成：
- 读取并分析了 `results/ik_keyboard_logs/ik_keyboard_2026-03-27_09-58-33.csv`。
- 统计确认该日志共 160 条采样，`ik_error` 全程为空，6 个 residual 全为 `0.0`。
- 统计确认 `joint_cmd` 与 `q_sim` 的误差整体较小，说明 Isaac Sim 关节执行跟踪基本正常。
- 统计确认 `q_ik` 与 `q_sim` 长期存在几十度级系统偏差，前后球铰都存在，且并非只出现在瞬态阶段。
- 结合 `test_ik_keyboard.py` 与 `IK_model.py` 的当前实现，确认本轮主要问题是 IK 比较链路中的零位/分支/映射定义未与仿真关节约定对齐，而不是 IK 方程求解失败。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 IK 键盘验证脚本的 residual 为 0，只能说明“给定姿态存在一组数学合法解”，不能说明“该解已映射回 Isaac Sim 当前实际关节分支”。
- 后续应优先标定零命令姿态下的球铰零位、分支选择和 `signs/biases`，再继续用该脚本做一致性验证。

下一步：
- 在 `test_ik_keyboard.py` 中把当前零命令姿态作为映射基准重新标定，并验证 `read_relative_rpy -> IK -> map_to_sim_joints -> q_sim` 是否能闭合。
已完成：
- 直接检查 `USD/complete_car.usd` 的 SPM 主链层级，确认零位姿态偏置固定存在于 `spm*_base -> spm*_spherical_virtual_z` 之间。
- 在 `USD/complete_car.usd` 中新增 `/World/complete_car_final/spm1_base/spm1_base_ref` 与 `/World/complete_car_final/spm2_base/spm2_base_ref`。
- 新增脚本 `scripts/isaac_sim/add_spm_base_reference_frames.py`，用于为当前 complete car 资产补写上述两个参考系，并自动生成 `USD/complete_car.usd.base_ref.bak` 备份。
- 重新打开 stage 验证新增 prim 后，确认 `spm1_base_ref -> spm1_platform` 与 `spm2_base_ref -> spm2_platform` 的相对 ZYX `rpy` 均已接近零。

修改文件：
- `USD/complete_car.usd`
- `scripts/isaac_sim/add_spm_base_reference_frames.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 USD 已具备两个固定在 base 上、且在机械零位与 platform 轴方向对齐的姿态参考系，可作为后续平台 `rpy` 读取的正确起点。
- 后续 `test_ik_keyboard.py` 应切换到 `spm*_base_ref -> spm*_platform` 读取零位姿态，而不应继续直接使用 `spm*_base -> spm*_platform`。

下一步：
- 在 `test_ik_keyboard.py` 中改用 `spm*_base_ref` 作为姿态参考 frame，并重新验证零位 `rpy` 与 IK 输入链路。
已完成：
- 将 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 的平台姿态读取基准从 `spm*_base -> spm*_platform` 改为 `spm*_base_ref -> spm*_platform`。
- 保留原有 `Rz(yaw) -> Ry(pitch) -> Rx(roll)` 的 ZYX 欧拉角分解与 IK 求解逻辑，仅替换姿态参考 frame。
- 对修改后的脚本执行 `python3 -m py_compile`，语法检查通过。
- 使用与脚本一致的读取公式重新检查机械零位，确认前球铰 `rpy≈[5.493e-06, 6.94e-07, -2.571e-06] deg`、后球铰 `rpy≈[-1.4661e-05, -1.3655e-05, 4.951e-06] deg`，可视为零。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 IK 静态验证脚本的 `rpy` 输入参考系已与 USD 中补入的零位参考 frame 对齐。
- 后续若 `q_ik` 与 `q_sim` 仍不一致，应优先继续检查 `IK_model.py` 输出到仿真关节的零位、分支与符号/偏置映射，而不是继续怀疑平台姿态读取坐标系。

下一步：
- 在已对齐的姿态输入前提下，继续标定 `IK_SIGNS_FRONT/REAR`、`IK_BIASES_FRONT/REAR` 与分支初值。
已完成：
- 在 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 中加入启动零偏标定逻辑。
- 脚本启动后会先对 6 个球铰保持零目标、对 6 个轮子保持零轮速，先静置 `240` 步，再连续采样 `120` 步，对前后 `spm*_base_ref -> spm*_platform` 的原始 `rpy` 求均值作为 `rpy_bias`。
- 后续 IK 输入改为 `raw_rpy - rpy_bias`，不再直接使用原始相对姿态。
- CSV 日志新增 `raw / bias / corrected` 三组平台 `rpy` 字段，便于区分物理稳态偏置与送入 IK 的校正姿态。
- 对修改后的脚本执行 `python3 -m py_compile`，语法检查通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 IK 键控验证脚本已具备启动零偏标定能力，可直接用新日志判断“原始平台姿态偏置”和“校正后送入 IK 的姿态”是否分离成功。

下一步：
- 重新运行脚本生成新日志，先检查 `front/rear_*_cur_deg` 是否在零命令稳态下接近 0，再继续分析 `q_ik` 与 `q_sim` 的剩余差异。
已完成：
- 读取并分析 `results/ik_keyboard_logs/ik_keyboard_2026-03-27_17-20-44.csv`，验证加入启动零偏标定后的新日志格式。
- 统计确认零命令稳态下，平台原始姿态 `raw_rpy` 仍存在小幅物理偏置，但校正后 `corrected_rpy` 已明显逼近零。
- 前平台 `corrected_rpy` 均值约为 `[0.013734, -0.010834, -0.00631] deg`，后平台约为 `[-0.001878, 0.000419, 0.003239] deg`。
- 同时确认 `q_ik` 与 `q_sim` 在零命令稳态下仍有系统差异，说明当前主问题已从姿态读取收敛到关节映射标定。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 启动零偏标定已基本解决“平台 `rpy` 输入不为零”的问题，后续应优先继续标定 `IK_SIGNS_*`、`IK_BIASES_*` 与分支初值。

下一步：
- 在零偏校正保持不变的前提下，针对前后球铰分别做单轴扫描，继续拟合 `q_ik -> q_sim` 的零位、符号和偏置。
已完成：
- 重写 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`，将其从“关节直控 + 反算对照”脚本改为“姿态目标 -> IK -> joint target -> articulation controller 跟踪”验证脚本。
- 键盘输入现直接修改前后平台的 `roll/pitch/yaw` 目标，不再直接修改 6 个球铰关节角。
- 启动阶段新增联合零位标定：同时估计平台 `rpy` 零偏和 Sim 当前球铰关节零位，并将后者作为 `map_to_sim_joints()` 的零位偏置。
- 控制链中新增两级一阶平滑：先对姿态目标做平滑，再对 IK 生成的 joint target 做平滑，最后再把 `q_cmd` 发送给 articulation controller。
- 日志字段改为完整记录 `raw/meas/des/cmd` 姿态、`q_ik/q_cmd/q_sim`、joint 跟踪误差以及 IK residual。
- 对重写后的脚本执行 `python3 -m py_compile`，语法检查通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `test_ik_keyboard.py` 已能直接验证三个关键问题：姿态目标是否稳定送进 IK、IK 生成的 joint target 是否和零位标定一致、articulation controller 是否能平滑跟踪 joint target。

下一步：
- 实际运行新脚本并读取新日志，检查 `rpy_des -> rpy_meas`、`q_cmd -> q_sim` 和 `track_err` 三条误差曲线，再决定是否需要继续调 `IK_SIGNS_*`、姿态/关节平滑系数或底层 drive 参数。
已完成：
- 读取并分析 `results/ik_keyboard_logs/ik_keyboard_2026-03-27_18-53-34.csv`，评估重构后 `test_ik_keyboard.py` 的整条控制链。
- 确认 `q_cmd -> q_sim` 跟踪效果较好，前后球铰关节平均绝对跟踪误差均在约 `0.02~0.07 deg` 量级，说明 articulation controller 可以平滑跟踪 joint target。
- 确认 IK 全程可解，`residual` 为 0，`ik_error` 为空。
- 同时确认 `rpy_cmd -> rpy_meas` 误差很大，前平台平均绝对误差约 `[5.62, 4.69, 4.71] deg`，后平台约 `[2.42, 0.50, 2.20] deg`，且单轴姿态命令会激发错误轴或相反方向。
- 据此得出当前关键结论：问题不在关节跟踪，而在“IK 电机角”和“USD 等效球铰关节坐标”不是同一组坐标，无法直接把 IK 输出当作现有等效模型的关节目标。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现阶段已验证：IK 可稳定求解，joint target 可被底层平滑跟踪；但姿态目标通过 IK 直接驱动当前等效球铰模型这条路线在语义上不成立。

下一步：
- 回到研究层重新决定架构：是保留等效球铰姿态控制并让 IK 仅作为真实电机角映射层，还是重建一个真实电机坐标可控的下层模型。
已完成：
- 明确了当前仿真建模的语义：USD 中 3 个等效球铰关节角本身就是移动平台姿态坐标，而不是 3-RRR 真实电机角代理。
- 因此重新界定 RL 与 IK 的角色分工：RL 在仿真中应直接控制等效球铰姿态角；IK 只负责把平台姿态并行映射为真实机构电机角，供后续可能的实物阶段使用。
- 据此停止继续沿“IK 电机角直接驱动当前等效球铰模型”这条路线投入。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 RL 主线重新收敛为：直接控制 3 个等效球铰姿态角和轮子动作；IK 暂不进入仿真闭环控制。

下一步：
- 回到 RL 环境设计与实现，明确动作空间、观测和奖励如何围绕等效球铰姿态控制来组织。

## 2026-03-28

已完成：
- 按 `literature-reading-notes` 的结构化方式整理 `Ha 等 - 2025 - Learning-based legged locomotion: State of the art and future perspectives`。
- 基于原始 PDF 提炼出该综述的整体逻辑、`MDP` 组成、训练框架、`sim-to-real` 路线以及 `control + learning` 组合方式。
- 将阅读笔记落盘到对应文献目录下，保持与现有 `Wiberg 2022`、`Xu 2024` 笔记一致的仓库组织方式。
- 同步更新项目状态与长期会话记忆，避免后续重复整理该综述。

修改文件：
- `docs/literature/mineru_output/Ha 等 - 2025 - Learning-based legged locomotion State of the art and future perspectives/auto/reading_notes.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已形成一份可直接复用的综述型阅读笔记，重点不是复述全文，而是为本课题提炼任务设计与训练组织方法。
- 该综述支持当前已确定的两阶段主线：先做最小可训练 baseline，再逐步加入外感知、分层控制和更强的 sim-to-real 机制。

下一步：
- 若继续沿文献主线推进，可把 `Ha 2025` 与 `Wiberg 2022`、`Xu 2024` 做一次横向对比，专门整理“baseline 如何定义、复杂度如何分阶段引入”的共性结论。

## 2026-03-30

已完成：
- 检查用户新增的地形相关脚本，确认有效源码/文档为 `mgdp_terrain_preview.py`、`run_terrain_preview.sh`、`README.md`，并将其统一整理到 `scripts/isaac_sim/terrain_preview/`。
- 修正 `mgdp_terrain_preview.py` 的仓库根路径解析逻辑，避免默认导出 USD 路径错误指向仓库外。
- 修正 `README.md` 中旧的启动路径示例，使其与实际目录 `scripts/isaac_sim/terrain_preview/` 一致。
- 对地形脚本执行静态校验：`python3 -m py_compile scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py` 通过，`bash -n scripts/isaac_sim/terrain_preview/run_terrain_preview.sh` 通过。
- 实际尝试使用 `/home/lbz/isaac-sim/python.sh` 以 `--headless --frames 1 --gallery stage1` 启动地形预览脚本。

修改文件：
- `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
- `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`
- `scripts/isaac_sim/terrain_preview/README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前地形预览脚本的仓库内路径与启动包装关系已整理清楚，脚本层不存在语法错误。
- 这次实际启动未能进入场景执行阶段，阻塞来自本机 Isaac Sim 图形环境：日志报错 `Vulkan 1.1 is not supported`、`no CUDA-capable device is detected`，随后段错误退出。
- 因此当前可得结论是：脚本包本身可以作为 Isaac Sim 启动入口使用，但这台机器当前不具备完成 Isaac Sim 启动的图形/驱动条件。

下一步：
- 若要继续验证窗口显示或 USD 导出，应在具备可用 Vulkan / CUDA / 显示环境的 Isaac Sim 主机上执行 `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`。

已完成：
- 新增 `scripts/isaac_sim/terrain_preview/terrain_builder.py`，将地形构建逻辑从单独预览脚本中抽成可复用模块。
- 重写 `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`，改为复用公共地形模块构建 gallery。
- 修改 `scripts/isaac_sim/control_keyboard.py`，使其在打开 `USD/complete_car.usd` 后、`World.reset()` 前可同步向同一 stage 注入一块地形。
- 当前 `control_keyboard.py` 新增 `--terrain`、`--terrain-seed` 参数；默认地形为 `slope_ramp`，也可切换为 `stairs_up`、`gap`、`corridor` 等，或用 `--terrain none` 禁用。
- 为避免已有地面把 `gap` 之类地形覆盖，脚本会优先尝试关闭若干常见默认 ground prim。
- 对 `control_keyboard.py`、`mgdp_terrain_preview.py`、`terrain_builder.py` 执行 `python3 -m py_compile`，语法检查通过。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
- `scripts/isaac_sim/terrain_preview/terrain_builder.py`
- `scripts/isaac_sim/terrain_preview/README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现在不需要分别启动两个 Isaac Sim 进程；直接运行 `control_keyboard.py` 就可以把车辆和单块地形放进同一个场景里做键盘联调。
- 该改动目前已完成静态校验，但由于当前主机的 Isaac Sim 图形环境仍有 Vulkan/CUDA 阻塞，尚未在本机完成实际窗口联调验证。

下一步：
- 在可正常启动 Isaac Sim 的主机上优先测试 `python3 scripts/isaac_sim/control_keyboard.py --terrain slope_ramp`，确认车辆初始位置、地面关闭逻辑和碰撞行为符合预期。

已完成：
- 定位 GitHub 推送失败原因，确认不是 SSH 认证问题，而是 `Drawing/完整小车等效串联.SAT` 超过 GitHub 普通仓库 100 MB 单文件限制。
- 按当前新要求将 `.SAT` 文件加入根目录 `.gitignore`，后续不再作为普通 Git 提交内容上传。
- 同步把这一推送约束写入项目状态与长期会话记忆，避免后续再次因为 `.SAT` 阻塞整仓上传。

修改文件：
- `.gitignore`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现阶段仓库的普通 Git 上传路径应排除 `.SAT` 原始 CAD 文件；否则会再次触发 GitHub 预接收钩子拒绝。

下一步：
- 从最近一次本地提交中移除已纳入历史的 `.SAT` 文件，重做提交并重新推送到 `origin/main`。

## 2026-03-30

已完成：
- 检查 `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh` 的执行失败原因，确认直接 `./scripts/...` 报“权限不够”是因为脚本缺少执行位，而不是 Bash 语法错误。
- 在本机实际文件系统中确认可用 Isaac Sim 启动器路径为 `/home/ubuntu/isaacsim/python.sh`，不是脚本中旧的 `/home/lbz/isaac-sim/python.sh`。
- 将 `run_terrain_preview.sh` 的默认 `ISAAC_SIM_ROOT` 修正为 `/home/ubuntu/isaacsim`，并同步更新 `scripts/isaac_sim/terrain_preview/README.md` 中的说明。
- 同步更新项目状态与长期会话记忆，避免后续继续沿用旧路径判断脚本不可用。

修改文件：
- `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`
- `scripts/isaac_sim/terrain_preview/README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前地形预览包装脚本的默认 Isaac Sim 路径已与本机真实安装位置对齐。
- 修复后若仍无法启动 Isaac Sim，应优先归因为本机 Vulkan / CUDA / 显示环境问题，而不是脚本权限或默认路径问题。

下一步：
- 给 `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh` 补上执行权限后，直接用 `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --gallery stage1` 做一次本机验证。

## 2026-03-30

已完成：
- 复现并定位 `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh` 在激活 `env_isaacLab` 时的真实报错链：不是地形脚本逻辑错误，而是 `run_terrain_preview.sh` 继承了 `CONDA_*` 环境变量，且 `mgdp_terrain_preview.py` 在 `SimulationApp` 初始化前就导入了 `omni.timeline`。
- 修改 `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`，在调用 Isaac Sim `python.sh` 之前主动 `unset` 常见 `CONDA_*` 变量。
- 修改 `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`，改为先创建 `SimulationApp`，再导入 `omni.timeline`、`omni.usd` 与 Isaac Sim 相关模块。
- 重新执行 `python3 -m py_compile scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py` 与 `bash -n scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`，静态检查通过。
- 实际执行 `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --headless --frames 1 --gallery stage1`，本次已成功跑通并生成 `outputs/isaacsim/mgdp_terrain_stage1.usd`。

修改文件：
- `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
- `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前地形预览脚本已经可以从激活的 `env_isaacLab` shell 直接通过包装脚本启动，不再需要用户手工先 `conda deactivate`。
- 之前的 `ModuleNotFoundError: No module named 'omni.timeline'` 已被修复。
- 当前主机在 Isaac Sim 启动日志里仍会出现 GPU / CUDA / 显示相关警告，但至少对当前 `--headless --frames 1 --gallery stage1` 的 USD 导出路径不再构成阻塞。

下一步：
- 若要继续验证更多 gallery，可直接执行 `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --gallery both`，或在 headless 模式下继续导出其他地形 USD。

## 2026-03-30

已完成：
- 复现 `python scripts/isaac_sim/control_keyboard.py --terrain none` 的失败链路，先确认原始报错不是地形逻辑，而是当前脚本写死了错误的机器人根 prim。
- 在宿主 Isaac Sim 下重新检查 `USD/complete_car.usd`，确认 `/World/complete_car_final` 不存在，当前真实机器人根路径仍是 `/World/complete_car_alternative`。
- 修改 `scripts/isaac_sim/control_keyboard.py`，将 `ROBOT_PRIM_PATH` 改为 `/World/complete_car_alternative`。
- 给 `control_keyboard.py` 加入从 conda shell 自动重启到宿主 `/home/ubuntu/isaacsim/python.sh` 的启动链，避免继续在错误的 Python/Isaac Sim 组合下运行。
- 给 `control_keyboard.py` 加入 `--headless`、`--frames` 与无显示环境自动 headless smoke 验证路径。
- 去掉脚本内此前加入的 `--portable-root` 注入；实测该路径会让本机 host 启动明显变慢甚至看似卡住，而使用宿主默认缓存路径可快速完成启动。
- 实际验证 `python -u scripts/isaac_sim/control_keyboard.py --terrain none --headless --frames 1`，本次已正常退出且返回码为 0。
- 实际验证 `timeout --signal=SIGINT 20s python -u scripts/isaac_sim/control_keyboard.py --terrain none`，本次脚本成功进入交互态并持续运行到超时，返回码为 124，说明不是崩溃退出。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `control_keyboard.py` 当前可用的运行根 prim 是 `/World/complete_car_alternative`。
- 当前机器上要稳定启动该脚本，应优先让它走宿主 `/home/ubuntu/isaacsim/python.sh`，而不是继续依赖激活中的 conda Python 解释器。
- 当前机器上不应再给该脚本强行注入新的 portable-root；这会放大 Isaac Sim 首次缓存初始化开销，影响“先跑起来”的目标。

下一步：
- 若要继续人工键盘联调，可直接执行 `python scripts/isaac_sim/control_keyboard.py --terrain none` 或替换为其他 `--terrain` 选项。

## 2026-03-30

已完成：
- 解释并复核 `scripts/isaac_sim/control_keyboard.py` 的当前键盘控制逻辑，确认 `W/S` 为六轮统一前进/后退轮速，`A/D` 为左右差速转向，数字小键盘为两个等效球铰的 6 个姿态自由度增量控制。
- 检查轮速与球铰控制链路，确认两者都已经有一阶平滑；其中轮速与球铰平滑系数此前均为 `0.20`。
- 诊断“前进后退像拖动不是轮子在转”的原因，确认不是轮子命令失效，而是 `--terrain none` 时缺少有效 ground contact，导致地面接触链路不成立。
- 修改 `scripts/isaac_sim/control_keyboard.py`：在 `--terrain none` 下自动创建 `ground plane`，并给地面与六个轮子碰撞体统一绑定 `static_friction=0.5`、`dynamic_friction=0.5` 的共享物理材质。
- 同步下调键盘联调默认速度与响应：`WHEEL_LINEAR_SPEED=2.5`、`WHEEL_TURN_SPEED=1.0`、`BALL_JOINT_DELTA=0.005`、`WHEEL_VELOCITY_SMOOTHING=0.10`、`BALL_POSITION_SMOOTHING=0.10`。
- 实际执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，静态检查通过。
- 实际执行 `timeout 90s python -u scripts/isaac_sim/control_keyboard.py --terrain none --headless --frames 1`，本次返回码为 `0`。
- 额外编写并执行宿主 Isaac Sim 诊断脚本，验证补地面与摩擦后小车在 120 步内前进约 `0.36 m`，且六个轮子角速度始终接近 `1 rad/s`。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `control_keyboard.py` 在 `--terrain none` 下不再是“无地面接触”的状态，车体可通过轮地摩擦产生真实推进，而不是仅表现为拖动感。
- 当前脚本内车轮速度和平滑、球铰步进和平滑都已下调，默认联调速度明显比之前更温和。
- 当前终端环境下 Isaac Sim 启动较慢且会伴随无 GPU、远端 `Example_Rotary` 引用等警告，但这些不影响本轮键盘控制修复结论。

下一步：
- 在具备可用图形环境的 Isaac Sim 主机上直接执行 `python scripts/isaac_sim/control_keyboard.py --terrain none` 做一次窗口联调，重点观察轮子可视旋转、底盘实际位移和球铰姿态响应是否与新的减速参数一致。

## 2026-04-02

已完成：
- 新增 `scripts/isaac_sim/preview_stage1_tile.py`，提供 Isaac Sim 中单独查看单个 `stage1` tile 的入口。
- 脚本当前支持两种选块方式：`--row/--col` 复现当前课程地图中的某一块，或 `--terrain-name` 直接指定某类地形。
- 为避免 `--list-terrains` 在 Isaac Sim 启动前触发整条任务包导入链，脚本改为按文件路径直接加载 `stage1_terrain.py`，不再依赖完整包导入。
- 脚本默认会删除 `TerrainImporterCfg(terrain_type="plane")` 自动生成的默认 plane，并只导入当前单块 tile mesh。
- 脚本默认不实例化整车，只有显式传入 `--spawn-car` 时才加载机器人资产。
- 已执行 `python3 -m py_compile scripts/isaac_sim/preview_stage1_tile.py`，静态检查通过。
- 已执行 `python scripts/isaac_sim/preview_stage1_tile.py --list-terrains`，当前可正常列出全部 `stage1` terrain 名称。
- 已执行 `timeout 60s python -u scripts/isaac_sim/preview_stage1_tile.py --headless --device cpu --frames 1 --row 0 --col 0`，本次返回码为 `0`。

修改文件：
- `scripts/isaac_sim/preview_stage1_tile.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现在已经有一个比整张大地图 preview 更直接的检查入口，可优先用于核对单块地形的几何、原点和相机视角。
- `--list-terrains` 当前已不再受 `pxr` 提前导入问题影响。
- 当前这台无 GPU / 无正常显示环境的机器上，单 tile headless 冒烟可以正常退出，但不适合把窗口显示效果是否完全正确作为唯一验证标准。

下一步：
- 在有正常图形环境的 Isaac Sim 会话中执行 `python scripts/isaac_sim/preview_stage1_tile.py --row <r> --col <c>`，逐块核对 `stage1` 各类地形的真实视觉效果与坐标系位置。

## 2026-04-02

已完成：
- 按用户要求将 `scripts/isaac_sim/preview_stage1_tile.py` 的默认行为从“单块预览”改为“同时显示所有单独 tile”。
- 当前默认启动脚本时，会把 `stage1` 当前课程地图的全部 `20 x 10 = 200` 个 tile 作为独立 mesh 导入 Isaac Sim，并按固定 `tile-spacing` 分开摆放，不再拼成一整张连续地形。
- 保留旧能力：新增 `--single-tile` 开关，仍可按 `--row/--col` 只看某一块；`--terrain-name <name>` 也仍可按地形名单独生成一块。
- 调整脚本内部 origin 可视化逻辑：不再依赖 `TerrainImporter.configure_env_origins()`，而是直接为每个独立 tile 生成 1 个 frame marker。
- 当前所有独立 tile 的 prim 路径统一为 `/World/terrain/tile_rXX_cYY_<terrain_name>`，便于在 Stage 面板中逐块定位。
- 已执行 `python3 -m py_compile scripts/isaac_sim/preview_stage1_tile.py`，静态检查通过。
- 已执行 `python scripts/isaac_sim/preview_stage1_tile.py --help` 与 `python scripts/isaac_sim/preview_stage1_tile.py --list-terrains`，参数与地形枚举正常。
- 已执行 `timeout 120s python -u scripts/isaac_sim/preview_stage1_tile.py --headless --device cpu --frames 1`，gallery 默认路径返回码为 `0`。
- 已执行 `timeout 90s python -u scripts/isaac_sim/preview_stage1_tile.py --headless --device cpu --frames 1 --single-tile --row 0 --col 0`，单块回退路径返回码为 `0`。
- 本轮 headless 校验日志已落盘：
  - `results/preview_stage1_tile_gallery.log`
  - `results/preview_stage1_tile_single.log`

修改文件：
- `scripts/isaac_sim/preview_stage1_tile.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现在直接运行 `python scripts/isaac_sim/preview_stage1_tile.py`，进入的就是“所有独立 tile 分离展示”模式，而不是旧的单块预览模式。
- 若后续还需要只看某一块，不需要再写新脚本，直接加 `--single-tile` 即可。
- 当前这台无 GPU / 无图形显示环境的机器上，headless 返回码可以证明脚本链路可跑通，但窗口里的最终视觉效果仍应以图形环境下的 Isaac Sim 实际画面为准。

下一步：
- 在有正常图形界面的 Isaac Sim 会话里直接执行 `python scripts/isaac_sim/preview_stage1_tile.py`，确认 200 个独立 tile 的相对布局、坐标系和相机总览是否符合预期；若太密，可再调 `--tile-spacing`。

## 2026-04-03

已完成：
- 新增 `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`，用于直接实例化真实训练任务 `Complete-Car-Rl-Training-v0`，保存训练时的 stage USD，并导出完整 prim tree 与 `/World/terrain` 子树。
- 基于用户在可用 GPU 机器上导出的 `training_stage_num_envs10.usda`、`training_stage_num_envs10.usda.tree.txt` 与 `training_stage_num_envs10.usda.terrain_tree.txt` 复核训练场景结构。
- 确认训练环境中真正的地形 prim 只有 `/World/terrain/stage1` 一张；用户在窗口里看到的“多张地图”不是训练脚本重复导入地形，而是 `USD/complete_car.usd` 中残留的 `/World/terrain_preview` 被每个 `env_i/Robot` 引用复制。
- 新增 `scripts/isaac_sim/remove_complete_car_terrain_preview.py`，为 `USD/complete_car.usd` 创建备份 `USD/complete_car.usd.terrain_preview_cleanup.bak` 后，移除 `/World/terrain_preview` 子树。
- 重新打开 `USD/complete_car.usd` 验证，确认 `/World/terrain_preview` 已无效；当前资产顶层 prim 保持为 `/World`、`/Render`、`/physicsScene`。
- 按用户要求在 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py` 的 `terrain_dict` 首项加入 `flat: 0.2`。
- 同步在 `make_tile_by_name(...)` 中补上 `flat -> make_flat_tile(...)` 分支，并调整 `slope down` 的区间中点计算，使插入 `flat` 后现有 `choice` 逻辑仍能正确落入 `slope down` 区间。
- 执行 `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`，静态检查通过。
- 复核当前默认 `num_cols = 10` 下的列映射，结果已变为 `flat x2 -> slope down x2 -> pyramid x2 -> stairs down x2 -> stairs up x2`。

修改文件：
- `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
- `scripts/isaac_sim/remove_complete_car_terrain_preview.py`
- `USD/complete_car.usd`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 训练时的真实大地图只有 `/World/terrain/stage1`，之后若再看到多张“地图”，应优先排查机器人资产是否夹带 preview 几何，而不是先改训练地形导入逻辑。
- `USD/complete_car.usd` 当前已经清理为机器人资产，不再应包含 `terrain_preview`。
- 当前 Stage1 在不改 `choice` 框架的前提下，首个地形类型已改为 `flat`，且权重按用户要求设为 `0.2`。

下一步：
- 在用户有可用 GPU 的 Isaac Sim 会话里重新导出一次训练 stage，确认新的 `training_stage_num_envs10.usda.tree.txt` 中不再出现 `env_i/Robot/terrain_preview`。

## 2026-04-03

已完成：
- 按用户要求新增独立预览脚本 `scripts/isaac_sim/preview_stage1_last_six.py`，用于在不修改 `stage1_terrain.py` 的前提下，单独查看当前 stage1 地形列表最后六种地形的外观。
- 新脚本沿用 `preview_stage1_tile.py` 的总体方式：直接按文件路径加载 `stage1_terrain.py`，删除 `TerrainImporterCfg(terrain_type="plane")` 自动生成的默认 plane，将每个地形以独立 mesh 导入 Stage，并支持 `--show-origin`、`--spawn-car`、`--save-usd` 等常用预览参数。
- 当前 gallery 默认加载的后六种地形已确认是：`hurdle`、`gap`、`ramp`、`beam`、`new stairs down`、`pit`。
- 已执行 `python3 -m py_compile scripts/isaac_sim/preview_stage1_last_six.py`，静态检查通过。
- 已执行 `python scripts/isaac_sim/preview_stage1_last_six.py --list-terrains`，地形枚举正常输出。

修改文件：
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现在查看 `hurdle / gap / ramp / beam / new stairs down / pit` 的几何外观，不再需要临时改动训练用 `terrain_dict` 顺序或权重。
- 该需求已有独立脚本入口，后续若要导出对应 USD 或在窗口里逐块看这六类地形，可直接复用该脚本。

下一步：
- 在可用 GPU / 图形环境的 Isaac Sim 会话中执行 `python scripts/isaac_sim/preview_stage1_last_six.py --device cuda:0`，直接观察这六种地形的窗口效果；若需要离线核对 Stage 结构，可再加 `--save-usd <path>.usda`。

## 2026-04-03

已完成：
- 按用户进一步澄清后的要求，撤回对 `scripts/isaac_sim/preview_stage1_tile.py` 职责的改动，将其恢复为原先的 `20 x 10` 全课程 tile 分离画廊入口。
- 同时改造 `scripts/isaac_sim/preview_stage1_last_six.py`，使其在保持“只看后六种地形”目标不变的前提下，也采用与 `preview_stage1_tile.py` 相同的 `20 x 10` tile 画廊形式。
- 当前 `preview_stage1_last_six.py` 的 gallery 只使用 `terrain_names[-6:]`：`hurdle`、`gap`、`ramp`、`beam`、`new stairs down`、`pit`；列方向按这六类循环分配，行方向继续用于展示不同难度层。
- 已执行 `python3 -m py_compile scripts/isaac_sim/preview_stage1_tile.py scripts/isaac_sim/preview_stage1_last_six.py`，静态检查通过。
- 已执行 `python scripts/isaac_sim/preview_stage1_tile.py --list-terrains`，确认旧脚本再次输出完整 terrain 集。
- 已执行 `python scripts/isaac_sim/preview_stage1_last_six.py --list-terrains`，确认新脚本仅输出后六种地形。

修改文件：
- `scripts/isaac_sim/preview_stage1_tile.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `preview_stage1_tile.py` 现在再次代表“全部 stage1 tile 画廊”，不再被重定向到后六种地形预览。
- `preview_stage1_last_six.py` 现在是“后六种地形版的 20 x 10 tile 画廊”，更符合用户想直接比较这些尾部地形几何外观的用途。

下一步：
- 在有可用 GPU / 图形环境的 Isaac Sim 会话中执行 `python scripts/isaac_sim/preview_stage1_last_six.py --device cuda:0`，直接观察这套后六种地形的 `20 x 10` 画廊效果。

## 2026-04-03

已完成：
- 按用户要求调整 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py` 前段地形阈值，使默认 `num_cols = 10` 下的前 10 列映射变为：
  - 第 1 列 `flat`
  - 第 2 列 `slope down`
  - 第 3 列 `slope up`
  - 第 4-5 列 `uneven rough`
  - 第 6-7 列 `stairs down`
  - 第 8-9 列 `stairs up`
  - 第 10 列 `discrete obstacles`
- 在 `terrain_dict` 中新增独立地形名 `slope up`，并把 `slope down` / `slope up` 分别固定到 `descending=True` / `descending=False`，不再沿用原先在同一 `"slope down"` 区间内部再二分出上下坡方向的逻辑。
- 将原公开地形名 `"pyramid"` 重命名为 `"uneven rough"`；当前保留原内部生成函数 `make_pyramid_tile(...)`，但对外列出的 terrain name 已改为更符合其“起伏粗糙、不规则变化”外观的名字。
- 已执行 `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`，静态检查通过。
- 已执行一次映射核对，当前默认 10 列实际输出为：
  - `['flat', 'slope down', 'slope up', 'uneven rough', 'uneven rough', 'stairs down', 'stairs down', 'stairs up', 'stairs up', 'discrete obstacles']`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现在前 10 列地形分配已经和用户指定顺序一致。
- 原先视觉上容易误解的 `"pyramid"` 名称已从对外 terrain 列表中替换为 `"uneven rough"`。

下一步：
- 在 Isaac Sim 中重新执行相关 preview 脚本，确认新的前 10 列顺序和 `"uneven rough"` 名称是否与用户预期一致。

## 2026-04-03

已完成：
- 按用户要求修改 `scripts/isaac_sim/control_keyboard.py`，使 `--terrain stage1` 不再接入旧的 preview/gallery 地形，而是直接复用训练环境使用的整张 `stage1` 地形。
- 新的 `stage1` 键盘联调地形链路当前直接按文件路径加载 `stage1_terrain.py`，调用 `build_stage1_terrain_data()` 生成训练用 mesh，并按训练环境同样的逻辑在 `x/y` 方向整体减去 `border_size` 后导入 `/World/terrain/stage1/mesh`。
- 同步给 `control_keyboard.py` 增加训练地形出生点对齐：当前在 `--terrain stage1` 下，机器人会在初始化句柄后自动移动到训练首个 env origin `[4.0, 4.0, 0.3]`，而不是继续停在地图边缘默认原点。
- 将旧的 `terrain_preview.terrain_builder` 顶层导入改为按分支延迟导入，避免 `--terrain stage1` 路径在启动时被一个已不存在的 preview 依赖提前拦死。
- 已执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，静态检查通过。
- 已执行 `timeout 90s python -u scripts/isaac_sim/control_keyboard.py --terrain stage1 --headless --frames 1`，本次在当前无可用 CUDA 的工具环境中仍成功完成 1 帧 smoke run。
- 本次运行日志已明确打印：
  - `Built training stage1 terrain mesh: root=/World/terrain spawn_position=[4.0, 4.0, 0.3]`
  - `Applied shared terrain friction material: /World/terrain/stage1/mesh`
  - `Moved robot to terrain spawn position: [4.0, 4.0, 0.3]`
  - `Headless smoke validation finished successfully.`

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现在 `control_keyboard.py --terrain stage1` 已经和训练环境在“地形几何来源 + 地图坐标偏移 + 初始出生点”这三件事上对齐。
- 当前保留 `--terrain stage2|both` 的旧 MGDP gallery preview 路径不变；本轮只把 `stage1` 键盘联调路径改成了训练同款地形。

下一步：
- 在用户有可用 GPU 的 Isaac Sim 会话中直接运行 `python scripts/isaac_sim/control_keyboard.py --terrain stage1`，窗口确认车辆是否已落在训练地图首块区域而非边框。

## 2026-04-03

已完成：
- 按用户要求继续修改 `scripts/isaac_sim/control_keyboard.py`，将键盘驱动控制方式改成与训练环境同构的控制链路，而不是沿用原先的平滑 teleop 快捷逻辑。
- 当前脚本中的球铰控制已改为与训练一致的 `JointPositionAction` 语义：
  - 键盘输入先形成 `raw action`
  - 再按 `scale = 0.25` 与默认关节位置 offset 转成球铰位置目标
- 当前脚本中的轮子控制已改为与训练一致的 `JointVelocityAction` 语义：
  - `W/S/A/D/SPACE` 先形成左右轮侧的 `raw action`
  - 再按 `scale = 8.0` 与默认关节速度 offset 转成 6 个轮关节速度目标
- 在 articulation 初始化后，脚本现在会显式把球铰与轮子的驱动参数设成训练环境同一组值：
  - 球铰：`stiffness=80.0`、`damping=8.0`、`effort_limit=120.0`、`velocity_limit=6.0`
  - 轮子：`stiffness=0.0`、`damping=10.0`、`effort_limit=80.0`、`velocity_limit=20.0`
- 同步把 teleop 世界时间步改为与训练一致：
  - `physics_dt = 1 / 120`
  - `render_dt = 1 / 60`
  - `action decimation = 2`
  - 即键盘 action 以 `60 Hz` 刷新，并在两个物理子步间保持不变
- 已执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，语法检查通过。
- 已执行 `timeout 120s python -u scripts/isaac_sim/control_keyboard.py --terrain none --headless --frames 1`，返回码为 `0`；当前输出仍包含本机无可用 CUDA / 无驱动、只读缓存路径和远端 `Example_Rotary` 引用告警，但未出现本轮控制改动引入的 Python 级报错。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `control_keyboard.py` 现在已经不再是“人工调出来的一套近似 teleop 参数”，而是与训练任务共享同一套球铰位置控制 / 轮子速度控制语义、同一组驱动参数和同一时间步结构。
- 当前最直接可人工比对的轮速 target 区间为 `[-8, 8] rad/s`；如果后续手动联调时频繁接近 `20 rad/s` 的 PhysX 上限，应优先怀疑当前训练轮速 scale 偏大或地形/阻力导致策略想靠饱和输出来补偿。

下一步：
- 在有正常 GPU / 图形环境的 Isaac Sim 会话中直接运行 `python scripts/isaac_sim/control_keyboard.py --terrain stage1`，手动观察球铰响应和轮速 target 区间，再决定训练里的 `stiffness / damping` 与 `scale` 是否需要调整。

## 2026-04-03

已完成：
- 按用户要求，仅对 `scripts/isaac_sim/control_keyboard.py` 中训练同构控制参数区补充中文行内注释，说明各参数对应的物理含义、控制语义和单位。
- 本轮未改动任何控制数值、键位映射、关节目标生成逻辑或物理参数本身，只提升脚本可读性与后续人工联调时的可解释性。
- 已执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，语法检查通过。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `control_keyboard.py` 的训练同构参数块已经可以直接从代码注释中读出含义，不需要再反查训练配置文件或聊天记录。

下一步：
- 若还需要继续提升可读性，可再把“球铰 action -> 位置目标”和“轮子 action -> 速度目标”的公式说明补到对应函数上方。

## 2026-04-03

已完成：
- 按用户要求，继续修改 `scripts/isaac_sim/control_keyboard.py`，移除键盘联调路径里的球铰人工运动范围限制。
- 当前 `update_ball_joint_actions()` 不再对 `ball_action_raw` 做 `clamp` 限幅，球铰位置目标现在直接按：
  - `ball_target = default_position + raw_action * 0.25`
  累加生成。
- 同步删除参数区中的 `BALL_JOINT_ACTION_LIMIT`，并把启动打印信息改为“球铰 raw action 无界，仅按 scale 映射到位置目标”。
- 已执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，语法检查通过。
- 额外复核训练环境配置，确认当前 RL 训练任务本身仍保留球铰越界终止项：
  - `complete_car_rl_training_env_cfg.py`
  - `ball_joint_out_of_bounds`
  - `bounds = (-0.8, 0.8)`

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `logs/daily_work_log.md`

产出/结论：
- 当前“球铰无运动范围限制”只对键盘联调脚本生效，方便人工观察驱动响应。
- 训练环境自身仍有 `ball_joint_out_of_bounds` 终止条件，尚未随本轮一起删除。

下一步：
- 若用户后续明确要求训练时也取消球铰范围限制，再单独修改 `complete_car_rl_training_env_cfg.py` 中的越界终止项。

## 2026-04-06

已完成：
- 按用户要求重新规划当前 RL 第一阶段任务定义，不再沿用此前“固定球铰、仅训练轮速”的阶段划分。
- 将新的第一阶段方案同步写入项目规划相关文件，使后续讨论与实现都以这版为默认：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `README.md`
  - `src/rl_lab/complete_car_rl_training/docs/rl_training_route.md`
- 当前新的第一阶段定义已明确为：
  - 观测：基座线速度、基座角速度、重力投影、6 个球铰关节位置、6 个球铰关节速度、6 个轮速、速度命令、上一时刻动作
  - 动作：6 个球铰关节位置目标 + 6 个车轮速度目标
  - 控制语义：球铰走位置目标、车轮走速度目标，沿用现有关节驱动 / `PD` 控制链
  - 奖励：线速度跟踪、角速度跟踪、车体姿态稳定、`lin_vel_z` 惩罚、`ang_vel_xy` 惩罚、动作变化惩罚、球铰偏离中位或过激摆动惩罚、碰撞惩罚、终止惩罚
  - 地形：继续使用当前 `stage1` terrain，第 1 列为 `flat`，其余列保留不同地形类型，但训练默认使用最低难度，使其接近平地
  - 当前阶段不加入外部地形感知

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `README.md`
- `src/rl_lab/complete_car_rl_training/docs/rl_training_route.md`
- `logs/daily_work_log.md`

产出/结论：
- 项目当前默认阶段规划已经切换到“球铰与车轮联合控制的第一阶段 baseline”。
- 旧的“固定球铰 + 轮速控制”阶段定义仅保留为历史讨论背景，不再作为当前默认实现目标。

下一步：
- 按这版阶段 1 规划，开始回写 `complete_car_env_cfg.py`、`mdp/observations.py`、`mdp/rewards.py` 和 `complete_car_stage1_env.py` 的任务定义与训练逻辑。

## 2026-04-06

已完成：
- 用户进一步收紧第一阶段地形范围，明确当前阶段不再采用“低难度混合地形 baseline”，而改为 `flat-only baseline`。
- 已将这一新决策同步写回：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `README.md`
  - `src/rl_lab/complete_car_rl_training/docs/rl_training_route.md`
- 当前第一阶段新的地形约束已明确为：
  - 训练默认只使用 `flat` 地形
  - 现有 `stage1` terrain 保留，但仅作为后续非平地阶段或对照实验入口
  - 其余 observation / action / reward 规划保持不变

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `README.md`
- `src/rl_lab/complete_car_rl_training/docs/rl_training_route.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前项目里的阶段 1 已正式收敛为 `flat-only` 基础运动策略 baseline。
- “低难度混合地形”不再是当前默认训练分布。

下一步：
- 按 `flat-only baseline` 去修改活跃任务代码里的 observation / action / reward / terrain 使用逻辑。

## 2026-04-06

已完成：
- 按用户要求重构地形运行时职责分层，不再让旧 `complete_car_stage1_env.py` 同时混着持有 terrain runtime、课程学习更新和 spawn/reset 偏移逻辑。
- 已将原文件重命名为：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
- 类名同步改为：
  - `CompleteCarStage1TerrainEnv`
- 当前新的 terrain runtime env 只保留：
  - stage1 地形 mesh 导入
  - terrain runtime state 缓存
  - env origin 同步
  - reset 时对 `mdp.curriculums` 和 `mdp.events` 的调用
- 已将 terrain curriculum 更新逻辑移到：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py`
  - 新增 `update_stage1_terrain_curriculum(...)`
- 已将 spawn/reset 偏移逻辑移到：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/events.py`
  - 新增 `apply_stage1_spawn_offsets(...)`
- 已同步修改任务注册入口：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/__init__.py`
  - 当前 `Complete-Car-Rl-Training-v0` 已指向新的 `complete_car_stage1_terrain_env:CompleteCarStage1TerrainEnv`
- 已执行静态校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/events.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/__init__.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/events.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/__init__.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 terrain runtime env 的职责已经明显收缩，后续阅读和扩展不需要再从一个大杂烩文件里同时找地形导入、课程学习和 spawn/reset 规则。
- 课程学习规则与 spawn/reset 偏移规则现在已经各自有明确落点。

下一步：
- 继续处理 terrain 接入方式本身，尤其是默认 plane 与自定义 stage1 mesh 的结构关系，以及 `flat-only baseline` 下的实际训练场景切换。

## 2026-04-06

已完成：
- 继续按用户要求收干 terrain 接入方式，不再让 active task 通过 `TerrainImporterCfg(terrain_type="plane")` 先创建默认 plane 再删除。
- 已修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
  - `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
- 当前 `CompleteCarRlTrainingSceneCfg` 已去掉默认 terrain 配置，scene 启动时不再自动生成 plane。
- 当前 `CompleteCarStage1TerrainEnv` 会在运行时直接使用：
  - `isaaclab.terrains.utils.create_prim_from_mesh`
  将 stage1 生成的 trimesh 导入到：
  - `/World/terrain/stage1`
- 当前 `scene.env_origins` 由 terrain runtime env 直接维护，不再依赖 `scene.terrain.configure_env_origins(...)`。
- 同步把 `export_training_stage.py` 改成兼容 `scene.terrain is None` 的情况，避免导出脚本再假定 scene 一定带 terrain importer。
- 已执行静态校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
- `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active task 的 terrain 接入已经不再依赖“默认 plane + 删除”的补丁式流程。
- stage1 terrain 现在是直接导入的单个 trimesh，结构上更符合“场景里只有这一种地形”的要求。

下一步：
- 继续明确 `flat-only baseline` 是否直接复用该 terrain runtime env，还是单独做一个更薄的平地训练入口。

## 2026-04-06

已完成：
- 按用户要求在 active task 中新增“只在 `flat` 列 reset”的功能，但未删除原有 mixed-terrain 所需的 terrain runtime 结构。
- 已修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py`
- 当前 `Stage1RuntimeCfg` 新增并默认启用：
  - `flat_only_reset=True`
- 当前 `CompleteCarStage1TerrainEnv` 在 `flat_only_reset=True` 时会把所有 env 的 `terrain_type` 固定到 `flat` 对应列，其余 terrain runtime 逻辑保持可复用。
- 当前 terrain curriculum 保留为可开关功能，并默认关闭：
  - `Stage1RuntimeCfg.curriculum=False`
- 已把阶段 1 的 observation / action / reward 正式写回 active task：
  - `complete_car_env_cfg.py` 中 observation 顺序已对齐为：基座线速度、基座角速度、重力投影、球铰位置、球铰速度、轮速、速度命令、上一时刻动作
  - action 维持为：6 个球铰位置目标 + 6 个车轮速度目标
  - reward 改为：线速度跟踪、角速度跟踪、姿态稳定、`lin_vel_z`、`ang_vel_xy`、动作变化、球铰偏离、球铰摆动、碰撞、终止
- 已把 `ang_vel_z` 命令范围从固定 `0` 改为可采样，避免角速度跟踪奖励失效。
- 已在 scene 中增加 3 个 chassis contact sensor，并在：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`
  中新增 `chassis_collision(...)` 奖励函数。
- 已执行静态校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前阶段 1 的默认 active task 已不再只是规划，而是已经真正切到 `flat-only baseline` 的 reset / command / reward / collision 逻辑。
- mixed-terrain 训练路径没有被删除，后续恢复时只需调整 runtime 配置开关。

下一步：
- 用新的阶段 1 配置做一次实际训练冒烟，确认 `flat-only reset`、contact reward 和 `ang_vel_z` 命令生效情况。

## 2026-04-06

已完成：
- 按用户要求将当前整个项目工作区上传到 GitHub。
- 已先把以下内容加入 `.gitignore`，未纳入本次提交：
  - `.obsidian/`
  - `.codex`
- 已对整个当前工作区执行：
  - `git add -A`
  - `git commit -m "upload current project state"`
  - `git push origin main`
- 推送结果：
  - 本地 `main` 已成功推送到 `origin/main`
  - 最新提交为：`2a9cfeb upload current project state`

修改文件：
- `.gitignore`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前本地代码与 GitHub 远程主分支已同步。
- `.obsidian` 与 `.codex` 已从版本管理范围排除，后续不会再被误提交。

下一步：
- 若继续推进训练主线，直接基于当前 `origin/main` 的 `2a9cfeb` 开始即可。

## 2026-04-07

已完成：
- 根据训练控制台 traceback 查明本轮启动失败不是 GPU、不是场景构建、也不是机器人配置解析失败，而是 `rsl_rl` 在创建 `OnPolicyRunner` 时无法解析 observation group。
- 已在：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/agents/rsl_rl_ppo_cfg.py`
  中补充：
  - `obs_groups = {"actor": ["FlatBaseline"], "critic": ["FlatBaseline"]}`
- 当前修正逻辑为：
  - actor 使用环境唯一观测组 `FlatBaseline`
  - critic 同样使用 `FlatBaseline`
- 已同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/agents/rsl_rl_ppo_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 本轮训练启动失败的直接原因已定位为 `obs_groups` 缺失，而非 active task 本身的 observation / reward / termination 配置错误。
- 当前项目在使用自定义 observation group 名时，PPO 配置必须显式声明 `obs_groups`，不能再依赖旧版本的隐式推断。

下一步：
- 重新启动训练，确认是否已越过 `OnPolicyRunner` 初始化阶段，并继续观察首轮 rollout 是否稳定。

## 2026-04-07

已完成：
- 对比分析训练 run：
  - `2026-04-07_12-25-02`
  - `2026-04-06_21-59-12`
- 已补导出旧 run 的 TensorBoard 标量：
  - `src/rl_lab/complete_car_rl_training/logs/rsl_rl/complete_car_rl_training/2026-04-06_21-59-12/tensorboard_export`
- 已确认新 run 变差不能归因于移除 `chassis_collision`：
  - 旧 run 的 `Episode_Reward/chassis_collision` 到结束都为 `0.0`
- 已确认新 run 虽然绝对 episode length 更长，但这是在 `episode_length_s: 8 -> 16` 的前提下发生，不能直接视为更好
- 已确认新 run 的核心跟踪能力明显下降：
  - `Train/mean_reward`: `2.97 -> 1.32`（对比旧 run 末值）
  - `error_vel_xy`: `1.29 -> 3.79`
  - `error_vel_yaw`: `1.76 -> 3.91`
- 已识别这两个 run 之间除 collision reward 外的其他关键变化：
  - `wheel_joints.damping: 10.0 -> 1e4`
  - `ball_joints.stiffness/damping: 80/8 -> 100/10`
  - `lin_vel_x` 命令范围：`[-1, 1] -> [-2, 2]`
  - `episode_length_s: 8 -> 16`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前“原地打转、看起来轮胎不触地”的回放现象，与标量诊断一致地对应“存活优先、跟踪变差”的局部最优。
- 仅凭当前标量不能证明轮胎真的离地；当前能确认的是策略没有学好速度跟踪。
- 若要继续定位主因，后续训练不能再把 reward、actuator、命令范围、episode 时长一起改动。

下一步：
- 用单变量回归方式继续对比，优先先回退 `wheel_joints.damping`，再回退 `lin_vel_x` 命令范围，最后再恢复 `episode_length_s=8` 做公平对比。

## 2026-04-07

已完成：
- 诊断训练 run：
  - `2026-04-07_13-13-46`
- 已确认本次实际使用配置为：
  - `wheel_joints.damping = 1000.0`
  - `num_envs = 512`
  - `max_iterations = 400`
  - `track_lin_vel_xy.std = 1.0`
- 与上一轮 `2026-04-07_12-53-43` 相比，本次出现明显改进：
  - `Train/mean_reward: 5.90 -> 26.43`
  - `Train/mean_episode_length: 741.56 -> 880.97`
  - `error_vel_xy: 3.52 -> 0.71`
  - `error_vel_yaw: 4.32 -> 1.95`
- 当前尾段状态：
  - `time_out ≈ 0.754`
  - `root_too_low ≈ 0.182`
  - `ball_joint_out_of_bounds ≈ 0.064`
- 结论：
  - 当前 baseline 已经从“只会活着”的阶段，进入“线速度跟踪明显有效、yaw 跟踪仍偏弱”的阶段
  - 该 run 已可作为当前阶段的默认 baseline 参考点

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `wheel damping = 1e3 + 512 envs + 400 iterations` 是当前更合适的 baseline 训练规模。
- 下一步不应再大范围改 baseline 结构，而应围绕 yaw 跟踪和非 timeout 终止继续做小幅调整。

下一步：
- 在当前 baseline 附近只做小改，优先减小 `root_too_low` 和 `ball_joint_out_of_bounds`，并继续观察 yaw tracking 是否能进一步提升。

## 2026-04-07

已完成：
- 对比分析训练 run：
  - `2026-04-07_13-13-46`
  - `2026-04-07_13-32-34`
- 已确认这两次 run 的关键差异仅为：
  - `track_ang_vel_z.weight: 0.5 -> 2.0`
- 对比结果：
  - yaw 跟踪显著改善：
    - `error_vel_yaw: 1.95 -> 0.88`
  - 线速度跟踪轻微变差：
    - `error_vel_xy: 0.71 -> 0.83`
  - 存活与失败分布几乎不变：
    - `time_out` 基本持平
    - `root_too_low` 基本持平
    - `ball_joint_out_of_bounds` 基本持平
- 已确认 `Train/mean_reward` 大幅上升不能直接当作“整体更好”的证据，因为这次直接把 yaw reward 权重提高到了原来的 4 倍。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- yaw 权重提到 `2.0` 的效果是“更会转向”，但代价是牺牲部分线速度跟踪，而且没有明显改善生存率。
- 对当前简单 baseline 来说，`track_ang_vel_z.weight = 2.0` 偏强，不适合作为默认最终配置。

下一步：
- 在保持其余配置不变的前提下，优先试 `track_ang_vel_z.weight = 1.0` 或 `1.5`，找线速度与 yaw 的折中点。

## 2026-04-07

已完成：
- 对比分析训练 run：
  - `2026-04-07_13-32-34`
  - `2026-04-07_13-41-53`
- 已确认这两次 run 的关键差异仅为：
  - `track_ang_vel_z.weight: 2.0 -> 1.5`
- 对比结果：
  - 线速度误差改善：
    - `error_vel_xy: 0.83 -> 0.68`
  - yaw 误差基本不变：
    - `error_vel_yaw: 0.88 -> 0.89`
  - 存活与失败分布变差：
    - `time_out: 0.76 -> 0.68`
    - `root_too_low` 变高
    - `ball_joint_out_of_bounds` 变高

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- yaw 权重从 `2.0` 降到 `1.5` 后，并没有带来更平衡的 baseline。
- 当前在这两次之间，`2026-04-07_13-32-34` 仍然是更好的 baseline 候选。

下一步：
- 若继续收敛 baseline，不应再优先调 yaw 权重；更应围绕 `root_too_low` 和 `ball_joint_out_of_bounds` 的失败模式做小幅调整。

## 2026-04-07

已完成：
- 在用户授权下，首次以沙箱外 GPU 方式直接运行完整车 Stage1 baseline 训练，确认 `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --num_envs 512 --max_iterations 400 --headless` 可稳定使用 `cuda:0`。
- 基于 `2026-04-07_13-32-34` 连续完成 3 轮直接调参与实跑：
  - `2026-04-07_13-56-35`
  - `2026-04-07_14-02-02`
  - `2026-04-07_14-06-10`
- 已完成这 3 次 run 与 `2026-04-07_13-32-34` 的结果对比，并把当前默认 baseline 收敛回 `13-32-34`。

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `2026-04-07_13-32-34` 仍是今天最均衡的阶段 1 baseline：
  - `mean_reward = 41.21`
  - `mean_episode_length = 841.79`
  - `error_vel_xy = 0.834`
  - `error_vel_yaw = 0.880`
  - `time_out = 0.757`
  - `root_too_low = 0.176`
  - `ball_joint_out_of_bounds = 0.066`
- 以下 3 个直接后续调参方向均未优于 `13-32-34`：
  - 收紧 reset 扰动并减小球铰动作幅度
  - 增大 `ball_joint_deviation`
  - 增大 `termination`
- 已确认此前 Codex 不能直接启用 GPU 的主因是沙箱权限，而不是这台机器本身不能运行 `cuda:0`。

下一步：
- 当前默认继续以 `13-32-34` 作为阶段 1 baseline。
- 若后续继续调参，不再优先重复今天已验证失败的 4 个方向，应提出新的物理假设后再试。

## 2026-04-07

已完成：
- 记录当前用户手动调参版本的关键参数变化，覆盖：
  - `complete_car_env_cfg.py`
  - `rsl_rl_ppo_cfg.py`
- 按用户要求取消当前阶段的球铰 reset 扰动：
  - `reset_ball_joints.position_range -> (0.0, 0.0)`
  - `reset_ball_joints.velocity_range -> (0.0, 0.0)`
- 已对当前 `complete_car_env_cfg.py` 与 `rsl_rl_ppo_cfg.py` 做 `py_compile` 静态校验，结果通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前用户手动调参版本相对先前 baseline 的关键变化包括：
  - reward/termination 约束明显增强
  - PPO rollout、网络规模和学习率明显增大
- 当前阶段不再保留球铰初始随机扰动，后续若要测试鲁棒性再单独恢复。

下一步：
- 若继续用当前手动调参版本训练，应优先先做一轮新的 run，判断“更强稳定性约束 + 更大 PPO 配置”是否仍能保持速度跟踪主目标。

## 2026-04-07

已完成：
- 新增训练过程中的 root 高度日志功能。
- 在 `mdp/commands.py` 中为当前 `base_velocity` 命令项添加了两项额外 metric：
  - `Metrics/base_velocity/root_height_mean`
  - `Metrics/base_velocity/root_height_min`
- 已确认当前 `root_too_low` 使用的 `root_pos_w` 语义是 articulation root link 的 actor frame 高度，而不是 COM 高度。

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/commands.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 后续训练后可以直接通过 root 高度均值和最低值判断 `root_too_low.minimum_height = 0.15` 是否合适。
- 当前 `root_too_low` 不是在看小车质心高度，而是在看 root link frame 的世界坐标 `z`。

下一步：
- 跑下一轮训练后，优先联动查看：
  - `Metrics/base_velocity/root_height_mean`
  - `Metrics/base_velocity/root_height_min`
  - `Episode_Termination/root_too_low`

## 2026-04-08

已完成：
- 按用户要求重构 Isaac Lab RL 训练目录，去掉旧的单体 `complete_car_env_cfg.py` 方案，改成可分阶段继承的 `common/ + stage1/` 架构。
- 新增通用模板层：
  - `common/base_env_cfg.py`
  - `common/agents/base_rsl_rl_ppo_cfg.py`
  - `common/robot_cfg.py`
  - `common/scene_cfg.py`
  - `common/mdp/`
- 将当前 Stage1 独立成子包：
  - `stage1/stage1_env_cfg.py`
  - `stage1/stage1_env.py`
  - `stage1/stage1_terrain.py`
  - `stage1/mdp/`
  - `stage1/agents/rsl_rl_ppo_cfg.py`
- 删除旧的顶层 Stage1 单体入口和旧 `mdp/`、旧 `agents/`。
- 已同步修改 `preview_stage1_terrain.py`、`preview_stage1_tile.py`、`preview_stage1_last_six.py`、`control_keyboard.py`，让它们全部从新的 `stage1/stage1_terrain.py` 取训练同源地形。
- 已执行一次 Python 语法级验证，确认新结构下主要任务文件与受影响脚本均可通过 `py_compile`。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `scripts/isaac_sim/preview_stage1_tile.py`
- `src/rl_lab/complete_car_rl_training/README.md`
- `README.md`
- `docs/project_file_map.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/__init__.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/common/__init__.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/common/base_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/common/agents/__init__.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/common/agents/base_rsl_rl_ppo_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1/stage1_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1/stage1_env.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1/stage1_terrain.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1/agents/rsl_rl_ppo_cfg.py`

产出/结论：
- 当前 RL 训练代码已经从“一个 Stage1 大配置文件不断改写”的模式，切到“通用模板 + 分阶段子包”的模式。
- 这次重构保留了 manager-based 框架负责的生命周期，不再模仿 MGDP 去重写 `base_task` 一类的底层骨架；真正被迁移的是“分阶段组织和配置继承思想”。
- 后续如果进入 Stage2 / Stage3，应新增同级子包，而不是重新把感知、地形、课程学习继续塞回 Stage1 配置文件。

下一步：
- 在新结构下重新执行一轮 `train.py` smoke test，确认 Gym 注册、Hydra 配置入口和日志输出都正常。

已完成：
- 检查用户本轮大规模目录整理后的实际仓库状态，确认 RL 主线已从旧的 `src/rl_lab/complete_car_rl_training/` 迁移到新的 `RL_Training/`。
- 修复会直接影响训练启动的旧导入路径问题：
  - `RL_Training/scripts/list_envs.py`
  - `RL_Training/scripts/zero_agent.py`
  - `RL_Training/scripts/random_agent.py`
  - `RL_Training/scripts/export_training_stage.py`
  - `RL_Training/scripts/rsl_rl/train.py`
  - `RL_Training/scripts/rsl_rl/play.py`
  上述脚本原本仍写 `import complete_car_rl_training.tasks`，当前已统一改为直接导入包根 `import complete_car_rl_training`。
- 修复仓库根目录 Isaac Sim 脚本对旧包结构和旧项目根的引用：
  - `scripts/isaac_sim/preview_stage1_terrain.py`
  - `scripts/isaac_sim/preview_stage1_tile.py`
  - `scripts/isaac_sim/preview_stage1_last_six.py`
  - `scripts/isaac_sim/control_keyboard.py`
  当前已统一改为从 `RL_Training/complete_car_rl_training/common/` 与 `RL_Training/complete_car_rl_training/stage1/` 读取配置与地形。
- 同步更新了根 README、当前状态、项目文件地图和 `RL_Training/README.md`，把默认主线入口改到 `RL_Training/`。
- 对 `RL_Training` 主包、训练脚本和受影响的 Isaac Sim 脚本执行了 `python3 -m py_compile`，静态检查通过。

修改文件：
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `docs/project_file_map.md`
- `logs/daily_work_log.md`
- `RL_Training/README.md`
- `RL_Training/docs/training_workflow_and_tensorboard_guide.md`
- `RL_Training/scripts/list_envs.py`
- `RL_Training/scripts/zero_agent.py`
- `RL_Training/scripts/random_agent.py`
- `RL_Training/scripts/export_training_stage.py`
- `RL_Training/scripts/rsl_rl/train.py`
- `RL_Training/scripts/rsl_rl/play.py`
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `scripts/isaac_sim/preview_stage1_tile.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `scripts/isaac_sim/control_keyboard.py`

产出/结论：
- 当前真正会导致训练或注册失败的代码级问题已经定位并修正，核心问题是“主线目录已经迁移，但脚本仍引用旧包入口和旧文件路径”。
- 当前剩余未完成的是运行态冒烟，而不是静态路径修正。

下一步：
- 在 `env_isaacLab` 中进入 `RL_Training/` 后，优先执行一次 `python scripts/list_envs.py --keyword Complete-Car` 或小规模 `train.py` 冒烟。

## 2026-04-10

已完成：
- 以 `complete_car_env_cfg.py` 为入口，对当前 direct complete-car 主线完成一轮结构性迁移。
- command 维度由旧设计改为 4 维：
  - `lin_vel_x`
  - `lin_vel_y`
  - `ang_vel_yaw`
  - `heading`
- policy action 改为仅输出 6 个球铰姿态关节目标角，不再把车轮速度作为 policy action 输出。
- 在 `complete_car_env.py` 中新增 env 侧车轮驱动映射：按 command 派生左右轮速度目标，避免 6 维 action 后训练主线失去前进驱动。
- policy observation 重构为以姿态角和姿态角变化率为主的最小本体输入，并删除旧的：
  - `lin_vel`
  - `projected_gravity`
  - `wheel_joint_vel`
  - `height_measurements`
  这些旧主线项不再进入 policy observation。
- 当前基础 observation 拼接顺序改为：
  - `roll, pitch, yaw`
  - `roll_rate, pitch_rate, yaw_rate`
  - `ball_joint_pos(6)`
  - `ball_joint_vel(6)`
  - `commands(4)`
  - `last_action(6)`
  当前基础 observation 总维度为 `28`。
- 新增本地速度跟踪 reward kernel：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/local_velocity_tracking_reward.py`
  并在 `rewards.py` 中组合本地 tracking、heading、姿态惩罚、关节惩罚、action-rate 惩罚。
- 新增本地 PPO 配置副本：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents/local_rsl_rl_cfg.py`
  `ppo_cfg.py` 不再直接继承外部 `RslRlOnPolicyRunnerCfg / RslRlPpoActorCriticCfg / RslRlPpoAlgorithmCfg`。
- 当前 PPO 配置同步改成 `actor / critic / distribution_cfg` 结构，以适配当前机器上的 `rsl-rl-lib 5.0.1`。
- 对本轮涉及的 direct-task 文件执行了 `python3 -m py_compile`，静态语法检查通过。

修改文件：
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/assets/robot_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/commands.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/observations.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/utils.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/rewards.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/local_velocity_tracking_reward.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents/local_rsl_rl_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents/ppo_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 direct 主线的动作、命令、观测、reward、PPO 配置已经切到新的结构，不再停留在旧的 12 维动作和旧 observation 语义上。
- 这次改动的关键不是“单纯减 action 维度”，而是同步补上了 env 侧车轮驱动闭环，使 6 维姿态动作仍然具备速度跟踪训练所需的推进能力。
- 当前仍缺少真实 Isaac Lab 运行态验证；下一步最应该先验证的是 Stage0 下新的 wheel-drive 映射和 28 维 observation 是否按预期工作。

下一步：
- 在 Isaac Lab 环境中优先运行 `python scripts/list_envs.py --keyword Complete-Car`。
- 然后对 `Complete-Car-Stage0-Flat-Direct-v0` 做一次小规模 `train.py` 冒烟，重点检查 action space、observation dim 和车轮驱动效果。

已完成：
- 按用户新要求修改 `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex` 中“整车运动学速度雅可比分析”对应正文。
- 本轮没有采用远端那种整段重写方式，而是在尽量保留当前正文叙述结构的前提下，只对涉及侧模块固定偏置的部分做不对称改写。
- 将原先共用单一 `\mathbf b` 的位置关系改为分别使用：
  - `${}^{1}\mathbf b_1`
  - `${}^{3}\mathbf b_3`
- 同步改写并校正了以下链条中的对应公式：
  - 前后模块参考点位置表达
  - 前后模块线速度传播
  - `\mathbf K_1(\mathbf q)`、`\mathbf K_3(\mathbf q)`
  - 前后轮对应的行雅可比显式展开
- 轮心位置向量与单模块轮速矩阵 `\mathbf H_i` 本轮仍保留原有符号化模板写法，没有切换成整段实测参数直代版正文。
- 在 `毕业论文/毕业论文模板/LaTeX/` 下执行：
  - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
  编译通过，`main.pdf` 已重新生成。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `毕业论文/毕业论文模板/LaTeX/main.pdf`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `chapter03` 正文已经从“统一侧模块偏置 `\mathbf b`”切到“前后固定偏置分开建模”的写法。
- 本轮采取的是最小侵入式正文修订，而不是整段换成新的远端版本。
- 当前论文仍只保留 2 条旧的非阻塞文献警告：
  - `fang2015survey`
  - `MATSUMURA2017566`

下一步：
- 如果还要继续打磨 chapter03，下一轮应优先检查各段文字对 `${}^{1}\mathbf b_1` 与 `${}^{3}\mathbf b_3` 的物理意义解释是否还可再压缩得更清楚，而不是再大范围重写正文结构。

已完成：
- 按用户新的严格修订要求，再次处理 `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex` 中“整车运动学速度雅可比分析”对应正文。
- 本轮仍坚持“不推翻原推导框架、不整体重写正文”，仅在原有主线内修正符号冲突、几何定义和物理表述。
- 已将车轮角速度符号从：
  - `\dot\phi_{iL}, \dot\phi_{iR}`
  统一改为：
  - `\Omega_{iL}, \Omega_{iR}`
  并同步修改相关文字、轮速向量与整车雅可比表达。
- 已将连接向量明确为：
  - `${}^{2}\mathbf a=[a_x,0,0]^T`
  同时把正文中的“对称结构”表述收紧为“前后连接中心沿 `x_2` 轴镜像分布”。
- 已将 `${}^{2}\mathbf v_c`、`${}^{2}\boldsymbol\omega_c` 的物理定义统一改为：
  - 主模块瞬时刚体速度
  - 运动学分析中的广义速度描述
  不再称为“运动指令”。
- 已将“纯滚动约束”相关措辞统一改为“基于滚动方向无滑移条件”的轮速映射表述，并补充说明这里只使用了滚动方向速度关系，没有完整展开侧向无滑移约束。
- 已补充车轮角速度正方向约定，并在欧拉角速度映射处补充参数奇异性说明。
- 在 `毕业论文/毕业论文模板/LaTeX/` 下再次执行：
  - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
  编译通过，`main.pdf` 已重新生成。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `毕业论文/毕业论文模板/LaTeX/main.pdf`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `chapter03` 中“整车运动学速度雅可比分析”这一节已经在保留原推导主线的前提下完成一轮更严格的学术化修订。
- 当前该节的关键符号、几何定义和物理表述已经与“不对称固定偏置 + 主模块瞬时刚体速度 + 滚动方向轮速映射”的写法保持一致。
- 当前论文仍只保留 2 条旧的非阻塞文献警告：
  - `fang2015survey`
  - `MATSUMURA2017566`

下一步：
- 若继续修改 chapter03，后续应优先做局部措辞压缩和版面整理，不再回退这套已经统一好的符号与物理定义。

已完成：
- 基于论文最终采用的真实参数与整车速度雅可比矩阵，新增独立轮速分配模块：
  - `RL_Training/kinematics/wheel_speed_allocator.py`
- 同步新增：
  - `RL_Training/kinematics/__init__.py`
  - `RL_Training/scripts/validate_wheel_speed_allocator.py`
- 新分配器内部已固定使用真实几何参数：
  - `a`
  - `b1`
  - `b3`
  - 三个模块左右轮轮心位置
  - `r_wheel`
- 新分配器同时提供：
  - `numpy` 验证接口
  - `torch` 运行接口
- 新分配器显式构造：
  - `\mathbf K_1(\mathbf q), \mathbf K_2, \mathbf K_3(\mathbf q)`
  - 实测参数版 `\mathbf H_i`
  - 整车 Jacobian `\mathbf J_w(\mathbf q)`
  并将论文中的前-中-后轮速顺序重排为仿真实际 joint 顺序：
  - `body_car_wheel_left_joint`
  - `body_car_wheel_right_joint`
  - `head_car_wheel_left_joint`
  - `head_car_wheel_right_joint`
  - `tail_car_wheel_left_joint`
  - `tail_car_wheel_right_joint`
- 已将 direct env 中旧的经验缩放轮速逻辑删除，改为在每步根据：
  - 当前 6 个球铰关节角
  - 当前 6 个球铰关节角速度
  - RL command 中的 `lin_vel_x / lin_vel_y / ang_vel_yaw`
  通过 Jacobian 分配器生成 6 维 wheel target。
- 已删除旧控制参数：
  - `wheel_drive_lin_vel_scale`
  - `wheel_drive_yaw_rate_scale`
  因为它们已不再符合当前轮速分配语义。
- 已在 `RL_Training/` 下执行：
  - `python3 scripts/validate_wheel_speed_allocator.py`
  基础数值检查通过，覆盖：
  - 零输入
  - 纯前进
  - 纯偏航
- 已执行：
  - `python3 -m py_compile RL_Training/kinematics/__init__.py RL_Training/kinematics/wheel_speed_allocator.py RL_Training/scripts/validate_wheel_speed_allocator.py RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
  静态语法检查通过。

修改文件：
- `RL_Training/kinematics/__init__.py`
- `RL_Training/kinematics/wheel_speed_allocator.py`
- `RL_Training/scripts/validate_wheel_speed_allocator.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 RL 主线已经从“经验缩放差速轮速”切到“真实参数 Jacobian 轮速分配”。
- 当前轮速分配模块既可以独立验证论文模型，也可以直接作为 Isaac Lab env 的 wheel target 生成器。
- 当前 `heading` command 仍保留给高层任务语义，但不直接进入瞬时轮速 Jacobian 映射。

下一步：
- 在真实 Isaac Lab 环境中优先验证新 allocator 接入后 Stage0 的前进、转向与速度跟踪 reward 是否一致。

## 2026-04-10

已完成：
- 按用户要求先以 GitHub 为准同步本地：
  - 发现 `origin/main` 已被强制更新，无法 fast-forward
  - 已将本地 `main` 直接重置到 `origin/main`
  - 当前同步基线为 `97ca6b6`
- 将当前环境中的 `rsl_rl` 实现整包 vendoring 到项目本地：
  - `RL_Training/rsl_rl/`
- 当前 vendored 包已包含训练主线实际会用到的实现链：
  - `runners/on_policy_runner.py`
  - `algorithms/ppo.py`
  - `models/mlp_model.py`
  - `storage/rollout_storage.py`
  - `modules/distribution.py`
  - `modules/mlp.py`
  - `modules/normalization.py`
  - `utils/logger.py`
  - 以及其余闭环依赖文件
- 修改 `RL_Training/scripts/rsl_rl/train.py` 与 `play.py`：
  - 在脚本启动时将 `RL_Training/` 项目根路径插入 `sys.path`
  - 让训练/回放优先导入仓库内 `RL_Training/rsl_rl/`
  - 不再把外部 `rsl-rl-lib` 的 metadata 版本当作当前实现本体来源
- 修改 `RL_Training/rsl_rl/__init__.py`：
  - 增加本地版本标记 `5.0.1-local`
- 修改 `RL_Training/setup.py`：
  - 将 `rsl_rl`、`rsl_rl.*` 纳入 editable install 的打包范围
  - 补充 `GitPython`、`tensordict`、`tensorboard` 依赖声明
- 更新 `README.md` 与 `RL_Training/README.md`，把 vendored `rsl_rl/` 明确记为当前训练主线的一部分。
- 执行：
  - `python3 -m compileall RL_Training/rsl_rl RL_Training/scripts/rsl_rl RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents`
  编译通过。
- 额外做了直接导入校验，确认当前解析到的是仓库内文件：
  - `OnPolicyRunner -> RL_Training/rsl_rl/runners/on_policy_runner.py`
  - `PPO -> RL_Training/rsl_rl/algorithms/ppo.py`
  - `MLPModel -> RL_Training/rsl_rl/models/mlp_model.py`

修改文件：
- `README.md`
- `RL_Training/README.md`
- `RL_Training/setup.py`
- `RL_Training/scripts/rsl_rl/train.py`
- `RL_Training/scripts/rsl_rl/play.py`
- `RL_Training/rsl_rl/`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前项目不再只有本地 PPO 配置壳；`rsl_rl` 的 runner、PPO、本体网络、分布、存储和日志实现也已经随仓库一并进入版本控制。
- 当前训练入口在运行时会优先吃仓库内 `RL_Training/rsl_rl/`，不再默认依赖 site-packages 中外部 `rsl_rl` 实现。
- 本轮目标不是替换算法逻辑，而是把当前正在使用的算法实现本体一并纳入项目，便于后续继续改 PPO / runner / network 细节。

下一步：
- 在真实 Isaac Lab 环境中跑一次 `Stage0` 冒烟，确认训练启动时加载的确实是仓库内 `RL_Training/rsl_rl/`。
- 然后把本轮 vendored `rsl_rl` 改动与训练主线改动一起提交并推送到 GitHub。

## 2026-04-14

已完成：
- 使用 Google Scholar 按 3 组关键词做一轮分批检索，每组抓取第 1 页，共整理 30 篇候选论文：
  - `("articulated wheeled robot" OR "articulated vehicle" OR "articulated rover") AND ("rough terrain" OR "uneven terrain") AND (control OR "reinforcement learning")`
  - `("active suspension" OR "actively articulated suspension" OR "articulated suspension") AND (robot OR rover) AND ("rough terrain" OR terrain)`
  - `("wheeled robot" OR "ground vehicle") AND ("rough terrain" OR "off-road") AND ("reinforcement learning" OR "deep reinforcement learning")`
- 按“与 articulated / multi-body / actively-jointed wheeled robot + rough terrain + reinforcement learning + terrain perception 的贴合程度”对候选结果做了二次人工重排。
- 当前检索结果可归为 3 类：
  - 主动车体/主动悬架在粗糙地形上的机构与控制
  - 粗糙地形轮式/地面车辆 RL 导航与控制
  - 地形几何估计 / 地形感知驱动的悬架或轮速分配
- 当前第一轮最有价值的 seed papers 已收口为：
  - `Hybrid Learning for Rough Terrain Navigation of Actively Articulated Wheeled Vehicles`
  - `Control of rough terrain vehicles using deep reinforcement learning`
  - `Simultaneous control of terrain adaptation and wheel speed allocation for a planetary rover with an active suspension system`
  - `Control of robotic vehicles with actively articulated suspensions in rough terrain`
- 已同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前与课题四要素同时高度重合的论文并不多，更多是：
  - 主动关节/主动悬架一类论文覆盖机构与地形适应
  - RL 一类论文覆盖粗糙地形控制或导航
  - 地形感知一类论文覆盖 terrain geometry estimation / wheel-terrain contact
- 后续二轮扩展更适合从 seed papers 做 cited-by 追踪，而不是继续大范围宽搜。

已完成：
- 继续处理 `RL_Training/scripts/train.py` 在真实 GPU 训练启动阶段的 articulation 创建失败问题。
- 使用最小 Isaac Sim headless 检查脚本读取 `USD/complete_car.usd` 的真实 prim 层级，确认：
  - 资产根在 `/World/complete_car_alternative`
  - articulation root 在 `/World/complete_car_alternative/body_car_chassis`
  - IMU 实际 prim 名为 `Imu_Sensor`
  - 双目左相机实际 prim 名为 `Stereo_Vision_Camera/Camera_left`
  - LiDAR 实际 prim 名为 `Example_Rotary`
- 修改 `assets/robot_cfg.py`：
  - `COMPLETE_CAR_ARTICULATION_ROOT_PRIM_PATH` 改为 `/complete_car_alternative/body_car_chassis`
- 修改传感器与 height scanner 路径：
  - `sensors/imu.py`
  - `sensors/lidar.py`
  - `sensors/stereo_camera.py`
  - `terrain/terrain_cfg.py`
  统一补上 `complete_car_alternative` 中间层，并改为 USD 中真实存在的传感器 prim 名称
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/assets/robot_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/imu.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/lidar.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/stereo_camera.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
  完成静态编译检查，检查通过。
- 在沙箱外 GPU 环境执行最小训练命令：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 1 --max_iterations 1`
- 实测结果：
  - articulation 创建成功
  - 仿真启动成功
  - actor/critic 网络构建成功
  - 完成 1 次 PPO 学习迭代
  - `Training time: 0.83 seconds`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/assets/robot_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/imu.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/lidar.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/stereo_camera.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前用户这次遇到的训练启动失败已经解决。
- 根因是代码中的 articulation root 与传感器 prim 路径没有对齐 USD 内部的 `complete_car_alternative` 根层级及真实传感器命名。
- 当前 `Stage0` 已恢复为可在真实 GPU 环境中正常完成最小训练启动与 1 次学习迭代的状态。

已完成：
- 处理 `RL_Training/scripts/train.py` 启动时报错的配置类阻塞问题。
- 修改 `terrain/terrain_cfg.py`：
  - 删除会被 Isaac Lab `configclass` 误当作可写成员的只读 `num_height_points` property
  - 改为通过 `get_num_height_points()` 与内部即时采样点解析逻辑计算 patch 点数
- 修改 `base/complete_car_cfg.py` 与 `utils/io_descriptors.py`：
  - 调整为调用 `terrain.get_num_height_points()`
- 修改 `sensors/imu.py`、`sensors/lidar.py`、`sensors/stereo_camera.py`、`sensors/sensor_cfg.py`：
  - 删除 `policy_feature_dim` 只读 property
  - 改为统一使用 `get_policy_feature_dim()`
- 修改 `terrain/terrain_builder.py`：
  - 将 `Stage1TerrainCfg` 从 `frozen dataclass` 改为普通 dataclass
  - 使 Hydra 可以回写 terrain generator 嵌套配置
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_builder.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/imu.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/lidar.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/stereo_camera.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
  完成静态编译检查，检查通过。
- 使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cpu --num_envs 1 --max_iterations 1`
  做真实训练入口冒烟验证。
- 结果：
  - 已确认原始启动报错链路不再出现
  - 训练入口已越过 Hydra 配置注册与 `env_cfg` 构建，进入 Isaac Lab 仿真上下文创建
  - 当前继续看到的是环境级问题：
    - 无 CUDA 驱动 / 无可用 GPU
    - Isaac Sim `user.config.json` 与 cache 目录写入受限

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/imu.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/lidar.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/stereo_camera.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_builder.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 direct workflow 的配置树中，不应再用继承只读 property 来表示可推导配置量。
- 当前 terrain generator 嵌套配置必须保持可写，不能继续使用 `frozen dataclass`。
- 用户本次贴出的训练启动报错已经解决；若后续仍无法跑通，应转而排查本机 Isaac Sim 运行环境而不是继续回到这组配置类问题。

已完成：
- 按用户要求调整 GitHub 同步范围：
  - 保留所有当前代码与文档改动进入本轮同步
  - 排除 `.~lock*` 临时锁文件
  - 将 `URDF/complete_car_alternative/vehicle_dimensions_axles_tracks.xlsx` 纳入本轮提交
- 修改根 `.gitignore`：
  - 新增 `.~lock*`
  - 新增 `docs/literature/`
  - 新增 `毕业论文/`
- 明确仓库同步策略：
  - `docs/literature/` 与 `毕业论文/` 仅保留为本地资料目录
  - 本轮同步时会从 Git 索引中移除它们，使 GitHub 远端仓库同步删除对应内容，但不删除本地文件
- 同步更新项目记忆文件：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `.gitignore`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 后续 GitHub 远端仓库将不再保存论文正文目录与文献资料目录。
- 这两个目录今后默认只作为本地研究工作区保留。

已完成：
- 按用户要求更新并精简 `docs/training_workflow_and_tensorboard_guide.md`。
- 删除文档中已失效的旧工程路径与旧 task id：
  - `src/rl_lab/complete_car_rl_training`
  - `Complete-Car-Rl-Training-v0`
- 文档现已统一改为当前有效主线：
  - `RL_Training/`
  - `scripts/train.py`
  - `scripts/play.py`
  - `CompleteCar-Stage0/1/2`
- 文档内容已收口为最小工作流：
  - 环境准备
  - 训练命令
  - 回放命令
  - 日志与 checkpoint 目录
  - TensorBoard 查看命令
  - 离线导出 TensorBoard 标量命令

修改文件：
- `docs/training_workflow_and_tensorboard_guide.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前训练流程说明文档已与现有代码结构一致，可直接作为 `RL_Training/` 主线的简明操作入口使用。

已完成：
- 分析真实 Stage0 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_12-48-16`
- 已确认该次 run 的 TensorBoard 当前只有 21 个 scalar tag，不是 TensorBoard 故障，而是训练日志覆盖面不足。
- 已根据当前 active 语义补强训练日志链路：
  - `env.py` 现可输出当前步的：
    - `Reward/...`
    - `Tracking/...`
    - `Action/...`
    - `Command/...`
    - `Observation/...`
    - `Termination/...`
  - 终止逻辑已拆成显式分项：
    - `bad_orientation`
    - `ball_joint_out_of_bounds`
    - `root_too_low`
    - `time_out`
  - episode 侧新增：
    - `episode/return`
    - `episode/return_per_step`
    - `episode_per_step/...`
    - `episode_reset/...`
- 已修改 TensorBoard 离线导出脚本：
  - 新增 `group_summary.csv`
  - `latest_values.csv` 新增：
    - `group`
    - `first_value`
    - `last_value`
    - `delta`
    - `min_value`
    - `max_value`
    - `mean_value`
- 已执行：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py`
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_12-48-16`
  均已通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前代码已经补齐新一轮训练应当输出的大部分核心运行指标。
- 旧 run `2026-04-14_12-48-16` 的 event 文件不会自动长出新 tag；需要重新跑一次训练才能验证新增指标是否进入 TensorBoard。

已完成：
- 定位并修正一次回放链路报错。
- 用户执行：
  - `python scripts/play.py --task CompleteCar-Stage0 --load_run 2026-04-14_12-48-16 --num_envs 2`
  时，原先会报：
  - `TypeError: first argument must be string or compiled pattern`
- 根因已确认：
  - `agents/rsl_rl_ppo_cfg.py` 中默认：
    - `load_run = -1`
    - `load_checkpoint = -1`
  - 但 Isaac Lab 的 `get_checkpoint_path()` 需要的是正则字符串，而不是整数哨兵值。
- 当前已修正：
  - `agents/rsl_rl_ppo_cfg.py`
    - 改为：
      - `load_run = ".*"`
      - `load_checkpoint = "model_.*.pt"`
  - `scripts/train.py`
  - `scripts/play.py`
    - 在调用 `get_checkpoint_path()` 前新增类型归一化，避免旧整数值再次导致崩溃
- 已执行：
  - `python3 -m py_compile RL_Training/scripts/train.py RL_Training/scripts/play.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`
  - 并做了本地选择器归一化检查，确认：
    - `load_run='2026-04-14_12-48-16', load_checkpoint=-1`
    会被转换为：
    - `('2026-04-14_12-48-16', 'model_.*.pt')`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`
- `RL_Training/scripts/train.py`
- `RL_Training/scripts/play.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前回放命令在只指定 `--load_run` 时，逻辑上应会自动选择该 run 下最新的 `model_*.pt`，不应再因为 `-1` 类型错误崩溃。

已完成：
- 继续修正同一回放链路中的下一处报错。
- 用户再次执行回放时，原先会报：
  - `packaging.version.InvalidVersion: '5.0.1-local'`
- 根因已确认：
  - 本地 vendored `rsl_rl/__init__.py` 中版本号写成了：
    - `5.0.1-local`
  - `scripts/play.py` 中使用 `packaging.version.parse()` 做版本分支判断，这个字符串不符合 PEP 440。
- 当前已修正：
  - `rsl_rl/__init__.py`
    - 改为：
      - `5.0.1+local`
  - `scripts/play.py`
    - 增加版本兼容解析函数，若遇到旧的 `-local` 后缀会先归一化再解析
- 已执行：
  - `python3 -m py_compile RL_Training/scripts/play.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/__init__.py`
  - 本地纯 Python 验证：
    - `5.0.1-local`
    - `5.0.1+local`
    均可被当前回放辅助函数归一化并通过比较

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/__init__.py`
- `RL_Training/scripts/play.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前回放链路已连续修掉：
  - checkpoint 选择器类型错误
  - vendored 版本号解析错误
- 还需要在真实 Isaac Lab 环境里继续执行一次回放，确认后续运行时链路没有新的阻塞。

已完成：
- 分析真实 Stage0 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_13-07-32`
- 已确认本次 run 的新增日志链路已实际写入 event 文件：
  - scalar tag 数量为 `64`
  - 分组已包含：
    - `Action`
    - `Command`
    - `Reward`
    - `Tracking`
    - `Observation`
    - `Termination`
    - `episode_per_step`
    - `episode_reset`
- 当前 run 的高层训练结果与上一轮：
  - `2026-04-14_12-48-16`
  在旧共有指标上数值一致，说明相同 seed / 配置下复现稳定。
- 本次 run 的 last50 结果大致为：
  - `Train/mean_reward ≈ 2196`
  - `Train/mean_episode_length ≈ 716`
  - `Tracking/lin_vel_x_abs_error ≈ 0.084`
  - `Tracking/ang_vel_yaw_abs_error ≈ 0.388`
  - `Reward/total ≈ 3.107`
  - `Observation/tilt_deg ≈ 3.11`
- 当前主要剩余终止来源不是：
  - `bad_orientation`
  - `root_too_low`
  而是：
  - `ball_joint_limit`
- 同时当前动作指标显示：
  - `Action/policy_abs_mean ≈ 0.886`
  - `Action/policy_std ≈ 0.815`
  说明 policy 动作整体较激进，和球铰越界终止现象一致。
- 已执行：
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_13-07-32`
  并完成 event 标量统计与上一轮 run 对比。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 新日志体系已经在真实 run 中验证生效。
- 当前 Stage0 下一轮更应该优先处理球铰越界终止，而不是姿态倾覆或车体高度问题。

已完成：
- 按用户确认执行方案一，新增球铰软约束惩罚：
  - `ball_joint_limit_soft`
- 当前实现位置：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- 当前实现语义：
  - 仅当球铰利用率超过可用范围的 `80%` 后激活
  - 按默认位姿到硬 limit 的相对使用率计算
  - 对 6 个球铰取均值
  - 使用二次惩罚
  - 当前 scale 为：
    - `-0.2`
- 同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
- 已执行真实 GPU 训练：
  - `cd /home/ubuntu/Graduation-Project/RL_Training`
  - `source /home/ubuntu/miniconda3/etc/profile.d/conda.sh && conda activate env_isaacLab`
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --run_name soft_limit_v1`
- 本轮新 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_13-36-38_soft_limit_v1`
- 已执行离线导出：
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_13-36-38_soft_limit_v1`
- 与 baseline：
  - `2026-04-14_13-07-32`
  的 last50 对比结果：
  - `Train/mean_reward`：
    - `2196 -> 2387`
  - `Train/mean_episode_length`：
    - `716 -> 743`
  - `Tracking/ang_vel_yaw_abs_error`：
    - `0.388 -> 0.310`
  - `episode_reset/ball_joint_limit_rate`：
    - `0.395 -> 0.344`
  - `episode_reset/time_out_rate`：
    - `0.605 -> 0.656`
  - 但 `Observation/tilt_deg`：
    - `3.11 -> 6.85`
    出现明显上升
- 额外结论：
  - `Loss/value` 仍明显波动，不是单调收敛
  - 但结合奖励、tracking、episode length 的改善，当前不能把 value loss 波动直接解释成训练失败
  - 当前问题已从“球铰越界明显”变成“软约束改善 joint-limit reset，但带来了更大的姿态倾角”

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 方案一已真实跑通并完成结果对比。
- 当前 soft limit 方向有效，但下一轮应围绕“压回姿态倾角”做单变量修正，而不是回退这个软约束项。

已完成：
- 按用户要求进入自动奖励优化循环，对 Stage0 又连续执行了 2 轮真实 GPU 单变量训练，并在每轮结束后导出 TensorBoard 标量做后 50 次均值对比。
- 第 1 轮：
  - 将 `Stage0` 的 `orientation` 权重从 `-3.0` 回调到 `-2.5`
  - 训练命令：
    - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --run_name soft_limit_v1_orient25`
  - run：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_13-57-08_soft_limit_v1_orient25`
  - 导出命令：
    - `python source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir logs/rsl_rl/complete_car_stage0/2026-04-14_13-57-08_soft_limit_v1_orient25`
- 第 2 轮：
  - 以当前最稳的 `orientation = -3.0` 版本为底座，临时把 `tracking_lin_vel` 提高到 `2.2`
  - 训练命令：
    - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --run_name soft_limit_v1_orient3_lin22`
  - run：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_14-04-19_soft_limit_v1_orient3_lin22`
  - 导出命令：
    - `python source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir logs/rsl_rl/complete_car_stage0/2026-04-14_14-04-19_soft_limit_v1_orient3_lin22`
- 已将 `Stage0` 当前代码恢复到本轮验证后的最优已知配置：
  - `orientation = -3.0`
  - 保留 `ball_joint_limit_soft = -0.2`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 5 个可比 run 中，最优已验证配置仍然是：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_13-48-25_soft_limit_v1_orient3`
- 其 last50 关键结果大致为：
  - `Train/mean_reward ≈ 2779`
  - `Train/mean_episode_length ≈ 893`
  - `Tracking/lin_vel_x_abs_error ≈ 0.141`
  - `Tracking/ang_vel_yaw_abs_error ≈ 0.344`
  - `Observation/tilt_deg ≈ 2.03`
  - `episode_reset/terminated_rate ≈ 0.085`
  - `episode_reset/time_out_rate ≈ 0.915`
- `orientation = -2.5` 虽然比 `-3.0` 更像折中，但稳定性明显退化：
  - `episode_reset/terminated_rate ≈ 0.191`
  - `tilt_deg ≈ 4.02`
- `tracking_lin_vel = 2.2` 虽然把 `Reward/tracking_lin_vel` 提高到约 `1.91`，但真实前向误差并没有改善，反而恶化到：
  - `Tracking/lin_vel_x_abs_error ≈ 0.163`
  同时：
  - `Tracking/ang_vel_yaw_abs_error ≈ 0.449`
  - `tilt_deg ≈ 4.84`
  - `episode_reset/terminated_rate ≈ 0.177`
- 因此本轮自动优化已经收口到一个“当前较为理想”的结果：
  - 保留软约束惩罚
  - Stage0 使用更强的姿态惩罚 `orientation = -3.0`
  - 不继续保留 `orientation = -2.5` 或 `tracking_lin_vel = 2.2` 这两条临时实验分支

下一步：
- 若继续做 Stage0 调优，应优先围绕动作正则或 reward 耦合做新的单变量设计，而不是继续直接削弱姿态惩罚。

已完成：
- 确认本次训练 `2026-04-14_20-52-07` 的实际结果目录为：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_20-52-07/`
- 检查该目录下当前已有：
  - `events.out.tfevents.*`
  - `model_0.pt` 到 `model_599.pt`
  - `params/env.yaml`
  - `params/agent.yaml`
  - `git/Graduation-Project.diff`
- 更新 `docs/training_workflow_and_tensorboard_guide.md`：
  - 补充每次训练结果的固定保存规则
  - 补充绝对路径写法
  - 补充 `run_dir` 的时间戳命名方式
  - 补充本次训练的实际示例路径

修改文件：
- `docs/training_workflow_and_tensorboard_guide.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前训练结果统一保存在：
  - `RL_Training/logs/rsl_rl/<experiment_name>/<run_dir>/`
- 对于当前这次 Stage0 训练，对应目录就是：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_20-52-07/`

## 2026-04-15

已完成：
- 按用户要求检查两个真实 Stage0 run 的 observation 项，确认能否通过 scale 反推出原始量级并判断当前参数是否合适：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_14-04-19_soft_limit_v1_orient3_lin22`
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_20-52-07`
- 由于第二个 run 原本只有 `events.out.tfevents.*`，已先补执行：
  - `python3 source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir logs/rsl_rl/complete_car_stage0/2026-04-14_20-52-07`
- 对照两次 run 冻结下来的 `params/env.yaml`，确认两次 run 的 observation scale 完全一致：
  - `base_lin_vel = 1.0`
  - `base_ang_vel = 0.25`
  - `projected_gravity = 1.0`
  - `ball_joint_pos = 1.0`
  - `ball_joint_vel = 0.05`
  - `ball_joint_target_error = 1.0`
  - `module_roll_pitch = 1.0`
  - `wheel_joint_vel = 0.05`
  - `commands = 1.0`
- 已根据 last50 统计反推归一化后的观测量级：
  - 可直接反推的观测项大多落在 `0.03 ~ 0.54` 这一量级
  - 当前没有发现明显的 observation scale 配置错误
- 同时确认一个重要限制：
  - `Observation/base_lin_vel_x`
  - `Observation/base_ang_vel_yaw`
  - `Command/lin_vel_x`
  - `Command/ang_vel_yaw`
  当前日志记录的是跨 env 的有符号均值，不能直接拿来判断真实幅值分布

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 的 observation scale 不是主要矛盾。
- 相比之下，更值得继续盯的是：
  - `Action/policy_abs_mean` 仍接近 `1.0`
  - `ball_joint_target_error_abs_mean` 仍偏大
- 因此如果后续继续做 Stage0 诊断，优先级应放在动作激进性和 reward 耦合，而不是先去大幅重配 observation scale。

已完成：
- 按用户要求修改 TensorBoard 的 step-level observation 输出，使其显式记录未乘 scale 的原始观测值，而不是和 policy 输入混在一起。
- 在：
  - `mdp/observations.py`
  中新增原始观测分量收集函数，并将 Actor observation 的 scale 乘法保留在观测拼接阶段。
- 在：
  - `base/env.py`
  中把 TensorBoard 使用的 `Observation/...` 日志改为从原始观测分量直接取值，并统一追加 `_raw` 后缀。
- 当前新增/替换的原始观测标签包括：
  - `Observation/base_lin_vel_x_raw`
  - `Observation/base_ang_vel_yaw_raw`
  - `Observation/projected_gravity_xy_norm_raw`
  - `Observation/ball_joint_pos_abs_mean_raw`
  - `Observation/ball_joint_vel_abs_mean_raw`
  - `Observation/ball_joint_target_error_abs_mean_raw`
  - `Observation/wheel_joint_vel_abs_mean_raw`
  - `Observation/head_roll_pitch_abs_mean_raw`
  - `Observation/tail_roll_pitch_abs_mean_raw`
  - `Observation/goal_rel_x_raw`
  - `Observation/goal_rel_y_raw`
  - `Observation/goal_rel_psi_raw`
  - `Observation/last_action_abs_mean_raw`
- 已执行静态检查：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 之后新的 TensorBoard run 中，`Observation/..._raw` 可以直接拿来读原始物理量，不需要再手工除以 scale。
- policy 输入归一化逻辑仍然保留，不影响训练执行链。

已完成：
- 按用户要求删去动作链中的电机干扰项。
- 当前已从主执行链路中移除：
  - `motor_strength`
  - reset 时的 `sample_motor_strength(...)`
  - `Action/motor_strength_mean` 日志项
- `preprocess_policy_actions(...)` 现已改为：
  - 先裁剪 policy action
  - 再直接作为 `processed_actions`
  - 不再乘任何电机强度系数
- `RandomizationCfg` 已删除：
  - `randomize_motor_strength`
  - `motor_strength_range`
- 当前动作侧若后续开启随机化，仅剩：
  - `action_noise_std`
  - `action_bias_std`
  这两类显式机制
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/randomization.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active action pipeline 已不存在电机强度扰动项。
- 之后如果训练中还出现动作侧不稳定，应优先从：
  - policy 输出本身
  - `action_noise_std`
  - `action_bias_std`
  去查，而不是再去找 `motor_strength` 支路。

已完成：
- 按用户要求从当前 active direct workflow 中删去 `root_too_low` 相关内容。
- 当前已删除：
  - `TerminationCfg.minimum_root_height`
  - `done_terms["root_too_low"]`
  - `Termination/root_too_low_rate`
  - `episode_reset/root_too_low_rate`
  - `episode/root_height_mean`
  - `episode/root_height_min`
  - `Observation/root_height`
- env 内部也不再维护用于该终止项诊断的 root-height 统计缓存。
- 当前 active 失败终止条件已收口为：
  - `bad_orientation`
  - `ball_joint_out_of_bounds`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 之后新的 direct-workflow run 不应再出现 `root_too_low` 相关 termination 和统计标签。
- 历史日志中与 `root_too_low` 相关的条目仍保留为历史结论，但不再代表当前 active 主线。

已完成：
- 按用户要求在当前 active direct workflow 的现有观测项基础上新增 18 维轮地接触相关观测：
  - 6 维各轮纵向滑移率
  - 6 维各轮侧滑角
  - 6 维按整车重量归一化的各轮法向接触力
- 当前 slip / contact 观测实现已按用户给定物理定义接入：
  - 纵向滑移率使用
    - `(v_x - r * omega) / max(|v_x|, eps)`
  - 侧滑角使用
    - `atan2(v_y, |v_x| + eps)`
  - 法向接触力使用
    - `max(0, F_contact · z_hat) / (m_total * g)`
- 当前低速保护与裁剪参数为：
  - `eps = 0.1`
  - `slip ratio clip = [-1, 1]`
  - `slip angle clip = [-pi/2, pi/2]`
- 当前 wheel contact force 入口已打通：
  - `robot_cfg.py` 中 USD spawn 已启用 `activate_contact_sensors = True`
  - `sensor_cfg.py` 中新增了绑定 6 个 wheel body 的 `ContactSensor`
  - `env.py` 中会读取 `net_forces_w` 并传入 observation 计算链
- 当前 wheel body 与参数常量已显式收口：
  - `WHEEL_BODY_NAMES`
  - `WHEEL_RADIUS = 0.19`
- 当前 actor / critic 单帧观测维度已由：
  - `52 / 52`
  更新为：
  - `70 / 70`
- TensorBoard step-level 原始观测日志已新增：
  - `Observation/wheel_longitudinal_slip_abs_mean_raw`
  - `Observation/wheel_slip_angle_abs_mean_raw`
  - `Observation/wheel_normal_contact_force_abs_mean_raw`
  - `Observation/wheel_normal_contact_force_sum_raw`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/assets/__init__.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/assets/robot_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active direct workflow 已具备显式轮地滑移/侧滑/载荷分布观测。
- 当前法向接触力仍采用世界系 `z` 方向近似法向，这是当前实现里有意保留的简化，而不是局部接触面法向重建。
- 已通过目标文件的 `python3 -m py_compile` 静态编译检查。

已完成：
- 按用户要求删除车轮动作映射里重复的上下限配置项：
  - `wheel_joint_action_lower_limits`
  - `wheel_joint_action_upper_limits`
- 当前车轮动作只保留一个对称速度上限入口：
  - `wheel_joint_velocity_limit_sim`
- 当前后 6 维标准化车轮动作的映射已改为：
  - `wheel_target = action * wheel_joint_velocity_limit_sim`
- 因此当前车轮动作语义为：
  - `action = 1` 对应 `+v_max`
  - `action = -1` 对应 `-v_max`
  - `action = 0` 对应 `0`
- env 主链调用和文档说明已同步到这一口径。
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前车轮动作映射参数已收口，不再出现“先定义速度上限、再重复定义一组对称上下限”的冗余配置。
- 后续若要调整车轮动作幅值，只需要改：
  - `wheel_joint_velocity_limit_sim`
- 已通过目标文件的 `python3 -m py_compile` 静态编译检查。

已完成：
- 按用户要求，先将以下 5 组量从当前 active policy observation trunk 中注释掉，暂不送入 PPO：
  - 6 个球铰角速度
  - 6 个球铰目标跟踪误差
  - 前车绝对 roll/pitch
  - 后车绝对 roll/pitch
  - 6 个车轮轮速
- 当前修改只影响 actor / critic 观测主干，不影响：
  - 底层状态本身
  - reward 主链
  - 动作执行链
- observation descriptor 与 observation-noise 维度已同步收口。
- 当前 actor / critic 单帧观测维度已由：
  - `70 / 70`
  调整为：
  - `48 / 48`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active policy observation trunk 已精简为：
  - 中车 body-frame 线速度
  - 中车 body-frame 角速度
  - 中车重力投影
  - 6 个球铰角
  - 6 个车轮纵向滑移率
  - 6 个车轮侧滑角
  - 6 个按整车重量归一化的车轮法向接触力
  - 相对目标命令
  - 上一时刻动作
- 已通过目标文件的 `python3 -m py_compile` 静态编译检查。

已完成：
- 按用户要求，将轮胎法向接触力从“世界系 `z` 分量近似”改成“沿轮胎-地面接触法向”的更严格版本。
- 先对照本地 Isaac Lab 手册确认：
  - `ContactSensor.data.net_forces_w`
  本身就是世界系下的净法向接触力向量，而不是总接触力。
- 因此当前实现已从：
  - `max(0, F_contact · z_hat) / (m_total * g)`
  改为：
  - `||net_forces_w|| / (m_total * g)`
- 当前含义是：
  - 直接使用 6 个 wheel body 的净法向接触力向量模长
  - 再按整车总重量归一化
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前轮胎法向接触力不再依赖世界系竖直方向近似。
- 当前实现已经切到基于 Isaac Lab 法向接触力向量本身的更严格口径。

已完成：
- 按用户要求，将当前 direct workflow 的奖励主线从旧的速度跟踪型 reward 重构为目标导向 reward。
- 当前 reward 不再使用旧的：
  - `tracking_lin_vel`
  - `tracking_ang_vel`
  - `orientation`
  - `action_rate`
  - `ball_joint_limit_soft`
  - `termination`
- 当前 active reward 结构已经改为：
  - `target_bonus + gated_progress`
- 其中：
  - `progress = (d_{t-1} - d_t) * control_frequency`
  - `gated_progress = progress * roll_gate * speed_gate * force_gate * composite_gate`
  - `composite_gate = (heading_gate + longitudinal_slip_gate + lateral_slip_gate) / 3`
- 当前已新增并接线的 reward 组成包括：
  - `target_bonus`
  - `progress`
  - `roll_gate`
  - `speed_gate`
  - `force_gate`
  - `heading_gate`
  - `longitudinal_slip_gate`
  - `lateral_slip_gate`
  - `composite_gate`
  - `gated_progress`
- env 当前已维护：
  - 上一时刻目标距离缓存
  - reset 后目标距离初始化
  - 命令重采样后的目标距离重置
- TensorBoard step 级 reward 指标已同步切换为新的目标导向指标命名。
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 direct workflow 的 active reward 已正式切到目标达成 + 朝目标推进主线。
- 当前奖励已经与 goal-conditioned 命令空间一致，不再保留旧速度命令跟踪逻辑。
- 已通过针对改动文件的 `python3 -m py_compile` 静态编译检查。

已完成：
- 继续做 Stage0 的低滑移 / 低侧滑定向实验，不再插入单独 smoke，而是直接跑对比训练。
- reward 新增并保留：
  - `wheel_action_rate_gate`
- 训练日志新增并保留：
  - `Observation/base_lin_vel_y_raw`
- 试验并否决：
  - `lateral_speed_gate`
  - 在 `gated_progress` 外再次额外乘一次 `lateral_slip_gate`
- 已将上述两个否决方向从默认代码回退。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `docs/RL阶段训练参数一览表.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前最佳短跑参考 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-45-26_wheel_action_smooth_v1`
  - 在约 `iteration 39/40`：
    - `wheel_longitudinal_slip_abs_mean_raw ≈ 0.8145`
    - `wheel_slip_angle_abs_mean_raw ≈ 0.7318`
    - `base_lin_vel_x_raw ≈ 1.3777`
    - `Loss/value ≈ 0.027`
- `lateral_speed_gate` 已否决，对应 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-48-41_lateral_speed_gate_v1`
  - 结论：
    - critic 更稳
    - 但长期滑移/侧滑改善不足，不如 `wheel_action_smooth_v1`
- “额外提高 lateral slip 权重”也已否决：
  - 短跑：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-50-45_lateral_slip_priority_v1`
  - 长跑：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-52-30_lateral_slip_priority_v1_iter300`
    - 实际观察到约 `iteration 143/300` 后停止
  - 中后期结论：
    - critic 仍稳，`Loss/value ≈ 0.001 ~ 0.002`
    - 但策略重新回到激进区：
      - `base_lin_vel_x_raw ≈ 1.62 ~ 1.65`
      - `wheel_longitudinal_slip_abs_mean_raw ≈ 0.816 ~ 0.819`
      - `wheel_slip_angle_abs_mean_raw ≈ 0.733 ~ 0.735`
      - `tilt_deg ≈ 16.4 ~ 16.7`
- 当前默认代码已回到：
  - Stage0 稳定性优先 bundle
  - 平滑 slip gates
  - `wheel_action_rate_gate`

下一步：
- 不再继续叠加同类 multiplicative gate。
- 下一轮应转向更结构性的侧滑来源，例如轮速映射或动作语义，而不是继续在同一 reward 结构上加门。
