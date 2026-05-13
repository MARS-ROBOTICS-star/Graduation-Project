# 当前状态

## 当前 Stage1 history4 训练状态

- 2026-05-13 已按用户要求在 TensorBoard 写到 step `900` 后结束 `stage1_history4_hard_quality_96env_1000iter_20260513` 训练；训练进程已释放，GPU 无 IsaacLab compute 进程。
- 上一轮 725 续训已完成：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-13_00-42-29_stage1_model725_hard_quality_finetune_96env_300iter_20260513`，最终保存 `model_1024.pt`。
- 上一轮 725 续训最终结果：obstacles 推进明显改善，`col08` 末 25 step 平均 level 约 `14.52`，`col09` 约 `12.32`；但 stairs down 从中期约 row `10` 回退到末段约 row `5.6-5.7`，后车跟随仍低、接触支撑很低、near-edge overspeed 仍约 `0.92-0.95`，说明 hard quality reward 没有把台阶行为稳定下来。
- 当前最新 run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-13_03-25-50_stage1_history4_hard_quality_96env_1000iter_20260513`。
- runtime log：`RL_Training/logs/runtime/stage1_history4_hard_quality_96env_1000iter_20260513.log`；IsaacLab log：`/tmp/isaaclab/logs/isaaclab_2026-05-13_03-25-50.log`。
- 启动口径：`CompleteCar-Stage1`、headless、`cuda:0`、`96 env`、`--max_iterations 1000`、无 `--resume`、无 `--warmstart`。原因是 history4 使 actor 输入维度从 `82` 变为 `328`，不能直接加载旧 `model_725.pt` 的 actor。
- 当前源码已开启 `observations.use_history=True`、`observations.history_length=4`；新 run 的 `params/env.yaml` 已确认 `observation_space.actor=328`、`observation_space.critic=906`。
- `model_900.pt` 已确认落盘，时间 `2026-05-13 11:13:17 +0800`；TensorBoard 最终标量写到 step `901`，这是 `SIGINT` 发生在 `model_900.pt` 保存后、下一轮日志边界附近的结果。
- history4 训练过程：obstacles 两列曾推进到较高 row，`col08` 最高平均 row 约 `17.60`，`col09` 最高平均 row 约 `17.71`；stairs down 三列曾在 step `620-624` 附近到达平均 row `14.6-14.7`，随后回落。
- 结束时 stairs down 三列最终 row：`col05=6.66`、`col06=6.87`、`col07=6.89`；`rows_advanced_mean` 分别约 `0.24/0.33/0.28`，`row_advance_rate` 分别约 `0.23/0.26/0.26`。
- 用户已明确后续监督台阶训练时，优先看 `current_level_mean`、`rows_advanced_mean`、`row_advance_rate` 和推进速度；不要把 pitch、support、rear follow 作为台阶 row 推进判断的主要依据。
- 已完成全部 checkpoint 的 row 推进对比：若以 10 列平均 row 为主、平均 `rows_advanced_mean` 和 `row_advance_rate` 为辅，综合最优为 `model_500.pt`；若只看全地形 / hard terrain 平均 row 绝对高度，最优为 `model_625.pt`；若只看 stairs down 平均 row 最高，最优为 `model_650.pt`。
- 已按用户要求打包本次 history4 训练结果、TensorBoard 数据和 RL 环境配置，输出为 `results/stage1_history4_900_results_tensorboard_env_no_checkpoints_2026-05-13.zip`；包内不含 `model_*.pt`、`exported/` 或 ONNX 权重文件。
- 当前下一步：优先回放 / 对比 `model_500.pt`、`model_625.pt`、`model_650.pt` 和 `model_900.pt`，重点比较 `col05-col07 stairs_down` 的 row 推进能力与推进速度。

## 当前 Stage1 hard terrain reward / termination 优化状态

- 2026-05-13 已按用户确认的边界修改 Stage1：只新增 middle/root roll 终止，`orientation_limit_deg = 35.0`；未把侧倾纳入 `progress_quality_score`。
- `mdp/terminations.py` 现在返回 `orientation_out_of_bounds`，`base/env.py` 的 `_get_dones()` 已将其纳入 terminated，并增加 episode / step 级终止率与最大 roll 诊断。
- 下坑 / gap 抗俯冲已从单步弱惩罚升级为 drop guard latch：检测到 `g_step_down/g_gap` 且目标仍在前方后进入 guard，直到前轮接触稳定、pitch rate 与下落速度满足释放阈值后退出；Stage1 `drop_anti_dive_penalty_weight = -40.0`。
- stairs down 后车跟随已强化：上台阶支撑缺失惩罚采用 `mid=0.4,rear=0.6`，模块进展权重采用 `front=0.15,middle=0.35,rear=0.50`，并新增 `rear_follow_reward` / `rear_follow_penalty` 及 rear follow 诊断。
- hard terrain 低质量推进折减增强：`step_up_progress_quality_min_multiplier = 0.2`；quality 评价拆为严格 `quality_gate_score` 与加权 `motion_quality_score`，`quality_gated_terrain_advance` 仍保持 `False`。
- 已完成 `python3 -m py_compile` 和 `git diff --check`。普通 Python reward 小样本因当前环境缺 `pxr` 无法导入 Isaac Lab 包；Isaac 环境下的旧 `model_725.pt` col05-col09 reward audit 已完成，当前已进入从 `model_725.pt` 续训验证阶段。
- 2026-05-13 已完成旧 `model_725.pt` 对 col05-col09、row11 的 reward audit 回放：输出目录 `results/stage1_model725_col05_col09_reward_audit_2026-05-13/`，`15 env`、`120 warmup + 1200` control step，导出 `17980` 行有效样本，无 done rows。
- reward audit 末 `100` step 总体结论：收益排序已经明显改写，`drop_anti_dive_penalty` 约为 progress 量级的 `0.58x`，`step_up_front_posture_penalty` 约 `0.60x`，`rear_follow_penalty` 约 `1.56x`，`step_up_module_progress_reward` 约 `0.10x`；col05-col08 的 hard penalty 已压过 progress，col09 仍保持 selected net 为正。
- 本次 audit 显示 `quality_gate_score` 在 col05-col09 末段均为 `0`，因此当前 strict gate 只能作为诊断，不应直接重新开启 `quality_gated_terrain_advance`；`motion_quality_score` 末段约 `0.32-0.43`，更适合作整体运动质量评分。

## 当前 RL 底层运动学状态

- 2026-05-12 已按用户要求把 `RL_Training` 主环境底层运动学改回原模型；恢复来源为 `backups/low_level_kinematics_20260512_232415/`。
- 当前 active 链路重新回到 direct-target 口径：policy 输出 `q_desired` 后直接限幅为球铰 position target `q_target = clamp(q_desired)`。
- 轮速分配中的姿态变化率重新使用实际球铰角速度低通：`qdot_alloc = LPF(qdot_actual)`，`tau_v = 0.04 s`。
- 球铰 drive 参数恢复为 `Kp=120,Kd=10,effort=60 N*m,velocity=2.0 rad/s`；不再向球铰下发 velocity target。
- 2026-05-12 曾短暂迁入 `q_desired -> q_cmd/qdot_cmd` reference governor 并导出平地 trace，结果保留在 `results/stage1_model725_flat_refgov_pd_2026-05-12/` 作为历史对照；该链路现在不是 active 源码口径。
- 当前下一步若继续回放或导出 trace，应按已恢复的 direct-target + `qdot_alloc` 口径解释 `q_position_target` 和 `qdot_alloc` 字段。

## 当前 USD 直连 front pitch 在线 PD 控制器离线扫参状态

- 已新增离线扫参脚本：`scripts/isaac_sim/sweep_front_pitch_trace_pd.py`，用于在进入 Isaac Sim 前先筛选 `q_desired -> q_cmd/qdot_cmd -> PD plant` 的控制器参数。
- 该脚本与 `replay_front_pitch_trace_pd.py` 使用同一条控制链路：历史 `q_desired_spm1_platform_joint_y` 先经过 reference governor 生成平滑且限速 / 限加速度的 `q_cmd/qdot_cmd`，再用简化单轴 PD plant 评估底层跟踪、原始目标滞后、力矩饱和、速度贴限和速度命令抖动。
- 最新推荐结果目录：`results/front_pitch_trace_pd_usd_sweep/model725_col05_env5_kp1200_1600_kd2_10_ultrafine_20260512_230706/`；输入 trace 为 `model725_allcols_30hz_col05_stairs_down.csv`、`env_id=5`，共 `1198` 个样本。
- 2026-05-12 按用户要求扩展到 `Kp=100-5000`、`Kd=2-2000` 后完成三轮扫参：全局粗扫 `640000` 组、局部细扫 `244608` 组、最优区超细扫 `176256` 组。全局范围确认最优不贴 `Kp=5000`，而 `Kd` 持续贴近用户给定下界 `2`。
- 最新超细扫范围：`Kp=1200:5:1600`、`Kd=2:0.5:10`、`tau_ref=0.06/0.08/0.10/0.12 s`、`qddot_limit=3/4/5/6/8/10/12/16 rad/s^2`、`velocity_limit=1.2/1.5/1.8/2.0 rad/s`、`effort_limit=60 N*m`；plant 使用 `J=0.115`、`B=18.0`、`tau_load=0`。
- 按综合 `risk_score` 排序的当前最优候选：`Kp=1390,Kd=2,tau_ref=0.12 s,qddot_limit=16 rad/s^2,velocity_limit=2 rad/s,effort=60 N*m`；离线 `q_cmd -> q_model` 平均误差 `0.003308 rad`，`q_desired -> q_model` 平均误差 `0.147381 rad`，力矩饱和率 `0%`，速度贴限率约 `6.34%`，但 `qdot_cmd` 变化均值约 `0.406 rad/s`，更激进。
- 更平滑的 Isaac Sim 首验候选更新为：`Kp=1470,Kd=2,tau_ref=0.12 s,qddot_limit=3 rad/s^2,velocity_limit=1.2 rad/s,effort=60 N*m`；离线 `q_cmd -> q_model` 平均误差 `0.001706 rad`，`q_desired -> q_model` 平均误差 `0.237393 rad`，速度命令变化均值约 `0.093893 rad/s`，力矩峰值约 `21.6 N*m`。
- 解释边界：该扫参是 USD 直连控制器进入 Isaac Sim 前的候选筛选，不是最终真实动力学结论；最终是否采用仍需 `replay_front_pitch_trace_pd.py` 打开 `complete_car.usd` 后观察姿态、碰撞、速度命令和误差 summary。

## 当前 USD 直连 front pitch trace PD 测试状态

- 已新增独立 Isaac Sim 旁路测试脚本：`scripts/isaac_sim/replay_front_pitch_trace_pd.py`。
- 该脚本不导入 `RL_Training` env、不修改 `wheel_speed_allocator.py`、不需要训练；它直接打开 `USD/complete_car.usd`，读取历史 trace 中的 `q_desired_spm1_platform_joint_y`，经 reference governor 生成稳定的 `q_cmd/qdot_cmd`，再通过 `SingleArticulation.apply_action()` 同时向 `spm1_platform_joint_y` 下发 position target 和 velocity target。
- 2026-05-12 已加入 GUI 实时查看能力：非 headless 运行时默认创建 `Front Pitch Trace PD Monitor` 的 `omni.ui` 窗口，实时显示 `q_desired/q_cmd/q_actual`、position error、velocity error、估计 PD 力矩、力矩饱和率、速度命令限幅和运行均值；同时默认把 viewport camera 调到便于观察车辆的角度。
- 新增 GUI 相关参数：`--require-gui` 用于没有可用显示时直接报错而不是静默 headless；`--realtime-factor` 控制 GUI 播放速度，`1.0` 表示按 trace 实时播放；`--hold-open` 控制回放结束后窗口保留秒数；`--no-gui-monitor` 和 `--no-camera-setup` 可关闭实时数据窗口或自动相机设置。
- 2026-05-12 已将地面改为默认创建：脚本会在 `/World/defaultGroundPlane` 创建一个本地 `30 m x 30 m`、顶面 `z=0` 的灰色静态碰撞地面，不再依赖 Isaac 默认地面资源；若要关闭地面需显式传 `--no-ground`。
- 默认输入 trace 为 `results/stage1_model725_allcols_30hz_fine_pd_2026-05-12/raw_traces/model725_allcols_30hz_col05_stairs_down.csv`，默认 `env_id=5`、`Kp=600,Kd=30`、`effort_limit=60 N*m`、`velocity_limit=2 rad/s`、`qddot_limit=8 rad/s^2`、`tau_ref=0.05 s`。
- 输出目录默认为 `results/front_pitch_trace_pd_usd/`，会导出逐步记录 CSV 和 summary JSON；指标区分 `q_cmd -> q_actual` 底层跟踪误差、`q_desired -> q_actual` 原始目标执行误差、`qdot_cmd -> qdot_actual` 速度误差、估计力矩饱和率和 `qdot_cmd` 抖动。
- 已完成语法和 trace 字段检查；短 smoke 结果包括旧 `Kp=600,Kd=30` 三帧测试、新 GUI 参数后的 `Kp=1250,Kd=2.5` 两帧测试，以及默认创建地面后的 `1` 帧测试：`results/front_pitch_trace_pd_usd/spm1_platform_joint_y_env5_kp1250_kd2.5_20260512_230338/front_pitch_trace_pd_summary.json` 中 `|q_cmd-q_actual|` 均值约 `4.90e-05 rad`，估计力矩饱和率 `0%`。该 smoke 仅验证脚本链路可执行；当前运行环境仍报告 `no CUDA-capable device` / GPU renderer 警告，不能作为完整 GUI 或物理稳定性结论。

## 当前 RL policy 动作更新频率状态

- 已按用户要求将当前 RL policy 动作更新频率从 `60 Hz` 降到 `30 Hz`。
- 当前统一口径：`control.sim_dt = 1/120 s` 保持不变，`control.decimation = 4`，`control.control_dt = 1/30 s`；即每个 policy action 保持 `4` 个 PhysX 子步。
- Stage0、Stage1 和共享 Base 配置已同步；Stage2 继承 Base 默认值，因此后续默认也是 `30 Hz`。
- `episode_length_s = 40.0 s` 未改变，因此 Stage0 / Stage1 的 `max_episode_length` 由 `2400` 个控制步变为 `1200` 个控制步。
- PPO `num_steps_per_env = 512` 未在本次改动中调整；后续每个 rollout 覆盖的真实时间会从约 `8.53 s` 变为约 `17.07 s`。
- 2026-05-12 已导出的 `model_725.pt` 球铰 trace 和基于该 trace 的相对误差扫参来自旧 `60 Hz` 控制口径；若要评估新动作频率下的球铰跟踪，应重新导出 `30 Hz` trace 后再扫参。

## 当前 `model_725.pt` 30 Hz 全地形 trace 与 Kp/Kd 精扫状态

- 已按当前 `30 Hz` 控制口径重新导出 `model_725.pt` 覆盖 Stage1 地形列 `0-9` 的全地形球铰 trace。
- 输出目录：`results/stage1_model725_allcols_30hz_fine_pd_2026-05-12/raw_traces/`；`30 env`，每列约 `3 env`；`flat row0`，`slope / rough row5`，`stairs_down / discrete_obstacles row11`；总有效样本 `35972` 行，done rows 为 `0`。
- 已新增并继续修正 `scripts/matlab/stage1_ball_joint_pd/run_fine_kpkd_sweep_numba.py`，用于大范围 Kp/Kd 精扫；它不调用 MATLAB/Simulink，而是用 Numba 复现单轴 PD plant、力矩限幅、速度限幅和相对误差排序逻辑。当前版本会先用已知 `Kp=120,Kd=10` 的 Isaac trace 校准简化 plant，再用校准 plant 进行 Kp/Kd 扫参。
- 本次精扫范围：`Kp = 100:10:2000`、`Kd = 10:10:1000`，共 `19100` 组；最终用于扫参的校准 plant 为 `J=0.115 kg*m^2`、`B=18.0`、`tau_load=-2.0 N*m`、`tau_max=60 N*m`、`qdot_max=2 rad/s`。校准 RMSE 为 `0.078885 rad`，输出 `plant_calibration_grid.csv` 和 `plant_calibration_best.json`。
- 最新校准后排序结果目录：`results/stage1_model725_allcols_30hz_fine_pd_2026-05-12/sweep_kp100_2000_kd10_1000_isaac_calibrated_rmse/`。
- 最新 `risk_score` 已按用户要求将力矩饱和率和速度贴限率惩罚阈值从 `0.30` 放宽到 `0.70`；这是排序函数阈值，不改变 Isaac 或 plant 中的 `tau_max=60 N*m`、`qdot_max=2 rad/s` 物理限幅。
- 按 `risk_score` 综合排序，第一名为 `Kp=100,Kd=10`，`risk=0.869811`，相对误差均值 `0.790135`，绝对误差均值 `0.102371 rad`，力矩饱和率约 `0.000380`，速度贴限率约 `0.294929`；该点保守平滑，但跟踪改善有限。
- 在 `sat_ratio <= 0.70` 且 `qdot_limit_rate <= 0.70` 的用户阈值内，按最小相对误差排序第一名为 `Kp=1690,Kd=10`，相对误差均值 `0.462546`，绝对误差均值 `0.060708 rad`，但速度贴限率 `0.698579` 已贴近上限，力矩饱和率 `0.417033`，不宜未经 Isaac replay 直接作为训练默认。
- 在更保守的 `qdot_limit_rate <= 0.60`、`sat_ratio <= 0.30` 内，按最小相对误差排序第一名为 `Kp=990,Kd=10`，相对误差均值 `0.493667`，绝对误差均值 `0.063795 rad`，力矩饱和率 `0.299431`，速度贴限率 `0.535233`；若要继续做真实 Isaac replay 验证，这是比 `1690/10` 更稳的候选。
- Simulink 模型 `scripts/matlab/stage1_ball_joint_pd/stage1_ball_joint_pd_uniform.slx` 已重建为当前 trace 口径：默认加载 `model725_allcols_30hz_col05_stairs_down.csv`，默认 `env_id=5`，默认增益 `Kp=170,Kd=30`；模型中不再导入或显示 `q_target_old/q_actual_old/qdot_cmd_old` 等旧 planner 信号，只显示 `q_desired`、Isaac trace 的 `q_position_target/q_actual/qdot_actual/qdot_alloc` 和简化 PD 仿真输出。
- 若只想判断当前 Isaac 实际跟踪是否合适，Simulink plant 不是必要步骤；已新增 `scripts/matlab/stage1_ball_joint_pd/plot_model725_trace_desired_vs_actual.m`，直接从 trace 画 `q_desired` 与 `Isaac actual` 六关节曲线，并单独生成估计球铰 PD 力矩图。默认角度图：`results/stage1_model725_allcols_30hz_fine_pd_2026-05-12/trace_figures/desired_vs_isaac_actual_env5_model725_allcols_30hz_col05_stairs_down.png`；默认力矩图：`results/stage1_model725_allcols_30hz_fine_pd_2026-05-12/trace_figures/estimated_torque_kp170_kd30_env5_model725_allcols_30hz_col05_stairs_down.png`。该力矩是按 `tau=Kp*(q_target-q_actual)-Kd*qdot_actual` 和 `±60 N*m` 限幅从 trace 估算的 PD 命令，不是 Isaac 直接导出的 measured joint torque。
- 已按用户要求完成一次真实 Isaac replay-only 验证：`model_725.pt` 在 `Kp=910,Kd=10, effort=60 N*m, velocity=2 rad/s` 下重新导出 30 Hz 全地形 trace。有效输出目录：`results/stage1_model725_allcols_30hz_kp910_kd10_applied_2026-05-12/`；日志明确打印 `Ball-joint replay drive: Kp=910, Kd=10, effort=60, velocity=2`。注意：此前未重建 robot actuator cfg 的 `stage1_model725_allcols_30hz_kp910_kd10_2026-05-12/` 不作为结论数据。
- `Kp=910,Kd=10` 实际 replay 全地形误差：`|q_desired-q_actual|` 均值 `0.116173 rad`、RMSE `0.171553 rad`、p95 `0.372855 rad`、p99 `0.566413 rad`、最大 `1.462076 rad`；相对误差均值 `0.731970`、p95 `2.050437`；速度贴限率 `18.839%`；估计 PD 力矩饱和率 `46.133%`。与前次 `Kp=120,Kd=10` 30 Hz 真实 trace 对比，绝对误差均值几乎不变（`0.116990 -> 0.116173 rad`），相对误差下降（`0.891246 -> 0.731970`），但绝对误差 p95 变差（`0.300481 -> 0.372855 rad`）、速度贴限率明显升高（`3.581% -> 18.839%`）。
- 已按原训练增益 `Kp=120,Kd=10` 对 `model_725.pt` 重新跑第 `5` 列 `stairs_down` 回放并导出包含 reward diagnostic 的 trace，输出目录：`results/stage1_model725_col05_diag_kp120_kd10_2026-05-12/`；日志确认 `Ball-joint replay drive: Kp=120, Kd=10, effort=60, velocity=2`。
- 第 `5` 列末 `100` control step、`6` 个 env 聚合诊断：`front_pitch_ref` 均值 `-0.207373 rad`，`q_desired_spm1_platform_joint_y` 均值 `-0.045937 rad`，`front_pitch_actual/q_actual` 均值 `0.022644 rad`；`q_desired-front_pitch_ref` 均值 `0.161436 rad`、绝对均值 `0.241683 rad`，`q_actual-q_desired` 均值 `0.068581 rad`、绝对均值 `0.171945 rad`，`front_pitch_actual-front_pitch_ref` 绝对均值 `0.251207 rad`。前 pitch 的速度贴限率约 `7.0%`，估计力矩饱和率约 `0.833%`。
- 本次第 `5` 列诊断结论：`front_pitch_ref` 是奖励/诊断参考，不是直接下发的 actuator command；主要差距来自策略没有稳定把 `q_desired` 推向该参考姿态，底层 PD 跟踪误差存在但不是这段 `front_pitch_ref` 与 `front_pitch_actual` 大误差的首要来源。末 `100` step 中 `terrain_gate_step_up` 均值约 `0.716`，但 `step_up_approach_mask` 仅约 `0.09`，说明显式前 pitch 姿态惩罚激活范围很窄，策略有较大空间忽略该参考。
- 已生成 `front_pitch_ref` 逻辑链路可视化报告：`results/front_pitch_ref_logic_visual_2026-05-12/front_pitch_ref_logic_visual_report.md`。真实 col05 row11 trace 验证显示：全 trace 中 `front_pitch_ref` 饱和率约 `65.9%`，`step_up_approach_mask` 均值约 `14.2%`；`step_up_distance_m <= 0.20 m` 的接触/很近阶段占 `56.6%`，末 `100` step 占 `66.5%`，这些阶段 `g_step_up` 和 `|front_pitch_ref|` 都很高，但显式前 pitch 姿态惩罚因 `approach_mask=0` 关闭。当前更像是 approach 阶段短暂提醒 policy，而不是接触/爬升阶段持续约束前 pitch。
- 2026-05-12 已将 Stage1 `front_pitch_ref` 的显式姿态惩罚激活从旧 `approach_mask` 改为真实车头相位 `front_gap_m = step_up_distance_m - terrain.patch_front_extent`；其中 `terrain.patch_front_extent = 0.942209 m`。当前 `step_up_posture_weight` 在 `front_gap_m = 0.60 -> 0.15 m` 逐渐激活；达到满激活后，只要 `g_step_up` 仍存在且目标仍在前方，就不再因为车头已经接近或压上台阶而提前释放。现有相位速度限制、超速惩罚和模块高度推进 reward 保持不变。
- 已用旧 release 版本的第 `5` 列 `stairs_down row11` trace 复算新无 release 公式：全 trace `step_up_posture_weight` 均值由约 `0.156` 提升到 `0.723`，末 `100` step 均值由约 `0.0447` 提升到 `0.891`。这说明新激活逻辑会在接触/爬升末段继续约束前 pitch 姿态，不再只在接近台阶前短暂提醒。
- 已按 row11 第 `5` 列重新收集真实 height patch 数据并生成可视化报告：`results/stage1_row11_col05_height_patch_real_2026-05-12/row11_col05_real_height_patch_report.md`。有效数据目录为 `raw_col05/`，包含 `900` 个真实局部高度图 snapshot；报告直接从 `terrain_z_world` 和训练使用的 `h_rel_m` 复算中心剖面、正向高度跳变、`step_up_height_m`、`step_up_distance_m` 和 `front_pitch_ref`。复算结果：`step_up_height_m` 均值 `0.1033 m`、中位数 `0.1138 m`、p95 `0.1421 m`，`front_pitch_ref` 饱和率约 `65.1%`。按 reward / observation 的 `1` step 时序差对齐后，复算 `front_pitch_ref` 与 CSV diagnostic 最大差约 `1.53e-07 rad`，说明该链路与训练源码一致。注意同目录早先 `raw/` 是未重置 replay curriculum 的 flat 数据，不作为 row11 结论。
- 解释边界：本次没有把 `Kp/Kd` 精网格再乘完整 `J/B/tau_load/tau_v/qdot_max` 不确定性网格，因为组合会达到 `35,812,500` 组，不适合直接全量运行；若需要鲁棒结论，应基于当前精扫结果再做局部不确定性复扫。

## 当前 Stage1 `model_725.pt` 球铰 trace 与 PD 扫参状态

- 已导出 `model_725.pt` 覆盖 Stage1 地形列 `0-9` 的 headless 球铰真实 trace，输出目录为 `results/stage1_model725_allcols_ball_joint_pd_2026-05-12/raw_traces/`。
- 导出口径：`30 env`，每列约 `3 env`；`flat row0`，`slope / rough row5`，`stairs_down / discrete_obstacles row11`；每列约 `3600` 行有效 control-step 样本。
- 已将 `run_expanded_pd_sweep.py` 改为支持自定义 trace 目录 / glob，并把扫参排序核心改为相对误差 `|q_target - q_actual| / max(|q_target|, 0.05 rad)`，避免只看绝对误差低估小目标下的大比例跟踪失败。
- 当前 `Kp=120, Kd=10` 在 `model_725.pt` trace 上：全地形 `target_gap_abs_mean = 0`，说明 `q_desired` 已直接进入 position target；但 stairs_down 前 pitch 轴真实误差约为目标幅值的 `88%-92%`，且 `q_desired` 每步跳变约为当前 `2 rad/s` 速度上限每步可跟踪量的 `2.0x-2.1x`。
- 新相对误差鲁棒扫参第一候选为 `Kp=160, Kd=10, tau_v=0.03`；但其平均 `qdot_limit_rate ≈ 0.326`，后续进入训练配置前仍需 Isaac 短回放验证稳定性。

## 当前 Stage1 obstacle 地形高度参数状态

- 已将 `discrete obstacles` 最大障碍高度系数从 `0.20` 调整为 `0.17`，当前公式为 $h_{\mathrm{obs,max}} = 0.05 + 0.17 \cdot difficulty$。
- 在 `num_rows = 20`、`vertical_scale = 0.005 m` 下，最高 `row 19` 的公式高度为 `0.2115 m`，heightfield 实际最大障碍高度量化为 `0.21 m`。
- 当前修改只影响后续重新生成的 Stage1 地形；已生成 run 的历史地形和历史回放不 retroactively 改变。

## 当前 Stage1 回放视频处理状态

- `model_725.pt` 在 Stage1 地形列 `5 / 8 / 9` 的双视角 2K 录制已生成原速版和 `_slow2x` 慢放版。
- `_slow2x` 文件通过时间戳缩放生成，不重新编码；画质不损失，播放速度为原来的 `0.5x`，原 `20 min` 视频变为约 `40 min`，原 `10 min` 视频变为约 `20 min`。
- 视频目录：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-11_12-20-55_stage1_80env_resume_from_m100_1000iter_20260511_1220/videos/play/`。
- 已从 `model725_col05_dual_2k_goal_patch_20min_fixed_chase_slow2x.mp4` 剪出播放时间 `6:07-6:37` 的 30 秒片段，输出为同目录 `model725_col05_dual_2k_goal_patch_20min_fixed_chase_slow2x_6m07_6m37.mp4`；原视频保留不变。
- 已按 `model_725.pt`、`col03 rough`、`1 env`、目标 marker 和局部高度图配置录制 `5 min`、`1080p`、`chase` 视角视频：`model725_col03_rough_goal_patch_5min_chase_1080p.mp4`。
- `RL_Training/scripts/play.py` 已新增 `--zero_actions`，仅用于回放时把 policy action 置零，方便静止观察 debug 可视化，不改变训练逻辑。
- `play.py --follow_view_top_height` 的实际回放默认值已从 `2.5 m` 调整为 `3.5 m`。
- 已生成 `model_725.pt` 的 `flat / col00` 静止顶视 4K 局部高度图截图；最新 `3.5 m` 顶视高度版本为：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-11_12-20-55_stage1_80env_resume_from_m100_1000iter_20260511_1220/videos/play/model725_flat_static_topdown_h3p5_heightpatch_4k_frame.png`。

## 当前台阶准静态模型参数整理状态

- 已新增 `docs/台阶爬升准静态模型参数整理.md`，按车轮参数、三节车体几何、球铰姿态范围、质量与质心、接触摩擦、台阶地形、车体底部关键点和初始姿态整理当前可确认参数。
- 文档明确区分两套口径：USD/CAD 实际装配几何与 `wheel_speed_allocator.py` 当前底层简化运动学几何；第一版台阶准静态推导建议使用“车体质心坐标系 + CAD/URDF 几何”，若要复现训练代码轮速分配器则必须按 allocator 源码公式。
- 已确认关键默认值：车轮半径 `0.19 m`、车轮力矩上限 `20 N·m`、六轮全驱、球铰 position drive `Kp=120, Kd=10, effort=60 N·m, velocity=2 rad/s`、pitch 范围 `[-1.6, 0.5] rad`、摩擦 `static/dynamic=1.0`、恢复系数 `0.0`。
- 已新增 `docs/三体二维准静态台阶接触可行性模型.md`，推导三体二维准静态接触可行性模型，并按当前 Stage1 台阶步宽 `0.31 m`、轮半径 `0.19 m`、球铰限位和车体底部 clearance 计算多级台阶高度边界。
- 当前理论解释边界：若只按“允许球铰变形、车体不穿模、三对轮能落在多级台阶踏面上”的几何 / 接触可行口径，最大单级台阶高度约 `0.216 m`，对应 row `18-19` 之间；若要求不依赖动态冲击且轮端准静态推爬仍有合理力学余量，有效稳定上限约 `0.165 m`，对应 row `13` 附近。row `15-16` 已接近轮半径奇异区，row `16+` 不能再用普通准静态轮式爬升能力解释。

## 当前文献 PDF 转 Markdown 工具状态

- 已新增 Codex Skill：`/home/lbz/.codex/skills/opendataloader-pdf/`。
- 后续文献 PDF 转 Markdown 默认使用该 Skill 和本地 OpenDataLoader PDF 项目；MinerU 不作为默认工具，`pdftotext` 仅用于诊断或修复 OpenDataLoader 已确认无法恢复的 PDF 字体/CMap 损坏片段，不作为整批替代转换器。
- 当前固定本地项目路径：`/home/lbz/opendataloader-pdf-fulltty`，其远端为 `https://github.com/opendataloader-project/opendataloader-pdf.git`；`/home/lbz/` 下重复的 `opendataloader-pdf*` 实验目录已清理，只保留该目录。
- Skill 内置批量转换脚本：`/home/lbz/.codex/skills/opendataloader-pdf/scripts/convert_pdfs.py`。
- 本终端环境运行 OpenDataLoader 时需设置 `JAVA_TOOL_OPTIONS=-Djava.awt.headless=true`。
- `docs/literature/lunwen` 已完成 PDF 清理与第一章写作用途分类：删除 `20` 个内容完全一致的 `-1.pdf` 副本，并按用户追加要求删除 `14` 个 `_zh-CN_dual.pdf` 双语版本；当前分类语料保留英文/原始版本 `41` 个 PDF，另有用户加入的本科毕业设计样本 `基于双目视觉的多自由度机械臂避障与运动规划 (2).pdf` 用于第一章写作风格调研；当前未发现 `_zh-CN_dual.pdf` 文件。
- `docs/literature/lunwen` 当前按 `01_development_and_applications`、`02_morphology_structure_mechanism`、`03_model_based_dynamics_control`、`04_terrain_perception_planning`、`05_rl_complex_terrain_control`、`06_learning_frameworks_transfer` 六类组织；第一章各小节参考文献选择和写作思路见 `docs/literature/lunwen/第一章文献分类与写作思路.md`。
- 已按用户逐节评价与修改建议继续润色第一章绪论 Markdown 初稿：`docs/literature/lunwen/第一章绪论初稿.md`；新版 `1.1` 从复杂地形失效机制切入，弱化工具平台表述，将“感知”收窄为当前阶段的局部地形观测。
- 新版第一章已重构为带二级小节的硕博论文式结构：`1.2` 按折腰转向/全地形运输、工程车辆机器人化、主动形态调节、模型控制到学习控制展开；`1.3` 改为三节主动铰接复杂地形控制难点；`1.4` 按模型方法的启示与局限组织；`1.5` 增加课程学习与 Stage0 到 Stage1 阶段训练逻辑；`1.7` 降调为“本文主要研究内容”。正文采用顺序编码引用，末尾列出 `42` 条参考文献，当前参考文献条目仍需后续按学校格式逐条核对。
- 正式 LaTeX 第一章 `毕业论文/毕业论文模板/LaTeX/chapters/chapter01.tex` 已补写 `1.4 论文主要研究内容`：按等效建模与仿真平台、底层运动控制链路、强化学习任务构建、Stage0 到 Stage1 阶段化训练与评价四项组织，并保持“不预设主动铰接结构必然优于其他结构”的表述边界。
- 正式 LaTeX 第二章和第四章正文初稿已更新：`chapter02.tex` 写成“系统结构与仿真建模”，突出从真实机构到可训练仿真模型的转换；`chapter04.tex` 写成基于强化学习的地形自适应控制方法，按分层控制、RL 问题定义、Stage0、Stage1、PPO warm-start 和结果边界展开。用户已明确要求第三章原来的运动学模型推导和底层动力学/轮级分配完整保留，当前 `chapter03.tex` 已恢复为“车辆运动学建模”主线，不再用 3-RRR 正逆运动学推导替换原正文。
- 已按用户澄清生成 `docs/literature/全部文献BibTeX.md`：扫描 `docs/literature/**/*.pdf` 共 `158` 个 PDF，按规范化题名合并跨目录副本、`-1` 副本和 `_zh-CN_dual` 双语副本后得到 `95` 个唯一 BibTeX 条目；缺少完整出版信息的条目用本地 PDF 文件名推断并保留草稿提示，正式进入论文参考文献库前仍需逐条核对。
- `docs/literature/全部文献LaTeX引用.md` 是此前误按 LaTeX 正文引用键生成的清单，不是本轮用户最终要求的 BibTeX 输出。
- 已使用 OpenDataLoader 将 `docs/literature/综述论文/Wang 等 - 2024 - A Survey on Path Planning for Autonomous Ground Vehicles in Unstructured Environments.pdf` 转换为 `docs/literature/output/Wang 等 - 2024 - A Survey on Path Planning for Autonomous Ground Vehicles in Unstructured Environments.md`；该 PDF 与 `docs/literature/lunwen/` 下同名文件 SHA-256 一致，输出 Markdown 为 `851` 行，并生成 `12` 张图片资源。
- 已使用 OpenDataLoader 将 `docs/literature/综述论文/无人驾驶铰接转向车辆路径跟踪控制研究综述_祝青园.pdf` 转换为 `docs/literature/output/无人驾驶铰接转向车辆路径跟踪控制研究综述_祝青园.md`；源 PDF 为 `21` 页，输出 Markdown 为 `966` 行，并生成 `16` 张图片资源。该 CNKI PDF 存在字体/CMap 映射警告，正文整体可读，但公式变量和部分参考编号可能需要回查源 PDF。
- 已使用 OpenDataLoader 将 `docs/literature/铰接车发展历史` 中 `20` 个 PDF 覆盖转换到 `docs/literature/output/铰接车发展历史`，输出 `20` 个 Markdown 文件、`20` 个图片目录、`528` 张图片。
- 本次已修复该目录中 PDF 连字、私有区数学字形和参考文献空括号问题：`15` 个文件进行了通用乱码清理，其中 `2自由度铰接车体车辆越障偏移饱和控制_寇伟.md` 与 `张君 - 2019 - 双桥独立驱动铰接车辆牵引力控制策略研究.md` 因 CNKI PDF 字体/CMap 损坏严重，保留 OpenDataLoader 图片目录并用 PDF 文本层重建正文。
- 已基于上述 `20` 篇 Markdown 完成铰接车发展历史文献阶段 `3-8` 的结构化整理，输出位置仍为 `docs/literature/output/铰接车发展历史`。
- 阶段 `3-8` 产物包括：`literature_database.yaml`、`missing_references.md`、`classification_system.md`、`timeline.md`、`timeline.html`、`articulated_vehicle_review.md`、`quality_check.md`。
- 已完成一轮铰接式越野车辆综述网络检索：国外最直接的发展脉络综述仍以 Holm 1970《Articulated, wheeled off-the-road vehicles》为核心；国内优先使用成龙 2018《铰接履带式全地形车技术发展对比解析》、李补莲和叶晓彤 2011《俄罗斯铰接式全地形车》、曲学春等 2014《国外履带式全地形车发展现状》等中文来源；近年补充可用 SAE 2023 主动铰接轮式架构和 Euro-SD 2025 军用铰接全地形车述评。
- SAE 2023《Actively Articulated Wheeled Architectures for Autonomous Ground Vehicles - Opportunities and Challenges》的 NSF PAGES accepted manuscript 公开全文已下载到 `docs/literature/综述论文/Mehta 等 - 2023 - Actively Articulated Wheeled Architectures for Autonomous Ground Vehicles - Opportunities and Challenges.pdf`。
- 已基于本地 `docs/literature/` 语料整理铰接式越野车辆与 AAWV 发展脉络，输出 `docs/literature/铰接式越野车辆与AAWV发展脉络整理.md`；文件包含 `21` 个车辆/图谱条目，每个条目均给出图片、文字说明、图片来源文献和本地引用位置/引用状态，并补充可用于第一章的综述表述草稿。
- 当前语料中没有直接以强化学习控制铰接式移动机器人为主题的论文；综述中应把 RL 作为当前课题的研究缺口和后续路线，不应写成该文献集已经验证过的成熟方向。
- 当前结构化抽取仍有不确定项：部分论文的铰接自由度、DOI、期刊/会议信息和复杂公式需要回查源 PDF 或补充数据库检索；相关位置已用 `[UNCERTAIN]` 或 `[MISSING]` 标记。

## 当前 Stage1 地形训练状态

- 2026-05-11 `80 env` Stage1 续训已完整结束，并已完成 hard terrain checkpoint 横向比较：
  - 新 run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-11_12-20-55_stage1_80env_resume_from_m100_1000iter_20260511_1220`
  - runtime log：`RL_Training/logs/runtime/stage1_80env_resume_from_m100_1000iter_20260511_1220.log`
  - 启动口径：`CompleteCar-Stage1`、headless、`cuda:0`、`80 env`、`--resume --load_run 2026-05-11_11-24-20_stage1_96env_1000iter_20260511_112415 --checkpoint model_100.pt`、`--max_iterations 1000`。
  - 降到 `80 env` 的原因：上一轮 `96 env` 在 `iteration 121/1000` 后触发系统 OOM，当前机器无 swap，继续 `96 env` 中途再次被 kill 风险高。
  - 完成状态：训练正常跑到 `1099/1100`，`Time progress = 100.0%`，训练耗时约 `24384.78 s`；最后 checkpoint 为 `model_1099.pt`，当前无 Stage1 训练进程。
  - 结果配置包：`results/stage1_80env_resume_from_m100_results_config_no_checkpoints_2026-05-11.zip`，大小约 `27M`，`unzip -tq` 通过；包含 TensorBoard event/export、params、git diff、runtime log、Stage1 源码/文档，排除 `model_*.pt` checkpoint、`exported/` 策略权重、回放视频和 Python bytecode 缓存。此前含 checkpoint 的 `170M` 包仍保留在 `results/stage1_80env_resume_from_m100_results_config_2026-05-11.zip`。
  - 重要解释：该 resume 继承策略 / 优化器 checkpoint，但不继承上一轮环境中的 terrain-column row / completed-column 状态；新 run 中 `completed_column_rate` 从 `0` 重新开始，`unfinished_column_count = 10`。这意味着它是“从 model_100 权重继续训练”，不是“从 step 122 的 row 分布原地续跑”。
  - 最终结果：`completed_column_rate = 0.5`、`unfinished_column_count = 5`，未完成列仍集中在 `col05-col07 stairs_down` 与 `col08-col09 obstacles`；障碍列后期推进明显，台阶列曾在中段到 row `13+`，末段回落到 row `10` 左右。
  - checkpoint 横向比较结论：若单看 hard terrain 平均 row，`model_825.pt` 最高；若要回放观察整体 hard terrain 推进与行为质量，优先候选为 `model_900.pt`，其 hard 平均 row 约 `11.53`、五列 row 约 `[11.6, 11.6, 11.6, 13.8, 9.1]`、平均 adv_rate 约 `0.448`、平均 pitch 约 `13.6 deg`、rear follow 约 `0.442`。若更重视所有 hard 列都超过 row `10`，候选为 `model_950.pt`；若只看障碍最高 row，候选为 `model_1099.pt`；若只看台阶最高 row，候选为 `model_725.pt`。
- 2026-05-11 新一轮 Stage1 `96 env / 1000 iteration` 长训已异常结束：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-11_11-24-20_stage1_96env_1000iter_20260511_112415`
  - runtime log：`RL_Training/logs/runtime/stage1_96env_1000iter_20260511_112415.log`
  - 启动口径：`CompleteCar-Stage1`、headless、`cuda:0`、`96 env`、`1000 iteration`、`warmstart_best_baseline5_model75_terrain_features/model_0.pt`，当前源码已关闭 hard terrain 质量晋级硬门槛。
  - 停止状态：训练在 `iteration 121/1000` 后被系统 OOM killer 杀死，GPU 训练进程已释放；runtime log 末尾显示 `217031 已杀死`，内核日志确认为 `Out of memory: Killed process 217031 (python)`，被杀时 Python `anon-rss` 约 `18.0 GiB`，swap 为 `0 kB`。
  - 最后确认落盘 checkpoint 为 `model_100.pt`；没有确认到 `model_125.pt` 或更后 checkpoint，因此后续回放 / 复盘优先使用 `model_100.pt`。
  - 最后 TensorBoard scalar step 为 `122`：`completed_column_rate = 0.5`、`unfinished_column_count = 5`，completed-column retention 仍在生效，已完成列仍保留约 `40.6%` active env；completed 列平均约 `7.8` 个 env，remaining 列平均约 `11.4` 个 env。
  - step `122` remaining row / adv_rate：`col05 stairs_down row = 7.72, adv = 0.281`；`col06 stairs_down row = 8.01, adv = 0.466`；`col07 stairs_down row = 7.64, adv = 0.295`；`col08 obstacles row = 8.88, adv = 0.302`；`col09 obstacles row = 1.75, adv = 0.750`。
  - 行为质量观察：全局 `stuck_timeout_rate = 0`、动作饱和仍低；但 stairs_down 三列 pitch 偏大、边缘超速接近 `1`、`row_contact_support_min` 接近 `0`，说明 row 有推进但台阶通过质量仍差。`col09 obstacles` 虽 adv_rate 不低，但 row 长期显著低于 `col08`，当前问题是课程难度没有累计抬升，而不是运动质量明显更差。
- 2026-05-11 当前主线 Stage1 `96 env / 1400 iteration` 长训已按用户要求手动结束：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-11_01-04-27_stage1_best_baseline5_m75_debug_off_metrics16_96env_1400iter`
  - 启动口径：`CompleteCar-Stage1`、headless、`cuda:0`、`96 env`、`1400 iteration`、`best_baseline5/model_75.pt` Stage1 warm-start 转换版。
  - runtime log：`RL_Training/logs/runtime/stage1_best_baseline5_m75_debug_off_metrics16_96env_1400iter_2026-05-11_01-04-14.log`
  - 监督摘要 log：`RL_Training/logs/runtime/stage1_best_baseline5_m75_96env_1400iter_monitor_2026-05-11_01-04-14.log`，训练结束后对应后台监控循环也已停止。
  - 启动验证已通过：scene creation `6.312 s`，simulation start `2.167 s`，warm-start checkpoint 正常加载，已完成 `iteration 0/1400` 和 `1/1400`。
  - 初始速度：iteration `0` 为 `17.753 s` collection + `0.385 s` learning，iteration `1` 为 `16.958 s` collection + `0.300 s` learning；终端 ETA 约 `6 h 53 min`。
  - 手动结束状态：2026-05-11 `10:27` 左右向训练进程发送 `SIGINT`，GPU 训练进程已释放；最后完整控制台打印为 `iteration 1315/1400`，但最后已确认落盘 checkpoint 是 `model_1300.pt`，因此后续可复现评估应优先使用 `model_1300.pt`。
  - 中止前观察：global `completed_column_rate = 0.5`，`unfinished_column_count = 5`，`current_level_mean = 3.7425`，`rows_advanced_mean = 1.7923`；flat retention 仍强，但 hard terrain 质量推进失败，`col05-col07 stairs_down` 基本停在 row `1`，`col08-col09 obstacles` 也没有稳定晋级。
  - 当前解释边界：这轮不是完整 `1400` iteration 结果；但到 `1300+` iteration 时 hard terrain quality-gated 晋级仍没有打开，足以作为“本轮 quality-gated hard terrain 训练方案未达到预期”的失败证据，不能继续把它解释为只差后面少量 iteration。
  - 2026-05-11 进一步复盘该 run：末段 `col05-col07 stairs_down current_level_mean = 1`，`col08 obstacles ≈ 1.36`，`col09 obstacles = 1`；hard terrain 上 `raw_hard_hit_rate` 与 `row_advance_without_quality_rate` 基本相等，说明车辆已有少量命中目标事件，但都被质量晋级 gate 拦下。用户判断应去掉 hard terrain 质量晋级机制，奖励函数中的质量相关项可以保留；下一步默认方向是将质量从“晋级硬门槛”降级为“奖励/诊断信号”。
  - 2026-05-11 已按用户确认落地：Stage1 默认 `quality_gated_terrain_advance = False`；hard terrain 命中目标后按普通逻辑升 row / completed，不再因为 `low_quality_terrain_hit` 终止 episode；`quality_row_advance_reward`、`quality_advance_score` 和 `row_advance_without_quality_rate` 继续保留，用于奖励高质量通过和观察低质量晋级比例。
  - 2026-05-11 已完成 RL 环境训练速度审计与轻量优化：确认 Stage1 长训默认未启用 IMU / 双目 / LiDAR / height scanner / debug draw / follow view / sensor raw extras；`env.py` 已复用 reward 阶段计算过的局部 height patch 给随后 observation，reset 或换 row 的 env 会局部重算，避免每步全 env 重复采样；`_get_dones()` 到 `_get_rewards()` 的相对目标命令也改为同一步复用；disabled debug draw 不再每步进入绘制函数。`4 env / 1 iteration` Stage1 headless 烟测通过，run：`2026-05-11_11-11-26_stage1_env_perf_cache_smoke`。同日进一步将 Stage1 默认 `logging.step_metrics_interval` 从 `16` 提高到 `64`，继续降低 `Stage1Eval/*` 和 step metrics 的日志同步频率。
- 2026-05-11 已完成 `128 env` 被 kill 的代码与系统层诊断：
  - 2026-05-11 追加复测：在关闭 Stage1 配置层 debug 并将 `step_metrics_interval=16` 后，重新测试 `128 env / 1 iteration`，仍在场景创建阶段被 OOM killer 杀死，未打印 `Time taken for scene creation`，未进入 PPO；内核日志显示 `Out of memory: Killed process ... (python)`，被杀时 Python anon RSS 约 `20.6 GiB`、swap 仍为 `0 kB`。
  - 因 `128 env` 已在 scene creation 阶段再次 OOM，未继续测试 `160 env` 和 `200 env`；当前仍按 `96 env` 作为本机 Stage1 长训最大可靠配置。
  - 内核日志明确显示多次 `Out of memory: Killed process ... (python)`，swap 为 `0 kB`；被杀时 Python 进程 anon RSS 约 `19.7-20.7 GiB`，因此 `112+ / 128 env` 失败是系统内存 OOM，不是 Isaac / PPO 主动报错。
  - 失败发生在 Isaac 场景创建早期，未进入 PPO iteration；主要压力来自 Stage1 多 env 克隆当前 `complete_car.usd` 机器人、PhysX/Fabric scene 和 contact-report 相关数据。
  - 已确认普通训练入口不默认启用 debug draw / follow view / video / camera：只有显式传 `--show_goal_vis`、`--show_wheel_slip_vis`、`--create_follow_views`、`--follow_all_envs` 或 `--record_terrain_chase_videos` 才打开相关可视化。
  - 代码已同步把 Stage1 配置层 debug 默认值也改为关闭，并关闭 `debug.log_sensor_outputs`，避免配置默认与训练入口覆盖逻辑不一致。
  - 已新增 `logging.step_metrics_interval`，Stage1 默认当前为 `64`，使大量 `Stage1Eval` / TensorBoard step metrics 不再每个 rollout step 都执行 `torch.mean(...).item()` CPU 同步；该改动不改变 observation、reward、termination、action 或 PPO 样本，只降低日志计算频率。此前 `96 env` 性能验证使用的是 `16`，后续新 run 按 `64` 解释。
  - 验证 run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-11_00-55-37_stage1_smoke_debug_off_metrics16_96env_1iter`，`96 env / 1 iteration` 正常完成，`collection_time = 16.990 s`、`learning_time = 0.382 s`、`steps_per_second = 2829`、训练耗时约 `26.48 s`。
  - 对比上一轮同口径 `96 env` 冒烟：`collection_time` 从 `40.198 s` 降到 `16.990 s`，说明运行时冗余日志计算是明显性能热点；但它不是 `128 env` OOM 的根因，因为 `128` 在进入 rollout 前已被内核杀死。
- 2026-05-11 已完成 Stage1 大 env 数启动上限探测：
  - 用户原计划启动 `200 env / 1000 iteration` 长训练；按要求先做启动检验。
  - `200 env / 1 iteration`、`160 env / 1 iteration`、`144 env / 1 iteration`、`128 env / 1 iteration`、`112 env / 1 iteration` 均在 Isaac 场景创建早期被系统 kill，退出码 `137`，未进入 PPO iteration；GPU 随后释放，未留下训练进程。
  - `96 env / 1 iteration` 成功完成，run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-11_00-48-08_stage1_smoke_best_baseline5_m75_96env_1iter`，启动口径为当前默认 `best_baseline5/model_75.pt` Stage1 warm-start，耗时约 `50.18 s`，第 0 轮 `collection_time = 40.198 s`、`learning_time = 0.394 s`、`steps_per_second = 1210`。
  - 本机当前推荐最大 Stage1 长训 env 数为 `96`；`112+` 在当前源码 / USD / Isaac Lab 口径下不作为可靠长训配置。
  - 本轮未启动 `200 env / 1000 iteration` 长训，因为 200 env 启动检验未通过。
- 2026-05-11 已按用户要求完成一次 Stage1 机制检验短训：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-11_00-11-15_stage1_mechanism_check_best_baseline5_m75_32env_20iter`
  - 启动口径：`CompleteCar-Stage1`、headless、`cuda:0`、`32` env、`20` iteration，使用 `--resume --warmstart --load_run warmstart_best_baseline5_model75_terrain_features --checkpoint model_0.pt`，即来源为 `best_baseline5/model_75.pt` 的 Stage1 warm-start 转换版。
  - 训练完整跑到 `19/20`，退出码 `0`，训练耗时约 `991.58 s`；已保存 `model_0.pt` 与 `model_19.pt`，TensorBoard scalar 已导出到该 run 的 `tensorboard_export/`。
  - 数值与训练机制检查：checkpoint 正常加载，PPO loss 未出现大尖峰；`Loss/03_surrogate` 全程约 `-0.024 ~ -0.007`，`action_saturation_rate` 末值约 `0.0167`，GPU 训练进程已释放。
  - curriculum / retention 检查：`completed_column_rate` 从 `0` 到 `0.1`，`unfinished_column_count` 从 `10` 到 `9`，`recycled_env_ever_rate` 到 `0.125`，`completed_column_active_rate` 到 `0.09375`，说明 completed-column retention 机制在短训中被触发并正常写出。
  - 行为指标：`current_level_mean` 从 `2.00` 到 `4.77`，`rows_advanced_mean` 末值约 `0.563`，`stagnation_rate` 末值约 `0.0277`，`stuck_timeout_rate` 仍为 `0`；flat 的 `row_advance_rate` 末值约 `0.836`，说明平地迁移能力基本保留。
  - hard terrain 机制检查：`stairs_down` 三列仍停在 row `1`，`discrete obstacles` 末值也回到 row `1`；`raw_hard_hit_rate` 与 `row_advance_without_quality_rate` 仅约 `6.1e-05`，说明 20 iteration 内几乎没有 hard terrain 命中 / 晋级事件，暂不能据此判断质量门控是否改善爬越能力。
  - 2026-05-11 已补齐 Stage1Eval TensorBoard 白名单：`hard_quality_advance_rate`、`low_quality_hit_rate`、`raw_hard_hit_rate`、`row_advance_without_quality_rate`、`quality_advance_score`、`phase_module_progress_score`、`front/middle/rear climb success`、`actual_overspeed_near_edge_rate`、`row_contact_support_min` 和 `row_stuck_time_max` 后续会按 global / flat / colXX 写入 TensorBoard；该修改只影响日志输出，不改变训练逻辑。
  - 当前短训结论：本轮验证通过的是“best_baseline5/model_75.pt warm-start + direct-target 球铰链 + retention / logger / PPO 短训链路可运行”；尚未证明 hard terrain 学习已经有效，下一步若继续机制检验，应优先做 `model_19.pt` 的指定列回放或更长但仍受控的 Stage1 短训。
- 2026-05-10 最新 Stage1 调参训练状态：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-09_16-48-52_stage1_sec14_tune_v1_128env_700iter`
  - 训练已完整跑到 `699/700`，进程退出码 `0`，训练耗时约 `29052 s`；最终 checkpoint 已保存为 `model_699.pt`，TensorBoard scalar 已重新导出到该 run 的 `tensorboard_export/`。
  - 本轮使用第 14 节七项优化后的源码口径：动态 env 回收、地形 + 相位速度限制、增强 stuck/no-progress、轻量 spin、progress quality、quality row advance 和障碍 recovery 均已启用。
  - 该 run 的动态 env 回收正常：`train_active_rate = 1.0`、`completed_column_rate = 0.5`、`unfinished_column_count = 5`、`active_envs_per_unfinished_column_mean = 25.6`；当时后期 128 env 全部集中到 `5-7 stairs_down` 和 `8-9 discrete obstacles`。
  - 2026-05-10 当前源码已修改 completed / retired 列保留机制：`curriculum.terrain_column_completed_retention_ratio = 0.40`。后续新 run 中，已完成列不会完全退出采样；回收候选会优先补足约 40% env 到 completed / retired 列低 row，剩余 env 继续按列均衡分配到未完成列。
  - step `699` 全局：`current_level_mean = 10.2160`、`rows_advanced_mean = 0.1126`、`row_advance_rate = 0.1055`、`stagnation_rate = 0.0689`、终端最终 `stuck_timeout_rate = 0.0000`、`contact_loss_rate = 0.4459`、`pitch_abs_mean = 13.6701`、`action_saturation_rate = 0.0220`、`v_forward_mean = 0.4837 m/s`。
  - 末 `25` step 全局均值：`current_level_mean = 10.2126`、`rows_advanced_mean = 0.1250`、`row_advance_rate = 0.1218`、`stagnation_rate = 0.0710`、`contact_loss_rate = 0.4501`、`pitch_abs_mean = 13.9142`、`action_saturation_rate = 0.0220`、`v_forward_mean = 0.4775 m/s`。
  - 各剩余列末 `25` step 推进：`col05 stairs_down row_advance_rate = 0.2141`、`col06 = 0.1818`、`col07 = 0.1796`；`col08 obstacles = 0.0027`、`col09 obstacles = 0.0298`。
  - 各剩余列末 `25` step level：`col05 stairs_down = 11.13`、`col06 = 11.10`、`col07 = 11.03`；`col08 obstacles = 12.00`、`col09 obstacles = 5.91`。
  - 结论：本轮运动行为质量是近期较好的一轮，低动作饱和、低 stuck timeout、低滞留和较低接触丢失保持住；推进速度仍慢，主要瓶颈已集中到离散障碍列，尤其 `col08` 已推到最高难度附近但末段几乎不再 advance，`col09` 仍停在约 row `6`。
  - 2026-05-10 已完成该 run 的结果分析包：`results/stage1_sec14_tune_v1_analysis_2026-05-10.zip`，约 `17M`，`695` 个条目，`unzip -tq` 通过；包内包含原始 TensorBoard event、`673` 个 scalar CSV、`params/env.yaml`、`params/agent.yaml`、run git diff、当前 Stage1 文档和分析报告，不包含 `.pt` / `.onnx` / `.onnx.data` 模型文件。
  - 该分析明确当前核心问题不是完全不能推进，而是低 row 学到了“速度 / 接触冲过去”的低质量通过方式；高 row 离散障碍和台阶类局部正高度突变需要相位化球铰协同，但当前 `front_pitch_ref` 与 `front_pitch_actual` 差距大、`quality_row_advance_rate` 近 `0`、模块高度推进 reward 太弱，不能支持稳定爬越。
  - 2026-05-10 已按用户确认的新方案继续修改 Stage1：`stairs_down` 和 `discrete obstacles` 的 row / level 晋级改为 quality-gated，低质量命中目标会触发 `low_quality_terrain_hit` 终止但不升 row；`step_up_module_progress_reward_weight` 从 `1.0` 提到 `10.0`，`step_up_front_posture_penalty_weight` 从 `-5.0` 提到 `-12.0`，actual overspeed 系数改为 `2.0`。新增日志包括 `hard_quality_advance_rate`、`low_quality_hit_rate`、`raw_hard_hit_rate`、`row_advance_without_quality_rate`、`quality_advance_score`、`phase_module_progress_score`、`front/middle/rear climb success` 和 `actual_overspeed_near_edge_rate`。
  - 2026-05-10 direct target + `qdot_alloc = LPF(qdot_actual)` 口径已在 2026-05-12 按用户要求恢复为当前 active 底层链路。
  - 2026-05-10 已按用户修正新增独立 MATLAB 文档 `docs/Stage1球铰PD控制MATLAB真实轨迹仿真实验方案.md`，并同步修订总方案：MATLAB 调参主线改为优先使用 IsaacLab 真实 policy 逐 control step 轨迹，人工阶跃只做 sanity check；第一版球铰 PD 增益采用统一 $K_p,K_d$，不做分关节 gain；仿真时间步按当前源码 `control.sim_dt = 1/120 s`、`control.control_dt = 1/30 s`。
  - 2026-05-10 已实现 `RL_Training/scripts/export_ball_joint_policy_trace.py` 并用 `model_699.pt` 完成一次真实轨迹导出：输出目录为 `results/stage1_ball_joint_pd_matlab/raw_traces/`，包含 combined CSV、`col00 flat`、`col05/06/07 stairs_down`、`col08/09 discrete_obstacles` 六个分列 CSV 和 summary JSON；本次导出使用 `18` env，flat 为 row `0`，stairs_down / discrete_obstacles 为 row `11`，有效非 done 样本共 `21590` 行。
  - 2026-05-10 已搭建并打开 Stage1 球铰 PD Simulink 初版模型：`scripts/matlab/stage1_ball_joint_pd/stage1_ball_joint_pd_uniform.slx`。配套脚本包括 `build_stage1_ball_joint_pd_simulink.m`、`init_stage1_ball_joint_pd_workspace.m` 和 `load_isaac_ball_joint_trace.m`；加载器支持从长表 CSV 中选择单个 `env_id`，当前已用 `col08_discrete_obstacles` 的 `env_id=4` 真实轨迹完成 `19.983 s` 仿真验证。模型已重排为顶层主控制链路 + `J1-J6` 六个关节显示子系统，每个关节内部按 `Angle rad`、`Velocity radps`、`Torque Nm` 分 Scope 显示，并支持直接打开 `.slx` 后自动初始化工作区变量。
  - 2026-05-10 已继续优化 Simulink 论文展示效果：`build_stage1_ball_joint_pd_simulink.m` 将显示子系统和内部 Scope 块放大、字体提升到论文截图更清晰的尺寸，并强制 Scope 白色背景、黑色坐标前景、legend/grid、标题和 Y 轴标签；新增 `export_stage1_ball_joint_pd_publication_figures.m`，可从同一 PD 仿真逻辑导出 `6` 张白底 `300 dpi` PNG 到 `results/stage1_ball_joint_pd_matlab/publication_figures/`，曲线采用固定高对比配色，避免直接截 Scope 时出现黑色背景。
  - 2026-05-10 已完成 MATLAB 真实轨迹统一 `Kp/Kd` 扫参：新增 `simulate_uniform_ball_joint_pd.m`、`compute_trace_metrics.m`、`plot_trace_response.m` 和 `run_real_trace_pd_sweep.m`；输出 `metrics_uniform_gain_sweep.csv` 共 `756` 行、`best_uniform_gain_candidates.csv`、`best_uniform_gain_by_case.csv` 和 `report_stage1_ball_joint_pd_matlab.md`。在固定 `J=0.10`、`B=0.5`、`tau_load=0`、`tau_v=0.05` 的第一版 plant 假设下，综合推荐统一增益为 `Kp=120, Kd=24`，可把 `Kp=160, Kd=24` 作为更激进 Isaac 短回放对照。
  - 2026-05-10 已按用户追加范围完成扩展 plant 不确定性扫参：`J=[0.03,0.05,0.08,0.10,0.15]`、`B=[0,0.5,1,2,5]`、`tau_load=[-10,-5,0,5,10]`、`tau_v=[0.03,0.04,0.05]`，共 `15750` 个参数组合、`18` 个真实轨迹 case、`283500` 条仿真评估。输出 `metrics_expanded_param_sweep_summary.csv`、`robust_expanded_control_candidates.csv`、`best_expanded_param_by_case.csv` 和 `report_stage1_ball_joint_pd_expanded_sweep.md`。结论：扩展不确定性下 `Kd=24` 的速度贴限风险上升，鲁棒跟踪主推荐改为 `Kp=120, Kd=10`；`tau_v` 不改变 PD 跟踪，只影响 `qdot_alloc` 低通，当前工程折中建议 `tau_v=0.04 s`，并用 `0.03/0.05 s` 做低滞后 / 更平滑对照。Simulink 初始化默认值已同步改为 `Kp=120, Kd=10, tau_v=0.04 s`，并在 MATLAB 中 update 验证通过。
  - 当前源码已恢复 direct-target 球铰控制链：Stage0 / Stage1 / Base 统一为 `ball_joint_stiffness=120.0`、`ball_joint_damping=10.0`、`ball_joint_effort_limit_sim=60.0`、`ball_joint_velocity_limit_sim=2.0`、`ball_joint_qdot_alloc_filter_tau_s=0.04`；`compute_low_slip_control_targets()` 直接使用 `q_target = clamp(q_desired)`，轮速分配姿态变化率使用 env 中的 `qdot_alloc = LPF(qdot_actual)`。
  - 已完成一次 `model_699.pt` 短回放信号验证：输出目录 `results/stage1_ball_joint_direct_target_replay_2026-05-10/raw_traces/`，覆盖 flat row `0`、stairs_down / discrete_obstacles row `11`，共 `3240` 行有效样本；各列 `target_gap_mean = 0.0`、`target_gap_max = 0.0`，确认 `q_desired` 已直接进入球铰 position target。短回放中 `desired_actual_mean` 约 `0.132 ~ 0.173 rad`、`qdot_alloc_abs_mean` 约 `0.478 ~ 0.638 rad/s`，说明底层 PD 仍存在实际跟踪误差，下一步应通过回放行为和必要短训判断该误差是否可接受。
  - 2026-05-10 已实现 `RL_Training/scripts/identify_ball_joint_dynamics.py`，用于脚本驱动车辆前进并激励六个球铰轴，记录 `q/qdot/qddot/computed_torque/applied_torque` 并拟合 $J/B/\tau_{\mathrm{load}}$；正式 flat drive-lift 导出位于 `results/stage1_ball_joint_identification/flat_drive_lift_18env_1800_*`，共 `32400` 行样本。当前拟合 $J$ 约 `0.03 ~ 0.08 kg*m^2`，但 $R^2$ 仅约 `0.02 ~ 0.05`，说明该行驶接触工况下单轴线性模型解释力弱；这些结果只能约束 MATLAB 扫描范围，不能作为唯一真实参数。
  - 训练后段多次出现 PPO surrogate loss 大尖峰，最大可见超过 `9000`；目前未传导成行为质量崩坏，但后续继续长训或扩大实验前需要作为优化稳定性风险单独复核。
- 当前 Stage1 后续训练默认 warm-start 已按用户要求改为 `best_baseline5/model_75.pt` 的 Stage1 转换版：
  - 默认 Stage1 warm-start：`RL_Training/logs/rsl_rl/complete_car_stage1/warmstart_best_baseline5_model75_terrain_features/model_0.pt`
  - 来源 Stage0 run：`RL_Training/logs/rsl_rl/complete_car_stage0/best_baseline5`
  - 来源 Stage0 checkpoint：`model_75.pt`
  - 已核对 checkpoint metadata：`source_iter = 75`、`target_actor_obs_dim = 82`、`target_critic_obs_dim = 660`、`ball_joint_order_fix_io = False`、`source_joint_order_assumption = current_preserve_order`。
  - 该来源是在当前 `preserve_order=True` 和 direct-target 球铰控制口径下训练得到的 Stage0 checkpoint，因此转换时只做 `54 -> 82/660` 观测维度扩展，不应用旧 `best_baseline_2` 的输入 / 输出通道重排。
  - `RL_Training/scripts/convert_stage0_to_stage1_warmstart.py` 的默认输入 / 输出已改为该口径；`CompleteCarStage1PPORunnerCfg` 的默认 `load_run/load_checkpoint` 也已改为该 warm-start。
  - 后续启动 Stage1 训练可使用 `--resume --warmstart --load_run warmstart_best_baseline5_model75_terrain_features --checkpoint model_0.pt`；若不显式传 `--load_run`，当前 Stage1 PPO 配置也会默认指向该文件。
  - `warmstart_best_baseline4_model375_terrain_features/model_0.pt`、`warmstart_best_baseline_2_terrain_features_orderfix_io/model_0.pt`、`warmstart_best_baseline3_terrain_features_orderfix_io/model_0.pt` 和 `2026-05-09_05-42-25_stage1_warmstart_best_baseline3_128env_800iter/model_375.pt` 仅作为历史对照，不作为当前默认 warm-start。
- 旧 `best_baseline_2` 来源 Stage0 使用旧 wheel allocator 几何，历史 `d1/d2/d3` 约为 `0.447 m`，当前源码为实测 `0.539 m`。此前判断它作为 Stage1 warm-start 的稳定性更好，但存在旧几何连续分布偏移；当前切换到 `best_baseline5/model_75.pt` 是用户明确选择优先使用当前 direct-target 球铰控制和 pitch gate 后的 Stage0 候选。
- 2026-05-09 `best_baseline3` 历史训练链路状态：
  - Stage0 run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-05-09_02-31-58_best_baseline3`
  - Stage0 checkpoint：`model_699.pt`，已完成 `700` iteration。
  - Stage0 启动前发现当前 Stage0 直接进入了 Stage1 terrain-column 指标路径，触发 `IndexError: too many indices for tensor of dimension 1`；已在 `env.py` 中将 terrain-column tile 指标 gated 到 Stage1 train-retirement 且 terrain generator enabled 的场景，Stage0 后续训练完成。
  - 新 Stage1 warm-start：`RL_Training/logs/rsl_rl/complete_car_stage1/warmstart_best_baseline3_terrain_features_orderfix_io/model_0.pt`，来源为 `best_baseline3/model_699.pt`；actor obs normalizer / 第一层已为 `82` 维，critic obs normalizer / 第一层已为 `660` 维，actor 输出仍为 `8` 维。
  - Stage1 run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-09_05-42-25_stage1_warmstart_best_baseline3_128env_800iter`
  - Stage1 原计划 `800` iteration；按用户后续要求已停止，GPU 训练进程当前已退出，最新 checkpoint 停在 `model_375.pt`，TensorBoard 最新 Stage1Eval 数据到 step `381`。
  - ChatGPT 无模型分析包：`results/stage1_latest_best_baseline3_chatgpt_analysis_no_models_2026-05-09.zip`，大小约 `7.8M`，`528` 个 zip 条目，`unzip -tq` 通过；包内包含原始 TensorBoard event、`503` 个非空 scalar CSV、`params/env.yaml`、`params/agent.yaml`、run git diff、Stage1 相关文档、辅助图和分析提示词，不包含 `.pt` / `.onnx` / `.onnx.data` 模型或策略文件。
  - step `381` 全局 active 指标：`train_active_rate = 0.5`、`train_retired_rate = 0.5`、`current_level_mean = 9.0910`、`rows_advanced_mean = 0.1611`、`stagnation_rate = 0.2097`、`contact_loss_rate = 0.5595`、`longitudinal_slip_abs_mean = 7.5195`、`pitch_abs_mean = 14.0340`、`action_saturation_rate = 0.1509`。
  - step `381` active terrain 结论：下台阶两列仍能少量推进，`col05/06 row_advance_rate = 0.3391 / 0.2796`，但纵滑和接触丢失偏高；上台阶两列是当前主瓶颈，`col07/08 row_advance_rate = 0`，`contact_loss_rate ≈ 0.625`，动作饱和约 `0.31`；离散障碍 `col09 row_advance_rate = 0.1890`，但卡滞、侧向比例和纵滑仍偏高。
  - 球铰表现：TensorBoard 显示球铰使用接近高限位，`Stage1Eval/global/ball_joint_limit_usage_max = 0.9269`，且 `spm1_platform_joint_y` / `front_pitch_ref` 为前车体抬高方向；但 row 推进、接触和滑移指标尚不能支持“已经学会稳定利用球铰抬高车体适应地形”的结论，只能说明策略正在使用球铰进行姿态调节尝试。
  - 该链路不再作为后续 Stage1 默认 warm-start；若后续分析它，应明确标注为 `best_baseline3` 历史对照。
- 最新 Stage1 第二次训练测试已按用户要求在 `1500` checkpoint 后停止：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-06_23-51-57_stage1_second_training_test_128env_450_to_1600_overnight`
  - 启动方式：从 `2026-05-06_21-41-43_stage1_second_training_test_128env_resume_to_700/model_450.pt` resume，`128` env，原计划补跑到 `1600` iteration。
  - 停止状态：`model_1500.pt` 已在 `2026-05-07 09:10:30` 保存；为确认保存完成后发送 `SIGINT`，GPU 训练进程已退出；TensorBoard 缓冲数据覆盖到 step `1508`。
  - TensorBoard 已导出到该 run 下 `tensorboard_export/`，共 `343` 个非空 scalar CSV 和 `3` 个汇总文件。
  - ChatGPT 无模型分析包：`results/stage1_1500_chatgpt_analysis_no_models_2026-05-07.zip`，大小约 `13M`，`467` 个条目，`unzip -tq` 通过；包内包含全部 iteration 曲线数据、参数/源码/说明文档和分析提示词，不包含任何 `.pt` 模型权重文件。
  - 1500 时关键指标：`current_level_mean = 10.1306`，`rows_advanced_mean = 1.5704`，`flat/retention_score = 0.9297`，`flat/row_advance_rate = 0.8681`，`effective_failure_rate = 0.0000`。
  - 1500 时主要瓶颈仍为台阶：`col05_stairs_down = 0.5374`、`col06_stairs_down = 0.5357`、`col07_stairs_up = 0.5432`、`col08_stairs_up = 0.5532`；动作饱和 `0.3869`、pitch `11.0940`，说明策略已能推进到 row 10 附近，但运动质量尚未充分收敛。
  - 全曲线复核结论：`450-1508` step 内 `current_level_mean` 峰值为 `10.8296`，末 `50` step 均值为 `9.7618`，说明 row 10 可反复触达但不能稳定继续上推；末段台阶上下 `difficulty_score` 约 `0.539-0.540` 且 `row_advance_rate` 近 `0`，是当前主要瓶颈。
- 当前 Stage1 已改为 `best_baseline5/model_75.pt` 转换版 warm-start 地形训练口径；上方 `best_baseline3` 只保留为历史对照链路。
- warm-start 来源：
  - Stage0 run：`RL_Training/logs/rsl_rl/complete_car_stage0/best_baseline5`
  - Stage0 checkpoint：`model_75.pt`
  - 当前低维地形特征 Stage1 warm-start checkpoint：`RL_Training/logs/rsl_rl/complete_car_stage1/warmstart_best_baseline5_model75_terrain_features/model_0.pt`
- warm-start 方式：
  - 不能直接 resume Stage0 checkpoint，因为 Stage0 actor/critic 观测维度为 `54`，当前 Stage1 actor 为 `82`、critic 为 `660`。
  - 已将 actor 第一层和 obs normalizer 从 `54` 维扩展到 `82` 维，critic 从 `54` 维扩展到 `660` 维；前 `54` 维继承 Stage0，新增低维地形特征和完整 height patch 维度初始化为零权重。
  - 训练使用 `--warmstart` 只加载 actor/critic，不加载 optimizer 和 iteration。
  - 当前推荐 warm-start 必须使用 `warmstart_best_baseline5_model75_terrain_features/model_0.pt`。该资产来自当前 `preserve_order=True` 和 direct-target 球铰控制口径下选出的 Stage0，metadata 中 `ball_joint_order_fix_io = False`；旧 `warmstart_best_baseline_2/model_0.pt` 是 `632` 维结构，不能用于新主线；旧 `warmstart_best_baseline_2_terrain_features/model_0.pt` 未修正 joint 通道顺序，不再作为默认 warm-start；`warmstart_best_baseline_2_terrain_features_orderfix_io/model_0.pt` 和 `warmstart_best_baseline4_model375_terrain_features/model_0.pt` 仅保留为历史稳定性对照。
- 当前 Stage1 观测策略：
  - actor 为 `54 + 28 = 82` 维，即 Stage0 基础观测加确定性低维地形特征 `z_terrain`。
  - critic 为 `82 + 34 * 17 = 660` 维，即 actor 观测加完整 `578` 维 height patch privileged information。
  - 前 `54` 维继承自 Stage0 的本体 / command / last action 观测，当前 active scale 与 Stage0 对齐，全部为 `1.0`。
  - `last_action` 观测已修正为当前 step 刚执行过的 policy action；reward 中的 `action_rate_penalty` 仍使用 `actions - last_actions` 表示当前动作相对上一控制步动作的变化。
  - `z_terrain` 由 `mdp/terrain_features.py` 从完整 height patch 中确定性提取，第一版固定 `28` 维；高度类 actor 特征使用 `observations.terrain_feature_height_scale_m = 0.25 m` 归一化，critic 仍额外接收原始完整 patch。
  - 完整 patch 原始量仍为 `root_z - terrain_height`；提取台阶/坑语义前先转换为相对地形高度 `H_rel = D_ref - D_patch`。
  - 2026-05-07 已完成 `1` iteration headless smoke：run `2026-05-07_16-55-38_stage1_terrain_features_smoke_1iter`，终端确认 Actor Model 第一层 `in_features=82`、Critic Model 第一层 `in_features=660`，TensorBoard 已出现 `TerrainFeature/*` 和 `TerrainGate/*`。
- 当前低维地形特征 Stage1 正式测试 run 已按用户要求在 `525` checkpoint 后停止：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-07_17-14-44_stage1_terrain_features_actor82_critic660_warmstart_700iter_restart`
  - 启动方式：`128` env、headless、从 `warmstart_best_baseline_2_terrain_features/model_0.pt` warm-start，计划 `700` iteration。注意：这是 `2026-05-07` 历史 run 的实际口径；当前后续训练默认已改用 `warmstart_best_baseline5_model75_terrain_features/model_0.pt`。
  - 停止状态：`model_525.pt` 已在 `2026-05-07 22:13:08` 保存；用户要求 `525` 时停止，因终端刷新滞后，事件文件最后写到 step `527`，随后发送 `SIGINT`，GPU 训练进程已退出。
  - step `525` 关键指标：`current_level_mean = 9.2296`，`rows_advanced_mean = 1.5870`，`flat/row_advance_rate = 0.9345`，`contact_loss_rate = 0.6582`，`pitch_abs_mean = 9.3597`，`action_saturation_rate = 0.3085`。
  - step `525` 地形瓶颈：`col05_stairs_down = 0.5061`、`col06_stairs_down = 0.5205`、`col07_stairs_up = 0.5342`、`col08_stairs_up = 0.5510`；step `527` 仍为台阶和离散障碍偏难，`col09_obstacles = 0.4839`。
  - 阶段判断：低维地形特征 run 已反复到达 row `9` 附近，平地能力保留较好；但 `contact_loss_rate` 约 `0.66`、纵向滑移约 `4.6`、低滑移通过率仍低，台阶 difficulty 未降出瓶颈区，不能判断为收敛。
  - ChatGPT 分析包：`results/stage1_525_terrain_features_chatgpt_analysis_2026-05-07.zip`，约 `6.9M`，`390` 个条目，`unzip -tq` 通过；包内包含 TensorBoard 原始 event、`371` 个非空 scalar 的 CSV 导出、`params/env.yaml`、`params/agent.yaml`、run git diff、Stage1 参数/指标/奖励/优化方案文档和分析提示词，不包含 `.pt` / `.onnx` 权重或策略文件。
- 当前 Stage1 参数详情表：`docs/Stage1参数详情表.md`。
- `docs/Stage1参数详情表.md` 已按当前 Stage1 源码配置重新同步，区分了源码默认值、训练命令覆盖值和历史 run 参数快照；2026-05-08 已补充第 `9.3` / `9.4` 节，详细记录 `28` 维低维地形特征和 `g_step_up`、`g_step_down`、`g_gap`、`g_rough`、`g_flat` 的计算方式；2026-05-09 已同步第 `14` 节七项优化落地后的当前口径，并明确标出地形 + 相位速度、stuck/no-progress、spin penalty、progress quality、模块爬升、quality row advance 和 recovery 的新增 / 修改内容。
- 当前 Stage1 局部 height patch 工程示意图：`results/stage1_patch_layout.png`；生成脚本为 `scripts/isaac_sim/draw_stage1_patch_layout.py`，按当前 patch 范围、`+Y` 为车体左侧、left/right track 竖向条带、front/middle/rear support 前后分区绘制；新版仿照参考图配色与排版，并在下方独立 legend 栏说明各区域含义；`center_track` 已用高对比黄色竖向带和橙色边界线突出显示；车辆几何已改为用户给定实测尺寸：总长 `1.884419 m`、总宽 `0.560747 m`、前/中/后轴 x 为 `+0.552977 / 0 / -0.552977 m`，轮中心 y 约为 `±0.2695 m`。
- 当前 Stage1 地形特征分布图：`results/stage1_terrain_feature_distributions.png`；生成脚本为 `scripts/isaac_sim/plot_stage1_terrain_feature_distributions.py`，直接采样 Stage1 地形生成器的 `flat / uneven rough / stairs up+down / discrete obstacles` 四组地形，输出样本 CSV `results/stage1_terrain_feature_distribution_samples.csv` 和汇总 CSV `results/stage1_terrain_feature_distribution_summary.csv`。该图仍可作为地形特征函数参考，但当前实际训练列已不再采样 `stairs up`。2026-05-12 已按用户要求将 `g_step_up` 激活中心阈值从 `0.08 m` 降到 `0.05 m`；这会让正高度突变更早激活，但也可能增加 rough 小起伏的 step-up 响应，需在后续训练 / 回放中观察误触发。
- 当前 Stage1 terrain gate 函数曲线图：`results/stage1_terrain_gate_functions.png`；生成脚本为 `scripts/isaac_sim/plot_stage1_gate_functions.py`，按 `mdp/terrain_features.py` 中当前公式绘制 `g_step_up/g_step_down`、`g_gap`、`g_rough` 和 `g_flat` 的输入-输出关系；物理量横坐标统一使用 m，`g_flat` 因输入是 gate 总和而保留无量纲横坐标。当前 `g_step_up` 中心阈值为 `0.05 m`，`g_step_down` 中心阈值仍为 `0.08 m`。
- 当前 Stage1 奖励函数后续设计草案：`docs/Stage1奖励函数设计草案.md`；该文档已补充当前源码实际 reward 公式对照和拟采用 reward 公式设计。当前已将动作变化惩罚、接触权重 mask slip、模块支撑惩罚和地形突变前速度惩罚写入源码，其余拟采用项尚未写入源码；设计边界仍是保留局部高程图输入，不加入双目/LiDAR 原始感知、球铰极限惩罚和非轮体碰撞惩罚。
- 当前 Stage1 第二阶段优化方案已写入 `docs/优化方案.md` 的第 `13` 节：下一轮不再扩大 actor 观测，而是基于现有 `TerrainGate/*` 落地 terrain-gated 速度硬限幅、gate-aware contact support、stuck penalty/reset、台阶姿态 / 下台阶 anti-dive 和新增 TensorBoard 诊断。用户已确认执行口径：`spm1_platform_joint_y > 0` 表示前车体低头，`spm2_platform_joint_y > 0` 表示后车体抬头；不建立独立 `Stage1b` 专训；stuck timeout 触发后直接退级；球铰软限位第一版只日志不进 reward；A1 速度硬限幅和 A2 gate-aware contact support 合并为同一次训练改动。
- 2026-05-08 已完成 Stage1 第 `13` 节落地后的 R1-R20 短训复盘；当前结论仍是 R1-R20 未解决台阶类地形的推进质量，R20 主要增加推进压力但纵滑、接触丢失和俯仰偏高，不适合按旧配置直接做 `700+` 长训。复盘文档为 `results/stage1_reward_experiments/Stage1_R1-R20训练修改与结果汇总_2026-05-08.md`。
- 2026-05-09 最新 Stage1 结果分析后的优化方案已写入 `docs/优化方案.md` 第 `14` 节，且用户已要求按第 `14` 节七项建议全部落地。当前源码已完成：`stuck_speed_threshold_mps = 0.10`、`stuck_penalty_grace_s = 0.5 s`、`stuck_timeout_s = 4.0 s`、`no_progress_penalty_weight = -1.0`、相位速度 `0.45/0.75/0.35/0.40 m/s`、`airborne_spin_penalty_weight = -1.0`、`hard_terrain_spin_penalty_weight = -1.0`、`step_up_module_progress_reward_weight = 10.0`、`quality_row_advance_reward_weight = 1.0` 和离散障碍 recovery。2026-05-11 已关闭 quality-gated hard terrain advance，质量指标保留为 reward / diagnostics。2026-05-13 当前 hard terrain 质量口径进一步改为 `step_up_progress_quality_min_multiplier = 0.2`、drop guard latch、rear-follow reward / penalty、`quality_gate_score` / `motion_quality_score` 拆分和 root roll `35 deg` 终止。评价上不能单看 `difficulty_score`，必须同时看 row 推进、stagnation、stuck、滑移、姿态、接触、动作饱和、drop guard、rear follow 和 quality score 日志。
- 当前底层轮速分配几何已按用户给定轮距修正：`wheel_speed_allocator.py` 中前 / 中 / 后三轴左右轮距 `d1/d2/d3` 统一为 `0.539 m`，不再使用旧的 `0.447 m`。该参数会影响轮心位置、横摆分配、轮速参考和低滑移控制链路。
- 当前 Stage1 TensorBoard / 终端日志指标说明文档：`docs/stage1评价指标.md`；该文档基于当前 logger、env 和 train 源码整理指标含义，并明确当前本地缺少 Stage1 event/runtime log，未伪造具体曲线数值。
- 当前 Stage1 日志系统已重构为 stage-specific：Stage0 仍使用原 TensorBoard 白名单和终端 `CONSOLE_PRIORITY_TAGS`；Stage1 终端只打印 `Stage1Eval/*` 高信号评价指标，不再把固定为 `0` 的 `Termination/success_rate` 作为主指标。
- Stage1 新增 `Stage1Eval/global`、`Stage1Eval/flat` 和 `Stage1Eval/col00-col09` 指标，用于观察 flat retention、terrain column 通过能力、max-row reached、valid-target masked、滑移、接触、姿态、动作饱和与最难地形列。
- Stage1 PerWheel TensorBoard 调试默认关闭：`logging.enable_stage1_per_wheel_debug = False`；打开后只写法向力、纵滑、侧滑角、轮地纵/侧向速度、轮端力矩目标和轮速参考。
- `scripts/train.py` 训练默认不再开启可视化 debug draw：普通 headless 训练不会显示目标 marker、目标方向或轮滑箭头；需要训练时看目标 marker 时显式加 `--show_goal_vis`，需要轮滑箭头时显式加 `--show_wheel_slip_vis`。`--record_terrain_chase_videos` / `--follow_all_envs` 只为相机跟踪启用 debug draw，不会自动打开目标 marker 或轮滑箭头。
- 2026-05-09 Stage1 训练耗时审计结论：当前慢主要不是由未接线参数本身造成，而是 rollout/env step。`best_baseline3` Stage0 末次 `collection_time ≈ 13.62 s/iter`、`learning_time ≈ 0.30 s/iter`；对应 Stage1 128 env run 末次 `collection_time ≈ 30.98 s/iter`、`learning_time ≈ 0.30 s/iter`。Stage1 每 iteration 样本数为 `128 * 512 = 65536`，是 Stage0 常用 `64 * 512` 的两倍；此外 Stage1 每步还计算 `578` 维 height patch、`28` 维 terrain feature、terrain-column 指标、轮地接触和大量 step metrics。
- 2026-05-09 已完成 Stage1 轻量清理：`env.py` 增加单 control step 轮地接触力缓存，按 `pre_physics` / `post_physics` 分相位复用并在 reset 时清空；`compute_reward_terms()` 对当前权重为 `0` 的旧 `edge_speed_penalty`、`airborne_spin_penalty`、`hard_terrain_spin_penalty`、`action_soft_limit_penalty` 跳过原始项计算；Stage1 默认 `terrain_dict` 只保留当前实际采样的 `flat / slope down / slope up / uneven rough / stairs down / discrete obstacles`。
- Stage1 后续更大的工程热点仍是 `env.step()` 每步收集 `extras["metrics"]`：其中包含大量 `torch.mean(...).item()` CPU 同步和 `Stage1Eval` 分列统计。若还要继续加速，应优先做训练轻量日志模式或 Stage1Eval 降频/按 iteration 统计；`noise.enabled=False`、IMU/相机/LiDAR/height_scanner disabled 对每步训练无实质开销。
- 当前 CompleteCar 训练链路已补充 NaN/Inf 数值安全保护：policy action mean / std / log_std 在进入 `Normal` 前清理并保证 `std > 0`，obs / reward / extras metrics 写入前执行 `nan_to_num`，Stage1Eval 的 retention / difficulty 空 mask 返回 `0`。
- 已修复 Stage1 iteration `31` 暴露出的分布参数原地修改问题：`SquashedGaussianDistribution` 现在先在 `no_grad` 下清理 `log_std_param`，再让清理后的参数参与当前 autograd graph，避免 backward 报 `modified by an inplace operation`。
- PPO update 主流程已加入有限值保护：batch / loss / gradient / 参数更新前后都会检查 finite 状态；异常 mini-batch 会跳过，异常 optimizer step 会恢复更新前参数并清空 optimizer state，避免一次 `inf` surrogate loss 污染整条训练链。
- 当前 `complete_car_stage1_cfg.py` 已改为 Stage1 相关参数显式配置风格，后续 Stage1 参数优先在该文件中统一修改。
- 当前新启动的 Stage1 run 使用与 Stage0 相同的底盘动作物理速度输出范围：
  - `a0 -> vx_cmd` 映射为 `[-2.0, 2.0] m/s`，允许倒车。
  - `a1 -> yaw_rate_cmd` 映射为 `[-2.0, 2.0] rad/s`。
- 当前 Stage1 训练地形列映射：
  - `0: flat`
  - `1: slope down`
  - `2: slope up`
  - `3-4: uneven rough`
  - `5-7: stairs down`
  - `8-9: discrete obstacles`
  - 即当前 10 个训练列不再采样 `stairs up`，第 `7` 列改为 `stairs down`，第 `8` 列改为 `discrete obstacles`。
- 当前 Stage1 初始出生 / 训练列分配：
  - 初始化时 env 按 id 均匀分配到 `0-9` 全部地形列。
  - 初始 row 已按地形限制：`stairs down` 固定为 `1`，`discrete obstacles` 为 `1-2`，`flat` / `slope` / `rough` 保持 `0-5`。
  - episode 内 terrain-column 目标推进只增加 row，不改变 column，因此全地形训练依赖初始化时覆盖所有 column。
  - 当前已启用 completed-env recycling + completed-column retention：每列累计完成次数达到初始化时该列 env 配额后才视为该列完成；完成 env 在 reset 时先补足约 40% active env 到 completed / retired 列低 row，剩余回收 env 再按 active env 数均衡回收到剩余未完成列。若后期只剩 `5-7 stairs down` 和 `8-9 discrete obstacles`，未完成列内部仍按列均分，对应地形比例约为 `3:2`。
- 当前 Stage1 回放列选择：
  - `scripts/play.py` 新增 `--terrain_replay_columns`，默认 `all`。
  - `all` 表示按 env id 轮转分配到 `0-9` 全部地形列，要求 `--num_envs >= 10`。
  - 可指定单列编号，如 `--terrain_replay_columns 7`，使所有 env 出生在该地形列。
  - 可指定列编号列表，如 `--terrain_replay_columns 5,6`，也可指定地形名，如 `flat`、`slope_up`、`stairs_down`、`discrete_obstacles`；重复地形名会映射到对应多列。
  - 2026-05-11 已修复指定地形名回放后首次 reset 被 completed-env recycling 改回其他列的问题：`play.py` 现在会在设置 `terrain_types` 后重新采样合法初始 row、重建 Stage1 列完成目标，并清空 recycling / retired 状态；例如 `--num_envs 4 --terrain_replay_columns slope_down` 会将 4 个 env 全部锁定为 `col01 slope_down`。
  - 2026-05-11 已将回放 debug 可视化改为显式开启口径：目标 marker 默认关闭，需要时传 `--show_goal_vis`；目标方向箭头需要额外传 `--show_goal_heading`；局部高度图红色 `/Visuals/HeightPatch/positive_y_axis` 默认关闭，需要时传 `--show_height_patch_axis`。
  - 2026-05-11 已扩展 `--create_follow_views` 相机：每个被跟踪 env 会创建 `/view/env_N/top_down_camera`、右后方 `/view/env_N/chase_camera`、左后方对称 `/view/env_N/left_chase_camera`、前向 `/view/env_N/forward_camera` 和右侧正对 `/view/env_N/right_side_camera`；前向相机位于中车体 articulation root 上方 `3 m`，看向车体 `+X` 正前方；右侧相机位于中车体 root 右侧 `3.5 m`、向上 `1.0 m`，看向中车体质心。
  - 2026-05-11 `scripts/play.py` 已支持 `--record_camera_view {chase,left_chase,forward,right_side,top_down}` 单视角录制，也支持 `--record_camera_views chase,right_side` 多视角并行录制；配合 `--record_chase_view --stream_video` 可在 GUI 开启时为每个 follow camera 各自创建 render product 并写入独立 mp4，文件名会自动追加视角后缀；可用 `--video_resolution WIDTHxHEIGHT`、`--video_crf`、`--video_preset` 控制录制分辨率与 x264 质量；`--video_length` 默认 `0` 表示不限时录制，关闭 GUI 或中断进程时停止并封装视频。
  - 2026-05-11 已修复 headless 多视角 follow-view 录制的空帧假成功问题：旧逻辑只按循环步数打印 `Streamed N/M`，但 follow camera render product 没有显式 `sim.render()` 刷新，导致本次 `model725_col05_dual_2k_goal_patch_20min_*.mp4` 跑到 `72000/72000` 后未落盘。`play.py` 现在会在读取 follow camera annotator 前显式 `raw_env.sim.render()`，并且只有所有请求视角真实写帧后才计数，连续空帧会报错。120 帧双视角 smoke 已通过：`model725_col05_dual_2k_goal_patch_smoke_render120_chase.mp4` 与 `..._right_side.mp4` 均为 `2560x1440`、`60 fps`、`120` 帧、`2.0 s`。
  - 2026-05-09 已修复 warm-start checkpoint 回放加载：`scripts/play.py` 会自动识别缺少 `optimizer_state_dict`、但包含 `actor_state_dict` / `critic_state_dict` 的 warm-start 文件，并按 actor/critic-only 方式加载；因此可直接回放当前 `warmstart_best_baseline5_model75_terrain_features/model_0.pt`，旧 `warmstart_best_baseline4_model375_terrain_features/model_0.pt` 和 `warmstart_best_baseline_2_terrain_features_orderfix_io/model_0.pt` 也可作为历史对照回放。
  - `scripts/play.py` 新增 `--replay_episode_length_s`，只覆盖回放 episode 时长，用于观察策略在超过训练 timeout 后是否仍能到达 terrain-column 目标；该参数不改变已训练模型权重，也不应与训练 TensorBoard reward 曲线直接混作同一口径。
  - `scripts/play.py` 新增 `--show_height_patch_vis`，可在 Isaac Sim 视口显示指定 env 的局部高度图 patch 采样点；采样点位置使用当前 policy 实际高度 patch 的世界坐标，颜色以 patch 平均地形高度为中心，低处偏蓝、高处偏红。
  - `scripts/play.py` 的高度 patch 可视化支持红色局部 `+Y` 半区箭头；2026-05-07 回放确认该 `+Y` 箭头位于车体左侧，因此后续低维地形特征中 `left_track` 固定使用 `y > 0`，`right_track` 固定使用 `y < 0`，`left_right_height_diff > 0` 表示左侧轮路径更高。
  - 2026-05-09 已将 `debug_draw.py` 中目标方向、轮速方向和高度 patch `+Y` 指示从 IsaacLab 远程 `arrow_x.usd` marker 改为本地 primitive cylinder marker，避免离线回放时因无法访问 Omniverse 远程 USD 而在创建 marker 阶段崩溃；目标红色 sphere marker 保持不变。
  - `scripts/isaac_sim/control_keyboard.py` 新增 `--show-height-patch-vis`，键盘手动控制时也可按 Stage1 当前 patch 定义显示 `34 * 17 = 578` 个局部高度采样点；`--terrain stage1` 时采样点高度来自同一 Stage1 heightfield，平面模式下显示在 `z=0` 附近。Stage1 地形模式建议用 `/home/ubuntu/IsaacLab/isaaclab.sh -p scripts/isaac_sim/control_keyboard.py ...` 启动。
  - `scripts/play.py` 已修正 checkpoint 解析：`--checkpoint model_699.pt` 这类裸文件名会结合 `--load_run` 在 run 目录下查找；绝对路径、带目录的相对路径或 URI 仍按显式路径读取。
- 为避免 terrain-column target 与自由 waypoint 采样语义混淆，Stage1 cfg 不再显式写入 `commands.goal_distance` / `commands.goal_direction_max_deg`；其 reward 名义距离尺度改由 `rewards.params.nominal_goal_distance_m = 8.0` 表达。
- 当前 Stage1 `reached_target` 奖励已启用，参数与 Stage0 相同：`reached_target_base_reward = 2.0`、`reached_target_weight = 6.0`。
- 当前 Stage1 `slip_penalty` 使用纵滑率系数 `5.0` 和侧滑角系数 `1.0`，总权重仍为 `slip_penalty_weight = -2.0`；该项已复用底层接触权重做 masked mean，只主要惩罚有效接地轮滑移，并用 `max(sum(c_i), 1.0)` 作为保护分母。
- 当前 `action_rate_penalty` 已在 Stage0 / Stage1 启用，用最大 episode 步数 `N = 1200` 归一化；Stage1 为 `weight = -10.0`、底盘动作权重 `0.5`、球铰姿态动作权重 `1.0`；Stage0 为 `weight = -50.0`、底盘动作权重 `0.2`、球铰姿态动作权重 `1.0`。
- 2026-05-10 已启动新一轮 Stage0 训练 `2026-05-10_18-21-11_stage0_slip2_actionrate_m50_qmon_700iter`，当前配置为 `action_rate_penalty_weight = -50.0`、`slip_longitudinal_penalty_ratio = 2.0`、`slip_angle_penalty_ratio = 1.0`。本轮重点监控四项：`Action/ball_joint_desired_delta_abs_mean_raw`、`Observation/ball_joint_vel_limit_rate_raw`、`Observation/ball_joint_target_error_abs_mean_raw` 和 waypoint 完成率 / success rate。早期 iteration `2-4` 可见新增指标正常写出：`q_desired` 每步跳变约 `0.138 rad`、`qdot` 贴限比例约 `3.6%`、tracking error 约 `0.104 rad`、waypoint 完成率暂为 `0%`。
- 当前 Stage1 `contact_support_penalty` 已切换为 terrain-gated 模块支撑惩罚；`contact_support_penalty_weight = -20.0`，`contact_support_min_weight = 0.3`，`contact_support_lr_balance_ratio = 0.15`。该项不强制六轮同时接地，而是按 `flat/rough`、`step_up`、`step_down/gap` gate 调整前 / 中 / 后模块支撑要求。
- 当前 Stage1 旧 `edge_speed_penalty` 权重为 `0.0`，实际启用的是 `terrain_aware_edge_speed_penalty_weight = -20.0` 和控制链路中的 terrain-gated 正向速度硬限幅；当前安全速度已改为地形 + 相位字段：step-up approach `0.45 m/s`、step-up climb `0.75 m/s`、step-down `0.35 m/s`、obstacle/gap approach `0.40 m/s`，`terrain_speed_limit_mps = 0.50 m/s` 仅作为 fallback。该限幅只约束正向 `vx_cmd`，倒车分支仍保留。
- 当前 Stage1 目标点逻辑：
  - 使用 terrain column / terrain type 生成目标点。
  - 目标方向沿地形列纵向 `+x`。
  - 目标列保持同列，目标行固定偏移 `1` 行；除 `stairs down`、`discrete obstacles` 外，目标点 `y` 方向允许左右随机偏移 `3 m`。
  - `stairs down`、`discrete obstacles` 的目标 x / y 直接使用下一行同列 tile origin，不做横向偏移。
  - 目标采样不再允许超过最大 row 后夹紧到同一最后 row；若推进会进入没有合法下一目标的最高 row 区域，则本段记为 `terrain_column_completed` 并作为终止结束，reset 时不再回到低 row 重新采样。
  - 触发 `terrain_column_completed` 的完成 transition 仍写入一次训练；reset 后该 env 优先用于维持 completed / retired 列约 40% 低 row 保留采样，达到保留配额后再回收到剩余未完成列并保持 `train_mask=True`；只有没有未完成列时才 inactive / `train_mask=False`。若所有 terrain column 都完成，runner 在当前 rollout/update 后停止训练并保存模型。
  - step 类地形初始 / reset 最小 row 已改为 `1`：`stairs down` 固定从 row `1` 起，`discrete obstacles` 从 row `1-2` 采样；失败退级也不会低于该地形最小 row。
  - `discrete obstacles` 已归入 `step` terrain class；`stairs down`、`discrete obstacles` reset 时 xy 直接使用当前 tile origin，spawn z 由该 origin 点 heightfield 高度加 `0.30 m` 得到，不再使用 tile start 前 `0.3-0.8 m` 的 approach spawn。
  - terrain-column 目标不使用 `commands.resampling_time` 的计时重采样；row 升级只由目标点命中触发，不再使用相对当前 `tile_start_x` 前进超过 `5.6 m` 的距离捷径。
  - terrain-column reset 时按当前目标段进度判断 row 退级：若 episode 失败/超时、未命中目标且当前段进度 `< 0.30`，则当前 row 退一级；若已推进至少 `30%`，则保持当前 row 继续练习。
  - 目标命中不会触发 Stage1 success termination，但会贡献 `reached_target` 稀疏奖励并触发 row / target 推进。
  - reset 朝向固定为 `+x`。
  - 训练地形颜色已改为黑色 `(0.0, 0.0, 0.0)`。
  - 当前 episode 时长为 `40.0 s`，场景级 PhysX `max_velocity_iteration_count = 4`，机器人 articulation root `solver_velocity_iteration_count = 4`。
- 当前最新 Stage1 完整训练：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-03_02-17-59_stage1_resume_from125_ppo_guard_to700`
  - 启动方式：从 `2026-05-03_01-17-07_stage1_resume_from25_fixed_distribution_to700/model_125.pt` resume，`32` env、headless、目标补足到 `700` iterations。
  - 训练结果：终端输出到 `699/700`，进程退出码 `0`，训练耗时约 `15492.84 s`，最终 checkpoint 为 `model_699.pt`。
  - 输出文件：同一 run 目录下已保存 TensorBoard event 文件、`model_125.pt` 到 `model_699.pt` 的间隔 checkpoint、`params/` 和 `git/` 快照；已导出 `308` 个非空 TensorBoard scalar tag 到 `tensorboard_export/`。
  - 数值稳定结论：未复现 iteration `31` 的 in-place autograd crash，也未出现会终止训练的 NaN/Inf distribution 错误。
  - 策略效果边界：训练链路已跑通，但末段仍未学出可靠全地形前进；最后可见 `Stage1Eval/flat/row_advance_rate = 0.0000`、`Stage1Eval/global/rows_advanced_mean = 0.0087`、`Stage1Eval/global/longitudinal_slip_abs_mean = 5.8542`、`Stage1Eval/global/contact_loss_rate = 0.5531`、`Stage1Eval/global/pitch_abs_mean = 10.5290`。
  - Flat 全过程复核：`Stage1Eval/flat` 不能只看最后 50 iteration。三段有效 Stage1 训练链路中，flat 在每次从低 row 重新开始后约 `9` 个 PPO iteration 内达到 `current_level_mean = 19`；到达最后 row 前，`row_advance_rate` 均值约 `0.75-0.85`，`v_forward_mean` 约 `1.9-2.1 m/s`，`retention_score` 约 `0.85-0.89`，说明 Stage0 平地前进技能基本保留。最后 row 后的 `row_advance_rate = 0` 主要受 terrain level 饱和和目标推进语义影响，不能单独解释为平地技能丢失。
  - TensorBoard 全量数据包：`results/stage1_tensorboard_all_iterations_2026-05-03.tar.gz` / `.zip`，包含当前 `complete_car_stage1` 下 `11` 个 run 的原始 event 文件、全部 scalar CSV/JSON 导出，以及有效训练链路 `0-699` 的 long/wide 合并表。
  - ChatGPT 高效分析精简包：`results/stage1_tensorboard_chatgpt_essential_0_699_2026-05-03.zip`，只保留 `0-699` 全 iteration 结果分析必要的核心 CSV、地形列长表、摘要表和分析提示；压缩包约 `1.5M`，内部 `10` 个实际文件。
  - 工程判断：当前优先问题已从“训练会崩溃”转为“Stage1 reward / curriculum / 目标推进语义下 policy 未形成稳定全地形通过能力”。
- 历史可视化训练：
  - GUI run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-04-28_18-17-55_stage1_warmstart_best_baseline_2_32env_view_700iter`
  - 已按用户要求停止，终端最后完整输出到 PPO iteration `18/700`。
  - 该 run 当前只看到 `model_0.pt`，没有跑到默认保存间隔产生后续 checkpoint。
- 当前 Git 上传规则：
  - Stage1 当前模型、checkpoint、TensorBoard event、run diff、输出目录默认不上传 GitHub。
  - `.gitignore` 已显式忽略 `RL_Training/logs/`、`RL_Training/outputs/`、`results/*.zip`、`results/*.tar.gz`、`results/Videos/`、`results/stage1_*_analysis*/`、`results/stage1_tensorboard_*/` 和 `results/stage1_reward_experiments/`。
  - 2026-05-08 已按用户明确要求将 `results/Videos/` 下 `6` 个 replay MP4 通过 Git LFS 上传到 GitHub；`.gitattributes` 跟踪规则为 `results/Videos/*.mp4 filter=lfs diff=lfs merge=lfs -text`。
  - 只有当用户明确要求上传某一次 Stage1 训练结果时，才使用 `git add -f` 纳入对应 run。

## 当前 active Stage0 基准

- 当前最新实际完成的 Stage0 run 为继续训练后的 `best_baseline4`：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-05-09_14-22-59_best_baseline4`
  - 启动口径：从 `2026-05-09_12-12-50_best_baseline4/model_225.pt` resume，`CompleteCar-Stage0`、headless、`cuda:0`、`64` env，继续训练到总 `699/700` iteration。
  - checkpoint：已保存 `model_250.pt` 到 `model_699.pt`；最终 checkpoint 为 `model_699.pt`。
  - 训练状态：进程退出码 `0`，训练耗时约 `7184 s`，TensorBoard scalar 已导出到该 run 的 `tensorboard_export/`。
- 2026-05-09 继续训练后的 `best_baseline4` 与 `best_baseline_2/model_699.pt` 对比结论：
  - 对比口径为 checkpoint 对应的末 `25` iteration 窗口；`best_baseline_2` 使用 `675-699`，`best_baseline4/model_699.pt` 使用 `675-699`。
  - `best_baseline_2/model_699.pt`：`success_rate = 1.0000`，平均 episode length 约 `669.1` step，`v_parallel_abs` 约 `1.1821 m/s`，wheel speed reference 约 `8.732 rad/s`，`LowSlip/combined_pass_rate` 约 `0.0886`，`pitch_deg` 约 `-0.573`，`projected_gravity_xy_norm` 约 `0.0175`。
  - `best_baseline4/model_699.pt`：`success_rate = 1.0000`，平均 episode length 约 `619.9` step，`v_parallel_abs` 约 `1.2507 m/s`，wheel speed reference 约 `9.158 rad/s`，`LowSlip/combined_pass_rate` 约 `0.0755`，`pitch_deg` 约 `-4.124`，`projected_gravity_xy_norm` 约 `0.0723`。
  - 结论：`best_baseline4` 继续训练后速度和完成效率已明显超过 `best_baseline_2`，但低滑移通过率更差，车体姿态明显更前倾；姿态差异主要来自 pitch，roll 差异很小。
  - 在 `best_baseline4` 内部，速度 / episode length 最优候选是 `model_675.pt` 或 `model_699.pt`；若把车体姿态纳入综合运动质量，`model_600.pt` 更平衡；若只看低滑移通过率，`model_375.pt` 最好；但没有任何 `best_baseline4` checkpoint 在车体姿态上接近 `best_baseline_2`。
  - 2026-05-09 重新按“任务推进优先、兼顾低滑移和车体姿态”的统一窗口评分后，`best_baseline4` 内部当前推荐综合 checkpoint 改为 `model_375.pt`：末 `25` iteration `success_rate = 1.0000`、平均 episode length 约 `651.7` step、`v_parallel_abs` 约 `1.192 m/s`、`LowSlip/combined_pass_rate` 约 `0.0809`、`pitch_abs` 约 `2.77 deg`、`projected_gravity_xy_norm` 约 `0.0493`。它不是最快，但相比 `model_600/675/699` 姿态和低滑移更稳，任务推进已达到可用水平。
  - 2026-05-09 对 `best_baseline4/model_375.pt` 与 `best_baseline_2/model_699.pt` 做同窗口复核后，曾建议 Stage1 默认 warm-start 保持 `best_baseline_2` 修正版 orderfix 文件：两者成功率均为 `1.0`，`model_375.pt` episode length 和速度略优，但 `best_baseline_2` 的低滑移通过率更高、pitch 和 `projected_gravity_xy_norm` 明显更好。
  - 2026-05-10 用户曾要求将 Stage1 warm-start 改为 `best_baseline4/model_375.pt`；随后用户进一步要求将本轮 Stage0 pitch gate 训练重命名为 `best_baseline5`，并将 `model_75.pt` 作为 Stage1 warm-start。当前默认已切换为 `warmstart_best_baseline5_model75_terrain_features/model_0.pt`。
  - 2026-05-10 已按当前 direct-target 球铰 PD 口径回放 `best_baseline4/model_375.pt`：GUI 回放开启追踪视角和目标点 marker，日志保存在 `results/stage0_model375_gui_replay_2026-05-10/gui_play.log`；同步导出逐 step trace 到 `results/stage0_model375_gui_replay_2026-05-10/raw_trace/`，共 `4794` 行有效 flat 样本，并保存统计摘要 `contact_replay_summary.txt`。
  - 本次 Stage0 375 回放统计摘要：`active_segment_completion_pct_tail = 67.39%`、`pitch_deg_mean = 0.58`、`roll_deg_mean = 0.49`、`ball_joint_target_error_abs_mean = 0.1525 rad`、`ball_joint_vel_abs_mean = 0.8301 rad/s`、`v_parallel_abs_mean = 1.0149 m/s`、`v_perp_abs_mean = 0.0818 m/s`。该结果用于后续反馈当前底层 PD 改动后旧 Stage0 policy 的实际表现。
  - 进一步分析确认 GUI 看到的抖动与数据一致：球铰 `q_desired` 每 control step 绝对变化均值 `0.138 rad`、p95 `0.412 rad`，相当于目标变化率远超当前 `2 rad/s` 球铰速度上限；实际 `qdot` p95 已达 `1.986 rad/s`，约 `11.6%` 样本超过 `1.8 rad/s`。因此当前问题优先解释为旧 policy 输出的球铰目标高频跳变在 direct-target 链路下暴露出来，而不是单纯 `Kp/Kd` 过小。
  - 包含 done 行的补充 trace 位于 `results/stage0_model375_gui_replay_2026-05-10/raw_trace_include_done/`。该次 20 s 回放中 `env0` 未完成 episode，其余 env 有 `1-2` 次 done；但当前 exporter 的 `done_reason` 仍为空，后续若要严谨定位目标捕获失败，应补充导出 `active_waypoint_index`、`waypoints_completed`、`active_waypoint_pos_error` 和 per-env completion。
- 早停历史 `best_baseline4`：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-05-09_12-12-50_best_baseline4`
  - checkpoint：`model_225.pt`
  - 状态：曾按用户要求在稳定成功率平台期后停止；当前已作为继续训练的 resume 起点，不再视为最新 Stage0 候选。
- 上一轮 `best_baseline3`：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-05-09_02-31-58_best_baseline3`
  - checkpoint：`model_699.pt`
  - 训练结果：完成 `700` iteration；末段 success 为 `1.0`，但低滑移通过率仍低、纵滑偏高，因此仅作为当前工程修正版 Stage0 baseline 的历史对照。
- 当前 Stage0 文档目标仍以 `best_baseline` / `best_baseline_2` 为基准。2026-05-09 最新回滚后，部分关键参数已恢复到历史 `best_baseline_2` 口径，但仍不是逐项严格复现。
- 历史 `best_baseline` 对应版本：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_18-26-58_stage0_lowslip_gate_v1_700iter`
  - checkpoint：`model_699.pt`
  - 详细报告：`results/stage0_lowslip_gate_v1_model699_detailed_result_config_motion_model_2026-04-28.md`
- 历史 `best_baseline_2` 对应版本：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-28_15-28-38_best_baseline_2`
  - checkpoint：`model_699.pt`
- 恢复范围：
  - Stage0 reward 恢复为 lowslip gate v1 的 7 项结构。
  - PPO timeout 语义恢复为 `is_finite_horizon = False`，即 timeout 作为 time-limit，允许 PPO bootstrap。
  - 底层控制恢复为 low-slip allocator + 车轮 torque target，不再使用直接 wheel velocity target。
  - 纵滑率方向恢复为历史口径：`kappa = (v_parallel - r * omega) / max(abs(v_parallel), epsilon)`。
- 当前直接重启 Stage0 时仍会保持一致的主要项：`64` env、`40 s` episode、`30 Hz` 控制、`54` 维 actor/critic 观测、`8` 维动作、平地、双 waypoint、PPO `512` steps/env、`700` iterations、`learning_rate = 1e-4`、`desired_kl = 0.008`。
- 当前已恢复到历史 `best_baseline_2` 口径的关键项：
  - `base_allow_reverse = True`。
  - 未接线的 `ball_joint_planner_qddot_limits` 和 `ball_joint_planner_track_error_limit` 已从 Stage0 配置和接触回放评估脚本中移除。
  - `wheel_joint_effort_limit_sim = 20.0`。
  - `progress_gate_min_multiplier = 0.25`。
- 2026-05-12 已按用户要求从备份恢复原底层运动学模型；Stage0、Stage1 和共享 Base 配置中的底层球铰 / 车轮执行参数继续统一。
  - 球铰 active 链路为 `q_target = clamp(q_desired)`，不使用 reference governor。
  - 轮速分配姿态变化率为 `qdot_alloc = LPF(qdot_actual)`，`tau_v = 0.04 s`。
  - 球铰 actuator `stiffness = 120.0`、`damping = 10.0`、`effort_limit_sim = 60.0`、`velocity_limit_sim = 2.0`。
  - 车轮 actuator `stiffness = 0.0`、`damping = 0.0`、`effort_limit_sim = 20.0`、`velocity_limit_sim = 20.0`。
  - low-slip / 牵引参数：`low_slip_lambda_tracking = 1.0`、`low_slip_lambda_lateral = 5.0`、`wheel_torque_tracking_gain = 2.0`、`wheel_slip_feedback_gain = 4.0`。
- 2026-05-10 新修改：Stage0 已启用 `action_rate_penalty` 作为第一步动作平滑约束；`action_rate_penalty_weight = -50.0`、`action_rate_base_ratio = 0.2`、`action_rate_joint_ratio = 1.0`，重点压制六个球铰动作在连续控制步之间的高频跳变。
- 当前源码与历史 bestline / `best_baseline_2` 仍不一致的关键项：
  - 底层控制参数现在以 Stage0 / Stage1 统一和 direct-target 验证为优先，不再逐项追求复现历史 `best_baseline_2` 的球铰 drive 和 planner gain。
  - 旧 `ball_joint_planner_qdot_limits` 不再是 active 配置；历史 `best_baseline_2` 仍使用旧 planner 口径。
  - `ball_joint_velocity_limit_sim`：当前 `2.0`，历史 `1.0`。
  - `ball_joint_effort_limit_sim`：当前 `60.0`，历史 `20.0`。
  - 最新工程修正：当前 `wheel_speed_allocator.py` 已用实测轮距 `d1/d2/d3 = 0.539 m`，历史 run diff 记录旧轮距约 `0.447 m`；当前 articulation root `solver_velocity_iteration_count = 4`，历史 run 参数为 `0`。
- 当前 Stage0 已重新允许倒车：`base_allow_reverse = True`，`a0 -> vx_cmd` 映射为 `[-2.0, 2.0] m/s`；该项已与历史 `best_baseline_2` 一致。
- 当前仍保留的当前口径：
  - 侧滑角不恢复 2026-04-25 的 wheel local `Y` 旧轴向。
  - 当前继续使用 wheel local `Z` 作为水平侧向轴，并使用 `atan2(v_perp, max(abs(v_parallel), epsilon))`。
- 结论：若目标是训练一版“继承 bestline 思路但带当前修正”的 Stage0，可以直接启动；若目标是严格复现历史 `best_baseline_2`，启动前需要先把上述 Stage0 参数恢复到历史 `params/env.yaml` 口径，或者明确保留 `0.539 m` 轮距和 velocity solver `4` 作为新的工程修正版 baseline。

## 当前 Stage0 配置摘要

- 任务：平地双 waypoint。
- 并行环境：`64`。
- episode 时长：`40 s`。
- 控制频率：`30 Hz`。
- 每段 waypoint 距离：`10 m`。
- 命中半径：`0.5 m`。
- 动作维度：`8`，即 `[vx_cmd, yaw_rate_cmd, 6 个球铰姿态目标]`。
- 观测维度：actor / critic 均为 `54`。
- PPO 默认：
  - `experiment_name = complete_car_stage0`
  - `run_name = best_baseline`
  - `num_steps_per_env = 512`
  - `max_iterations = 700`
  - `seed = 1`
- 当前 Stage0 baseline 参数详情表：`docs/stage0_baseline参数详情表.md`。

## 当前 Stage0 回放视频

- 已按用户要求回放 `best_baseline_2/model_699.pt` 并录制 2 分钟 chase 跟踪视角视频。
- 视频文件：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-28_15-28-38_best_baseline_2/videos/play/best_baseline_2_chase_120s.mp4`。
- 视频规格：`1280x720`、`60 fps`、`120 s`、`7200` 帧。
- 回放设置：
  - 使用 `env_0` chase follow view：`/view/env_0/chase_camera`。
  - 开启目标点红色 marker。
  - 目标方向箭头关闭，避免此前 Fabric point-instancer warning。
- 抽帧检查：`results/best_baseline_2_chase_120s_frame10.jpg`，确认 chase 视角和目标点 marker 可见。
- 2026-05-09 现场复核结论：直接用当前 `scripts/play.py` 加载原始 `best_baseline_2/model_699.pt` 会使用当前源码和当前 Stage0 配置，而不会自动恢复该 run 的 `params/env.yaml` 和旧源码快照；若回放中小车运动很差，应优先解释为“旧 policy 权重 + 当前环境 / 底层控制 / joint 顺序语义”的错配，不应直接否定历史 `best_baseline_2` 的训练结果。
- 已确认本次现场回放加载路径和网络维度正确：checkpoint 为 `2026-04-28_15-28-38_best_baseline_2/model_699.pt`，actor / critic 输入维度为 `54`、actor 输出维度为 `8`。主要错配风险包括：当前轮距 allocator `d1/d2/d3 = 0.539 m` vs 历史约 `0.447 m`，当前 ball qdot / sim velocity / low-slip 参数与历史不完全一致，当前 articulation root velocity solver 为 `4` vs 历史 `0`，以及原始 Stage0 checkpoint 未经过 Stage1 warm-start 使用的 orderfix 输入 / 输出通道重排。

## 当前 reward 结构

Stage0 / Stage1 共享 active reward 项：

1. `distance_to_target`
2. `progress_to_target`
3. `reached_target`
4. `far_from_target`
5. `angle_diff`
6. `slip_penalty`
7. `action_rate_penalty`（Stage0 / Stage1 均启用；Stage0 当前 `weight = -50.0`、`base_ratio = 0.2`、`joint_ratio = 1.0`）

Stage1 额外 active reward 项：

1. `contact_support_penalty`
2. `terrain_aware_edge_speed_penalty`
3. `stuck_penalty`
4. `no_progress_penalty`
5. `airborne_spin_penalty`
6. `hard_terrain_spin_penalty`
7. `step_up_front_posture_penalty`
8. `step_up_module_progress_reward`
9. `quality_row_advance_reward`
10. `recovery_reward`
11. `drop_anti_dive_penalty`

当前不再 active 的中间实验项：

- `timeout_penalty`
- `load_equalization`
- `turn_speed_penalty`

说明：

- `turn_speed_penalty` 已从 active reward 代码、配置字段和日志中删除；`action_rate_penalty` 已作为 Stage0 / Stage1 归一化动作变化惩罚接入。
- `edge_speed_penalty` 是旧项，Stage1 当前使用 `terrain_aware_edge_speed_penalty`；`action_soft_limit_penalty` 当前保留配置字段但权重为 `0.0`。
- `progress_gate` 使用平均 gate：`0.5 * (G_kappa + G_alpha)`，不是 `min` gate。
- 正向 progress 受 gate 调制，负 progress 不被 gate 削弱。

最新 reward 尺度校验：

- Stage0 当前滑移惩罚已改为 `slip_longitudinal_penalty_ratio = 2.0`、`slip_angle_penalty_ratio = 1.0`；此前 `3.0/1.0` reward 统计输出位于 `results/stage0_model375_gui_replay_2026-05-10/reward_scale_slip_long3_angle1_summary.txt`，但最新训练已按 `2.0/1.0` 启动。
- 旧 `60 Hz` 口径下，`best_baseline4/model_375.pt` 回放的 `Reward/slip_penalty` 平均每步约 `-0.009168`，按当时 `2400` 步完整 episode 折算约 `-22.00`；`Reward/action_rate_penalty` 约 `-0.001627/step`，折算约 `-3.91`。
- 同次回放中 `Reward/progress_to_target` 约 `+0.01200/step`、`Reward/reached_target` 约 `+0.01082/step`、`Reward/distance_to_target` 约 `+0.00219/step`、`Reward/angle_diff` 约 `+0.00164/step`。
- 当前判断：`action_rate_penalty_weight = -50.0` 仍是明显但不过量的第一版平滑约束；新的滑移惩罚已经是主负项之一，约为 action-rate 惩罚的 `5.6` 倍，约为 progress 奖励绝对值的 `76%`，会明显推动策略减少纵向打滑。

## 当前底层运动模型

active 控制链：

1. policy 输出 action。
2. action 前两维映射为 `vx_cmd` 和 `yaw_rate_cmd`。
3. action 后六维映射为两组等效球铰目标姿态。
4. 球铰 position target 直接使用 `q_target = clamp(q_desired)`。
5. env 用实际球铰角速度低通维护 `qdot_alloc = LPF(qdot_actual)`。
6. low-slip 平面命令整形器生成 `shaped_planar_command`。
7. 轮速分配器用当前实际 `q`、`qdot_alloc` 和 `shaped_planar_command` 生成 `wheel_speed_reference`。
8. 轮级 traction allocator 根据纵滑反馈和接触权重生成 `wheel_torque_targets`。
9. 环境对球铰下发 position target，对车轮下发 effort target。

当前底层模型详细说明文档：`docs/底层运动学轮速分配球铰规划与力矩分配.md`。该文档按当前源码口径整理 wheel order、球铰 direct target、`qdot_alloc`、low-slip 平面命令整形、轮速参考、纵滑率和车轮 effort target 力矩公式；旧 `docs/Stage0球铰姿态规划器与底层运动学模型推导.md` 仍只作为 2026-04-20 候选推导稿保留。

当前不 active：

- 车轮 direct velocity target。
- env 层 qddot 轨迹器传入 allocator 的中间版本。
- 去掉低滑移整形后的直接轮速参考链路。
- `g_kappa/g_alpha` 纵滑/侧滑衰减诊断字段；当前轮级力矩公式不使用这两个衰减因子。

## 当前结论边界

- `best_baseline` 可作为 Stage0 平地双 waypoint 可学习、工程链路可闭环的基准版本。
- 不能把该 baseline 直接解释为低滑移协同控制已经成功。
- 原始历史 TensorBoard 的侧滑角来自旧 local `Y` 口径，不能作为真实水平侧滑证据。
- 当前代码已修正侧滑角口径，因此后续新训练的侧滑角曲线不能与历史旧侧滑角曲线直接数值比较。

## 最新训练监控结果

- 已按用户要求停止最新 Stage0 调参短训：`2026-05-10_18-21-11_stage0_slip2_actionrate_m50_qmon_700iter`。
- 本轮配置为 `action_rate_penalty_weight = -50.0`、`slip_longitudinal_penalty_ratio = 2.0`、`slip_angle_penalty_ratio = 1.0`，底层球铰 direct-target PD 为 `Kp=120, Kd=10, effort=60, velocity_limit=2, tau_v=0.04`。
- 训练已保存 `model_200.pt` 后手动终止；GPU 训练进程已释放。由于终止发生在保存后，最后控制台完整打印到 iteration `199/700`，但 `model_200.pt` 已确认落盘。
- iteration `199` 关键监控：`Action/ball_joint_desired_delta_abs_mean_raw = 0.1001`、`Observation/ball_joint_vel_limit_rate_raw = 0.0159`、`Observation/ball_joint_target_error_abs_mean_raw = 0.0800`、`Termination/success_rate = 1.0000`、`Tracking/episode_completion_pct = 23.7045`、`Observation/wheel_longitudinal_slip_abs_mean_raw = 3.1066`、`Observation/pitch_deg = -3.2621`、`Observation/wheel_normal_contact_force_sum_raw = 1.0433`。
- 当前判断：动作跳变、球铰速度贴限比例和 tracking error 相比开局均明显下降，说明 action-rate 惩罚和 direct-target PD 没有导致球铰失控；但 waypoint 完成率仍停在约 `24%`，纵滑率约 `3.1` 平台化，低滑移完成质量还没有突破。下一步应优先用 `model_200.pt` 做 GUI 回放和更细的球铰目标幅值 / tracking error ratio / 分轮接地分析。
- 已完成 `model_200.pt` 的 Stage0 flat 真实球铰轨迹导出和 MATLAB 统一 `Kp/Kd` 扫参，输出目录：`results/stage0_model200_ball_joint_pd_matlab/`。
  - 导出 CSV：`raw_traces/stage0_model200_flat_combined.csv` 和 `raw_traces/stage0_model200_flat_col00_flat.csv`，共 `9584` 行、`8` 个 env、无 done 行。
  - 当前真实回放：`q_desired_abs_mean = 0.0897 rad`、`tracking_error_abs_mean = 0.0478 rad`、误差 / 目标幅值均值比约 `0.532`、`position_target_gap = 0`、`qdot_abs_p95 = 1.255 rad/s`、`qdot >= 1.9 rad/s` 比例约 `0.66%`。
  - MATLAB 预筛：当前 `Kp=120,Kd=10` 保守稳定、速度贴限低，但真实 tracking error 占比仍偏大；`Kp=120,Kd=16`、`Kp=160,Kd=16` 可作为下一步 Isaac GUI 短回放的保守 / 中等候选，`Kp=320,Kd=24` 虽综合 risk 最低但预测 `qdot_limit_rate = 0.328`，只能作为激进候选单独观察，不宜直接替换默认训练参数。
- 已按用户要求保持 `Kp=120,Kd=10`，从 `model_200.pt` 续训到 `model_300.pt` 后停止：
  - 续训 run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-05-10_19-52-05_stage0_slip2_actionrate_m50_qmon_resume200_to_quality`
  - 已保存 `model_225.pt`、`model_250.pt`、`model_275.pt`、`model_300.pt`，GPU 已释放。
  - iteration `301` 末 `25` 轮窗口：`success_rate = 1.0000`、`episode_completion_pct ≈ 23.62%`、`v_parallel ≈ 1.29 m/s`、`q_desired` 每步跳变约 `0.0945 rad`、`qdot` 贴限比例约 `1.8%`、tracking error 约 `0.081 rad`、纵滑率约 `3.18`、`LowSlip/combined_pass_rate ≈ 0.067`、中车 pitch 约 `-6.0 deg`。
  - 当前判断：推进效率已接近或超过 `best_baseline_2`，但姿态质量明显变差；继续只靠 action-rate 惩罚不能保证中车姿态回稳。
- 2026-05-10 新增 Stage0-only pitch progress gate：
  - 当前已按用户要求改为更敏感版本：`progress_pitch_gate_deadband_deg = 1.0`、`progress_pitch_gate_k_rad = π / 32`。
  - 仅当 `|pitch| > 1 deg` 时对正向 `progress_to_target` 额外乘以 `exp(-0.5 * (|pitch| / k)^2)`；Stage1 显式保持 `progress_pitch_gate_k_rad = 0.0`，不启用该 gate。
  - 修改依据：从 `150.pt` warmstart 的 run `2026-05-10_20-39-29_stage0_pitch_gate_gauss_from150_to700` 已手动停止，最后保存到 `model_150.pt`。该 run 成功率和推进速度很快进入平台，但 `model_125` 附近 pitch 已约 `-2.60 deg`，`model_150` 前后终端可见 pitch 约 `-2.82 deg`、`ProgressGate/pitch_gate ≈ 0.963`，说明原 `deadband = 2 deg`、`k = π / 16` 太温和，不能有效压制“快速推进但中车前俯”的策略倾向。
  - 新尺度下，`|pitch| = 3 deg` 时 gate 约 `0.867`，`|pitch| = 6 deg` 时 gate 约 `0.567`，会比上一版更早、更明显地降低前俯推进的正 progress 收益。
- 2026-05-10 已按 `deadband = 1 deg, k = π / 32` 从原 `2026-05-10_18-21-11_stage0_slip2_actionrate_m50_qmon_700iter/model_150.pt` 重新 warmstart 训练：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage0/best_baseline5`
  - 已在 `model_150.pt` 保存点后停止并释放 GPU；TensorBoard 已导出到该 run 的 `tensorboard_export/`。
  - 该 run 成功率从 `model_50.pt` 起持续为 `1.0`，进入高平台；相比旧 gate run，pitch 明显改善，稳定在约 `-1.4~-1.6 deg`，没有再漂到 `-2.8 deg`。
  - 末 `25` iteration 窗口：`success_rate = 1.0000`、`episode length ≈ 619.7`、`v_parallel ≈ 1.279 m/s`、`q_desired_delta ≈ 0.1100 rad`、`qdot_limit_rate ≈ 0.0241`、`tracking_error ≈ 0.0906 rad`、`low_slip ≈ 0.0757`、`pitch ≈ -1.40 deg`。
  - 保存点窗口对比：`model_75.pt` 当前最平衡，并已按用户要求作为 `best_baseline5` 的 Stage1 warm-start 来源；窗口指标为 `success = 1.0`、`episode length ≈ 630.1`、`low_slip ≈ 0.0799`、`pitch ≈ -1.41 deg`、`tracking_error ≈ 0.0873`；`model_150.pt` 速度更快但 tracking error 升到约 `0.0898`、low-slip 降到约 `0.0767`。
  - 结论：`π / 32` gate 有效抑制了明显前俯，但尚未达到 `best_baseline2` 的运动质量；主要差距仍是 pitch 未接近 `-0.57 deg`、low-slip 未到 `0.0886`，且后段球铰 tracking 压力上升。下一步若继续优化，应优先回放 `model_75.pt` 与 `model_150.pt`，再决定是否采用更强 pitch gate 或新增更直接的姿态 / tracking 质量项。

- 已完成继续训练 run：`2026-05-09_14-22-59_best_baseline4`。
- 启动命令口径：从 `2026-05-09_12-12-50_best_baseline4/model_225.pt` resume，`CompleteCar-Stage0`、headless、`cuda:0`、`64` env，继续到总 `699/700` iteration。
- 训练全程未提前停止，最终正常退出；已确认 `model_699.pt` 落盘。
- 末 `25` iteration 对比 `best_baseline_2/model_699.pt`：`best_baseline4/model_699.pt` 的速度更高、平均 episode length 更短，但 `LowSlip/combined_pass_rate` 更低，`pitch_deg` 从 `best_baseline_2` 的约 `-0.573` 变为约 `-4.124`，车体姿态明显更差。
- 当前候选选择：速度优先可看 `model_675.pt` / `model_699.pt`；综合任务推进、打滑和车体姿态，当前优先选择 `model_375.pt`；`model_600.pt` 可作为速度更高但姿态更差的次级折中。

## MGDP 深度感知迁移调研状态

- 已检查本地 `/home/lbz/MGDP` 与官方远端 `origin/master`：当前本地 `master` 相对 `origin/master` 为“领先 1、落后 1”，远端新增提交 `dc0e4ef Uupdate author info`，仅修改 `index.html` 作者信息；`personal` 远端需要 GitHub 凭据，未完成 fetch。
- 已对照 MGDP 论文与代码实现：其深度感知主线是 Warp 深度图采集、深度图噪声注入、CNN encoder/decoder 重建干净深度图、可选高度图 encoder/decoder、深度 token 与高度 token 对比约束，再把低维视觉 token 与本体历史估计一起输入 actor。
- 当前 CompleteCar Stage1 已有局部高度 patch 直接进入 actor/critic，且相机、LiDAR 配置目前默认不参与策略输入；因此“直接复制 MGDP 完整感知模型”不是当前最短主线。
- 初步工程判断：把 MGDP 思路迁移到小车是可行的，但更适合作为 Stage2/Stage1 后续增强；在用户确认研究目标前，不应把它默认替换当前 Stage1 主线。
- 已完成围绕 height map / depth map / LiDAR / stereo / traversability / rough terrain RL / Isaac Lab height scanner 的补充检索：未找到成熟综述专门以“双目相机与 LiDAR 融合作为强化学习外感知模型”为中心；可用文献应按三条线组织，即地形可通行性与高程图融合综述、感知式强化学习 locomotion、开源感知与仿真训练框架。
- 对 CompleteCar 后续 Stage2 的当前边界判断：更合理的感知增强路线是先将双目/深度相机与 LiDAR 统一为局部 elevation / traversability map 或低维感知 token，再接入 RL 策略；不宜直接把原始双目图像和点云拼接到当前 Stage1 actor 中作为默认方案。
- 进一步按 Google Scholar / CNKI 线索复核后，英文侧最贴合“双目相机 + LiDAR 融合感知”的综述是 Marsh 等 2022《A Critical Review of Deep Learning-Based Multi-Sensor Fusion Techniques》；CNKI 侧最贴合的是王荣儿、伍济钢 2026《面向AGV环境感知的图像点云融合研究综述》和马建红等 2022《自动驾驶中图像与点云融合方法研究综述》。CNKI 中“图像点云融合”通常对应相机与 LiDAR 融合，不一定专门限定双目相机。

## 下一步优先事项

1. 若要重启 Stage1 训练，当前默认 warm-start 使用 `warmstart_best_baseline5_model75_terrain_features/model_0.pt`；来源为 `best_baseline5/model_75.pt`，不是旧 `best_baseline_2` orderfix 文件，也不是上一版 `best_baseline4/model_375.pt`。
2. 若继续研究低滑移控制，不应只看 `success_rate`，需要同步观察纵滑率、当前口径侧滑角、有效推进速度、中车载荷和 waypoint 完成质量。
3. 若要声称低滑移/协同控制贡献，需要设计新的成功条件、对比实验或 ablation，而不是仅依赖该 baseline。
