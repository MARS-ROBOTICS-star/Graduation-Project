# 项目文件地图

本文档用于把当前仓库中的主要文件和目录按职责归类，减少后续在聊天记录里重复解释“哪个文件是主线、哪个文件是资料、哪个文件是派生产物”。

## 1. 启动必读

- `AGENTS.md`
  - 仓库级最高优先级规则，定义项目目标、角色边界、执行主线和记忆文件维护规则。
- `docs/current_status.md`
  - 当前阶段、阻塞点、下一步优先事项和默认方案。
- `docs/conversation_history.md`
  - 需要跨会话继承的结论。
- `logs/daily_work_log.md`
  - 按日期记录已经完成的工作。
- `README.md`
  - 顶层仓库概览和当前主线入口。

## 2. 根目录按职责划分

- `src/`
  - 当前唯一活跃的 RL 代码工作区入口。
- `scripts/`
  - Isaac Sim 验证、资产修复、文献处理等辅助脚本。
- `USD/`
  - 当前使用的 USD 入口文件和子层配置。
- `docs/`
  - 项目状态、长期结论、文献库和说明文档。
- `results/`
  - 仿真验证、键盘测试等输出结果。
- `refs/`
  - 本地知识库和外部手册镜像。
- `complete_car_alternative/`
  - 机器人导出包之一，偏早期/替代版本。
- `complete_car_final/`
  - 机器人导出包之一，偏收敛/对照版本。
- `毕业论文/`
  - 论文模板、章节正文、编译输出。
- `Drawing/`
  - 图纸、示意图、PPT 素材。
- `IK_iteration.md`
  - 逆运动学符号推导的 Markdown 导出。
- `IK_iteration.mlx`
  - MATLAB Live Script 版逆运动学推导主文件。
- `IK_iteration.asv`
  - MATLAB 自动保存文件，属于派生产物。
- `literature_note_skill.md`
  - 文献阅读 skill 的仓库内草稿源。
- `.venv-mineru/`
  - 文献转换相关的本地虚拟环境。

## 3. 主线代码工作区

主线目录：

- `src/rl_lab/complete_car_rl_training/`

该目录是当前唯一应该持续演化的 Isaac Lab RL 项目，内部再分为：

- `complete_car_rl_training/`
  - Python 包根目录。
- `complete_car_rl_training/tasks/`
  - 环境定义、动作、观测、reward、termination 等主线任务代码。
- `scripts/`
  - `train.py`、`play.py`、`zero_agent.py`、`random_agent.py`、`tensorboard_export.py` 等运行入口。
- `docs/`
  - 训练日志阅读说明等项目内文档。
- `skills/isaac-rl-run-diagnosis/`
  - 训练日志诊断 skill。
- `IK_model.py`、`IK_model_true.py`
  - 与球铰逆运动学相关的 Python 推导/验证脚本。
- `test_ik_keyboard.py`
  - 当前较新的键盘验证脚本，走“姿态目标 -> IK -> joint target -> articulation controller”链路。

结论：

- 只要是 RL baseline、环境定义、训练脚本、日志导出相关问题，默认先看这里。
- 不应再把新的 RL 主线代码分散到根目录或其他旧工作区。

## 4. Isaac Sim 与资产相关目录

### 4.1 `USD/`

当前包含：

- `USD/complete_car.usd`
  - 当前主线机器人 USD。
- `USD/complete_car_equivlent.usd`
  - 等效模型相关 USD。
- `USD/Spherical_Parallel_test.usd`
  - 球面并联机构测试资产。
- `USD/default_scene.usd`
  - 场景相关 USD。
- `USD/configuration/`
  - `complete_car_*` 与 `default_scene_*` 的子层配置文件。

### 4.2 `scripts/isaac_sim/`

功能类型可分为：

- 键盘控制与遥操作
  - `control_keyboard.py`
  - `rover_control.py`
- 资产检查与依赖检查
  - `check_isaaclab_asset.py`
  - `inspect_usd_dependencies.py`
- USD 修复与结构整理
  - `repair_complete_car_usd.py`
  - `repair_complete_car_usd_v2.py`
  - `repair_complete_car_usd_v3.py`
  - `repair_complete_car_usd_v4.py`
  - `align_complete_car_structure_to_equivalent.py`
  - `add_spm_base_reference_frames.py`
  - `add_wheel_friction_material.py`
- 传感器验证
  - `validate_sensors.py`

### 4.3 `complete_car_alternative/` 与 `complete_car_final/`

这两个目录是机器人包级导出产物，包含：

- `urdf/`
- `meshes/`
- `config/`
- `launch/`
- `package.xml`
- `CMakeLists.txt`

用途：

- 作为机器人资产来源、对照版本和导出记录。
- 不是当前 RL 环境主线代码位置。

## 5. 文献工作区

主目录：

- `docs/literature/`

职责分层：

- 根目录 PDF
  - 本地原始论文语料库。
- `mineru_output/`
  - MinerU 转换结果，每篇文献一个目录。
- `rl_training_strategy_pdfs_2026-03-23/`
  - 按主题整理出的 RL 训练策略相关子集。
- `README.md`
  - 文献目录使用说明。

当前值得优先关注的已整理文献包括：

- `Wiberg 等 - 2022`
- `Xu 等 - 2024`
- `Ha 等 - 2025`

其中 `Ha 等 - 2025` 已新增：

- 原始 PDF
- `mineru_output/.../auto/reading_notes.md`

## 6. 论文工作区

主目录：

- `毕业论文/毕业论文模板/LaTeX/`

内部可再分为：

- `chapters/`
  - 章节正文。当前 `chapter03.tex` 已写入球铰逆运动学推导首版。
- `reference/ref.bib`
  - 论文参考文献库。
- `main.tex`
  - 主文档入口。
- `DLUT-thesis.cls`、`GBT7714-2005NLang.bst`
  - 模板类文件。

需要注意：

- 该目录内同时混有大量编译产物，如 `.aux`、`.log`、`.bbl`、`.blg`、`.xdv`、`main.pdf`。
- 真正应长期编辑的核心源文件是 `chapters/*.tex`、`reference/ref.bib`、`main.tex`。

## 7. 推导与图纸

### 7.1 逆运动学推导

- `IK_iteration.mlx`
  - MATLAB Live Script 主文件。
- `IK_iteration.md`
  - 导出的可读推导版本。
- `IK_iteration.asv`
  - 自动保存副本。

### 7.2 图纸与素材

- `Drawing/3DOF-ModifieIntegrated.SAT`
- `Drawing/3DOF-ModifieIntegrated.svg`
- `Drawing/模型图片.pptx`
- `Drawing/运动学模型.svg`

这些文件属于机构设计、汇报和论文配图素材，不属于 RL 代码主线。

## 8. 结果输出目录

主目录：

- `results/ik_keyboard_logs/`
  - 键盘测试 CSV 日志。
- `results/sensor_validation/`
  - 相机、深度、LiDAR、IMU 的验证输出。

用途：

- 保存实验结果和验证证据。
- 应视为结果区，而不是源码区。

## 9. 本地参考知识库

- `refs/isaac_kb/isaacsim_5.1_full_manual.md`
- `refs/isaac_kb/isaaclab_2.3.0_full_manual.md`
- `refs/isaac_kb/README.md`

规则：

- 遇到 Isaac Sim / Isaac Lab 用法问题，优先先查这里，再考虑外部检索。

## 10. 当前最常用入口文件

如果你的问题是下面这些，优先打开对应文件：

- 当前项目规则和边界
  - `AGENTS.md`
- 当前阶段和下一步
  - `docs/current_status.md`
- 长期继承结论
  - `docs/conversation_history.md`
- RL 环境主配置
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- RL 训练脚本
  - `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`
- 旧版键盘控车脚本
  - `scripts/isaac_sim/control_keyboard.py`
- 当前 IK 键盘验证脚本
  - `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- 论文逆运动学章节
  - `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`

## 11. 对后续整理的直接建议

基于当前实际结构，可以把仓库内容理解为五条并行工作线：

- RL 主线
  - `src/rl_lab/complete_car_rl_training/`
- 资产与仿真验证线
  - `USD/`、`scripts/isaac_sim/`、`complete_car_*`
- 文献线
  - `docs/literature/`
- 论文线
  - `毕业论文/`
- 机构推导与配图线
  - `IK_iteration.*`、`Drawing/`

如果以后再做“物理上的目录重组”，也应围绕这五条线来收敛，而不是按文件后缀机械分类。
