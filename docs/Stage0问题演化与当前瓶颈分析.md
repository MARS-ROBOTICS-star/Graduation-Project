# Stage0问题演化与当前瓶颈分析

本文档基于以下信息整理当前 Stage0 面临的问题：

- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- 已有代表性训练 run 的诊断结论

文档目的不是重复聊天记录，而是把**问题如何暴露、做过哪些修改、为什么仍然不行、当前真正卡在哪里**系统写清楚，供后续继续设计任务定义、reward、观测和 allocator 时直接使用。

---

## 0. 2026-04-18 当前主线口径

这份问题分析文档保留了当天多个分支的实验结论，但**当前默认主线已经再次变化**。  
因此使用本文件时要先区分：

- 当前默认源码口径：
  - `8m / 16s / 70obs / 12动作直驱 / long slip显式代价`
- 之前回退口径：
  - `8m / 16s / 66obs / 8动作 / 单段 tracking reward / allocator`
- 同日 `2m` 重构分支：
  - `2m / 32s / pose + capture + traction-aware scaling`

当前这版默认主线还没有新训练结果。  
所以本文件下面保留的历史问题链条，主要仍用于说明：

- 高滑移和半程平台是怎样暴露出来的
- allocator 分支为什么会长期卡住
- 之前各轮 reward / task-geometry 重构分别解决了什么，没解决什么

---

## 1. 当前问题一句话概括

当前 Stage0 的反复失败模式不是“训练跑不起来”，而是：

- 要么靠高滑移、横滚、抬前车、硬挪去换一点距离缩短
- 要么在显式惩罚滑移后掉进“少动少滑、但基本走不过去”的保守局部最优

也就是说，当前主问题不是 PPO 数值稳定性，而是：

**任务定义、reward 目标、以及当前开环速度分配模型的物理假设之间存在结构性不一致。**

---

## 2. 当前已经明确排除的“伪问题”

根据多轮训练和诊断，下面这些已经不再是当前主因：

### 2.1 不是训练启动问题

多轮 run 已证明：

- Isaac Lab 环境创建稳定
- `cuda:0` 正常
- articulation 能正常建立
- 不存在长期的 NaN / 立即发散

因此当前不是“项目没跑通”，而是“跑通后学到的行为不对”。

### 2.2 不是单纯 observation scale 配错

之前已对 observation scale 做过专门检查，结论是：

- 当前 observation scale 不是首要矛盾
- 真正的问题在动作语义、reward 耦合和执行层物理一致性

### 2.3 不是简单翻车或姿态失稳

多轮 run 中经常出现：

- `time_out_rate` 很高
- `bad_orientation_rate` 不高
- 系统能活很久

说明很多失败策略并不是“翻车了”，而是：

- 活着
- 也在朝目标挪
- 但运动质量差，滑移高，或者后期停在平台区

---

## 3. 问题演化主线

下面按实验脉络梳理问题是怎么一步步暴露出来的。

### 3.1 最小 reward 阶段：progress 学回来了，但高滑移、球铰越界和姿态问题重新暴露

代表 run：

- `2026-04-17_13-21-54`

当时结论：

- 策略已经能学到明显推进
- 但主要问题变成：
  - 球铰越界
  - 姿态激进
  - 纵滑 / 侧滑仍高
  - critic value loss 偏高

这说明：

- 单纯恢复 progress 信号，不能自动得到“健康运动”
- policy 会用更激进的姿态和球铰余量去换推进

### 3.2 roll_gate 阶段：生存率改善了，但任务质量下降

代表 run：

- `2026-04-17_14-12-39`
- `2026-04-17_15-30-13`

当时尝试：

- 加 `roll_gate`
- 收紧 `orientation_limit_deg`

结果：

- 存活和 goal reaching 改善
- 但没有真正进入低倾斜、低滑移的健康区间
- 后来还出现了“低 roll 但低任务质量”的局部最优

这说明：

- 姿态约束可以改变行为风格
- 但它并没有解决“如何高质量地推进”这个核心问题

### 3.3 slip gate 阶段：reward 结构开始主导训练失败

代表 run：

- `2026-04-17_16-29-08`
- `2026-04-17_17-02-10_slipclip3_latk4_v1`

当时尝试：

- 把纵滑和侧滑更明确地放进 gate
- 放宽 slip clip
- 调小 `lateral_slip_gate_scale`

结果：

- slip gate 长期接近 `0`
- progress 信号几乎被关死
- critic 变得不健康

当时已经得到一个关键结论：

- 问题不只是“滑移大”
- 而是 “6 个轮子的 slip gate 连乘结构太严”，导致 reward 主信号被关断

### 3.4 8维动作 + allocator 阶段：训练终于健康起来，但高滑移和球铰余量消耗问题仍然存在

代表 run：

- `2026-04-17_17-28-36_action8_allocator_v1`
- `2026-04-17_17-33-20`
- `2026-04-17_18-02-38_axis_usage_probe_v1`

当时做的关键修改：

- 从 `6球铰 + 6轮速直驱` 改为：
  - `6球铰 + 2底盘平面命令`
- wheel speed 改为通过 measured-geometry allocator 计算

结果：

- 这是目前最健康的 Stage0 主线
- PPO 数值更稳定
- `mean_episode_length` 可以跑满
- 后段也不再必然球铰崩坏

但新的问题暴露出来：

- 高纵滑和高侧滑仍然存在
- 策略更会推进后，会主动消耗球铰姿态余量
- 球铰姿态开始成为换取 progress 和 heading 的直接杠杆

这一步非常关键，因为它说明：

- 动作语义修正是有价值的
- 但 allocator 本身仍然没有解决“高滑移换 progress”的根因

### 3.5 球铰限位分析：越界不是偶然，而是更有效策略主动消耗余量

代表 run：

- `2026-04-17_17-33-20`
- `2026-04-17_18-02-38_axis_usage_probe_v1`

当时新增：

- 分轴球铰位置
- 分轴限位利用率均值 / 最大值

结论：

- “更接近目标后 ball joint limit 抬升”不是因为姿态失控
- 而是更会推进的策略开始主动用球铰余量换 progress / heading_gate

这说明：

- 球铰当前在任务里并不是“协同转向器”
- 更像一个 policy 可以随时拿来补偿推进和转向的自由形态杠杆

### 3.6 terminal phase / capture 方向：验证后发现当前 Stage0 还不是终端捕获任务

代表 run：

- `2026-04-17_18-35-19_capture_holdgoal_v1`
- `2026-04-17_18-38-44_capture_holdgoal_goal6_v1`
- `2026-04-17_18-41-26_capture_holdgoal_goal6_bonus10_v1`
- `2026-04-17_18-44-04_capture_holdgoal_goal6_bonus10_reverse_v1`
- `2026-04-17_20-21-01_terminal_phase_verify_v1`

当时做的尝试：

- 改 hold-goal
- 缩短 goal distance
- 提高 terminal bonus
- 开 reverse
- 做 terminal/capture phase

结果：

- tracking 主线没被打坏
- 但 terminal capture 仍然几乎没有真正建立起来

结论：

- 当前 Stage0 本质上仍然是 tracking-style shaping 任务
- 不是简单改几个命令/bonus 参数就能变成 terminal task

### 3.7 8m 几何减压实验：目标距离缩短立刻改善主任务，但不是根因修复

代表 run：

- `2026-04-17_21-55-30_exp1_goal8_baseline_no_traction_v1`

结果：

- 从 `12m` 改到 `8m` 以后，goal completion 和 goal error 明显改善

结论：

- 任务几何压力确实是一个变量
- 但它改变的是任务难度，不是执行层物理一致性

### 3.8 traction-aware v2 wheel-limit：执行层开始介入，但效果不够

代表 run：

- `2026-04-17_22-15-03_exp2_goal8_traction_v2_v1`

当时做的事：

- 在 allocator 输出之后、写 wheel command 之前
- 加逐轮动态 wheel-speed limit

结果：

- 这个 v2 governor 不是没工作
- 但它没有带来足够有意义的主任务提升

结论：

- 只在 wheel target 后面做限速，不足以解决当前问题
- 因为 allocator 主体仍然按开环纯滚映射工作

### 3.9 旧 explicit slip cost：traction 指标改善，但代价转移到姿态 / 球铰

代表 run：

- `2026-04-17_22-34-48_exp3_goal8_explicit_slip_cost_v1`

当时做的事：

- 关掉 slip gates
- 用显式 slip cost 直接扣 tracking reward

结果：

- `goal_completion_pct`、`goal_pos_error`、`long slip`、`slip angle` 都比同日另外两轮更好
- 但姿态压力明显上升

结论：

- 明确惩罚 slip 是有效的
- 但如果缺少对球铰余量 / 姿态代价的同步约束，策略会把代价转移到其他自由度

### 3.10 66维观测 + 新 reward 分支：训练稳定，但进入高滑移平台区

代表 run：

- `2026-04-18_10-33-52_gpu_stage0_obs66_goal8_v1`

当时改动：

- 把 `ball_joint_vel`
- `ball_joint_target_error`
- `head_roll_pitch / tail_roll_pitch`
- `wheel_joint_vel`
  正式接入 actor 观测

结果：

- 环境稳定
- PPO 稳定
- 后段 ball joint 不崩
- 但进入高滑移、高姿态代价的平台区

关键结论：

- 新观测没有把系统搞坏
- 但也没有单独解决执行层 traction mismatch

### 3.11 当前 explicit long slip cost 分支：滑移压下来了，但主任务塌成保守局部最优

代表 run：

- `2026-04-18_11-08-59_66obs_longslip_cost_v1`

当时改动：

- `long slip` 从 gate 中拿出来，改成显式负代价
- `side slip gate` 改为 `6` 轮绝对值均值进入余弦 gate

结果：

- `|longitudinal slip|`、`|slip angle|`、`tilt_deg` 都显著下降
- 但 `progress`、`gated_progress`、`goal_completion_pct` 明显塌缩

结论：

- 这版 reward 没炸训练
- 但把策略推成了“少动少滑”的保守局部最优

---

## 4. 现阶段真正暴露出来的问题

把上面的实验串起来，当前问题已经比较清楚了。

### 4.1 问题一：当前任务定义更像“稳定到点”，但环境没有把“如何到点”定义完整

当前 reward 的核心仍是：

- 距离缩短
- 朝向对准
- 部分滑移约束

但它没有把以下内容定义为同等级核心目标：

- 运输质量
- 低姿态消耗
- 低异常抬头
- 合理载荷分布
- 合理球铰余量使用

因此 policy 很容易学到：

- 只要 reward 接受，抬头、横滚、硬拖也可以

### 4.2 问题二：当前 allocator 是开环运动学模型，不对真实运动质量负责

当前 measured-geometry allocator 的主体仍然是：

- 高层 planar command
- 当前球铰位置 / 速度
- Jacobian 乘法分配轮速

它没有显式考虑：

- wheel normal force
- 纵滑
- 侧滑
- 接触状态
- 实际底盘 twist 与命令 twist 的误差

因此：

- 一旦高层命令和真实轮地接触状态不一致
- policy 就只能自己通过球铰、横滚、抬头、硬挪来补偿

### 4.3 问题三：reward 和执行层在“谁来负责 traction”这件事上互相错位

现在的情况是：

- allocator 假设可以按理想几何把命令分到轮速
- reward 再去事后惩罚 slip

这会导致两类失败模式反复出现：

1. 不惩罚或惩罚不够时：
   - 高滑移换一点 progress
2. 惩罚过强时：
   - 少动少滑但不前进

也就是说：

当前 reward 在事后纠错，但执行层并没有先提供一个物理上一致的执行语义。

### 4.4 问题四：球铰当前被用成了“补偿器”，不是“协同器”

从多轮回放和分轴日志看，当前球铰被 policy 用来：

- 改变姿态
- 改变接触几何
- 改变法向载荷分布
- 换取 progress / heading

这说明当前球铰在系统里的角色更接近：

- 补偿推进和转向困难的自由度

而不是：

- 结构化的协同转向器
- 结构化的地形适应器

### 4.5 问题五：当前 Stage0 还不是“目标频繁变化下协同转向”的任务

当前：

- `resampling_time = 16 s`
- `episode_length = 16 s`

所以每个 episode 基本只有一个目标。

这意味着：

- 当前 Stage0 还不能检验
  - “目标频繁变化时球铰能否帮助快速转向”

也就是说，用户现在脑中更强的研究问题，是后续阶段问题，不是当前 Stage0 已经在测的问题。

---

## 5. 之前做过的优化，为何仍然不够

### 5.1 reward 优化做过很多，但 reward 不是唯一矛盾

已经做过：

- 最小 reward
- roll gate
- slip gate
- slip gate 放宽
- explicit slip cost
- current long-slip quadratic penalty

这些修改都改变了行为风格，但没有一版同时满足：

- 稳定推进
- 可接受滑移
- 低姿态代价
- 低球铰余量消耗

这说明：

- reward 很重要
- 但它不是唯一根因

### 5.2 观测增强有价值，但不是直接解法

已经新增到 policy 的观测：

- `ball_joint_vel`
- `ball_joint_target_error`
- `head_roll_pitch`
- `tail_roll_pitch`
- `wheel_joint_vel`

结果：

- 训练依然稳定
- 但高滑移平台区问题仍然存在

这说明：

- policy 更“看得见”系统了
- 但执行层物理假设不变时，policy 仍然可能学出不理想补偿行为

### 5.3 wheel limit 有帮助，但“后限速”不足以替代分配模型本身

traction-aware v2 的经验是：

- 只在 allocator 输出之后做 wheel limit
- 不能从根本上修正 allocator 对理想纯滚的依赖

所以：

- 简单的 wheel speed scale / limit 不是最终答案

### 5.4 goal_distance 调整改变难度，但不是根因修复

从 `12m` 调到 `8m`，主任务变好了，但不代表系统已经健康。

它更像：

- 降低任务几何压力
- 让现有问题更容易被观察

而不是：

- 从根本上解决高滑移和硬挪问题

---

## 6. 当前综合诊断

把所有实验放在一起，当前最可信的综合诊断是：

### 6.1 当前反复出现的“高滑移换取部分到达”不是偶然

它是当前系统在以下条件下的自然结果：

- 任务要求到点
- reward 主要奖距离缩短
- allocator 不考虑真实 traction / slip
- 球铰可自由改变姿态和载荷

在这个条件下，policy 最容易学到：

- 用球铰和姿态换接触几何
- 用高滑移和拖拽换一点 progress

### 6.2 当前反复出现的“低滑移但走不过去”也不是偶然

只要 reward 把滑移罚得更明显，而 allocator 仍然不能提供“低滑移且高推进”的可执行路径，policy 就会倾向于：

- 保守
- 少动
- 少滑
- 低姿态消耗

于是主任务塌缩。

### 6.3 这两个失败模式其实是同一个问题的两面

它们都指向同一件事：

**当前 Stage0 的任务目标、reward 设计和 wheel allocation 物理模型还没有在“什么叫健康运动”上达成一致。**

---

## 7. 当前面临的问题清单

后续继续推进前，至少要正视以下问题：

### 7.1 任务定义层

- Stage0 到底是不是“平地稳定到点”任务？
- 如果是，“稳定”的物理含义必须补全，不能只等同于“没翻车 + 距离缩短”

### 7.2 reward 层

- 如何同时表达：
  - 到点
  - 推进效率
  - 纵滑约束
  - 结构性侧滑容许
  - 球铰余量
  - 姿态质量
  - 载荷质量

### 7.3 观测层

- 当前 policy 虽然看到了不少状态量，但还缺少更直接的“异常运输质量”语义量，例如：
  - 载荷重分配异常
  - 轮子卸载
  - 前后模块抬头 / 俯仰使用量

### 7.4 执行层

- 当前 measured-geometry allocator 还不是 traction-aware allocator
- 轮速分配模型目前没有显式吸收：
  - `Fz_i`
  - `kappa_i`
  - `alpha_i`
  - contact state

### 7.5 阶段划分层

- 当前 Stage0 还不是频繁换目标任务
- 因此“球铰是否能协同快速转向到新目标”还没有被真正测试

---

## 8. 当前最重要的结论

当前已经可以非常明确地说：

1. Stage0 不是“跑不起来”，而是“跑起来后学出的策略不健康”。  
2. 反复出现的高滑移 / 低推进 tradeoff，不是单个 reward 项调错这么简单。  
3. 旧的开环 allocator + 事后 reward 惩罚结构，正在把问题推给 policy 自己用球铰和姿态去补偿。  
4. 当前真正该继续推进的方向，必须回到：
   - 任务定义
   - reward 语义
   - 观测语义
   - 速度分配模型的物理假设

这也是为什么后续不能再把问题理解成：

- “再调一个 gate”
- “再加一个 slip penalty”
- “再跑一轮看看”

而必须系统地重整当前 RL 环境的设计逻辑。
