# Isaac Lab 训练项目使用指南

本文档对应当前仓库中唯一保留的 Isaac Lab 训练项目：

- `src/rl_lab/complete_car_rl_training/`

该目录已经从原始模板整理为单层项目结构，不再保留重复的 `source/complete_car_rl_training/...` 壳层。

## 1. 当前项目结构

核心目录如下：

- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/`
  - Python 包入口与任务实现
- `src/rl_lab/complete_car_rl_training/scripts/`
  - 环境枚举、零动作测试、随机动作测试、训练、回放脚本
- `src/rl_lab/complete_car_rl_training/config/extension.toml`
  - Isaac Lab 扩展元数据
- `src/rl_lab/complete_car_rl_training/setup.py`
  - Python 安装入口
- `src/rl_lab/complete_car_rl_training/pyproject.toml`
  - 本地工具配置与构建配置

## 2. 当前关键文件

- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/__init__.py`
  - 包入口，只负责导入任务注册
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/__init__.py`
  - Gym 任务注册
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
  - manager-based 环境配置
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/agents/rsl_rl_ppo_cfg.py`
  - PPO 配置
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/mdp/rewards.py`
  - 自定义奖励函数

## 3. 当前任务状态

- 当前任务 ID：`Complete-Car-Rl-Training-v0`
- 当前日志实验名：`complete_car_rl_training`
- 当前环境采用 manager-based workflow
- 当前动作设计为 12 维：
  - 6 维球铰位置动作
  - 6 维车轮速度动作

## 4. 安装方式

进入项目目录：

```bash
cd /home/ubuntu/Graduation-Project/src/rl_lab/complete_car_rl_training
```

在已激活的 `env_isaacLab` conda 环境中安装项目包：

```bash
python -m pip install -e . --no-build-isolation
```

说明：

- 当前安装入口已经改为项目根目录。
- 不再使用旧的 `pip install -e source/complete_car_rl_training`。
- 若首次在无交互终端中启动 Isaac Sim / Isaac Lab，先执行：

```bash
export OMNI_KIT_ACCEPT_EULA=YES
```

## 5. 常用命令

列出当前项目注册的环境：

```bash
python scripts/list_envs.py --keyword Complete-Car
```

零动作验证：

```bash
python scripts/zero_agent.py --task Complete-Car-Rl-Training-v0 --num_envs 32
```

随机动作验证：

```bash
python scripts/random_agent.py --task Complete-Car-Rl-Training-v0 --num_envs 32
```

第一次训练冒烟测试：

```bash
python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0  --num_envs 100 
```

训练结果回放：

```bash
python scripts/rsl_rl/play.py --task Complete-Car-Rl-Training-v0 --device cpu
```

## 6. 当前建议工作顺序

1. 先执行 `python -m pip install -e . --no-build-isolation`
2. 用 `scripts/list_envs.py` 确认任务已注册
3. 用 `scripts/zero_agent.py` 验证环境能创建和 reset
4. 用 `scripts/random_agent.py` 验证环境能持续 step
5. 再启动第一次 `train.py --headless`

## 7. 当前整理结论

- 训练项目已经整理为单层结构，后续开发统一在 `src/rl_lab/complete_car_rl_training/` 下进行
- 包路径已经统一到 `complete_car_rl_training/...`
- 当前默认启动方式是在激活的 `env_isaacLab` 环境中直接运行 `python scripts/...`
- 项目包需要先执行一次 `python -m pip install -e . --no-build-isolation`
- 旧模板的 UI 示例、嵌套 `.git`、`.vscode` 和重复壳层已移除
