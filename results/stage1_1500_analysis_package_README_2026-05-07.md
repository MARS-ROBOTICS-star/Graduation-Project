# Stage1 1500 Iteration 分析包说明

## 基本信息

- 训练任务：`CompleteCar-Stage1`
- run 目录：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-06_23-51-57_stage1_second_training_test_128env_450_to_1600_overnight`
- 本轮启动方式：从 `2026-05-06_21-41-43_stage1_second_training_test_128env_resume_to_700/model_450.pt` resume，目标原计划继续到 `1600` iteration。
- 用户本次要求：训练到 `1500` 后保存模型并停止，然后打包 TensorBoard 数据和 Stage1 RL 环境参数配置；后续补充要求为保留全部 iteration 数据曲线，模型文件按每 `100` iteration 放一个。
- 已确认目标 checkpoint：`model_1500.pt`
- 停止说明：`model_1500.pt` 已在 `2026-05-07 09:10:30` 落盘；为确认保存完成后再停止，随后发送 `SIGINT` 停止训练。由于停止信号发出前还有缓冲写入，TensorBoard 导出的 scalar 曲线覆盖 step `450-1508`。

## 压缩包主要内容

- `events.out.tfevents.*`：原始 TensorBoard event 文件。
- `tensorboard_export/`：从 event 文件导出的全部非空 scalar CSV 和摘要 JSON。
  - `summary.json`：所有 scalar tag 的统计摘要。
  - `latest_values.csv`：每个 scalar 的首值、末值、均值、最小值、最大值等。
  - `group_summary.csv`：按 tag group 汇总。
  - `scalars/*.csv`：每个 scalar tag 的逐 step 曲线；本包共导出 `343` 个非空 scalar CSV，另有 `3` 个汇总文件，曲线 step 范围为 `450-1508`。
- `params/env.yaml`：本次 run 保存的环境参数快照。
- `params/agent.yaml`：本次 run 保存的 PPO / agent 参数快照。
- `git/Graduation-Project.diff`：训练启动时记录的工程差异快照。
- `model_450.pt`：本次 resume 训练段的起点模型。
- `model_500.pt`、`model_600.pt`、`model_700.pt`、`model_800.pt`、`model_900.pt`、`model_1000.pt`、`model_1100.pt`、`model_1200.pt`、`model_1300.pt`、`model_1400.pt`、`model_1500.pt`：按每 `100` iteration 保留的模型 checkpoint。
- `RL_Training/source/complete_car_lab/.../complete_car/`：Stage1 环境、地形、MDP、奖励、观测、动作、reset、evaluation 等源码配置。
- `RL_Training/scripts/train.py` 与 `RL_Training/scripts/play.py`：训练与回放入口脚本。
- `docs/Stage1参数详情表.md`、`docs/stage1评价指标.md`、`docs/Stage1奖励函数设计草案.md`：Stage1 参数与指标说明文档。

## 1500 附近关键指标

`Learning iteration 1500/1600`：

- `Mean reward`: `9.78`
- `Mean episode length`: `445.67`
- `Stage1Eval/global/current_level_mean`: `10.1306`
- `Stage1Eval/global/rows_advanced_mean`: `1.5704`
- `Stage1Eval/global/effective_failure_rate`: `0.0000`
- `Stage1Eval/flat/retention_score`: `0.9297`
- `Stage1Eval/flat/row_advance_rate`: `0.8681`
- `Stage1Eval/flat/v_forward_mean`: `2.2458`
- `Stage1Eval/global/longitudinal_slip_abs_mean`: `4.2330`
- `Stage1Eval/global/pitch_abs_mean`: `11.0940`
- `Stage1Eval/global/action_saturation_rate`: `0.3869`
- 最难地形列：`hardest_col_index = 7.1562`

1500 时各地形列难度：

- `col01_slope_down`: `0.1334`
- `col02_slope_up`: `0.1164`
- `col03_rough`: `0.2719`
- `col04_rough`: `0.2210`
- `col05_stairs_down`: `0.5374`
- `col06_stairs_down`: `0.5357`
- `col07_stairs_up`: `0.5432`
- `col08_stairs_up`: `0.5532`
- `col09_obstacles`: `0.4834`

## 初步观察边界

- 平地、坡地、粗糙地形已经具备较稳定推进能力，row 10 可反复触达。
- 台阶上 / 下仍是主要瓶颈，尤其 `col07-col08 stairs_up` 在 `1500` 附近最难。
- 训练没有出现有效失败率上升，`effective_failure_rate` 保持为 `0`。
- 运动质量还不能判断为完全收敛：纵向滑移、pitch 和 action saturation 仍偏高，说明策略在台阶等难地形上仍有“用大动作硬顶”的倾向。
