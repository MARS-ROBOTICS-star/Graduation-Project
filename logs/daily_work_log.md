# 每日工作日志

## 2026-04-03

已完成：
- 针对用户提出的“训练时为什么像加载了好几张地图”，重新检查当前 RL 任务的真实地形导入链路：
  - `Complete-Car-Rl-Training-v0`
  - `complete_car_stage1_env.py`
  - `complete_car_rl_training_env_cfg.py`
  - `stage1_terrain.py`
- 代码层确认当前训练环境的地形导入逻辑为：
  - 先删除 `TerrainImporterCfg(terrain_type="plane")` 自动生成的默认 plane
  - 再把整张 `stage1` 高度图转换得到的单个 trimesh 通过 `import_mesh("stage1", ...)` 只导入一次
  - 再通过 `configure_env_origins(...)` 给不同并行环境分配出生点
- 直接用纯 Python 方式复核 `stage1_terrain.py` 的数据规模，确认当前训练地形生成结果是单张完整大地图，而不是按 env 拆成多张：
  - `height_field_raw.shape == (2100, 1300)`
  - `env_origins.shape == (20, 10, 3)`
  - `vertices.shape == (2730000, 3)`
  - `faces.shape == (5453202, 3)`
  - `terrain_type_unique == [0, 1, 2, 3, 4]`
- 新增训练环境 stage 导出脚本：
  - `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
  - 用途是直接实例化真实训练任务，并尝试把 live RL stage 保存成 USD，同时导出 prim tree 文本
- 根据用户后续提供的 `isaaclab_2026-04-03_11-39-39.log` 与配套 `kit_20260403_113931.log` 继续排查：
  - 日志显示当前启动的是 `export_training_stage.py`，不是 `scripts/rsl_rl/train.py`
  - `Complete-Car-Rl-Training-v0` 的环境构建实际上已经成功完成，机器人 articulation、动作项和观测项都已初始化
  - Kit 日志末尾为 `SimulationApp.close` 正常关闭，没有出现任务包自身的 Python traceback
- 进一步确认这次调用里 `--save-usd` 传入的是目录 `/home/ubuntu/Graduation-Project/results/`，不是具体 USD 文件名。
- 已修改 `export_training_stage.py`：
  - 若 `--save-usd` 是已存在目录，立即抛出清晰 `ValueError`
  - 若 `--save-usd` 不以 `.usd` 或 `.usda` 结尾，也立即报错
- 已执行 `python3 -m py_compile src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`，静态检查通过。
- 在用户随后成功导出 `results/training_stage_num_envs10.usda` 后，直接检查导出的 prim tree：
  - `/World/terrain` 下只有 1 张真实训练地形：
    - `/World/terrain/stage1/mesh`
  - 但每个 `/World/envs/env_i/Robot` 下都存在：
    - `terrain_preview/mix/terrain_surface`
    - `terrain_preview/mix/tile_base`
  - 因而“像有好几张地图”的直接来源不是训练 terrain importer 重复导入多张 `stage1`，而是机器人资产里残留的 preview 地形被每个并行环境复制。
- 按用户要求新增 `scripts/isaac_sim/remove_complete_car_terrain_preview.py`，并对 `USD/complete_car.usd` 执行清理：
  - 自动创建备份 `USD/complete_car.usd.terrain_preview_cleanup.bak`
  - 删除 `/World/terrain_preview` 子树
- 删除后重新打开 `USD/complete_car.usd` 验证：
  - `/World/terrain_preview` 已返回 `IsValid() == False`
  - 当前顶层 prim 只剩 `/World`、`/Render`、`/physicsScene`
- 实际在本机执行：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
  - `python -u scripts/export_training_stage.py --task Complete-Car-Rl-Training-v0 --num_envs 10 --steps 0 --headless --device cpu --save-usd ...`
- 实测结果：
  - 脚本可以进入 Isaac Lab scene creation
  - 但在当前无 NVIDIA driver / 无可用 CUDA 的环境里，进程会在 `gym.make(...)` 场景创建完成后提前退出，没有继续走到脚本自己的 `env.reset()` 与 `save_stage()` 逻辑
  - 因此本轮未能在本机生成真实训练环境的 stage USD 文件

修改文件：
- `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
- `scripts/isaac_sim/remove_complete_car_terrain_preview.py`
- `USD/complete_car.usd`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前训练代码路径本身并没有“按并行环境复制多张完整 stage1 地图”的显式逻辑；它导入的是 1 张全局 `stage1` mesh，再给各 env 分配不同 origin。
- 用户这次提供的日志并不支持“训练环境没拉起来”这个判断；从日志看，环境已经创建成功，关闭点更接近导出脚本参数或脚本执行流程，而不是任务配置本身崩溃。
- 本次最明确的问题是 `--save-usd` 目标写成了目录，后续必须改成具体文件名。
- 当前已经确认并修复：训练导出中每个 `env_i/Robot` 下反复出现的假地形来自 `complete_car.usd` 的 `/World/terrain_preview` 残留，而不是训练 terrain importer 自己重复导入多张 stage1 地图。
- 若窗口里看起来像有多张地图，后续应优先从：
  - `/World/terrain` 下是否存在多个 terrain prim
  - `/World/envs/env_*` 的多环境复制
  - 默认 plane / debug 可视化
  这三类来源排查，而不是先假设 `stage1_terrain.py` 生成了多张地图。
- 当前仓库已经有可复用的训练 stage 导出脚本，但真正导出 live RL stage 仍需放到有正常 GPU/驱动的 Isaac Lab 会话中执行。

下一步：
- 在可正常使用 `cuda:0` 的 Isaac Lab 环境中重新导出一次 `training_stage_num_envs10.usda`，确认每个 `env_i/Robot` 下已不再出现 `terrain_preview` 子树；若仍有异常，再继续排查 `PhysicsScene`、远端传感器引用和训练场景自身的多环境可视化。

## 2026-04-02

已完成：
- 按用户要求实际执行 `preview_stage1_terrain.py`，尝试在当前机器上通过 `--headless --device cpu --frames 1 --save-usd` 导出 preview stage 的 USD 文件，并额外保存完整日志到：
  - `results/preview_save.log`
  - `results/preview_save_unbuffered.log`
- 结果确认：
  - 当前 Isaac Sim 会话能启动到 headless 模式
  - 但在这台无可用 CUDA / 无图形显示环境中，`--save-usd` 仍未实际生成 `results/stage1_preview.usda`
- 直接读取 `USD/complete_car.usd`，导出 prim 树到：
  - `results/complete_car_usd_tree.txt`
- 基于导出的 prim 树确认 `complete_car.usd` 的主要结构：
  - `/World/complete_car_alternative` 为机器人主根
  - 机体/轮子/SPM 机构普遍采用 `visuals + collisions` 双子树
  - `/World/complete_car_alternative/joints` 下集中存放轮子与两组等效球铰相关 `PhysicsRevoluteJoint/PhysicsFixedJoint`
  - 传感器包括 `Imu_Sensor`、双目相机和 `Example_Rotary`
  - 文件末尾仍存在顶层 `/physicsScene`
- 再次通过文件级导入检查 `stage1_terrain.py` 的 `env_origins`：
  - `shape == (20, 10, 3)`，说明逻辑上 20x10 共 200 个 tile 坐标系都已生成
  - `x` 范围为 `4.0 ~ 156.0`
  - `y` 范围为 `4.0 ~ 76.0`
  - 左上角 tile 原点为 `(4, 4, z)`，右下角 tile 原点为 `(156, 76, z)`
- 同时核对 Isaac Lab `TerrainImporter` 源码，确认 `scene.terrain.set_debug_vis(True)` 会在 `/Visuals/TerrainOrigin` 下创建 `VisualizationMarkers`，其本质是 `UsdGeom.PointInstancer`，并将 `env_origins.reshape(-1, 3)` 全部可视化，而不是为每个 tile 手工创建一个独立 Xform。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已经实际验证：preview 导出 USD 文件这一步在本机 headless/CPU 环境里不可靠，不能再默认认为 `--save-usd` 一定会落盘。
- 当前可以明确解释：
  - live preview stage 的主要组成来自 `preview_stage1_terrain.py` 场景配置和 `TerrainImporter`
  - 机器人本体资产的内部 prim 结构可直接参考 `results/complete_car_usd_tree.txt`
  - tile 坐标系逻辑上并不缺列；若窗口里仍看到左侧坐标系缺失，应优先继续从 live stage 对齐或可视化层排查，而不是回到 `env_origins` 生成逻辑

下一步：
- 若用户还要继续精确核对 live preview stage，下一步应优先在可用 GUI 的 Isaac Sim 会话里导出 USD，或直接写一个专门的 stage-tree dump 脚本，绕开当前 `save_stage` 不落盘的问题。

已完成：
- 根据用户补充的窗口观察现象，继续定位 `stage1` 预览中的场景错位问题：用户反馈为“两个相同大地图堆叠、tile 坐标系从右边开始、左边两列没有坐标系”。
- 复核后确认：
  - `preview_stage1_terrain.py` 与 `stage1_terrain.py` 在地形生成参数层本身一致
  - 剩余问题来自 `MGDP` 原版 mesh 放置规则未完整迁移：本地 `env_origins` 按无 border 的 tile 中心计算，但导入 mesh 若不整体减去 `border_size`，会比 marker 网格整体偏右/偏上约 `25 m`
- 将 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py` 补齐与 preview 相同的 mesh 坐标修正：
  - 新增 `_offset_mesh_to_mgdp_frame(...)`
  - 在 `import_mesh("stage1", ...)` 前先把整张 trimesh 的 `x/y` 顶点整体减去 `border_size`
- 继续保留 scene 层默认 plane 清理逻辑，形成最终一致规则：
  - 删默认 plane
  - stage1 mesh 减去 `border_size`
  - 再配置 `env_origins`
- 实际验证：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
  - `python3 -m py_compile scripts/isaac_sim/preview_stage1_terrain.py`
  - `python scripts/isaac_sim/preview_stage1_terrain.py --headless --frames 1`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `preview` 与训练环境在 stage1 场景放置层已经一致，都按 `MGDP` 规则处理了默认 plane 和 `border_size` 坐标偏移。
- 用户在窗口里看到的“左边没坐标系、坐标系从右边开始”现象，已被固化为 mesh/world frame 对齐问题，不应再误判为 preview 和 generator 使用了不同参数。

下一步：
- 直接在 Isaac Sim 窗口里重新打开 `preview_stage1_terrain.py`，优先人工确认是否还存在第二张大地图和左侧 marker 缺失。

已完成：
- 根据用户要求，继续把本项目 `stage1_terrain.py` 与 MGDP 原始 stage1 地形生成代码逐项对齐，重点核对：
  - `/home/ubuntu/MGDP/legged_gym/models/MGDP/stage1/001/random_dog_config_stage1.py`
  - `/home/ubuntu/MGDP/legged_gym/legged_gym/utils/terrain.py`
  - `/home/ubuntu/MGDP/legged_gym/legged_gym/utils/new_terrains/add_mix_terrain.py`
  - `/home/ubuntu/MGDP/isaacgym/python/isaacgym/terrain_utils.py`
- 重写 `src/rl_lab/complete_car_rl_training/.../stage1_terrain.py` 中的主要单块地形生成语义，使其更接近 MGDP 原版：
  - `slope down` 改为 MGDP `pyramid_sloped_terrain`
  - `pyramid` 改为 MGDP `pyramid_sloped_terrain + random_uniform_terrain`
  - `stairs down / stairs up / new stairs down` 改为 MGDP `pyramid_stairs_terrain`
  - `discrete obstacles` 改为 MGDP `discrete_obstacles_terrain`
  - `hurdle / gap / ramp / beam / pit` 改为 MGDP `add_mix_terrain.py` 对应语义
- 将 `env_origin` 计算改回 MGDP `mix` 的中心 `2m x 2m` patch 规则，不再对 `gap/pit/hurdle/beam` 单独做出生点偏移特判。
- 保留并确认 `preview_stage1_terrain.py` 与 `CompleteCarStage1Env` 中默认 plane 清理逻辑，从 scene 层避免 ground plane 与自定义 stage1 mesh 叠加。
- 实际验证：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`
  - 通过文件级导入直接执行 `build_stage1_terrain_data()`
  - `python scripts/isaac_sim/preview_stage1_terrain.py --headless --frames 1`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `preview_stage1_terrain.py` 和 `stage1_terrain.py` 在“地形生成参数与 mesh 来源”层是一致的：preview 直接调用 `Stage1TerrainCfg + build_stage1_terrain_data()`，不存在两套独立地形参数。
- 当前“地形交叠 + 额外 ground”问题已经确认并修复为 scene 导入问题，而不是 `stage1_terrain.py` 和 preview 参数不一致。
- 当前 `stage1_terrain.py` 虽已显著向 MGDP 原版收敛，但由于 `terrain_dict` 权重和 `num_cols = 10` 的组合仍未覆盖全部 terrain index，默认课程地图实际仍只会出现前 5 类地形。

下一步：
- 若要让预览图中真的看到 `gap / ramp / beam / pit` 等后半段 terrain，需要继续调整列分配逻辑或 `terrain_dict` 权重，而不是再去排查 preview 和 stage1 代码是否使用了不同参数。

已完成：
- 核对本项目 `stage1_terrain.py` 与 MGDP 原始 stage1 地形代码，定位 `terrain_dict / terrain_proportions / choice=j/num_cols+0.001 / heightfield->trimesh` 主体逻辑来源。
- 确认当前 Isaac Sim 中“stage1 地形交叠 + 额外 ground/grid 存在”的直接根因不是地形生成公式本身，而是场景导入路径：
  - `scripts/isaac_sim/preview_stage1_terrain.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
  先通过 `TerrainImporterCfg(terrain_type="plane")` 自动创建了 `/World/terrain/terrain`，随后又额外 `import_mesh("stage1", ...)`，导致默认 plane 与自定义地形 mesh 同时存在。
- 在上述两个入口中新增默认 plane 清理逻辑：scene 创建后，先删除 `/World/terrain/terrain` 并从 `terrain_prim_paths` 中移除，再导入 stage1 mesh。
- 实际验证：
  - `python3 -m py_compile scripts/isaac_sim/preview_stage1_terrain.py`
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
  - `python scripts/isaac_sim/preview_stage1_terrain.py --headless --frames 1`

修改文件：
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `preview_stage1_terrain.py` 与 `CompleteCarStage1Env` 都不会再把默认 plane 和 stage1 mesh 叠加到同一场景中。
- 当前“额外 ground/grid”问题已定位为 scene 初始化行为，不应再误判为 MGDP `gap / ramp / beam` 等单块地形函数本身生成了第二层网格。
- 同时确认本项目与 MGDP 原版仍有若干几何层差异，主要集中在 `gap / hurdle / pit / env_origin` 的具体实现语义；这些差异会影响地形形状是否一致，但不是这次 plane 叠加问题的根因。

下一步：
- 若要继续把本项目 stage1 地形形状尽量对齐 MGDP，应优先按原版逐项收敛 `parkour_step_gap_terrain`、`parkour_step_terrain`、`pit_terrain` 和 `env_origin` 计算，而不是继续排查 scene 中是否还有第二张地面。

已完成：
- 修复 `scripts/isaac_sim/preview_stage1_terrain.py` 的启动参数冲突。此前脚本手动声明了 `--headless`，而 `isaaclab.app.AppLauncher.add_app_launcher_args()` 也会注入同名参数，导致脚本一启动就在参数解析阶段抛出 `ValueError`。
- 删除脚本中重复的 `parser.add_argument("--headless", ...)`，保留 `AppLauncher` 注入的标准 `--headless` 参数。
- 实际验证：
  - `python3 -m py_compile scripts/isaac_sim/preview_stage1_terrain.py`
  - `python scripts/isaac_sim/preview_stage1_terrain.py --help`

修改文件：
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `preview_stage1_terrain.py` 现在可以正常完成参数解析，不会再在 `AppLauncher.add_app_launcher_args()` 阶段因为重复定义 `--headless` 而直接报错。
- 后续这个脚本若继续使用 `AppLauncher`，应避免手动重复声明其会自动注入的参数。

下一步：
- 可直接重新执行 `python scripts/isaac_sim/preview_stage1_terrain.py`，若后续再报错，再继续处理运行时层面的场景或资源问题。

已完成：
- 按用户要求撤销上一轮直接落下去的 `MGDP stage1` RL 训练接入代码，不再保留“先写完整实现、再解释”的协作方式。
- 删除任务包内新增的 `mgdp_stage1_terrain.py`、`complete_car_terrain_env.py` 和占位 terrain USDA 文件。
- 将 `Complete-Car-Rl-Training-v0` 的任务注册入口恢复为基础 `ManagerBasedRLEnv`。
- 将 `complete_car_rl_training_env_cfg.py` 恢复到撤销前的基线状态，去掉 `TerrainImporterCfg`、rough-terrain 相关 reset/reward/termination 收敛和运行时地形导入依赖。
- 更新 `docs/current_status.md` 与 `docs/conversation_history.md`，把项目状态改为“阶段 1 方案已确认，但代码实现已回退，后续按教学模式从空白重建”。
- 在教学模式启动时，曾短暂代写一个 `mgdp_stage1_terrain.py` 骨架文件；随后按用户要求立即删除，后续改为只给手敲指导，不再由 Codex 代写教学步骤中的代码。
- 按教学模式继续推进 `stage1_terrain.py`：已完成 `Stage1TerrainCfg/Stage1TerrainData`、`terrain_dict/terrain_proportions`、像素尺寸派生量、空地图分配函数、flat/slope/pit 三种 tile、tile 写入大地图、terrain_type 记录、env_origin 记录，以及 `choice -> terrain_idx -> tile` 的初版调度逻辑。
- 已将 `row` 首次接入难度变量 `difficulty = row / cfg.num_rows`，并验证同一列 slope 在不同 row 上会表现出不同最大高度：第 0 行几乎为平地，第 19 行最大高度约为 18 个高度单位。

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/__init__.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_terrain_env.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/mgdp_stage1_terrain.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/assets/mgdp_stage1_placeholder.usda`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库不再保留任务内 `MGDP stage1` rough-terrain 训练接入代码。
- 研究层面仍保留“阶段 1 目标切到 `MGDP stage1` 混合地形 + 固定球铰 + 速度跟踪”的方向，但工程实现需要重新开始。
- 后续协作方式已明确：先讲清方案，再按教学模式一步一步写；用户自己手敲代码，Codex 只做结构讲解、逐行指导和复查。
- 当前 `stage1_terrain.py` 已经从零搭到“完整二维课程地图骨架 + 初版 row/col 语义”，但还没接入真实 MGDP 多地形完整分支，也还没接入 Isaac Lab terrain importer。

下一步：
- 先向用户讲清楚从当前基线出发时，`MGDP stage1` 接入应拆成哪些代码落点，再从第一步数据结构和参数定义开始，由用户手工敲入。
- 继续在教学模式下扩展 `stage1_terrain.py`：让更多地形函数接入 `difficulty`，再逐步过渡到完整 `MGDP stage1` 地形选择和最终 mesh 导出。

## 2026-04-01

已完成：
- 根据用户新确认的主线，停止沿用“阶段 1 平地 + 目标导向移动”定义，改为“`MGDP stage1` 混合地形 + 固定球铰 + 6 维轮速动作 + 速度跟踪”。
- 在 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/` 下新增任务内 `mgdp_stage1_terrain.py`，把 `MGDP stage1` 的 mixed terrain 生成逻辑直接迁移到当前 Isaac Lab 任务包。
- 新增自定义环境类 `complete_car_terrain_env.py`，通过自定义 `ManagerBasedRLEnv` 子类在环境启动后导入 stage1 mesh，并在 `_reset_idx()` 中执行 terrain curriculum 更新。
- 新增占位文件 `assets/mgdp_stage1_placeholder.usda`，用于先初始化 Isaac Lab `TerrainImporterCfg`，再在运行时导入真实 `MGDP stage1` trimesh。
- 修改 `complete_car_rl_training_env_cfg.py`：
  - scene 从默认平地切到 `TerrainImporterCfg`
  - commands 切到速度跟踪配置
  - actions 收敛为仅 6 维轮速
  - 观测移除球铰动作相关项
  - reset 中将球铰固定为零位
  - reward / termination 切到 rough-terrain velocity tracking 口径
  - episode 长度改为 `20 s`
- 修改任务注册入口 `__init__.py`，将 `Complete-Car-Rl-Training-v0` 的 entry point 从基础 `ManagerBasedRLEnv` 改为新的 `CompleteCarTerrainEnv`。
- 实际执行静态检查：
  - `python3 -m py_compile .../mgdp_stage1_terrain.py`
  - `python3 -m py_compile .../complete_car_terrain_env.py`
  - `python3 -m py_compile .../complete_car_rl_training_env_cfg.py`
  - `python3 -m py_compile .../__init__.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/mgdp_stage1_terrain.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_terrain_env.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/assets/mgdp_stage1_placeholder.usda`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/__init__.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 RL 任务主线已不再是“平地目标导向移动”，而是切到“`MGDP stage1` rough terrain + velocity tracking”。
- 当前代码层已经具备 task-local 的 `MGDP stage1` 地形生成与 terrain curriculum 接口，但尚未在 `env_isaacLab` 里完成一次真实运行时 smoke 验证。
- 当前终端上下文无法直接导入 `isaaclab`，因此本轮只能完成静态改造与语法检查，运行时接口是否完全匹配 Isaac Lab 2.3.x 仍待下轮验证。

下一步：
- 在 `env_isaacLab` 中依次执行 `list_envs`、`zero_agent` 和短程 `train --max_iterations 10`，先确认新任务入口可创建、可 reset、可 step。

## 2026-04-02

已完成：
- 按用户要求停止“逐步教学到每个小步都由用户手敲”的节奏，直接完成 `stage1_terrain.py` 中从 Step 36 到 Step 45 的地形生成层实现。
- 在 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py` 中补齐 MGDP stage1 对应的地形函数与分发表：
  - `stairs down`
  - `stairs up`
  - `new stairs down`
  - `discrete obstacles`
  - `hurdle`
  - `gap`
  - `ramp`
  - `beam`
- 将 `pyramid`、`hurdle`、`gap`、`ramp`、`beam` 等地形加入 roughness 处理，并为随机型地形加入基于 `(row, col, terrain_idx)` 的确定性 seed。
- 将 `make_tile_by_col()` 升级为：
  - `choice -> terrain_idx`
  - `terrain_idx -> terrain_name`
  - `terrain_name -> generator`
  的完整分发结构。
- 将各类关键地形参数接入 `difficulty`：
  - 斜坡高度
  - 台阶高度 / 台阶宽度
  - 离散障碍高度
  - hurdle 高度
  - gap 宽度
  - ramp 坡度
  - beam 长度 / 间距 / 高度
  - pit 深度
- 修正 `stairs` 的初版实现偏差，改为更接近 MGDP 语义的“台阶段 + 中心 platform”结构，避免在整块 8 m tile 上无约束累加导致累计高度过大。
- 完成运行验证：
  - `python3 -m py_compile .../stage1_terrain.py`
  - 逐个 terrain name 调用 `make_tile_by_name(...)`
  - `build_stage1_terrain_data(...)`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `stage1_terrain.py` 已不再是教学骨架，而是完整的 MGDP stage1 地形生成层实现基础。
- 当前 `build_stage1_terrain_data()` 已可同时生成：
  - `height_field_raw`
  - `env_origins`
  - `terrain_type`
  - `vertices`
  - `faces`
  - `x_edge_mask`
- 当前按 MGDP 原 `choice = j / num_cols + 0.001` 与累计 `terrain_proportions` 的列选择逻辑，`20 x 10` 默认课程地图实际只命中前几类 terrain index；这是原配置逻辑的结果，不是本轮移植错误。

下一步：
- 从 Step 46 起恢复教学模式，继续处理 `env_origin` 与特殊地形出生点策略，再接 `TerrainImporter`、自定义 Isaac Lab 环境类和 terrain curriculum。

## 2026-03-31

已完成：
- 修复完整 MGDP 画廊模式下的一个 USD 构建报错：`terrain_builder.py` 中 `create_box()` 之前每次都无条件 `AddTranslateOp()` / `AddScaleOp()`，当同一路径 prim 已存在时会触发 `xformOp:translate already exists`。
- 将 `create_box()` 改为幂等写法：先检查已有 `translate/scale` xform op，存在则直接复用并更新数值，不存在时才新增。
- 实际执行：
  - `python3 -m py_compile scripts/isaac_sim/terrain_preview/terrain_builder.py`
  - `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`
- 修复 `scripts/isaac_sim/control_keyboard.py` 在 Isaac Sim 工具栏执行 `Stop -> Play` 后失去键盘控制的问题。
- 根据本地 `isaacsim_5.1` 手册与脚本现状，确认根因是 articulation 只在启动时初始化了一次，而 timeline 从 `stopped` 重新切回 `playing` 后没有重新 `initialize()`。
- 将脚本中的 articulation 初始化重构为可重复调用的 `initialize_robot_handles(...)` 流程，统一负责重新绑定 DOF 名称、关节索引、控制目标和键盘状态。
- 修改交互主循环：现在会在检测到 timeline 停回第 0 帧后，把下一次 `Play` 视为一次需要 `world.reset()` + articulation 重初始化的状态跳变；对普通 `Pause -> Play` 只恢复物理，不强制 reset。
- 补充懒加载修复：把 `mgdp_gallery_builder` 的导入从模块顶层移到完整画廊分支内部，避免 `--terrain none` 或单块 tile 旧路径被 `pydelatin` 依赖提前打坏。
- 实际执行：
  - `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`
  - `timeout 180s python3 -u scripts/isaac_sim/control_keyboard.py --terrain none --headless --frames 1`
- 新增 `scripts/isaac_sim/terrain_preview/mgdp_gallery_builder.py`，把完整 MGDP `stage1/stage2` 画廊地形的构建逻辑从预览脚本中抽成可复用共享模块。
- 重构 `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`，改为直接调用上述共享模块，不再在脚本内保留一份独立的完整地形构建实现。
- 修改 `scripts/isaac_sim/control_keyboard.py`，使 `--terrain` 除了原有单块 tile 外，还支持完整 `stage1`、`stage2` 与 `both`。
- 为完整画廊模式补充启动环境分流：单块 tile / `none` 仍沿用 conda shell 自动重启到宿主 `/home/ubuntu/isaacsim/python.sh` 的旧路径；当 `--terrain` 为 `stage1/stage2/both` 时，脚本保留在 `env_isaacLab` Python 中运行，以复用 `pydelatin` 等 `terrain_preview` 依赖。
- 修改 `control_keyboard.py` 的地形材质绑定逻辑，使共享物理材质除了绑定六个轮子碰撞体外，也会绑定到 `/World/terrain_preview` 地形根节点。
- 实际执行以下静态检查：
  - `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`
  - `python3 -m py_compile scripts/isaac_sim/terrain_preview/mgdp_gallery_builder.py`
  - `python3 -m py_compile scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
- 实际执行以下 headless 冒烟验证：
  - `conda run -n env_isaacLab python -u scripts/isaac_sim/control_keyboard.py --terrain stage1 --headless --frames 1`
  - `conda run -n env_isaacLab python -u scripts/isaac_sim/control_keyboard.py --terrain stage2 --headless --frames 1`

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `scripts/isaac_sim/terrain_preview/mgdp_gallery_builder.py`
- `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 完整 MGDP `stage1/stage2` 画廊现在不会再因为重复定义同一路径下的 base box 而在 `create_box()` 处抛出 USD xform op 冲突异常。
- `control_keyboard.py` 现在会在 Stop 后重新 Play 时自动重建 teleop 所需的 articulation 句柄和目标状态，不再沿用已经失效的启动期句柄。
- 当前脚本已恢复兼容两条路径：
  - 宿主 `python.sh` 下的 `--terrain none` / 单块 tile
  - `env_isaacLab` 下的完整 MGDP `stage1/stage2` 画廊
- `control_keyboard.py` 现在已经不是只能注入单块 `slope_ramp/gap/corridor` 之类的局部地形，而是可以直接把 `terrain_preview` 中的完整 MGDP `stage1` 或 `stage2` 画廊放进同一个 teleop stage。
- 当前机器上，完整 MGDP 画廊模式不能继续走宿主 `isaacsim/python.sh` 默认路径，因为该路径缺少 `pydelatin`；正确运行方式应为激活 `env_isaacLab` 后执行 `python scripts/isaac_sim/control_keyboard.py --terrain stage1` 或 `--terrain stage2`。
- `stage1` 与 `stage2` 两条新路径都已在本机 headless 1 帧模式下实际跑通并正常退出，说明这次修改不只是静态代码改动。

下一步：
- 若要继续人工联调，可在 `env_isaacLab` 中直接运行 `python scripts/isaac_sim/control_keyboard.py --terrain stage1` 或 `python scripts/isaac_sim/control_keyboard.py --terrain stage2`，再观察车体初始落点、轮地接触与通过性表现。

已完成：
- 检查当前机器的 Conda 启动默认值，确认新开的交互式 `bash` 仍会因为 `auto_activate_base=True` 而默认进入 `base`。
- 将 `~/.condarc` 改为 `auto_activate: false`，关闭 `base` 自动激活。
- 在 `~/.bashrc` 的 `conda init` 之后追加交互式 shell 自动 `conda activate env_isaacLab` 的启动逻辑。
- 实际验证：
  - `conda config --show auto_activate_base`
  - `bash -ic 'printf "%s\n" "CONDA_DEFAULT_ENV=$CONDA_DEFAULT_ENV" "CONDA_PREFIX=$CONDA_PREFIX"'`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前机器新开的交互式 `bash` 终端默认已不再进入 `base`，而是直接进入 `env_isaacLab`。
- 后续在这个工作站里执行本仓库的 Isaac Lab / Isaac Sim 相关命令时，一般不再需要先手动 `conda activate env_isaacLab`。

下一步：
- 若后续更换 shell、用户或机器，需要重新检查对应启动文件是否也继承了这一默认环境设置。

## 2026-03-30

已完成：
- 按“代码与文档改动 + `mgdp_port/` 新源码，排除缓存/输出/备份文件”的范围重新整理本次待上传内容。
- 扩充根目录 `.gitignore`，新增忽略 `.cache/`、`outputs/`、`__pycache__/`、`*.py[cod]`、`*.bak`，避免 Isaac Sim 本地缓存、导出物和备份文件再次混入普通 Git 提交。
- 复核工作区后确认本次未跟踪内容只剩 `scripts/isaac_sim/terrain_preview/mgdp_port/` 源码目录，缓存与生成物已从待提交列表中排除。
- 将这一仓库级提交边界补写进 `docs/conversation_history.md`，作为后续常规 Git 上传默认规则。

修改文件：
- `.gitignore`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库普通 Git 上传的默认范围已进一步收敛为“源码、文档、必要结果”，不再混入本地运行时制品。
- 后续若继续用 Isaac Sim 做联调，生成的 `.cache/`、`outputs/`、`__pycache__` 与 `*.bak` 将默认留在本地，不再干扰正常推送。

下一步：
- 将本次整理后的源码与文档提交并推送到 GitHub `origin/main`。

已完成：
- 将 MGDP 中与地形生成、terrain curriculum 相关的脚本复制到 `scripts/isaac_sim/terrain_preview/mgdp_port/`，包括 `terrain.py`、`terrain_utils.py` 和 `new_terrains/`。
- 新增 `scripts/isaac_sim/terrain_preview/mgdp_port/configs.py` 与 `curriculum.py`，把 MGDP 的 stage1 / stage2 地形参数和课程学习地形分配逻辑独立迁移到本仓库。
- 重写 `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`，改为基于 `isaaclab.app.AppLauncher` 直接在 Isaac Sim 中构建 MGDP 地形网格、转换 mesh，并附带课程学习环境原点标记。
- 修改 `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`，使其默认激活 `conda` 环境 `env_isaacLab` 后直接用 `python` 启动，不再依赖旧的 `isaacsim/python.sh` 包装路径。
- 修复迁移后地形工具在新环境下的兼容问题，包括去掉对 `isaacgym` / `legged_gym` 包结构的硬依赖，以及将 `scipy.interpolate.interp2d` 替换为 `RegularGridInterpolator`。
- 为当前 `env_isaacLab` 修复 Isaac Sim 窗口启动所需的数值栈，将 `numpy` 回滚到 `1.26.0`，并将 `scipy` 调整为 `1.14.1`。
- 实际完成以下验证：
  - `python -m py_compile scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
  - `python -m py_compile scripts/isaac_sim/terrain_preview/mgdp_port/*.py` 相关核心脚本
  - `bash -n scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --headless --frames 1 --gallery stage1`
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --headless --frames 1 --gallery stage2`
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --frames 1 --gallery stage1`
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --frames 1 --gallery stage2`

修改文件：
- `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
- `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`
- `scripts/isaac_sim/terrain_preview/README.md`
- `scripts/isaac_sim/terrain_preview/mgdp_port/__init__.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/configs.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/curriculum.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/terrain.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/terrain_utils.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/new_terrains/__init__.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/new_terrains/add_mix_terrain.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/new_terrains/add_trimesh_terrain.py`
- `scripts/isaac_sim/terrain_preview/mgdp_port/new_terrains/add_extreme_gap_terrain.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库中已经有一份可独立于原 MGDP 仓库启动的地形预览迁移版，核心目标是“在 Isaac Sim 中查看 MGDP 地形生成和地形课程学习布局”。
- 当前 `env_isaacLab` 下，MGDP 地形预览已不是仅能 headless 导出 USD，而是可以实际启动 Isaac Sim 窗口查看。
- 当前这条预览链路依赖 `numpy==1.26.0`；若后续又被升级到 `numpy 2.x`，Isaac Sim 扩展加载大概率会再次报二进制兼容错误。

下一步：
- 若需要继续与完整车联调，可在现有 MGDP 地形预览基础上再决定是否把完整车资产放进同一个 stage 做实际通过性观察。

已完成：
- 继续修改 `scripts/isaac_sim/control_keyboard.py`，将此前被固定为零速的 6 个轮子重新接回键盘遥操作。
- 按仓库已有遥操作习惯，将车轮控制设为 `W/S` 前后、`A/D` 差速转向、`SPACE` 将轮速目标清零。
- 保留数字小键盘 `1-9`、`/`、`*`、`-` 对 6 个球铰自由度的正负位置调节。
- 为车轮速度命令与球铰位置命令都加入一阶平滑，避免按键切换时目标突变。
- 对更新后的脚本执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，语法检查通过。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `control_keyboard.py` 现同时支持轮式差速控制和球铰位置控制。
- 当前键位分工为：`W/S/A/D/SPACE` 控轮子，数字小键盘控球铰，二者互不冲突。
- 控制链路已加入基础平滑，更接近可用于手动调试的实际 teleop 形式。

下一步：
- 若需要，可继续在 Isaac Sim 中实际启动脚本，观察平滑系数是否偏软或偏硬，再调 `WHEEL_VELOCITY_SMOOTHING` 与 `BALL_POSITION_SMOOTHING`。

## 2026-03-30

已完成：
- 修改 `scripts/isaac_sim/control_keyboard.py`，将加载的机器人资产从旧的仓库根目录 `complete_car_alternative.usd` 切换为 `USD/complete_car.usd`。
- 将脚本中的机器人根 prim 路径同步改为 `/World/complete_car_final`，与当前 `complete_car.usd` 的实际机器人本体一致。
- 将原先的字母键控制方案改为数字小键盘控制方案，使用 `1-9`、`/`、`*`、`-` 对 6 个球铰自由度进行正负调节。
- 由于这 12 个键已全部用于 6 个自由度的正负控制，当前脚本模式下将 6 个轮子保持为零速度，不再单独提供轮速键盘控制。
- 对修改后的脚本执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，语法检查通过。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `control_keyboard.py` 已与当前主 USD 资产 `USD/complete_car.usd` 和 `/World/complete_car_final` 对齐。
- 新键位方案已经从字符串按键名切换为 `carb.input.KeyboardInput` 的数字小键盘枚举，避免对事件名做字符串猜测。
- 当前脚本更适合做 6 自由度球铰姿态手动调试，不再承担轮式推进键盘遥操作。

下一步：
- 若后续仍需要同时做轮速遥控和球铰遥控，需要重新定义一套不与数字小键盘冲突的轮子控制键位。

## 2026-03-30

已完成：
- 按用户给出的新稿，整体替换 `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`。
- 新版 `chapter03` 现以“运动学模型”为题，覆盖空间位置/姿态/位姿、旋转矩阵、齐次变换矩阵，以及 3-RRR 球面并联机构逆运动学解析推导。
- 由于新稿引入了 `tikzpicture` 插图，在 `毕业论文/毕业论文模板/LaTeX/main.tex` 中补入 `tikz` 与 `arrows.meta` 宏包依赖。
- 在论文主目录下连续执行两次 `xelatex -interaction=nonstopmode -halt-on-error main.tex`，确认替换后的正文可编译。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `毕业论文/毕业论文模板/LaTeX/main.tex`
- `毕业论文/毕业论文模板/LaTeX/main.pdf`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `chapter03.tex` 已切换为用户提供的新版本内容，不再是上一版“球铰等效机构逆运动学建模”文本。
- 新稿引入的 TikZ 插图依赖已经补齐，主文档编译链路可正常通过。
- 当前仍存在两类非阻塞告警：`chapter01` 的历史未定义引用，以及新章节长公式带来的 `Overfull \hbox` 提示。

下一步：
- 若后续需要继续打磨论文排版，可优先处理 `chapter03` 中长公式的断行与版面压缩。

## 2026-03-29

已完成：
- 对整个仓库做了目录级盘点，梳理当前各文件组的职责边界。
- 新增 `docs/project_file_map.md`，把仓库内容归纳为 RL 主线、资产与仿真验证、文献、论文、逆运动学推导与配图、结果输出六大块。
- 重写根 `README.md`，使其与当前阶段主线一致，并补充当前最重要的目录入口说明。
- 将本次仓库文件归纳结果同步写入长期记忆和当前状态，避免后续再次靠聊天临时解释目录用途。

修改文件：
- `README.md`
- `docs/project_file_map.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库已经有一份显式的文件地图，可直接用于后续定位代码、论文、文献和资产文件。
- 根 README 不再停留在早期最小 baseline 描述，而是对齐到当前真实主线和目录结构。

下一步：
- 若后续需要做物理目录重组，可直接以 `docs/project_file_map.md` 的六块职责划分为准继续收敛。

## 2026-03-29

已完成：
- 核对本地 `main` 与 GitHub `origin/main` 的提交关系，确认远端在同步前没有额外新提交。
- 按当前工作区原样整理并提交 Git 变更，包含现有删除项与未跟踪新增内容。
- 将当前仓库快照推送到 GitHub `origin/main`，使远端与本地工作区保持一致。
- 同步更新 `docs/current_status.md`，移除“待同步”状态。

修改文件：
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- GitHub `origin/main` 已更新为当前本地工作区快照。
- 本轮同步后，仓库当前状态与远端主分支已一致。

下一步：
- 回到 RL baseline 收敛、USD 清理与论文写作主线。

## 2026-03-29

已完成：
- 根据 3-RRR 球面并联机构文献与现有符号化推导结果，重写毕业论文 `chapter03` 的球铰逆运动学部分。
- 在章节中补入三维旋转矩阵、齐次变换矩阵、方向向量约束、半角代换以及闭式逆解公式。
- 统一论文符号口径，将动平台姿态写为 `(\phi,\vartheta,\psi)`，将主动关节角保留为 `\theta_i`，避免姿态角与关节角冲突。
- 向论文参考文献库新增 `Sadeqi 等 2017` 的 BibTeX 条目。
- 实际执行 `xelatex -> bibtex -> xelatex -> xelatex` 编译验证，确认新增章节可被模板接受。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `毕业论文/毕业论文模板/LaTeX/reference/ref.bib`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `chapter03.tex` 已从占位模板改写为可直接用于论文正文的中文逆运动学章节。
- 当前章节推导链路已经固定为 方向向量建模 -> 几何约束 -> 半角代换 -> 二次方程闭式求解。
- 编译过程中与本次改动直接相关的引用和交叉引用均已收敛；主文档仍保留 `chapter01` 历史未补的两个旧引用告警，与本次修改无关。

下一步：
- 若需要，可继续在 `chapter04` 或 `chapter05` 中承接本章公式，补写控制映射、仿真验证或实验结果分析内容。

## 2026-03-28

已完成：
- 基于原始 PDF 重新整理 `Learning-based legged locomotion: State of the art and future perspectives` 的阅读笔记。
- 按已安装的 `literature-reading-notes` skill 模板重写了文献笔记结构，补齐论文快照、章节逻辑、mind map、分章节精读、术语表、重要参考文献和可复用 related-work 段落。
- 将该文献的总结重点进一步对齐到当前课题两阶段主线，明确其对 observation / reward / action / training framework / sim-to-real 的可迁移启发。
- 同步更新 `docs/current_status.md`，记录该阅读笔记已完成规范化重写。
- 根据用户新要求，将该笔记再次改写为“重要内容摘录与整理”版本，重点围绕正文中的概念定义、使用方式、该段引用的相关工作，以及对应完整参考文献信息。
- 去除了与当前课题直接绑定的分析内容，回到面向原文内容本身的综述笔记写法。
- 继续按用户给出的示例格式重写整份笔记，结构明确对齐为：论文快照、全文结构、mind map、章节精读笔记、关键知识点、术语表、重要参考文献、可复用综述段落。
- 将 `Section 3.2 Observation` 及其子节改为“核心观点 / 本节作用 / 段落主旨 / 重点概念提炼 / 学术含义 / 完整参考文献”风格，并同步重排 `Reward`、`Action Space`、`Learning Frameworks`、`Sim-to-real`、`Combining control and learning` 等关键章节。

修改文件：
- `docs/literature/mineru_output/Ha 等 - 2025 - Learning-based legged locomotion State of the art and future perspectives/auto/reading_notes.md`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前该文献对应目录下的 `reading_notes.md` 已不再只是首轮高层梳理，而是可直接复用的结构化综述笔记。
- 该综述继续支持当前仓库已固化的阶段化路线：先最小 baseline，再逐步加入复杂 observation、球铰控制、复杂地形和 sim-to-real 设计。
- 当前版本更符合“文献摘录式阅读笔记”用途：可以直接按节查看某个概念在综述中的定义、作用与引用来源。
- 当前版本已更接近“综述型文献精读卡片”，便于后续继续逐段扩写。

下一步：
- 若需要，可继续把 `3.3 Reward`、`3.4 Action space`、`4 Learning frameworks` 进一步扩展成逐段摘录版，并补得更全。

## 2026-03-16

已完成：
- 将仓库重组为更清晰的 `scripts/`、`results/`、`refs/` 和 `src/` 结构。
- 在 `AGENTS.md` 中加入仓库级启动上下文规则。
- 新增持久化会话记录文件 `docs/conversation_history.md`。
- 新增按日期记录的进度日志 `logs/daily_work_log.md`。
- 更新 Isaac Sim 辅助脚本，使其使用仓库相对路径。
- 确认 `.codex/config.toml` 存在且已启用 Web 搜索。
- 新增 `scripts/isaac_sim/check_isaaclab_asset.py` 用于 Isaac Lab 资产验证。
- 对 `USD/complete_car_alternative.usd` 进行了 Isaac Lab headless 验证。
- 识别出当前 USD 包尚不能直接作为 Isaac Lab articulation 生成，原因包括缺失 `configuration/*.usd` 依赖文件以及缺少 default prim。
- 将 Isaac Lab 资产检查入口切换为 `USD/complete_car.usd`。
- 对 `USD/complete_car.usd` 再次进行了 Isaac Lab headless 验证。
- 确认 stage 中实际根节点仍为 `/World/complete_car_alternative`，同时 `USD/complete_car.usd` 仍缺少 default prim，且 `USD/configuration/` 下存在 unresolved references。
- 修复 `USD/complete_car.usd`，将 default prim 设置为 `/World`。
- 清理 `USD/configuration/default_scene_base.usd` 中四个损坏的纯可视化引用。
- 通过 USD 检查确认损坏引用已被移除。
- 通过 Isaac Lab headless 加载确认当前机器人已被识别为 12 关节 articulation。

修改文件：
- `AGENTS.md`
- `README.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `docs/current_status.md`
- `scripts/isaac_sim/check_isaaclab_asset.py`
- `scripts/isaac_sim/inspect_usd_dependencies.py`
- `scripts/isaac_sim/repair_complete_car_usd.py`
- `scripts/isaac_sim/repair_complete_car_usd_v2.py`
- `scripts/isaac_sim/repair_complete_car_usd_v3.py`
- `scripts/isaac_sim/repair_complete_car_usd_v4.py`
- `scripts/isaac_sim/control_keyboard.py`
- `scripts/isaac_sim/validate_sensors.py`
- `refs/isaac_kb/README.md`
- `src/rl_lab/README.md`

下一步：
- 构建最小 Isaac Lab 任务骨架，并为完整车补齐 actuator 配置。

## 2026-03-16

已完成：
- 删除了仓库内手写的 direct-workflow 任务骨架 `src/rl_lab/tasks/`。
- 保留 `src/rl_lab/complete_car_rl_training/` 作为唯一的 Isaac Lab 模板 project。
- 更新仓库状态说明，明确后续 RL 环境开发应继续在模板 project 内进行。

修改文件：
- `src/rl_lab/__init__.py`
- `src/rl_lab/tasks/__init__.py`
- `src/rl_lab/tasks/complete_car_attitude_direct/__init__.py`
- `src/rl_lab/tasks/complete_car_attitude_direct/complete_car_env.py`
- `src/rl_lab/tasks/complete_car_attitude_direct/agents/__init__.py`
- `src/rl_lab/tasks/complete_car_attitude_direct/agents/rsl_rl_ppo_cfg.py`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

下一步：
- 将 `src/rl_lab/complete_car_rl_training/` 中的 cartpole 模板内容替换为完整车的 manager-based 最小任务。

## 2026-03-16

已完成：
- 新增 `docs/isaaclab模板使用指南.md`，整理了当前模板 project 的用途、推荐工作流、具体使用命令以及模板改造位置。
- 将 `docs/current_status.md` 改写为中文。
- 将 `logs/daily_work_log.md` 改写为中文，并明确后续新增日志统一使用中文。
- 在 `AGENTS.md` 中补充规则：`docs/current_status.md` 与 `logs/daily_work_log.md` 统一使用中文维护。

修改文件：
- `AGENTS.md`
- `docs/isaaclab模板使用指南.md`
- `docs/current_status.md`
- `logs/daily_work_log.md`

下一步：
- 按照 `docs/isaaclab模板使用指南.md` 中的顺序，在模板 project 内替换任务名、资产配置、动作配置、观测配置、奖励配置和 PPO 配置。

## 2026-03-17

已完成：
- 修复了 `complete_car_rl_training_env_cfg.py` 中已有的语法和 Isaac Lab API 拼写错误。
- 将模板环境中的 cartpole 资产配置整体替换为完整车 `ArticulationCfg`，入口指向 `USD/complete_car.usd`。
- 为完整车补齐了两组 actuator：
  - 6 个球铰等效关节 `ball_joints`
  - 6 个车轮关节 `wheel_joints`
- 将动作空间改为 12 维：
  - 6 维球铰位置动作
  - 6 维车轮速度动作
- 加入 `UniformVelocityCommandCfg`，使策略可以基于速度指令学习前进/后退。
- 将观测改为完整车版本，包含底盘速度、重力投影、速度指令、球铰状态、车轮速度和上一时刻动作。
- 将 reset、reward、termination 从 cartpole 版本替换为完整车版本。
- 用 `python3 -m py_compile` 对新的环境配置文件做了语法检查，结果通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/source/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前模板环境已经不再依赖 cartpole 关节名。
- 当前基线任务设计已经从“仅球铰姿态控制”升级为“球铰姿态 + 车轮前进/后退”的联合控制版本。
- 目前只完成了静态改写和语法检查，尚未完成 Isaac Lab 运行时验证。

下一步：
- 用 `list_envs.py`、`zero_agent.py` 或 `random_agent.py` 验证完整车环境能否正常创建与 step。
- 根据运行结果继续调节 wheel actuator 参数、奖励权重和终止阈值。

## 2026-03-18

已完成：
- 删除了 `complete_car_rl_training_env_cfg.py` 中 scene 级重复定义的 `ground` 与 `dome_light`。
- 将完整车 RL 环境的默认场景来源明确为 `USD/complete_car.usd` 内部已有场景元素。
- 将 PPO 配置中的 `experiment_name` 从 `cartpole_direct` 改为 `complete_car_rl_training`。
- 在 `AGENTS.md` 中新增“第一性原理”和“方案规范”两组仓库级协作约束。
- 同步更新了项目当前状态和长期会话结论。

修改文件：
- `src/rl_lab/complete_car_rl_training/source/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/source/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/agents/rsl_rl_ppo_cfg.py`
- `AGENTS.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 RL scene 只保留机器人资产定义，不再在配置层重复生成地面和灯光。
- 后续训练日志目录将使用完整车任务名，不再落到 cartpole 模板名下。
- 后续运行时验证需要优先确认 `complete_car.usd` 内置场景在 Isaac Lab 多环境复制下的行为是否稳定。

下一步：
- 运行 `list_envs.py`、`zero_agent.py` 或 `random_agent.py` 做环境创建与 step 验证。

## 2026-03-18

已完成：
- 对 `src/rl_lab/complete_car_rl_training/` 进行了目录整理，移除了重复的模板壳层。
- 将 Python 包从 `source/complete_car_rl_training/complete_car_rl_training/` 收平到项目根下的 `complete_car_rl_training/`。
- 将 `setup.py` 与 `config/extension.toml` 移到训练项目根目录，并将安装方式统一为 `pip install -e .`。
- 将 `setup.py` 改为优先使用标准库 `tomllib`，避免在 Python 3.11 下额外依赖第三方 `toml` 包。
- 删除了训练项目中的嵌套 `.git`、`.vscode`、UI 示例文件和旧 `src/rl_lab/tasks/` 残留。
- 更新了训练项目 README、仓库 README 和 `docs/isaaclab模板使用指南.md`，同步新的目录结构与命令。
- 新增 `src/rl_lab/README.md`，明确 `complete_car_rl_training/` 是唯一保留的训练工作区。

修改文件：
- `src/rl_lab/README.md`
- `src/rl_lab/complete_car_rl_training/setup.py`
- `src/rl_lab/complete_car_rl_training/pyproject.toml`
- `src/rl_lab/complete_car_rl_training/.gitignore`
- `src/rl_lab/complete_car_rl_training/config/extension.toml`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/__init__.py`
- `src/rl_lab/complete_car_rl_training/README.md`
- `src/rl_lab/complete_car_rl_training/scripts/list_envs.py`
- `README.md`
- `docs/isaaclab模板使用指南.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 训练项目后续统一按“项目根 + 单个 Python 包 + scripts”结构维护。
- 后续所有安装、运行、训练、回放命令都应从 `src/rl_lab/complete_car_rl_training/` 项目根执行。
- `python3 setup.py --name` 已能在本机默认 Python 下通过，不再因为缺少 `toml` 包失败。

下一步：
- 在新结构下重新执行 `pip install -e .`，然后做 `list_envs.py`、`zero_agent.py`、`random_agent.py` 验证。

## 2026-03-18

已完成：
- 实际执行了完整车 RSL-RL 训练启动流程，并确认正确任务 ID 为 `Complete-Car-Rl-Training-v0`。
- 确认当前终端会话下默认 GPU 路径不可用，CUDA / NVIDIA driver 未加载，直接按默认配置会在 runner 初始化时失败。
- 修复了 `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`，使 `--device` 同时覆盖环境和 RSL-RL runner 的 device。
- 使用 `PYTHONPATH` 注入训练项目根目录，绕过当前沙箱下 `pip install -e .` 的 build isolation 联网与用户站点只读问题。
- 以 `--headless --device cpu --num_envs 100` 实际跑通了 `reset -> step -> train` 链路。
- 训练已进入稳定学习迭代，并在日志目录中生成了 `model_0.pt` 与 `model_50.pt`。
- 识别出 `USD/complete_car.usd` 仍有离线不可解析的远端引用，以及多环境复制时的 `PhysicsScene` replication 报错。
- 从训练指标确认当前主要行为问题是 `root_too_low` 终止长期为 `1.0`，说明环境虽可训练，但 rollout 质量很差。

修改文件：
- `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 第一条完整训练链路已经在本机 CPU 模式下验证通过，说明任务注册、环境创建、manager 配置、RSL-RL runner 与日志落盘均已打通。
- 最新训练输出目录为 `src/rl_lab/complete_car_rl_training/logs/rsl_rl/complete_car_rl_training/2026-03-18_17-14-07/`。
- 当前真正阻塞点已经从“能否启动训练”切换为“USD 资产离线清理 + replicated physics scene 清理 + root height 相关任务调参”。

下一步：
- 清理 `USD/complete_car.usd` 中的远端引用和内嵌 `PhysicsScene`。
- 结合当前训练日志调整初始高度、`root_too_low` 阈值、reset 范围和奖励权重。
- 如果继续在当前终端会话运行训练，默认使用 `--device cpu`。

## 2026-03-18

已完成：
- 重新在当前 `env_isaacLab` conda 环境中核实了启动方式，确认 `python` 直接可导入 `isaaclab` 与 `isaacsim`。
- 确认旧文档中的 `env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV /home/ubuntu/IsaacLab/isaaclab.sh -p ...` 属于历史工作绕过方式，不再应作为默认启动命令。
- 识别出直接 `python scripts/...` 初始失败的真实原因不是 conda，而是：
  - 首次无交互启动会卡在 Omniverse EULA 确认
  - 当前 conda 环境内尚未安装项目包 `complete_car_rl_training`
- 使用 `python -m pip install -e . --no-build-isolation` 将训练项目安装到 `env_isaacLab`。
- 在安装后重新验证，直接运行 `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --num_envs 4 --headless --device cpu --max_iterations 1` 已可进入完整训练循环并完成 1 次 learning iteration。
- 更新了训练项目 README、模板使用指南、当前状态和长期会话结论，使仓库文档与当前真实启动方式一致。

修改文件：
- `src/rl_lab/complete_car_rl_training/README.md`
- `docs/isaaclab模板使用指南.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前默认启动路径应为：激活 `env_isaacLab` -> `python -m pip install -e . --no-build-isolation` -> 必要时设置 `OMNI_KIT_ACCEPT_EULA=YES` -> 直接运行 `python scripts/...`。
- 直接训练链路已在当前 conda 环境下重新验证通过。

下一步：
- 继续清理 `USD/complete_car.usd` 的远端引用与内嵌 `PhysicsScene`。
- 在直接 `python` 启动路径下继续迭代训练配置与奖励设计。

## 2026-03-18

已完成：
- 根据 Isaac Lab 的资产组织方式，重新明确了 `complete_car.usd` 与 `scene cfg` 的职责分离：
  - `complete_car.usd` 仅保留小车 articulation 本体与车体挂载传感器
  - `scene cfg` 负责地面和灯光
- 修改 `src/rl_lab/complete_car_rl_training/.../complete_car_rl_training_env_cfg.py`，在 `CompleteCarRlTrainingSceneCfg` 中补回 `ground` 与 `dome_light`。
- 识别出当前两个主要远端依赖分别是：
  - scene 层的 `default_environment.usd`
  - 机器人 USD 内的 `Example_Rotary.usda`
- 按当前需求，保留 scene 层 `default_environment.usd`，不再使用临时本地 `CuboidCfg` 地面方案。

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `scene` 层的 ground/light 配置已经重新回到 Isaac Lab 标准职责边界。
- 当前远端依赖分为两类：
  - scene 层继续使用 `default_environment.usd`
  - 机器人 USD 中仍有 `Example_Rotary.usda`

下一步：
- 清理 `USD/complete_car.usd` 中残留的 `Example_Rotary.usda` 远端引用。
- 继续评估 camera / lidar / IMU 是否都需要保留在当前 RL 基线资产里。

## 2026-03-19

已完成：
- 重新整理了仓库级 `AGENTS.md` 结构，将启动上下文、项目背景、优先级、协作规则、记忆规则和规范文件职责重新归类。
- 将 RL 训练路径正式固化到 `AGENTS.md`：
  - 阶段 0 先跑通训练闭环

## 2026-03-28

已完成：
- 读取并整理了根目录草稿 `literature_note_skill.md`。
- 将其安装为可被 Codex 发现的本地 skill：`/home/lbz/.codex/skills/literature-reading-notes/`。
- 新增该 skill 的 `SKILL.md` 与 `agents/openai.yaml`，统一技能名为 `literature-reading-notes`。
- 将本次变更同步写入 `docs/current_status.md` 与 `docs/conversation_history.md`，保证后续会话可继承。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `/home/lbz/.codex/skills/literature-reading-notes/SKILL.md`
- `/home/lbz/.codex/skills/literature-reading-notes/agents/openai.yaml`

产出/结论：
- 当前已可直接使用 `$literature-reading-notes` 触发结构化文献阅读笔记工作流。
- 根目录 `literature_note_skill.md` 现可视为技能草稿源，而不是最终可发现的 skill 入口。

下一步：
- 如需继续完善，可再按实际使用频率补充该 skill 的示例、引用规则细化或与 `docs/literature/` 的仓库内工作流衔接说明。
  - 阶段 1 做平地基础速度跟踪 baseline
  - 阶段 2 再加入球铰控制
  - 更后续阶段再加入运动学先验、地形适应和感知融合
- 明确了第 1 阶段默认 baseline 应优先采用“固定球铰姿态 + 轮式运动控制 + 低维本体观测”的最短路径方案。
- 同步更新了 `docs/current_status.md` 与 `docs/conversation_history.md`，把新的训练主线和当前代码现状之间的差异记录为长期记忆。

修改文件：
- `AGENTS.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 后续会话不应再把“轮子 + 球铰联合控制 + 复杂扩展”默认视为第一阶段主线。
- 当前应先把平地速度跟踪 baseline 做稳定，再逐步恢复机构复杂度。
- `AGENTS.md` 现在已经包含完整且可继承的 RL 训练路线说明，不再依赖单次对话上下文。

下一步：
- 按新的第 1 阶段主线收敛环境配置，优先确认是否需要把当前 12 维联合动作基线简化为固定球铰版本。
- 继续处理 `USD/complete_car.usd` 的远端依赖、复制兼容性和 `root_too_low` 相关训练稳定性问题。

## 2026-03-19

已完成：
- 读取并解释了 `2026-03-19_13-13-03` 训练 run 的 Isaac Lab 日志、Hydra 配置和 TensorBoard 标量项。
- 确认该 run 已生成 `model_0.pt`、`model_50.pt`、`model_100.pt`、`model_149.pt`，属于完整训练完成而非中途终止。
- 新增 `scripts/tensorboard_export.py`，可将单次 run 的 TensorBoard scalar 自动导出为本地 `csv/json`。
- 修改 `scripts/rsl_rl/train.py`，使训练结束后自动生成 `tensorboard_export/summary.json`、`latest_values.csv` 和各 tag 的 `scalars/*.csv`。
- 对 `2026-03-19_13-13-03` 的已有 run 执行了一次导出验证，确认离线分析文件已正常生成。
- 更新训练项目 `README.md`，补充 TensorBoard 离线导出说明。
- 新增 `docs/tensorboard_reading_guide.md`，总结 TensorBoard 读图方法、指标含义和诊断顺序。
- 新增 `skills/isaac-rl-run-diagnosis/` skill，并复制安装到 `~/.codex/skills/isaac-rl-run-diagnosis/`。

修改文件：
- `src/rl_lab/complete_car_rl_training/scripts/tensorboard_export.py`
- `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`
- `src/rl_lab/complete_car_rl_training/README.md`
- `src/rl_lab/complete_car_rl_training/docs/tensorboard_reading_guide.md`
- `src/rl_lab/complete_car_rl_training/skills/isaac-rl-run-diagnosis/SKILL.md`
- `src/rl_lab/complete_car_rl_training/skills/isaac-rl-run-diagnosis/agents/openai.yaml`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 后续每次训练结束后，都可以直接读取 run 目录下的 `tensorboard_export/`，不必依赖 TensorBoard 网页界面。
- 当前 `2026-03-19_13-13-03` run 的关键信号是：
  - `Train/mean_reward` 已明显上升
  - `Train/mean_episode_length` 已到 `480.0`
  - `Episode_Termination/time_out = 1.0`
  - `Episode_Termination/root_too_low = 0.0`
- 这说明当前 run 的 rollout 存活性明显好于此前 `root_too_low` 主导的异常情况。

下一步：
- 基于导出的 `latest_values.csv` 与各 tag CSV，继续逐项分析奖励构成和速度跟踪误差。
- 再按第 1 阶段主线评估是否应将球铰动作从默认 baseline 中收紧或固定。

## 2026-03-20

已完成：
- 为 `docs/literature/` 建立了“原始 PDF 保留 + MinerU 转 Markdown”并存的文献工作流。
- 新增 `scripts/literature/mineru_batch_convert.sh`，用于批量或单篇执行 MinerU PDF 转 Markdown。
- 新增 `scripts/literature/build_literature_manifest.py`，用于自动生成文献 PDF 与 Markdown 对照索引。
- 新增 `docs/literature/README.md`，明确文献目录规范、转换命令和 Codex 的读取顺序。
- 生成了首版 `docs/literature/catalog.md`，当前已列出全部本地 PDF，待 MinerU 转换后自动补齐 Markdown 路径。
- 更新 `AGENTS.md`、`README.md` 和 `docs/current_status.md`，把本地文献优先读 Markdown、PDF 负责核验的规则固化为长期约定。
- 创建仓库级 `.gitignore`，忽略本地 `.venv-mineru/` 文献工具虚拟环境。
- 在当前 `env_isaacLab` 环境中安装完成 `MinerU`。
- 首次单篇转换验证中，确认当前会话继承的本地代理变量会阻塞 MinerU 模型下载；已切换为“清空代理 + `MINERU_MODEL_SOURCE=modelscope`”的首跑方式。

修改文件：
- `.gitignore`
- `AGENTS.md`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `docs/literature/README.md`
- `docs/literature/catalog.md`
- `scripts/literature/mineru_batch_convert.sh`
- `scripts/literature/build_literature_manifest.py`

产出/结论：
- 本仓库后续文献读取默认采用：
  - 先读 `md`
  - 再用 `pdf` 核对图、公式、页码和可疑段落
- 文献目录已经从“仅 PDF 堆放”升级为“可转换、可索引、可被 Codex 稳定读取”的结构。
- 当前机器上 MinerU 的首次模型下载不应直接沿用现有代理环境，而应优先使用 `modelscope`。

下一步：
- 完成至少一篇文献的 MinerU 转换 smoke test，并确认真实输出目录结构。
- 确认 MinerU 的实际输出目录结构后，再按真实产物补齐 catalog 中的 Markdown 链接。


补充完成：
- 阅读并筛选了 `docs/literature/` 下与 RL 环境配置和训练设计相关的文献。
- 按“与本课题形态相似度 + 对 observation/reward/action/termination 的直接借鉴价值 + 与当前阶段主线的贴合度”完成了推荐排序。
- 新增 `docs/literature/rl_env_reading_notes.md`，作为后续持续维护的文献阅读笔记。
- 将当前优先阅读顺序收敛为：
  - `Wiberg 2022`
  - `Wiberg 2024`
  - `Bauer 2025`
  - `Xu 2024`
  - `Salvi 2022`

补充修改文件：
- `docs/literature/rl_env_reading_notes.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

补充产出/结论：
- 已形成一份面向 RL env 设计的本地文献阅读入口，不再需要每次从全部文献重新筛选。
- 当前不应优先把感知综述和 3-RRR 机构学论文作为第 1 阶段 baseline 的主参考。

补充下一步：
- 基于阅读笔记中的前 3 篇文献，进一步提炼可直接映射到 Isaac Lab 的 `observation / action / reward / termination` 草案。

## 2026-03-20

已完成：
- 对 `Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning.pdf` 执行了单篇 MinerU 转换。
- 成功生成对应 Markdown、图片与中间产物目录：
  - `docs/literature/mineru_output/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning/auto/`
- 自动更新 `docs/literature/catalog.md`，将该文献条目标记为 `ready`。
- 基于生成的 Markdown 与原始 PDF，补充了 `docs/literature/rl_env_reading_notes.md` 中该文的精读结论。
- 提炼了该文对本课题的可迁移要点：
  - reward 的主目标项 + 约束项组织方式
  - termination 的危险姿态 / 危险接触 / timeout 框架
  - curriculum 的逐层加难组织方式
  - 不应在第 1 阶段直接照搬高维地形 observation 与联合结构控制

修改文件：
- `docs/literature/catalog.md`
- `docs/literature/mineru_output/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning/auto/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning.md`
- `docs/literature/rl_env_reading_notes.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库已经有这篇论文的本地 Markdown，可直接作为后续阅读入口。
- 这篇论文对本课题最重要的价值不是“平台完全相同”，而是它把 rough-terrain vehicle 的 RL 任务定义拆得很完整。
- 对当前主线最合适的吸收方式是：先借鉴 reward / termination 逻辑，再在后续阶段逐步吸收地形 observation 和结构联合控制。

下一步：
- 继续辅助用户精读该文，并把其 `observation / action / reward / termination / curriculum` 映射到本课题的 Isaac Lab 环境设计上。

## 2026-03-21

已完成：
- 根据用户提出的要求，补充并固化了文献阅读类任务的交互协议。
- 在 `AGENTS.md` 的研究交互部分新增文献阅读辅助规则，明确：
  - 先确认单篇阅读目标
  - 默认按文章写作顺序推进提问
  - 提问逻辑优先遵循“是什么 -> 为什么 -> 联想与反思”
  - 每轮回答后需要进行纠正、补充与整理
  - 若理解不充分，允许围绕同一问题继续二次追问
- 确认当前 `Wiberg 等 - 2022` 的阅读目标为：
  - 主目标：整体掌握文章内容与逻辑
  - 次目标：提炼并学习 RL 环境设计
- 同步更新项目当前状态与长期会话结论，避免后续会话丢失这条协作规则。

修改文件：
- `AGENTS.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 本仓库后续的文献辅助阅读默认采用“教师式带读”而不是直接给结论。
- 对高相关文献，后续应先帮助用户掌握文章整体逻辑，再进入 env 设计细节和与本课题的迁移讨论。

下一步：
- 按新的交互协议，从 `Wiberg 等 - 2022` 的引言开始，依照文章顺序继续带读。
## 2026-03-22

已完成：
- 围绕 `Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning` 开展了一轮问答式精读，重点聚焦 RL 环境设计而非全文泛读。
- 将本轮对话中关于任务定义、observation、action、reward、termination、curriculum、evaluation 的梳理整理为结构化阅读笔记。
- 在该文献的 MinerU 输出目录下新增 `reading_notes.md`，便于后续直接在文献旁复习，不再只依赖聊天记录。
- 同步更新 `docs/current_status.md`，记录该文献目录下已形成可复用阅读笔记这一状态。

修改文件：
- `docs/literature/mineru_output/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning/auto/reading_notes.md`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已将该文献的第一轮精读结论沉淀为本地笔记，核心包括：
  - 任务定义应区分“目标”和“结果表现”
  - observation 可整理为地形感知、本体状态、任务相关信息三组
  - reward 设计应按“主任务 + 行为质量约束 + 终止条件 + 评估指标”来理解
  - curriculum、自然化 reset、训练/评估地形分离是该文献的重要训练组织方法

下一步：
- 继续对比后续 rough-terrain RL 文献，形成跨文献的可迁移设计共识，再回到本课题任务定义收敛。

## 2026-03-22

已完成：
- 安装并配置了独立的 `MinerU` 工作环境 `.venv-mineru`，避免污染现有 Isaac Lab 环境。
- 首次运行中补齐了 MinerU 所需的本地模型缓存，包括主模型、版面分析、阅读顺序、OCR、表格识别等依赖。
- 将 `Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain.pdf` 按仓库既定脚本流程转换为 Markdown。
- 围绕该文献完成了一轮问答式精读，重点提炼其 `observation / action / reward / termination / curriculum` 设计。
- 在该文献对应目录下新增 `reading_notes.md`，沉淀可复用阅读笔记，服务后续跨文献横向对比。

修改文件：
- `docs/literature/mineru_output/Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain/auto/Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain.md`
- `docs/literature/mineru_output/Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain/auto/reading_notes.md`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 该文献提供了一种更轻量的 rough-terrain RL 任务定义：高层 action、简洁 observation、极简 reward、单一维度 curriculum。
- 相比 `Wiberg 2022`，它更适合作为“任务简化、课程推进、goal-directed mobility 设计”的参考，而不是多执行器联合控制模板。
- 当前已具备至少两篇高相关文献的本地 Markdown 与结构化阅读笔记，后续可继续积累 2-3 篇后开展横向对比与本课题方案规划。

下一步：
- 继续精读 2-3 篇高相关文献并整理阅读笔记。
- 在文献样本足够后，系统输出面向本课题的横向对比与方案规划。

## 2026-03-22

已完成：
- 将 `Bouton和Gao - 2023 - MARCEL mobile active rover chassis for enhanced locomotion.pdf` 转换为 Markdown。
- 基于文献内容判断其更适合作为“结构动机与机理解释”参考，而不是当前阶段的 RL 环境配置主文献。
- 按用户要求，将该文献标记为后续撰写论文动机部分时应回看的参考文献。

修改文件：
- `docs/literature/mineru_output/Bouton和Gao - 2023 - MARCEL mobile active rover chassis for enhanced locomotion/auto/Bouton和Gao - 2023 - MARCEL mobile active rover chassis for enhanced locomotion.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `MARCEL` 与当前课题在“主动内部关节提升轮式平台通过能力”的动机层面较高相关。
- 但其不作为当前 RL 环境配置主线文献，后续写动机与结构价值时再重点回看。

下一步：
- 继续把阅读重点收敛到 RL 环境配置相关文献上。


## 2026-03-23

已完成：
- 读取仓库启动上下文，确认当前文献工作应优先围绕 RL 环境与训练设计主线展开。
- 检查 `docs/literature/` 目录、文献目录索引和 `rl_env_reading_notes.md`。
- 按“直接涉及 RL 训练/策略设计”的标准，从现有文献中筛出 17 篇相关 PDF。
- 新建 `docs/literature/rl_training_strategy_pdfs_2026-03-23/`，并将筛选出的 PDF 复制到该目录中，便于后续集中阅读。

修改文件：
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前独立整理出的 RL 训练策略相关 PDF 目录为 `docs/literature/rl_training_strategy_pdfs_2026-03-23/`。
- 该目录当前包含 17 篇文献，覆盖 rough terrain vehicle、articulated robot、curriculum、sim-to-real、state estimator joint training 等主题。

下一步：
- 若需要进一步收敛，可在这 17 篇中再细分出“最贴近本课题完整车 RL baseline”的高优先级子集。

已完成：
- 将本轮讨论确定的两阶段 RL 训练主线写入项目记忆文件。
- 更新 `docs/current_status.md`，把旧的“速度跟踪/平地加入球铰”表述替换为新的两阶段目标。
- 更新 `docs/conversation_history.md`，固化阶段 1 与阶段 2 的职责边界、任务定义和研究含义。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 阶段 1 正式定义为“平地 + 本体感知 + 固定球铰 + 目标导向移动”。
- 阶段 2 正式定义为“球铰纳入控制 + 底层 PID 与逆运动学映射 + 多样地形 + 外部感知与本体感知融合”。

下一步：
- 按新的阶段 1 目标，重写 env 的 observation、reward、termination、reset 与目标采样逻辑。

已完成：
- 将当前项目工作区整理后准备同步到 GitHub 远端 `origin/main`。

修改文件：
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前本地仓库状态已与待推送内容对齐，准备作为最新项目快照上传到 GitHub。

## 2026-03-24

已完成：
- 优化了根目录 `IK_iteration.mlx` 的符号推导脚本。
- 为 `R01`、`u_i`、`R_local`、`R_w`、`w_i`、`R03`、`R_rpy`、`R_v`、`v_i`、约束方程、半角代换结果、分子分母、多项式以及 `A/B/C` 系数补充了命令行输出。
- 为关键表达式统一增加 `expand + simplify` 化简流程，便于将移相三角表达式尽量压缩为更标准的 `sin/cos` 形式后再核对文献公式。
- 重新打包生成更新后的 `IK_iteration.mlx`。

修改文件：
- `IK_iteration.mlx`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 live script 在每一步关键推导后都会显示结果，更适合逐步检查逆运动学推导链路。
- 当前脚本会先做展开再做符号化简，表达式可读性比原版更高。

下一步：
- 在 MATLAB 中实际运行 `IK_iteration.mlx`，确认本机符号工具箱对 `simplify(..., ''Steps'', 100, ''IgnoreAnalyticConstraints'', true)` 的输出形式满足预期。

## 2026-03-26

已完成：
- 对比 `USD/complete_car.usd` 与 `USD/complete_car_equivlent.usd` 的机器人本体层级和关节树。
- 新增 `scripts/isaac_sim/align_complete_car_structure_to_equivalent.py`，用于按 equivalent 主链清理 `complete_car.usd` 机器人子树。
- 按用户要求，仅在 `/World/complete_car_final` 及其 `joints/` 范围内执行结构树收敛。
- 删除了 12 个多余的 SPM 腿部刚体：
  - `spm1_leg1_proximal`、`spm1_leg1_distal`、`spm1_leg2_proximal`、`spm1_leg2_distal`、`spm1_leg3_proximal`、`spm1_leg3_distal`
  - `spm2_leg1_proximal`、`spm2_leg1_distal`、`spm2_leg2_proximal`、`spm2_leg2_distal`、`spm2_leg3_proximal`、`spm2_leg3_distal`
- 删除了 `joints/` 下对应的 12 个 fixed joint，使保留链路收敛为 `base -> virtual_z -> virtual_y -> platform`。
- 生成编辑前备份 `USD/complete_car.usd.spm_leg_cleanup.bak`。
- 复查修改结果，确认 `/World/complete_car_final` 下已不再包含上述腿部刚体，`joints/` 下也只保留 equivalent 主链所需关节。

修改文件：
- `USD/complete_car.usd`
- `USD/complete_car.usd.spm_leg_cleanup.bak`
- `scripts/isaac_sim/align_complete_car_structure_to_equivalent.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `complete_car.usd` 的机器人本体结构树已按 equivalent 主链收敛，不再保留多余的 SPM 腿部层级。
- 这一步只处理机器人本体层级，不涉及场景层 `/Environment`、`/Render`、`/physicsScene` 以及根级 `/visuals`、`/colliders`、`/meshes`。
- 当前资产仍存在未解决问题，包括轮子零速 drive、损坏的 visual 引用、远端 `Example_Rotary` 引用和内嵌 `PhysicsScene` 风险。

下一步：
- 在新的结构树基础上继续清理 `complete_car.usd` 的 drive、损坏引用与 replicated 不兼容项，再重新验证 `Play` 时是否仍出现 transform 爆炸。

已完成：
- 新增 `scripts/isaac_sim/add_wheel_friction_material.py`，用于给 `complete_car.usd` 的 6 个轮子 collision 子树统一绑定 physics material。
- 在 `USD/complete_car.usd` 中新增共享材质 `/World/complete_car_final/Looks/wheel_physics_material`。
- 将该材质参数设置为：`staticFriction=1.0`、`dynamicFriction=1.0`、`frictionCombineMode=multiply`。
- 将该材质绑定到 6 个轮子的 `collisions` 子树。
- 生成编辑前备份 `USD/complete_car.usd.wheel_friction.bak`。
- 复查确认材质属性和 6 个 wheel collision 绑定均已写入 USD。

修改文件：
- `USD/complete_car.usd`
- `USD/complete_car.usd.wheel_friction.bak`
- `scripts/isaac_sim/add_wheel_friction_material.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `complete_car.usd` 的 6 个轮子已不再依赖默认地面摩擦，而是显式使用统一的轮胎 physics material。
- 这一步只增加轮子接触摩擦参数，不处理轮子 drive、visual 引用错误、远端 `Example_Rotary` 引用和 `PhysicsScene` 风险。

已完成：
- 将 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 从原始关节直控脚本改为第一版 Isaac Sim IK 键控验证脚本。
- 将键盘控制对象从“6 个球铰关节角”改为“前后两个平台目标姿态”。
- 接入 `IK_3RRR_Spherical`，实现每帧根据目标姿态解算前后两组 3 电机角，并映射到 6 个球铰关节目标。
- 保留轮子速度控制，并增加周期性调试输出：`rpy_des / q_ik / q_sim / residual`。
- 将资产路径切换到 `USD/complete_car.usd`，机器人根路径切换到 `/World/complete_car_final`。
- 对更新后的脚本执行了 `python3 -m py_compile` 语法检查，结果通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已有一个可用于“姿态目标 -> IK -> 球铰目标 -> Isaac Sim 读回对比”的第一版键控验证脚本。
- 当前脚本仍使用第一轮假设的 `IK -> sim joint` 顺序、`signs` 和 `biases`，后续需要结合实际运动方向做标定。

已完成：
- 为 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 增加 CSV 日志功能。
- 新增日志目录 `results/ik_keyboard_logs/`，脚本启动时会自动创建时间戳日志文件。
- 日志内容包含 `rpy_des`、`q_ik`、`q_sim`、前后球铰残差以及 `ik_error` 字段，并在每次快照打印时同步落盘。
- 在终端调试输出中增加 `log_path` 字段，便于定位本次运行对应的日志文件。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 IK 键控验证脚本除终端快照外，还能把关键结果稳定保存到 CSV，便于后续直接读取和复盘。

## 2026-03-26

已完成：
- 重新梳理了 `test_ik_keyboard.py` 的验证目标，确认用户当前需要的是“静态几何一致性验证”，而不是“姿态命令下发后由 drive 跟踪”的控制执行验证。
- 将 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 改为新的静态一致性验证逻辑：
  - 键盘直接摆动 6 个球铰等效关节角
  - 每帧读取前后 platform 相对各自 base 的当前姿态
  - 将当前姿态送入 `IK_3RRR_Spherical`
  - 将 IK 预测关节角与 Isaac Sim 当前实际关节角直接对比
- 在脚本中新增前后 `base/platform` prim 路径读取、相对旋转矩阵提取，以及 `Rz(yaw) @ Ry(pitch) @ Rx(roll)` 对应的 ZYX 欧拉角反解。
- 保留并适配了 CSV 日志落盘，日志现记录当前平台姿态、手动关节命令、IK 预测关节角、Isaac Sim 实际关节角、残差和 `ik_error`。
- 对修改后的脚本执行了 `python3 -m py_compile` 语法检查，结果通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `test_ik_keyboard.py` 不再把 IK 输出回写给 Isaac Sim 关节执行，而是作为“当前姿态 -> IK 预测关节角”的几何一致性验证脚本使用。
- 之后读取日志时，应把 `q_ik` 与 `q_sim` 的差异理解为静态映射误差、坐标定义误差、零位/符号/偏置标定误差，而不再理解为 drive 跟踪误差。

下一步：
- 运行新的 `test_ik_keyboard.py`，分别做前球铰和后球铰的单轴扫描，进一步标定 `IK_SIGNS_*`、关节顺序和偏置。
## 2026-03-27

已完成：
- 读取并分析了 `results/ik_keyboard_logs/ik_keyboard_2026-03-27_09-58-33.csv`。
- 统计确认该日志共 160 条采样，`ik_error` 全程为空，6 个 residual 全为 `0.0`。
- 统计确认 `joint_cmd` 与 `q_sim` 的误差整体较小，说明 Isaac Sim 关节执行跟踪基本正常。
- 统计确认 `q_ik` 与 `q_sim` 长期存在几十度级系统偏差，前后球铰都存在，且并非只出现在瞬态阶段。
- 结合 `test_ik_keyboard.py` 与 `IK_model.py` 的当前实现，确认本轮主要问题是 IK 比较链路中的零位/分支/映射定义未与仿真关节约定对齐，而不是 IK 方程求解失败。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 IK 键盘验证脚本的 residual 为 0，只能说明“给定姿态存在一组数学合法解”，不能说明“该解已映射回 Isaac Sim 当前实际关节分支”。
- 后续应优先标定零命令姿态下的球铰零位、分支选择和 `signs/biases`，再继续用该脚本做一致性验证。

下一步：
- 在 `test_ik_keyboard.py` 中把当前零命令姿态作为映射基准重新标定，并验证 `read_relative_rpy -> IK -> map_to_sim_joints -> q_sim` 是否能闭合。
已完成：
- 直接检查 `USD/complete_car.usd` 的 SPM 主链层级，确认零位姿态偏置固定存在于 `spm*_base -> spm*_spherical_virtual_z` 之间。
- 在 `USD/complete_car.usd` 中新增 `/World/complete_car_final/spm1_base/spm1_base_ref` 与 `/World/complete_car_final/spm2_base/spm2_base_ref`。
- 新增脚本 `scripts/isaac_sim/add_spm_base_reference_frames.py`，用于为当前 complete car 资产补写上述两个参考系，并自动生成 `USD/complete_car.usd.base_ref.bak` 备份。
- 重新打开 stage 验证新增 prim 后，确认 `spm1_base_ref -> spm1_platform` 与 `spm2_base_ref -> spm2_platform` 的相对 ZYX `rpy` 均已接近零。

修改文件：
- `USD/complete_car.usd`
- `scripts/isaac_sim/add_spm_base_reference_frames.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 USD 已具备两个固定在 base 上、且在机械零位与 platform 轴方向对齐的姿态参考系，可作为后续平台 `rpy` 读取的正确起点。
- 后续 `test_ik_keyboard.py` 应切换到 `spm*_base_ref -> spm*_platform` 读取零位姿态，而不应继续直接使用 `spm*_base -> spm*_platform`。

下一步：
- 在 `test_ik_keyboard.py` 中改用 `spm*_base_ref` 作为姿态参考 frame，并重新验证零位 `rpy` 与 IK 输入链路。
已完成：
- 将 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 的平台姿态读取基准从 `spm*_base -> spm*_platform` 改为 `spm*_base_ref -> spm*_platform`。
- 保留原有 `Rz(yaw) -> Ry(pitch) -> Rx(roll)` 的 ZYX 欧拉角分解与 IK 求解逻辑，仅替换姿态参考 frame。
- 对修改后的脚本执行 `python3 -m py_compile`，语法检查通过。
- 使用与脚本一致的读取公式重新检查机械零位，确认前球铰 `rpy≈[5.493e-06, 6.94e-07, -2.571e-06] deg`、后球铰 `rpy≈[-1.4661e-05, -1.3655e-05, 4.951e-06] deg`，可视为零。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 IK 静态验证脚本的 `rpy` 输入参考系已与 USD 中补入的零位参考 frame 对齐。
- 后续若 `q_ik` 与 `q_sim` 仍不一致，应优先继续检查 `IK_model.py` 输出到仿真关节的零位、分支与符号/偏置映射，而不是继续怀疑平台姿态读取坐标系。

下一步：
- 在已对齐的姿态输入前提下，继续标定 `IK_SIGNS_FRONT/REAR`、`IK_BIASES_FRONT/REAR` 与分支初值。
已完成：
- 在 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 中加入启动零偏标定逻辑。
- 脚本启动后会先对 6 个球铰保持零目标、对 6 个轮子保持零轮速，先静置 `240` 步，再连续采样 `120` 步，对前后 `spm*_base_ref -> spm*_platform` 的原始 `rpy` 求均值作为 `rpy_bias`。
- 后续 IK 输入改为 `raw_rpy - rpy_bias`，不再直接使用原始相对姿态。
- CSV 日志新增 `raw / bias / corrected` 三组平台 `rpy` 字段，便于区分物理稳态偏置与送入 IK 的校正姿态。
- 对修改后的脚本执行 `python3 -m py_compile`，语法检查通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 IK 键控验证脚本已具备启动零偏标定能力，可直接用新日志判断“原始平台姿态偏置”和“校正后送入 IK 的姿态”是否分离成功。

下一步：
- 重新运行脚本生成新日志，先检查 `front/rear_*_cur_deg` 是否在零命令稳态下接近 0，再继续分析 `q_ik` 与 `q_sim` 的剩余差异。
已完成：
- 读取并分析 `results/ik_keyboard_logs/ik_keyboard_2026-03-27_17-20-44.csv`，验证加入启动零偏标定后的新日志格式。
- 统计确认零命令稳态下，平台原始姿态 `raw_rpy` 仍存在小幅物理偏置，但校正后 `corrected_rpy` 已明显逼近零。
- 前平台 `corrected_rpy` 均值约为 `[0.013734, -0.010834, -0.00631] deg`，后平台约为 `[-0.001878, 0.000419, 0.003239] deg`。
- 同时确认 `q_ik` 与 `q_sim` 在零命令稳态下仍有系统差异，说明当前主问题已从姿态读取收敛到关节映射标定。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 启动零偏标定已基本解决“平台 `rpy` 输入不为零”的问题，后续应优先继续标定 `IK_SIGNS_*`、`IK_BIASES_*` 与分支初值。

下一步：
- 在零偏校正保持不变的前提下，针对前后球铰分别做单轴扫描，继续拟合 `q_ik -> q_sim` 的零位、符号和偏置。
已完成：
- 重写 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`，将其从“关节直控 + 反算对照”脚本改为“姿态目标 -> IK -> joint target -> articulation controller 跟踪”验证脚本。
- 键盘输入现直接修改前后平台的 `roll/pitch/yaw` 目标，不再直接修改 6 个球铰关节角。
- 启动阶段新增联合零位标定：同时估计平台 `rpy` 零偏和 Sim 当前球铰关节零位，并将后者作为 `map_to_sim_joints()` 的零位偏置。
- 控制链中新增两级一阶平滑：先对姿态目标做平滑，再对 IK 生成的 joint target 做平滑，最后再把 `q_cmd` 发送给 articulation controller。
- 日志字段改为完整记录 `raw/meas/des/cmd` 姿态、`q_ik/q_cmd/q_sim`、joint 跟踪误差以及 IK residual。
- 对重写后的脚本执行 `python3 -m py_compile`，语法检查通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `test_ik_keyboard.py` 已能直接验证三个关键问题：姿态目标是否稳定送进 IK、IK 生成的 joint target 是否和零位标定一致、articulation controller 是否能平滑跟踪 joint target。

下一步：
- 实际运行新脚本并读取新日志，检查 `rpy_des -> rpy_meas`、`q_cmd -> q_sim` 和 `track_err` 三条误差曲线，再决定是否需要继续调 `IK_SIGNS_*`、姿态/关节平滑系数或底层 drive 参数。
已完成：
- 读取并分析 `results/ik_keyboard_logs/ik_keyboard_2026-03-27_18-53-34.csv`，评估重构后 `test_ik_keyboard.py` 的整条控制链。
- 确认 `q_cmd -> q_sim` 跟踪效果较好，前后球铰关节平均绝对跟踪误差均在约 `0.02~0.07 deg` 量级，说明 articulation controller 可以平滑跟踪 joint target。
- 确认 IK 全程可解，`residual` 为 0，`ik_error` 为空。
- 同时确认 `rpy_cmd -> rpy_meas` 误差很大，前平台平均绝对误差约 `[5.62, 4.69, 4.71] deg`，后平台约 `[2.42, 0.50, 2.20] deg`，且单轴姿态命令会激发错误轴或相反方向。
- 据此得出当前关键结论：问题不在关节跟踪，而在“IK 电机角”和“USD 等效球铰关节坐标”不是同一组坐标，无法直接把 IK 输出当作现有等效模型的关节目标。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现阶段已验证：IK 可稳定求解，joint target 可被底层平滑跟踪；但姿态目标通过 IK 直接驱动当前等效球铰模型这条路线在语义上不成立。

下一步：
- 回到研究层重新决定架构：是保留等效球铰姿态控制并让 IK 仅作为真实电机角映射层，还是重建一个真实电机坐标可控的下层模型。
已完成：
- 明确了当前仿真建模的语义：USD 中 3 个等效球铰关节角本身就是移动平台姿态坐标，而不是 3-RRR 真实电机角代理。
- 因此重新界定 RL 与 IK 的角色分工：RL 在仿真中应直接控制等效球铰姿态角；IK 只负责把平台姿态并行映射为真实机构电机角，供后续可能的实物阶段使用。
- 据此停止继续沿“IK 电机角直接驱动当前等效球铰模型”这条路线投入。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 RL 主线重新收敛为：直接控制 3 个等效球铰姿态角和轮子动作；IK 暂不进入仿真闭环控制。

下一步：
- 回到 RL 环境设计与实现，明确动作空间、观测和奖励如何围绕等效球铰姿态控制来组织。

## 2026-03-28

已完成：
- 按 `literature-reading-notes` 的结构化方式整理 `Ha 等 - 2025 - Learning-based legged locomotion: State of the art and future perspectives`。
- 基于原始 PDF 提炼出该综述的整体逻辑、`MDP` 组成、训练框架、`sim-to-real` 路线以及 `control + learning` 组合方式。
- 将阅读笔记落盘到对应文献目录下，保持与现有 `Wiberg 2022`、`Xu 2024` 笔记一致的仓库组织方式。
- 同步更新项目状态与长期会话记忆，避免后续重复整理该综述。

修改文件：
- `docs/literature/mineru_output/Ha 等 - 2025 - Learning-based legged locomotion State of the art and future perspectives/auto/reading_notes.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已形成一份可直接复用的综述型阅读笔记，重点不是复述全文，而是为本课题提炼任务设计与训练组织方法。
- 该综述支持当前已确定的两阶段主线：先做最小可训练 baseline，再逐步加入外感知、分层控制和更强的 sim-to-real 机制。

下一步：
- 若继续沿文献主线推进，可把 `Ha 2025` 与 `Wiberg 2022`、`Xu 2024` 做一次横向对比，专门整理“baseline 如何定义、复杂度如何分阶段引入”的共性结论。

## 2026-03-30

已完成：
- 检查用户新增的地形相关脚本，确认有效源码/文档为 `mgdp_terrain_preview.py`、`run_terrain_preview.sh`、`README.md`，并将其统一整理到 `scripts/isaac_sim/terrain_preview/`。
- 修正 `mgdp_terrain_preview.py` 的仓库根路径解析逻辑，避免默认导出 USD 路径错误指向仓库外。
- 修正 `README.md` 中旧的启动路径示例，使其与实际目录 `scripts/isaac_sim/terrain_preview/` 一致。
- 对地形脚本执行静态校验：`python3 -m py_compile scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py` 通过，`bash -n scripts/isaac_sim/terrain_preview/run_terrain_preview.sh` 通过。
- 实际尝试使用 `/home/lbz/isaac-sim/python.sh` 以 `--headless --frames 1 --gallery stage1` 启动地形预览脚本。

修改文件：
- `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
- `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`
- `scripts/isaac_sim/terrain_preview/README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前地形预览脚本的仓库内路径与启动包装关系已整理清楚，脚本层不存在语法错误。
- 这次实际启动未能进入场景执行阶段，阻塞来自本机 Isaac Sim 图形环境：日志报错 `Vulkan 1.1 is not supported`、`no CUDA-capable device is detected`，随后段错误退出。
- 因此当前可得结论是：脚本包本身可以作为 Isaac Sim 启动入口使用，但这台机器当前不具备完成 Isaac Sim 启动的图形/驱动条件。

下一步：
- 若要继续验证窗口显示或 USD 导出，应在具备可用 Vulkan / CUDA / 显示环境的 Isaac Sim 主机上执行 `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`。

已完成：
- 新增 `scripts/isaac_sim/terrain_preview/terrain_builder.py`，将地形构建逻辑从单独预览脚本中抽成可复用模块。
- 重写 `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`，改为复用公共地形模块构建 gallery。
- 修改 `scripts/isaac_sim/control_keyboard.py`，使其在打开 `USD/complete_car.usd` 后、`World.reset()` 前可同步向同一 stage 注入一块地形。
- 当前 `control_keyboard.py` 新增 `--terrain`、`--terrain-seed` 参数；默认地形为 `slope_ramp`，也可切换为 `stairs_up`、`gap`、`corridor` 等，或用 `--terrain none` 禁用。
- 为避免已有地面把 `gap` 之类地形覆盖，脚本会优先尝试关闭若干常见默认 ground prim。
- 对 `control_keyboard.py`、`mgdp_terrain_preview.py`、`terrain_builder.py` 执行 `python3 -m py_compile`，语法检查通过。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
- `scripts/isaac_sim/terrain_preview/terrain_builder.py`
- `scripts/isaac_sim/terrain_preview/README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现在不需要分别启动两个 Isaac Sim 进程；直接运行 `control_keyboard.py` 就可以把车辆和单块地形放进同一个场景里做键盘联调。
- 该改动目前已完成静态校验，但由于当前主机的 Isaac Sim 图形环境仍有 Vulkan/CUDA 阻塞，尚未在本机完成实际窗口联调验证。

下一步：
- 在可正常启动 Isaac Sim 的主机上优先测试 `python3 scripts/isaac_sim/control_keyboard.py --terrain slope_ramp`，确认车辆初始位置、地面关闭逻辑和碰撞行为符合预期。

已完成：
- 定位 GitHub 推送失败原因，确认不是 SSH 认证问题，而是 `Drawing/完整小车等效串联.SAT` 超过 GitHub 普通仓库 100 MB 单文件限制。
- 按当前新要求将 `.SAT` 文件加入根目录 `.gitignore`，后续不再作为普通 Git 提交内容上传。
- 同步把这一推送约束写入项目状态与长期会话记忆，避免后续再次因为 `.SAT` 阻塞整仓上传。

修改文件：
- `.gitignore`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现阶段仓库的普通 Git 上传路径应排除 `.SAT` 原始 CAD 文件；否则会再次触发 GitHub 预接收钩子拒绝。

下一步：
- 从最近一次本地提交中移除已纳入历史的 `.SAT` 文件，重做提交并重新推送到 `origin/main`。

## 2026-03-30

已完成：
- 检查 `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh` 的执行失败原因，确认直接 `./scripts/...` 报“权限不够”是因为脚本缺少执行位，而不是 Bash 语法错误。
- 在本机实际文件系统中确认可用 Isaac Sim 启动器路径为 `/home/ubuntu/isaacsim/python.sh`，不是脚本中旧的 `/home/lbz/isaac-sim/python.sh`。
- 将 `run_terrain_preview.sh` 的默认 `ISAAC_SIM_ROOT` 修正为 `/home/ubuntu/isaacsim`，并同步更新 `scripts/isaac_sim/terrain_preview/README.md` 中的说明。
- 同步更新项目状态与长期会话记忆，避免后续继续沿用旧路径判断脚本不可用。

修改文件：
- `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`
- `scripts/isaac_sim/terrain_preview/README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前地形预览包装脚本的默认 Isaac Sim 路径已与本机真实安装位置对齐。
- 修复后若仍无法启动 Isaac Sim，应优先归因为本机 Vulkan / CUDA / 显示环境问题，而不是脚本权限或默认路径问题。

下一步：
- 给 `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh` 补上执行权限后，直接用 `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --gallery stage1` 做一次本机验证。

## 2026-03-30

已完成：
- 复现并定位 `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh` 在激活 `env_isaacLab` 时的真实报错链：不是地形脚本逻辑错误，而是 `run_terrain_preview.sh` 继承了 `CONDA_*` 环境变量，且 `mgdp_terrain_preview.py` 在 `SimulationApp` 初始化前就导入了 `omni.timeline`。
- 修改 `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`，在调用 Isaac Sim `python.sh` 之前主动 `unset` 常见 `CONDA_*` 变量。
- 修改 `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`，改为先创建 `SimulationApp`，再导入 `omni.timeline`、`omni.usd` 与 Isaac Sim 相关模块。
- 重新执行 `python3 -m py_compile scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py` 与 `bash -n scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`，静态检查通过。
- 实际执行 `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --headless --frames 1 --gallery stage1`，本次已成功跑通并生成 `outputs/isaacsim/mgdp_terrain_stage1.usd`。

修改文件：
- `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
- `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前地形预览脚本已经可以从激活的 `env_isaacLab` shell 直接通过包装脚本启动，不再需要用户手工先 `conda deactivate`。
- 之前的 `ModuleNotFoundError: No module named 'omni.timeline'` 已被修复。
- 当前主机在 Isaac Sim 启动日志里仍会出现 GPU / CUDA / 显示相关警告，但至少对当前 `--headless --frames 1 --gallery stage1` 的 USD 导出路径不再构成阻塞。

下一步：
- 若要继续验证更多 gallery，可直接执行 `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --gallery both`，或在 headless 模式下继续导出其他地形 USD。

## 2026-03-30

已完成：
- 复现 `python scripts/isaac_sim/control_keyboard.py --terrain none` 的失败链路，先确认原始报错不是地形逻辑，而是当前脚本写死了错误的机器人根 prim。
- 在宿主 Isaac Sim 下重新检查 `USD/complete_car.usd`，确认 `/World/complete_car_final` 不存在，当前真实机器人根路径仍是 `/World/complete_car_alternative`。
- 修改 `scripts/isaac_sim/control_keyboard.py`，将 `ROBOT_PRIM_PATH` 改为 `/World/complete_car_alternative`。
- 给 `control_keyboard.py` 加入从 conda shell 自动重启到宿主 `/home/ubuntu/isaacsim/python.sh` 的启动链，避免继续在错误的 Python/Isaac Sim 组合下运行。
- 给 `control_keyboard.py` 加入 `--headless`、`--frames` 与无显示环境自动 headless smoke 验证路径。
- 去掉脚本内此前加入的 `--portable-root` 注入；实测该路径会让本机 host 启动明显变慢甚至看似卡住，而使用宿主默认缓存路径可快速完成启动。
- 实际验证 `python -u scripts/isaac_sim/control_keyboard.py --terrain none --headless --frames 1`，本次已正常退出且返回码为 0。
- 实际验证 `timeout --signal=SIGINT 20s python -u scripts/isaac_sim/control_keyboard.py --terrain none`，本次脚本成功进入交互态并持续运行到超时，返回码为 124，说明不是崩溃退出。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `control_keyboard.py` 当前可用的运行根 prim 是 `/World/complete_car_alternative`。
- 当前机器上要稳定启动该脚本，应优先让它走宿主 `/home/ubuntu/isaacsim/python.sh`，而不是继续依赖激活中的 conda Python 解释器。
- 当前机器上不应再给该脚本强行注入新的 portable-root；这会放大 Isaac Sim 首次缓存初始化开销，影响“先跑起来”的目标。

下一步：
- 若要继续人工键盘联调，可直接执行 `python scripts/isaac_sim/control_keyboard.py --terrain none` 或替换为其他 `--terrain` 选项。

## 2026-03-30

已完成：
- 解释并复核 `scripts/isaac_sim/control_keyboard.py` 的当前键盘控制逻辑，确认 `W/S` 为六轮统一前进/后退轮速，`A/D` 为左右差速转向，数字小键盘为两个等效球铰的 6 个姿态自由度增量控制。
- 检查轮速与球铰控制链路，确认两者都已经有一阶平滑；其中轮速与球铰平滑系数此前均为 `0.20`。
- 诊断“前进后退像拖动不是轮子在转”的原因，确认不是轮子命令失效，而是 `--terrain none` 时缺少有效 ground contact，导致地面接触链路不成立。
- 修改 `scripts/isaac_sim/control_keyboard.py`：在 `--terrain none` 下自动创建 `ground plane`，并给地面与六个轮子碰撞体统一绑定 `static_friction=0.5`、`dynamic_friction=0.5` 的共享物理材质。
- 同步下调键盘联调默认速度与响应：`WHEEL_LINEAR_SPEED=2.5`、`WHEEL_TURN_SPEED=1.0`、`BALL_JOINT_DELTA=0.005`、`WHEEL_VELOCITY_SMOOTHING=0.10`、`BALL_POSITION_SMOOTHING=0.10`。
- 实际执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，静态检查通过。
- 实际执行 `timeout 90s python -u scripts/isaac_sim/control_keyboard.py --terrain none --headless --frames 1`，本次返回码为 `0`。
- 额外编写并执行宿主 Isaac Sim 诊断脚本，验证补地面与摩擦后小车在 120 步内前进约 `0.36 m`，且六个轮子角速度始终接近 `1 rad/s`。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `control_keyboard.py` 在 `--terrain none` 下不再是“无地面接触”的状态，车体可通过轮地摩擦产生真实推进，而不是仅表现为拖动感。
- 当前脚本内车轮速度和平滑、球铰步进和平滑都已下调，默认联调速度明显比之前更温和。
- 当前终端环境下 Isaac Sim 启动较慢且会伴随无 GPU、远端 `Example_Rotary` 引用等警告，但这些不影响本轮键盘控制修复结论。

下一步：
- 在具备可用图形环境的 Isaac Sim 主机上直接执行 `python scripts/isaac_sim/control_keyboard.py --terrain none` 做一次窗口联调，重点观察轮子可视旋转、底盘实际位移和球铰姿态响应是否与新的减速参数一致。

## 2026-04-02

已完成：
- 新增 `scripts/isaac_sim/preview_stage1_tile.py`，提供 Isaac Sim 中单独查看单个 `stage1` tile 的入口。
- 脚本当前支持两种选块方式：`--row/--col` 复现当前课程地图中的某一块，或 `--terrain-name` 直接指定某类地形。
- 为避免 `--list-terrains` 在 Isaac Sim 启动前触发整条任务包导入链，脚本改为按文件路径直接加载 `stage1_terrain.py`，不再依赖完整包导入。
- 脚本默认会删除 `TerrainImporterCfg(terrain_type="plane")` 自动生成的默认 plane，并只导入当前单块 tile mesh。
- 脚本默认不实例化整车，只有显式传入 `--spawn-car` 时才加载机器人资产。
- 已执行 `python3 -m py_compile scripts/isaac_sim/preview_stage1_tile.py`，静态检查通过。
- 已执行 `python scripts/isaac_sim/preview_stage1_tile.py --list-terrains`，当前可正常列出全部 `stage1` terrain 名称。
- 已执行 `timeout 60s python -u scripts/isaac_sim/preview_stage1_tile.py --headless --device cpu --frames 1 --row 0 --col 0`，本次返回码为 `0`。

修改文件：
- `scripts/isaac_sim/preview_stage1_tile.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现在已经有一个比整张大地图 preview 更直接的检查入口，可优先用于核对单块地形的几何、原点和相机视角。
- `--list-terrains` 当前已不再受 `pxr` 提前导入问题影响。
- 当前这台无 GPU / 无正常显示环境的机器上，单 tile headless 冒烟可以正常退出，但不适合把窗口显示效果是否完全正确作为唯一验证标准。

下一步：
- 在有正常图形环境的 Isaac Sim 会话中执行 `python scripts/isaac_sim/preview_stage1_tile.py --row <r> --col <c>`，逐块核对 `stage1` 各类地形的真实视觉效果与坐标系位置。

## 2026-04-02

已完成：
- 按用户要求将 `scripts/isaac_sim/preview_stage1_tile.py` 的默认行为从“单块预览”改为“同时显示所有单独 tile”。
- 当前默认启动脚本时，会把 `stage1` 当前课程地图的全部 `20 x 10 = 200` 个 tile 作为独立 mesh 导入 Isaac Sim，并按固定 `tile-spacing` 分开摆放，不再拼成一整张连续地形。
- 保留旧能力：新增 `--single-tile` 开关，仍可按 `--row/--col` 只看某一块；`--terrain-name <name>` 也仍可按地形名单独生成一块。
- 调整脚本内部 origin 可视化逻辑：不再依赖 `TerrainImporter.configure_env_origins()`，而是直接为每个独立 tile 生成 1 个 frame marker。
- 当前所有独立 tile 的 prim 路径统一为 `/World/terrain/tile_rXX_cYY_<terrain_name>`，便于在 Stage 面板中逐块定位。
- 已执行 `python3 -m py_compile scripts/isaac_sim/preview_stage1_tile.py`，静态检查通过。
- 已执行 `python scripts/isaac_sim/preview_stage1_tile.py --help` 与 `python scripts/isaac_sim/preview_stage1_tile.py --list-terrains`，参数与地形枚举正常。
- 已执行 `timeout 120s python -u scripts/isaac_sim/preview_stage1_tile.py --headless --device cpu --frames 1`，gallery 默认路径返回码为 `0`。
- 已执行 `timeout 90s python -u scripts/isaac_sim/preview_stage1_tile.py --headless --device cpu --frames 1 --single-tile --row 0 --col 0`，单块回退路径返回码为 `0`。
- 本轮 headless 校验日志已落盘：
  - `results/preview_stage1_tile_gallery.log`
  - `results/preview_stage1_tile_single.log`

修改文件：
- `scripts/isaac_sim/preview_stage1_tile.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现在直接运行 `python scripts/isaac_sim/preview_stage1_tile.py`，进入的就是“所有独立 tile 分离展示”模式，而不是旧的单块预览模式。
- 若后续还需要只看某一块，不需要再写新脚本，直接加 `--single-tile` 即可。
- 当前这台无 GPU / 无图形显示环境的机器上，headless 返回码可以证明脚本链路可跑通，但窗口里的最终视觉效果仍应以图形环境下的 Isaac Sim 实际画面为准。

下一步：
- 在有正常图形界面的 Isaac Sim 会话里直接执行 `python scripts/isaac_sim/preview_stage1_tile.py`，确认 200 个独立 tile 的相对布局、坐标系和相机总览是否符合预期；若太密，可再调 `--tile-spacing`。

## 2026-04-03

已完成：
- 新增 `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`，用于直接实例化真实训练任务 `Complete-Car-Rl-Training-v0`，保存训练时的 stage USD，并导出完整 prim tree 与 `/World/terrain` 子树。
- 基于用户在可用 GPU 机器上导出的 `training_stage_num_envs10.usda`、`training_stage_num_envs10.usda.tree.txt` 与 `training_stage_num_envs10.usda.terrain_tree.txt` 复核训练场景结构。
- 确认训练环境中真正的地形 prim 只有 `/World/terrain/stage1` 一张；用户在窗口里看到的“多张地图”不是训练脚本重复导入地形，而是 `USD/complete_car.usd` 中残留的 `/World/terrain_preview` 被每个 `env_i/Robot` 引用复制。
- 新增 `scripts/isaac_sim/remove_complete_car_terrain_preview.py`，为 `USD/complete_car.usd` 创建备份 `USD/complete_car.usd.terrain_preview_cleanup.bak` 后，移除 `/World/terrain_preview` 子树。
- 重新打开 `USD/complete_car.usd` 验证，确认 `/World/terrain_preview` 已无效；当前资产顶层 prim 保持为 `/World`、`/Render`、`/physicsScene`。
- 按用户要求在 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py` 的 `terrain_dict` 首项加入 `flat: 0.2`。
- 同步在 `make_tile_by_name(...)` 中补上 `flat -> make_flat_tile(...)` 分支，并调整 `slope down` 的区间中点计算，使插入 `flat` 后现有 `choice` 逻辑仍能正确落入 `slope down` 区间。
- 执行 `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`，静态检查通过。
- 复核当前默认 `num_cols = 10` 下的列映射，结果已变为 `flat x2 -> slope down x2 -> pyramid x2 -> stairs down x2 -> stairs up x2`。

修改文件：
- `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
- `scripts/isaac_sim/remove_complete_car_terrain_preview.py`
- `USD/complete_car.usd`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 训练时的真实大地图只有 `/World/terrain/stage1`，之后若再看到多张“地图”，应优先排查机器人资产是否夹带 preview 几何，而不是先改训练地形导入逻辑。
- `USD/complete_car.usd` 当前已经清理为机器人资产，不再应包含 `terrain_preview`。
- 当前 Stage1 在不改 `choice` 框架的前提下，首个地形类型已改为 `flat`，且权重按用户要求设为 `0.2`。

下一步：
- 在用户有可用 GPU 的 Isaac Sim 会话里重新导出一次训练 stage，确认新的 `training_stage_num_envs10.usda.tree.txt` 中不再出现 `env_i/Robot/terrain_preview`。

## 2026-04-03

已完成：
- 按用户要求新增独立预览脚本 `scripts/isaac_sim/preview_stage1_last_six.py`，用于在不修改 `stage1_terrain.py` 的前提下，单独查看当前 stage1 地形列表最后六种地形的外观。
- 新脚本沿用 `preview_stage1_tile.py` 的总体方式：直接按文件路径加载 `stage1_terrain.py`，删除 `TerrainImporterCfg(terrain_type="plane")` 自动生成的默认 plane，将每个地形以独立 mesh 导入 Stage，并支持 `--show-origin`、`--spawn-car`、`--save-usd` 等常用预览参数。
- 当前 gallery 默认加载的后六种地形已确认是：`hurdle`、`gap`、`ramp`、`beam`、`new stairs down`、`pit`。
- 已执行 `python3 -m py_compile scripts/isaac_sim/preview_stage1_last_six.py`，静态检查通过。
- 已执行 `python scripts/isaac_sim/preview_stage1_last_six.py --list-terrains`，地形枚举正常输出。

修改文件：
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现在查看 `hurdle / gap / ramp / beam / new stairs down / pit` 的几何外观，不再需要临时改动训练用 `terrain_dict` 顺序或权重。
- 该需求已有独立脚本入口，后续若要导出对应 USD 或在窗口里逐块看这六类地形，可直接复用该脚本。

下一步：
- 在可用 GPU / 图形环境的 Isaac Sim 会话中执行 `python scripts/isaac_sim/preview_stage1_last_six.py --device cuda:0`，直接观察这六种地形的窗口效果；若需要离线核对 Stage 结构，可再加 `--save-usd <path>.usda`。

## 2026-04-03

已完成：
- 按用户进一步澄清后的要求，撤回对 `scripts/isaac_sim/preview_stage1_tile.py` 职责的改动，将其恢复为原先的 `20 x 10` 全课程 tile 分离画廊入口。
- 同时改造 `scripts/isaac_sim/preview_stage1_last_six.py`，使其在保持“只看后六种地形”目标不变的前提下，也采用与 `preview_stage1_tile.py` 相同的 `20 x 10` tile 画廊形式。
- 当前 `preview_stage1_last_six.py` 的 gallery 只使用 `terrain_names[-6:]`：`hurdle`、`gap`、`ramp`、`beam`、`new stairs down`、`pit`；列方向按这六类循环分配，行方向继续用于展示不同难度层。
- 已执行 `python3 -m py_compile scripts/isaac_sim/preview_stage1_tile.py scripts/isaac_sim/preview_stage1_last_six.py`，静态检查通过。
- 已执行 `python scripts/isaac_sim/preview_stage1_tile.py --list-terrains`，确认旧脚本再次输出完整 terrain 集。
- 已执行 `python scripts/isaac_sim/preview_stage1_last_six.py --list-terrains`，确认新脚本仅输出后六种地形。

修改文件：
- `scripts/isaac_sim/preview_stage1_tile.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `preview_stage1_tile.py` 现在再次代表“全部 stage1 tile 画廊”，不再被重定向到后六种地形预览。
- `preview_stage1_last_six.py` 现在是“后六种地形版的 20 x 10 tile 画廊”，更符合用户想直接比较这些尾部地形几何外观的用途。

下一步：
- 在有可用 GPU / 图形环境的 Isaac Sim 会话中执行 `python scripts/isaac_sim/preview_stage1_last_six.py --device cuda:0`，直接观察这套后六种地形的 `20 x 10` 画廊效果。

## 2026-04-03

已完成：
- 按用户要求调整 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py` 前段地形阈值，使默认 `num_cols = 10` 下的前 10 列映射变为：
  - 第 1 列 `flat`
  - 第 2 列 `slope down`
  - 第 3 列 `slope up`
  - 第 4-5 列 `uneven rough`
  - 第 6-7 列 `stairs down`
  - 第 8-9 列 `stairs up`
  - 第 10 列 `discrete obstacles`
- 在 `terrain_dict` 中新增独立地形名 `slope up`，并把 `slope down` / `slope up` 分别固定到 `descending=True` / `descending=False`，不再沿用原先在同一 `"slope down"` 区间内部再二分出上下坡方向的逻辑。
- 将原公开地形名 `"pyramid"` 重命名为 `"uneven rough"`；当前保留原内部生成函数 `make_pyramid_tile(...)`，但对外列出的 terrain name 已改为更符合其“起伏粗糙、不规则变化”外观的名字。
- 已执行 `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`，静态检查通过。
- 已执行一次映射核对，当前默认 10 列实际输出为：
  - `['flat', 'slope down', 'slope up', 'uneven rough', 'uneven rough', 'stairs down', 'stairs down', 'stairs up', 'stairs up', 'discrete obstacles']`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现在前 10 列地形分配已经和用户指定顺序一致。
- 原先视觉上容易误解的 `"pyramid"` 名称已从对外 terrain 列表中替换为 `"uneven rough"`。

下一步：
- 在 Isaac Sim 中重新执行相关 preview 脚本，确认新的前 10 列顺序和 `"uneven rough"` 名称是否与用户预期一致。

## 2026-04-03

已完成：
- 按用户要求修改 `scripts/isaac_sim/control_keyboard.py`，使 `--terrain stage1` 不再接入旧的 preview/gallery 地形，而是直接复用训练环境使用的整张 `stage1` 地形。
- 新的 `stage1` 键盘联调地形链路当前直接按文件路径加载 `stage1_terrain.py`，调用 `build_stage1_terrain_data()` 生成训练用 mesh，并按训练环境同样的逻辑在 `x/y` 方向整体减去 `border_size` 后导入 `/World/terrain/stage1/mesh`。
- 同步给 `control_keyboard.py` 增加训练地形出生点对齐：当前在 `--terrain stage1` 下，机器人会在初始化句柄后自动移动到训练首个 env origin `[4.0, 4.0, 0.3]`，而不是继续停在地图边缘默认原点。
- 将旧的 `terrain_preview.terrain_builder` 顶层导入改为按分支延迟导入，避免 `--terrain stage1` 路径在启动时被一个已不存在的 preview 依赖提前拦死。
- 已执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，静态检查通过。
- 已执行 `timeout 90s python -u scripts/isaac_sim/control_keyboard.py --terrain stage1 --headless --frames 1`，本次在当前无可用 CUDA 的工具环境中仍成功完成 1 帧 smoke run。
- 本次运行日志已明确打印：
  - `Built training stage1 terrain mesh: root=/World/terrain spawn_position=[4.0, 4.0, 0.3]`
  - `Applied shared terrain friction material: /World/terrain/stage1/mesh`
  - `Moved robot to terrain spawn position: [4.0, 4.0, 0.3]`
  - `Headless smoke validation finished successfully.`

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现在 `control_keyboard.py --terrain stage1` 已经和训练环境在“地形几何来源 + 地图坐标偏移 + 初始出生点”这三件事上对齐。
- 当前保留 `--terrain stage2|both` 的旧 MGDP gallery preview 路径不变；本轮只把 `stage1` 键盘联调路径改成了训练同款地形。

下一步：
- 在用户有可用 GPU 的 Isaac Sim 会话中直接运行 `python scripts/isaac_sim/control_keyboard.py --terrain stage1`，窗口确认车辆是否已落在训练地图首块区域而非边框。

## 2026-04-03

已完成：
- 按用户要求继续修改 `scripts/isaac_sim/control_keyboard.py`，将键盘驱动控制方式改成与训练环境同构的控制链路，而不是沿用原先的平滑 teleop 快捷逻辑。
- 当前脚本中的球铰控制已改为与训练一致的 `JointPositionAction` 语义：
  - 键盘输入先形成 `raw action`
  - 再按 `scale = 0.25` 与默认关节位置 offset 转成球铰位置目标
- 当前脚本中的轮子控制已改为与训练一致的 `JointVelocityAction` 语义：
  - `W/S/A/D/SPACE` 先形成左右轮侧的 `raw action`
  - 再按 `scale = 8.0` 与默认关节速度 offset 转成 6 个轮关节速度目标
- 在 articulation 初始化后，脚本现在会显式把球铰与轮子的驱动参数设成训练环境同一组值：
  - 球铰：`stiffness=80.0`、`damping=8.0`、`effort_limit=120.0`、`velocity_limit=6.0`
  - 轮子：`stiffness=0.0`、`damping=10.0`、`effort_limit=80.0`、`velocity_limit=20.0`
- 同步把 teleop 世界时间步改为与训练一致：
  - `physics_dt = 1 / 120`
  - `render_dt = 1 / 60`
  - `action decimation = 2`
  - 即键盘 action 以 `60 Hz` 刷新，并在两个物理子步间保持不变
- 已执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，语法检查通过。
- 已执行 `timeout 120s python -u scripts/isaac_sim/control_keyboard.py --terrain none --headless --frames 1`，返回码为 `0`；当前输出仍包含本机无可用 CUDA / 无驱动、只读缓存路径和远端 `Example_Rotary` 引用告警，但未出现本轮控制改动引入的 Python 级报错。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `control_keyboard.py` 现在已经不再是“人工调出来的一套近似 teleop 参数”，而是与训练任务共享同一套球铰位置控制 / 轮子速度控制语义、同一组驱动参数和同一时间步结构。
- 当前最直接可人工比对的轮速 target 区间为 `[-8, 8] rad/s`；如果后续手动联调时频繁接近 `20 rad/s` 的 PhysX 上限，应优先怀疑当前训练轮速 scale 偏大或地形/阻力导致策略想靠饱和输出来补偿。

下一步：
- 在有正常 GPU / 图形环境的 Isaac Sim 会话中直接运行 `python scripts/isaac_sim/control_keyboard.py --terrain stage1`，手动观察球铰响应和轮速 target 区间，再决定训练里的 `stiffness / damping` 与 `scale` 是否需要调整。

## 2026-04-03

已完成：
- 按用户要求，仅对 `scripts/isaac_sim/control_keyboard.py` 中训练同构控制参数区补充中文行内注释，说明各参数对应的物理含义、控制语义和单位。
- 本轮未改动任何控制数值、键位映射、关节目标生成逻辑或物理参数本身，只提升脚本可读性与后续人工联调时的可解释性。
- 已执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，语法检查通过。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `control_keyboard.py` 的训练同构参数块已经可以直接从代码注释中读出含义，不需要再反查训练配置文件或聊天记录。

下一步：
- 若还需要继续提升可读性，可再把“球铰 action -> 位置目标”和“轮子 action -> 速度目标”的公式说明补到对应函数上方。

## 2026-04-03

已完成：
- 按用户要求，继续修改 `scripts/isaac_sim/control_keyboard.py`，移除键盘联调路径里的球铰人工运动范围限制。
- 当前 `update_ball_joint_actions()` 不再对 `ball_action_raw` 做 `clamp` 限幅，球铰位置目标现在直接按：
  - `ball_target = default_position + raw_action * 0.25`
  累加生成。
- 同步删除参数区中的 `BALL_JOINT_ACTION_LIMIT`，并把启动打印信息改为“球铰 raw action 无界，仅按 scale 映射到位置目标”。
- 已执行 `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`，语法检查通过。
- 额外复核训练环境配置，确认当前 RL 训练任务本身仍保留球铰越界终止项：
  - `complete_car_rl_training_env_cfg.py`
  - `ball_joint_out_of_bounds`
  - `bounds = (-0.8, 0.8)`

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `logs/daily_work_log.md`

产出/结论：
- 当前“球铰无运动范围限制”只对键盘联调脚本生效，方便人工观察驱动响应。
- 训练环境自身仍有 `ball_joint_out_of_bounds` 终止条件，尚未随本轮一起删除。

下一步：
- 若用户后续明确要求训练时也取消球铰范围限制，再单独修改 `complete_car_rl_training_env_cfg.py` 中的越界终止项。
