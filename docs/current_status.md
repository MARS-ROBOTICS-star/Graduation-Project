# 当前状态

## 当前总目标
- 在 Isaac Lab 中维持一条可复现、可继续迭代的完整车 RL 主线。
- 当前代码主线已经按用户要求彻底切到 Isaac Lab direct workflow，后续不再沿用 manager-based 架构。

## 当前阶段
- 阶段 0 的 flat baseline 仍是后续真实运行时的最短冒烟入口。
- 本轮已完成 direct 架构重构，当前进入“代码结构已切换、等待真实 Isaac Lab 环境做运行态验证”的阶段。

## 当前 RL 主线位置
- 当前唯一活跃的 Isaac Lab RL 工作区已经从旧的 `src/rl_lab/complete_car_rl_training/` 迁到：
  - `RL_Training/`
- 当前 Python 包入口：
  - `RL_Training/complete_car_rl_training/__init__.py`
- 当前训练脚本入口：
  - `RL_Training/scripts/rsl_rl/train.py`
  - `RL_Training/scripts/rsl_rl/play.py`
  - `RL_Training/scripts/list_envs.py`

## 当前代码结构
- 当前 direct task 主目录：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/`
- 当前 terrain runtime：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terrain/`
- 当前 sensor runtime：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/sensors/`
- Isaac Sim 预览和键盘控制脚本仍保留在仓库根目录：
  - `scripts/isaac_sim/`

## 本轮已确认
- RL 主线已经从 manager-based 彻底切换到 Isaac Lab direct workflow。
- 当前 direct 任务注册入口：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/__init__.py`
- 当前 direct env 主类：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
- 当前 direct 共享配置主干：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- 当前分阶段配置：
  - `stage0_flat_cfg.py`
  - `stage1_terrain_cfg.py`
  - `stage2_perception_cfg.py`
- 当前 direct Gym task id 已改为：
  - `Complete-Car-Stage0-Flat-Direct-v0`
  - `Complete-Car-Stage1-Terrain-Direct-v0`
  - `Complete-Car-Stage2-Perception-Direct-v0`
- 旧的：
  - `envs/base/complete_car_config.py`
  - `envs/base/manager_helpers.py`
  - `envs/base/complete_car_env.py`
  - `envs/baseline/complete_car_config_baseline.py`
  - `utils/terrain.py`
  已从当前主线删除，不应再作为默认入口。
- terrain 逻辑现已拆为：
  - `terrain/terrain_generator.py`
  - `terrain/terrain_runtime.py`
- sensor 逻辑现已拆为：
  - `sensors/sensor_runtime.py`
- 根目录 Isaac Sim 预览和键盘脚本已改为读取新的：
  - `tasks/direct/complete_car/assets/robot_cfg.py`
  - `tasks/direct/complete_car/terrain/terrain_generator.py`
- 论文章节：
  - `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
  已完成一次面向编译恢复的格式清理，移除了损坏的伪 Markdown / 伪公式标记，并统一改回合法 LaTeX 写法。
- `chapter03.tex` 中“前后模块线速度推导”小节已进一步按“先引入惯性坐标系 ${W}$，再从绝对位置求导推出牵连速度项”的逻辑重写。
- 当前前、后模块线速度表达式不再直接给出，而是通过：
  - 绝对位置关系
  - 乘积求导
  - 旋转坐标系中的速度变换
  顺序推出：
  - `${}^{2}\mathbf v_1={}^2\mathbf v_2+{}^2\boldsymbol\omega_2\times{}^2\mathbf p_1+{}^2\dot{\mathbf p}_1`
  - `${}^{2}\mathbf v_3={}^2\mathbf v_2+{}^2\boldsymbol\omega_2\times{}^2\mathbf p_3+{}^2\dot{\mathbf p}_3`
- 论文主入口：
  - `毕业论文/毕业论文模板/LaTeX/main.tex`
  当前已可重新通过 `latexmk -xelatex` 完整生成 `main.pdf`。

## 当前默认设计选择
- 当前默认 runnable 起点：
  - `Complete-Car-Stage0-Flat-Direct-v0`
- 当前动作语义仍保持：
  - 6 个球铰位置目标
  - 6 个车轮轮速目标
- 当前默认 observation 仍是纯本体状态；Stage2 才开启 `camera / lidar / imu`。
- direct 组织原则已经固定：
  - env 主类直接负责 reset / observation / reward / done / command / terrain runtime / sensor runtime
  - 纯函数 helper 单独放在 `rewards.py / observations.py / commands.py / terminations.py`
  - terrain 和 sensor 保持 runtime helper，不回退成 manager term

## 当前阻塞 / 风险
- 当前电脑没有 Isaac Lab 运行环境，因此本轮只能完成代码级重构与静态语法检查，不能做真实环境注册和仿真冒烟。
- 新 direct 架构尚未在真实 Isaac Lab 环境中执行：
  - `list_envs.py`
  - `train.py`
  - `play.py`
- 仓库说明文件里仍有部分旧历史条目保留着 `src/rl_lab/...` 路径，这是历史记录，不代表当前主线位置。
- 论文编译当前仍保留 2 条非阻塞参考文献警告：
  - `fang2015survey`
  - `MATSUMURA2017566`
  它们在 `reference/ref.bib` 中缺失，但不影响 `main.pdf` 生成。

## 下一步优先级
- 在有 Isaac Lab 环境的机器上，从 `RL_Training/` 目录优先执行一轮：
  - `python scripts/list_envs.py --keyword Complete-Car`
  - `python scripts/rsl_rl/train.py --task Complete-Car-Stage0-Flat-Direct-v0 --headless --num_envs 100 --max_iterations 10`
- 如果 Stage0 direct 冒烟正常，再继续：
  - `Complete-Car-Stage1-Terrain-Direct-v0`
  - `Complete-Car-Stage2-Perception-Direct-v0`
