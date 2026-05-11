# ChatGPT Zip Analysis Prompt

你是一名强化学习机器人控制实验分析助手。请根据我上传的 zip 包，对一次 Isaac Lab / RSL-RL 的 Stage1 地形训练结果进行数据驱动分析。请不要泛泛评价，也不要只根据文件名或我给出的背景下结论；必须优先读取 zip 内的 `tensorboard_export/`、runtime log、`params/`、源码和文档后再下判断。

## 背景

这次 zip 包是一次 `CompleteCar-Stage1` 训练的结果和配置包，不包含 checkpoint 权重。请不要要求 `.pt` 模型文件，也不要做需要回放视频或模型推理才能完成的判断。可以基于 TensorBoard 标量、runtime log、参数配置和源码逻辑分析训练表现。

本次 run：

- run directory: `RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-11_12-20-55_stage1_80env_resume_from_m100_1000iter_20260511_1220`
- runtime log: `RL_Training/logs/runtime/stage1_80env_resume_from_m100_1000iter_20260511_1220.log`
- task: `CompleteCar-Stage1`
- num envs: `80`
- 训练从上一轮 `96 env` OOM 前最后可靠的 `model_100.pt` 继续，但请注意：RSL-RL checkpoint resume 继承策略/优化器，不继承 terrain-column runtime 状态，所以本 run 的 terrain row / completed-column 状态从新环境初始化开始。
- 训练已完整结束到最终 checkpoint `model_1099.pt`。
- hard terrain 训练列映射：
  - `col05-col07`: `stairs_down`
  - `col08-col09`: `discrete_obstacles`
- 其余地形列：
  - `col00`: `flat`
  - `col01`: `slope_down`
  - `col02`: `slope_up`
  - `col03-col04`: `uneven rough`
- 当前 Stage1 已关闭 hard terrain 的 quality-gated row advance：命中 hard terrain 目标后可以按普通逻辑升 row；质量相关信号仍作为 reward / diagnostics 保留。因此分析时要区分“row 推进了”和“运动质量是否足够好”。

## zip 内重点文件

请优先检查以下内容：

1. `tensorboard_export/latest_values.csv`
2. `tensorboard_export/summary.json`
3. `tensorboard_export/scalars/*.csv`
4. runtime log：`RL_Training/logs/runtime/stage1_80env_resume_from_m100_1000iter_20260511_1220.log`
5. `params/env.yaml`
6. `params/agent.yaml`
7. `git/Graduation-Project.diff`
8. Stage1 源码与文档：
   - `complete_car_stage1_cfg.py`
   - `base/env.py`
   - `mdp/rewards.py`
   - `mdp/stage1_eval.py`
   - `mdp/terrain_features.py`
   - `docs/Stage1参数详情表.md`
   - `docs/stage1评价指标.md`
   - `docs/优化方案.md`
   - `docs/current_status.md`
   - `docs/conversation_history.md`

如果某个指标不存在，请明确说“zip 中没有该指标”，不要编造。

## 分析目标

请重点回答以下问题。

### 1. 训练整体是否稳定、是否收敛

请基于标量曲线分析：

- PPO loss / surrogate loss / value loss / entropy / learning rate / fps 等训练稳定性指标。
- 是否存在 loss 尖峰、训练后期行为退化、震荡或平台期。
- `current_level_mean`、`rows_advanced_mean`、`row_advance_rate`、`completed_column_rate`、`unfinished_column_count` 等课程推进指标是否显示收敛。
- 不要把“训练跑完”直接等同于“策略收敛”。请给出证据。

### 2. hard terrain 下小车表现

请把 hard terrain 作为主分析对象，分别分析：

- `col05-col07 stairs_down`
- `col08-col09 discrete_obstacles`

请至少比较：

- row / current level 推进情况。
- `row_advance_rate` 或类似 adv_rate 指标。
- stagnation / stuck / no-progress。
- contact loss / contact support / row_contact_support_min。
- pitch / roll / pitch rate。
- action saturation / action magnitude / action rate。
- speed limit active rate / overspeed near edge。
- quality_advance_score / row_advance_without_quality_rate / raw_hard_hit_rate。
- rear follow / front/middle/rear module climb 或类似模块通过指标。

请明确回答：

- hard terrain 哪几列真正学得最好？
- 哪几列只是 row 高但质量不稳定？
- 哪些列出现明显平台期或退化？
- stairs_down 与 discrete_obstacles 的瓶颈是否相同？
- 当前策略是否可以认为已经在 hard terrain 上稳定收敛？为什么？

### 3. 其余地形表现

请分析：

- `flat`
- `slope_down`
- `slope_up`
- `rough`

重点看：

- flat retention 是否保持。
- slope / rough 是否已经完成或稳定。
- 是否存在对 hard terrain 优化后对简单地形的遗忘。
- 其余地形中是否有被 completed-env recycling 保留训练样本支持。

### 4. 奖励函数量级与作用

请结合 `params/env.yaml`、`complete_car_stage1_cfg.py`、`mdp/rewards.py` 和 TensorBoard 中 `Reward/*` 或 `Debug/Stage1/Reward/*` 相关 CSV，分析各 reward 分量的实际量级。

请特别比较：

- `progress_to_target`
- `reached_target`
- `distance_to_target`
- `angle_diff`
- `slip_penalty`
- `action_rate_penalty`
- `contact_support_penalty`
- `terrain_aware_edge_speed_penalty`
- `stuck_penalty` / `no_progress_penalty`
- posture / pitch / anti-dive 相关项
- quality row advance reward
- airborne / hard-terrain spin penalty
- total reward

请回答：

- 哪些 reward 项实际量级最大？
- 哪些 reward 项几乎不起作用？
- 是否存在某些惩罚压过推进目标，导致保守/停滞？
- 是否存在推进奖励过强，导致低质量 row advance？
- reward 量级是否随训练阶段或 hard terrain row 变化而变化？
- 如果需要修改 reward，请说明应该调哪一项、调大/调小、为什么。

### 5. 显著存在的问题

请按严重程度列出问题，并且每个问题都要给证据。请优先关注：

- hard terrain 未完成列。
- row 推进与运动质量不一致。
- 台阶/障碍列推进不均衡。
- 接触支撑不足。
- pitch 过大或俯仰变化过快。
- 动作饱和或动作跳变。
- stuck / stagnation / no-progress。
- 速度限制频繁触发或边缘超速。
- PPO loss 尖峰或训练不稳定。
- completed-env recycling 是否影响了指标解释。

请不要只说“需要继续训练”。如果认为继续训练有意义，要说明为什么；如果认为需要先改机制，也要说明为什么。

### 6. 下一步修改优化建议

请给出可执行的下一步建议，按优先级排序。每条建议请包含：

- 修改对象：reward / curriculum / reset / observation / low-level control / logging / PPO 参数 / replay evaluation。
- 具体修改内容。
- 预期影响。
- 可能副作用。
- 验证方法和判据。

请避免空泛建议，例如“调奖励”“增加训练时间”“加传感器”。除非数据明确支持，否则不要建议加入 LiDAR / 双目 / 新传感器；当前主线默认使用局部 height patch 和确定性低维地形特征。

请特别考虑：

- 是否应恢复 hard terrain 质量门槛，还是保持 row advance 不门控但加强质量 reward。
- 是否需要对 `stairs_down` 和 `discrete_obstacles` 分别设计不同的质量约束。
- 是否需要调整 completed-env recycling 比例。
- 是否需要对 hard terrain 高 row 做更慢速度或相位控制。
- 是否需要强化模块级通过奖励，而不是只看目标命中。
- 是否需要对 PPO loss 尖峰做 reward normalization / advantage scale / clipping / learning rate 调整。

## 输出格式要求

请用中文输出，结构如下：

1. `数据读取与可靠性说明`
2. `训练整体结论`
3. `Hard Terrain 重点分析`
4. `其余地形分析`
5. `奖励函数量级分析`
6. `显著问题清单`
7. `下一步优化建议`
8. `需要补充的回放或实验`

每个关键判断都要附上来源，例如：

- 文件路径
- scalar 名称
- step 范围或末段统计
- 具体数值

不要过度自信。不能由数据支持的内容，请标为“无法仅凭该 zip 判断”。
