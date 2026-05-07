# 给 ChatGPT 的分析提示词

你将收到一个 Stage1 强化学习训练分析包。请不要寻找或要求 `.pt` 模型权重文件；本次任务只分析训练曲线、环境配置、奖励设置和运动行为质量。`.pt` 只用于回放或继续训练，不用于本轮曲线分析。

## 数据包背景

- 任务：`CompleteCar-Stage1`
- 机器人：三车体六轮主动铰接地面车辆，使用等效串联球铰建模。
- 训练阶段：Stage1 地形课程训练。
- 本轮 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-06_23-51-57_stage1_second_training_test_128env_450_to_1600_overnight`
  - 从 `model_450.pt` resume，目标原计划到 `1600` iteration。
  - 用户要求在 `model_1500.pt` 保存后停止。
  - TensorBoard scalar 数据覆盖 step `450-1508`。
- 本包包含：
  - 原始 TensorBoard event 文件。
  - `tensorboard_export/scalars/*.csv`：逐项 scalar 曲线，共 `343` 个 CSV。
  - `tensorboard_export/summary.json`、`latest_values.csv`、`group_summary.csv`。
  - `params/env.yaml`、`params/agent.yaml`。
  - Stage1 环境、地形、动作、观测、奖励、reset、课程推进、评价指标源码。
  - Stage1 参数详情和评价指标说明文档。

## 地形列映射

请按以下地形列理解 `Stage1Eval/colXX_*`：

- `col00_flat` / `flat`：平地
- `col01_slope_down`：下坡
- `col02_slope_up`：上坡
- `col03_rough`、`col04_rough`：粗糙地形
- `col05_stairs_down`、`col06_stairs_down`：下台阶
- `col07_stairs_up`、`col08_stairs_up`：上台阶
- `col09_obstacles`：离散障碍

注意：`difficulty_score` 越高表示该地形越难或策略表现压力越大，不是奖励越高。

## 请完成的分析任务

请基于 CSV 曲线和参数配置，做一份全面训练结果分析报告。报告要覆盖以下内容：

1. 训练总体进展
   - 说明从 step `450` 到 `1508` 的整体学习趋势。
   - 分析 `Train/*`、`Loss/*`、`Perf/*` 的变化，判断训练是否数值稳定。
   - 关注 value loss、surrogate loss、entropy/action std、mean reward、episode length 是否表现出收敛、震荡或退化。

2. 全局地形推进能力
   - 重点分析：
     - `Stage1Eval/global/current_level_mean`
     - `Stage1Eval/global/rows_advanced_mean`
     - `Stage1Eval/global/row_advance_rate`
     - `Stage1Eval/global/max_row_reached_rate`
     - `Stage1Eval/global/forward_x_mean`
     - `Stage1Eval/global/stagnation_rate`
     - `Stage1Eval/global/effective_failure_rate`
   - 判断策略是否只是能偶尔到达 row 10，还是已经稳定保持并继续推进。
   - 如果存在“到高 row 后又回落”的现象，请解释可能含义。

3. 各地形分别分析
   - 分别分析平地、下坡、上坡、粗糙地形、下台阶、上台阶、离散障碍。
   - 对每类地形至少比较：
     - `current_level_mean`
     - `rows_advanced_mean`
     - `row_advance_rate`
     - `difficulty_score`
     - `v_forward_mean`
     - `stagnation_rate`
     - `effective_failure_rate`
   - 识别最容易地形、第二梯队困难地形、主要瓶颈地形。
   - 请明确说明上下坡和粗糙地形是否已经基本可用，台阶是否仍是瓶颈。

4. 运动行为质量分析
   - 重点分析以下曲线：
     - `longitudinal_slip_abs_mean`
     - `slip_angle_abs_mean`
     - `combined_low_slip_pass_rate`
     - `contact_loss_rate`
     - `pitch_abs_mean`
     - `roll_abs_mean`
     - `action_saturation_rate`
     - `action_abs_mean`
     - `action_rate_abs_mean`
     - `ball_joint_limit_usage_max`
     - `normal_force_sum_mean`
     - `v_lateral_abs_mean`
     - `lateral_velocity_ratio`
     - `yaw_rate_abs_mean`
   - 判断小车运动是“稳定通过”“高滑移硬顶”“大俯仰冲击”“动作接近饱和”还是“明显失稳”。
   - 请区分推进能力和运动质量：能向前推进不等于运动已经收敛或足够平稳。

5. 奖励与配置解释
   - 阅读 `params/env.yaml`、`complete_car_stage1_cfg.py`、`mdp/rewards.py`、`docs/Stage1奖励函数设计草案.md`。
   - 解释当前 reward 中哪些项可能促进前进，哪些项约束滑移、动作变化、接触支撑和地形突变前速度。
   - 如果训练曲线表现出“推进能力上升但 action saturation / pitch / slip 偏高”，请结合 reward 权重和指标解释可能原因。

6. 收敛性判断
   - 请给出明确判断：当前策略是否已经收敛？
   - 判断标准必须同时考虑：
     - terrain level 是否稳定继续提升
     - 各地形 difficulty 是否下降或稳定
     - failure 是否为 0
     - slip、pitch、contact loss、action saturation 是否趋稳
     - reward/loss 是否趋稳
   - 不要只因为 failure rate 为 0 就判断收敛。

7. 后续建议
   - 请只给出基于数据的诊断建议，不要泛泛而谈。
   - 建议要分为：
     - 需要回放验证的现象
     - 需要画图进一步确认的曲线组合
     - 可能的 reward / curriculum / reset 方向
     - 当前可以写入论文结果分析的边界性结论
   - 请保持研究表述边界：不能声称主动铰接结构已经被证明优于其它结构；只能说明当前 Stage1 策略在这些地形上的训练现象和局限。

## 输出格式要求

请用中文输出报告，结构建议如下：

1. 总体结论
2. 训练稳定性与收敛性
3. 地形分项分析
4. 运动行为质量分析
5. 关键曲线变化解读
6. 主要瓶颈与可能原因
7. 下一步验证建议
8. 可写入论文的谨慎表述

请尽量引用具体 scalar 名称、step 区间和数值范围。若某项数据在包内找不到，请明确说“未找到该 scalar”，不要猜测。
