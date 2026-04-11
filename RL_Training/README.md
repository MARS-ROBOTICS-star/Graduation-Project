# Complete Car RL Training

`RL_Training/` 现已被原地重构为新的 Isaac Lab direct workflow 训练工程。

## 项目目标

- 使用一个共享 direct 环境主类：
  - `source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- 使用一个共享基础配置主干：
  - `base/complete_car_cfg.py`
- 用 3 个阶段配置派生 3 个任务：
  - `CompleteCar-Stage0`
  - `CompleteCar-Stage1`
  - `CompleteCar-Stage2`

## 目录概览

```text
RL_Training/
├── README.md
├── pyproject.toml
├── scripts/
│   ├── train.py
│   └── play.py
└── source/
    └── complete_car_lab/
        ├── config/
        │   └── extension.toml
        ├── setup.py
        └── complete_car_lab/
            └── tasks/direct/complete_car/
                ├── base/
                ├── baseline/
                ├── environment_adaptive/
                ├── mdp/
                ├── terrain/
                ├── sensors/
                ├── kinematics/
                │   ├── ik_solver.py
                │   ├── fk_solver.py
                │   ├── legacy_ik/
                │   └── legacy_fk/
                ├── utils/
                │   ├── list_envs.py
                │   ├── random_agent.py
                │   ├── zero_agent.py
                │   ├── export_training_stage.py
                │   ├── tensorboard_export.py
                │   └── validate_wheel_speed_allocator.py
                └── rsl_rl/
```

## 安装

在 Isaac Lab Python 环境中执行：

```bash
cd /home/ubuntu/Graduation-Project/RL_Training
pip install -e source/complete_car_lab
```

## 训练

```bash
cd /home/ubuntu/Graduation-Project/RL_Training
python scripts/train.py --task CompleteCar-Stage0 --headless
python scripts/train.py --task CompleteCar-Stage1 --headless
python scripts/train.py --task CompleteCar-Stage2 --headless
```

## 回放

```bash
cd /home/ubuntu/Graduation-Project/RL_Training
python scripts/play.py --task CompleteCar-Stage0 --checkpoint /path/to/model.pt
```

`train.py` 和 `play.py` 会优先加载 `source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/`
里的本地 PPO 本体，不再依赖外部环境里碰巧安装的 `rsl_rl`。

## 辅助工具

安装扩展后，可通过模块方式调用迁入 `complete_car/utils/` 的辅助脚本，例如：

```bash
cd /home/ubuntu/Graduation-Project/RL_Training
python -m complete_car_lab.tasks.direct.complete_car.utils.list_envs
python -m complete_car_lab.tasks.direct.complete_car.utils.validate_wheel_speed_allocator
```

## 当前结构原则

- 任务注册只在 `tasks/direct/complete_car/__init__.py` 完成。
- Stage 差异只通过配置继承绑定，不在 `env.py` 里堆大量阶段 if-else。
- `env.py` 只做 orchestration，动作、观测、奖励、终止、重置、随机化、terrain、sensor、kinematics 全部拆到独立模块。
- 旧 `IK/FK` 资料不再放在 `RL_Training/utils/`，而是统一收口到 `tasks/direct/complete_car/kinematics/`。
- 旧 `rsl_rl` 本体不再放在 `RL_Training/rsl_rl/`，而是统一收口到 `tasks/direct/complete_car/rsl_rl/`。
