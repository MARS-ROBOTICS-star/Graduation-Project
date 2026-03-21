# RL 环境配置相关文献阅读笔记

更新时间：2026-03-20

## 用途

本文件作为本毕设后续持续维护的文献阅读笔记，优先聚焦与 Isaac Lab RL 环境配置和训练设计直接相关的内容，包括：

- observation 设计
- action 设计
- reward 设计
- termination / reset 设计
- curriculum / sim-to-real / 训练稳定性

当前排序标准不是单纯看机构学相似度，而是综合以下三点：

- 与本课题三节完整车、六轮、两处车体连接/铰接控制问题的相似度
- 对 RL 环境配置是否有可直接迁移的参考价值
- 是否贴合当前主线阶段：先做平地基础速度跟踪 baseline，再逐步加入球铰控制、地形与感知

## 当前推荐阅读顺序

### 1. Wiberg 等，2022

文献：

- `Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning.pdf`

推荐级别：

- 最高优先级

推荐理由：

- 这是当前文献库里与本课题最接近的一篇 RL 任务论文之一，平台为六轮、双车架铰接、主动悬架的粗糙地形车辆。
- 论文把 RL 问题定义得非常完整，直接覆盖 `observation`、`action`、`reward`、`termination`。
- 其 observation 组织方式很有借鉴价值，包含车体速度、roll/pitch、铰接关节角、悬架位移、轮滑移、轮载以及局部高度图。
- 其 action 设计是连续多维控制，适合参考“轮子控制 + 结构关节控制”如何共同进入策略输出。
- 其 reward 显式考虑了 progress、姿态稳定、滑移、能耗、地面作用和危险接触，和本课题后续从基础速度跟踪走向稳定/通过性目标的方向一致。
- termination 逻辑也很清楚，包括大姿态翻滚、车体与地形危险接触、越界等，适合作为本课题后续 termination 细化的直接参考。

对本课题的直接启发：

- 第 1 阶段可先借鉴其“目标跟踪 + 姿态约束”的 reward 组织方式。
- 第 2 阶段把球铰纳入控制时，可借鉴其多自由度 action 结构。
- 第 3 阶段加入地形后，可参考其局部高度图和轮滑移项。

### 2. Wiberg 等，2024

文献：

- `Wiberg 等 - 2024 - Sim-to-real transfer of active suspension control using deep reinforcement learning.pdf`

推荐级别：

- 非常高

推荐理由：

- 与 2022 论文平台高度一致，仍然是六轮、双铰接、主动悬架重型地形车辆，因此形态相似度极高。
- 这篇更突出训练工程问题，讨论了 observation noise、action delays、previous action、动作平滑惩罚和 sim-to-real。
- 对当前本课题非常有价值，因为我们已经不是“能否启动训练”的问题，而是“如何让训练更健康、更稳定、更可信”。
- 文中指出如果不约束动作变化，策略容易学出 simulation 里好看、现实里失效的 bang-bang 控制，这一点对后续球铰和车轮联控尤其重要。

对本课题的直接启发：************************

- 后续可把 `previous_action` 作为 observation 候选项。
- 若出现动作抖动或不连续，可借鉴动作变化惩罚。
- 如果后面做 sim-to-real，这篇应作为核心参考文献之一。

### 3. Bauer 等，2025

文献：

- `Bauer 等 - 2025 - Reinforcement learning for robust control of individual wheel drive mobile robots with passive artic.pdf`

推荐级别：

- 很高

推荐理由：

- 平台虽然是四轮而不是六轮，且是被动铰接转向，但“轮式 + 铰接 + RL 控制 + 安全角约束”这一组合与本课题的环境设计高度相关。
- 该文对 env 要素定义很直接：state 包含广义速度、命令速度、轮速、铰接角；action 为轮角速度；termination 使用最大铰接角。
- 论文场景虽然偏倒车防 jackknife，但其“如何把铰接安全约束显式写进任务设计”的思路很值得借鉴。
- 文中还使用了 TD3 + RNN，说明在存在时序依赖和被动关节耦合时，记忆机制可能比纯瞬时状态更有效。

对本课题的直接启发：

- 后续球铰或车体关节加入控制后，可参考如何引入“关节安全边界触发终止”。
- 若单步 observation 不足以表达关节耦合动态，可考虑 history 或 RNN 思路。

### 4. Xu 等，2024

文献：

- `Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain.pdf`

推荐级别：

- 高

推荐理由：

- 虽然平台是四轮，不如 Wiberg 系列和 Bauer 那么贴近本课题形态，但其 RL 问题定义非常适合做环境模板参考。
- 该文使用 PPO + curriculum，任务定义清晰：state 包含目标方向、车速和地形编码；action 是期望速度与转向；reward 由 progress、rollover penalty、timeout penalty 组成。
- 这篇很适合作为“从当前平地 baseline 向复杂地形 RL 过渡”的桥梁文献。

对本课题的直接启发：

- 第 1 阶段可以借鉴其简洁任务形式：先做速度/方向控制，不急于把结构控制全塞进来。
- 第 3 阶段加入地形时，可借鉴其课程学习组织方式。

### 5. Salvi 等，2022

文献：

- `Salvi 等 - 2022 - Stabilization of vertical motion of a vehicle on bumpy terrain using deep reinforcement learning.pdf`

推荐级别：

- 中高

推荐理由：

- 这篇不是多节车，也不是完整越障车体控制，但其 RL 任务定义非常清楚。
- 其 observation 使用车速、垂向加速度和地形预瞄；action 为命令速度；reward 通过地形预瞄动态调权。
- 这类“基于预瞄信息动态调 reward”的思路，适合本课题后续把视觉/地形感知接入时参考。

对本课题的直接启发：

- 当前阶段不宜直接照搬，因为它过于聚焦垂向舒适/稳定，而不是完整车多体耦合运动。
- 但未来若加入地形预瞄或前视感知，这篇可以作为 reward shaping 参考。

### 6. Sartoretti 等，2019

文献：

- `Sartoretti 等 - 2019 - Distributed learning of decentralized control policies for articulated mobile robots.pdf`

推荐级别：

- 中等

推荐理由：

- 论文对象是蛇形和六足，不是轮式车，因此平台相似度不高。
- 但它研究的是 articulated robot 的 decentralized RL，对“如何把一个高自由度系统拆成局部控制单元”很有启发。
- 如果后续把球铰、车体段、或局部结构控制拆开看，这篇对局部 state、局部 action、shared reward 的组织方式很有价值。

对本课题的直接启发：

- 更适合第 2 阶段及以后参考，不是当前平地轮式 baseline 的主文献。

### 7. Dynamics Modeling and Control of Multi-Segment Passively-Articulated Autonomous Wheeled Vehicles

文献：

- `Dynamics Modeling and Control of Multi-Segment Passively-Articulated Autonomous Wheeled Vehicles.pdf`

推荐级别：

- 中等

推荐理由：

- 这篇不是 RL 论文，但平台是 multi-segment、passively-articulated、wheeled vehicle，和本课题“多车体段耦合”这一点较接近。
- 它更适合帮助理解多节车体动力学、段间作用力以及基于本体反馈的控制思路。
- 对 env cfg 的直接帮助小于前几篇，但对决定 observation 里是否加入段间力、关节状态、失稳先兆有参考价值。

### 8. Mehta 等，2023

文献：

- `Mehta 等 - 2023 - Actively articulated wheeled architectures for autonomous ground vehicles - opportunities and challe.pdf`

推荐级别：

- 中等偏后

推荐理由：

- 这是主动铰接轮式平台的综述，更偏 architecture、建模、性能指标和控制挑战分析。
- 它对 thesis 的动机、背景、性能指标定义很有价值，但对当前要写的 RL observation/reward/action/termination 没有前几篇直接。

对本课题的直接启发：

- 适合服务于“为什么采用主动铰接/球铰类结构”和“实验指标如何组织”的论文写作部分。

### 9. Wang 等，2021

文献：

- `Wang 等 - 2021 - Rough terrain navigation using divergence constrained model-based reinforcement learning.pdf`

推荐级别：

- 当前阶段靠后

推荐理由：

- 这篇更偏 model-based RL 和轨迹优化/导航层。
- 它讨论的是 rough terrain 上如何处理模型不确定性和长时域规划，而不是当前我们最关心的低层 wheel/joint continuous control env 设计。
- 因此可作为后续高层局部规划或 model-based 扩展的参考，但不是当前阶段主文献。

## 当前不建议优先精读的文献组

### 1. 感知/地形分类/多传感器综述类

包括但不限于：

- `Arafin 等 - 2025 - Advances and trends in terrain classification methods for off-road perception.pdf`
- `Borges 等 - 2022 - A survey on terrain traversability analysis for autonomous ground vehicles methods, sensors, and ch.pdf`
- `Hu 等 - 2020 - A survey on multi-sensor fusion based obstacle detection for intelligent ground vehicles in off-road.pdf`
- `Yeong 等 - 2020 - A review of multi-sensor fusion system for large heavy vehicles off road in industrial environments.pdf`
- `Nampoothiri 等 - 2021 - Recent developments in terrain identification, classification, parameter estimation for the navigati.pdf`
- `Guastella和Muscato - 2021 - Learning-based methods of perception and navigation for ground vehicles in unstructured environments.pdf`

原因：

- 这些文献更适合后续感知增强阶段，不是当前第 1 阶段低维本体状态 baseline 的主文献。

### 2. 3-RRR 机构学/运动学/动力学文献

包括但不限于：

- `Staicu - 2007 - Dynamics of a 3-RRR Spherical Parallel Mechanism Based on Principle of Virtual Powers.pdf`
- `Tao和An - 2013 - Interference analysis and workspace optimization of 3-RRR spherical parallel mechanism.pdf`
- `Li 等 - 2025 - Closed-form forward kinematics of a novel class of 3-RRR spherical parallel mechanisms with coplanar.pdf`
- `Wu和Bai - 2019 - Design and kinematic analysis of a 3-RRR spherical parallel manipulator reconfigured with four–bar l.pdf`

原因：

- 这类文献对本课题的机构学论证、简化合理性说明、球铰等效建模背景有价值。
- 但它们对当前 RL 环境配置和训练主线的直接帮助明显弱于前述 RL 文献。

## 当前建议的精读顺序

如果只选 3 篇先精读，建议顺序为：

1. `Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning.pdf`
2. `Wiberg 等 - 2024 - Sim-to-real transfer of active suspension control using deep reinforcement learning.pdf`
3. `Bauer 等 - 2025 - Reinforcement learning for robust control of individual wheel drive mobile robots with passive artic.pdf`

如果完成这 3 篇，再读：

4. `Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain.pdf`
5. `Salvi 等 - 2022 - Stabilization of vertical motion of a vehicle on bumpy terrain using deep reinforcement learning.pdf`




