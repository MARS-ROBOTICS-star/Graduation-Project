# Xu 等 2024 阅读笔记

文献：`Reinforcement Learning for Wheeled Mobility on Vertically Challenging Terrain`

阅读目标：

- 提炼 RL 环境设计：`observation`、`action`、`reward`、`termination`、`curriculum`
- 为后续与 `Wiberg 2022` 等文献做横向对比做准备

阅读状态：

- 已完成一轮围绕 RL 环境设计的问答式梳理
- 当前重点是提炼其任务组织逻辑，而不是复述全文

## 1. 论文的任务是什么

### 1.1 任务定义

这篇论文的高层目标是让 wheeled robot 获得在 vertically challenging terrain 上的越野机动能力。

如果落到 RL 任务定义，更准确地说是：

- 让车辆在具有明显竖向挑战的非结构化地形上朝目标持续前进
- 避免翻滚或俯仰过大
- 避免被卡住
- 在时间限制内完成目标到达

### 1.2 任务本质

这篇论文的任务更接近：

- `goal-directed mobility`
- 或者说，面向目标的 traversability / mobility task

它不是：

- 纯姿态稳定任务
- 纯速度命令跟踪任务
- 也不是底层执行器直接控制任务

目标位置/方向是任务锚点，但论文真正关心的是车辆能否在困难地形上成功移动过去。

## 2. Action 设计

### 2.1 Policy 输出什么

RL policy 输出的是高层运动命令：

- 期望线速度
- 期望转向角

底层不直接由 policy 输出油门与转向执行量，而是：

- 通过 PID 控制器去实现期望的线速度和转向角

### 2.2 这一设计的含义

这篇论文采用的是：

- 低维
- 高层
- 接近驾驶命令的 action 形式

其优点是：

- 学习空间更小
- 不需要策略直接承担执行器层面的稳定控制
- 更适合把 RL 聚焦在 mobility / traversability 决策层

### 2.3 与 Wiberg 2022 的差异

- `Wiberg 2022`：高维、底层、多执行器直接控制
- `Xu 2024`：低维、高层，底层由 PID 兜住

这意味着两篇论文虽然都研究 rough / challenging terrain mobility，但控制层级明显不同。

## 3. Observation 设计

### 3.1 三类 observation

这篇论文的 observation 可以整理为：

1. 地形信息
- 以车辆为中心、对齐并裁剪的局部高程图
- 再通过 `SWAE` 编码为低维 latent representation

2. 本体状态
- 当前车辆速度

3. 任务相关信息
- 车辆当前航向与目标方向之间的角度差

### 3.2 Observation 背后的逻辑

其 observation 逻辑可概括为：

`局部地形几何 + 少量本体速度信息 + 朝向目标的方向误差`

这说明作者将大量复杂的底层车辆状态从输入中拿掉，保留了：

- 前方地形几何
- 当前运动快慢
- 是否朝着目标方向前进

### 3.3 与 Wiberg 2022 的差异

- `Wiberg 2022` 提供了大量本体动力学与轮地接触信息
- `Xu 2024` 的 observation 更简洁，更偏向高层 mobility policy 所需的信息

## 4. Reward 设计

### 4.1 Reward 结构

论文 reward 只有三项：

- `R_progress`
- `R_rollover`
- `R_timeout`

### 4.2 各项功能

1. `R_progress`
- 鼓励车辆朝目标前进
- 如果在短时间内几乎没有推进，会额外惩罚
- 这实际上兼顾了“防止卡住”

2. `R_rollover`
- 惩罚过大的 roll 与 pitch
- 其作用是防止车辆在竖向挑战地形上姿态失稳

3. `R_timeout`
- 若在时间限制内未到达目标，则在 episode 末端施加惩罚
- 惩罚不仅包含固定项，还与剩余距离相关

### 4.3 Reward 设计特点

这篇论文的 reward 极简，核心只抓三件事：

- 有没有向目标推进
- 有没有姿态失稳
- 有没有在规定时间内完成

相比 `Wiberg 2022`，它没有显式加入：

- 能耗
- 滑移
- 轮载分布
- 环境友好性
- 轮胎侧壁接触等多目标约束

### 4.4 为什么可以这么简化

主要原因包括：

1. 控制层级更高
- policy 只输出高层速度和转向命令
- 底层 PID 已经处理了部分执行稳定性问题

2. 平台复杂度更低
- 四轮平台的控制复杂度远低于多执行器大型林地车

3. 论文想证明的科学问题更聚焦
- 重点是证明 wheeled robot 在 vertically challenging terrain 上具有可学习的 mobility capability
- 而不是同时论证低滑移、低能耗、轮载优化等多目标性能

### 4.5 与 Wiberg 2022 的 reward 风格对比

- `Wiberg 2022`：多目标、行为品质型 reward
- `Xu 2024`：极简、任务导向型 reward

这说明 rough-terrain RL 的 reward 复杂度，应与任务层级和论文要证明的问题保持一致。

## 5. Episode 与 Termination 理解

### 5.1 Episode 结束

从文中明确可见的 episode 结束条件包括：

- 到达目标
- 到达时间上限 `T`

### 5.2 失败/受罚逻辑

- 若短时间推进不足，则在 `R_progress` 中受罚
- 若 roll / pitch 过大，则在 `R_rollover` 中持续受罚
- 若达到时间上限仍未到达目标，则在 episode 末端施加 `R_timeout`

### 5.3 这一设计的特点

这篇论文并没有像 `Wiberg 2022` 那样强调大量硬终止条件。

更准确地说：

- “卡住”和“姿态大”主要通过 reward shaping 处理
- 明确写出的硬边界主要是 goal reached 或 horizon reached

因此它相比 `Wiberg 2022` 更宽松，更愿意让策略在 episode 内继续尝试，而不是很早判死。

## 6. Curriculum 设计

### 6.1 Curriculum 是怎么做的

这篇论文不是通过人工设计多套任务 lesson 来推进，而是：

- 对地形高程图做插值
- 从平坦地形 `I0` 逐步插值过渡到崎岖地形 `IN`

因此它的 curriculum 本质是：

`terrain difficulty interpolation`

### 6.2 调的是什么难度

它主要调的是：

- 地形的竖向挑战程度
- 包括地形起伏、岩石/凸起、坡度和崎岖程度

### 6.3 与 Wiberg 2022 的不同

- `Wiberg 2022` 的 curriculum 是多维的：同时调地形、障碍、目标设置、步长等
- `Xu 2024` 的 curriculum 更单一、更连续：聚焦把地形从易到难平滑提升

可以概括为：

- `Wiberg`：复杂任务分阶段教学
- `Xu`：围绕单一核心任务逐步抬高环境难度

## 7. 当前提炼出的文献卡片

- `observation`：局部高程图编码 + 当前速度 + 目标方向误差
- `action`：期望线速度 + 期望转向角，由 PID 执行到底层
- `reward`：进度奖励 + 翻滚惩罚 + 超时惩罚
- `episode/termination`：到达目标或到达时间上限结束，卡住和姿态风险主要通过 reward shaping 处理
- `curriculum`：通过高程图插值连续提高地形竖向挑战难度

## 8. 对本课题的启发

### 8.1 值得保留的思想

- 可以把 rough-terrain 问题先压缩成一个较简洁的 goal-directed mobility task
- reward 不一定一开始就做成多目标重型结构
- curriculum 可以先从单一维度地形难度推进，而不是一开始同时改很多东西

### 8.2 与本课题存在的边界

- 这篇论文采用高层 action，而本课题后续可能需要轮子 + 球铰联合控制
- 这篇论文 observation 较轻，没有涉及结构关节状态、轮地接触质量等信息
- 因此它更适合作为“任务简化和课程设计”参考，而不是多执行器联合控制的直接模板

## 9. 当前阅读结论

这篇论文最重要的价值不是告诉我们 rough-terrain RL 一定要怎么做，而是提供了一种更轻、更聚焦的设计路径：

- 用简洁 observation 与高层 action 建立可训练的 mobility task
- 用极简 reward 直接围绕“前进、别翻、别超时”组织学习目标
- 用单一维度的 terrain interpolation curriculum 持续提高地形难度

它非常适合后续与 `Wiberg 2022` 做横向对比，帮助判断：

- 什么时候应采用极简任务定义
- 什么时候必须进入多执行器、多目标的复杂控制建模
