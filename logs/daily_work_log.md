# 每日工作日志

## 2026-04-22

已完成：
- 基于已筛选的 `22` 篇核心文献与七个固定写作模块，输出一份可直接用于论文写作的 Markdown 提纲：
  - `docs/literature/研究背景与综述提纲_基于22篇核心文献.md`
- 该提纲已按七个部分组织：
  - 每节目标
  - 建议写作顺序
  - 文献排序与推荐理由
  - 可直接展开的段落逻辑
- 按用户要求，将已筛选出的 `22` 篇核心文献按照七个综述模块重新排序，并确定各节主干引用顺序。
- 已明确后续写作原则：
  - 每一节优先使用前 `2-3` 篇 backbone 文献搭主线
  - 其余文献作为补充论证或过渡引用

修改文件：
- `docs/literature/研究背景与综述提纲_基于22篇核心文献.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已经有一份可直接进入论文写作阶段的综述骨架，不再只停留在文献池和排序阶段。
- 当前七个综述模块的主干顺序已明确：
  - 背景与能力需求：
    - `Borges 2022`
    - `Papadakis 2013`
    - `Prado 2018`
  - 常见构型及局限：
    - `Papadakis 2013`
    - `Borges 2022`
    - `Lei 2021`
  - 铰接式车辆意义：
    - `Iagnemma 2003`
    - `Li 2021`
    - `Cordes 2017`
  - 球面并联启发动机：
    - `Bai 2019`
    - `Abe 2021`
    - `Gosselin & Hamel 1994`
  - 控制难点：
    - `Li 2021`
    - `Wiberg 2022`
    - `Cordes 2017`
  - 传统方法与不足：
    - `Kayacan 2018`
    - `Iagnemma 2003`
    - `Li 2021`
  - RL 价值与不足：
    - `Wiberg 2022`
    - `Wiberg 2024`
    - `Josef & Degani 2020`
    - `Henderson 2019`
    - `Patterson 2024`

下一步：
- 直接基于该顺序进入七个模块的结构化阅读与综述草稿搭建。

## 2026-04-23

已完成：
- 按用户要求在 CNKI 完成一轮与“主动铰接车辆 / 地面轮式移动机器人 / 当前毕设结构相似论文”相关的中文文献检索与筛选。
- 已完成多组关键词交叉检索，并提炼出当前最接近毕设结构的三类文献簇：
  - `吉林大学`“二自由度铰接式车体轮式机器人”系列
  - `北京理工大学`“分布式驱动—转向多级铰接移动机器人”方向
  - `北京交通大学 / 吉林大学`“双铰接式车辆 / 双铰接轮式越野工程车辆”方向
- 已确认矿山铰接车相关论文更适合作为控制与自动驾驶背景补充，主要覆盖：
  - 折腰转向
  - 路径跟踪
  - 自主行驶
  - 松软路面建模

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前中文相关工作主链不应再从泛化“轮式移动机器人”开始，而应优先围绕“二自由度铰接车体 / 多级铰接移动机器人 / 双铰接车辆”继续下钻。
- 后续若需要写中文综述或 related work，可直接复用本轮筛出的高相关论文题目作为入口。

下一步：
- 若继续文献工作，可对本轮筛出的高相关论文逐篇提取摘要、关键词、方法点与可迁移到毕设的结构/控制要素。

已完成：
- 按用户要求补回论文正文页眉下方横线。
- 已将 `DLUT-thesis.cls` 中 `DLUT@heading` 与 `DLUT@headingNoNum` 的 `\headrulewidth` 从 `0pt` 调整为 `0.4pt`。
- 已重新执行：
  - `xelatex -interaction=nonstopmode main.tex`
  - 并确认 `main.pdf` 中页眉横线已恢复显示。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/DLUT-thesis.cls`
- `logs/daily_work_log.md`

产出/结论：
- 当前恢复原模板口径的基础上，页眉下方横线已重新显示。

已完成：
- 按用户最新要求，将上一轮对论文模板格式所做的整改恢复原样。
- 已回退：
  - `毕业论文/毕业论文模板/LaTeX/DLUT-thesis.cls`
  - `毕业论文/毕业论文模板/LaTeX/main.tex`
- 已准备重新编译，使 `main.pdf` 与 `main.bbl` 回到原模板输出口径。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/DLUT-thesis.cls`
- `毕业论文/毕业论文模板/LaTeX/main.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前论文模板不再处于“已按学校格式整改完成”状态，而是已恢复到整改前原样。
- 后续若再次进行格式合规修正，需要从当前原模板状态重新开始。

下一步：
- 重新执行 `bibtex` 与 `xelatex`，确认 `main.bbl` 和 `main.pdf` 已回到原模板输出。

已完成：
- 在用户明确保留“封面未填信息”和“中文题目 21 字不改”的前提下，对 `毕业论文/毕业论文模板/LaTeX/` 完成一轮模板层格式整改。
- 已修改：
  - `DLUT-thesis.cls`
  - `main.tex`
- 已完成的主要修正包括：
  - 页边距改为 `上 3.5 / 下 2.5 / 左 2.5 / 右 2.5 cm`
  - 页眉改为中文题目，页脚改为底部居中纯页码
  - 封面中英文题目样式改为新的字体链与字号控制
  - 图表标题恢复为 `图 / 表`
  - `结论 / 附录 / 致谢 / 参考文献` 标题改为中文
  - 参考文献样式切换为 `gbt7714-numerical`
  - `main.bbl` 不再含旧模板中多余的 `J.` / `C.`
- 已完成重新编译与结果核对：
  - `bibtex main`
  - `xelatex -interaction=nonstopmode main.tex`
  - `main.pdf` 正常生成
  - 已核对 `pdffonts`、`pdftotext` 与 `main.bbl`

修改文件：
- `毕业论文/毕业论文模板/LaTeX/DLUT-thesis.cls`
- `毕业论文/毕业论文模板/LaTeX/main.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前模板层主问题已从“已审查未整改”推进到“已整改并编译验证”。
- 当前剩余未动项仅为用户明确保留的封面占位信息与 `21` 字中文题目。

下一步：
- 若继续论文格式收尾，优先补齐封面真实信息，并决定是否把中文题目压缩到 `20` 字以内。

已完成：
- 根据 `docs/格式规则.md` 对 `毕业论文/毕业论文模板/LaTeX/` 进行一轮格式审查，重点核对封面、页眉页脚、页边距与参考文献。
- 已同时检查源码与导出 PDF：
  - `DLUT-thesis.cls`
  - `main.tex`
  - `main.bbl`
  - `reference/ref.bib`
  - `main.pdf`
- 已确认的主要问题包括：
  - 封面中文题目当前超过 `20` 字，且样式未严格落到学校要求
  - 封面仍存在 `评阅教师` 占位符与空白完成日期
  - 页边距与页眉内容不符合学校格式规则
  - 参考文献标题输出为 `References`
  - 参考文献仍使用 `GBT7714-2005NLang`
  - `main.bbl` 中各条文献末尾额外输出 `J.` / `C.`
  - 当前 PDF 实际嵌入字体为 `Fandol / NimbusRom`，尚未严格匹配学校要求字体

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前论文格式问题的主矛盾在模板层，不在 `chapter01.tex` 正文内容本身。
- 若后续继续整改论文格式，应优先修改 `DLUT-thesis.cls` 与参考文献样式链。

下一步：
- 若继续论文格式整改，先处理：
  - 封面字段与标题长度
  - 页边距与页眉
  - `参考文献` 标题与 `GB/T 7714-2015` 样式
  - 字体环境与字体映射

已完成：
- 按用户要求，对 `毕业论文/毕业论文模板/LaTeX/chapters/chapter01.tex` 第一节进行二轮重写，不再沿用首轮“复杂地形移动机器人的应用背景与能力需求”的单一展开方式。
- 已将第一节改写为“研究背景与研究意义”，并重组为四个小节：
  - `复杂地形地面机器人的应用需求与研究价值`
  - `非结构化环境的主要特征与技术挑战`
  - `国内外研究发展概况`
  - `本文问题的研究意义`
- 已按用户要求在首节中补入并串联多类应用场景：
  - 农业
  - 林业
  - 矿山/工程作业
  - 灾害救援
  - 野外勘测
  - 行星探测
- 已从本地文献转换结果中抽取并复制三张应用场景相关图片到论文目录：
  - `毕业论文/毕业论文模板/LaTeX/figures/ch1_agri_articulated_ugv.png`
  - `毕业论文/毕业论文模板/LaTeX/figures/ch1_forestry_xt28.png`
  - `毕业论文/毕业论文模板/LaTeX/figures/ch1_construction_acv_risk.png`
- 已保留并复用现有复杂地形环境图与铰接式行星车图，使第一章开头形成“场景需求 + 地形挑战 + 平台形态”的图文组合。
- 已再次执行主文档编译检查：
  - 命令：
    - `latexmk -xelatex -interaction=nonstopmode main.tex`
  - 结果：
    - `main.pdf` 成功生成
    - 第一节新增正文、插图与引用均已进入版面

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter01.tex`
- `毕业论文/毕业论文模板/LaTeX/figures/ch1_agri_articulated_ugv.png`
- `毕业论文/毕业论文模板/LaTeX/figures/ch1_forestry_xt28.png`
- `毕业论文/毕业论文模板/LaTeX/figures/ch1_construction_acv_risk.png`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 第一章第一节当前已经从“应用背景与能力需求”首轮草稿，推进到面向本科工科论文风格的“研究背景与研究意义”版本。
- 当前首节已经显式回答“为什么这个问题值得研究”，并把应用需求、环境压力、技术挑战和国内外发展情况压缩到同一条论证链中。

下一步：
- 若继续论文主线，优先统一 `chapter01.tex` 其余各节与新第一节之间的语言风格、段落密度和标题口径。

已完成：
- 按用户要求，在 `毕业论文/毕业论文模板/LaTeX/chapters/chapter01.tex` 中开始正式撰写第一章，先完成第一部分“复杂地形移动机器人的应用背景与能力需求”。
- 将 `chapter01.tex` 从英文模板占位稿改为中文论文正文，当前章节标题改为“绪论”。
- 第一部分已按既定顺序落稿：
  - 应用场景：行星探测、搜救、矿业、农业、林业、施工现场等
  - 复杂地形特征：坡度变化、障碍物、松软地面、碎石/坑洼、感知不完备
  - 能力需求映射：可通行性判断、姿态稳定性、持续轮地接触与法向载荷分配、效率与安全平衡
  - 问题落点：复杂地形适应是“机构-接触-控制”共同作用的问题
- 已从参考文献中抽取并接入插图：
  - 采用 `Borges 2022` Figure 1 的三张越野地形示意图
  - 已复制到论文目录：
    - `毕业论文/毕业论文模板/LaTeX/figures/ch1_offroad_grass.png`
    - `毕业论文/毕业论文模板/LaTeX/figures/ch1_offroad_sand.png`
    - `毕业论文/毕业论文模板/LaTeX/figures/ch1_offroad_gravel.png`
- 已在 `毕业论文/毕业论文模板/LaTeX/reference/ref.bib` 中新增本节使用的参考文献条目：
  - `borges2022survey`
  - `papadakis2013terrain`
  - `prado2018overcoming`
  - `wiberg2022control`
  - `huang2024terrain`
  - `xu2024rl`
- 已执行主文档编译检查：
  - 命令：
    - `latexmk -xelatex -interaction=nonstopmode main.tex`
  - 结果：
    - `main.pdf` 成功生成
    - 新增章节、图片路径与参考文献引用均已接入主文档

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter01.tex`
- `毕业论文/毕业论文模板/LaTeX/reference/ref.bib`
- `毕业论文/毕业论文模板/LaTeX/figures/ch1_offroad_grass.png`
- `毕业论文/毕业论文模板/LaTeX/figures/ch1_offroad_sand.png`
- `毕业论文/毕业论文模板/LaTeX/figures/ch1_offroad_gravel.png`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 第一章写作已从“文献筛选/提纲阶段”推进到“论文正文首段落稿阶段”。
- 当前 `chapter01.tex` 已成为后续七部分继续补写的主文件，不再沿用模板原始英文内容。
- 第一部分的论证链已经固定为：
  - 场景需求
  - 地形特征
  - 能力映射
  - `机构-接触-控制` 耦合落点

下一步：
- 继续在 `chapter01.tex` 中补写第二部分“地面车辆常见构型及其局限”。

已完成：
- 根据已筛选的 `22` 篇核心文献，完成 `chapter01.tex` 第一章剩余六部分与本章小结的首轮综述写作。
- 已补写的章节包括：
  - `地面车辆常见构型及其局限`
  - `铰接式地面车辆的研究意义`
  - `“球面并联关节启发”构型的引入动机`
  - `该类构型的控制难点`
  - `现有控制方法与不足`
  - `强化学习在复杂移动机器人控制中的价值与不足`
  - `本章小结`
- 已从参考文献中新增接入两张图片：
  - `Cordes 2018` 的 SherpaTT 行星车平台实物图
  - `Abe 2021` 的 ABENICS 主动球铰机构图
  - 已复制到论文目录：
    - `毕业论文/毕业论文模板/LaTeX/figures/ch1_articulated_rover.png`
    - `毕业论文/毕业论文模板/LaTeX/figures/ch1_active_ball_joint.png`
- 已在 `毕业论文/毕业论文模板/LaTeX/reference/ref.bib` 中补齐第一章剩余部分所需的核心文献条目。
- 已移除 `毕业论文/毕业论文模板/LaTeX/main.tex` 中模板自带的 `\nocite{*}`，使参考文献列表只保留正文实际引用的文献。
- 已再次执行主文档编译检查：
  - 命令：
    - `latexmk -xelatex -interaction=nonstopmode main.tex`
  - 结果：
    - `main.pdf` 成功生成
    - 第一章新增正文、图片与参考文献引用均已进入版面
    - 模板原始示例参考文献未再出现在导出参考文献列表中

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter01.tex`
- `毕业论文/毕业论文模板/LaTeX/main.tex`
- `毕业论文/毕业论文模板/LaTeX/reference/ref.bib`
- `毕业论文/毕业论文模板/LaTeX/figures/ch1_articulated_rover.png`
- `毕业论文/毕业论文模板/LaTeX/figures/ch1_active_ball_joint.png`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `chapter01.tex` 已不再处于“只完成第一部分”的状态，而是完成了整章七部分综述的首轮落稿。
- 第一章当前已形成完整论证链：
  - 复杂地形能力需求
  - 常见构型及其局限
  - 铰接式车辆意义
  - 球面并联关节启发动机
  - 控制难点
  - 传统控制方法不足
  - RL 价值与不足
- 后续论文写作若继续推进，不应再回到“下一段进入第一章第二部分”的旧状态。

下一步：
- 若继续论文主线，优先对 `chapter01.tex` 做二轮语言压缩、引用规范和版式检查，再决定是否继续改写后续章节模板内容。

已完成：
- 按用户要求，将 `docs/literature/` 下的原始 PDF 文献按“综述论文 / 研究论文”完成分类归档。
- 新建目录：
  - `docs/literature/综述论文/`
  - `docs/literature/研究论文/`
- 已将原先平铺在 `docs/literature/` 根目录的 `83` 篇 PDF 全部迁移完成：
  - `综述论文` `12` 篇
  - `研究论文` `71` 篇
  - 根目录剩余 PDF `0` 篇
- 已保留 `docs/literature/opendataloader_output/` 不变，避免影响当前第一章综述写作、提纲抽取和本地 Markdown 引用链。
- 已同步更新本地文献处理脚本，使其兼容新的分类目录结构：
  - `scripts/literature/mineru_batch_convert.sh`
  - `scripts/literature/build_literature_manifest.py`
- 已同步更新顶层说明与项目记忆：
  - `README.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `docs/literature/综述论文/`
- `docs/literature/研究论文/`
- `scripts/literature/mineru_batch_convert.sh`
- `scripts/literature/build_literature_manifest.py`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 本地原始 PDF 文献库已从“根目录平铺”切换为“按文献类型分类归档”。
- 现有 `opendataloader_output` Markdown 主线未被打断，论文写作相关路径保持稳定。
- 后续新增 PDF 应直接进入对应分类目录，批量转换脚本仍可从 `docs/literature/` 作为统一入口调用。

下一步：
- 若后续还要进一步整理，可再按研究主题在两类目录内部做二级分类；当前这一轮先保持最短路径，只完成“综述 / 研究”一级归档。

已完成：
- 根据本地代表文献的 `Introduction`，完成一轮“复杂地形地面机器人研究背景如何开头、如何收缩问题”的写法调研，目标是直接服务于毕业论文第一章二轮润色。
- 本轮重点抽查并比对了以下文献的引言开头：
  - `Borges 2022`
  - `Papadakis 2013`
  - `Prado 2018`
  - `Wiberg 2022`
  - `Cordes 2017`
  - `Cordes 2018`
  - `Li 2021`
  - `Huang 2024`
  - `Josef 2020`
  - `Xu 2024`
- 已形成可复用结论：
  - 主流写法不是直接讲机构或算法，而是先讲：
    - 应用场景 / 任务价值
    - 复杂地形特征与风险
    - 由此产生的能力需求或现有方法不足
    - 最后再收缩到本文对象与贡献
  - 更贴合当前论文主线的推荐起笔顺序仍是：
    - `场景需求 → 地形特征 → 能力映射 → 机构-接触-控制耦合`
- 已将该结论同步到项目记忆，供后续 `chapter01.tex` 二轮语言压缩和首段改写直接复用。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已经明确：复杂地形地面机器人研究背景的高频写法是“由场景和环境压力推到技术问题”，而不是“由方法反推问题”。
- 当前第一章第一节现有结构与代表文献主流开头方式一致，后续二轮润色应以压缩和提纯表达为主，不宜重写成方法先行结构。

下一步：
- 若继续论文写作，可直接基于本轮结论，对 `chapter01.tex` 第一节首两段做更强的学术化压缩，并强化从场景到能力需求的因果连接。

已完成：
- 根据学校模板文件 `docs/大连理工大学本科毕业论文（设计）模板.doc`，整理出一份可直接用于 LaTeX 论文版式检查的 Markdown 规则文档：
  - `docs/格式规则.md`
- 本轮已系统提炼的规则范围包括：
  - 页面设置与页边距
  - 页眉页脚与页码
  - 封面题目与信息项
  - 原创性声明、使用授权声明
  - 中文摘要、英文摘要、关键词、目录
  - 引言、正文、章/节/节内一级标题
  - 图、表、公式
  - 参考文献
  - 结论、附录、修改记录、致谢
  - 打印与装订要求
- 已在规则文档中区分：
  - 模板正文或文本框中的明确规定
  - 由样例页面整理出的`样例推断`
- 已将该规则文件定位为后续论文格式检查的默认核对口径，避免之后再次从旧版 `.doc` 模板中重复人工抽取。

修改文件：
- `docs/格式规则.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库内已经有一份面向毕业论文 LaTeX 版式校对的结构化规则清单。
- 后续若检查 `毕业论文/毕业论文模板/LaTeX/` 下的正文、参考文献或封面格式，可直接以 `docs/格式规则.md` 为基线。

下一步：
- 若继续论文排版工作，可直接对照 `docs/格式规则.md` 对 `main.tex` 及各章节输出 PDF 做首轮格式核查。

## 2026-04-21

已完成：
- 按用户要求，把 Stage0 继续推进到“路线预瞄 + 强制第二段转弯 + 差速代价”版本：
  - observation 新增 `next_turn_delta`
  - waypoint 采样新增 `min_segment_turn_deg = 20.0°`
  - reward 新增 `differential_turn_cost`
  - `slip_penalty / turn_speed_penalty` 已改为按转向需求加权
- 已同步更新 observation dim / descriptor / noise dim / logger：
  - actor / critic 观测维度由 `54 / 54` 升至 `55 / 55`
- 已完成静态检查：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 已尝试补跑 smoke：
  - 命令：
    - `python3 scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 16 --max_iterations 2 --run_name smoke_stage0_next_turn_preview_v1`
  - 结果：
    - 当前终端环境直接报 `ModuleNotFoundError: No module named 'isaaclab'`
    - 本轮未能完成 runtime smoke

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `docs/current_status.md`
- `docs/RL阶段训练参数一览表.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active Stage0 代码口径已变为：
  - 双 waypoint
  - 每段 `10m`
  - 第二段相对第一段最小转角 `20°`
  - 观测 `55 / 55`
  - reward `8` 项
- `differential_turn_cost` 当前基于三组左右轮扭矩差平均绝对值，不直接奖励球铰角度。
- 本轮代码改动已通过静态检查，但由于 Isaac Lab 运行环境缺失，尚未完成新的 smoke 与真实训练验证。

下一步：
- 先恢复 Isaac Lab 运行环境，再补跑 smoke 与新的真实训练，重点检查 `differential_turn_cost / slip_penalty / turn_speed_penalty` 是否真的把策略推向协同转向。

已完成：
- 按用户要求，在修正为“双 waypoint、每段 `10m`、总名义路程约 `20m`”后的新 Stage0 主线上启动一轮真实训练，并全程观察终端输出：
  - 命令：
    - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --max_iterations 150 --run_name stage0_waypoint_quality_goal10_v1_150iter`
  - 运行目录：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-21_21-51-09_stage0_waypoint_quality_goal10_v1_150iter`
  - 对应 Isaac 日志：
    - `/tmp/isaaclab/logs/isaaclab_2026-04-21_21-51-09.log`
  - 训练总时长：
    - `1286.63 s`
- 已补导出本轮 TensorBoard 标量：
  - `tensorboard_export/latest_values.csv`
  - `tensorboard_export/summary.json`
  - `tensorboard_export/scalars/*.csv`
- 已完成 run 级诊断并同步项目记忆。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前双 waypoint Stage0 主线已经“能学”，不是单纯起训失败：
  - `Train/mean_reward: -1.46 -> 19.15`
  - `goal_success_rate: 0.0 -> 0.5625`
  - `time_out_rate: 0.8809 -> 0.4375`
  - `episode/waypoints_completed: 0.0 -> 1.3047`
  - `episode/waypoint_completion_pct: 0.0 -> 65.23`
- 训练存在明显两阶段形态：
  - `iteration 0-117` 长时间平台，多数 episode 超时
  - `iteration 118+` 才出现 success 跃迁
  - `iteration 131` 一度达到：
    - `goal_success_rate = 1.0`
    - `time_out_rate = 0.0`
    - `waypoints_completed = 2.0`
  - 但该峰值没有稳定保持到末轮
- 当前主要问题不是吞吐或启动链，而是行为质量和成功稳定性：
  - 纵滑率从 `9.22` 降到 `3.49`
  - 但侧滑角从 `0.514` 升到 `0.630 rad`
  - 说明当前完成 waypoint 的方式仍偏高侧滑
  - `Loss/value` 末轮升到 `0.3265`，late-phase critic 稳定性偏弱
- 本轮运行性能正常：
  - `Perf/total_fps` 平均约 `4024`
  - `collection_time` 平均约 `7.95 s`

下一步：
- 基于本轮真实 run 重新判断 reward 平衡，重点检查：
  - `slip_penalty`
  - `turn_speed_penalty`
  - `progress_to_target`
 之间是否把策略推向了“会完成但不够干净”的解。

已完成：
- 按用户最新修正，将 Stage0 双 waypoint 几何从“每段 20m”改为“每段 10m、总名义路程约 20m”：
  - `commands.goal_distance: 20.0 -> 10.0`
- 已同步更新当前状态与参数文档口径。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/current_status.md`
- `docs/RL阶段训练参数一览表.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前双 waypoint Stage0 的默认几何已经修正为：
  - 两段 waypoint
  - 每段 `10m`
  - 总名义路程约 `20m`
- reward 与 termination 的实现形式不变，但它们依赖 `goal_distance` 的量会自动改到新尺度。

已完成：
- 按用户确认的 5 点方案，将 Stage0 从“单目标终点捕获”重构为“平地双 waypoint 高质量连续运动”主线：
  - `commands.num_waypoints_per_episode = 2`
  - `commands.goal_distance = 20.0`
  - `episode_length_s = 40.0`
  - 命中当前 waypoint 后自动切到下一个
  - 只有最后一个 waypoint 命中时 episode 才算 `success`
- 已将 `wheel_slip_angle` 正式加入 actor / critic observation：
  - 观测维度由 `48 / 48` 增至 `54 / 54`
- 已重构 reward 主干：
  - 保留 `distance_to_target / progress_to_target / reached_target / far_from_target / angle_diff`
  - 新增 `turn_speed_penalty`
  - 新增 `slip_penalty`
  - 当前 `commands[:, 3]` 已改为 active waypoint bearing，而不是最终目标朝向误差
- 已修正 `termination` 口径一致性：
  - `far_from_target` 不再写死 `goal_distance + 3.0`
  - 已改为读取 `goal_distance + far_from_target_margin`
- 已完成静态检查：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 已完成 smoke run：
  - 命令：
    - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --max_iterations 2 --run_name smoke_stage0_waypoint_quality_v1`
  - 运行目录：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-21_21-23-45_smoke_stage0_waypoint_quality_v1`
  - 对应 Isaac 日志：
    - `/tmp/isaaclab/logs/isaaclab_2026-04-21_21-23-45.log`
  - 在修正 `far_from_target` 判定口径后，又补跑了一次 smoke：
    - 命令：
      - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --max_iterations 2 --run_name smoke_stage0_waypoint_quality_v2_far_margin_fix`
    - 运行目录：
      - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-21_21-32-41_smoke_stage0_waypoint_quality_v2_far_margin_fix`
    - 对应 Isaac 日志：
      - `/tmp/isaaclab/logs/isaaclab_2026-04-21_21-32-41.log`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `docs/current_status.md`
- `docs/RL阶段训练参数一览表.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 的任务语义已经切换到用户确认的新平地主线，不再沿用旧的单目标终点捕获口径。
- 代码链已经能正常启动并输出新的 waypoint / reward / observation 指标，`far_from_target` 口径也已和配置统一。
- 当前最需要继续验证的是 reward 平衡；smoke run 中 `slip_penalty` 量级偏大，初始总回报为负。

已完成：
- 对照 `RLRoverLab` 的 `AAU` 目标可视化实现，完成当前 Stage0 回放链路的目标位姿 marker 接线：
  - 核对结论：
    - `AAU` 的做法不是在 `eval.py` 里临时绘制
    - 而是在命令运行时对象里通过 `VisualizationMarkers` 持有 marker，并在每步 debug callback 里刷新
  - 当前本仓库落地方式：
    - 在 `debug_draw.py` 中新增目标位置球 marker 与目标朝向箭头 marker
    - 在 `base/env.py` 中用现有 `command_targets_w` 每步刷新 marker
    - 在 `scripts/play.py` 中默认开启该可视化
    - 如需隐藏，可传：
      - `--hide_goal_vis`
- 已完成静态检查：
  - `python3 -m py_compile RL_Training/scripts/play.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/debug_draw.py`

修改文件：
- `RL_Training/scripts/play.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/debug_draw.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `python scripts/play.py --task CompleteCar-Stage0 ...` 默认会显示目标位置与目标朝向。
- 当前实现直接复用了 `command_targets_w` 的世界系目标缓存，不需要再额外维护一套回放专用目标状态。

已完成：
- 按用户确认的终点捕获导向方案重调 Stage0 reward：
  - 删除 `angle_to_target`
  - `distance_to_target_weight: 5.0 -> 8.0`
  - `angle_diff_weight: 5.0 -> 10.0`
  - 新增 `progress_to_target_relax_radius_m = 2.0`
  - `progress_to_target` 在 `d <= 2.0 m` 时改为只奖励前进，不惩罚短暂停止、绕行或后退
- 已同步清理运行时日志主链：
  - `env.py` 不再输出 `Reward/angle_to_target`
  - `logger.py` 不再保留 `Reward/angle_to_target` 的终端 / TensorBoard / episode tag
- 已完成静态检查：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 已完成短 smoke run 验证：
  - 命令：
    - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --max_iterations 2 --run_name smoke_reward_terminal_capture_v2`
  - 运行目录：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-21_19-02-56_smoke_reward_terminal_capture_v2`
  - 对应 Isaac 日志：
    - `/tmp/isaaclab/logs/isaaclab_2026-04-21_19-02-56.log`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `docs/current_status.md`
- `docs/RL阶段训练参数一览表.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active reward 已从 6 项改为 5 项，不再包含 `angle_to_target`。
- 新 reward 口径已经可以正常启动训练，smoke run 未出现 reward / logger 相关运行时错误。
- 下一步应直接跑一轮新的真实训练，验证：
  - `time_out_rate` 是否下降
  - `goal_heading_error_abs` 是否改善
  - `goal_success_rate` 是否更稳定

已完成：
- 按用户要求启动一轮 Stage0 GPU 真实训练前，先修复了 low-slip allocator 的启动阻塞：
  - 问题位置：
    - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py`
  - 现象：
    - 首轮 run `2026-04-21_15-39-43_stage0_full_diagnosis_2026-04-21` 在首个 `env.step()` 崩溃
    - 报错为：
      - `TypeError: maximum(): argument 'other' must be Tensor, not float`
  - 原因：
    - torch 路径 `_sat(...)` 直接把 Python float 边界传给了 `torch.maximum / minimum`
  - 修复：
    - `_sat(...)` 现已统一把 `lower / upper` 转成与 `values` 同 device、同 dtype 的 Tensor
- 已完成验证：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py`

产出/结论：
- 当前 low-slip 主线训练不再会在 contact weight 饱和阶段因 float/Tensor 类型不匹配崩溃。

已完成：
- 按用户要求启动并全程终端观察一轮 `CompleteCar-Stage0` GPU 真实训练：
  - 命令：
    - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --run_name stage0_full_diagnosis_2026-04-21_v2`
  - 运行目录：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-21_15-40-55_stage0_full_diagnosis_2026-04-21_v2`
  - 对应 Isaac 日志：
    - `/tmp/isaaclab/logs/isaaclab_2026-04-21_15-40-55.log`
  - 对应 Hydra 输出：
    - `RL_Training/outputs/2026-04-21/15-40-55/`
  - 实际停止位置：
    - `iteration 147 / 700`
  - 停止原因：
    - 终端行为形态、关键标量趋势和运行时问题已稳定显现，继续跑完整个 `700` 轮的信息增量很低
- 已完成：
  - 导出本轮 TensorBoard 标量：
    - `tensorboard_export/`
  - 读取并核对：
    - `params/env.yaml`
    - `params/agent.yaml`
    - `.hydra/overrides.yaml`
    - `latest_values.csv`
    - `summary.json`

本轮关键结果：
- 启动与接线正常：
  - articulation 初始化正常
  - `ball_joints` / `wheel_joints` actuator collection 正常
  - 本轮真实训练配置为：
    - `cuda:0`
    - `64` 个 env
    - `8` 维动作
    - `48 / 48` 观测
- 当前 low-slip 主线相比旧坏平衡，确实出现了结构性改善：
  - `Train/mean_reward`：
    - `0.238 -> 4.075`
  - `goal_pos_error`：
    - `7.689 m -> 3.018 m`
    - 最好约 `2.668 m`
  - `goal_completion_pct`：
    - `4.14% -> 62.28%`
    - 最好约 `66.65%`
  - `wheel_longitudinal_slip_abs_mean_raw`：
    - `9.401 -> 5.860`
    - 最低约 `3.669`
  - `wheel_torque_target_abs_mean_raw`：
    - `4.666 -> 3.890`
- 但主失败模式没有消失：
  - 末轮：
    - `mean_episode_length = 1199`
    - `time_out_rate = 1.0`
    - `termination_success_rate = 0.0`
    - `Tracking/goal_success_rate = 0.0`
  - 说明当前策略主要学成了：
    - 更低滑移地接近目标
    - 但不是稳定完成到达
- 本轮还暴露出两个新的诊断重点：
  - success 统计口径分裂：
    - `Termination/success_rate` 多次出现脉冲式非零，最大约 `0.193`
    - `Tracking/goal_success_rate` 全程为 `0`
    - 当前高概率是 reset 前后统计时刻不一致
  - rollout collection 性能退化：
    - `Perf/total_fps` 在约 `iteration 117` 后从 `~3330` 掉到 `~2240`
    - `Perf/collection_time` 从 `~9.6 s` 涨到 `~14.4 s`
    - `learning_time` 基本稳定，性能问题集中在 rollout collection

当前结论：
- 当前 Stage0 新主线已经不再是“完全不会朝目标靠近”，但仍没有形成稳定到达策略。
- 下一轮优先级不应先改 PPO 数值，而应先查清：
  - success 指标为什么口径分裂
  - collection throughput 为什么在中段断崖下降
  - reward 是否仍主要奖励“接近目标 + 活到超时”

已完成：
- 按用户要求将当前 Stage0 actor / critic 观测切换为 48 维最小闭环方案：
  - `ball_joint_pos` 6
  - `ball_joint_vel` 6
  - `base_lin_vel` 3
  - `base_ang_vel` 3
  - `wheel_joint_vel` 6
  - `wheel_longitudinal_slip` 6
  - `wheel_normal_contact_force` 6
  - `goal_relative_command` 4
  - `last_action` 8
- 已同步修改：
  - `io_descriptors.py`
  - `observations.py`
  - `math_utils.py`
- 已同步更新文档口径：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
- 已完成静态检查：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`

产出/结论：
- 当前 48 维观测已经把球铰状态、机体速度、轮系纵滑率和归一化法向接触力正式送入网络。
- 当前仍未送入网络的量主要保留为诊断项，包括：
  - `projected_gravity`
  - `ball_joint_target_error`
  - `head_roll_pitch`
  - `tail_roll_pitch`
  - `wheel_slip_angle`

已完成：
- 按用户要求统一诊断量与 allocator 的纵滑率定义：
  - `observations.py` 中的纵滑率不再单独手写一份公式
  - 已改为直接调用 `wheel_speed_allocator.py` 中新增的共享 torch 实现
  - 当前控制与诊断共用的原始纵滑率定义为：
    - `(v∥ - rΩ) / max(|v∥|, ε)`
- 当前控制与诊断都不再对纵滑率做额外裁剪
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
- 已完成静态检查：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/__init__.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`

产出/结论：
- 当前纵滑率定义的唯一来源已经收敛到 allocator 共享实现。
- 如果后面再调整滑移公式，控制和诊断会一起变，不会再出现两份逻辑漂移。

已完成：
- 按用户要求统一球铰动作映射边界与终止边界：
  - 当前后 `6` 维动作映射到 `q^d` 时，不再读取 `control` 侧单独的 action limit
  - 已改为直接使用：
    - `terminations.ball_joint_pos_lower_limits`
    - `terminations.ball_joint_pos_upper_limits`
  - allocator 内部 `q_cmd` 的位置饱和边界也同步改为 termination 边界
- 已同步清理配置主干中的重复字段：
  - 删除 `ControlCfg` 中旧的：
    - `ball_joint_action_lower_limits`
    - `ball_joint_action_upper_limits`
  - 删除 `CompleteCarStage0EnvCfg` 中对应覆写
- 已同步更新文档口径：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
- 已完成静态检查：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`

产出/结论：
- 当前 Stage0 的球铰边界口径已经收敛为单一来源：
  - termination 边界既负责 `ball_joint_out_of_bounds`
  - 也负责动作映射与 `q_cmd` 饱和
- 后续如果用户继续调球铰可动范围，只需要改 termination 边界，不需要再同步维护一套 action limit。

## 2026-04-20

已完成：
- 按用户要求，将论文第 3 章与当前 RL 主线同步升级为“球铰姿态规划器 + 接触感知低滑移 allocator”口径：
  - 在 `chapter03.tex` 中保留原有名义纯滚动参考层
  - 新增“面向低滑移的接触感知轮级牵引分配”小节
  - 正式写入：
    - 侧向速度分量 `v_{w,\perp}`
    - 接触权重 `c_w`
    - 平面命令整形 `u_v^\ast`
    - 轮级角速度参考 `\Omega_{w,\mathrm{ref}}`
    - 纵向滑移率 `s_w`
    - 驱动扭矩命令 `\tau_w^{cmd}`
- 已将当前 `wheel_speed_allocator.py` 重构为低滑移底层分配器：
  - 保留球铰姿态规划器
  - 新增轮心几何状态接口：
    - `compute_wheel_kinematic_state(...)`
  - 新增低滑移命令整形：
    - `shape_planar_command_for_low_slip(...)`
  - 新增名义轮速参考：
    - `compute_wheel_speed_references(...)`
  - 新增轮级牵引力矩分配：
    - `compute_wheel_traction_targets(...)`
  - 新增总入口：
    - `compute_low_slip_control_targets(...)`
- 已同步修改环境执行链：
  - `env.py` 当前每步会读取：
    - 六轮法向接触力
    - 六轮实际滚动速度
    - 六轮实际角速度
  - 当前环境中：
    - 球铰继续使用 `set_joint_position_target(...)`
    - 车轮已从 `set_joint_velocity_target(...)` 改为 `set_joint_effort_target(...)`
- 已同步修改：
  - `mdp/actions.py`
  - `complete_car_cfg.py`
  - `complete_car_stage0_cfg.py`
  - `kinematics/__init__.py`
  - `validate_wheel_speed_allocator.py`
  - `rsl_rl/utils/logger.py`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `docs/RL阶段训练参数一览表.md`
- 当前验证结果：
  - `python3 -m py_compile ...` 通过
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py --run-smoke-cases` 通过
  - 手动验证：
    - `q = 0`
    - `q^d = [20^\circ, 0, 0, 0, 0, 0]`
    - `u_v^d = [1, 1]`
    时，allocator 会把 `u_v^d` 整形成更小的 `\Omega_z`，并输出轮级力矩目标
  - 论文编译通过：
    - `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`
  - 当前仍保留的论文既有问题：
    - `fang2015survey`
    - `MATSUMURA2017566`
    两条参考文献仍缺失

下一步建议：
- 直接在新低滑移力矩控制链上启动一次真实训练 run，观察：
  - `wheel_longitudinal_slip_abs_mean_raw`
  - `wheel_slip_angle_abs_mean_raw`
  - `wheel_torque_target_abs_mean_raw`
  - `goal_success_rate`
  是否相较旧主线出现结构性改善。

已完成：
- 按用户要求补写论文 `chapter03.tex` 中公式（3.31）（3.32）的详细推导：
  - 已写清：
    - 位置雅可比 `{}^{2}\mathbf G_w(\mathbf q)` 的列定义
    - 前/后/中模块轮心位置对构型变量的链式求导
    - 从惯性系绝对位置微分得到速度传播公式的过程
    - `\mathbf R^T\dot{\mathbf R}` 与叉乘矩阵的关系
    - 叉乘项 `{}^{2}\boldsymbol\omega_c^d \times {}^{2}\mathbf p_w` 的分量展开
- 本轮结果：
  - `(3.31)` 仍对应：
    - `eq:wheel_position_jacobian`
  - `(3.32)` 仍对应：
    - `eq:wheel_center_velocity_direct_current`
  - 新增推导未打乱原有公式编号
- 修改文件：
  - `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 已完成验证：
  - 在 `毕业论文/毕业论文模板/LaTeX/` 下执行：
    - `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`
  - 主文件编译通过
  - 当前仍保留与本轮无关的既有问题：
    - `chapter01` 中 2 个未定义参考文献

已完成：
- 按用户要求，按论文 `chapter03.tex` 当前口径重写 RL 主线底层动作链：
  - policy 动作维度仍为 `8`
  - 前 `2` 维继续表示中模块期望平面运动命令 `u_v`
  - 后 `6` 维语义已改为球铰期望构型 `q^d`，不再直接作为球铰执行器位置命令写入
- 已在 `wheel_speed_allocator.py` 中加入球铰姿态规划器：
  - `qdot_cmd = sat(K_q (q^d - q))`
  - `q_cmd = sat(q + Δt qdot_cmd)`
- 已将 wheel allocator 从旧的静态 `J_w(q)` 扩展为论文当前完整口径：
  - `Ω^d = J_w(q) u_v + J_q(q) qdot_cmd`
- 已同步修改 RL 环境执行链：
  - `env.py`
  - `mdp/actions.py`
  - `io_descriptors.py`
  - `complete_car_cfg.py`
  - `complete_car_stage0_cfg.py`
- 已重写 `validate_wheel_speed_allocator.py`，当前可直接验证：
  - `q`
  - `q^d`
  - `u_v`
  - `qdot_cmd`
  - `q_cmd`
  - `J_w(q)`
  - `J_q(q)`
  - `Ω^d`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/__init__.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `docs/RL阶段训练参数一览表.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 RL 主线已经不再是“动作后 6 维直接给球铰位置目标 + 静态 `J_w(q)`”。
- 当前真实执行链已经切换为：
  - `q, q^d, u_v -> qdot_cmd, q_cmd, Ω^d`
- 已完成验证：
  - `python3 -m py_compile ...` 通过
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py --run-smoke-cases` 通过
  - 手动验证：
    - `q = 0, q^d = 0, u_v = [1, 1]`
    - `q = 0, q^d = [20°, 0, 0, -20°, 0, 0], u_v = [0, 0]`

下一步建议：
- 直接在当前完整第 3 章口径下启动新的 Stage0 真实训练 run，再判断是否仍会收敛到超时坏平衡。

已完成：
- 参考论文 `chapter03.tex`，新增一份与第 3 章符号体系一致的 `Stage0` 推导文档：
  - 新增文件：
    - `docs/Stage0球铰姿态规划器与底层运动学模型推导.md`
- 本轮推导口径：
  - 完整继承第 3 章已固定的核心记号：
    - `\mathbf u_v`
    - `\mathbf q`
    - `\mathbf q^d`
    - `\mathbf q^{cmd}`
    - `\boldsymbol\Omega^d`
    - `\mathcal P`
  - 在 `Stage0` 工作假设下做偏航约化：
    - `\theta_f = \phi_f = \theta_r = \phi_r = 0`
    - 只保留 `\psi_f,\psi_r`
  - 新建球铰姿态规划器：
    - 输入：
      - `(\mathbf u_v,\mathbf q,\mathcal P_\psi)`
    - 输出：
      - `\mathbf q^d`
      - `\mathbf q^{cmd}`
      - `\dot{\psi}_f^d`
      - `\dot{\psi}_r^d`
  - 将当前轮速分配从：
    - `\boldsymbol\Omega^d = \mathbf J_w(\mathbf q)\mathbf u_v`
    扩展为：
    - `\boldsymbol\Omega^d = \bar{\mathbf J}_w(\mathbf q)\bar{\mathbf u}_v`
  - 其中扩展输入向量为：
    - `\bar{\mathbf u}_v = [V_x^d,\Omega_z^d,\dot{\psi}_f^d,\dot{\psi}_r^d]^T`
- 本轮结论：
  - 当前已得到一套与论文第 3 章前后兼容的 `Stage0` 候选推导
  - 当 `\dot{\psi}_f^d = \dot{\psi}_r^d = 0` 时，新模型会退化回当前第 3 章的静态几何轮速分配关系
  - 这份文档当前只是候选推导稿，尚未直接回写进论文正文

已完成：
- 按用户要求统一仓库内 Markdown 文档的数学公式语法，并把该规则写入仓库级约束：
  - `docs/stage0_structured_control_scheme.md` 中的公式已统一改为 Obsidian 可编译写法
  - `AGENTS.md` 已新增 Markdown 公式规则：
    - 行内公式使用 `$...$`
    - 独立公式使用 `$$...$$`
    - 仓库 Markdown 文档不再使用 `\(...\)` 或 `\[...\]`
- 同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 当前说明：
  - 该规则用于仓库跟踪的 Markdown 文档
  - 不改变论文 LaTeX 源文件下的数学公式写法

已完成：
- 按用户要求，把“球铰姿态规划器 + 接触加权轮速/驱动力分配器 + 高层 RL”方案整理为独立设计文档并落到 `docs/`：
  - 新增文件：
    - `docs/stage0_structured_control_scheme.md`
- 文档内容覆盖：
  - `Stage0` 研究目标
  - 三层控制架构
  - 高层动作 `a_t = [v_d, \kappa_d]`
  - 球铰姿态规划器
  - 含 `\dot{\psi}_f^d / \dot{\psi}_r^d` 的底层运动学模型
  - 接触加权轮速/驱动力分配器
  - `RL` 环境的 observation / reward / termination 设计
  - `Stage0` 基线对比设计
  - 待用户确认的研究判断
- 当前说明：
  - 本文档是候选方案汇总，不代表这些研究判断已经全部最终确认

已完成：
- 针对当前论文一致 `J_w(q)` 轮速分配器，按用户提出的三类姿态做了离线运动学诊断，并把结果上升为项目记忆：
  - `q = 0, u_v = [1, 1]`
  - `q = [0, 10^\circ, 0, 0, 0, 0], u_v = [1, 0]`
  - `q = [1, 0, 0, 0, 0, 0], u_v = [1, 0]`
- 本轮确认：
  - 当前 allocator 只使用：
    - 实际球铰构型 `q`
    - 平面命令 `u_v`
  - 当前 allocator 不使用：
    - 接地状态
    - 法向接触力
    - 滑移 / 侧偏
    - 实际车体速度反馈
  - `q = 0` 时，当前模型在仿真语义上退化为三轴统一差速转向
  - 前车抬起时，前轮不会因为失去接地而自动停轮：
    - 分配器仍会给非零目标轮速
    - 仿真里更接近“空转但不提供有效牵引”
  - 当前车偏航 `\psi_f = 1 rad` 且 `u_v = [1, 0]` 时：
    - 前轮线速度目标约为 `0.5403 m/s`
    - 对应横向分量约为 `0.8415 m/s`
    - 这意味着仿真里前车更可能被中后车推着走并产生较强侧滑 / 刮擦
- 修改文件：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 已完成验证：
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py --ball-joint-pos 0 0 0 0 0 0 --planar-command 1 1 --show-jacobian`
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py --ball-joint-pos-deg 0 10 0 0 0 0 --planar-command 1 0 --show-jacobian`
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py --ball-joint-pos 1 0 0 0 0 0 --planar-command 1 0 --show-jacobian`
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py --ball-joint-pos-deg 0 60 0 0 0 0 --planar-command 1 0`

已完成：
- 按用户要求将 `validate_wheel_speed_allocator.py` 升级为可重复使用的命令行验证脚本：
  - 不再只依赖脚本内写死的输入
  - 现已支持手动输入任意：
    - 球铰构型 `q`
    - 平面运动命令 `u_v = [V_x^d, \Omega_z^d]`
- 当前新增命令行参数：
  - `--ball-joint-pos`
  - `--ball-joint-pos-deg`
  - `--planar-command`
  - `--show-jacobian`
  - `--run-smoke-cases`
- 当前脚本输出内容：
  - 输入球铰顺序
  - 输出轮关节顺序
  - `q` 的弧度值与角度值
  - `J_w(q)`（按需显示）
  - 六轮角速度目标 `\boldsymbol\Omega^d`
  - 对应轮缘线速度
- 本轮修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 已完成验证：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py`
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py --run-smoke-cases`
  - 手动输入示例：
    - `q = 0, u_v = [1, 0]`
    - `q = 0, u_v = [1, 1]`
    - `\theta_f = 10^\circ, u_v = [1, 0]`

已完成：
- 按用户要求清理当前 TensorBoard 空白项：
  - `logger` 端新增非有限值过滤，不再把空白曲线写入事件文件
  - `tensorboard_export.py` 默认过滤：
    - 全零标量序列
    - 无任何有限值的空白标量序列
  - 新增命令行别名：
    - `--prune-blank-tags`
- 已对历史 Stage0 run 批量执行空白 tag 清理：
  - 目标目录：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/`
  - 共重写：
    - `57` 个 run 的事件文件
  - 原始事件文件已备份到各自：
    - `tensorboard_export/original_events/`
- 本轮修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 已完成验证：
  - `python3 -m py_compile` 通过
  - 扫描确认历史 Stage0 run 中存在空白 tag 的目录已完成重写

已完成：
- 对完整训练 run `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-20_11-44-13` 做离线诊断：
  - 对应 Isaac 日志：
    - `/tmp/isaaclab/logs/isaaclab_2026-04-20_11-44-13.log`
  - 对应 Hydra 输出：
    - `RL_Training/outputs/2026-04-20/11-44-13/`
  - 本轮真实配置：
    - `episode_length_s = 20.0`
    - `commands.resampling_time = 20.0`
    - `action_space = 12`
    - `observation_space = 22 / 22`
    - `num_steps_per_env = 512`
    - `max_iterations = 700`
- 本轮关键结果：
  - 已完整跑满 `700` 轮，并保存到 `model_699.pt`
  - 后 `20` 轮：
    - `mean_episode_length = 1199`
    - `time_out_rate = 1.0`
  - 末 `5` 轮：
    - `goal_pos_error ≈ 5.35 m`
    - `goal_completion_pct ≈ 33.1%`
    - `goal_heading_error_abs ≈ 0.359 rad`
    - `|longitudinal slip| ≈ 2.17`
    - `|slip angle| ≈ 0.610 rad`
    - `wheel_velocity_target_abs_mean ≈ 3.92 rad/s`
- 当前结论：
  - 这条旧 `12` 维动作接口 run 已完整证明：
    - 训练不是“还没跑够”
    - 它已经稳定收敛到超时坏平衡
    - 单纯继续增加 iteration 没有证据能让它自动学会到达目标

已完成：
- 按用户要求修改当前 RL 主线动作空间：
  - 去掉球铰动作输出
  - 当前 policy 动作从 `12` 维收缩为 `6` 维纯轮速命令
  - 环境每步都将球铰目标固定回默认复位位姿，保持球铰链固定
- 同步影响：
  - `last_action` 观测由 `12` 维变为 `6` 维
  - actor / critic 观测维度由 `22 / 22` 变为 `16 / 16`
- 本轮修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `docs/RL阶段训练参数一览表.md`
  - `logs/daily_work_log.md`
- 已完成验证：
  - `python3 -m py_compile` 通过
  - 当前文档口径已同步修正为：
    - `episode_length_s = 20.0`
    - `commands.resampling_time = 20.0`
    - 动作维度 `6`
    - 观测维度 `16 / 16`

已完成：
- 按用户要求增强终端训练输出：
  - 在训练控制台 footer 新增 ASCII 时间进度条
  - 新增显示：
    - `Time progress`
    - `Time elapsed`
    - `ETA`
    - `Est. total time`
- 本轮修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 已完成验证：
  - `python3 -m py_compile` 通过

已完成：
- 按当前同步后的 Stage0 主线启动一轮真实训练，并在形成稳定趋势后停止做分析：
  - 训练命令：
    - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --run_name stage0_sync_pull_postpull_2026-04-20`
  - 运行目录：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-20_11-26-59_stage0_sync_pull_postpull_2026-04-20`
  - 对应 Isaac 日志：
    - `/tmp/isaaclab/logs/isaaclab_2026-04-20_11-26-59.log`
  - 对应 Hydra 输出：
    - `RL_Training/outputs/2026-04-20/11-26-59/`
  - 实际停止位置：
    - `iteration 18 / 700`
- 已完成：
  - 导出本轮 TensorBoard 标量：
    - `tensorboard_export/`
  - 读取并核对：
    - `params/env.yaml`
    - `params/agent.yaml`
    - `.hydra/config.yaml`
    - `.hydra/overrides.yaml`
    - `summary.json`
    - `latest_values.csv`
- 本轮关键结果：
  - 训练启动与数值稳定性正常：
    - `cuda:0` 正常
    - articulation / actuator 绑定正常
    - `Loss/value` 从约 `2.09e-3` 下降到约 `3.54e-5`
    - `Policy/mean_std` 保持在约 `0.199`
  - 当前同步后的 Stage0 真实网络输入已是：
    - `22 / 22` 观测
    - 不是旧记忆里的 `70 / 70`
  - 新 success / termination 口径已通过真实 run 验证：
    - `Tracking/goal_success_rate` 与 `Termination/success_rate` 对齐
    - 且本轮二者全程都为 `0`
  - 这轮 run 很快进入稳定的超时坏平衡：
    - 约从 `iteration 11` 起：
      - `mean_episode_length = 2399`
      - `time_out_rate = 1.0`
    - 末 `5` 轮：
      - `goal_pos_error ≈ 6.26 m`
      - `goal_completion_pct ≈ 21.8%`
      - `goal_heading_error_abs ≈ 0.362 rad`
  - 当前 reward 在上涨，但没有转化为真实到达：
    - `mean_reward` 从约 `0.128` 升到约 `1.559`
    - 但成功率仍为 `0`
  - 策略仍表现出高滑移推进特征：
    - 末 `5` 轮 `|longitudinal slip| ≈ 2.48`
    - 末 `5` 轮 `|slip angle| ≈ 0.387 rad`
    - 末 `5` 轮 `wheel_velocity_target_abs_mean ≈ 3.47 rad/s`
- 当前结论：
  - 当前 Stage0 主问题已不再是日志口径或 done 条件没接通
  - 而是：
    - 成功率真实为 `0`
    - 策略学成“活到超时”而不是“到达目标”
    - `12` 维接口下前 `6` 维球铰动作仍是死维度
    - `40 s` episode + `16 s` 重采样是否适合当前 Stage0 baseline 需要重新判断

已完成：
- 按用户要求重写并润色论文第 3 章 `chapter03.tex`：
  - 统一了底层运动学模型中的核心符号：
    - 实际构型 `\mathbf q`
    - 期望构型 `\mathbf q^d`
    - 六轮角速度目标 `\boldsymbol\Omega^d`
    - 球铰姿态角命令 `\mathbf q^{cmd}`
  - 将章节推导顺序重构为：
    - 坐标系与几何参数
    - 构型变量
    - 高层输入与底层输出
    - 模块参考点位置
    - 轮心位置与滚动方向
    - 轮心速度传播
    - 滚动约束投影
    - 六轮轮速分配矩阵
    - 球铰姿态角命令输出
  - 清理并修正了原稿中的问题：
    - 旧标签引用残留
    - `eq:qcmd_output` 重复定义
    - 实际构型/期望构型记号混用
    - 若干公式衔接不够严密、物理意义说明不足
- 本轮修改文件：
  - `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 验证：
  - 在 `毕业论文/毕业论文模板/LaTeX/` 下执行：
    - `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`
  - 论文主文件编译通过
  - 当前仍存在与本轮无关的既有告警：
    - `chapter01` 中 2 个未定义参考文献
- 当前结论：
  - 第 3 章的模型参数定义、物理意义、符号口径和公式推导链已经收敛到一致
  - 后续如果继续写第 4 章或摘要中的模型说明，应直接沿用本轮统一后的符号体系

已完成：
- 按用户进一步澄清的要求，再次调整论文第 3 章中“车轮速度分配”部分的推导路线：
  - 不改当前模型输入输出口径
  - 只把推导方法改回原稿中的“局部坐标 / 模块刚体速度”链条
- 当前轮速分配部分已改为：
  - 先定义各模块局部坐标系中的轮心安装向量
  - 再由中模块期望平面运动与当前实际构型得到各模块局部刚体速度
  - 再用刚体速度传播得到轮心速度
  - 再取轮心速度在局部 `x_i` 滚动方向上的分量
  - 最后通过无滑移条件得到左右轮角速度，并写成 `H_i` 与 `J_w(q)` 矩阵形式
- 当前保持不变的模型输入输出：
  - 输入仍为：
    - `u_v = [V_x^d, \Omega_z^d]^T`
    - `q^d`
  - 输出仍为：
    - `\boldsymbol\Omega^d`
    - `q^{cmd} = q^d`
- 本轮修改文件：
  - `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 当前结论：
  - 第 3 章轮速分配部分已恢复为更接近原稿的方法链
  - 但没有把 `\dot{\mathbf q}` 重新引入为模型输入，现有控制接口保持不变

已完成：
- 按用户最新要求，将论文第 3 章“车轮速度分配”部分从“模块刚体速度中间层”写法恢复为“轮心相对中模块坐标系直接推导”形式：
  - 先在各模块局部坐标系定义轮心安装向量
  - 再统一写出六个轮心在主坐标系下的位置与滚动方向
  - 再由中模块期望平面运动直接传播到各轮心速度
  - 再通过滚动方向投影与无滑移条件得到单轮角速度
  - 最后按六个单轮行向量堆叠成 `J_w(q)`
- 当前保持不变的模型输入输出：
  - 输入仍为：
    - `u_v = [V_x^d, \Omega_z^d]^T`
    - `q^d`
  - 输出仍为：
    - `\boldsymbol\Omega^d`
    - `q^{cmd} = q^d`
- 本轮修改文件：
  - `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 验证：
  - 在 `毕业论文/毕业论文模板/LaTeX/` 下执行：
    - `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`
  - 主文件编译通过
  - 当前仍保留与本轮无关的既有问题：
    - `chapter01` 中 2 个未定义参考文献
- 当前结论：
  - 第 3 章轮速分配部分现已恢复为更紧凑的直接推导形式
  - 当前构型 `q` 仍只通过轮心位置、滚动方向和 `J_w(q)` 进入轮速分配，未重新引入 `\dot{\mathbf q}`

已完成：
- 按用户要求，在论文第 3 章正文后新增“代入具体结构参数向量后的最终解析结果”小节：
  - 代入了：
    - `{}^{2}\mathbf a`
    - `{}^{1}\mathbf b`
    - `{}^{3}\mathbf b`
    - 左右轮安装向量
  - 显式给出了：
    - 前后模块参考点位置的展开形式
    - 前、中、后模块滚动方向单位向量
    - 六个单轮分配行向量 `j_w(q)`
    - 六个车轮角速度目标最终显式表达式
  - 单独总结了：
    - 轮速分配子模型输入输出
    - 整套底层运动学模型输入输出
- 本轮修改文件：
  - `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 验证：
  - 在 `毕业论文/毕业论文模板/LaTeX/` 下执行：
    - `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`
  - 主文件编译通过
  - 当前仍保留与本轮无关的既有问题：
    - `chapter01` 中 2 个未定义参考文献

已完成：
- 按用户要求收缩当前 Stage0 policy 观测输入：
  - 送入网络的观测只保留：
    - `wheel_joint_vel`
    - `goal_relative_command`
    - `last_action`
  - actor / critic 观测维度由 `71 / 71` 改为 `22 / 22`
  - 其余状态量不再进入网络，但仍保留在 TensorBoard / step metrics 中用于查看行为质量
- 同步修改：
  - `observation descriptor`
  - `compute_actor_observation`
  - `policy obs noise magnitudes`
  - `policy obs dim`
- 按用户要求调整 TensorBoard 与终端日志口径：
  - 关键行为质量指标改为优先排序
  - 新增前置总览分组：
    - `00_Behavior/...`
  - 全程为 `0` 的标量改为默认不写入 TensorBoard
  - `tensorboard_export.py` 也改为可清理任意全零标量序列
- 本轮修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `docs/RL阶段训练参数一览表.md`
  - `logs/daily_work_log.md`
- 验证：
  - `python3 -m py_compile` 已通过：
    - `utils/io_descriptors.py`
    - `mdp/observations.py`
    - `utils/math_utils.py`
    - `rsl_rl/utils/logger.py`
    - `utils/tensorboard_export.py`

已完成：
- 重新按当前 Stage0 源码核对并重写 `docs/RL阶段训练参数一览表.md`：
  - 修正回合时长为 `40.0 s`
  - 修正最大控制步数为 `2400`
  - 修正 PPO rollout 为 `512 steps / env`
  - 修正执行器参数为当前 `stage0_cfg` 实际数值
  - 明确当前 episode 内会因 `resampling_time = 16.0 s` 发生多次目标重采样
  - 明确当前 `12` 维动作接口下球铰动作被冻结，实际有效控制主要是 `6` 维轮速直驱
- 同步修正 `docs/current_status.md` 中过期的 `episode_length_s` 口径

已完成：
- 按用户要求重构当前 Stage0 termination 逻辑：
  - 保留：
    - `time_out`
    - `ball_joint_out_of_bounds`
  - 新增并接入 episode 结束：
    - `is_success`
    - `far_from_target`
  - 移除旧的姿态类硬终止参与：
    - `bad_orientation`
    - `head_tail_roll_out_of_bounds`
- 当前实际终止条件：
  - `time_out`：
    - `episode_length_buf >= max_episode_length - 1`
  - `is_success`：
    - 距离目标 `< 0.2 m`
    - 朝向误差 `< 0.1 rad`
  - `far_from_target`：
    - `distance > cfg.commands.goal_distance + 3.0`
  - `ball_joint_out_of_bounds`：
    - 任一球铰超出当前上下限
- 同步修正：
  - `Tracking/goal_success_rate` 与 `Termination/success_rate` 改为同一判据
  - episode / TensorBoard 日志不再输出旧的姿态终止率
  - 新增 `Termination/far_from_target_rate`
- 本轮修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `docs/RL阶段训练参数一览表.md`
  - `logs/daily_work_log.md`
- 当前说明：
  - 这轮没有启动真实训练，只完成了代码与文档口径整改
  - 还需要下一轮 run 验证新 termination 对训练行为和统计曲线的影响
- 已完成验证：
  - `python3 -m py_compile` 通过

已完成：
- 按用户要求替换当前 Stage0 reward 主式，不再使用旧的：
  - `distance_progress`
  - `goal_direction_reward`
  - `goal_heading_reward`
  - `stop_reward`
  - `success_bonus`
  - `time_penalty`
- 当前已落地的新 reward 项：
  - `distance_to_target`
  - `reached_target`
  - `oscillation`
  - `angle_to_target`
  - `far_from_target`
  - `angle_diff`
- 本轮按用户口径实现细节：
  - `distance_to_target = 5.0 * (1 / (1 + 0.11 * distance^2)) / max_episode_length`
  - `reached_target = 5.0 * (2.0 * reward_scale)`
  - `reward_scale = (max_episode_length - episode_length_buf) / max_episode_length`
  - `reached_target` 触发条件：
    - 距离目标 `< 0.2 m`
    - `|goal_heading_error| < 0.1 rad`
  - `oscillation = -0.05 * mean(|action_t - action_t-1|^4) / max_episode_length`
  - `angle_to_target = -1.5 * where(|atan2(y_b, x_b)| > 2.0, |angle| / max_episode_length, 0)`
  - `far_from_target` 阈值按用户要求实现为：
    - `cfg.commands.goal_distance + 3.0`
  - `angle_diff = 5.0 * (1 / (1 + distance)) * (1 / (1 + |goal_heading_error|)) / max_episode_length`
  - `heading_soft_constraint` 本轮未接入
- 已同步修改：
  - reward 参数默认值
  - Stage0 默认容差：
    - `target_position_tolerance = 0.2`
    - `target_yaw_tolerance_deg = degrees(0.1)`
  - step 指标与 TensorBoard reward tag
- 本轮修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `docs/RL阶段训练参数一览表.md`
  - `logs/daily_work_log.md`
- 已完成验证：
  - `python3 -m py_compile` 通过

已完成：
- 按用户要求修改当前 RL 环境 command 语义：
  - 将命令维度从 `3` 改为 `4`
  - 原 `commands = [goal_rel_x, goal_rel_y, goal_rel_psi]`
  - 现改为 `commands = [goal_rel_x, goal_rel_y, goal_rel_z, goal_rel_heading]`
- 已在目标采样链中接入目标点高度查询：
  - 世界系先采样目标 `xy`
  - 再通过 `terrain_runtime.sample_heights_world_xy(...)` 查询该目标点高度作为 `goal_target_z_world`
  - 平地模式下高度返回 `0`
  - 生成地形模式下高度由高度图双线性插值给出
- 已完成 reward / termination / logger / 观测链同步整改：
  - heading 误差索引从旧的 `commands[:, 2]` 改为新的 `commands[:, 3]`
  - step 指标与 episode 指标中的命令日志改为：
    - `goal_target_z_world`
    - `goal_target_heading_world`
    - `goal_rel_z`
    - `goal_rel_heading`
  - 原 `goal_rel_psi`、`goal_target_yaw_world`、`goal_yaw_error_abs` 不再是当前主线口径
- 当前维度变化：
  - `num_commands = 4`
  - Stage0 actor / critic 观测维度由 `70 / 70` 变为 `71 / 71`
- 本轮修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `docs/RL阶段训练参数一览表.md`
  - `logs/daily_work_log.md`
- 已完成验证：
  - `python3 -m py_compile` 通过
- 当前说明：
  - 本轮未直接启动环境实例验证 `observation_space`，因为当前 shell 环境缺少 `gymnasium`

## 2026-04-19

已完成：
- 按用户要求整理 GitHub 同步边界：
  - 新增 `.gitignore` 规则，忽略：
    - `RL_Training/logs/`
    - `RL_Training/outputs/`
  - 后续默认只同步源码、文档和配置，不再把训练日志、checkpoint、导出结果直接上传到 GitHub
- 已将该同步策略写入项目记忆：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
- 当前结论：
  - 常规代码同步与训练产物上传已经解耦
  - 后续只有在用户明确要求上传训练结果，或跑出较理想模型时，才提醒是否需要单独上传训练产物

已完成：
- 对新 bounded policy 主线下的首轮真实 Stage0 run 做完整诊断：
  - 运行目录：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-19_16-16-01`
  - 匹配并读取：
    - `/tmp/isaaclab/logs/isaaclab_2026-04-19_16-16-01.log`
    - `RL_Training/outputs/2026-04-19/16-16-01/.hydra/config.yaml`
    - `RL_Training/outputs/2026-04-19/16-16-01/.hydra/overrides.yaml`
    - `params/env.yaml`
    - `params/agent.yaml`
- 已补导出 TensorBoard 标量：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-19_16-16-01/tensorboard_export/`
- 本轮关键诊断结论：
  - 这次 run 已确认 bounded policy 动作链整改有效：
    - `Action/policy_abs_mean` 与 `Action/processed_abs_mean` 全程一致
    - `Action/policy_std` 与 `Action/processed_std` 全程一致
    - 说明策略采样动作没有再被 env 预处理链改写
  - 训练启动和数值稳定性没有暴露新炸点：
    - Isaac Sim 原始日志无启动级报错
    - articulation / actuator 绑定正常
    - late-stage termination 基本只剩：
      - `success`
      - `time_out`
  - 相比 `2026-04-18_16-05-54_stage0_direct12_longslipcost_v1`，这轮不再是“零成功 + 全程超时”的坏平衡：
    - `Termination/success_rate` 峰值约 `0.877`
    - 末值约 `0.432`
    - `goal_pos_error` 末 `50` 轮均值约 `1.63 m`
    - `goal_completion_pct` 末 `50` 轮均值约 `79.6%`
  - 但仍暴露出新的主问题：
    - 当前 Stage0 接口仍是 `12` 维动作
    - 其中 `6` 个球铰动作在 `stage0_cfg` 中被固定为 `0`
    - 实际有效控制只剩 `6` 个轮速直驱维度，存在明显死动作维度
  - 策略仍高度依赖高轮速 / 高滑移推进：
    - `|longitudinal slip|` 末 `50` 轮均值约 `2.38`
    - `|slip angle|` 末 `50` 轮均值约 `0.568 rad`
    - `wheel_velocity_target_abs_mean` 末 `50` 轮均值约 `8.03 rad/s`
  - 末端朝向质量没有和距离进展同步改善：
    - `goal_yaw_error_abs` 从约 `0.34 rad` 升到约 `1.04 rad`
    - 末 `50` 轮均值约 `1.17 rad`
  - 当前存在一个日志口径问题：
    - `Termination/success_rate` 明显非零
    - 但 `Tracking/goal_success_rate` 整轮恒为 `0`
    - 该指标当前不能再作为主判断依据
- 本轮更新文件：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 当前结论：
  - bounded policy 这条动作执行链已经通过真实 run 验证
  - 当前主阻塞已从“动作链数值/实现问题”转移到：
    - 有效动作语义不一致
    - 高滑移推进
    - success 指标口径失真
- 按用户要求整理 `docs/MGDP_stage1_reward.md` 中的公式文档：
  - 将正文中的英文说明改为中文
  - 将文档中的公式统一改为 Obsidian 可编译数学语法
  - 保留 `mermaid` reward 结构图
  - 将历史失效的 `legged_gym/random_dog` 仓库内链接改为“历史源码映射说明”
  - 当前该文档仍是历史 `MGDP` 口径整理，并不对应当前 `RL_Training/` 主线实现

## 2026-04-18

已完成：
- 按用户授权持续在 GPU 上进行 Stage0 主线重构、训练、分析与反复迭代，不再停在单轮 reward 诊断。
- 本轮新增并验证的源码修改：
  - reward 新增：
    - `pose_reward`
    - `capture_reward`
    - `module_pitch_cost_penalty`
    - `arrival_stability_gate`
  - termination 新增：
    - `head_tail_pitch_out_of_bounds`
  - allocator 新增：
    - 基于 `wheel_longitudinal_slip` 与 `wheel_normal_contact_force` 的 traction-aware scaling
  - step / TensorBoard 指标新增：
    - `Tracking/goal_success_rate`
    - traction-aware action 指标
    - reward 细分项
- 本轮连续真实 run 包括：
  - `2026-04-18_14-15-56_stage0_quality_allocator_v1`
  - `2026-04-18_14-39-45_stage0_quality_allocator_v2b`
  - `2026-04-18_14-42-38_stage0_quality_capture_v1`
  - `2026-04-18_14-44-16_stage0_quality_capture_v2`
  - `2026-04-18_14-47-06_stage0_goal4_quality_v1`
  - `2026-04-18_14-51-41_stage0_goal4_32s_v1`
  - `2026-04-18_14-55-12_stage0_goal4_32s_pose_v1`
  - `2026-04-18_14-57-33_stage0_goal4_32s_pose_tracrelax_v1`
  - `2026-04-18_14-59-54_stage0_goal4_straight_v1`
  - `2026-04-18_15-02-04_stage0_goal2_straight_v1`
- 本轮关键过程结论：
  - `4m` 和 `8m` 几何下，即使加入 pose reward、capture reward 和 32 秒时域，策略仍会长期停在约 `2m` 量级的平台区。
  - 单纯延长 episode 不足以解决后段平台。
  - 单纯放松 traction-aware allocator 会抬高 slip 和 heading 误差，使结果更差。
  - 将 Stage0 几何收缩为：
    - `goal_distance = 2.0`
    - `goal_direction_max_deg = 0.0`
    - `goal_heading_delta_max_deg = 0.0`
    后，才首次形成真正可复现、零硬终止、且成功率进入两位数的 flat-ground baseline。
- 当前最佳 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-18_15-02-04_stage0_goal2_straight_v1`
- 已导出 TensorBoard：
  - `tensorboard_export/`
- 当前代表性末值：
  - `goal_pos_error ≈ 0.767 m`
  - `goal_success_rate ≈ 0.193`
  - `goal_yaw_error_abs ≈ 0.068 rad`
  - `|longitudinal slip| ≈ 1.465`
  - `|slip angle| ≈ 0.394 rad`
  - `tilt_deg ≈ 0.310`
  - `traction_limit_scale_mean ≈ 0.629`
  - `time_out_rate = 1.0`
- 本轮更新文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `docs/RL阶段训练参数一览表.md`
  - `docs/Stage0问题演化与当前瓶颈分析.md`
  - `logs/daily_work_log.md`
- 当前结论：
  - Stage0 现阶段默认主线应固定为 `2m` 正前方静态目标 baseline。
  - 后续应从这条基线出发，先抬最终成功率，再逐步恢复方向扰动与更长目标距离。

已完成：
- 按用户授权在 GPU 上启动当前工作区真实代码口径下的新一轮 `Stage0` 训练，并按用户后续要求提前停止做分析：
  - 运行目录：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-18_10-33-52_gpu_stage0_obs66_goal8_v1`
  - 停止位置：
    - `iteration 464 / 1000`
  - 实际生效口径：
    - `66 / 66` 观测
    - `8维动作`
    - `goal_distance = 8.0 m`
    - `episode_length_s = 16.0`
    - `num_steps_per_env = 240`
- 已完成：
  - 对该 run 导出 TensorBoard 标量：
    - `tensorboard_export/`
  - 读取：
    - `params/env.yaml`
    - `params/agent.yaml`
    - `git/Graduation-Project.diff`
- 当前结果：
  - 训练链路稳定：
    - `cuda:0` 正常
    - `time_out_rate` 后段为 `1.0`
    - `ball_joint_limit_rate` 后段为 `0`
  - 但后段进入平台区：
    - `goal_completion_pct` 末 50 轮均值约 `51.0%`
    - `goal_pos_error` 末 50 轮均值约 `3.92 m`
    - `goal_yaw_error_abs` 末 50 轮均值约 `0.289 rad`
    - `|longitudinal slip|` 末 50 轮均值约 `1.63`
    - `|slip angle|` 末 50 轮均值约 `0.723 rad`
    - `tilt_deg` 末 50 轮均值约 `5.29°`
  - `reward` 抬升并不等于平均运动质量继续变好：
    - `progress` 从前 20 轮均值约 `0.293` 降到末 50 轮均值约 `0.0866`
    - `gated_progress` 虽提升到末 50 轮均值约 `0.1168`
    - 但 `target_bonus` 末 50 轮均值也已到约 `0.247`
- 当前结论：
  - 这轮首先证明当前代码可稳定训练
  - 但没有证明已经学到更健康的低滑移、低姿态消耗策略
  - 当前更像是进入了“能活到超时、能部分对准目标、但仍靠较高滑移和姿态余量换取回报”的平台区

已完成：
- 按用户确认将 `long slip cost` 落地为显式负代价：
  - 先取 `6` 轮 `|long slip|` 的均值
  - 采用“死区后二次罚”：
    - `weight * relu(mean_abs_long_slip - deadzone)^2`
  - 当前默认参数：
    - `deadzone = 0.3`
    - `weight = 0.25`
- 同时补齐：
  - reward 配置参数
  - `env.py` step 指标导出
  - TensorBoard tag 映射
- 当前 reward 口径：
  - `composite_gate = (heading_gate + lateral_slip_gate) / 2`
  - `lateral_slip_gate` 基于 `6` 轮 `|slip_angle|` 均值
  - `longitudinal_slip_gate` 不再参与 gate 路径
  - 总 reward 现在显式扣除：
    - `longitudinal_slip_cost_penalty`
- 本轮修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 当前结论：
  - `long slip` 现在已经从“待讨论”进入“已落地的显式惩罚项”
  - 后续是否需要改 `deadzone` 或 `weight`，应通过新 run 结果再判断

已完成：
- 按用户要求修改当前 Stage0 reward 结构：
  - `long slip` 先从 gate 路径中移出
  - `lateral slip gate` 保留，但不再做 `6` 轮连乘
  - 改为先取 `6` 轮 `|slip_angle|` 的均值，再进入当前余弦 gate 形式
  - `composite_gate` 从三项平均改为两项平均：
    - `heading_gate`
    - `lateral_slip_gate`
- 当前明确未做：
  - 没有擅自定义 `long slip` 的显式负代价函数
  - 该函数形式仍待后续讨论
- 本轮修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 当前结论：
  - 这一轮只完成用户已经明确决定的 reward 结构调整
  - `long slip` 显式负代价仍未落地，因此当前 reward 对 `long slip` 暂时没有直接作用

已完成：
- 按用户要求将以下状态量正式接入 `Stage0` policy 观测主干：
  - `ball_joint_vel`
  - `ball_joint_target_error`
  - `head_roll_pitch / tail_roll_pitch`
  - `wheel_joint_vel`
- 本轮同时改齐：
  - 实际 actor 观测拼接顺序
  - `observation descriptor`
  - `observation noise magnitudes` 顺序
- 当前观测维度变化：
  - Actor：`44 -> 66`
  - Critic：`44 -> 66`
- 本轮新增修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
- 当前结论：
  - 这些观测项此前已经能被计算并记录到原始指标里，但没有真正喂给 policy
  - 现在已消除“日志能看见、policy 吃不到”的不一致

已完成：
- 按用户要求，将当前 `Stage0` RL 环境设计从实验支线回退到目前最健康的主线版本：
  - 保留：
    - `8维动作空间 + allocator`
    - 单阶段 tracking reward
    - 原始 Stage0 termination 结构
  - 删除：
    - `traction-aware v2`
    - `capture reward / terminal phase`
    - `success dwell` 终止
    - `explicit slip cost`
- 本轮源码回退涉及：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 当前回退结果：
  - reward 回到：
    - `target_bonus + progress * composite_gate * roll_gate`
  - termination 回到：
    - `bad_orientation`
    - `head_tail_roll_out_of_bounds`
    - `ball_joint_out_of_bounds`
    - `time_out`
  - step / episode 日志已去掉：
    - `capture_rate`
    - `capture_reward`
    - `success_rate`
    - traction-aware 相关 action 指标
    - explicit slip cost 相关 reward 指标
- 参考回退口径：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_18-02-38_axis_usage_probe_v1`
- 同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `docs/RL阶段训练参数一览表.md`
  - `logs/daily_work_log.md`
- 按用户要求整理 `docs/MGDP_stage1_reward.md` 中的公式文档，当前内容已改为中文表述：
  - 已将原有公式统一改为 Obsidian 可编译数学语法
  - 保留 `mermaid` reward 结构图
  - 将正文中的英文说明统一改为中文
- 同时清理该文档中的历史失效引用：
  - 原文引用的 `legged_gym/random_dog` 相关源码路径在当前仓库中均不存在
  - 已改为“历史源码映射说明”的文字口径，不再保留失效链接
- 修改文件：
  - `docs/MGDP_stage1_reward.md`
  - `docs/current_status.md`
  - `logs/daily_work_log.md`
- 当前结论：
  - `MGDP Stage 1 reward` 公式说明已经可以直接作为中文阅读稿或论文笔记底稿使用
  - 当前文档仍是历史 `MGDP` 口径整理，并不对应当前 `RL_Training/` 主线实现

## 2026-04-17

已完成：
- 按用户授权在 GPU 上完成一组三轮 `goal_distance = 8 m` 对照训练，并统一导出 TensorBoard：
  - `2026-04-17_21-55-30_exp1_goal8_baseline_no_traction_v1`
  - `2026-04-17_22-15-03_exp2_goal8_traction_v2_v1`
  - `2026-04-17_22-34-48_exp3_goal8_explicit_slip_cost_v1`
- 当前三轮设置分别是：
  - 实验 1：
    - `goal_distance = 8.0`
    - `traction-aware = off`
    - reward 结构保持原状
  - 实验 2：
    - `goal_distance = 8.0`
    - `traction-aware = on`
    - 当前 v2 参数：
      - `min_scale = 0.55`
      - `longitudinal start/full = 1.6 / 2.2`
      - `slip angle start/full = 35° / 50°`
      - `contact force low/high = 0.02 / 0.08`
  - 实验 3：
    - `goal_distance = 8.0`
    - `traction-aware = off`
    - `use_slip_gates = False`
    - `use_explicit_slip_cost = True`
    - `longitudinal_slip_cost_weight = 0.25`
    - `lateral_slip_cost_weight = 0.20`
- 为实验 3 新增 reward 开关与日志：
  - `use_slip_gates`
  - `use_explicit_slip_cost`
  - `longitudinal_slip_cost_weight`
  - `lateral_slip_cost_weight`
  - step 日志新增：
    - `Reward/longitudinal_slip_cost`
    - `Reward/lateral_slip_cost`
    - `Reward/slip_cost_penalty`
- 当前横向结果：
  - 实验 1 `8m baseline`：
    - 后段 `goal_completion_pct ≈ 47.93%`
    - `goal_pos_error ≈ 4.17 m`
    - `long slip ≈ 1.666`
    - `slip angle ≈ 0.639 rad`
    - `capture_rate ≈ 0.276`
    - `ball_joint_limit_rate` 后段均值约 `0`
  - 实验 2 `8m + traction-aware v2`：
    - governor 后段真实介入：
      - `traction_limit_scale_mean ≈ 0.654`
      - `traction_limit_velocity_mean_raw ≈ 7.85 rad/s`
    - 但结果基本不优于实验 1：
      - `goal_completion_pct ≈ 47.06%`
      - `goal_pos_error ≈ 4.24 m`
      - `long slip ≈ 1.669`
      - `slip angle ≈ 0.641 rad`
      - `ball_joint_limit_rate` 后段均值约 `0.141`
  - 实验 3 `8m + explicit slip cost`：
    - 后段 traction 指标改善最明显：
      - `goal_completion_pct ≈ 49.45%`
      - `goal_pos_error ≈ 4.04 m`
      - `long slip ≈ 1.596`
      - `slip angle ≈ 0.610 rad`
      - `capture_rate ≈ 0.321`
    - 但同时出现代价转移：
      - `tilt_deg ≈ 0.255`
      - `ball_joint_limit_rate` 后段均值约 `0.047`
- 当前结论：
  - 单把目标段缩到 `8 m` 就已经是有效改动
  - 当前 `traction-aware v2` 已触发，但收益不足，不适合作为默认主线
  - 显式 `slip cost` 有价值，但如果继续，必须配套限制球铰余量或姿态代价
- 修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

已完成：
- 将当前项目工作区按完整范围同步到 GitHub：
  - 同步口径：
    - 当前整个 worktree
    - 包含代码改动、文档更新、训练日志、结果图与新增脚本
  - 远端：
    - `git@github.com:MARS-ROBOTICS-star/Graduation-Project.git`
  - 校验：
    - `python3 -m py_compile` 已对本轮改动的 Python 文件通过静态编译检查

已完成：
- 按用户要求补充当前 `traction-aware wheel limit` 参数的可视化说明：
  - 新增脚本：
    - `scripts/plot_traction_limit_curves.py`
  - 生成结果：
    - `results/traction_limit/traction_limit_curves_stage0.png`
  - 当前图中直接画出：
    - `|longitudinal slip| -> scale`
    - `|slip angle| -> scale`
    - `normalized contact force -> scale`
    - `wheel velocity limit -> rad/s`
- 同时修正脚本运行环境：
  - 默认设置：
    - `MPLCONFIGDIR=/tmp/matplotlib`
  - 目的：
    - 避免当前工作区下 `matplotlib` 因默认缓存目录不可写而反复告警
- 当前结论：
  - 后续讨论 traction-aware 参数时，可以直接基于图来解释阈值起点、打满点和最小限幅
- 修改文件：
  - `scripts/plot_traction_limit_curves.py`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

已完成：
- 按用户要求，先从执行层入手，为当前 `Stage0` 加入第一版 `traction-aware wheel limit`：
  - 不改 allocator 的 Jacobian 主体
  - 只在 allocator 给出 `wheel_targets` 之后、写入车轮关节目标之前，加一层逐轮动态轮速上限
- 当前动态轮速上限同时受 3 类运行态信号控制：
  - absolute 纵滑
  - absolute 侧滑角
  - 归一化法向接触力
- 当前 Stage0 生效参数：
  - `traction_limit_min_scale = 0.35`
  - `longitudinal_slip_start/full = 0.6 / 1.5`
  - `slip_angle_start/full = 12° / 28°`
  - `contact_force_low/high = 0.05 / 0.12`
- 三路限幅当前取更严格者：
  - `min(longitudinal_scale, lateral_scale, contact_scale)`
- 本轮修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 当前新增日志指标：
  - `Action/traction_limit_scale_mean`
  - `Action/traction_longitudinal_scale_mean`
  - `Action/traction_lateral_scale_mean`
  - `Action/traction_contact_scale_mean`
  - `Action/traction_limit_velocity_mean_raw`
- 验证：
  - `python3 -m py_compile` 对修改文件的静态编译检查已通过
  - 在真实 `Isaac Lab` 环境中完成 1 轮 GPU 冒烟：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_21-20-08_traction_limit_smoke_v1`
    - `max_iterations = 1`
  - 当前确认：
    - 训练入口正常
    - 环境创建正常
    - actor / critic 维度正常
    - reward 链路正常
    - wheel target 动态限幅链路正常
- 当前结论：
  - `traction-aware wheel limit` 已经成功接入执行层
  - 但目前只完成了代码接入与最小真实冒烟
  - 还没有完成一轮足够长的对照训练，因此还不能判断它是否真的改善牵引效率
- 在 `env_isaacLab` 中使用 GPU 跑完一轮新的 `Stage0 terminal phase` 真实训练：
  - 命令：
    - `/home/ubuntu/miniconda3/envs/env_isaacLab/bin/python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --run_name terminal_phase_verify_v1`
  - 运行目录：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_20-21-01_terminal_phase_verify_v1`
  - Isaac Lab log：
    - `/tmp/isaaclab/logs/isaaclab_2026-04-17_20-21-01.log`
  - 本轮完整跑满：
    - `600 / 600`
  - 训练总耗时约：
    - `1023.29 s`
- 对该 run 补齐 TensorBoard 离线导出：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_20-21-01_terminal_phase_verify_v1/tensorboard_export/`
- 当前最终结果：
  - `Train/mean_reward ≈ 593.35`
  - `Train/mean_episode_length = 1439.0`
  - `Termination/time_out_rate = 1.0`
  - `Termination/ball_joint_limit_rate = 0.0`
  - `Termination/success_rate = 0.0`
  - `Tracking/goal_pos_error ≈ 6.94 m`
  - `Tracking/goal_completion_pct ≈ 42.18%`
  - `Tracking/goal_yaw_error_abs ≈ 0.0698 rad`
  - `Reward/capture_reward ≈ 0.00335`
  - `Phase/capture_rate ≈ 0.0091`
  - `Reward/target_bonus = 0.0`
  - `Loss/value ≈ 0.189`
- 当前结论：
  - terminal phase 改造没有把当前 Stage0 tracking 主线打坏
  - rollout 生存、tracking 和 PPO 数值稳定性都正常
  - `ball_joint_limit_rate` 只在早中期短暂抬升，后段已经回到 `0`
  - 当前主问题不是训练不稳定，而是：
    - capture phase 直到约 `iteration 299` 才开始偶发触发
    - 后段虽有少量 capture，但 `success_rate` 与 `target_bonus` 仍始终为 `0`
  - 当前直接判断为：
    - 在 `capture_switch_distance = 2.0 m` 下，terminal capture 触发过晚、触发过少，导致成功驻留学不到
- 已同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 按用户确认将当前 `Stage0` 改为显式 `terminal phase` 两阶段任务：
  - 远距离阶段保留：
    - `target_bonus + progress * composite_gate * roll_gate`
  - 近目标阶段切换为：
    - `target_bonus + capture_reward`
- 当前 terminal phase 关键实现已落地：
  - 切换距离：
    - `capture_switch_distance = 2.0 m`
  - capture 期底盘命令限幅：
    - `capture_base_forward_velocity_max = 0.40 m/s`
    - `capture_base_yaw_rate_max = 0.25 rad/s`
    - `capture_allow_reverse = True`
  - capture reward 当前由以下 4 个门平均组成：
    - 距离门
    - 航向门
    - 平面速度门
    - 偏航角速度门
  - 新增成功驻留终止：
    - 位置满足
    - 朝向满足
    - 平面速度小于 `0.12 m/s`
    - 偏航角速度小于 `0.12 rad/s`
    - 连续保持 `12` 个控制步
- 本轮修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 新增日志项：
  - `Reward/capture_reward`
  - `Phase/capture_rate`
  - `Termination/success_rate`
- 验证：
  - `python3 -m py_compile` 对上述 Python 修改文件的静态编译检查已通过
- 当前结论：
  - 终端捕获不再依赖“只改 command 几何”的局部策略
  - 已正式切换到“tracking + capture”两阶段任务实现
  - 还没有启动新训练，下一步应直接做一轮验证 run
- 按用户要求给当前 Stage0 step/终端日志新增：
  - `Tracking/goal_completion_pct`
- 当前口径为：
  - `max(goal_distance - goal_pos_error, 0) / goal_distance * 100%`
  - 表示当前目标段已经收缩掉的目标距离百分比
- 修改：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 当前效果：
  - 终端训练日志可直接看到当前目标段完成百分比
  - TensorBoard 中也会新增：
    - `Tracking/goal_completion_pct`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 按用户确认将当前 `Stage0` 动作链从：
  - `6 维球铰 + 6 维轮速直驱`
  改为：
  - `6 维球铰 + 2 维底盘平面命令`
- 修改：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- 当前新动作语义为：
  - 前 `6` 维：
    - 球铰目标动作
  - 后 `2` 维：
    - `a_base = [a_v, a_w]`
- 当前 env 内已新增：
  - `a_base -> [v_x_cmd, yaw_rate_cmd]` 映射
  - measured planar-command transform
  - `TorchWheelSpeedAllocator` 调用链
- 当前 Stage0 默认底盘命令参数：
  - `base_forward_velocity_max = 1.2 m/s`
  - `base_yaw_rate_max = 0.6 rad/s`
  - `base_allow_reverse = False`
- 当前 wheel target 生成流程已改为：
  - policy 输出 `a_base`
  - env 映射得到 `[v_x_cmd, yaw_rate_cmd]`
  - 结合当前球铰位置与球铰速度
  - 通过 allocator 生成 `6` 个轮速目标
  - 再统一按 `wheel_joint_velocity_limit_sim` 做限幅
- 结果影响：
  - `Stage0` 当前动作维度由 `12` 改为 `8`
  - 因 `last_action` 维度变化，当前 actor / critic 单帧观测维度由 `48` 改为 `44`
- 验证：
  - `python3 -m py_compile` 对以下文件的静态编译检查已通过：
    - `utils/io_descriptors.py`
    - `base/complete_car_cfg.py`
    - `mdp/actions.py`
    - `base/env.py`
    - `baseline/complete_car_stage0_cfg.py`
  - 尝试用普通 `python3` 做配置导入检查时，因当前环境缺少：
    - `pxr`
    导致动态导入未继续；这不是本轮代码语法错误
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 按用户要求修改当前观测口径：
  - `wheel_longitudinal_slip`
    - 当前不再在 observation 路径裁切
  - `wheel_slip_angle`
    - 当前不再在 observation 路径裁切
    - reward 内部仍保留侧滑角裁切
- 按用户要求把当前 Stage0 观测 scale 全部设为：
  - `1.0`
- 修改：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 使用 `python3 -m py_compile` 对以下文件完成静态编译检查，检查通过：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- 按用户要求给当前 Stage0 active reward 新增：
  - `longitudinal_slip_gate`
  - `lateral_slip_gate`
  - `composite_gate = (heading_gate + longitudinal_slip_gate + lateral_slip_gate) / 3`
- 当前总奖励主干改为：
  - `target_bonus + progress * composite_gate * roll_gate`
- 当前新增参数：
  - `longitudinal_slip_gate_scale = 0.3`
  - `lateral_slip_gate_scale = 6.0`
- 当前具体口径：
  - `longitudinal_slip_gate`
    - 六个轮子分别按
      - `exp[-1/2 * (slip / 0.3)^2]`
      计算后取乘积
  - `lateral_slip_gate`
    - 六个轮子的侧滑角先按
      - `[-pi/6, +pi/6]`
      截断
    - 再逐轮按
      - `0.5 * cos(6 * slip_angle) + 0.5`
      计算后取乘积
- 修改：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 使用 `python3 -m py_compile` 对以下文件完成静态编译检查，检查通过：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 按用户要求把当前 Stage0 active reward 主线改回：
  - `target_bonus + progress * heading_gate * roll_gate`
- 当前前后车 absolute `roll` 不再进入 active reward。
- 按用户要求新增前后车 absolute `roll` 终止：
  - 当前前车或后车 absolute `|roll| > 35°` 时直接终止 episode
- 当前新增 termination 指标：
  - `Termination/head_tail_roll_limit_rate`
- 修改：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/Stage0_reward设计详解.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 使用 `python3 -m py_compile` 对以下文件完成静态编译检查，检查通过：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 对真实训练 run
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_15-30-13`
  补齐一轮 TensorBoard 离线导出，并与
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_14-12-39`
  做并排对比诊断。
- 运行：
  - `python RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_15-30-13`
  成功补齐：
  - `tensorboard_export/`
- 当前对比结论：
  - 新增前后车 absolute `roll` gate 后，姿态激进性显著下降：
    - `tilt_deg` 末 10 轮均值：
      - `15.83° -> 0.21°`
    - `head_roll_pitch_abs_mean_raw` 末 10 轮均值：
      - `0.709 -> 0.081 rad`
    - `ball_joint_pos_abs_mean_raw` 末 10 轮均值：
      - `0.406 -> 0.232`
  - 但任务完成质量下降：
    - `Train/mean_reward` 末 10 轮均值：
      - `1582.62 -> 1351.16`
    - `Tracking/goal_pos_error` 末 10 轮均值：
      - `5.64 -> 5.94 m`
    - `Tracking/goal_yaw_error_abs` 末 10 轮均值：
      - `0.338 -> 0.664 rad`
    - `Reward/target_bonus` 末 10 轮均值：
      - `0.0203 -> 0.0`
  - 牵引指标没有根本改善：
    - `wheel_longitudinal_slip_abs_mean_raw` 略降：
      - `0.831 -> 0.810`
    - `wheel_slip_angle_abs_mean_raw` 仍高且基本不变：
      - `0.740 -> 0.742 rad`
    - `wheel_normal_contact_force_sum_raw` 末 10 轮均值反而下降：
      - `0.948 -> 0.838`
- 当前判断：
  - `head_tail_roll_gate` 成功把策略推向了低 roll、低构型偏转的新解
  - 但它同时削弱了转向和航向修正所需的构型使用
  - 当前主要问题已从“姿态过激进”转为：
    - “过度保守，姿态很好但任务完成度下降”
- 已同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 按用户确认的 Stage0 任务定义修改当前 active reward：
  - 保留中车现有 `roll_gate`
  - 暂不启用 `straighten_gate`
  - 新增前后车 absolute `roll` 的软门控：
    - `head_roll_gate`
    - `tail_roll_gate`
    - `head_tail_roll_gate = min(head_roll_gate, tail_roll_gate)`
- 当前总奖励主干改为：
  - `target_bonus + progress * heading_gate * roll_gate * head_tail_roll_gate`
- 当前新增参数并固定为对称默认值：
  - `head_roll_free_deg = 8.0`
  - `tail_roll_free_deg = 8.0`
  - `head_roll_sigma_deg = 6.0`
  - `tail_roll_sigma_deg = 6.0`
- 当前前后车 gate 逻辑为：
  - 在各自 free 区内，gate 为 `1`
  - 超出 free 区后，按高斯形式连续衰减
  - 合成时取前后车两者中的更严格值
- 修改：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/Stage0_reward设计详解.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 使用 `python3 -m py_compile` 对以下文件完成静态编译检查，检查通过：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- 按用户要求补齐当前 reward 新项的日志与 TensorBoard 埋点：
  - `Reward/head_roll_gate`
  - `Reward/tail_roll_gate`
  - `Reward/head_tail_roll_gate`
- 修改：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 当前效果：
  - 终端训练日志可直接看到上述 3 个 reward 指标
  - TensorBoard 中也会以 reward 主块顺序写入上述 3 个 scalar
- 使用 `python3 -m py_compile` 对以下文件完成静态编译检查，检查通过：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 按用户要求重新设定当前 Stage0 球铰越界终止范围：
  - yaw：`[-0.6, 0.6]`
  - pitch：`[-1.0, 0.4]`
  - roll：`[-0.5, 0.5]`
- 当前语义改为：
  - 只要任一球铰关节超出该范围，就直接终止 episode
- 本次仅修改：
  - `termination` 用的球铰范围
  - 未同步修改当前 action target 上下界
- 修改：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 按用户要求修改当前 active `tilt` 语义与坏姿态终止口径：
  - `Observation/tilt_deg`
  - `bad_orientation`
  当前都只看中车 `body_car_chassis` 的 `|roll|`
  - 不再把 `pitch` 计入当前坏姿态定义
- 修改：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 对真实训练 run
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_14-12-39`
  完成一轮完整离线诊断，并与上一轮
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_13-21-54`
  做了并排对比。
- 运行：
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_14-12-39`
  成功补齐本次 run 的 TensorBoard 离线导出。
- 当前对比结论：
  - 生存显著改善：
    - `mean_episode_length ≈ 1400.44 / 1439`
    - `time_out_rate ≈ 1.0`
    - `ball_joint_limit_rate ≈ 0.0`
  - 目标推进更强：
    - `goal_pos_error ≈ 5.38 m`
    - `target_bonus` 已非零
  - `tilt_deg` 确实下降：
    - `21.21° -> 15.96°`
    但仍未进入低倾斜区
  - 仍存在：
    - `wheel_longitudinal_slip_abs_mean_raw ≈ 0.83`
    - `wheel_slip_angle_abs_mean_raw ≈ 0.74 rad`
    - `head_roll_pitch_abs_mean_raw ≈ 0.73 rad`
    - `Loss/value ≈ 203`
- 当前判断：
  - `roll_gate` 已经把策略从“高倾斜+频繁球铰越界”拉回到“中等倾斜但可长期存活”
  - 但它没有把姿态压到更低，主因是：
    - 只在 `|body_car_roll| > 5°` 时启用
    - 且只通过航向误差间接衰减推进
    - 当前 `roll_gate ≈ 0.95`，抑制力度偏弱
    - `tilt` 包含 pitch，而当前 gate 只看 roll
    - `30°` 的坏姿态阈值对当前 `15°~16°` 区间几乎不起作用
- 已同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 补充核对当前 active reward 的三个解释点，并同步更新：
  - `docs/RL阶段训练参数一览表.md`
- 已确认：
  - `pi / 16` 当前已经不是写死常数，而是具名参数：
    - `body_car_roll_gate`
- 已确认当前 `target_bonus_ratio = 0.03`、`goal_distance = 12.0`、`control_dt = 1/60` 时：
  - `target_bonus ≈ 22.27`
- 已补充说明：
  - `heading_distance_scale = goal_distance / (2 sin(goal_direction_max_deg))`
  当前更适合解释为：
  - `heading_gate` 的目标几何尺度
  - 不是小车真实性能意义下的最小转弯半径
- 按用户要求把当前 Stage0 reward 主线从：
  - `target_bonus + progress * heading_gate`
  调整为：
  - `target_bonus + progress * heading_gate * roll_gate`
- 当前新增 reward 组件：
  - `roll_gate`
- 当前生效逻辑改为：
  - 当 `|中车 roll| <= 5°` 时：
    - `roll_gate = 1`
  - 当 `|中车 roll| > 5°` 时：
    - `roll_gate = exp[-1/2 * (航向误差 / (pi/16))^2]`
- 本次修改文件：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 按用户要求把终止条件中的：
  - `orientation_limit_deg`
  从：
  - `45°`
  收紧为：
  - `30°`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/Stage0_reward设计详解.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 按用户要求调整当前 `Stage0` 时间配置，目标是：
  - 延长单目标可用时间
  - 保证每个重采样间隔内小车更有机会到达目标点
  - 同时保持一个 episode 内至少经历 `3` 个目标段
- 修改：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- 当前生效值改为：
  - `episode_length_s = 24.0`
  - `commands.resampling_time = 8.0`
  - `commands.goal_distance = 12.0`
- 当前默认 episode 目标时序改为：
  - `t = 0 s` 首次采样
  - `t = 8 s` 第一次重采样
  - `t = 16 s` 第二次重采样
  - 因而一个 `24 s` episode 默认覆盖 `3` 个目标段
- 本次调整依据：
  - 上一轮最小 reward run
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_13-21-54`
    中末段 `Reward/progress ≈ 1.64`
  - 按该量级估算，收缩 `12 m` 目标距离大约需要：
    - `12 / 1.64 ≈ 7.3 s`
  - 因此把单目标窗口从 `5.3 s` 拉到 `8.0 s`
    更符合“先确保能到达目标点”的当前目标
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 按用户要求把航向奖励中的 `kd` 收口为由任务几何自动计算：
  - 当前对应参数：
    - `heading_distance_scale`
  - 修改：
    - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - 当前计算口径改为：
    - `heading_distance_scale = goal_distance / (2 sin(goal_direction_max_deg))`
  - 在当前 Stage0 参数下：
    - `goal_distance = 12.0`
    - `goal_direction_max_deg = 30.0`
    - 因此 `heading_distance_scale = 12.0`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 对真实训练 run
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_13-21-54`
  完成一轮完整离线诊断，并补齐：
  - `tensorboard_export/`
- 已读取并核对：
  - `/tmp/isaaclab/logs/isaaclab_2026-04-17_13-21-54.log`
  - `RL_Training/outputs/2026-04-17/13-21-54/.hydra/overrides.yaml`
  - `params/env.yaml`
  - `params/agent.yaml`
  - `tensorboard_export/latest_values.csv`
  - `tensorboard_export/summary.json`
- 运行：
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_13-21-54`
  成功补齐本次 run 的 TensorBoard 离线导出。
- 已确认本轮 run 的主要正信号：
  - `Train/mean_reward ≈ 1365.38`
  - `Train/mean_episode_length ≈ 845.94 / 959`
  - `Reward/gated_progress ≈ 1.60`
  - `Tracking/goal_pos_error ≈ 7.38 m`
  - 当前最小 reward 主线下，策略已经明显学会持续推进目标。
- 已确认本轮 run 的主要问题：
  - `Termination/time_out_rate ≈ 0.57`
  - `Termination/ball_joint_limit_rate ≈ 0.43`
  - `Observation/tilt_deg ≈ 21.21°`
  - `Observation/wheel_slip_angle_abs_mean_raw ≈ 0.766 rad`
  - `Observation/wheel_longitudinal_slip_abs_mean_raw ≈ 0.790`
  - `Loss/value` 末段约 `47.8`，近 `10` 轮均值约 `98.6`
  - 当前 reset 主因不是翻车，而是球铰越界。
- 已对 `Observation/turn_radius_raw` 做训练结果解释：
  - 当前口径仍是：
    - `R = ||v_xy|| / |yaw_rate|`
  - 该指标表示车体系平面瞬时曲率半径，不是严格几何最小转弯半径。
  - 本轮 run 中：
    - `turn_radius_raw ≈ 10.05 m`
    - 近 `10` 轮均值约 `9.94 m`
  - 结合：
    - `goal_distance = 12.0`
    - `goal_direction_max_deg = 30.0`
    当前更像“大半径弧线推进”，不是“小半径急转能力”。
- 已同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 按用户要求把小车平面转弯半径接入当前 TensorBoard step metrics：
  - 修改：
    - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
    - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 当前新增指标：
  - `Observation/turn_radius_raw`
- 当前物理口径定义为：
  - 中模块 COM 在车体系下的平面瞬时转弯半径
  - $R = \sqrt{v_x^2 + v_y^2} / |\omega_z|$
- 当前环境变量取自：
  - `raw_obs_terms["base_lin_vel"][:, 0]`
  - `raw_obs_terms["base_lin_vel"][:, 1]`
  - `raw_obs_terms["base_ang_vel"][:, 2]`
- 为避免直行时半径发散，当前只在满足以下条件的 env 上统计均值：
  - `sqrt(v_x^2 + v_y^2) > 0.2`
  - `|\omega_z| > 0.05`
  - 若当前 step 没有有效转弯样本，则写入 `0.0`
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  完成静态编译检查，检查通过。
- 按用户要求将当前 Stage0 active reward 主线强制收口为：
  - `target_bonus + progress * heading_gate`
- 修改 reward 实现：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - 当前 reward component 只保留：
    - `target_bonus`
    - `progress`
    - `heading_gate`
    - `gated_progress`
- 当前已从 active reward 计算链路中移除：
  - `roll_gate`
  - `speed_gate`
  - `force_gate`
  - `vertical_speed_gate`
  - `ball_joint_speed_gate`
  - `wheel_action_rate_gate`
  - `longitudinal_slip_gate`
  - `lateral_slip_gate`
  - `composite_gate`
- 同步修改 step metrics 与 TensorBoard / 终端 logger：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  - 当前 reward 日志面板只保留：
    - `Reward/target_bonus`
    - `Reward/progress`
    - `Reward/heading_gate`
    - `Reward/gated_progress`
    - `Reward/total`
- 同步精简 reward 配置项：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - 当前 `RewardParamsCfg` 只保留 active 参数：
    - `target_bonus_ratio`
    - `target_position_tolerance`
    - `target_yaw_tolerance_deg`
    - `heading_distance_scale`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/Stage0_reward设计详解.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/Stage0_reward设计详解.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 reward 已不再直接用 reward gate 去压滑移、受力、滚转、球铰速度和平滑性。
- 后续若训练行为发生变化，应优先从：
  - 目标任务定义
  - 观测
  - 动作输出结构
  - 终止条件
 角度解释，而不是再把原因归到旧 gate。

下一步：
- 基于新的最小 reward 主线，重新观察：
  - `progress`
  - `heading_gate`
  - `goal_pos_error`
  - `goal_yaw_error_abs`
  与实际滑移/姿态指标之间的耦合关系。

## 2026-04-16

已完成：
- 按用户要求整理当前 active Stage0 reward 设计，并输出独立说明文档：
  - `docs/Stage0_reward设计详解.md`
  - 文档已包含：
    - 当前全部 reward 项
    - 每项数学公式
    - 参数含义
    - 当前取值
    - 当前取值理由
  - 随后按用户要求将文档中的公式表达改为数学符号形式
  - 已去掉代码块中的英文公式写法
- 按用户要求清理 `Stage0` TensorBoard 空指标显示：
  - 修改：
    - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
    - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py`
  - 当前对以下 termination 原因指标启用“零值稀疏写入”：
    - `Termination/terminated_rate`
    - `Termination/bad_orientation_rate`
    - `Termination/ball_joint_limit_rate`
  - 若上述指标在整段 run 中始终为 `0`，则后续新 run 默认不再在 TensorBoard 中创建对应 tag。
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py`
  完成静态编译检查，检查通过。
- 先在临时副本验证了事件文件重写逻辑：
  - `/tmp/tb-prune-KC0Msm/2026-04-16_13-20-05`
  - 验证通过后再处理真实 run。
- 运行：
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_13-20-05 --prune-sparse-zero-tags`
  已完成真实 run 事件文件清理与重新导出。
- 当前真实 run
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_13-20-05`
  的 TensorBoard termination 标签现仅保留：
  - `Termination/00_time_out_rate`
  已删除的空指标：
  - `Termination/01_terminated_rate`
  - `Termination/02_bad_orientation_rate`
  - `Termination/03_ball_joint_limit_rate`
- 原始事件文件已备份到：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_13-20-05/tensorboard_export/original_events/events.out.tfevents.1776316811.ubuntu22.20391.0`

- 按用户要求将 Stage0：
  - `goal_distance`
  改为：
  - `12.0`
- 直接启动真实 GPU 训练：
  - `/home/ubuntu/miniconda3/envs/env_isaacLab/bin/python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --run_name goaldist12_v1`
- 本轮 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_13-36-23_goaldist12_v1`
  实际在 `iteration 13/300` 主动停止，因为前期问题已足够明显，无需完整跑完。
- 对新一轮短距离多目标 Stage0 run
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_13-20-05`
  做了一轮完整离线诊断。
- 运行：
  - `python RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_13-20-05`
  成功补齐本次 run 的 TensorBoard 离线导出。
- 按用户要求重构 Stage0 配置维护方式：
  - `baseline/complete_car_stage0_cfg.py` 当前已显式集中维护 Stage0 活跃参数
  - 后续修改 Stage0 默认参数时，不再需要先回到：
    - `base/complete_car_cfg.py`
- 修改命令配置：
  - `episode_length_s = 16.0`
  - `resampling_time = 5.3`
  - `goal_distance = 3.0`
  - `goal_direction_max_deg = 30.0`
  - `goal_heading_delta_max_deg = 12.0`
- 修改基类装配逻辑：
  - `CompleteCarEnvCfg.__post_init__()` 不再强制把：
    - `commands.resampling_time`
    对齐到：
    - `episode_length_s`
- 修改命令采样逻辑：
  - `goal_heading_delta_max_deg` 当前作为独立参数参与采样
  - 不再默认使用：
    - `goal_direction_max_deg / 2`
- 按用户要求调整 TensorBoard step metrics 埋点：
  - `Command/*` 当前不再对全部环境取均值
  - 当前改为只记录：
    - `env_0`
  - 停止输出：
    - `Observation/base_lin_vel_x_raw`
    - `Observation/base_ang_vel_yaw_raw`
  - 旧主线中的：
    - `Tracking/ang_vel_yaw_abs_error`
    - `Tracking/lin_vel_x_abs_error`
    当前 active goal-conditioned Stage0 已不再输出
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  完成静态编译检查，检查通过。
- 按用户要求统一 TensorBoard termination 日志口径：
  - 旧的 `episode_reset/*` 输出已改名并并入：
    - `Termination/*`
  - 原先 step-level 的 `Termination/*` 已停止输出
  - 当前新 run 中将不再出现：
    - `episode_reset/terminated_rate`
    - `episode_reset/time_out_rate`
    - `episode_reset/bad_orientation_rate`
    - `episode_reset/ball_joint_limit_rate`
- 按用户要求继续精简 Observation 埋点：
  - 删除：
    - `Observation/wheel_normal_contact_force_abs_mean_raw`
- 按用户要求调整日志显示优先级：
  - 修改：
    - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  - 当前训练终端日志只输出高频必看的核心项
  - 低频或重复项不再在终端逐轮打印
  - TensorBoard 中高频必看项已加排序前缀：
    - `00_`
    - `01_`
    - `02_`
    用于把重点图放到每个命名空间最前面
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
  完成静态编译检查，检查通过。
- 对完整 `300` iteration 真实训练 run
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_10-12-26`
  做了一轮完整离线诊断。
- 已定位并读取：
  - `/tmp/isaaclab/logs/isaaclab_2026-04-16_10-12-26.log`
  - `params/env.yaml`
  - `params/agent.yaml`
  - `tensorboard_export/latest_values.csv`
  - `tensorboard_export/summary.json`
  - 全部 scalar CSV
- 运行：
  - `python RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-16_10-12-26`
  成功补齐本次 run 的 TensorBoard 离线导出。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py`
- `docs/RL阶段训练参数一览表.md`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 本次 run 不是启动失败，也不是 rollout 不健康。
- 到 `iteration 299/300`：
  - `Train/mean_reward ≈ 55.87`
  - `Train/mean_episode_length ≈ 903 / 959`
  - `Tracking/goal_pos_error ≈ 7.96 m`
  - `Observation/base_lin_vel_x_raw ≈ 1.28 m/s`
  - `Observation/wheel_longitudinal_slip_abs_mean_raw ≈ 0.864`
  - `Observation/wheel_slip_angle_abs_mean_raw ≈ 0.803 rad`
  - `Observation/tilt_deg ≈ 19.89°`
  - `Reward/longitudinal_slip_gate ≈ 0.0099`
  - `Reward/lateral_slip_gate ≈ 0.145`
  - `Reward/force_gate ≈ 0.288`
  - `Loss/value ≈ 0.07`
- 训练中期 `iteration 148 ~ 157` 附近出现一次 critic `value loss` 瞬时尖峰，峰值到 `O(10^2 ~ 10^3)`，后续自行回落。
- 当前主问题已从“能否稳定跑起来”转为：
  - 纵滑仍高
  - 侧滑更差
  - 中后期车体倾斜偏大
  - 轮地法向载荷分布不理想
- 下一步优先方向应转到：
  - 轮速输出结构
  - 侧滑抑制
  - 轮地载荷分布
  而不是继续单纯压 PPO 或压球铰。

下一步：
- 基于本次诊断，优先设计一轮“轮速输出限幅/整形 + 载荷分布约束 + 侧滑抑制”定向实验。

## 2026-04-15

已完成：
- 按用户指定，把 Stage0 默认优化方向改为：
  - 先低纵向滑移
  - 低侧滑
  - 低跳动
  - 球铰速度更平滑
  - 再处理 critic 稳定性
- 将默认训练轮数改为：
  - `300`
- 调整 Stage0 PPO：
  - `save_interval = 100`
  - `actor init_std = 0.35`
  - `learning_rate = 2.0e-4`
  - `num_learning_epochs = 4`
  - `entropy_coef = 0.002`
  - `desired_kl = 0.008`
  - `value_loss_coef = 0.7`
  - `max_grad_norm = 0.7`
- 调整 Stage0 环境参数：
  - 收紧球铰动作范围
  - 球铰阻尼改为 `20.0`
  - 球铰速度上限改为 `0.8 rad/s`
  - 车轮速度上限改为 `12.0 rad/s`
  - `PhysX max_velocity_iteration_count = 1`
  - `enable_external_forces_every_iteration = True`
- 调整 reward：
  - 新增 `vertical_speed_gate`
  - 新增 `ball_joint_speed_gate`
  - `gated_progress` 当前变为：
    - `progress * roll_gate * speed_gate * force_gate * vertical_speed_gate * ball_joint_speed_gate * composite_gate`
- 调整 Stage0 观测 scale：
  - `base_ang_vel = 0.35`
  - `projected_gravity = 1.5`
  - `wheel_longitudinal_slip = 2.0`
  - `wheel_slip_angle = 1.5`
  - `wheel_normal_contact_force = 1.25`
  - `last_action = 1.5`
- 发现并修复一个 Stage0 配置装配问题：
  - `CompleteCarEnvCfg.__post_init__()` 会在末尾重建 `self.robot`
  - 因此 Stage0 在 `super().__post_init__()` 后再修改 actuator 相关 `control` 参数时，必须额外再次执行：
    - `self.robot = build_complete_car_robot_cfg(self.control, self.resets)`
  - 否则 PhysX articulation 实际仍使用 base cfg 的旧驱动参数
- 使用：
  - `python3 -m py_compile`
  完成相关 Python 文件静态编译检查，检查通过。
- 使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --max_iterations 1`
  完成两轮真实 GPU 冒烟验证。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 第一轮冒烟已确认 reward / PPO / Stage0 cfg 改动不会阻塞训练启动。
- 第二轮冒烟进一步确认 actuator 新参数真正下发到了 PhysX：
  - 球铰阻尼 `20.0`
  - 球铰速度上限 `0.8`
  - 车轮速度上限 `12.0`
- 最新通过验证的 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-26-28`
- 当前新的默认 Stage0 起点已经从“progress 优先”切到“稳定性优先”。
- 随后已启动一轮完整 `300` iteration 长跑用于中期趋势判断：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-29-47_stability_v1_iter300`
  - 实际在约 `iteration 85/300` 手动停止
- 当前长跑中期结论：
  - critic 稳定性已明显改善：
    - `Mean value loss` 约 `0.13 ~ 0.18`
  - 球铰速度已明显更平滑：
    - `ball_joint_vel_abs_mean_raw` 约 `0.43 ~ 0.45`
  - 竖向跳动约束有效：
    - `vertical_speed_gate` 约 `0.92 ~ 0.93`
  - 姿态与球铰限位不再是主要问题：
    - `bad_orientation_rate = 0`
    - `ball_joint_limit_rate = 0`
  - 但轮胎 traction 问题仍未解决：
    - `wheel_longitudinal_slip_abs_mean_raw` 约 `0.81 ~ 0.87`
    - `wheel_slip_angle_abs_mean_raw` 约 `0.64 ~ 0.75 rad`
    - 两个 slip gate 长期接近 `0`
- 下一步不应继续优先压球铰，而应转到：
  - 车轮速度目标映射
  - slip gate 结构
  - wheel action 平滑/增量约束

已完成：
- 先做了一轮“只压 wheel cap”的排除实验：
  - 临时将 Stage0 `wheel_joint_velocity_limit_sim` 改到 `8.5 rad/s`
  - 依据是 `speed_limit = 1.6 m/s` 与 `wheel_radius = 0.19 m` 对应角速度约 `8.4 rad/s`
- 使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --max_iterations 1`
  完成真实 GPU 冒烟，并确认 PhysX articulation 中 wheel velocity limit 已变成 `8.5`
- 再使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --max_iterations 40 --run_name slip_cap85_v1`
  做短训练验证
- 该实验结论：
  - 确实压低了 wheel speed
  - 但明显拖慢了前向推进
  - 且纵向滑移没有得到足够改善
  - 因此不保留为默认方案
- 随后回退该临时 wheel cap 改动，改做“slip gate 去饱和”：
  - `longitudinal_slip_gate` 从每轮乘积式 Gaussian 改为：
    - `exp(-mean(abs(longitudinal_slip)) / scale)`
  - `lateral_slip_gate` 从硬裁切余弦乘积改为：
    - `exp(-mean(abs(slip_angle)) / (pi / lateral_slip_gain))`
- 使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --max_iterations 1`
  完成新的真实 GPU 冒烟验证
- 使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --max_iterations 40 --run_name slip_gate_v1`
  完成完整短训练验证

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `8.5 rad/s` 的 wheel cap 方案被否决，不作为默认配置保留。
- `slip_gate_v1` 这轮验证 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-39-33_slip_gate_v1`
- `slip_gate_v1` 到 `iteration 39/40` 的关键信号：
  - `Observation/wheel_longitudinal_slip_abs_mean_raw ≈ 0.821`
  - `Observation/base_lin_vel_x_raw ≈ 1.17`
  - `Observation/wheel_slip_angle_abs_mean_raw ≈ 0.72 rad`
  - `Loss/value ≈ 0.15`
- 这说明：
  - slip gate 不再从一开始就塌到 `0`
  - 纵向滑移与前向推进的折中明显比 `slip_cap85_v1` 更好
  - critic 仍保持稳定
  - 当前剩下的主要 traction 问题已集中到侧滑角，而不是纵向 gate 完全失效

已完成：
- 对真实 Stage0 run
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_21-35-52`
  做了一轮完整离线诊断，重点检查了 `Observation/*_raw` 标量范围。
- 已导出并读取：
  - simulator log
  - Hydra 配置
  - `params/env.yaml`
  - `params/agent.yaml`
  - `tensorboard_export/latest_values.csv`
  - `tensorboard_export/summary.json`
  - 全部 `Observation/*_raw` scalar CSV

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 该 run 已明显学会存活与朝目标推进：
  - `mean_episode_length` 约升至 `941 / 959`
  - `goal_pos_error` 约降至 `8.75 m`
- 当前主要剩余问题是：
  - 高纵向滑移
  - 高侧滑角
  - 动作幅值偏大
  - 回合末球铰限位终止占比抬升
  - critic `value loss` 偏大
- 当前阶段判断更新为：
  - survival/progress 已建立
  - traction quality 与 critic stability 仍待解决

已完成：
- 修正 `RL_Training/scripts/play.py` 的 `--load_run` 路径解析逻辑。
- 当前 `play.py` 已支持以下 `--load_run` 写法：
  - 纯 run 目录名，如 `2026-04-15_21-35-52`
  - 带实验名前缀的相对路径，如 `complete_car_stage0/2026-04-15_21-35-52`
  - 直接指向 run 目录的绝对路径
- 原问题已定位为：
  - 旧脚本把 `--load_run complete_car_stage0/2026-04-15_21-35-52` 原样传给 Isaac Lab `get_checkpoint_path()`
  - 但当时 `log_root_path` 已经是 `.../complete_car_stage0`
  - 因此会错误拼出重复层级并报：
    - `No runs present in the directory ... match ...`
- 使用：
  - `python3 -m py_compile RL_Training/scripts/play.py`
  完成静态编译检查，检查通过。
- 使用以下真实回放命令验证：
  - `python scripts/play.py --task CompleteCar-Stage0 --load_run complete_car_stage0/2026-04-15_21-35-52 --num_envs 1 --headless`
- 验证结果：
  - 已确认回放流程不再卡在 checkpoint 路径解析
  - 当前新的实际阻塞点变为：
    - 运行机器当时无可用 CUDA 设备
    - 报错为：
      - `RuntimeError: No CUDA GPUs are available`

修改文件：
- `RL_Training/scripts/play.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `play.py` 的回放路径解析问题已修复。
- 若后续继续回放失败，应优先检查当前机器 GPU / driver / device 配置，而不是再怀疑 run 目录不存在。

已完成：
- 核对当前局部高程 patch 的真实实现入口，并删除一段无用的旧高度扫描代码。
- 当前 active critic 高程 patch 真实写在：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - 函数：
    - `_compute_critic_height_patch()`
- 删除：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
  中未被主线使用的：
  - `get_height_features()`
- 同时删除 `env._get_observations()` 中对该函数的无效调用。
- 删除原因：
  - 当前 Stage0 / Stage1 / Stage2 都没有启用 `height_scanner`
  - 该函数返回值没有进入 actor / critic 观测
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前局部高程 patch 的 active 主线只保留 `env._compute_critic_height_patch()`。
- 旧的 `height_scanner.get_height_features()` 路径已确认是死代码并已移除。

已完成：
- 将目标命令重采样改为“一个 episode 只保留一个目标”。
- 修改 `base/complete_car_cfg.py`：
  - `commands.resampling_time` 当前会在 env cfg 装配阶段自动对齐到 `episode_length_s`
- 修改 `base/env.py`：
  - 预物理步中的 timer 重采样逻辑已加门控
  - 仅当 `resampling_time < episode_length_s` 时才允许回合内中途重采样
  - 当前默认行为因此变为：
    - reset 时采样一次目标
    - 一个回合内不再切换目标
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 本次 `goaldist12_v1` 早期训练结论：
  - `Tracking/goal_pos_error: 12.02 -> 10.58`
  - `Reward/progress ≈ 0.56`
  - `Reward/gated_progress ≈ 0.008`
  - `longitudinal_slip_gate ≈ 0.011`
  - `lateral_slip_gate ≈ 0.192`
  - `wheel_longitudinal_slip_abs_mean_raw ≈ 0.852`
  - `wheel_slip_angle_abs_mean_raw ≈ 0.692`
  - `tilt_deg ≈ 3.00°`
- 当前判断：
  - 目标距离恢复到 `12m` 后，策略确实重新追求更强 progress
  - 但有效推进几乎仍被 slip gate 吃掉
  - 因此前期已经足以判断：该设置会重新把训练推向“堆 progress、牺牲 traction 质量”的方向
- 本次 `2026-04-16_13-20-05` run 的主要结论：
  - `Train/mean_episode_length = 959 / 959`
  - `Termination/time_out_rate = 1.0`
  - `tilt_deg ≈ 6.6°`
  - `wheel_normal_contact_force_sum_raw ≈ 0.94`
  - `wheel_longitudinal_slip_abs_mean_raw ≈ 0.85`
  - `wheel_slip_angle_abs_mean_raw ≈ 0.70 rad`
  - `Reward/progress` 末段接近 `0`，近 10 轮均值为负
  - `Reward/target_bonus` 成为总回报主导来源
  - `Loss/value` 在后段持续维持高位，末段约 `21`，近 10 轮均值约 `24`
- 当前判断：
  - 新任务定义显著降低了姿态和失载问题
  - 但当前策略更像“稳定存活 + 偶尔吃到 target bonus”
  - 还没有形成持续、高质量的目标推进
- 当前 goal-conditioned 主线已不再在一个 episode 内多次更换目标。
- 后续课程学习可以直接按“单回合对应单目标”的口径设计成功 / 失败判据。

已完成：
- 将轮地法向接触力的 strict 版本补充到真实可用状态，并完成默认 `64` 环境训练启动验证。
- 修正 `sensors/sensor_cfg.py`：
  - wheel-ground filter 不再指向 ground 根 prim 或通配子树
  - 当前运行时先递归解析 `ground_prim_path` 下的真实碰撞 prim
  - 平地对应 `Plane`，generator terrain 对应 `Mesh`
- 保留逐接触点法向聚合实现：
  - `sum(normal_force_scalar * contact_normal_vector)`
- 使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --max_iterations 1`
  完成真实 GPU 启动验证。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 strict 版本轮地法向力实现已可在默认 `64` 环境下正常启动训练。
- 本轮验证 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_21-10-27`
- 当前 `Observation/wheel_normal_contact_force_abs_mean_raw` 已恢复为非零，说明 ground filter 与逐接触点法向聚合链路生效。

已完成：
- 将当前轮地法向接触力实现进一步改为“基于真实接触点法向的严格版本”。
- 修改 `sensors/sensor_cfg.py`：
  - wheel-ground contact view 不再直接调用 `get_net_contact_forces(dt)`
  - 当前改为对 `get_contact_data(dt)` 返回的逐接触点法向标量与接触法向做聚合
  - 每个轮子的世界系法向合力向量按：
    - `sum(normal_force_scalar * contact_normal_vector)`
    重建
- 修改 `mdp/observations.py`：
  - 保持观测接口不变
  - 将“法向接触力”语义更新为上述聚合后法向合力向量的模长，并继续按整车重量归一化
- 同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前轮地法向接触力不再是“直接读取法向合力接口”的实现口径，而是显式基于真实接触点法向重建。
- 当前观测与奖励仍沿用同一 6 维轮载输入接口，但其底层物理定义已经收口为逐接触点法向聚合版本。

已完成：
- 删除当前 critic 显式地形高度 patch 的“三车独立 patch 拼接”方案，不再保留可选分支。
- `terrain/terrain_cfg.py` 已移除：
  - `terrain.height_patch_scheme`
  - 三 patch 总维度计算逻辑
- `base/env.py` 已恢复为：
  - 仅以中车参考系生成单份 patch
  - 仅使用中车 yaw 做 patch 旋转
  - 仅返回单份中车相对高度 patch 给 critic
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 critic 显式高度 patch 已恢复为只保留原始中车单 patch 方案。
- 之后不再使用前 / 中 / 后三 patch 拼接方案。

已完成：
- 为当前 critic 显式地形高度 patch 新增一套可选的三车独立方案。
- 保留原有：
  - `terrain.height_patch_scheme = "body_single"`
- 新增：
  - `terrain.height_patch_scheme = "three_body_separate"`
- 在新方案下：
  - 分别以前车 / 中车 / 后车的质心为 patch 原点
  - 三份 patch 分别跟随各自车体 yaw 旋转
  - 三份 patch 按 `head -> body -> tail` 顺序展平后拼接进 critic 观测
  - 每份 patch 的高度值相对各自车体质心高度计算
- 已同步让：
  - `terrain.get_num_height_points()`
  按当前方案自动返回单 patch 或三 patch 拼接后的总维度
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 critic 显式高度 patch 已支持“中车单 patch”和“前中后三 patch 拼接”两套方案。
- 默认行为仍保持原方案不变；如需启用新方案，只需在配置里切到：
  - `terrain.height_patch_scheme = "three_body_separate"`

已完成：
- 对当前三节关节小车 direct workflow 做了一轮 goal-conditioned 主线重构。
- 当前命令空间已从速度命令改为目标位姿命令：
  - env 内存储为全局目标位姿：
    - `[x_t, y_t, psi_target]`
  - 目标采样规则改为：
    - 固定距离 `12 m`
    - 相对起始航向偏角 `phi ∈ [-18.43°, 18.43°]`
    - 使用 `phi = s * phi_max * sqrt(u)` 的边缘强化二次采样
    - 目标朝向附加偏置 `delta ∈ [-9.215°, 9.215°]`
- 当前观测中的命令项已改为车体系下的相对目标：
  - `[x_rel, y_rel, psi_rel]`
- 当前动作空间已从仅球铰控制改为：
  - `6` 个球铰姿态目标
  - `6` 个车轮速度目标
  - 共 `12` 维
- wheel allocator 已从当前 env 执行链路中移除，车轮速度目标改为由 policy 直接输出并映射到速度上下界。
- 为保持 env 可运行，本轮对 reward/curriculum/metrics 做了最小兼容改动，但完整 goal-conditioned reward 设计尚未展开。
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/assets/robot_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/curriculum.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 direct workflow 的命令与动作接口已经切换到用户指定的 goal-conditioned 口径。
- 当前 Stage0 默认关键维度已变为：
  - 动作 `12`
  - Actor 观测 `52`
  - Critic 观测 `52`

已完成：
- 新增 Zotero 本地补挂脚本：
  - `scripts/literature/attach_local_pdfs_to_zotero_collection.py`
- 针对 Zotero 集合：
  - `核心参考-RL、Sim-to-Real`
  执行了一次本地 PDF 回填
- 因当前 `zotero-mcp` 的 collection 接口受 `Local API is not enabled` 限制，实际采用：
  - 关闭 `zotero-bin`
  - 备份 `zotero.sqlite`
  - 直接写入 Zotero 本地 SQLite 与 `storage/` 附件目录
  - 重开 Zotero
- 本轮从：
  - `docs/literature/`
  成功补挂 `10` 个原本缺 PDF 的条目
- 已核对补挂成功的 parent key：
  - `QFLNKZ2Q`
  - `V7VESQJM`
  - `KXTHNV77`
  - `3NRQAKKS`
  - `LMTJ8X83`
  - `ZNSS2JA8`
  - `5M2SGTER`
  - `XH4XPRC6`
  - `WXIK6J7M`
  - `2TICENYY`

修改文件：
- `scripts/literature/attach_local_pdfs_to_zotero_collection.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `核心参考-RL、Sim-to-Real` 集合里，凡是 `docs/literature/` 已有对应 PDF 且原条目缺 PDF 的项目，本轮已完成自动补挂。
- 已在真实 Zotero 库修改前生成数据库备份：
  - `/home/lbz/Zotero/zotero.sqlite.backup_2026-04-15_00-27-59`

已完成：
- 在 Zotero 桌面端已打开、并选中目标集合的前提下，使用 Google Scholar BibTeX + 本地 Zotero Connector 流程，将上轮筛出的 10 篇核心候选论文导入 Zotero 集合：
  - `核心参考-RL、Sim-to-Real`
- 本轮导入的 10 篇文献包括：
  - `Hybrid Learning for Rough Terrain Navigation of Actively Articulated Wheeled Vehicles`
  - `Control of rough terrain vehicles using deep reinforcement learning`
  - `Simultaneous control of terrain adaptation and wheel speed allocation for a planetary rover with an active suspension system`
  - `Control of robotic vehicles with actively articulated suspensions in rough terrain`
  - `Design and field testing of a rover with an actively articulated suspension system in a Mars analog terrain`
  - `Actively articulated suspension for a wheel-on-leg rover operating on a martian analog surface`
  - `Deep reinforcement learning for safe local planning of a ground vehicle in unknown rough terrain`
  - `A sim-to-real pipeline for deep reinforcement learning for autonomous robot navigation in cluttered rough terrain`
  - `Static force distribution and orientation control for a rover with an actively articulated suspension system`
  - `Predict the rover mobility over soft terrain using articulated wheeled bevameter`
- 导入结果：
  - 10 篇元数据全部导入成功
  - 3 篇 PDF 自动附加成功
  - 5 篇 PDF 因站点重定向或 `403` 被拒绝，未自动附加
  - 其余 2 篇本轮未附带可直接抓取的 PDF 链接
- 自动附加成功的 PDF 对应：
  - `Deep reinforcement learning for safe local planning of a ground vehicle in unknown rough terrain`
  - `A sim-to-real pipeline for deep reinforcement learning for autonomous robot navigation in cluttered rough terrain`
  - `Predict the rover mobility over soft terrain using articulated wheeled bevameter`
- 已同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前课题第一轮核心英文参考文献池已经落入 Zotero 主集合，后续继续做 cited-by 扩展、批注、读书笔记时可以直接从该集合接续。
- 若后续需要完整 PDF，仍需针对未自动附加的 5 篇做单篇补抓。

已完成：
- 重新检查 `USD/complete_car.usd` 的 6 个轮子刚体根节点，确认用户已手动补入 `Contact Report API`。
- 修改 `sensors/sensor_cfg.py`：
  - 为 runtime 手动创建的传感器补上 `{ENV_REGEX_NS}` 显式解析
  - 初始尝试将 wheel contact sensor 的 prim 路径修正为：
    - `{ENV_REGEX_NS}/Robot/complete_car_alternative/(body_car_wheel_left|...|tail_car_wheel_right)`
  - 进一步确认 Isaac Lab `ContactSensor` 在默认 `64` 环境 direct workflow 启动场景下仍会报：
    - `Failed to initialize contact reporter for specified bodies`
  - 最终改为运行时直接创建 6 个 PhysX `rigid_contact_view`，不再依赖 `ContactSensor`
- 修改 `base/env.py`：
  - 将 `_total_vehicle_weight` 显式放到 `self.device`
  - 修复轮地法向接触力归一化时的 CPU / CUDA 设备不一致问题
- 使用以下命令完成真实 GPU 最小训练验证：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless`
- 本轮验证通过并进入持续训练循环的 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_20-57-31`

修改文件：
- `USD/complete_car.usd`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 wheel-ground contact force 主线已经切换为 PhysX 直接 contact view，不再依赖 Isaac Lab `ContactSensor`。
- 当前默认训练命令已在真实 GPU 环境下成功进入持续训练循环。

## 2026-04-13

已完成：
- 按用户要求把当前 Stage0 命令主线从 4 维收口为单一 2 维模式：
  - `lin_vel_x`
  - `ang_vel_yaw`
- 删除 active direct workflow 中的：
  - `lin_vel_y`
  - `heading`
  命令配置入口与对应运行时使用点。
- 修改 `base/complete_car_cfg.py`：
  - `CommandCfg.num_commands` 由 `4` 改为 `2`
  - 删除 `CommandRangesCfg` 中的：
    - `lin_vel_y`
    - `heading`
  - 删除奖励配置中的：
    - `tracking_heading`
    - `tracking_heading_std`
- 修改 `mdp/commands.py`：
  - 命令重采样改为只采样 `Vx / Wz`
  - 当前将二维命令先扩成虚拟三维向量 `[Vx, 0, Wz]`，左乘固定变换矩阵后，再收口回 `[Vx', Wz']`
- 修改 `kinematics/wheel_speed_allocator.py`：
  - allocator 的平面命令入口统一改为 2 维 `[Vx, Wz]`
- 修改 `mdp/rewards.py`：
  - 删除 `tracking_heading`
  - `tracking_lin_vel` 改为只跟踪 `Vx`
- 修改 `base/env.py`：
  - episode 日志移除 `command_heading`
  - `command_ang_vel_yaw` 的索引改为新的二维命令索引
- 修改 `utils/validate_wheel_speed_allocator.py`：
  - 数值验证入口改为使用二维命令
- 更新文档：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `AGENTS.md`
- 在 `AGENTS.md` 中新增维护规则：
  - 之后只要 Stage0 RL 环境设计或训练参数配置发生实质变化，必须同步更新 `docs/RL阶段训练参数一览表.md`
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `AGENTS.md`

产出/结论：
- 当前 Stage0 active command 语义已经正式收口为二维：
  - `Vx`
  - `Wz`
- 当前 Stage0 单帧 actor/critic 观测维度由 `47` 变为 `45`
- 当前 reward 集合已进一步收口为 5 项，不再包含 `tracking_heading`

已完成：
- 对 `docs/RL阶段训练参数一览表.md` 做了一轮数学公式统一整理。
- 当前该文档不再混用：
  - `\[\]`
  - `\(\)`
  两套 LaTeX 分隔符。
- 现统一为：
  - 显示公式使用 `$$ ... $$`
  - 行内公式使用 `$ ... $`
- 已覆盖的部分包括：
  - reset 公式
  - command 变换矩阵
  - observation 拼接公式
  - action 映射公式
  - reward 公式
  - termination 公式
  - PPO / GAE 公式
- 使用 `rg -n '\\\\\\[|\\\\\\]|\\\\\\(|\\\\\\)' docs/RL阶段训练参数一览表.md` 做残留检查，已无旧公式分隔符残留。

修改文件：
- `docs/RL阶段训练参数一览表.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 参数总表的数学公式标记已经统一成更适合 Markdown 渲染的写法。
- 后续继续编辑这份文档时，应保持同一套 `$$ / $` 约定。

已完成：
- 按用户要求删除当前 direct workflow 中的：
  - `terrain.flat_only_reset`
- 修改代码位置：
  - `terrain/terrain_cfg.py`
  - `mdp/curriculum.py`
  - `baseline/complete_car_stage0_cfg.py`
  - `baseline/complete_car_stage1_cfg.py`
  - `environment_adaptive/complete_car_stage2_cfg.py`
- 当前 generator 模式下的初始 terrain type 分配不再通过 `flat_only_reset` 固定到默认地形列，而是统一走 `mdp/curriculum.py` 中的按列分布初始化逻辑。
- 同时修正 `docs/RL阶段训练参数一览表.md` 中两处会导致公式/符号渲染不正确的问题：
  - root reset 位置公式中缺失的两个 `+`
  - command 变换矩阵中的 `\times 10^{-5}` 写法
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/curriculum.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/environment_adaptive/complete_car_stage2_cfg.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/curriculum.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/environment_adaptive/complete_car_stage2_cfg.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active direct workflow 已不再保留 `flat_only_reset` 这个 reset/terrain 特殊开关。
- Stage0 参数总表中的相关数学公式已修正为可正常渲染的写法。

已完成：
- 在 `docs/` 下新增：
  - `RL阶段训练参数一览表.md`
- 该文档当前按 `CompleteCar-Stage0` 的实际代码配置整理了一份完整训练参数总表，内容覆盖：
  - 仿真与 scene
  - 地形
  - 机器人与 actuator
  - reset
  - command
  - observation
  - action
  - reward
  - termination
  - randomization
  - curriculum
  - PPO 超参数
- 文档顺序按 RL 训练流程组织，并补充了当前代码口径下的：
  - Actor / Critic / Action 维度
  - command 变换矩阵
  - 观测拼接公式
  - 逐轴动作映射公式
  - 奖励公式
  - 终止公式
  - GAE / PPO 核心公式
- 同步在 `docs/current_status.md` 中登记了这份 Stage0 参数总表文档。

修改文件：
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 已经有一份可以直接用于查参数、写实验记录和论文任务定义回填的集中式文档。
- 后续只要 Stage0 的 reward、observation、action、命令或 PPO 配置有实质变化，这份文档也需要同步更新。

已完成：
- 按用户要求从当前 direct workflow 奖励主线中删除以下 4 项：
  - `lin_vel_z`
  - `ang_vel_xy`
  - `ball_joint_deviation`
  - `ball_joint_swing`
- 修改 `mdp/rewards.py`：
  - 从 `REWARD_TERM_NAMES` 中移除上述 4 项
  - 从 `compute_reward_terms(...)` 中删除对应张量计算与加权拼接
- 修改 `base/complete_car_cfg.py`：
  - 从 `RewardScalesCfg` 中删除上述 4 个 scale 参数
  - 从 `RewardCfg` 中删除已失效的：
    - `ball_joint_target`
- 保留的当前奖励集合为：
  - `tracking_lin_vel`
  - `tracking_ang_vel`
  - `tracking_heading`
  - `orientation`
  - `action_rate`
  - `termination`
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 direct workflow 奖励集合已经显式简化，不再包含垂向速度、横滚/俯仰角速度和球铰正则项。
- 后续奖励调参与日志分析应以新的 6 项 reward 集合为准。

已完成：
- 按用户要求把 terrain curriculum 从 terrain runtime 中拆出，单独建立：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/curriculum.py`
- 在 `base/complete_car_cfg.py` 中新增：
  - `CurriculumCfg`
  用于统一保存课程学习参数：
  - `enabled`
  - `max_init_terrain_level`
  - `default_terrain_name`
  - `move_up_distance_ratio`
  - `move_down_command_ratio`
- 在 `terrain/terrain_cfg.py` 中移除了原先混在 terrain runtime 配置里的 curriculum 参数，保留 terrain 自身参数与 spawn offset 参数。
- 修改 `terrain/terrain_runtime.py`：
  - 不再内置初始 terrain level/type 采样逻辑
  - 不再内置 `update_curriculum(...)`
  - 当前只负责 terrain 数据、env origin 同步和 spawn offset
- 修改 `base/env.py`：
  - 在 `_setup_scene()` 中显式调用 `mdp/curriculum.py` 完成 terrain curriculum 初始化
  - 在 `_reset_idx()` 中显式调用 `mdp/curriculum.py` 更新 terrain curriculum
- 修改各 stage 配置：
  - `Stage0` 改为 `self.curriculum.enabled = False`
  - `Stage1` 改为 `self.curriculum.enabled = True`
  - `Stage2` 改为 `self.curriculum.enabled = True`
- 本轮额外发现并修正一个旧的运行时问题：
  - `Stage1` 中的 `default_terrain_name = "mix"` 并不是 `terrain_builder.py` 中的合法地形名
  - 当前已改为 `"flat"`
- 使用：
  - `python3 -m py_compile $(find RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car -name '*.py' | sort)`
  完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/curriculum.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/__init__.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_runtime.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/environment_adaptive/complete_car_stage2_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 terrain curriculum 的参数入口和执行入口已经分离：
  - 参数入口：`CurriculumCfg`
  - 执行入口：`mdp/curriculum.py`
- 当前 `terrain_runtime.py` 已经从“terrain + curriculum 混合文件”收口为纯 terrain runtime 文件。
- 当前 stage 覆写 curriculum 时应统一改：
  - `self.curriculum.*`
  而不是再改：
  - `self.terrain.curriculum`

下一步：
- 在真实 Isaac Lab 环境中检查 curriculum 重构后：
  - `_setup_scene()` 是否能正常初始化 terrain levels / terrain types
  - `_reset_idx()` 是否能正常更新 terrain level
  - Stage1 / Stage2 的 terrain origin 是否随课程学习正确变化

已完成：
- 对最近动作映射改造做了一轮残留检查，发现 `actions.py` 和 `env.py` 已经改成依赖：
  - `ball_joint_action_lower_limits`
  - `ball_joint_action_upper_limits`
  但 `ControlCfg` 中一度残留旧的：
  - `ball_joint_action_scale`
  且缺失新的逐轴动作范围字段。
- 已在 `base/complete_car_cfg.py` 中删除旧的统一动作缩放字段，并补齐逐轴动作上下界配置，使运行时动作映射与当前 `actions.py` 的实现一致。
- 当前动作上下界与用户最新修改后的终止上下界保持一致：
  - `yaw in [-0.7, 0.7]`
  - `pitch in [-1.6, 0.5]`
  - `roll in [-0.5, 0.5]`
- 同步更新 `docs/current_status.md`，避免默认设计说明仍停留在旧的 pitch 范围。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前动作映射主线不再残留旧的统一 `ball_joint_action_scale` 配置。
- 当前 `ControlCfg`、`actions.py`、`env.py`、`terminations.py` 四处对球铰动作/范围的口径已经重新对齐。

已完成：
- 按用户要求取消“统一 `ball_joint_action_scale + 统一 clip_actions`”的旧动作映射方式。
- 在 `base/complete_car_cfg.py` 的 `ControlCfg` 中新增逐轴动作上下界：
  - `ball_joint_action_lower_limits`
  - `ball_joint_action_upper_limits`
  当前顺序按 `z, y, x, z, y, x` 对应：
  - `yaw in [-0.7, 0.7]`
  - `pitch in [-1.57, 0.4]`
  - `roll in [-0.5, 0.5]`
- 在 `mdp/actions.py` 中重写 `apply_ball_joint_targets(...)`：
  - policy 动作先按标准化区间 `[-1, 1]` 解释
  - 采用相对于默认关节角的非对称映射
  - 保证：
    - `action = 0` 对应默认位姿
    - `action = 1` 对应上界
    - `action = -1` 对应下界
- 在 `base/env.py` 中移除对统一 `ball_joint_action_scale` 的调用，改为向 `actions.py` 传入逐轴上下界。
- 在 `agents/rsl_rl_ppo_cfg.py` 中把 PPO wrapper 的 `clip_actions` 同步改为 `1.0`，与当前标准化动作语义一致。
- 使用 `python3 -m py_compile` 对相关文件完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前动作映射已经和逐轴球铰范围联动起来，不再依赖统一物理 scale。
- 当前动作语义已经从“统一增量控制”变为“按每个关节独立范围归一化控制”。
- 其中 pitch 的非对称范围现在能够被正确表达，且 `action=0` 不会把目标直接推到区间中心。

下一步：
- 在真实 Isaac Lab 环境中验证 6 个球铰目标是否都严格落在各自上下界内
- 观察策略初期是否更容易学出稳定的 pitch 控制

已完成：
- 按用户要求把球铰终止条件从统一阈值改为按 `yaw / pitch / roll` 分别判断。
- 在 `base/complete_car_cfg.py` 的 `TerminationCfg` 中删除了统一的：
  - `soft_ball_joint_pos_limit`
  并改为显式上下界：
  - `ball_joint_pos_lower_limits`
  - `ball_joint_pos_upper_limits`
- 当前 6 维球铰顺序按：
  - `z, y, x, z, y, x`
  解释为：
  - `yaw, pitch, roll, yaw, pitch, roll`
- 当前启用的关节范围为：
  - `yaw in [-0.7, 0.7]`
  - `pitch in [-1.57, 0.4]`
  - `roll in [-0.5, 0.5]`
  前后两组球铰目前使用同一套范围。
- 在 `mdp/terminations.py` 中把统一的绝对值比较改为逐维上下界比较，并增加了维度不匹配时报错的检查。
- 使用 `python3 -m py_compile` 对相关文件完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前终止条件中的球铰角约束已经不再是一概而论的单一标量阈值。
- 当前任务主线已经开始按轴使用非对称、分维度的球铰角终止范围。

下一步：
- 把 `clip_actions` / `ball_joint_action_scale` 的设计也和这套逐轴角度范围联动起来，避免动作目标轻易推到 pitch 上界附近

已完成：
- 按用户要求为动作随机化增加统一总开关，并保持现阶段默认关闭。
- 在 `base/complete_car_cfg.py` 的 `RandomizationCfg` 中新增：
  - `enable_action_randomization: bool = False`
- 修改 `_build_action_noise_model_cfg()`：
  - 当总开关为 `False` 时直接返回 `None`
  - 因此当前不会启用 action noise / action bias
- 修改 `mdp/randomization.py` 中 `sample_motor_strength(...)`：
  - 只有在：
    - `enable_action_randomization == True`
    - 且 `randomize_motor_strength == True`
    时才会采样随机 `motor_strength`
  - 否则始终返回全 1
- 使用 `python3 -m py_compile` 对相关文件完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/randomization.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前动作随机化已经有统一总开关。
- 当前默认配置下：
  - `enable_action_randomization = False`
  - 不使用动作噪声
  - 不使用动作 bias
  - 不使用 motor strength 动作随机化

下一步：
- 若后续需要做域随机化实验，再在对应 stage cfg 中显式打开 `enable_action_randomization`

已完成：
- 对用户完成的 MGDP 风格显式地形高度 patch 全部 6 步实现做了一轮全链路静态检查，覆盖：
  - `terrain/terrain_cfg.py`
  - `terrain/terrain_runtime.py`
  - `base/env.py`
  - `mdp/observations.py`
  - `base/complete_car_cfg.py`
  - `utils/io_descriptors.py`
  - `utils/math_utils.py`
  - `baseline/complete_car_stage1_cfg.py`
  - `environment_adaptive/complete_car_stage2_cfg.py`
  - `agents/rsl_rl_ppo_cfg.py`
- 发现并修正一个会导致“功能虽然写完但默认不生效”的配置问题：
  - `CompleteCarStage1EnvCfg` 中仍写着 `self.terrain.measure_heights = False`
  - 已改为 `True`
- 结合当前 patch 几何参数重新核对默认网格尺寸：
  - `measured_points_x = 28`
  - `measured_points_y = 7`
  - `num_height_points = 196`
- 因此在当前代码口径下：
  - 单帧 `actor` 观测维度为 `47`
  - 单帧 `critic` 观测维度在 Stage1 中为 `243`
  - Stage0 / Stage2 当前仍为 `47`
- 使用 `python3 -m py_compile` 对上述相关文件完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 6 步主线代码在静态层面已打通。
- 当前真正启用显式高度 patch 的阶段是 `Stage1`。
- 当前 Stage1 观测维度为：
  - `actor = 47`
  - `critic = 243`

下一步：
- 在真实 Isaac Lab 环境中验证 `critic` 张量末尾 196 维是否随 terrain 起伏变化
- 检查 PPO 运行时是否正确接收 `actor/critic` 两组不同维度的观测

已完成：
- 检查并修复 MGDP 风格显式地形高度 patch 迁移中的第三步实现，重点核对：
  - `base/env.py`
  - `mdp/observations.py`
  - `base/complete_car_cfg.py`
- 修正了 `env.py` 中 `_compute_critic_height_patch()` 被错误粘贴到 `_reset_idx()` 内部且语法损坏的问题；当前该函数已恢复为环境类的正式成员方法。
- 在 `env.py` 中补齐了第三步完整链路：
  - 从 `terrain_cfg.py` 生成的局部 patch 点展开到所有环境
  - 只按中车 `yaw` 做旋转
  - 加上中车世界位置得到 patch 世界坐标
  - 调用 `terrain_runtime.sample_heights_world_xy(...)` 查询地形高度
  - 构造相对高度 `base_z - terrain_height`
- 在 `mdp/observations.py` 中新增 `compute_critic_observation(...)`，使当前 critic 观测能在 actor 基础上追加显式高度 patch。
- 在 `base/complete_car_cfg.py` 中把 `observation_space` 恢复为：
  - `{"actor": ..., "critic": ...}`
  以匹配当前 env 与 PPO 的双观测组接口，并使 critic 维度在启用 `measure_heights` 时自动增加 `num_height_points`。
- 使用 `python3 -m py_compile` 对上述 3 个文件完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前第三步“中车 yaw 对齐 patch 世界点生成 + 相对高度构造”已经在 env 主线中落地。
- 当前 critic 观测链路已经具备拼接显式高度 patch 的能力，actor 仍保持原 47 维主观测不变。
- 当前 Stage1 配置仍把 `terrain.measure_heights` 设为 `False`，因此运行时默认还不会真正启用这张 critic 高度图；这属于启用配置问题，不是第三步实现错误。

下一步：
- 在阶段配置中显式打开 `terrain.measure_heights`
- 验证 `critic` 维度是否大于 `actor`
- 在真实 Isaac Lab 环境里检查相对高度 patch 数值是否符合 terrain 起伏

已完成：
- 检查用户为 MGDP 风格显式地形高度 patch 所做的前两步修改，重点核对：
  - `terrain/terrain_cfg.py`
  - `terrain/terrain_runtime.py`
- 确认当前迁移主线已经从旧的 `RayCaster height_scanner` 思路切到：
  - patch 几何参数配置
  - 局部采样点生成
  - `height_field_raw` 运行时缓存
  - 世界坐标高度查询接口
  这条 MGDP 风格链路。
- 直接修正了两处会破坏后续链路的简单错误：
  - `terrain_cfg.py` 中 `num_height_points` 对 `measured_points_y` 的拼写错误
  - `terrain_runtime.py` 中在 `initialize_after_scene_clone()` 错误清空 `_height_field_raw` 的问题
- 同步整理了 `terrain_cfg.py` 中 patch 几何辅助函数与局部 patch 点生成函数的格式与注释，使其更适合后续教学和继续扩展。
- 使用 `python3 -m py_compile` 对上述两个 terrain 文件完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_runtime.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前方案一 patch 的几何定义和局部网格生成接口已经落在 `terrain_cfg.py`。
- 当前训练地形的大高度表已经能在 `terrain_runtime.py` 中保留并提供世界坐标查询入口，不再依赖旧的 `height_scanner` 作为主路线。
- 当前仍未把显式高度 patch 真正拼入 `critic` 观测，下一步应进入 `env.py`。

下一步：
- 在 `env.py` 中实现：
  - 中车 yaw 对齐的 patch 世界点生成
  - 调用 `sample_heights_world_xy(...)`
  - 构造相对高度 patch
  - 只先拼入 `critic`

已完成：
- 检查并修复完整车 RL 主线中 Actor/Critic 观测分组修改后的连锁问题，重点核对了：
  - `base/complete_car_cfg.py`
  - `base/env.py`
  - `mdp/observations.py`
  - `utils/io_descriptors.py`
  - `utils/math_utils.py`
  - `agents/rsl_rl_ppo_cfg.py`
- 修正了 `mdp/observations.py` 中多处因手动改名产生的变量引用错误，包括：
  - `robto`
  - `front_body_id / rear_body_id`
  - `whell_joint_ids`
  - `command`
  这些不一致命名已统一到可运行版本。
- 在 `base/env.py` 中补齐：
  - `head_car_chassis`
  - `tail_car_chassis`
  的 `find_bodies()` 查询，并把环境输出从旧的单组：
  - `policy`
  改为显式双组：
  - `actor`
  - `critic`
- 在 `agents/rsl_rl_ppo_cfg.py` 中将 PPO 输入组映射从：
  - `{"actor": ["policy"], "critic": ["policy"]}`
  改为：
  - `{"actor": ["actor"], "critic": ["critic"]}`
- 在配置和维度计算侧补齐了新增观测项对应的：
  - scale
  - noise
  - descriptor
  - observation_space
  使 actor/critic 单帧观测维度统一为 `47`。
- 使用 `python3 -m py_compile` 对修改后的关键文件以及整个：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/`
  Python 树完成静态编译检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前观测主线已不再依赖旧的单组 `policy` 观测，而是显式区分：
  - `actor`
  - `critic`
- 当前 `critic` 仍与 `actor` 保持完全一致，后续若做 privileged critic，可直接在现有 `critic` 组上扩展。
- Stage2 传感器运行时链路仍保留，但当前默认不再拼入 actor/critic 主观测主干。

下一步：
- 在真实 Isaac Lab 环境中优先做一轮 `CompleteCar-Stage0` 冒烟，确认：
  - actor/critic 双组观测能被 env wrapper 与 PPO 正常接收
  - 观测维度与运行时实际返回张量一致

## 2026-04-12

已完成：
- 按用户要求，为完整车 RL 主线中的 `Vx / Vy / Wz` 命令语义加入固定左乘变换矩阵：
  - `[[1, 0, -0.00614478162640497], [0, 1, -1.07379532542362e-5], [0, 0, 1]]`
- 在 `wheel_speed_allocator.py` 中保留 NumPy 版命令变换 helper：
  - `transform_planar_command_numpy`
- 按用户进一步要求，将 `transform_planar_command_torch` 的实现移动到 `mdp/commands.py` 内部，使 Torch 命令语义逻辑直接放在命令模块中。
- 在 `mdp/commands.py` 的命令重采样出口统一对 `commands[:, :3]` 应用该变换，使 env 内保存的命令直接变成变换后的语义。
- 同步更新 `utils/validate_wheel_speed_allocator.py`，使独立验证脚本与训练主线使用同一命令变换逻辑，并增加对纯 `yaw` 命令变换结果的数值断言。
- 使用 `python3 -m py_compile` 对本轮修改的 Python 文件完成静态语法检查，检查通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `commands` 张量在 env 内已经不是原始采样值，而是对 `Vx,Vy,Wz` 左乘固定矩阵后的结果；因此观测、奖励、terrain curriculum、轮速分配和日志现在都共享同一套命令语义。
- 当前命令变换逻辑按使用层拆分为：
  - `mdp/commands.py` 中的 Torch 实现，供 env 主线调用
  - `wheel_speed_allocator.py` 中的 NumPy 实现，供独立验证脚本调用
- 当前终端环境中的 `python3` 缺少 `numpy`，因此本轮无法在这里直接跑通 `validate_wheel_speed_allocator.py`，但静态编译已通过。

下一步：
- 在带 `numpy` 的 Python 环境中运行：
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py`
- 在真实 Isaac Lab 环境中继续做 `CompleteCar-Stage0` 冒烟，确认训练主线下该命令变换不会引入新的运行态问题。

已完成：
- 修改毕业论文 `chapter_03` 中速度雅可比矩阵模型推导，将前后侧模块固定偏置从 `${}^{1}\mathbf b_1 / {}^{3}\mathbf b_3` 改为由单一标量 `b` 定义的镜像偏置 `${}^{1}\mathbf b=[-b,0,0]^T`、`${}^{3}\mathbf b=[b,0,0]^T`。
- 按用户更正，明确偏置向量仅保留 `x` 分量，且 `y=z=0`。
- 同步修正文中几何定义、位置关系、速度传播、雅可比展开、章节小结与英文 `Summary` 的相关表述。
- 进一步利用 `\mathbf e_x^T\mathbf S({}^{i}\mathbf b)=0` 对显式轮速行雅可比中的相关项做了化简。
- 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 完成论文主文档编译验证。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `chapter03.tex` 内与该推导相关的公式已统一到单一参数 `b` 的对称偏置建模，不再保留 `b_1 / b_3` 的旧记号，也不再保留 `b_z` 或非零 `y/z` 分量。
- LaTeX 编译通过，输出文件为 `毕业论文/毕业论文模板/LaTeX/main.pdf`。
- 当前仍有未定义引用与排版类 warning，但与本次公式修改无直接关系。

下一步：
- 如需继续收口论文第三章，可进一步统一图注、变量说明表和前后章节中对偏置向量的文字描述。

## 2026-04-11

已完成：
- 清理并重写 `docs/RL环境设计.md` 中的 LaTeX 公式与符号渲染格式。
- 删除文档内残留的私有区引用乱码字符：
  - `filecite...`
- 将原来的：
  - `\\(...\\)`
  - `\\[...\\]`
  数学写法统一改为更适合 Markdown 渲染器的：
  - `$...$`
  - `$$...$$`
- 同步修正了公式内少量文本符号写法，例如：
  - `heading`
  - `command`
  - `body collision`
  以避免被数学渲染器错误当作变量串。
- 已使用 `pandoc` 实际导出验证：
  - `pandoc docs/RL环境设计.md -f markdown+tex_math_dollars -t html5 -s --mathjax -o /tmp/RL环境设计_mathjax.html`
  导出成功。
- 已确认文档内不再存在：
  - 旧 LaTeX 定界符
  - 私有区乱码字符
  - Unicode 替换字符 `�`

修改文件：
- `docs/RL环境设计.md`
- `logs/daily_work_log.md`

产出/结论：
- `docs/RL环境设计.md` 现在已经改成统一的 Markdown 数学公式格式，后续在支持数学渲染的 Markdown 预览器中应能正常显示，不再夹杂引用乱码。

下一步：
- 若还需要，可继续把同类数学格式清洗规则应用到 `docs/` 下其他含公式文档。

已完成：
- 按用户要求新增顶层 RL 重构工程：
  - `complete_car_rl_training/`
- 新工程已改成 Isaac Lab 扩展式目录：
  - `scripts/train.py`
  - `scripts/play.py`
  - `source/complete_car_lab/config/extension.toml`
  - `source/complete_car_lab/setup.py`
  - `source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/...`
- 当前 direct task 已按新要求拆分为：
  - `base/env.py`
  - `base/complete_car_cfg.py`
  - `baseline/complete_car_stage0_cfg.py`
  - `baseline/complete_car_stage1_cfg.py`
  - `environment_adaptive/complete_car_stage2_cfg.py`
- `mdp/` 已拆分出：
  - `commands.py`
  - `actions.py`
  - `observations.py`
  - `rewards.py`
  - `terminations.py`
  - `resets.py`
  - `randomization.py`
- `terrain/`、`sensors/`、`kinematics/`、`utils/` 也已按新结构补齐。
- 新 Gym task id 已统一为：
  - `CompleteCar-Stage0`
  - `CompleteCar-Stage1`
  - `CompleteCar-Stage2`
- 已执行：
  - `python3 -m py_compile $(find complete_car_rl_training -name '*.py' | sort)`
  静态语法检查通过。

修改文件：
- `complete_car_rl_training/README.md`
- `complete_car_rl_training/pyproject.toml`
- `complete_car_rl_training/scripts/train.py`
- `complete_car_rl_training/scripts/play.py`
- `complete_car_rl_training/source/complete_car_lab/config/extension.toml`
- `complete_car_rl_training/source/complete_car_lab/setup.py`
- `complete_car_rl_training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/...`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前活跃 RL 重构主线已经从旧的 `RL_Training/...` 逻辑树迁到新的 `complete_car_rl_training/`。
- 新主线的任务注册、配置主干、stage 配置、训练脚本、回放脚本、模块边界已经统一到同一套 direct workflow 架构下。

下一步：
- 在带 Isaac Lab 环境的机器上优先验证：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless`
  - `python scripts/play.py --task CompleteCar-Stage0 --checkpoint <model.pt>`

已完成：
- 按用户进一步要求，把上一轮错误新建的平行目录重构结果迁回现有：
  - `RL_Training/`
  做原地替换。
- 当前 `RL_Training/` 根目录已清理为：
  - `README.md`
  - `pyproject.toml`
  - `scripts/train.py`
  - `scripts/play.py`
  - `source/complete_car_lab/...`
- 已删除旧结构与残留目录：
  - `RL_Training/complete_car_rl_training/`
  - `RL_Training/config/`
  - `RL_Training/docs/`
  - `RL_Training/kinematics/`
  - `RL_Training/rsl_rl/`
  - `RL_Training/scripts/rsl_rl/`
  - `RL_Training/setup.py`
  - `RL_Training/skills/`
  - `RL_Training/utils/`
- 已删除错误创建的平行目录：
  - `complete_car_rl_training/`
- 已执行：
  - `python3 -m py_compile $(find RL_Training -name '*.py' | sort)`
  静态语法检查通过。

修改文件：
- `RL_Training/README.md`
- `RL_Training/pyproject.toml`
- `RL_Training/scripts/train.py`
- `RL_Training/scripts/play.py`
- `RL_Training/source/complete_car_lab/...`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 这次重构已经不是平行新建项目，而是把现有 `RL_Training/` 原地替换成新架构。
- 后续检查项目时，只需要看 `RL_Training/`，不应再寻找已删除的 `complete_car_rl_training/`。

下一步：
- 在 Isaac Lab 环境中从 `RL_Training/` 根目录执行：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless`
  - `python scripts/play.py --task CompleteCar-Stage0 --checkpoint <model.pt>`

已完成：
- 按用户要求，更新 `docs/isaaclab_rl_template_and_mgdp_structure.md`，为当前 active direct 主线
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/`
  增补了一整节逐文件结构说明。
- 新增内容不再只停留在旧 manager-based 模板梳理，而是补齐了 current `complete_car` 目录下各脚本的：
  - 文件职责
  - 包含的类
  - 包含的函数
  - 类与函数在当前 direct workflow 中的功能含义
- 本轮文档覆盖了：
  - `__init__.py`
  - `complete_car_env_cfg.py`
  - `stage0_flat_cfg.py`
  - `stage1_terrain_cfg.py`
  - `stage2_perception_cfg.py`
  - `complete_car_env.py`
  - `commands.py`
  - `observations.py`
  - `local_velocity_tracking_reward.py`
  - `rewards.py`
  - `terminations.py`
  - `utils.py`
  - `assets/`
  - `sensors/`
  - `terrain/`
  - `agents/`
- 同步更新项目记忆文件，使后续会话能直接继承这次文档化结论。

修改文件：
- `docs/isaaclab_rl_template_and_mgdp_structure.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `docs/isaaclab_rl_template_and_mgdp_structure.md` 现在已经可以作为当前 direct `complete_car` 主线的结构化索引使用，后续阅读时可以先按文档确认“哪个脚本负责什么、类和函数分别做什么”，再进入源码细读。

下一步：
- 若继续补教学文档，可再把 `RL_Training/scripts/rsl_rl/train.py`、`play.py` 以及 `RL_Training/rsl_rl/` 的关键调用链按相同粒度补到结构文档里。

已完成：
- 按用户要求，将 `complete_car_env_cfg.py` 从“文件级多个并列配置类”改为“以 `CompleteCarEnvCfg` 为中心的嵌套配置类”组织。
- 当前嵌套结构包括：
  - `CommandCfg -> ranges`
  - `ObservationCfg -> scales / noise_scales`
  - `RewardCfg -> scales`
  - `ControlCfg / ResetCfg / RandomizationCfg`
  均作为 `CompleteCarEnvCfg` 的内部配置类存在。
- 按用户进一步要求，`CommandCfg`、`ObservationCfg`、`RewardCfg` 的子配置类名已统一改成与字段同名的小写形式，例如：
  - `ranges: ranges = ranges()`
  - `scales: scales = scales()`
  - `noise_scales: noise_scales = noise_scales()`
- 已检查仓库内对旧顶层配置类名的引用，当前 `RL_Training/` 中没有残留外部依赖这些旧类型名的位置。
- 已执行：
  - `python3 -m py_compile RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py RL_Training/complete_car_rl_training/tasks/direct/complete_car/stage0_flat_cfg.py RL_Training/complete_car_rl_training/tasks/direct/complete_car/stage1_terrain_cfg.py RL_Training/complete_car_rl_training/tasks/direct/complete_car/stage2_perception_cfg.py`
  静态校验通过。

修改文件：
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `complete_car_env_cfg.py` 当前已经改为更内聚的嵌套配置结构，后续阅读和维护时应从 `CompleteCarEnvCfg` 向下展开，而不是继续把各组配置类视为文件级平铺对象。

下一步：
- 若继续统一风格，可考虑把 `stage0_flat_cfg.py`、`stage1_terrain_cfg.py`、`stage2_perception_cfg.py` 中针对 `terrain/sensors/scene` 的 stage 覆写也进一步补成更显式的局部说明。

已完成：
- 按用户要求，参考 `complete_car_env_cfg.py` 前两个配置类的注释风格，为其余配置类补齐字段说明与少量方法级说明。
- 本轮注释补充覆盖了：
  - `CompleteCarControlCfg`
  - `CompleteCarObservationScalesCfg`
  - `CompleteCarObservationNoiseScalesCfg`
  - `CompleteCarObservationCfg`
  - `CompleteCarRewardScalesCfg`
  - `CompleteCarRewardCfg`
  - `CompleteCarResetCfg`
  - `CompleteCarRandomizationCfg`
  - `CompleteCarEnvCfg`
- 同步补充了 `CompleteCarEnvCfg` 中噪声模型构建和 `__post_init__` 主流程的简短说明，未改动任何配置值或运行逻辑。
- 已执行：
  - `python3 -m py_compile RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
  静态校验通过。

修改文件：
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `complete_car_env_cfg.py` 中共享 direct cfg 主干的主要字段都已有与现有风格一致的英文注释，后续讲解和维护时不必再反复对照运行逻辑猜字段含义。

下一步：
- 若继续做可读性维护，可按相同风格补齐 `stage0_flat_cfg.py`、`stage1_terrain_cfg.py`、`stage2_perception_cfg.py` 中仍偏稀疏的配置注释。

已完成：
- 按用户最新要求，把上一轮被删掉但仍需保留的旧内容重新迁入当前 `RL_Training/` 新架构内部。
- 已恢复并重定位本地 PPO 本体：
  - 旧位置：`RL_Training/rsl_rl/`
  - 新位置：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/`
- 已修改：
  - `RL_Training/scripts/train.py`
  - `RL_Training/scripts/play.py`
  让训练和回放优先导入项目内的 `complete_car/rsl_rl/`，不再默认依赖外部环境里的 `rsl_rl`。
- 已把旧辅助脚本迁入：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/`
  包括：
  - `list_envs.py`
  - `random_agent.py`
  - `zero_agent.py`
  - `export_training_stage.py`
  - `tensorboard_export.py`
  - `validate_wheel_speed_allocator.py`
- 这些辅助脚本的导入已同步改成：
  - `complete_car_lab`
  - `CompleteCar-Stage0/1/2`
- 已把旧 `RL_Training/utils/` 中的 IK/FK 内容迁入：
  - `kinematics/ik_solver.py`
  - `kinematics/fk_solver.py`
  - `kinematics/legacy_ik/`
  - `kinematics/legacy_fk/`
- `IK_model.py` 的 3RRR 球面并联逆解逻辑已经并入 `ik_solver.py`，并保留旧推导资料作为参考文件。
- 已执行：
  - `python3 -m py_compile $(find RL_Training -name '*.py' | sort)`
  静态校验通过。

修改文件：
- `RL_Training/scripts/train.py`
- `RL_Training/scripts/play.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/...`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/...`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/ik_solver.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/fk_solver.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/legacy_ik/...`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/legacy_fk/...`
- `README.md`
- `RL_Training/README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前新架构并没有丢掉旧 PPO 本体、旧 IK/FK、旧辅助脚本，而是把它们统一收口到了 `tasks/direct/complete_car/` 之下。
- 顶层 `RL_Training/scripts/` 现只保留训练和回放入口，其余辅助脚本已迁入包内 `utils/`。

下一步：
- 在 Isaac Lab 环境中验证：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless`
  - `python scripts/play.py --task CompleteCar-Stage0 --checkpoint <model.pt>`
  - `python -m complete_car_lab.tasks.direct.complete_car.utils.list_envs`

已完成：
- 按用户要求，为 `base/complete_car_cfg.py` 中的 `CommandCfg` 补充了以下字段的中文注释：
  - `heading_command`
  - `zero_command`
  - `rel_standing_envs`
- 同时为 `ControlCfg` 中时间步长、控制周期、球铰/车轮刚度阻尼、力矩上限、速度上限等字段补充了单位注释。
- 本轮未改动任何配置值与运行逻辑，仅提升配置文件可读性。
- 已执行：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `complete_car_cfg.py` 里命令语义和控制参数单位已经更明确，后续阅读和讲解时不需要再额外口头说明这些字段的物理含义。

已完成：
- 按用户要求，修改当前 direct 主线的本体观测定义，不再把车体姿态欧拉角和姿态角速率作为 policy observation。
- 新的基础本体观测改为：
  - `base_lin_vel_b`
  - `base_ang_vel_b`
  - `projected_gravity_b`
  - `ball_joint_pos`
  - `ball_joint_vel`
  - `commands`
  - `last_action`
- 同步修改了：
  - `ObservationScalesCfg`
  - `ObservationNoiseCfg`
  - observation descriptor
  - observation 维度与噪声幅值计算
- 已执行：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active observation 已经从“姿态角 + 姿态角速度”切换成“base 线速度 + base 角速度 + 重力投影”，后续解释环境时应以这套定义为准。

已完成：
- 按用户要求，删除 `CompleteCarEnvCfg` 中按 `stage_name` 自动绑定 terrain / sensor 默认值的 `_bind_stage_defaults()`。
- 同步把原先 Stage0 / Stage1 / Stage2 的 terrain 和 sensor 开关配置，下放到各自的 stage cfg 文件中显式定义：
  - `complete_car_stage0_cfg.py`
  - `complete_car_stage1_cfg.py`
  - `complete_car_stage2_cfg.py`
- `CompleteCarEnvCfg.__post_init__()` 不再隐式修改阶段差异，base cfg 现在只负责共享骨架和统一装配。
- 已执行：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/environment_adaptive/complete_car_stage2_cfg.py`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/environment_adaptive/complete_car_stage2_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 stage 差异已经真正下沉到分阶段配置文件中，后续用户可直接在各 stage cfg 内继续定义 terrain / sensor 方案，而不需要修改 base cfg 中的集中绑定逻辑。

## 2026-04-10

已完成：
- 按用户要求，处理 `complete_car.usd` 中 articulation root 迁移到 `/World/complete_car_alternative/body_car_chassis` 后的联动脚本。
- direct RL 资产配置已显式对齐新的 articulation root：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/assets/robot_cfg.py`
  现在通过 `articulation_root_prim_path = "/body_car_chassis"` 指向新的根节点，而不是继续隐式依赖 USD 自动搜索。
- 与车体挂点相关的默认 prim path 已同步修改：
  - `sensors/sensor_runtime.py`
    - IMU -> `.../body_car_chassis/IMU_body`
    - camera -> `.../head_car_chassis/Stereo_rig/left_camera`
    - lidar -> `.../head_car_chassis/Example_Rotary`
  - `terrain/terrain_runtime.py`
    - height scanner -> `.../body_car_chassis`
- 直接打开 USD 并创建 articulation 的脚本已切到新的 articulation root：
  - `scripts/isaac_sim/control_keyboard.py`
  - `scripts/isaac_sim/rover_control.py`
- `scripts/isaac_sim/check_isaaclab_asset.py` 已补充新的 root 检查，并在最小加载测试里显式写入 `articulation_root_prim_path="/body_car_chassis"`。

修改文件：
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/assets/robot_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/sensors/sensor_runtime.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terrain/terrain_runtime.py`
- `scripts/isaac_sim/check_isaaclab_asset.py`
- `scripts/isaac_sim/control_keyboard.py`
- `scripts/isaac_sim/rover_control.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前项目已经明确区分：
  - 资产挂载根
  - articulation root
- RL 主线继续挂载在 `.../Robot` 下，但 articulation API 会显式落到 `.../Robot/body_car_chassis`。
- 已执行 `python3 -m py_compile`，本轮涉及文件静态校验通过。

下一步：
- 在 Isaac Sim / Isaac Lab 环境中优先验证：
  - `scripts/isaac_sim/control_keyboard.py`
  - `scripts/isaac_sim/check_isaaclab_asset.py`
  - `python scripts/list_envs.py --keyword Complete-Car`

已完成：
- 按用户要求清理当前 direct 主线中的模板残余和未接线字段。
- 收口训练与回放脚本：
  - `RL_Training/scripts/rsl_rl/train.py`
  - `RL_Training/scripts/rsl_rl/play.py`
  现在不再保留 manager-based / MARL 模板类型联合，也移除了 `train.py` 中只对 manager-based 生效的 `--export_io_descriptors` 分支。
- 收口 direct env 配置主干：
  - 删除 `CompleteCarCommandCfg` 中未接线的 `heading_command`、`rel_heading_envs`、`debug_vis`
  - 删除 `CompleteCarCommandRangesCfg` 中未接线的 `ang_vel_z`、`heading`
  - 删除 `CompleteCarRewardCfg` 中未接线的 `base_height_target`
- 将当前 direct 主线的噪声链路切回 Isaac Lab 基类能力：
  - `DirectRLEnvCfg.action_noise_model`
  - `DirectRLEnvCfg.observation_noise_model`
  当前 `randomization.action_noise_std / action_bias_std` 与 `observations.add_noise / noise_level / noise_scales` 仍作为参数源保留，但不再由 `CompleteCarEnv` 和 `observations.py` 手写加噪。
- 同步修正文档中“这些残余仍存在”的旧描述，并纠正架构文档实际路径为：
  - `docs/complete_car_direct_workflow_architecture.md`

修改文件：
- `RL_Training/scripts/rsl_rl/train.py`
- `RL_Training/scripts/rsl_rl/play.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/observations.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/utils.py`
- `README.md`
- `docs/complete_car_direct_workflow_architecture.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 direct 主线已经不再保留用户本轮点名的模板残余和未接线字段。
- 噪声配置现在有了清晰边界：
  - 本地 cfg 负责参数源
  - Isaac Lab 基类负责运行时噪声注入
- 当前默认 stage 仍是 `use_history = False`，因此观测噪声切回基类后不会影响现有主线的历史堆叠语义。
- 已对本轮涉及的训练脚本与 direct 主线核心 Python 文件执行 `python3 -m py_compile`，静态校验通过。

下一步：
- 在具备 Isaac Lab 运行环境的机器上，优先做一次 Stage0 direct 冒烟。

已完成：
- 按用户要求，替换 `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex` 中 `3.1.10`“整车速度雅可比矩阵构造”部分，采用新的长版推导正文。
- 将用户草稿里混入的非法格式全部改回合法 LaTeX，包括：
  - 非法分隔符
  - 损坏的矩阵换行
  - 错误的公式对齐
  - 非法符号拼接
- 保留并整理了该小节的主要公式链：
  - 整车广义速度 `\boldsymbol\xi`
  - 反对称矩阵算子 `\mathbf S(\mathbf x)`
  - 模块刚体速度映射 `\mathbf K_1(\mathbf q), \mathbf K_2, \mathbf K_3(\mathbf q)`
  - 单模块轮速映射 `\mathbf H_i`
  - 整车速度雅可比 `\mathbf J_w(\mathbf q)`
- 在 `毕业论文/毕业论文模板/LaTeX/` 下重新执行：
  - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
  编译成功，`main.pdf` 已更新。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `毕业论文/毕业论文模板/LaTeX/main.pdf`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `3.1.10` 小节已经从用户提供的损坏草稿替换为可编译、符号一致的 LaTeX 版本。
- 当前论文主文档可继续通过 XeLaTeX 生成 PDF。
- 当前仍只剩 2 条旧的非阻塞文献警告：
  - `fang2015survey`
  - `MATSUMURA2017566`

下一步：
- 若继续打磨 chapter03，可再针对这一节里过长的行公式做版面收缩，但这已经不影响编译通过。

已完成：
- 根据用户新的长期主线要求，将完整车 RL 项目从 Isaac Lab manager-based 架构彻底重构为 direct workflow。
- 新增 direct task 主目录：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/`
- 实际新增文件包括：
  - `complete_car_env.py`
  - `complete_car_env_cfg.py`
  - `stage0_flat_cfg.py`
  - `stage1_terrain_cfg.py`
  - `stage2_perception_cfg.py`
  - `rewards.py`
  - `observations.py`
  - `commands.py`
  - `terminations.py`
  - `utils.py`
  - `agents/ppo_cfg.py`
  - `assets/robot_cfg.py`
  - `terrain/terrain_generator.py`
  - `terrain/terrain_runtime.py`
  - `sensors/sensor_runtime.py`
- 新 direct Gym task id 已改为：
  - `Complete-Car-Stage0-Flat-Direct-v0`
  - `Complete-Car-Stage1-Terrain-Direct-v0`
  - `Complete-Car-Stage2-Perception-Direct-v0`
- 已删除旧主线文件：
  - `envs/base/complete_car_config.py`
  - `envs/base/complete_car_env.py`
  - `envs/base/manager_helpers.py`
  - `envs/base/robot_cfg.py`
  - `envs/baseline/complete_car_config_baseline.py`
  - `envs/__init__.py`
  - `utils/terrain.py`
- 已同步修改根目录 Isaac Sim 预览/控车脚本，使其读取新的：
  - `tasks/direct/complete_car/assets/robot_cfg.py`
  - `tasks/direct/complete_car/terrain/terrain_generator.py`
- 已同步更新：
  - `README.md`
  - `RL_Training/README.md`
  - `RL_Training/docs/training_workflow_and_tensorboard_guide.md`
  - `docs/project_file_map.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`

修改文件：
- `README.md`
- `RL_Training/README.md`
- `RL_Training/docs/training_workflow_and_tensorboard_guide.md`
- `docs/project_file_map.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `RL_Training/complete_car_rl_training/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/stage0_flat_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/stage1_terrain_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/stage2_perception_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/rewards.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/observations.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/commands.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terminations.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/utils.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents/ppo_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/assets/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/assets/robot_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terrain/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terrain/terrain_generator.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terrain/terrain_runtime.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/sensors/__init__.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/sensors/sensor_runtime.py`
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `scripts/isaac_sim/preview_stage1_tile.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `scripts/isaac_sim/control_keyboard.py`

产出/结论：
- 当前 RL 工程主线已经从“manager term 组装任务”切换为“env 主类直接管理任务语义”的 direct workflow。
- 结构上已经保留了“共享参数模板 + 分阶段继承配置”的思想，但不再保留 `CompleteCarObservationsCfg / CompleteCarActionsCfg / CompleteCarEventsCfg` 这类 manager-based 配置分组。
- 当前机器没有 Isaac Lab 运行环境，因此本轮不做运行态冒烟，只完成代码重构和仓库记忆同步。

下一步：
- 在有 Isaac Lab 环境的机器上，优先执行：
  - `python scripts/list_envs.py --keyword Complete-Car`
  - `python scripts/rsl_rl/train.py --task Complete-Car-Stage0-Flat-Direct-v0 --headless --num_envs 100 --max_iterations 10`

已完成：
- GitHub 同步后，清理了本地未跟踪的旧 `src/` 残留目录，不再保留旧 `src/rl_lab/complete_car_rl_training/` 工作树副本。
- 统一修正后续使用的命令入口和说明文件，明确当前所有可运行命令默认都应从：
  - `/home/ubuntu/Graduation-Project/RL_Training`
  执行。
- 修正文档与技能中的旧路径或失效引用：
  - `AGENTS.md`
  - `RL_Training/README.md`
  - `RL_Training/docs/training_workflow_and_tensorboard_guide.md`
  - `RL_Training/skills/isaac-rl-run-diagnosis/SKILL.md`
  - `docs/isaaclab模板使用指南.md`
  - `docs/isaaclab_rl_template_and_mgdp_structure.md`
  - `docs/current_status.md`

修改文件：
- `AGENTS.md`
- `RL_Training/README.md`
- `RL_Training/docs/training_workflow_and_tensorboard_guide.md`
- `RL_Training/skills/isaac-rl-run-diagnosis/SKILL.md`
- `docs/isaaclab模板使用指南.md`
- `docs/isaaclab_rl_template_and_mgdp_structure.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库已经不再保留本地旧 `src/` 运行入口。
- 后续列环境、训练、回放、TensorBoard 导出等命令，默认都应在 `RL_Training/` 下执行。

下一步：
- 在具备 Isaac Lab 运行环境的机器上，从 `RL_Training/` 执行一次 `list_envs.py` 和 Stage0 小规模 `train.py` 冒烟。

已完成：
- 基于当前 direct workflow 真实代码，新增了完整车 RL 主线的长期架构说明文档：
  - `docs/complete_car_direct_workflow_architecture.md`
- 文档内容已系统整理：
  - task 注册与入口机制
  - env / cfg / terrain runtime / sensor runtime 的职责边界
  - 训练调用链
  - Stage0 / Stage1 / Stage2 的组织关系
  - 后续修改观测、奖励、动作、命令、课程学习、terrain、传感器、stage、agent 配置时应优先修改的位置
- 同步更新仓库说明与项目地图，使新文档可被后续会话直接发现：
  - `README.md`
  - `docs/project_file_map.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`

修改文件：
- `docs/complete_car_direct_workflow_architecture.md`
- `README.md`
- `docs/project_file_map.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库已经有一份可长期保留、可反复检索的 direct workflow 架构说明，不再需要每次从聊天记录临时重建调用链和修改入口。

下一步：
- 如果后续 direct 主线继续演化，优先维护这份文档，而不是只在聊天记录里解释。

## 2026-04-10（GitHub 同步）

已完成：
- 检查当前仓库 Git 状态，确认当前分支为 `main`，远程 `origin` 指向 `git@github.com:MARS-ROBOTICS-star/Graduation-Project.git`。
- 为避免误提交论文编译中间产物，在 `毕业论文/毕业论文模板/LaTeX/.gitignore` 中补充了 `*.xdv` 忽略规则。
- 将当前工作区状态整理后提交，并准备推送到远程 GitHub 仓库。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/.gitignore`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库的 GitHub 同步路径已经明确，后续只需继续在 `main` 分支提交并推送到现有 `origin`。
- `main.xdv` 不再作为未跟踪文件干扰后续提交。

下一步：
- 将本地提交推送到 `origin/main`，完成本次上传。

## 2026-04-09

已完成：
- 按用户新要求继续收敛 RL 训练文件结构，使 `base` 更像通用框架层，`baseline` 更像阶段参数覆写层。
- 实际结构调整：
  - 保留并重写：
    - `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
  - 新增：
    - `RL_Training/complete_car_rl_training/envs/baseline/complete_car_config_baseline.py`
    - `RL_Training/complete_car_rl_training/utils/__init__.py`
  - 将原：
    - `envs/baseline/stage1_terrain.py`
    移动并改为：
    - `RL_Training/complete_car_rl_training/utils/terrain.py`
  - 删除旧 baseline 子文件：
    - `envs/baseline/__init__.py`
    - `envs/baseline/stage1_env.py`
    - `envs/baseline/stage1_env_cfg.py`
    - `envs/baseline/agents/`
    - `envs/baseline/mdp/`
- 新的职责划分：
  - `base/complete_car_config.py`
    - 作为共享 RL 训练框架文件
    - 当前明确包含：
      - `env`
      - `terrain`
      - `perception`
      - `control`
      - `scene`
      - `commands`
      - `observations`
      - `actions`
      - `events`
      - `rewards`
      - `terminations`
      - `curriculum`
      - `CompleteCarRLEnv`
      - `CompleteCarCfgPPO`
  - `baseline/complete_car_config_baseline.py`
    - 只负责 baseline 阶段 reward / terrain / perception / PPO 参数覆写与 Gym 注册
  - `utils/terrain.py`
    - 负责 terrain 生成和 terrain runtime helper
- 同步修复：
  - `envs/__init__.py`
    - 改为直接导入 `baseline/complete_car_config_baseline.py`
  - `scripts/isaac_sim/preview_stage1_terrain.py`
  - `scripts/isaac_sim/preview_stage1_tile.py`
  - `scripts/isaac_sim/preview_stage1_last_six.py`
  - `scripts/isaac_sim/control_keyboard.py`
    的 terrain 模块路径，统一指向 `utils/terrain.py`
- 实际执行静态校验：
  - 对 `RL_Training/complete_car_rl_training`、`RL_Training/scripts`、`scripts/isaac_sim` 执行了 `python3 -m py_compile`
  - 语法检查通过

修改文件：
- `README.md`
- `RL_Training/README.md`
- `docs/current_status.md`
- `docs/project_file_map.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `RL_Training/complete_car_rl_training/envs/__init__.py`
- `RL_Training/complete_car_rl_training/envs/base/__init__.py`
- `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
- `RL_Training/complete_car_rl_training/envs/baseline/complete_car_config_baseline.py`
- `RL_Training/complete_car_rl_training/utils/__init__.py`
- `RL_Training/complete_car_rl_training/utils/terrain.py`
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `scripts/isaac_sim/preview_stage1_tile.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `scripts/isaac_sim/control_keyboard.py`

产出/结论：
- 当前 `base` 已经更接近“MGDP 风格的通用 config trunk”，但仍保持 Isaac Lab manager-based 的组织方式，没有回退到大而全的手写 `base_task` 模式。
- 当前 `baseline` 目录已被压缩成单文件参数覆写层，后续更容易保留阶段配置而不是不断覆盖旧版本。
- 当前 terrain 逻辑已经离开 baseline 目录，后续若拓展 Stage2 / Stage3，不必再复制一份 terrain 生成文件。

下一步：
- 在 `env_isaacLab` 中从 `RL_Training/` 目录执行：
  - `python scripts/list_envs.py --keyword Complete-Car`
  - `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --headless --num_envs 100 --max_iterations 10`
 继续做运行态冒烟。

## 2026-04-09（论文编译修复）

已完成：
- 根据用户要求排查 `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex` 的编译失败问题。
- 确认原 `chapter03.tex` 中混入了大量非法格式内容，包括：
  - 伪 Markdown 分隔线
  - `#` 标记
  - 损坏的矩阵换行
  - 错误的下标和行内数学写法
- 将 `chapter03.tex` 正文重写为干净的 LaTeX 版本，保留章节结构、主要公式标签和整车运动学 / 速度雅可比推导主线。
- 在 `毕业论文/毕业论文模板/LaTeX/` 下执行：
  - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
  现已可成功生成 `main.pdf`。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `chapter03.tex` 的格式性编译错误已清除，整篇论文恢复可编译状态。
- 当前剩余的编译输出里仍有 2 条非阻塞文献警告：
  - `fang2015survey`
  - `MATSUMURA2017566`
  它们来自 `reference/ref.bib` 缺失条目，不影响 `main.pdf` 生成。

下一步：
- 若需要完全清空编译警告，可继续补齐 `reference/ref.bib` 中缺失的 2 条文献。

## 2026-04-09（论文推导重写）

已完成：
- 根据用户要求，重写 `chapter03.tex` 中“前后模块线速度推导”部分。
- 当前改写方式不再直接给出
  - `${}^{2}\mathbf v_1={}^2\mathbf v_2+{}^2\boldsymbol\omega_2\times{}^2\mathbf p_1+{}^2\dot{\mathbf p}_1`
  - `${}^{2}\mathbf v_3={}^2\mathbf v_2+{}^2\boldsymbol\omega_2\times{}^2\mathbf p_3+{}^2\dot{\mathbf p}_3`
  而是先引入惯性坐标系 `${W}`，从模块参考点绝对位置关系出发，经乘积求导与旋转坐标系速度变换，自然推出牵连项与相对位置导数项。
- 同步保留并复用原有主要公式标签，避免破坏后文引用链。
- 再次执行：
  - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
  编译通过，`main.pdf` 已更新。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 这一段推导现在更适合作为论文正文教学型叙述，能直接回答“为什么会多出 `${}^{2}\dot{\mathbf p}_1` / ${}^{2}\dot{\mathbf p}_3` 这一项”。
- 当前仍只剩 2 条旧的文献缺失警告，不影响 PDF 生成。

下一步：
- 若还要继续打磨 chapter03，可再把这一节中的“牵连速度”“相对运动速度”术语与后文雅可比构造部分统一一下表述。

## 2026-04-09（续）

已完成：
- 按用户要求，继续参照 `/MGDP/legged_gym/legged_gym/envs/base/legged_robot_config.py` 重写共享 trunk：
  - `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
- 当前 trunk 现在明确收口为两个主类：
  - `CompleteCarCfg`
  - `CompleteCarPPoCfg`
- `CompleteCarCfg` 已按更接近 MGDP 的方式补齐并重排根配置树，当前显式包含：
  - `env`
  - `env_init_info`
  - `IMU`
  - `camera`
  - `Radar`
  - `terrain`
  - `commands`
  - `init_state`
  - `control`
  - `asset`
  - `domain_rand`
  - `rewards`
  - `evals`
  - `normalization`
  - `noise`
  - `viewer`
  - `sim`
  - `randomization`
  - `privInfo`
- 同时仍保留 Isaac Lab manager-based 运行层：
  - `scene`
  - `observations`
  - `actions`
  - `events`
  - `terminations`
  - `curriculum`
  - `CompleteCarRLEnv`
- 本轮实际实现方式：
  - `camera` 与 `IMU` 使用 Isaac Lab 原生 sensor cfg 风格
  - `sim / sim.physx / viewer / observation scale / observation noise` 沿用 Isaac Lab 原生配置方式
  - `Radar` 先作为标准保留配置槽位写入 trunk，默认关闭，未直接接入当前 scene manager
  - `commands` 与 `rewards` 采用“用户参数树 + `__post_init__` 生成 manager 运行配置”的方式落地
- 同步调整：
  - `RL_Training/complete_car_rl_training/envs/base/__init__.py`
    - 共享 PPO trunk 导出名改为：
      - `CompleteCarPPoCfg`
  - `RL_Training/complete_car_rl_training/envs/baseline/complete_car_config_baseline.py`
    - 改为主要继承共享配置树并覆写 Stage1 baseline 参数
- 实际执行静态校验：
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/base/__init__.py`
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/baseline/complete_car_config_baseline.py`
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/__init__.py`
  - 语法检查通过

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `RL_Training/complete_car_rl_training/envs/base/__init__.py`
- `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
- `RL_Training/complete_car_rl_training/envs/baseline/complete_car_config_baseline.py`

产出/结论：
- 当前共享 trunk 已不再只是“分块式 manager 配置集合”，而是已经变成“MGDP 风格参数树 + Isaac Lab manager-based 运行层”的统一配置入口。
- 之后如果做 baseline、Stage2、传感器阶段或 privileged 信息阶段，优先继承 `CompleteCarCfg` 并覆写嵌套参数，不应再重新拆一份新的共享骨架。
- 当前共享 PPO 主类名称已经固定为：
  - `CompleteCarPPoCfg`

下一步：
- 在 `env_isaacLab` 中从 `RL_Training/` 目录执行：
  - `python scripts/list_envs.py --keyword Complete-Car`
  - 或 `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --headless --num_envs 100 --max_iterations 10`
  继续做运行态冒烟，确认新 trunk 在真实 Isaac Lab 环境里可正常注册和启动。

## 2026-04-09（再续）

已完成：
- 根据用户进一步澄清的文件职责边界，继续收口 `envs/base/`：
  - `complete_car_config.py` 现在只保留两个顶层主类：
    - `CompleteCarCfg`
    - `CompleteCarPPoCfg`
- 将运行环境类移出到：
  - `RL_Training/complete_car_rl_training/envs/base/complete_car_env.py`
  当前包含：
  - `CompleteCarRLEnv`
- 将 command / reward helper 与 Isaac Lab manager 辅助配置移出到：
  - `RL_Training/complete_car_rl_training/envs/base/manager_helpers.py`
  当前包含：
  - `CompleteCarUniformVelocityCommand`
  - `UniformVelocityCommandCfg`
  - `joint_pos_target_l2`
  - `CompleteCarSceneCfg`
  - `CompleteCarObservationsCfg`
  - `CompleteCarActionsCfg`
  - `CompleteCarEventsCfg`
  - `CompleteCarTerminationsCfg`
  - `CompleteCarCurriculumCfg`
- 当前 `CompleteCarCfg.__post_init__` 的职责已经收口为：
  - 读取嵌套参数树
  - 组装 Isaac Lab manager-based 运行配置
  - 不再在本文件中定义 env runtime 类和独立 helper 函数
- 同步更新：
  - `RL_Training/complete_car_rl_training/envs/base/__init__.py`
    - 改为从新拆分文件导出 `CompleteCarRLEnv` 和 `CompleteCarSceneCfg`
- 实际执行静态校验：
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/base/manager_helpers.py`
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/base/complete_car_env.py`
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
  - `python3 -m py_compile RL_Training/complete_car_rl_training/envs/base/__init__.py RL_Training/complete_car_rl_training/envs/baseline/complete_car_config_baseline.py RL_Training/complete_car_rl_training/envs/__init__.py`
  - 语法检查通过

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `RL_Training/complete_car_rl_training/envs/base/__init__.py`
- `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
- `RL_Training/complete_car_rl_training/envs/base/complete_car_env.py`
- `RL_Training/complete_car_rl_training/envs/base/manager_helpers.py`

产出/结论：
- 当前 `complete_car_config.py` 已满足“只保留两个顶层类”的结构边界。
- 当前共享主干已经形成：
  - 参数树文件
  - helper 文件
  - runtime env 文件
  三者分离的结构。
- 之后若继续加 reward / command / env runtime 逻辑，不应再回填到 `complete_car_config.py`。

下一步：
- 在 `env_isaacLab` 中从 `RL_Training/` 目录执行：
  - `python scripts/list_envs.py --keyword Complete-Car`
  - 或 `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --headless --num_envs 100 --max_iterations 10`
  继续确认这次拆分后注册和运行态没有被破坏。

## 2026-04-08

已完成：
- 按用户最新要求进一步重构 `RL_Training/complete_car_rl_training/` 的主包结构。
- 实际调整：
  - 删除顶层历史残留目录：
    - `RL_Training/complete_car_rl_training/agents`
    - `RL_Training/complete_car_rl_training/mdp`
  - 删除 `envs/base/agents/` 与 `envs/base/mdp/`
  - 删除旧共享文件：
    - `envs/base/base_env_cfg.py`
    - `envs/base/scene_cfg.py`
  - 新增并作为共享主干收口到：
    - `envs/base/complete_car_config.py`
- 新共享主干当前集中承载：
  - `CompleteCarCfg`
  - `CompleteCarCfgPPO`
  - `CompleteCarSceneCfg`
  - `CompleteCarRLEnv`
  - 共享 command / observation / action / event / termination / reward helper 逻辑
- 同步修复：
  - `complete_car_rl_training/__init__.py`
  - 新增 `complete_car_rl_training/envs/__init__.py`
  - `envs/baseline/stage1_env_cfg.py`
  - `envs/baseline/stage1_env.py`
  - `envs/baseline/agents/rsl_rl_ppo_cfg.py`
  - 根目录 Isaac Sim 脚本对旧 `common/stage1` 路径的引用
- 根目录 Isaac Sim 脚本当前统一改为从：
  - `complete_car_rl_training.envs.base`
  - `complete_car_rl_training.envs.baseline.stage1_terrain`
  读取机器人配置和地形。
- 实际执行静态校验：
  - 对主包、Stage1 包、训练脚本和 Isaac Sim 相关脚本执行了新的 `py_compile`
  - 语法检查通过

修改文件：
- `README.md`
- `RL_Training/README.md`
- `docs/current_status.md`
- `docs/project_file_map.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `RL_Training/complete_car_rl_training/__init__.py`
- `RL_Training/complete_car_rl_training/envs/__init__.py`
- `RL_Training/complete_car_rl_training/envs/base/__init__.py`
- `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
- `RL_Training/complete_car_rl_training/envs/base/robot_cfg.py`
- `RL_Training/complete_car_rl_training/envs/baseline/stage1_env_cfg.py`
- `RL_Training/complete_car_rl_training/envs/baseline/stage1_env.py`
- `RL_Training/complete_car_rl_training/envs/baseline/agents/rsl_rl_ppo_cfg.py`
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `scripts/isaac_sim/preview_stage1_tile.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `scripts/isaac_sim/control_keyboard.py`

产出/结论：
- 当前 RL 主线已经从“`common/ + stage1/` 两层包结构”进一步收敛到“`envs/base + envs/baseline`”结构。
- 当前共享模板不再分散在多个 base 子文件里，而是统一集中到 `complete_car_config.py`。
- 这次调整的重点不是改变任务语义，而是让后续 Stage2 / Stage3 扩展时继续保持“共享主干明确、阶段特化独立”的组织方式。

下一步：
- 在 `env_isaacLab` 中从 `RL_Training/` 目录执行：
  - `python scripts/list_envs.py --keyword Complete-Car`
  - 或小规模 `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --headless --num_envs 100 --max_iterations 10`
  继续做运行态冒烟确认。

## 2026-04-07

已完成：
- 诊断训练 run `2026-04-07_19-42-44`，并整理相对上一轮 `2026-04-07_15-57-27` 的参数变化。
- 实际检查：
  - `/tmp/isaaclab/logs/isaaclab_2026-04-07_19-42-44.log`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_19-42-44/params/env.yaml`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_19-42-44/params/agent.yaml`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_19-42-44/tensorboard_export/summary.json`
  - 与 `2026-04-07_15-57-27` 的 `env.yaml / agent.yaml` 做 diff
- 关键参数变化：
  - `agent.max_iterations: 600 -> 500`
  - `reset_base.velocity_range`
    - `x/y/z/roll/pitch/yaw` 全部改为 `0`
  - `base_velocity` 新增曲率耦合命令：
    - `curvature_range = (-0.5, 0.5)`
    - `turn_lin_vel_threshold = 0.1`
- 关键结果：
  - `Train/mean_episode_length = 960.0`
  - `Episode_Termination/time_out = 1.0`
  - `bad_orientation = 0.0`
  - `ball_joint_out_of_bounds = 0.0`
  - `mean_reward: 48.14 -> 50.92`
  - `error_vel_xy: 0.616 -> 0.613`
  - `error_vel_yaw: 0.676 -> 0.542`
  - `root_height_mean: 0.111 -> 0.139`
  - `root_height_min: 0.051 -> 0.111`
- 结论：
  - 这次 run 继续保持完全健康 rollout，并且 yaw tracking 明显优于 `15-57-27`。
  - 取消初始 root velocity 扰动和引入速度-曲率耦合命令，没有把训练带坏，反而带来了更平衡的 tracking。
  - 但 root frame 仍然偏低，只能说“比上一轮更好”，还不能说“车身高度问题已经解决”。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `2026-04-07_19-42-44` 目前是当日这条基线上的更优参考 run。

下一步：
- 如果继续调参，优先围绕“如何在不破坏当前 tracking 的前提下，进一步改善 root frame 过低”的问题展开。

已完成：
- 按用户要求将 Stage1 车轮动作空间从“3 个车桥轮速”改回“6 个车轮独立轮速”。
- 实际修改：
  - 删除本轮新增的 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/actions.py`
  - 修改 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py`
    - 恢复导出 `JointVelocityActionCfg`
  - 修改 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - `wheel_joint_vel` 改回 6 个轮关节独立 `JointVelocityActionCfg`
  - 修改 `README.md`
    - 恢复 Stage1 baseline 描述为 `6 球铰 + 6 轮速`
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- 结果：
  - 当前动作空间已恢复到先前版本
  - 总动作维度重新回到 `12`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `README.md`

产出/结论：
- 当前 Stage1 baseline 仍按“6 个球铰 + 6 个车轮独立速度”解释。

下一步：
- 若后续还要讨论左右轮是否应耦合，需把它作为新的任务定义变更重新评估，而不是保留两套动作语义并存。

已完成：
- 按用户要求修改 Stage1 `base_velocity` 命令采样逻辑，改为“线速度 + 曲率”生成 yaw 命令。
- 实际修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/commands.py`
    - 为本地 `CompleteCarUniformVelocityCommand` 增加曲率采样分支
    - 当配置了 `curvature_range` 时：
      - 先采样 `lin_vel_x`
      - 再采样 `curvature`
      - 令 `yaw_vel = lin_vel_x * curvature`
      - 若 `|lin_vel_x| < turn_lin_vel_threshold`，则强制 `yaw_vel = 0`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - 当前默认设置为：
      - `curvature_range = (-0.5, 0.5)`
      - `turn_lin_vel_threshold = 0.1`
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/commands.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- 结果：
  - 当前 yaw command 已不再独立于前进速度采样
  - 当前命令语义更接近车辆“速度 + 曲率”的控制方式

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/commands.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 从当前版本开始，Stage1 训练结果中的 yaw tracking 需要按“速度耦合转向命令”解释，不能再直接与旧的独立 `ang_vel_z` 采样 run 混为一类。

下一步：
- 重新训练一轮，再比较新的 command 分布对线速度/yaw 跟踪平衡是否有改善。

已完成：
- 按用户要求修改 Stage1 动作空间，取消 6 个车轮完全独立的轮速控制，改为 3 个车桥轮速自由度。
- 实际修改：
  - 新增 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/actions.py`
    - 实现 `CoupledWheelVelocityAction`
    - 将每个车桥的 1 个动作映射到左右两个轮关节的相同速度目标
  - 修改 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py`
    - 导出 `CoupledWheelVelocityActionCfg`
  - 修改 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - 用 `wheel_groups` 替代原 6 轮独立 `JointVelocityActionCfg`
    - 当前轮速动作顺序为：
      - body axle
      - head axle
      - tail axle
  - 修改 `README.md`
    - 同步 Stage1 baseline 描述为 `6 球铰 + 3 车桥轮速`
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/actions.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- 结果：
  - 当前策略不再能给同一车桥左右轮下相反方向的速度命令
  - 动作总维度从 `12` 变为 `9`
  - 观测中的 `wheel_joint_vel_rel` 仍保留 6 维，便于继续观察左右轮实际执行差异

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/actions.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `README.md`

产出/结论：
- 当前 Stage1 baseline 的车轮控制语义已经变成“按车桥控制”，更符合车辆实际约束。

下一步：
- 用训练启动命令重新跑一次，确认新的 9 维动作空间下 rollout 是否稳定，以及 yaw/线速度 tracking 是否受明显影响。

已完成：
- 诊断训练 run `2026-04-07_15-57-27`，确认移除 `root_too_low` 后 rollout 已恢复为正常走满。
- 实际检查：
  - `/tmp/isaaclab/logs/isaaclab_2026-04-07_15-57-27.log`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-57-27/params/env.yaml`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-57-27/params/agent.yaml`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-57-27/tensorboard_export/summary.json`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-57-27/tensorboard_export/scalars/*.csv`
- 关键结论：
  - `Train/mean_episode_length = 960.0`
  - `Episode_Termination/time_out = 1.0`
  - `Episode_Termination/bad_orientation = 0.0`
  - `Episode_Termination/ball_joint_out_of_bounds = 0.0`
  - `error_vel_xy ≈ 0.62`
  - `error_vel_yaw ≈ 0.68`
  - 说明去掉 `root_too_low` 后，训练已从上一轮“几乎全部早死”的坏状态恢复到完整 episode 存活，并且速度跟踪已正常学起来。
  - 同时根高度日志显示：
    - `root_height_mean` 最近 20 点均值约 `0.132`
    - `root_height_min` 最近 20 点均值约 `0.090`，最小下探到约 `0.017`
  - 因而当前结论是：
    - 上一轮 `2026-04-07_15-29-34` 的主因确实是 `root_too_low`
    - 但移除高度终止后，当前策略会允许 root frame 处在很低的位置，后续若要约束离地间隙，应重新设计更物理的信号，而不是恢复原绝对阈值

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `2026-04-07_15-57-27` 是当前用户这组激进 reward/PPO 配置下第一轮恢复到健康 rollout 的 run。

下一步：
- 继续用回放确认：
  - 小车是否真实稳定跟踪，而不是靠很低的 root frame 姿态“贴地生存”
  - 若确实存在长期低车身姿态，后续应考虑改为更有物理意义的 clearance/relative-height 约束

已完成：
- 按用户决定从当前 Stage1 baseline 中移除 `root_too_low` termination。
- 实际修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - 删除 `TerminationsCfg.root_too_low`
- 保留不变：
  - `root_height_mean / root_height_min` 两个训练日志指标继续输出
  - 其余 termination 保留为：
    - `time_out`
    - `bad_orientation`
    - `ball_joint_out_of_bounds`
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前简单 Stage1 baseline 已不再使用 `root_too_low` 作为硬终止条件，避免尚未标定清楚的 root link 高度阈值直接主导训练结果。

下一步：
- 用相同训练命令重新跑一轮，重点看：
  - `time_out`
  - `bad_orientation`
  - `ball_joint_out_of_bounds`
  - `root_height_mean / root_height_min`
  是否出现更合理的 rollout 行为。

已完成：
- 诊断训练 run `2026-04-07_15-29-34` 的失败原因，并结合新加入的 root 高度日志确认本轮主问题不是启动或 PPO 数值崩溃，而是 `root_too_low` 终止几乎完全主导 rollout。
- 实际检查：
  - `/tmp/isaaclab/logs/isaaclab_2026-04-07_15-29-34.log`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-29-34/params/env.yaml`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-29-34/params/agent.yaml`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-29-34/tensorboard_export/summary.json`
  - `logs/rsl_rl/complete_car_rl_training/2026-04-07_15-29-34/tensorboard_export/scalars/*.csv`
- 关键结论：
  - 本轮训练已正常完成到 `model_999.pt`，不是启动失败。
  - 尾段指标显示：
    - `Episode_Termination/root_too_low = 1.0`
    - `Episode_Termination/time_out = 0.0`
    - `Train/mean_episode_length ≈ 10.57`
    - `Metrics/base_velocity/root_height_mean ≈ 0.242`
    - `Metrics/base_velocity/root_height_min ≈ 0.164`
  - 当前 `root_too_low.minimum_height = 0.15` 与 root link 实际高度工作带贴得过近，只剩约 `1.4 cm` 裕量；结合该终止项使用的是瞬时 root link 高度而非 COM，高度阈值 `0.15` 很可能就是本轮 rollout 被卡死的直接主因之一。
  - 同时也确认这轮实验并非只改了高度阈值，还叠加了更强的姿态/速度/球铰惩罚、更严格的 `45°` 姿态终止以及更激进的 PPO 配置，因此后续若要验证高度阈值，需要做单变量对比。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前对 `2026-04-07_15-29-34` 的最稳妥判断是：该 run 的主导失败模式是 `root_too_low`，而 `minimum_height = 0.15` 对当前 root link frame 很可能过高。

下一步：
- 若要验证这一判断，应只改 `root_too_low.minimum_height` 一项，再做新一轮对比训练。

已完成：
- 按用户在 Isaac Sim 地图预览中手动调整得到的新视角，更新 active task 默认 viewer 相机位姿。
- 已修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - `self.viewer.eye` 改为 `(-53.885, 43.696, 64.903)`
    - 新增 `self.viewer.lookat = (-53.054, 43.698, 64.346)`
- 已执行静态校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active task 在 GUI 下默认会从用户挑选后的地图总览视角打开，不再沿用原先的近距离默认视角。

下一步：
- 若还要继续调视角，可重复读取 `/OmniverseKit_Persp` 的 `eye/lookat` 后直接覆盖当前配置。

已完成：
- 按用户要求移除阶段 1 active task 中的底盘碰撞奖励，原因是当前真实小车默认不具备与该仿真 reward 对应的底盘接触传感输入。
- 已修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - 删除 `body_chassis_contact / head_chassis_contact / tail_chassis_contact` 三个 `ContactSensorCfg`
    - 删除 `RewardsCfg.chassis_collision`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`
    - 删除本地 `chassis_collision(...)` helper 与对应导出项
- 已执行静态校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前阶段 1 baseline 的 reward 集合已不再包含底盘碰撞项。
- 先前的底盘碰撞逻辑本质上是在用仿真 contact sensor 检测三个 chassis 与地面或其他物体的接触力是否超过阈值，主要约束的是“底盘擦地/砸地/撞障碍”这类行为，而不是轮地正常接触。
- 当前 active task 不再依赖这类仿真专用信号。

下一步：
- 重新做一次训练冒烟，重点观察移除底盘碰撞项后 episode 稳定性、姿态惩罚和终止项是否足够约束坏行为。

## 2026-04-06

已完成：
- 按用户要求将完整车训练项目中的仓库路径逻辑收敛为统一入口。
- 实际修改：
  - 新增 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/paths.py`
    - 统一提供 `PROJECT_ROOT`、`USD_DIR`、`RESULTS_DIR`、`COMPLETE_CAR_USD`
  - 修改 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
    - 不再本地拼接 `_THIS_FILE / _PROJECT_ROOT / _COMPLETE_CAR_USD`
    - 改为直接导入 `COMPLETE_CAR_USD`
  - 修改 `src/rl_lab/complete_car_rl_training/tools/ik/test_ik_keyboard.py`
    - 不再单独向上查找 `AGENTS.md`
    - 改为复用统一的 `COMPLETE_CAR_USD` 与 `RESULTS_DIR`
- 实际执行校验：
  - `rg -n "_THIS_FILE|PROJECT_ROOT = next\\(|AGENTS.md\\)\\.exists\\(" src/rl_lab/complete_car_rl_training -S`
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/paths.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py src/rl_lab/complete_car_rl_training/tools/ik/test_ik_keyboard.py`
- 结果：
  - 当前活跃训练项目中的路径逻辑已集中到一个模块维护
  - `complete_car_env_cfg.py` 与 IK 工具脚本不再重复各自写仓库根目录探测
  - 静态编译通过
  - 上述 `rg` 返回空结果，说明当前 `src/rl_lab/complete_car_rl_training/` 下已没有遗留的分散根目录探测写法

已完成：
- 按用户要求将训练环境 `stage1` 地形颜色进一步改为纯黑色。
- 实际修改：
  - `complete_car_stage1_terrain_env.py`
    - `STAGE1_TERRAIN_DIFFUSE_COLOR: (0.10, 0.10, 0.10) -> (0.0, 0.0, 0.0)`
- 保持不变：
  - 地形 mesh 几何
  - physics material
  - reset / curriculum / reward / observation / action 逻辑
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`

已完成：
- 按用户要求更新仓库级代码讲解规则，修改：
  - `AGENTS.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 已固化的新规则：
  - 以后讲解代码时默认不写完整绝对路径
  - 优先先讲脚本整体结构
  - 再按 import / 常量 / 类 / 函数 / 引用关系逐段、逐行分析
  - 默认按“用户 Python 基础较弱”的教学口径解释配置对象、函数引用与数据流
- 结果：
  - 后续会话中的代码教学风格已统一，不再重复口头约定

已完成：
- 按用户确认结果，进一步把“代码讲解的节奏、层次和内容把握方式”固化到仓库规则。
- 实际修改：
  - `AGENTS.md`
    - 新增“Preferred teaching rhythm for code walkthroughs”
    - 明确要求以后默认按以下顺序讲解：
      - 先说明脚本在系统中的角色
      - 再讲整体结构
      - 再按源码顺序逐块展开
      - 每块先讲作用，再讲关键代码行
      - 明确区分“引用/注册”和“真正执行逻辑”
      - 每个大块结束后重新接回 RL 主线
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 结果：
  - 用户认可的这套教学节奏已经从临时口头反馈升级为仓库级默认讲解规范

已完成：
- 按用户要求继续将训练环境 `stage1` 地形颜色调深，改为更偏黑的黑灰色，以提高和周围环境的对比度。
- 实际修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
    - `STAGE1_TERRAIN_DIFFUSE_COLOR: (0.18, 0.18, 0.18) -> (0.10, 0.10, 0.10)`
- 保持不变：
  - 地形 mesh 几何
  - physics material
  - reset / curriculum / reward / observation / action 逻辑
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`

已完成：
- 按用户要求将训练脚本与键盘控制脚本的默认运行语义统一到 GPU。
- 实际修改：
  - `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`
    - 未显式传 `--device` 时默认改为 `cuda:0`
  - `scripts/isaac_sim/control_keyboard.py`
    - `--help` 说明中明确写成默认走 Isaac Sim 的 GPU 路径
  - `src/rl_lab/complete_car_rl_training/docs/training_workflow_and_tensorboard_guide.md`
    - 默认训练命令、冒烟命令、回放命令统一改为 GPU 版
    - 键盘控制章节补充“默认走 GPU，不提供单独 CPU 模式”
  - `docs/current_status.md`
  - `docs/conversation_history.md`
- 实际执行校验：
  - `python src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py --help`
  - `python scripts/isaac_sim/control_keyboard.py --help`
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`
  - `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`
- 结果：
  - 当前仓库默认训练入口已切到 `cuda:0`
  - `control_keyboard.py` 的帮助信息已与 GPU 默认语义保持一致
- 额外说明：
  - 这次修改统一的是仓库默认行为，不代表当前机器的 NVIDIA driver / CUDA 环境已经恢复；本机若无可用 GPU，实际运行仍会受环境阻塞

已完成：
- 按用户要求修复 `scripts/isaac_sim/control_keyboard.py` 当前“无法打开”的仓库级问题。
- 排查结论：
  - `--terrain stage1` 使用的 `stage1_terrain.py` 本地路径写错，导致脚本走到对应分支时无法加载训练同源地形模块。
  - 脚本里同时还暴露了 `gap / stage2 / both` 等旧地形选项，但这些路径依赖的 `scripts/isaac_sim/terrain_preview/` 源码当前不在工作区中，已不属于可靠入口。
- 实际修改：
  - 修正 `scripts/isaac_sim/control_keyboard.py` 中 `STAGE1_TERRAIN_PATH`
  - 将 `--terrain` 选项收窄为 `none / stage1`
  - 默认地形改为 `none`
  - 删除对缺失 `terrain_preview` 模块的旧分支依赖
  - 同步更新 `src/rl_lab/complete_car_rl_training/docs/training_workflow_and_tensorboard_guide.md`、`docs/current_status.md`、`docs/conversation_history.md`
- 实际执行校验：
  - `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`
  - `python scripts/isaac_sim/control_keyboard.py --help`
  - `timeout 90s python -u scripts/isaac_sim/control_keyboard.py --terrain stage1 --headless --frames 1`
- 结果：
  - 脚本级过期路径和缺失模块问题已修复，当前文档与项目记忆也已统一到 `none / stage1` 这组真实支持范围。
  - 本机 headless smoke run 已能完成到 `Headless smoke validation finished successfully.`，说明 `stage1` 导入、机器人初始化、共享摩擦材质绑定与训练同构控制参数应用都能走通。
- 额外说明：
  - 当前这台机器仍无可用 NVIDIA driver / GPU，因此 Isaac Sim 交互窗口是否能真正弹出仍受运行环境限制；这部分不再属于本轮脚本代码错误。

已完成：
- 按用户要求新增训练操作说明文档：
  - `src/rl_lab/complete_car_rl_training/docs/training_workflow_and_tensorboard_guide.md`
- 文档已覆盖：
  - 训练脚本启动指令
  - TensorBoard 查看指令
  - 策略回放指令
  - 键盘控制脚本指令
  - 地形查看脚本指令
  - 本地结果保存位置
  - 核心 TensorBoard 图表的横纵轴、含义与好坏判断
- 已核对 `train.py --help`、`play.py --help`、`control_keyboard.py --help`，并修复 `preview_stage1_tile.py` 与 `preview_stage1_last_six.py` 中过期的 `stage1_terrain.py` 路径，使文档中的地形查看命令恢复可用。
- 修复 `env_isaacLab` 中 `tensorboard` 无法启动的问题。
- 现象：
  - 执行 `tensorboard --logdir ...` 时在 `tensorboard/default.py` 导入 `pkg_resources` 处报错
  - 当前环境中 `setuptools==82.0.1` 可导入 `setuptools`，但已无 `pkg_resources`
- 排查后确认：
  - 本机 conda 缓存已存在 `setuptools-80.10.2-py311h06a4308_0.conda`
  - 离线回退后 `pkg_resources` 恢复，`tensorboard --version` 可正常输出 `2.20.0`
- 实际执行：
  - `conda install -n env_isaacLab --offline -y /home/ubuntu/miniconda3/pkgs/setuptools-80.10.2-py311h06a4308_0.conda`
  - `tensorboard --version`
- 按用户要求将训练环境 `stage1` 地形显示颜色调整为黑灰色。
- 修改 `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`：
  - 为 `create_prim_from_mesh("/World/terrain/stage1", ...)` 增加显式视觉材质
  - 使用 `sim_utils.PreviewSurfaceCfg(diffuse_color=(0.18, 0.18, 0.18))`
- 保持原有 physics material、地形 mesh 几何、reset 和 curriculum 逻辑不变。
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
- 按用户要求清理 `src/` 训练脚本中的 `mgdp` 风格函数命名，重点处理：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1_terrain.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_env.py`
- 将地形 helper 和 mesh 偏移 helper 改为中性命名，并同步修正全部本地调用关系，例如：
  - `_mgdp_random_uniform_terrain -> _random_uniform_terrain`
  - `_maybe_add_mgdp_roughness -> _maybe_add_roughness`
  - `_offset_mesh_to_mgdp_frame -> _offset_mesh_to_stage1_frame`
- 本轮只改函数标识符，不改 terrain 生成逻辑、参数、课程分配或训练行为。
- 实际执行校验：
  - `rg -n "def .*mgdp|class .*mgdp|_mgdp|mgdp_" src`
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1_terrain.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_env.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/docs/training_workflow_and_tensorboard_guide.md`
- `scripts/isaac_sim/preview_stage1_tile.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1_terrain.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `src/` 活跃训练代码路径下，函数命名已去掉 `mgdp` 关联前缀。
- 本轮属于命名清理，不涉及行为变更；静态编译通过，且再次搜索未发现 `src/` 中残留的 `mgdp` 风格函数名。

下一步：
- 若还要继续统一命名风格，可再单独清理 `src/` 之外脚本目录中的 `mgdp` 文件名或注释，但这不属于本轮已执行范围。

已完成：
- 按用户要求整理 `stage1_terrain.py` 的代码结构，把公共 `make_*_tile` 地形生成函数整理成连续区块，并按 `terrain_dict` 中的地形顺序重新排列：
  - `flat`
  - `slope down`
  - `slope up`
  - `uneven rough`
  - `stairs down`
  - `stairs up`
  - `discrete obstacles`
  - `hurdle`
  - `gap`
  - `ramp`
  - `beam`
  - `new stairs down`
  - `pit`
- 为了让代码顺序和地形顺序一一对应，补了几个轻量包装函数：
  - `make_slope_down_tile`
  - `make_slope_up_tile`
  - `make_new_stairs_down_tile`
- 保持已有核心函数名不变，例如：
  - `make_pyramid_tile` 仍对应 `uneven rough`
  - `make_stairs_tile` 仍作为 `stairs down / stairs up / new stairs down` 的共享实现
- 顺手清理了同文件里几处格式不整齐的问题，但未改地形生成语义。
- 实际执行校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1_terrain.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1_terrain.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `stage1_terrain.py` 的公共地形生成函数阅读顺序已和配置顺序一致，后续查阅和维护会更直接。
- 本轮只做结构整理与可读性优化，不涉及课程分配、地形权重或 mesh 生成逻辑变化。

下一步：
- 若还要继续收敛结构，可再把 `make_tile_by_name` 改成显式的生成器注册表，但这属于后续重构，不是本轮已执行内容。

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

已完成：
- 新建根目录 `FK_iteration.m`，按用户给出的 Agile Eye 论文口径整理正运动学符号推导脚本。
- 在脚本中明确建立零位姿基座坐标系与平台坐标系，写入：
  - `u1,u2,u3`
  - `v1',v2',v3'`
  - `R = Rz(phi) * Ry(theta) * Rx(psi)`
  - `v_i` 展开式
  - `w_i` 表达式
  - `w_i^T v_i = 0` 三条标量约束
- 在脚本中继续补齐 forward kinematics 的两个分支推导：
  - `cos(theta)=0` 的 trivial branch
  - `phi=theta3` 的 nontrivial branch
  - `p1..p4`、行列式消元、`q1,q2`、`theta/psi` 主值解表达式
- 修正并显式说明第二条支链约束的符号问题：保留 `w2^T v2` 原始展开式，同时保留论文把方程两边同乘 `-1` 后得到的式(9c)写法，避免后续误判为推导错误。
- 用 `sympy` 对脚本对应的公式做了交叉核对，确认 `v_i` 展开、式(9b)(9c)(9d)、分支代回和式(17) 的等价关系都成立。
- 更新 `docs/current_status.md`、`docs/conversation_history.md`、`logs/daily_work_log.md` 与根 `README.md`，把这次正运动学推导脚本和关键结论写入项目记忆。

修改文件：
- `FK_iteration.m`
- `README.md`
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

产出/结论：
- 当前仓库已不再只有逆运动学推导工作区，根目录同时具备一份可直接查看的 Agile Eye 正运动学符号推导脚本。
- 正运动学脚本当前已经覆盖论文中从坐标系建立、向量约束、分支切分到非平凡解消元的主干推导。
- 第二条约束和论文式(9c)之间的差异仅是整体乘 `-1` 的等价变形，不属于模型或代码错误。
- 本轮尝试用本机 `matlab -batch` 做命令行验证，但当前终端里即使最小 `disp('hi')` 也会空退出且返回码为 `1`；因此本轮有效验证依据是 `sympy` 的符号等价检查，而不是 MATLAB 命令行输出。

下一步：
- 若用户继续推进，可把 `FK_iteration.m` 中已经固化的符号结果同步整理进论文 `chapter03.tex` 的“正运动学模型”小节，或继续补 rotation matrix 形式的 trivial solutions 输出。

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

## 2026-04-06

已完成：
- 按用户要求重新规划当前 RL 第一阶段任务定义，不再沿用此前“固定球铰、仅训练轮速”的阶段划分。
- 将新的第一阶段方案同步写入项目规划相关文件，使后续讨论与实现都以这版为默认：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `README.md`
  - `src/rl_lab/complete_car_rl_training/docs/rl_training_route.md`
- 当前新的第一阶段定义已明确为：
  - 观测：基座线速度、基座角速度、重力投影、6 个球铰关节位置、6 个球铰关节速度、6 个轮速、速度命令、上一时刻动作
  - 动作：6 个球铰关节位置目标 + 6 个车轮速度目标
  - 控制语义：球铰走位置目标、车轮走速度目标，沿用现有关节驱动 / `PD` 控制链
  - 奖励：线速度跟踪、角速度跟踪、车体姿态稳定、`lin_vel_z` 惩罚、`ang_vel_xy` 惩罚、动作变化惩罚、球铰偏离中位或过激摆动惩罚、碰撞惩罚、终止惩罚
  - 地形：继续使用当前 `stage1` terrain，第 1 列为 `flat`，其余列保留不同地形类型，但训练默认使用最低难度，使其接近平地
  - 当前阶段不加入外部地形感知

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `README.md`
- `src/rl_lab/complete_car_rl_training/docs/rl_training_route.md`
- `logs/daily_work_log.md`

产出/结论：
- 项目当前默认阶段规划已经切换到“球铰与车轮联合控制的第一阶段 baseline”。
- 旧的“固定球铰 + 轮速控制”阶段定义仅保留为历史讨论背景，不再作为当前默认实现目标。

下一步：
- 按这版阶段 1 规划，开始回写 `complete_car_env_cfg.py`、`mdp/observations.py`、`mdp/rewards.py` 和 `complete_car_stage1_env.py` 的任务定义与训练逻辑。

## 2026-04-06

已完成：
- 用户进一步收紧第一阶段地形范围，明确当前阶段不再采用“低难度混合地形 baseline”，而改为 `flat-only baseline`。
- 已将这一新决策同步写回：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `README.md`
  - `src/rl_lab/complete_car_rl_training/docs/rl_training_route.md`
- 当前第一阶段新的地形约束已明确为：
  - 训练默认只使用 `flat` 地形
  - 现有 `stage1` terrain 保留，但仅作为后续非平地阶段或对照实验入口
  - 其余 observation / action / reward 规划保持不变

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `README.md`
- `src/rl_lab/complete_car_rl_training/docs/rl_training_route.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前项目里的阶段 1 已正式收敛为 `flat-only` 基础运动策略 baseline。
- “低难度混合地形”不再是当前默认训练分布。

下一步：
- 按 `flat-only baseline` 去修改活跃任务代码里的 observation / action / reward / terrain 使用逻辑。

## 2026-04-06

已完成：
- 按用户要求重构地形运行时职责分层，不再让旧 `complete_car_stage1_env.py` 同时混着持有 terrain runtime、课程学习更新和 spawn/reset 偏移逻辑。
- 已将原文件重命名为：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
- 类名同步改为：
  - `CompleteCarStage1TerrainEnv`
- 当前新的 terrain runtime env 只保留：
  - stage1 地形 mesh 导入
  - terrain runtime state 缓存
  - env origin 同步
  - reset 时对 `mdp.curriculums` 和 `mdp.events` 的调用
- 已将 terrain curriculum 更新逻辑移到：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py`
  - 新增 `update_stage1_terrain_curriculum(...)`
- 已将 spawn/reset 偏移逻辑移到：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/events.py`
  - 新增 `apply_stage1_spawn_offsets(...)`
- 已同步修改任务注册入口：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/__init__.py`
  - 当前 `Complete-Car-Rl-Training-v0` 已指向新的 `complete_car_stage1_terrain_env:CompleteCarStage1TerrainEnv`
- 已执行静态校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/events.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/__init__.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/events.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/__init__.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 terrain runtime env 的职责已经明显收缩，后续阅读和扩展不需要再从一个大杂烩文件里同时找地形导入、课程学习和 spawn/reset 规则。
- 课程学习规则与 spawn/reset 偏移规则现在已经各自有明确落点。

下一步：
- 继续处理 terrain 接入方式本身，尤其是默认 plane 与自定义 stage1 mesh 的结构关系，以及 `flat-only baseline` 下的实际训练场景切换。

## 2026-04-06

已完成：
- 继续按用户要求收干 terrain 接入方式，不再让 active task 通过 `TerrainImporterCfg(terrain_type="plane")` 先创建默认 plane 再删除。
- 已修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
  - `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
- 当前 `CompleteCarRlTrainingSceneCfg` 已去掉默认 terrain 配置，scene 启动时不再自动生成 plane。
- 当前 `CompleteCarStage1TerrainEnv` 会在运行时直接使用：
  - `isaaclab.terrains.utils.create_prim_from_mesh`
  将 stage1 生成的 trimesh 导入到：
  - `/World/terrain/stage1`
- 当前 `scene.env_origins` 由 terrain runtime env 直接维护，不再依赖 `scene.terrain.configure_env_origins(...)`。
- 同步把 `export_training_stage.py` 改成兼容 `scene.terrain is None` 的情况，避免导出脚本再假定 scene 一定带 terrain importer。
- 已执行静态校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
- `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active task 的 terrain 接入已经不再依赖“默认 plane + 删除”的补丁式流程。
- stage1 terrain 现在是直接导入的单个 trimesh，结构上更符合“场景里只有这一种地形”的要求。

下一步：
- 继续明确 `flat-only baseline` 是否直接复用该 terrain runtime env，还是单独做一个更薄的平地训练入口。

## 2026-04-06

已完成：
- 按用户要求在 active task 中新增“只在 `flat` 列 reset”的功能，但未删除原有 mixed-terrain 所需的 terrain runtime 结构。
- 已修改：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py`
- 当前 `Stage1RuntimeCfg` 新增并默认启用：
  - `flat_only_reset=True`
- 当前 `CompleteCarStage1TerrainEnv` 在 `flat_only_reset=True` 时会把所有 env 的 `terrain_type` 固定到 `flat` 对应列，其余 terrain runtime 逻辑保持可复用。
- 当前 terrain curriculum 保留为可开关功能，并默认关闭：
  - `Stage1RuntimeCfg.curriculum=False`
- 已把阶段 1 的 observation / action / reward 正式写回 active task：
  - `complete_car_env_cfg.py` 中 observation 顺序已对齐为：基座线速度、基座角速度、重力投影、球铰位置、球铰速度、轮速、速度命令、上一时刻动作
  - action 维持为：6 个球铰位置目标 + 6 个车轮速度目标
  - reward 改为：线速度跟踪、角速度跟踪、姿态稳定、`lin_vel_z`、`ang_vel_xy`、动作变化、球铰偏离、球铰摆动、碰撞、终止
- 已把 `ang_vel_z` 命令范围从固定 `0` 改为可采样，避免角速度跟踪奖励失效。
- 已在 scene 中增加 3 个 chassis contact sensor，并在：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`
  中新增 `chassis_collision(...)` 奖励函数。
- 已执行静态校验：
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前阶段 1 的默认 active task 已不再只是规划，而是已经真正切到 `flat-only baseline` 的 reset / command / reward / collision 逻辑。
- mixed-terrain 训练路径没有被删除，后续恢复时只需调整 runtime 配置开关。

下一步：
- 用新的阶段 1 配置做一次实际训练冒烟，确认 `flat-only reset`、contact reward 和 `ang_vel_z` 命令生效情况。

## 2026-04-06

已完成：
- 按用户要求将当前整个项目工作区上传到 GitHub。
- 已先把以下内容加入 `.gitignore`，未纳入本次提交：
  - `.obsidian/`
  - `.codex`
- 已对整个当前工作区执行：
  - `git add -A`
  - `git commit -m "upload current project state"`
  - `git push origin main`
- 推送结果：
  - 本地 `main` 已成功推送到 `origin/main`
  - 最新提交为：`2a9cfeb upload current project state`

修改文件：
- `.gitignore`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前本地代码与 GitHub 远程主分支已同步。
- `.obsidian` 与 `.codex` 已从版本管理范围排除，后续不会再被误提交。

下一步：
- 若继续推进训练主线，直接基于当前 `origin/main` 的 `2a9cfeb` 开始即可。

## 2026-04-07

已完成：
- 根据训练控制台 traceback 查明本轮启动失败不是 GPU、不是场景构建、也不是机器人配置解析失败，而是 `rsl_rl` 在创建 `OnPolicyRunner` 时无法解析 observation group。
- 已在：
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/agents/rsl_rl_ppo_cfg.py`
  中补充：
  - `obs_groups = {"actor": ["FlatBaseline"], "critic": ["FlatBaseline"]}`
- 当前修正逻辑为：
  - actor 使用环境唯一观测组 `FlatBaseline`
  - critic 同样使用 `FlatBaseline`
- 已同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/agents/rsl_rl_ppo_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 本轮训练启动失败的直接原因已定位为 `obs_groups` 缺失，而非 active task 本身的 observation / reward / termination 配置错误。
- 当前项目在使用自定义 observation group 名时，PPO 配置必须显式声明 `obs_groups`，不能再依赖旧版本的隐式推断。

下一步：
- 重新启动训练，确认是否已越过 `OnPolicyRunner` 初始化阶段，并继续观察首轮 rollout 是否稳定。

## 2026-04-07

已完成：
- 对比分析训练 run：
  - `2026-04-07_12-25-02`
  - `2026-04-06_21-59-12`
- 已补导出旧 run 的 TensorBoard 标量：
  - `src/rl_lab/complete_car_rl_training/logs/rsl_rl/complete_car_rl_training/2026-04-06_21-59-12/tensorboard_export`
- 已确认新 run 变差不能归因于移除 `chassis_collision`：
  - 旧 run 的 `Episode_Reward/chassis_collision` 到结束都为 `0.0`
- 已确认新 run 虽然绝对 episode length 更长，但这是在 `episode_length_s: 8 -> 16` 的前提下发生，不能直接视为更好
- 已确认新 run 的核心跟踪能力明显下降：
  - `Train/mean_reward`: `2.97 -> 1.32`（对比旧 run 末值）
  - `error_vel_xy`: `1.29 -> 3.79`
  - `error_vel_yaw`: `1.76 -> 3.91`
- 已识别这两个 run 之间除 collision reward 外的其他关键变化：
  - `wheel_joints.damping: 10.0 -> 1e4`
  - `ball_joints.stiffness/damping: 80/8 -> 100/10`
  - `lin_vel_x` 命令范围：`[-1, 1] -> [-2, 2]`
  - `episode_length_s: 8 -> 16`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前“原地打转、看起来轮胎不触地”的回放现象，与标量诊断一致地对应“存活优先、跟踪变差”的局部最优。
- 仅凭当前标量不能证明轮胎真的离地；当前能确认的是策略没有学好速度跟踪。
- 若要继续定位主因，后续训练不能再把 reward、actuator、命令范围、episode 时长一起改动。

下一步：
- 用单变量回归方式继续对比，优先先回退 `wheel_joints.damping`，再回退 `lin_vel_x` 命令范围，最后再恢复 `episode_length_s=8` 做公平对比。

## 2026-04-07

已完成：
- 诊断训练 run：
  - `2026-04-07_13-13-46`
- 已确认本次实际使用配置为：
  - `wheel_joints.damping = 1000.0`
  - `num_envs = 512`
  - `max_iterations = 400`
  - `track_lin_vel_xy.std = 1.0`
- 与上一轮 `2026-04-07_12-53-43` 相比，本次出现明显改进：
  - `Train/mean_reward: 5.90 -> 26.43`
  - `Train/mean_episode_length: 741.56 -> 880.97`
  - `error_vel_xy: 3.52 -> 0.71`
  - `error_vel_yaw: 4.32 -> 1.95`
- 当前尾段状态：
  - `time_out ≈ 0.754`
  - `root_too_low ≈ 0.182`
  - `ball_joint_out_of_bounds ≈ 0.064`
- 结论：
  - 当前 baseline 已经从“只会活着”的阶段，进入“线速度跟踪明显有效、yaw 跟踪仍偏弱”的阶段
  - 该 run 已可作为当前阶段的默认 baseline 参考点

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `wheel damping = 1e3 + 512 envs + 400 iterations` 是当前更合适的 baseline 训练规模。
- 下一步不应再大范围改 baseline 结构，而应围绕 yaw 跟踪和非 timeout 终止继续做小幅调整。

下一步：
- 在当前 baseline 附近只做小改，优先减小 `root_too_low` 和 `ball_joint_out_of_bounds`，并继续观察 yaw tracking 是否能进一步提升。

## 2026-04-07

已完成：
- 对比分析训练 run：
  - `2026-04-07_13-13-46`
  - `2026-04-07_13-32-34`
- 已确认这两次 run 的关键差异仅为：
  - `track_ang_vel_z.weight: 0.5 -> 2.0`
- 对比结果：
  - yaw 跟踪显著改善：
    - `error_vel_yaw: 1.95 -> 0.88`
  - 线速度跟踪轻微变差：
    - `error_vel_xy: 0.71 -> 0.83`
  - 存活与失败分布几乎不变：
    - `time_out` 基本持平
    - `root_too_low` 基本持平
    - `ball_joint_out_of_bounds` 基本持平
- 已确认 `Train/mean_reward` 大幅上升不能直接当作“整体更好”的证据，因为这次直接把 yaw reward 权重提高到了原来的 4 倍。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- yaw 权重提到 `2.0` 的效果是“更会转向”，但代价是牺牲部分线速度跟踪，而且没有明显改善生存率。
- 对当前简单 baseline 来说，`track_ang_vel_z.weight = 2.0` 偏强，不适合作为默认最终配置。

下一步：
- 在保持其余配置不变的前提下，优先试 `track_ang_vel_z.weight = 1.0` 或 `1.5`，找线速度与 yaw 的折中点。

## 2026-04-07

已完成：
- 对比分析训练 run：
  - `2026-04-07_13-32-34`
  - `2026-04-07_13-41-53`
- 已确认这两次 run 的关键差异仅为：
  - `track_ang_vel_z.weight: 2.0 -> 1.5`
- 对比结果：
  - 线速度误差改善：
    - `error_vel_xy: 0.83 -> 0.68`
  - yaw 误差基本不变：
    - `error_vel_yaw: 0.88 -> 0.89`
  - 存活与失败分布变差：
    - `time_out: 0.76 -> 0.68`
    - `root_too_low` 变高
    - `ball_joint_out_of_bounds` 变高

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- yaw 权重从 `2.0` 降到 `1.5` 后，并没有带来更平衡的 baseline。
- 当前在这两次之间，`2026-04-07_13-32-34` 仍然是更好的 baseline 候选。

下一步：
- 若继续收敛 baseline，不应再优先调 yaw 权重；更应围绕 `root_too_low` 和 `ball_joint_out_of_bounds` 的失败模式做小幅调整。

## 2026-04-07

已完成：
- 在用户授权下，首次以沙箱外 GPU 方式直接运行完整车 Stage1 baseline 训练，确认 `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --num_envs 512 --max_iterations 400 --headless` 可稳定使用 `cuda:0`。
- 基于 `2026-04-07_13-32-34` 连续完成 3 轮直接调参与实跑：
  - `2026-04-07_13-56-35`
  - `2026-04-07_14-02-02`
  - `2026-04-07_14-06-10`
- 已完成这 3 次 run 与 `2026-04-07_13-32-34` 的结果对比，并把当前默认 baseline 收敛回 `13-32-34`。

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `2026-04-07_13-32-34` 仍是今天最均衡的阶段 1 baseline：
  - `mean_reward = 41.21`
  - `mean_episode_length = 841.79`
  - `error_vel_xy = 0.834`
  - `error_vel_yaw = 0.880`
  - `time_out = 0.757`
  - `root_too_low = 0.176`
  - `ball_joint_out_of_bounds = 0.066`
- 以下 3 个直接后续调参方向均未优于 `13-32-34`：
  - 收紧 reset 扰动并减小球铰动作幅度
  - 增大 `ball_joint_deviation`
  - 增大 `termination`
- 已确认此前 Codex 不能直接启用 GPU 的主因是沙箱权限，而不是这台机器本身不能运行 `cuda:0`。

下一步：
- 当前默认继续以 `13-32-34` 作为阶段 1 baseline。
- 若后续继续调参，不再优先重复今天已验证失败的 4 个方向，应提出新的物理假设后再试。

## 2026-04-07

已完成：
- 记录当前用户手动调参版本的关键参数变化，覆盖：
  - `complete_car_env_cfg.py`
  - `rsl_rl_ppo_cfg.py`
- 按用户要求取消当前阶段的球铰 reset 扰动：
  - `reset_ball_joints.position_range -> (0.0, 0.0)`
  - `reset_ball_joints.velocity_range -> (0.0, 0.0)`
- 已对当前 `complete_car_env_cfg.py` 与 `rsl_rl_ppo_cfg.py` 做 `py_compile` 静态校验，结果通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前用户手动调参版本相对先前 baseline 的关键变化包括：
  - reward/termination 约束明显增强
  - PPO rollout、网络规模和学习率明显增大
- 当前阶段不再保留球铰初始随机扰动，后续若要测试鲁棒性再单独恢复。

下一步：
- 若继续用当前手动调参版本训练，应优先先做一轮新的 run，判断“更强稳定性约束 + 更大 PPO 配置”是否仍能保持速度跟踪主目标。

## 2026-04-07

已完成：
- 新增训练过程中的 root 高度日志功能。
- 在 `mdp/commands.py` 中为当前 `base_velocity` 命令项添加了两项额外 metric：
  - `Metrics/base_velocity/root_height_mean`
  - `Metrics/base_velocity/root_height_min`
- 已确认当前 `root_too_low` 使用的 `root_pos_w` 语义是 articulation root link 的 actor frame 高度，而不是 COM 高度。

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/commands.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 后续训练后可以直接通过 root 高度均值和最低值判断 `root_too_low.minimum_height = 0.15` 是否合适。
- 当前 `root_too_low` 不是在看小车质心高度，而是在看 root link frame 的世界坐标 `z`。

下一步：
- 跑下一轮训练后，优先联动查看：
  - `Metrics/base_velocity/root_height_mean`
  - `Metrics/base_velocity/root_height_min`
  - `Episode_Termination/root_too_low`

## 2026-04-08

已完成：
- 按用户要求重构 Isaac Lab RL 训练目录，去掉旧的单体 `complete_car_env_cfg.py` 方案，改成可分阶段继承的 `common/ + stage1/` 架构。
- 新增通用模板层：
  - `common/base_env_cfg.py`
  - `common/agents/base_rsl_rl_ppo_cfg.py`
  - `common/robot_cfg.py`
  - `common/scene_cfg.py`
  - `common/mdp/`
- 将当前 Stage1 独立成子包：
  - `stage1/stage1_env_cfg.py`
  - `stage1/stage1_env.py`
  - `stage1/stage1_terrain.py`
  - `stage1/mdp/`
  - `stage1/agents/rsl_rl_ppo_cfg.py`
- 删除旧的顶层 Stage1 单体入口和旧 `mdp/`、旧 `agents/`。
- 已同步修改 `preview_stage1_terrain.py`、`preview_stage1_tile.py`、`preview_stage1_last_six.py`、`control_keyboard.py`，让它们全部从新的 `stage1/stage1_terrain.py` 取训练同源地形。
- 已执行一次 Python 语法级验证，确认新结构下主要任务文件与受影响脚本均可通过 `py_compile`。

修改文件：
- `scripts/isaac_sim/control_keyboard.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `scripts/isaac_sim/preview_stage1_tile.py`
- `src/rl_lab/complete_car_rl_training/README.md`
- `README.md`
- `docs/project_file_map.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/__init__.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/common/__init__.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/common/base_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/common/agents/__init__.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/common/agents/base_rsl_rl_ppo_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1/stage1_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1/stage1_env.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1/stage1_terrain.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1/agents/rsl_rl_ppo_cfg.py`

产出/结论：
- 当前 RL 训练代码已经从“一个 Stage1 大配置文件不断改写”的模式，切到“通用模板 + 分阶段子包”的模式。
- 这次重构保留了 manager-based 框架负责的生命周期，不再模仿 MGDP 去重写 `base_task` 一类的底层骨架；真正被迁移的是“分阶段组织和配置继承思想”。
- 后续如果进入 Stage2 / Stage3，应新增同级子包，而不是重新把感知、地形、课程学习继续塞回 Stage1 配置文件。

下一步：
- 在新结构下重新执行一轮 `train.py` smoke test，确认 Gym 注册、Hydra 配置入口和日志输出都正常。

已完成：
- 检查用户本轮大规模目录整理后的实际仓库状态，确认 RL 主线已从旧的 `src/rl_lab/complete_car_rl_training/` 迁移到新的 `RL_Training/`。
- 修复会直接影响训练启动的旧导入路径问题：
  - `RL_Training/scripts/list_envs.py`
  - `RL_Training/scripts/zero_agent.py`
  - `RL_Training/scripts/random_agent.py`
  - `RL_Training/scripts/export_training_stage.py`
  - `RL_Training/scripts/rsl_rl/train.py`
  - `RL_Training/scripts/rsl_rl/play.py`
  上述脚本原本仍写 `import complete_car_rl_training.tasks`，当前已统一改为直接导入包根 `import complete_car_rl_training`。
- 修复仓库根目录 Isaac Sim 脚本对旧包结构和旧项目根的引用：
  - `scripts/isaac_sim/preview_stage1_terrain.py`
  - `scripts/isaac_sim/preview_stage1_tile.py`
  - `scripts/isaac_sim/preview_stage1_last_six.py`
  - `scripts/isaac_sim/control_keyboard.py`
  当前已统一改为从 `RL_Training/complete_car_rl_training/common/` 与 `RL_Training/complete_car_rl_training/stage1/` 读取配置与地形。
- 同步更新了根 README、当前状态、项目文件地图和 `RL_Training/README.md`，把默认主线入口改到 `RL_Training/`。
- 对 `RL_Training` 主包、训练脚本和受影响的 Isaac Sim 脚本执行了 `python3 -m py_compile`，静态检查通过。

修改文件：
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `docs/project_file_map.md`
- `logs/daily_work_log.md`
- `RL_Training/README.md`
- `RL_Training/docs/training_workflow_and_tensorboard_guide.md`
- `RL_Training/scripts/list_envs.py`
- `RL_Training/scripts/zero_agent.py`
- `RL_Training/scripts/random_agent.py`
- `RL_Training/scripts/export_training_stage.py`
- `RL_Training/scripts/rsl_rl/train.py`
- `RL_Training/scripts/rsl_rl/play.py`
- `scripts/isaac_sim/preview_stage1_terrain.py`
- `scripts/isaac_sim/preview_stage1_tile.py`
- `scripts/isaac_sim/preview_stage1_last_six.py`
- `scripts/isaac_sim/control_keyboard.py`

产出/结论：
- 当前真正会导致训练或注册失败的代码级问题已经定位并修正，核心问题是“主线目录已经迁移，但脚本仍引用旧包入口和旧文件路径”。
- 当前剩余未完成的是运行态冒烟，而不是静态路径修正。

下一步：
- 在 `env_isaacLab` 中进入 `RL_Training/` 后，优先执行一次 `python scripts/list_envs.py --keyword Complete-Car` 或小规模 `train.py` 冒烟。

## 2026-04-10

已完成：
- 以 `complete_car_env_cfg.py` 为入口，对当前 direct complete-car 主线完成一轮结构性迁移。
- command 维度由旧设计改为 4 维：
  - `lin_vel_x`
  - `lin_vel_y`
  - `ang_vel_yaw`
  - `heading`
- policy action 改为仅输出 6 个球铰姿态关节目标角，不再把车轮速度作为 policy action 输出。
- 在 `complete_car_env.py` 中新增 env 侧车轮驱动映射：按 command 派生左右轮速度目标，避免 6 维 action 后训练主线失去前进驱动。
- policy observation 重构为以姿态角和姿态角变化率为主的最小本体输入，并删除旧的：
  - `lin_vel`
  - `projected_gravity`
  - `wheel_joint_vel`
  - `height_measurements`
  这些旧主线项不再进入 policy observation。
- 当前基础 observation 拼接顺序改为：
  - `roll, pitch, yaw`
  - `roll_rate, pitch_rate, yaw_rate`
  - `ball_joint_pos(6)`
  - `ball_joint_vel(6)`
  - `commands(4)`
  - `last_action(6)`
  当前基础 observation 总维度为 `28`。
- 新增本地速度跟踪 reward kernel：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/local_velocity_tracking_reward.py`
  并在 `rewards.py` 中组合本地 tracking、heading、姿态惩罚、关节惩罚、action-rate 惩罚。
- 新增本地 PPO 配置副本：
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents/local_rsl_rl_cfg.py`
  `ppo_cfg.py` 不再直接继承外部 `RslRlOnPolicyRunnerCfg / RslRlPpoActorCriticCfg / RslRlPpoAlgorithmCfg`。
- 当前 PPO 配置同步改成 `actor / critic / distribution_cfg` 结构，以适配当前机器上的 `rsl-rl-lib 5.0.1`。
- 对本轮涉及的 direct-task 文件执行了 `python3 -m py_compile`，静态语法检查通过。

修改文件：
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/assets/robot_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/commands.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/observations.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/utils.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/rewards.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/local_velocity_tracking_reward.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents/local_rsl_rl_cfg.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents/ppo_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 direct 主线的动作、命令、观测、reward、PPO 配置已经切到新的结构，不再停留在旧的 12 维动作和旧 observation 语义上。
- 这次改动的关键不是“单纯减 action 维度”，而是同步补上了 env 侧车轮驱动闭环，使 6 维姿态动作仍然具备速度跟踪训练所需的推进能力。
- 当前仍缺少真实 Isaac Lab 运行态验证；下一步最应该先验证的是 Stage0 下新的 wheel-drive 映射和 28 维 observation 是否按预期工作。

下一步：
- 在 Isaac Lab 环境中优先运行 `python scripts/list_envs.py --keyword Complete-Car`。
- 然后对 `Complete-Car-Stage0-Flat-Direct-v0` 做一次小规模 `train.py` 冒烟，重点检查 action space、observation dim 和车轮驱动效果。

已完成：
- 按用户新要求修改 `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex` 中“整车运动学速度雅可比分析”对应正文。
- 本轮没有采用远端那种整段重写方式，而是在尽量保留当前正文叙述结构的前提下，只对涉及侧模块固定偏置的部分做不对称改写。
- 将原先共用单一 `\mathbf b` 的位置关系改为分别使用：
  - `${}^{1}\mathbf b_1`
  - `${}^{3}\mathbf b_3`
- 同步改写并校正了以下链条中的对应公式：
  - 前后模块参考点位置表达
  - 前后模块线速度传播
  - `\mathbf K_1(\mathbf q)`、`\mathbf K_3(\mathbf q)`
  - 前后轮对应的行雅可比显式展开
- 轮心位置向量与单模块轮速矩阵 `\mathbf H_i` 本轮仍保留原有符号化模板写法，没有切换成整段实测参数直代版正文。
- 在 `毕业论文/毕业论文模板/LaTeX/` 下执行：
  - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
  编译通过，`main.pdf` 已重新生成。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `毕业论文/毕业论文模板/LaTeX/main.pdf`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `chapter03` 正文已经从“统一侧模块偏置 `\mathbf b`”切到“前后固定偏置分开建模”的写法。
- 本轮采取的是最小侵入式正文修订，而不是整段换成新的远端版本。
- 当前论文仍只保留 2 条旧的非阻塞文献警告：
  - `fang2015survey`
  - `MATSUMURA2017566`

下一步：
- 如果还要继续打磨 chapter03，下一轮应优先检查各段文字对 `${}^{1}\mathbf b_1` 与 `${}^{3}\mathbf b_3` 的物理意义解释是否还可再压缩得更清楚，而不是再大范围重写正文结构。

已完成：
- 按用户新的严格修订要求，再次处理 `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex` 中“整车运动学速度雅可比分析”对应正文。
- 本轮仍坚持“不推翻原推导框架、不整体重写正文”，仅在原有主线内修正符号冲突、几何定义和物理表述。
- 已将车轮角速度符号从：
  - `\dot\phi_{iL}, \dot\phi_{iR}`
  统一改为：
  - `\Omega_{iL}, \Omega_{iR}`
  并同步修改相关文字、轮速向量与整车雅可比表达。
- 已将连接向量明确为：
  - `${}^{2}\mathbf a=[a_x,0,0]^T`
  同时把正文中的“对称结构”表述收紧为“前后连接中心沿 `x_2` 轴镜像分布”。
- 已将 `${}^{2}\mathbf v_c`、`${}^{2}\boldsymbol\omega_c` 的物理定义统一改为：
  - 主模块瞬时刚体速度
  - 运动学分析中的广义速度描述
  不再称为“运动指令”。
- 已将“纯滚动约束”相关措辞统一改为“基于滚动方向无滑移条件”的轮速映射表述，并补充说明这里只使用了滚动方向速度关系，没有完整展开侧向无滑移约束。
- 已补充车轮角速度正方向约定，并在欧拉角速度映射处补充参数奇异性说明。
- 在 `毕业论文/毕业论文模板/LaTeX/` 下再次执行：
  - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
  编译通过，`main.pdf` 已重新生成。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `毕业论文/毕业论文模板/LaTeX/main.pdf`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `chapter03` 中“整车运动学速度雅可比分析”这一节已经在保留原推导主线的前提下完成一轮更严格的学术化修订。
- 当前该节的关键符号、几何定义和物理表述已经与“不对称固定偏置 + 主模块瞬时刚体速度 + 滚动方向轮速映射”的写法保持一致。
- 当前论文仍只保留 2 条旧的非阻塞文献警告：
  - `fang2015survey`
  - `MATSUMURA2017566`

下一步：
- 若继续修改 chapter03，后续应优先做局部措辞压缩和版面整理，不再回退这套已经统一好的符号与物理定义。

已完成：
- 基于论文最终采用的真实参数与整车速度雅可比矩阵，新增独立轮速分配模块：
  - `RL_Training/kinematics/wheel_speed_allocator.py`
- 同步新增：
  - `RL_Training/kinematics/__init__.py`
  - `RL_Training/scripts/validate_wheel_speed_allocator.py`
- 新分配器内部已固定使用真实几何参数：
  - `a`
  - `b1`
  - `b3`
  - 三个模块左右轮轮心位置
  - `r_wheel`
- 新分配器同时提供：
  - `numpy` 验证接口
  - `torch` 运行接口
- 新分配器显式构造：
  - `\mathbf K_1(\mathbf q), \mathbf K_2, \mathbf K_3(\mathbf q)`
  - 实测参数版 `\mathbf H_i`
  - 整车 Jacobian `\mathbf J_w(\mathbf q)`
  并将论文中的前-中-后轮速顺序重排为仿真实际 joint 顺序：
  - `body_car_wheel_left_joint`
  - `body_car_wheel_right_joint`
  - `head_car_wheel_left_joint`
  - `head_car_wheel_right_joint`
  - `tail_car_wheel_left_joint`
  - `tail_car_wheel_right_joint`
- 已将 direct env 中旧的经验缩放轮速逻辑删除，改为在每步根据：
  - 当前 6 个球铰关节角
  - 当前 6 个球铰关节角速度
  - RL command 中的 `lin_vel_x / lin_vel_y / ang_vel_yaw`
  通过 Jacobian 分配器生成 6 维 wheel target。
- 已删除旧控制参数：
  - `wheel_drive_lin_vel_scale`
  - `wheel_drive_yaw_rate_scale`
  因为它们已不再符合当前轮速分配语义。
- 已在 `RL_Training/` 下执行：
  - `python3 scripts/validate_wheel_speed_allocator.py`
  基础数值检查通过，覆盖：
  - 零输入
  - 纯前进
  - 纯偏航
- 已执行：
  - `python3 -m py_compile RL_Training/kinematics/__init__.py RL_Training/kinematics/wheel_speed_allocator.py RL_Training/scripts/validate_wheel_speed_allocator.py RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
  静态语法检查通过。

修改文件：
- `RL_Training/kinematics/__init__.py`
- `RL_Training/kinematics/wheel_speed_allocator.py`
- `RL_Training/scripts/validate_wheel_speed_allocator.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
- `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 RL 主线已经从“经验缩放差速轮速”切到“真实参数 Jacobian 轮速分配”。
- 当前轮速分配模块既可以独立验证论文模型，也可以直接作为 Isaac Lab env 的 wheel target 生成器。
- 当前 `heading` command 仍保留给高层任务语义，但不直接进入瞬时轮速 Jacobian 映射。

下一步：
- 在真实 Isaac Lab 环境中优先验证新 allocator 接入后 Stage0 的前进、转向与速度跟踪 reward 是否一致。

## 2026-04-10

已完成：
- 按用户要求先以 GitHub 为准同步本地：
  - 发现 `origin/main` 已被强制更新，无法 fast-forward
  - 已将本地 `main` 直接重置到 `origin/main`
  - 当前同步基线为 `97ca6b6`
- 将当前环境中的 `rsl_rl` 实现整包 vendoring 到项目本地：
  - `RL_Training/rsl_rl/`
- 当前 vendored 包已包含训练主线实际会用到的实现链：
  - `runners/on_policy_runner.py`
  - `algorithms/ppo.py`
  - `models/mlp_model.py`
  - `storage/rollout_storage.py`
  - `modules/distribution.py`
  - `modules/mlp.py`
  - `modules/normalization.py`
  - `utils/logger.py`
  - 以及其余闭环依赖文件
- 修改 `RL_Training/scripts/rsl_rl/train.py` 与 `play.py`：
  - 在脚本启动时将 `RL_Training/` 项目根路径插入 `sys.path`
  - 让训练/回放优先导入仓库内 `RL_Training/rsl_rl/`
  - 不再把外部 `rsl-rl-lib` 的 metadata 版本当作当前实现本体来源
- 修改 `RL_Training/rsl_rl/__init__.py`：
  - 增加本地版本标记 `5.0.1-local`
- 修改 `RL_Training/setup.py`：
  - 将 `rsl_rl`、`rsl_rl.*` 纳入 editable install 的打包范围
  - 补充 `GitPython`、`tensordict`、`tensorboard` 依赖声明
- 更新 `README.md` 与 `RL_Training/README.md`，把 vendored `rsl_rl/` 明确记为当前训练主线的一部分。
- 执行：
  - `python3 -m compileall RL_Training/rsl_rl RL_Training/scripts/rsl_rl RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents`
  编译通过。
- 额外做了直接导入校验，确认当前解析到的是仓库内文件：
  - `OnPolicyRunner -> RL_Training/rsl_rl/runners/on_policy_runner.py`
  - `PPO -> RL_Training/rsl_rl/algorithms/ppo.py`
  - `MLPModel -> RL_Training/rsl_rl/models/mlp_model.py`

修改文件：
- `README.md`
- `RL_Training/README.md`
- `RL_Training/setup.py`
- `RL_Training/scripts/rsl_rl/train.py`
- `RL_Training/scripts/rsl_rl/play.py`
- `RL_Training/rsl_rl/`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前项目不再只有本地 PPO 配置壳；`rsl_rl` 的 runner、PPO、本体网络、分布、存储和日志实现也已经随仓库一并进入版本控制。
- 当前训练入口在运行时会优先吃仓库内 `RL_Training/rsl_rl/`，不再默认依赖 site-packages 中外部 `rsl_rl` 实现。
- 本轮目标不是替换算法逻辑，而是把当前正在使用的算法实现本体一并纳入项目，便于后续继续改 PPO / runner / network 细节。

下一步：
- 在真实 Isaac Lab 环境中跑一次 `Stage0` 冒烟，确认训练启动时加载的确实是仓库内 `RL_Training/rsl_rl/`。
- 然后把本轮 vendored `rsl_rl` 改动与训练主线改动一起提交并推送到 GitHub。

## 2026-04-14

已完成：
- 使用 Google Scholar 按 3 组关键词做一轮分批检索，每组抓取第 1 页，共整理 30 篇候选论文：
  - `("articulated wheeled robot" OR "articulated vehicle" OR "articulated rover") AND ("rough terrain" OR "uneven terrain") AND (control OR "reinforcement learning")`
  - `("active suspension" OR "actively articulated suspension" OR "articulated suspension") AND (robot OR rover) AND ("rough terrain" OR terrain)`
  - `("wheeled robot" OR "ground vehicle") AND ("rough terrain" OR "off-road") AND ("reinforcement learning" OR "deep reinforcement learning")`
- 按“与 articulated / multi-body / actively-jointed wheeled robot + rough terrain + reinforcement learning + terrain perception 的贴合程度”对候选结果做了二次人工重排。
- 当前检索结果可归为 3 类：
  - 主动车体/主动悬架在粗糙地形上的机构与控制
  - 粗糙地形轮式/地面车辆 RL 导航与控制
  - 地形几何估计 / 地形感知驱动的悬架或轮速分配
- 当前第一轮最有价值的 seed papers 已收口为：
  - `Hybrid Learning for Rough Terrain Navigation of Actively Articulated Wheeled Vehicles`
  - `Control of rough terrain vehicles using deep reinforcement learning`
  - `Simultaneous control of terrain adaptation and wheel speed allocation for a planetary rover with an active suspension system`
  - `Control of robotic vehicles with actively articulated suspensions in rough terrain`
- 已同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前与课题四要素同时高度重合的论文并不多，更多是：
  - 主动关节/主动悬架一类论文覆盖机构与地形适应
  - RL 一类论文覆盖粗糙地形控制或导航
  - 地形感知一类论文覆盖 terrain geometry estimation / wheel-terrain contact
- 后续二轮扩展更适合从 seed papers 做 cited-by 追踪，而不是继续大范围宽搜。

已完成：
- 继续处理 `RL_Training/scripts/train.py` 在真实 GPU 训练启动阶段的 articulation 创建失败问题。
- 使用最小 Isaac Sim headless 检查脚本读取 `USD/complete_car.usd` 的真实 prim 层级，确认：
  - 资产根在 `/World/complete_car_alternative`
  - articulation root 在 `/World/complete_car_alternative/body_car_chassis`
  - IMU 实际 prim 名为 `Imu_Sensor`
  - 双目左相机实际 prim 名为 `Stereo_Vision_Camera/Camera_left`
  - LiDAR 实际 prim 名为 `Example_Rotary`
- 修改 `assets/robot_cfg.py`：
  - `COMPLETE_CAR_ARTICULATION_ROOT_PRIM_PATH` 改为 `/complete_car_alternative/body_car_chassis`
- 修改传感器与 height scanner 路径：
  - `sensors/imu.py`
  - `sensors/lidar.py`
  - `sensors/stereo_camera.py`
  - `terrain/terrain_cfg.py`
  统一补上 `complete_car_alternative` 中间层，并改为 USD 中真实存在的传感器 prim 名称
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/assets/robot_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/imu.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/lidar.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/stereo_camera.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
  完成静态编译检查，检查通过。
- 在沙箱外 GPU 环境执行最小训练命令：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 1 --max_iterations 1`
- 实测结果：
  - articulation 创建成功
  - 仿真启动成功
  - actor/critic 网络构建成功
  - 完成 1 次 PPO 学习迭代
  - `Training time: 0.83 seconds`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/assets/robot_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/imu.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/lidar.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/stereo_camera.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前用户这次遇到的训练启动失败已经解决。
- 根因是代码中的 articulation root 与传感器 prim 路径没有对齐 USD 内部的 `complete_car_alternative` 根层级及真实传感器命名。
- 当前 `Stage0` 已恢复为可在真实 GPU 环境中正常完成最小训练启动与 1 次学习迭代的状态。

已完成：
- 处理 `RL_Training/scripts/train.py` 启动时报错的配置类阻塞问题。
- 修改 `terrain/terrain_cfg.py`：
  - 删除会被 Isaac Lab `configclass` 误当作可写成员的只读 `num_height_points` property
  - 改为通过 `get_num_height_points()` 与内部即时采样点解析逻辑计算 patch 点数
- 修改 `base/complete_car_cfg.py` 与 `utils/io_descriptors.py`：
  - 调整为调用 `terrain.get_num_height_points()`
- 修改 `sensors/imu.py`、`sensors/lidar.py`、`sensors/stereo_camera.py`、`sensors/sensor_cfg.py`：
  - 删除 `policy_feature_dim` 只读 property
  - 改为统一使用 `get_policy_feature_dim()`
- 修改 `terrain/terrain_builder.py`：
  - 将 `Stage1TerrainCfg` 从 `frozen dataclass` 改为普通 dataclass
  - 使 Hydra 可以回写 terrain generator 嵌套配置
- 使用：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_builder.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/imu.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/lidar.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/stereo_camera.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
  完成静态编译检查，检查通过。
- 使用：
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cpu --num_envs 1 --max_iterations 1`
  做真实训练入口冒烟验证。
- 结果：
  - 已确认原始启动报错链路不再出现
  - 训练入口已越过 Hydra 配置注册与 `env_cfg` 构建，进入 Isaac Lab 仿真上下文创建
  - 当前继续看到的是环境级问题：
    - 无 CUDA 驱动 / 无可用 GPU
    - Isaac Sim `user.config.json` 与 cache 目录写入受限

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/imu.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/lidar.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/stereo_camera.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_builder.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 direct workflow 的配置树中，不应再用继承只读 property 来表示可推导配置量。
- 当前 terrain generator 嵌套配置必须保持可写，不能继续使用 `frozen dataclass`。
- 用户本次贴出的训练启动报错已经解决；若后续仍无法跑通，应转而排查本机 Isaac Sim 运行环境而不是继续回到这组配置类问题。

已完成：
- 按用户要求调整 GitHub 同步范围：
  - 保留所有当前代码与文档改动进入本轮同步
  - 排除 `.~lock*` 临时锁文件
  - 将 `URDF/complete_car_alternative/vehicle_dimensions_axles_tracks.xlsx` 纳入本轮提交
- 修改根 `.gitignore`：
  - 新增 `.~lock*`
  - 新增 `docs/literature/`
  - 新增 `毕业论文/`
- 明确仓库同步策略：
  - `docs/literature/` 与 `毕业论文/` 仅保留为本地资料目录
  - 本轮同步时会从 Git 索引中移除它们，使 GitHub 远端仓库同步删除对应内容，但不删除本地文件
- 同步更新项目记忆文件：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `.gitignore`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 后续 GitHub 远端仓库将不再保存论文正文目录与文献资料目录。
- 这两个目录今后默认只作为本地研究工作区保留。

已完成：
- 按用户要求更新并精简 `docs/training_workflow_and_tensorboard_guide.md`。
- 删除文档中已失效的旧工程路径与旧 task id：
  - `src/rl_lab/complete_car_rl_training`
  - `Complete-Car-Rl-Training-v0`
- 文档现已统一改为当前有效主线：
  - `RL_Training/`
  - `scripts/train.py`
  - `scripts/play.py`
  - `CompleteCar-Stage0/1/2`
- 文档内容已收口为最小工作流：
  - 环境准备
  - 训练命令
  - 回放命令
  - 日志与 checkpoint 目录
  - TensorBoard 查看命令
  - 离线导出 TensorBoard 标量命令

修改文件：
- `docs/training_workflow_and_tensorboard_guide.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前训练流程说明文档已与现有代码结构一致，可直接作为 `RL_Training/` 主线的简明操作入口使用。

已完成：
- 分析真实 Stage0 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_12-48-16`
- 已确认该次 run 的 TensorBoard 当前只有 21 个 scalar tag，不是 TensorBoard 故障，而是训练日志覆盖面不足。
- 已根据当前 active 语义补强训练日志链路：
  - `env.py` 现可输出当前步的：
    - `Reward/...`
    - `Tracking/...`
    - `Action/...`
    - `Command/...`
    - `Observation/...`
    - `Termination/...`
  - 终止逻辑已拆成显式分项：
    - `bad_orientation`
    - `ball_joint_out_of_bounds`
    - `root_too_low`
    - `time_out`
  - episode 侧新增：
    - `episode/return`
    - `episode/return_per_step`
    - `episode_per_step/...`
    - `episode_reset/...`
- 已修改 TensorBoard 离线导出脚本：
  - 新增 `group_summary.csv`
  - `latest_values.csv` 新增：
    - `group`
    - `first_value`
    - `last_value`
    - `delta`
    - `min_value`
    - `max_value`
    - `mean_value`
- 已执行：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py`
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_12-48-16`
  均已通过。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前代码已经补齐新一轮训练应当输出的大部分核心运行指标。
- 旧 run `2026-04-14_12-48-16` 的 event 文件不会自动长出新 tag；需要重新跑一次训练才能验证新增指标是否进入 TensorBoard。

已完成：
- 定位并修正一次回放链路报错。
- 用户执行：
  - `python scripts/play.py --task CompleteCar-Stage0 --load_run 2026-04-14_12-48-16 --num_envs 2`
  时，原先会报：
  - `TypeError: first argument must be string or compiled pattern`
- 根因已确认：
  - `agents/rsl_rl_ppo_cfg.py` 中默认：
    - `load_run = -1`
    - `load_checkpoint = -1`
  - 但 Isaac Lab 的 `get_checkpoint_path()` 需要的是正则字符串，而不是整数哨兵值。
- 当前已修正：
  - `agents/rsl_rl_ppo_cfg.py`
    - 改为：
      - `load_run = ".*"`
      - `load_checkpoint = "model_.*.pt"`
  - `scripts/train.py`
  - `scripts/play.py`
    - 在调用 `get_checkpoint_path()` 前新增类型归一化，避免旧整数值再次导致崩溃
- 已执行：
  - `python3 -m py_compile RL_Training/scripts/train.py RL_Training/scripts/play.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`
  - 并做了本地选择器归一化检查，确认：
    - `load_run='2026-04-14_12-48-16', load_checkpoint=-1`
    会被转换为：
    - `('2026-04-14_12-48-16', 'model_.*.pt')`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`
- `RL_Training/scripts/train.py`
- `RL_Training/scripts/play.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前回放命令在只指定 `--load_run` 时，逻辑上应会自动选择该 run 下最新的 `model_*.pt`，不应再因为 `-1` 类型错误崩溃。

已完成：
- 继续修正同一回放链路中的下一处报错。
- 用户再次执行回放时，原先会报：
  - `packaging.version.InvalidVersion: '5.0.1-local'`
- 根因已确认：
  - 本地 vendored `rsl_rl/__init__.py` 中版本号写成了：
    - `5.0.1-local`
  - `scripts/play.py` 中使用 `packaging.version.parse()` 做版本分支判断，这个字符串不符合 PEP 440。
- 当前已修正：
  - `rsl_rl/__init__.py`
    - 改为：
      - `5.0.1+local`
  - `scripts/play.py`
    - 增加版本兼容解析函数，若遇到旧的 `-local` 后缀会先归一化再解析
- 已执行：
  - `python3 -m py_compile RL_Training/scripts/play.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/__init__.py`
  - 本地纯 Python 验证：
    - `5.0.1-local`
    - `5.0.1+local`
    均可被当前回放辅助函数归一化并通过比较

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/__init__.py`
- `RL_Training/scripts/play.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前回放链路已连续修掉：
  - checkpoint 选择器类型错误
  - vendored 版本号解析错误
- 还需要在真实 Isaac Lab 环境里继续执行一次回放，确认后续运行时链路没有新的阻塞。

已完成：
- 分析真实 Stage0 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_13-07-32`
- 已确认本次 run 的新增日志链路已实际写入 event 文件：
  - scalar tag 数量为 `64`
  - 分组已包含：
    - `Action`
    - `Command`
    - `Reward`
    - `Tracking`
    - `Observation`
    - `Termination`
    - `episode_per_step`
    - `episode_reset`
- 当前 run 的高层训练结果与上一轮：
  - `2026-04-14_12-48-16`
  在旧共有指标上数值一致，说明相同 seed / 配置下复现稳定。
- 本次 run 的 last50 结果大致为：
  - `Train/mean_reward ≈ 2196`
  - `Train/mean_episode_length ≈ 716`
  - `Tracking/lin_vel_x_abs_error ≈ 0.084`
  - `Tracking/ang_vel_yaw_abs_error ≈ 0.388`
  - `Reward/total ≈ 3.107`
  - `Observation/tilt_deg ≈ 3.11`
- 当前主要剩余终止来源不是：
  - `bad_orientation`
  - `root_too_low`
  而是：
  - `ball_joint_limit`
- 同时当前动作指标显示：
  - `Action/policy_abs_mean ≈ 0.886`
  - `Action/policy_std ≈ 0.815`
  说明 policy 动作整体较激进，和球铰越界终止现象一致。
- 已执行：
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_13-07-32`
  并完成 event 标量统计与上一轮 run 对比。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 新日志体系已经在真实 run 中验证生效。
- 当前 Stage0 下一轮更应该优先处理球铰越界终止，而不是姿态倾覆或车体高度问题。

已完成：
- 按用户确认执行方案一，新增球铰软约束惩罚：
  - `ball_joint_limit_soft`
- 当前实现位置：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- 当前实现语义：
  - 仅当球铰利用率超过可用范围的 `80%` 后激活
  - 按默认位姿到硬 limit 的相对使用率计算
  - 对 6 个球铰取均值
  - 使用二次惩罚
  - 当前 scale 为：
    - `-0.2`
- 同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
- 已执行真实 GPU 训练：
  - `cd /home/ubuntu/Graduation-Project/RL_Training`
  - `source /home/ubuntu/miniconda3/etc/profile.d/conda.sh && conda activate env_isaacLab`
  - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --run_name soft_limit_v1`
- 本轮新 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_13-36-38_soft_limit_v1`
- 已执行离线导出：
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_13-36-38_soft_limit_v1`
- 与 baseline：
  - `2026-04-14_13-07-32`
  的 last50 对比结果：
  - `Train/mean_reward`：
    - `2196 -> 2387`
  - `Train/mean_episode_length`：
    - `716 -> 743`
  - `Tracking/ang_vel_yaw_abs_error`：
    - `0.388 -> 0.310`
  - `episode_reset/ball_joint_limit_rate`：
    - `0.395 -> 0.344`
  - `episode_reset/time_out_rate`：
    - `0.605 -> 0.656`
  - 但 `Observation/tilt_deg`：
    - `3.11 -> 6.85`
    出现明显上升
- 额外结论：
  - `Loss/value` 仍明显波动，不是单调收敛
  - 但结合奖励、tracking、episode length 的改善，当前不能把 value loss 波动直接解释成训练失败
  - 当前问题已从“球铰越界明显”变成“软约束改善 joint-limit reset，但带来了更大的姿态倾角”

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 方案一已真实跑通并完成结果对比。
- 当前 soft limit 方向有效，但下一轮应围绕“压回姿态倾角”做单变量修正，而不是回退这个软约束项。

已完成：
- 按用户要求进入自动奖励优化循环，对 Stage0 又连续执行了 2 轮真实 GPU 单变量训练，并在每轮结束后导出 TensorBoard 标量做后 50 次均值对比。
- 第 1 轮：
  - 将 `Stage0` 的 `orientation` 权重从 `-3.0` 回调到 `-2.5`
  - 训练命令：
    - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --run_name soft_limit_v1_orient25`
  - run：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_13-57-08_soft_limit_v1_orient25`
  - 导出命令：
    - `python source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir logs/rsl_rl/complete_car_stage0/2026-04-14_13-57-08_soft_limit_v1_orient25`
- 第 2 轮：
  - 以当前最稳的 `orientation = -3.0` 版本为底座，临时把 `tracking_lin_vel` 提高到 `2.2`
  - 训练命令：
    - `python scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --run_name soft_limit_v1_orient3_lin22`
  - run：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_14-04-19_soft_limit_v1_orient3_lin22`
  - 导出命令：
    - `python source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir logs/rsl_rl/complete_car_stage0/2026-04-14_14-04-19_soft_limit_v1_orient3_lin22`
- 已将 `Stage0` 当前代码恢复到本轮验证后的最优已知配置：
  - `orientation = -3.0`
  - 保留 `ball_joint_limit_soft = -0.2`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 5 个可比 run 中，最优已验证配置仍然是：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_13-48-25_soft_limit_v1_orient3`
- 其 last50 关键结果大致为：
  - `Train/mean_reward ≈ 2779`
  - `Train/mean_episode_length ≈ 893`
  - `Tracking/lin_vel_x_abs_error ≈ 0.141`
  - `Tracking/ang_vel_yaw_abs_error ≈ 0.344`
  - `Observation/tilt_deg ≈ 2.03`
  - `episode_reset/terminated_rate ≈ 0.085`
  - `episode_reset/time_out_rate ≈ 0.915`
- `orientation = -2.5` 虽然比 `-3.0` 更像折中，但稳定性明显退化：
  - `episode_reset/terminated_rate ≈ 0.191`
  - `tilt_deg ≈ 4.02`
- `tracking_lin_vel = 2.2` 虽然把 `Reward/tracking_lin_vel` 提高到约 `1.91`，但真实前向误差并没有改善，反而恶化到：
  - `Tracking/lin_vel_x_abs_error ≈ 0.163`
  同时：
  - `Tracking/ang_vel_yaw_abs_error ≈ 0.449`
  - `tilt_deg ≈ 4.84`
  - `episode_reset/terminated_rate ≈ 0.177`
- 因此本轮自动优化已经收口到一个“当前较为理想”的结果：
  - 保留软约束惩罚
  - Stage0 使用更强的姿态惩罚 `orientation = -3.0`
  - 不继续保留 `orientation = -2.5` 或 `tracking_lin_vel = 2.2` 这两条临时实验分支

下一步：
- 若继续做 Stage0 调优，应优先围绕动作正则或 reward 耦合做新的单变量设计，而不是继续直接削弱姿态惩罚。

已完成：
- 确认本次训练 `2026-04-14_20-52-07` 的实际结果目录为：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_20-52-07/`
- 检查该目录下当前已有：
  - `events.out.tfevents.*`
  - `model_0.pt` 到 `model_599.pt`
  - `params/env.yaml`
  - `params/agent.yaml`
  - `git/Graduation-Project.diff`
- 更新 `docs/training_workflow_and_tensorboard_guide.md`：
  - 补充每次训练结果的固定保存规则
  - 补充绝对路径写法
  - 补充 `run_dir` 的时间戳命名方式
  - 补充本次训练的实际示例路径

修改文件：
- `docs/training_workflow_and_tensorboard_guide.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前训练结果统一保存在：
  - `RL_Training/logs/rsl_rl/<experiment_name>/<run_dir>/`
- 对于当前这次 Stage0 训练，对应目录就是：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_20-52-07/`

## 2026-04-15

已完成：
- 按用户要求检查两个真实 Stage0 run 的 observation 项，确认能否通过 scale 反推出原始量级并判断当前参数是否合适：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_14-04-19_soft_limit_v1_orient3_lin22`
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-14_20-52-07`
- 由于第二个 run 原本只有 `events.out.tfevents.*`，已先补执行：
  - `python3 source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py --run_dir logs/rsl_rl/complete_car_stage0/2026-04-14_20-52-07`
- 对照两次 run 冻结下来的 `params/env.yaml`，确认两次 run 的 observation scale 完全一致：
  - `base_lin_vel = 1.0`
  - `base_ang_vel = 0.25`
  - `projected_gravity = 1.0`
  - `ball_joint_pos = 1.0`
  - `ball_joint_vel = 0.05`
  - `ball_joint_target_error = 1.0`
  - `module_roll_pitch = 1.0`
  - `wheel_joint_vel = 0.05`
  - `commands = 1.0`
- 已根据 last50 统计反推归一化后的观测量级：
  - 可直接反推的观测项大多落在 `0.03 ~ 0.54` 这一量级
  - 当前没有发现明显的 observation scale 配置错误
- 同时确认一个重要限制：
  - `Observation/base_lin_vel_x`
  - `Observation/base_ang_vel_yaw`
  - `Command/lin_vel_x`
  - `Command/ang_vel_yaw`
  当前日志记录的是跨 env 的有符号均值，不能直接拿来判断真实幅值分布

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 的 observation scale 不是主要矛盾。
- 相比之下，更值得继续盯的是：
  - `Action/policy_abs_mean` 仍接近 `1.0`
  - `ball_joint_target_error_abs_mean` 仍偏大
- 因此如果后续继续做 Stage0 诊断，优先级应放在动作激进性和 reward 耦合，而不是先去大幅重配 observation scale。

已完成：
- 按用户要求修改 TensorBoard 的 step-level observation 输出，使其显式记录未乘 scale 的原始观测值，而不是和 policy 输入混在一起。
- 在：
  - `mdp/observations.py`
  中新增原始观测分量收集函数，并将 Actor observation 的 scale 乘法保留在观测拼接阶段。
- 在：
  - `base/env.py`
  中把 TensorBoard 使用的 `Observation/...` 日志改为从原始观测分量直接取值，并统一追加 `_raw` 后缀。
- 当前新增/替换的原始观测标签包括：
  - `Observation/base_lin_vel_x_raw`
  - `Observation/base_ang_vel_yaw_raw`
  - `Observation/projected_gravity_xy_norm_raw`
  - `Observation/ball_joint_pos_abs_mean_raw`
  - `Observation/ball_joint_vel_abs_mean_raw`
  - `Observation/ball_joint_target_error_abs_mean_raw`
  - `Observation/wheel_joint_vel_abs_mean_raw`
  - `Observation/head_roll_pitch_abs_mean_raw`
  - `Observation/tail_roll_pitch_abs_mean_raw`
  - `Observation/goal_rel_x_raw`
  - `Observation/goal_rel_y_raw`
  - `Observation/goal_rel_psi_raw`
  - `Observation/last_action_abs_mean_raw`
- 已执行静态检查：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 之后新的 TensorBoard run 中，`Observation/..._raw` 可以直接拿来读原始物理量，不需要再手工除以 scale。
- policy 输入归一化逻辑仍然保留，不影响训练执行链。

已完成：
- 按用户要求删去动作链中的电机干扰项。
- 当前已从主执行链路中移除：
  - `motor_strength`
  - reset 时的 `sample_motor_strength(...)`
  - `Action/motor_strength_mean` 日志项
- `preprocess_policy_actions(...)` 现已改为：
  - 先裁剪 policy action
  - 再直接作为 `processed_actions`
  - 不再乘任何电机强度系数
- `RandomizationCfg` 已删除：
  - `randomize_motor_strength`
  - `motor_strength_range`
- 当前动作侧若后续开启随机化，仅剩：
  - `action_noise_std`
  - `action_bias_std`
  这两类显式机制
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/randomization.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active action pipeline 已不存在电机强度扰动项。
- 之后如果训练中还出现动作侧不稳定，应优先从：
  - policy 输出本身
  - `action_noise_std`
  - `action_bias_std`
  去查，而不是再去找 `motor_strength` 支路。

已完成：
- 按用户要求从当前 active direct workflow 中删去 `root_too_low` 相关内容。
- 当前已删除：
  - `TerminationCfg.minimum_root_height`
  - `done_terms["root_too_low"]`
  - `Termination/root_too_low_rate`
  - `episode_reset/root_too_low_rate`
  - `episode/root_height_mean`
  - `episode/root_height_min`
  - `Observation/root_height`
- env 内部也不再维护用于该终止项诊断的 root-height 统计缓存。
- 当前 active 失败终止条件已收口为：
  - `bad_orientation`
  - `ball_joint_out_of_bounds`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 之后新的 direct-workflow run 不应再出现 `root_too_low` 相关 termination 和统计标签。
- 历史日志中与 `root_too_low` 相关的条目仍保留为历史结论，但不再代表当前 active 主线。

已完成：
- 按用户要求在当前 active direct workflow 的现有观测项基础上新增 18 维轮地接触相关观测：
  - 6 维各轮纵向滑移率
  - 6 维各轮侧滑角
  - 6 维按整车重量归一化的各轮法向接触力
- 当前 slip / contact 观测实现已按用户给定物理定义接入：
  - 纵向滑移率使用
    - `(v_x - r * omega) / max(|v_x|, eps)`
  - 侧滑角使用
    - `atan2(v_y, |v_x| + eps)`
  - 法向接触力使用
    - `max(0, F_contact · z_hat) / (m_total * g)`
- 当前低速保护与裁剪参数为：
  - `eps = 0.1`
  - `slip ratio clip = [-1, 1]`
  - `slip angle clip = [-pi/2, pi/2]`
- 当前 wheel contact force 入口已打通：
  - `robot_cfg.py` 中 USD spawn 已启用 `activate_contact_sensors = True`
  - `sensor_cfg.py` 中新增了绑定 6 个 wheel body 的 `ContactSensor`
  - `env.py` 中会读取 `net_forces_w` 并传入 observation 计算链
- 当前 wheel body 与参数常量已显式收口：
  - `WHEEL_BODY_NAMES`
  - `WHEEL_RADIUS = 0.19`
- 当前 actor / critic 单帧观测维度已由：
  - `52 / 52`
  更新为：
  - `70 / 70`
- TensorBoard step-level 原始观测日志已新增：
  - `Observation/wheel_longitudinal_slip_abs_mean_raw`
  - `Observation/wheel_slip_angle_abs_mean_raw`
  - `Observation/wheel_normal_contact_force_abs_mean_raw`
  - `Observation/wheel_normal_contact_force_sum_raw`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/assets/__init__.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/assets/robot_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active direct workflow 已具备显式轮地滑移/侧滑/载荷分布观测。
- 当前法向接触力仍采用世界系 `z` 方向近似法向，这是当前实现里有意保留的简化，而不是局部接触面法向重建。
- 已通过目标文件的 `python3 -m py_compile` 静态编译检查。

已完成：
- 按用户要求删除车轮动作映射里重复的上下限配置项：
  - `wheel_joint_action_lower_limits`
  - `wheel_joint_action_upper_limits`
- 当前车轮动作只保留一个对称速度上限入口：
  - `wheel_joint_velocity_limit_sim`
- 当前后 6 维标准化车轮动作的映射已改为：
  - `wheel_target = action * wheel_joint_velocity_limit_sim`
- 因此当前车轮动作语义为：
  - `action = 1` 对应 `+v_max`
  - `action = -1` 对应 `-v_max`
  - `action = 0` 对应 `0`
- env 主链调用和文档说明已同步到这一口径。
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前车轮动作映射参数已收口，不再出现“先定义速度上限、再重复定义一组对称上下限”的冗余配置。
- 后续若要调整车轮动作幅值，只需要改：
  - `wheel_joint_velocity_limit_sim`
- 已通过目标文件的 `python3 -m py_compile` 静态编译检查。

已完成：
- 按用户要求，先将以下 5 组量从当前 active policy observation trunk 中注释掉，暂不送入 PPO：
  - 6 个球铰角速度
  - 6 个球铰目标跟踪误差
  - 前车绝对 roll/pitch
  - 后车绝对 roll/pitch
  - 6 个车轮轮速
- 当前修改只影响 actor / critic 观测主干，不影响：
  - 底层状态本身
  - reward 主链
  - 动作执行链
- observation descriptor 与 observation-noise 维度已同步收口。
- 当前 actor / critic 单帧观测维度已由：
  - `70 / 70`
  调整为：
  - `48 / 48`
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/math_utils.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active policy observation trunk 已精简为：
  - 中车 body-frame 线速度
  - 中车 body-frame 角速度
  - 中车重力投影
  - 6 个球铰角
  - 6 个车轮纵向滑移率
  - 6 个车轮侧滑角
  - 6 个按整车重量归一化的车轮法向接触力
  - 相对目标命令
  - 上一时刻动作
- 已通过目标文件的 `python3 -m py_compile` 静态编译检查。

已完成：
- 按用户要求，将轮胎法向接触力从“世界系 `z` 分量近似”改成“沿轮胎-地面接触法向”的更严格版本。
- 先对照本地 Isaac Lab 手册确认：
  - `ContactSensor.data.net_forces_w`
  本身就是世界系下的净法向接触力向量，而不是总接触力。
- 因此当前实现已从：
  - `max(0, F_contact · z_hat) / (m_total * g)`
  改为：
  - `||net_forces_w|| / (m_total * g)`
- 当前含义是：
  - 直接使用 6 个 wheel body 的净法向接触力向量模长
  - 再按整车总重量归一化
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前轮胎法向接触力不再依赖世界系竖直方向近似。
- 当前实现已经切到基于 Isaac Lab 法向接触力向量本身的更严格口径。

已完成：
- 按用户要求，将当前 direct workflow 的奖励主线从旧的速度跟踪型 reward 重构为目标导向 reward。
- 当前 reward 不再使用旧的：
  - `tracking_lin_vel`
  - `tracking_ang_vel`
  - `orientation`
  - `action_rate`
  - `ball_joint_limit_soft`
  - `termination`
- 当前 active reward 结构已经改为：
  - `target_bonus + gated_progress`
- 其中：
  - `progress = (d_{t-1} - d_t) * control_frequency`
  - `gated_progress = progress * roll_gate * speed_gate * force_gate * composite_gate`
  - `composite_gate = (heading_gate + longitudinal_slip_gate + lateral_slip_gate) / 3`
- 当前已新增并接线的 reward 组成包括：
  - `target_bonus`
  - `progress`
  - `roll_gate`
  - `speed_gate`
  - `force_gate`
  - `heading_gate`
  - `longitudinal_slip_gate`
  - `lateral_slip_gate`
  - `composite_gate`
  - `gated_progress`
- env 当前已维护：
  - 上一时刻目标距离缓存
  - reset 后目标距离初始化
  - 命令重采样后的目标距离重置
- TensorBoard step 级 reward 指标已同步切换为新的目标导向指标命名。
- 已同步更新：
  - `docs/RL阶段训练参数一览表.md`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 direct workflow 的 active reward 已正式切到目标达成 + 朝目标推进主线。
- 当前奖励已经与 goal-conditioned 命令空间一致，不再保留旧速度命令跟踪逻辑。
- 已通过针对改动文件的 `python3 -m py_compile` 静态编译检查。

已完成：
- 继续做 Stage0 的低滑移 / 低侧滑定向实验，不再插入单独 smoke，而是直接跑对比训练。
- reward 新增并保留：
  - `wheel_action_rate_gate`
- 训练日志新增并保留：
  - `Observation/base_lin_vel_y_raw`
- 试验并否决：
  - `lateral_speed_gate`
  - 在 `gated_progress` 外再次额外乘一次 `lateral_slip_gate`
- 已将上述两个否决方向从默认代码回退。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `docs/RL阶段训练参数一览表.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前最佳短跑参考 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-45-26_wheel_action_smooth_v1`
  - 在约 `iteration 39/40`：
    - `wheel_longitudinal_slip_abs_mean_raw ≈ 0.8145`
    - `wheel_slip_angle_abs_mean_raw ≈ 0.7318`
    - `base_lin_vel_x_raw ≈ 1.3777`
    - `Loss/value ≈ 0.027`
- `lateral_speed_gate` 已否决，对应 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-48-41_lateral_speed_gate_v1`
  - 结论：
    - critic 更稳
    - 但长期滑移/侧滑改善不足，不如 `wheel_action_smooth_v1`
- “额外提高 lateral slip 权重”也已否决：
  - 短跑：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-50-45_lateral_slip_priority_v1`
  - 长跑：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-15_22-52-30_lateral_slip_priority_v1_iter300`
    - 实际观察到约 `iteration 143/300` 后停止
  - 中后期结论：
    - critic 仍稳，`Loss/value ≈ 0.001 ~ 0.002`
    - 但策略重新回到激进区：
      - `base_lin_vel_x_raw ≈ 1.62 ~ 1.65`
      - `wheel_longitudinal_slip_abs_mean_raw ≈ 0.816 ~ 0.819`
      - `wheel_slip_angle_abs_mean_raw ≈ 0.733 ~ 0.735`
      - `tilt_deg ≈ 16.4 ~ 16.7`
- 当前默认代码已回到：
  - Stage0 稳定性优先 bundle
  - 平滑 slip gates
  - `wheel_action_rate_gate`

下一步：
- 不再继续叠加同类 multiplicative gate。
- 下一轮应转向更结构性的侧滑来源，例如轮速映射或动作语义，而不是继续在同一 reward 结构上加门。

## 2026-04-17

已完成：
- 对 `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_16-29-08` 做完整训练诊断。
- 使用 `tensorboard_export.py` 导出该 run 的 TensorBoard 标量，补齐离线分析数据。
- 同步更新项目记忆文件：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 该 run 已建立：
  - 存活
  - 朝目标推进
  - 末段 target bonus 触发
- 末段关键量级：
  - `Train/mean_episode_length ≈ 1335.64 / 1439`
  - `Train/mean_reward ≈ 768.02`
  - `Tracking/goal_pos_error ≈ 4.88 m`
  - `Tracking/goal_yaw_error_abs ≈ 0.259 rad`
  - `Reward/01_progress ≈ 1.123`
  - `Reward/00_gated_progress ≈ 0.364`
  - `Reward/03_longitudinal_slip_gate ≈ 2.58e-4`
  - `Reward/04_lateral_slip_gate ≈ 1.94e-4`
  - `Reward/05_composite_gate ≈ 0.215`
  - `Loss/value ≈ 852`
- 当前主问题已不是姿态或球铰越界，而是：
  - 新增的纵滑 / 侧滑 gate 在当前量级下长期接近 `0`
  - 导致 `progress` 奖励被大幅衰减
  - critic value loss 明显恶化
- 当前最主要原因是：
  - 观测侧已取消 slip 裁切
  - reward 侧仍使用较严参数：
    - `longitudinal_slip_gate_scale = 0.3`
    - `lateral_slip_gate_scale = 6.0`
  - 且 6 个轮子的 gate 采用连乘，导致总 gate 对当前滑移量级过于敏感

下一步：
- 下一轮如果继续沿这条 reward 主线调，应优先检查：
  - slip-gate 参数强度
  - slip-gate 聚合方式
  - `composite_gate` 对 `progress` 的实际压缩程度

## 2026-04-17

已完成：
- 基于当前 active Stage0 配置与 `2026-04-17_16-29-08` 真实 run，分析“观测 scale 全设为 1.0 后的量级分布”和“纵滑/侧滑裁切范围应如何设定”。
- 同步更新项目记忆文件：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 actor/critic 仍开启：
  - `obs_normalization = true`
- 因此“全部 observation scale = 1.0”并非没有影响，但影响被经验归一化明显削弱。
- 当前最新 run 里，大多数非 slip active 观测项仍主要落在：
  - `O(1)` 或 `O(1) ~ O(10)` 量级
- 当前真正偏大的 active 观测仍是：
  - `wheel_longitudinal_slip`
    - mean `2.79`
    - max `5.69`
  - `wheel_slip_angle`
    - mean `0.75 rad`
- 当前判断：
  - 最新训练结果受影响更大的不是“其他 scale 全部设成 1.0”，而是：
    - raw slip 观测取消裁切
    - slip-gate 本身过严
- 若恢复 observation-path 纵向滑移率裁切，第一版建议先试：
  - `[-3.0, +3.0]`
- 对当前侧滑角 reward：
  - 若保持 `0.5 * cos(k * alpha) + 0.5`
  - 且当前 `k = 6`
  - 则 reward-side clip 应继续保持：
    - `[-pi/6, +pi/6]`
  - 如果希望放宽侧滑角 reward 有效区间，应优先改：
    - `k`
    而不是只改单独 clip

下一步：
- 如果下一轮继续调 slip 相关项，应把：
  - observation-path clip
  - reward-side clip
  - cosine 参数 `k`
  当成联动设计处理，而不是分别独立调。 

## 2026-04-17

已完成：
- 按用户要求修改 Stage0：
  - observation-path `wheel_longitudinal_slip` 恢复裁切到 `[-3.0, +3.0]`
  - `lateral_slip_gate_scale` 从 `6.0` 改为 `4.0`
- 对改动文件做 `python3 -m py_compile` 静态检查，通过。
- 启动一轮真实 GPU 训练：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_17-02-10_slipclip3_latk4_v1`
- 用户确认不需要跑满全部 iteration，因此在问题暴露后停止训练，并导出当前 TensorBoard 标量做中期判断。
- 同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `docs/RL阶段训练参数一览表.md`
  - `docs/Stage0_reward设计详解.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `docs/RL阶段训练参数一览表.md`
- `docs/Stage0_reward设计详解.md`
- `logs/daily_work_log.md`

产出/结论：
- 本轮部分训练停在约：
  - `527 / 600`
- 相比上一轮 `2026-04-17_16-29-08`，当前改动的直接效果是：
  - 纵向滑移率原始量级明显下降：
    - `2.79 -> 1.80`
  - 目标误差和朝向误差改善：
    - `goal_pos_error ≈ 5.21 m`
    - `goal_yaw_error_abs ≈ 0.150 rad`
  - `target_bonus` 已明显非零
- 但主问题仍存在：
  - `Reward/03_longitudinal_slip_gate ≈ 5.27e-06`
  - `Reward/04_lateral_slip_gate ≈ 7.74e-04`
  - 两个 slip gate 仍长期接近 `0`
  - `Loss/value ≈ 312.94`
  - 末段 `ball_joint_limit_rate ≈ 0.719`
- 当前结论：
  - `±3.0` 纵滑 observation 裁切有效
  - `k = 4` 确实比 `6` 更宽容
  - 但在“6 个轮子 gate 连乘”的结构下，当前 slip-gate 依旧过严

下一步：
- 如果继续沿当前 reward 主线调，优先级应转到：
  - slip-gate 聚合方式
  - 与 ball-joint-limit 的后段耦合

## 2026-04-17

已完成：
- 对用户修改后的动作空间启动一轮新的真实 GPU 训练：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_17-28-36_action8_allocator_v1`
- 先做动作链与 env 接口静态检查：
  - `actions.py`
  - `env.py`
  - `complete_car_stage0_cfg.py`
  的 `python3 -m py_compile` 已通过
- 训练跑到中期趋势清晰后停止，并导出 TensorBoard 标量做诊断。
- 同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 run 停在约：
  - `66 / 600`
- 当前动作空间运行时自洽：
  - actor obs dim = `44`
  - critic obs dim = `44`
  - action dim = `8`
- 相比上一轮 `slipclip3_latk4_v1`，当前最重要的改善是：
  - `Reward/03_longitudinal_slip_gate` 不再接近 `0`
    - 当前约 `0.0079`
  - `Reward/04_lateral_slip_gate` 也不再接近 `0`
    - 当前约 `0.0062`
  - `Termination/04_ball_joint_limit_rate` 当前为 `0.0`
  - `Loss/00_value ≈ 4.26`
    - 明显低于上一轮的 `312.94`
- 当前中期任务指标为：
  - `Train/mean_reward ≈ 248.79`
  - `Tracking/goal_pos_error ≈ 8.59 m`
  - `Tracking/goal_yaw_error_abs ≈ 0.498 rad`
  - `Reward/target_bonus = 0`
- 当前判断：
  - 8 维动作空间方向是有效的
  - 当前动作语义已经明显改善：
    - slip gate 长期塌缩
    - critic 爆高
    - ball joint 后段越界
  - 当前下一步更值得看的是：
    - 收敛速度
    - 更长训练下 target bonus 是否开始触发

## 2026-04-17

已完成：
- 对 `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_17-33-20` 做中期训练诊断。
- 导出并检查该 run 的 TensorBoard 标量：
  - `summary.json`
  - `latest_values.csv`
- 同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 该 run 实际已跑到约：
  - `162 / 600`
- 当前关键结果：
  - `Train/mean_reward ≈ 501.59`
  - `Train/mean_episode_length ≈ 1380.19`
  - `Tracking/goal_pos_error ≈ 7.75 m`
  - `Tracking/goal_yaw_error_abs ≈ 0.136 rad`
  - `Reward/03_longitudinal_slip_gate ≈ 0.0055`
  - `Reward/04_lateral_slip_gate ≈ 0.0028`
  - `Loss/00_value ≈ 2.07`
  - `Observation/03_tilt_deg ≈ 0.081°`
- 当前主要问题：
  - `Termination/04_ball_joint_limit_rate ≈ 0.50`
  - `Termination/00_time_out_rate ≈ 0.50`
  - `Reward/target_bonus = 0`
- 当前结论：
  - 新动作空间主线继续成立
  - 当前更长一点训练后，主要矛盾开始集中到：
    - 后段 ball joint 越界重新抬升
  - 当前不再是：
    - slip gate 长期塌缩
    - critic 不稳定

下一步：
- 如果继续沿当前动作空间主线调，应优先围绕：
  - 后段 ball joint limit
  - 与 progress / heading 攻击性之间的耦合

## 2026-04-17

已完成：
- 继续推进“到底是哪个球铰轴先顶边界”的分析支持。
- 在 env step metrics 中新增分轴球铰日志：
  - 每个球铰轴的实际位置
  - 每个球铰轴的平均限位利用率
  - 每个球铰轴的最大限位利用率
- 对修改后的 `env.py` 做 `python3 -m py_compile` 静态检查，通过。
- 同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已有 run 的 aggregate 日志只能说明：
  - 球铰余量在被主动消耗
- 但还不能精确定位：
  - 是前模块还是后模块
  - 是 `yaw / pitch / roll` 中的哪一轴先顶边界
- 现在新的 step metrics 已经能直接输出：
  - `Observation/spm1_platform_joint_z_pos_raw`
  - `Observation/spm1_platform_joint_z_limit_usage_mean_raw`
  - `Observation/spm1_platform_joint_z_limit_usage_max_raw`
  - 以及其余 5 个球铰轴对应指标
- 下一轮训练开始后，可以直接在 TensorBoard 判断：
  - 哪个具体球铰轴最先逼近边界

## 2026-04-17

已完成：
- 按用户要求把 `heading_distance_scale (kd)` 临时改为 `6.0`，并启动一轮短训练验证：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_19-48-06_kd6_v1`
- 本轮在约 `26 / 600` 主动停止，原因是趋势已经足够明确：
  - `goal_yaw_error_abs` 快速恶化到约 `1.07 ~ 1.22 rad`
  - `ball_joint_limit_rate` 在 `iteration 26` 升到约 `0.781`
  - `heading_gate` 中期约降到 `0.70 ~ 0.75`
  - `target_bonus` 始终为 `0`
- 本轮结论：
  - `kd = 6` 虽然放宽了前期航向门，但把中后段约束也一起放宽过头
  - 策略会更愿意带着大 yaw 误差和更激进的球铰动作去换 progress
  - 结果明显差于当前健康主线 `kd = 12`
- 已在实验结束后把 active 默认恢复为：
  - `heading_distance_scale = 12.0`
- 同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `kd` 不能继续靠“整体缩小”来放宽前期航向要求。
- 如果后续还要做早期更宽容、后期仍严格的 heading gate，需要换机制，而不是继续全局减小 `kd`。

已完成：
- 围绕“把 Stage0 从追踪任务改成终端捕获任务”做了 4 轮自动化短训练实验，并在每轮出现明显趋势后主动停止。
- 实验 1：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_18-35-19_capture_holdgoal_v1`
  - 修改：
    - `resampling_time: 8.0 -> 24.0`
  - 结果：
    - `mean_reward ≈ 89.68`
    - `mean_episode_length ≈ 1359.75`
    - `ball_joint_limit_rate ≈ 0.339`
    - `target_bonus = 0`
- 实验 2：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_18-38-44_capture_holdgoal_goal6_v1`
  - 修改：
    - 保持单目标
    - `goal_distance: 12.0 -> 6.0`
  - 结果：
    - `goal_pos_error ≈ 4.41 m`
    - `target_bonus = 0`
    - 策略停在离目标数米处
- 实验 3：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_18-41-26_capture_holdgoal_goal6_bonus10_v1`
  - 修改：
    - 保持实验 2
    - `target_bonus_ratio: 0.03 -> 0.10`
  - 结果：
    - `progress` 已掉到接近零 / 负值
    - `target_bonus = 0`
- 实验 4：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_18-44-04_capture_holdgoal_goal6_bonus10_reverse_v1`
  - 修改：
    - 保持实验 3
    - `base_allow_reverse: False -> True`
  - 结果：
    - `target_bonus` 仅偶发非零
    - `goal_yaw_error_abs ≈ 0.708 rad`
    - `Loss/value ≈ 214.7`
- 本轮统一结论：
  - 当前 active Stage0 仍然是 tracking-style shaping 任务
  - 不能仅靠：
    - 单目标保持
    - 缩短目标距离
    - 增大 terminal bonus
    - 放开倒车
    这些局部修改，直接把它变成稳定的 terminal capture 任务
- 已在实验结束后把 active 默认配置恢复为：
  - `resampling_time = 8.0`
  - `goal_distance = 12.0`
  - `target_bonus_ratio = 0.03`
  - `base_allow_reverse = False`
- 同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前“终端捕获”方向已经有了明确的反例证据。
- 如果后续还要继续推进这个方向，下一步不应再只改命令几何，而应回到任务定义层重新处理 terminal phase 机制。

已完成：
- 完成 `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_18-02-38_axis_usage_probe_v1` 的整轮训练与最终诊断。
- 本轮完整跑满：
  - `600 / 600`
- 导出并读取：
  - `tensorboard_export/latest_values.csv`
  - `tensorboard_export/summary.json`
  - 分轴球铰 `limit_usage_max_raw / mean_raw / pos_raw` 标量
- 当前最终结果：
  - `Train/mean_reward ≈ 616.77`
  - `Train/mean_episode_length = 1439.0`
  - `Termination/time_out_rate = 1.0`
  - `Termination/ball_joint_limit_rate = 0.0`
  - `Tracking/goal_pos_error ≈ 7.09 m`
  - `Tracking/goal_yaw_error_abs ≈ 0.0629 rad`
  - `Reward/target_bonus = 0.0`
  - `Loss/value ≈ 0.315`
- 分轴诊断结论：
  - 这轮里 `ball_joint_limit_rate` 非零只出现在较早阶段，共约 `15` 个 step
  - 主导责任轴是：
    - `spm1_platform_joint_z`
  - 物理上对应：
    - 前模块 `yaw`
  - 在有 `ball_joint_limit_rate` 的 step 上，这一轴的 `limit_usage_max_raw` 始终最高，峰值约：
    - `0.966`
  - 到训练末段，六个球铰轴都回到了安全区
- 当前更新后的判断：
  - 当前 8 维动作空间 + allocator 主线已成为当前最健康的 Stage0 主线
  - “后段球铰越界持续抬升”不再是当前默认结论
  - 新的主要问题变成：
    - 策略已经学会高质量推进和 yaw 对准
    - 但 `target_bonus` 仍始终为 `0`
    - 说明它还没有稳定进入最终成功区

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已经用完整 run 推翻了“后段 ball joint 必然重新抬升”的临时判断。
- 当前后续若要处理球铰软约束，应优先怀疑前模块 `yaw`，而不是对六个轴一视同仁。

已完成：
- 按用户要求再次启动一轮 Stage0 真实训练：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_18-02-38_axis_usage_probe_v1`
- 本轮训练目的不是修改主线配置，而是利用刚补充的分轴球铰日志埋点，直接观察：
  - 前/后模块哪一轴最先逼近球铰边界
- 当前训练已稳定跑到约：
  - `52 / 600`
- 当前中期状态：
  - `Termination/ball_joint_limit_rate = 0.0`
  - `Termination/time_out_rate = 1.0`
  - `Train/mean_episode_length = 1439.0`
  - `Tracking/goal_pos_error ≈ 9.16 m`
  - `Tracking/goal_yaw_error_abs ≈ 0.406 rad`
  - `Reward/longitudinal_slip_gate ≈ 0.0065`
  - `Reward/lateral_slip_gate ≈ 0.0088`
  - `Reward/composite_gate ≈ 0.281`
- 当前判断：
  - 这轮训练结构与前一轮 `action8_allocator_v1` 中期表现基本一致
  - 当前还没有出现球铰越界
  - 下一步应继续盯分轴 `limit_usage_max_raw`，而不是只看 aggregate 的 `ball_joint_limit_rate`

修改文件：
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前新的分轴探针 run 已经开始提供后续定位依据。
- 只要后段出现球铰越界，就可以直接用每一轴的 `limit_usage_max_raw` 判断责任轴。

已完成：
- 围绕 `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_17-33-20` 做“为什么更接近目标后 ball joint limit 抬升”的针对性分析。
- 额外对齐并检查了以下时序量：
  - `ball_joint_limit_rate`
  - `goal_pos_error`
  - `goal_yaw_error_abs`
  - `progress`
  - `heading_gate`
  - `ball_joint_pos_abs_mean_raw`
  - `ball_joint_target_error_abs_mean_raw`
  - `ball_joint_vel_abs_mean_raw`
  - `Action/policy_abs_mean`
- 同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前更准确的解释不是：
  - “快到点所以自然越界”
- 而是：
  - 随着策略更会推进和对准目标，它开始更主动地消耗球铰姿态余量
- 主要依据：
  - 后段 `heading_gate ≈ 0.96`
  - `progress ≈ 1.14`
  - `Action/policy_abs_mean ≈ 0.57`
  - `ball_joint_target_error_abs_mean_raw` 与 `ball_joint_pos_abs_mean_raw` 同步抬升
- 同时排除了几类旧问题：
  - `tilt_deg` 很低
  - `roll_gate = 1.0`
  - `head_tail_roll_limit_rate = 0.0`
  - `Loss/value` 低
- 当前判断：
  - 主因不是姿态失稳，也不是 critic 发散
  - 主因是：
    - reward 没有对“逼近球铰限位”做软惩罚
    - 新动作空间下球铰姿态成为帮助 allocator 完成有效推进/转向的直接杠杆
    - 策略会主动用球铰余量换 `progress` 和 `heading_gate`
- 另一个重要结论：
  - `ball_joint_pos_abs_mean_raw ≈ 0.17 ~ 0.18 rad`
    不代表整体安全
  - 因为 termination 只要任一单轴超界就触发
  - 单个球铰轴逼近极限会被均值掩盖

## 2026-04-18

已完成：
- 按用户要求启动一轮当前 reward 分支的真实 GPU 训练：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-18_11-08-59_66obs_longslip_cost_v1`
- 本轮训练使用当前代码主线：
  - `66` 维观测
  - `8` 维动作
  - `target_bonus + gated_progress - longitudinal_slip_cost_penalty`
  - `composite_gate = (heading_gate + lateral_slip_gate) / 2`
  - `longitudinal_slip_cost_penalty = 0.25 * relu(mean_abs_long_slip - 0.3)^2`
- 训练在确认失败模式后提前停止：
  - `iteration 230 / 1000`
- 导出了当前 run 的 TensorBoard 标量：
  - `tensorboard_export/summary.json`
  - `tensorboard_export/latest_values.csv`
- 同时重新导出了历史对照 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-17_22-34-48_exp3_goal8_explicit_slip_cost_v1`
- 按用户要求，不再把本轮综述背景候选文献放入已有 Zotero 集合，而是新建独立顶层集合：
  - `综述背景候选-复杂地形_铰接_RL_球并联-2026-04-17`
  - `collection_key = CREC6ZEZ`
- 本轮共处理 `27` 篇文献：
  - A 类 `14` 篇
  - B 类 `8` 篇
  - C 类 `5` 篇
- 写入结果：
  - `19` 篇为新建条目
  - `8` 篇为 Zotero 库中已有条目归入新集合
- 当前新集合已核对为顶层集合：
  - `parentCollection = false`
  - `numItems = 27`
- 本轮对已有 collection 的处理口径：
  - 不把新筛文献导入旧 `核心参考-RL、Sim-to-Real` 作为目标集合
  - 旧集合结构未被当作本轮导入目标继续使用
- 本轮同时给条目补充了分类标签，便于后续按：
  - `A/B/C`
  - 综述背景用途
 继续筛读和写作

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 reward 分支不是训练炸掉，而是掉进了明显的保守局部最优。
- 到停止时，当前 run 主要指标为：
  - `Train/mean_reward ≈ 10.44`
  - `Train/mean_episode_length ≈ 822.90`
  - `goal_pos_error ≈ 7.76 m`
  - `goal_completion_pct ≈ 3.01%`
  - `goal_yaw_error_abs ≈ 0.438 rad`
  - `|longitudinal slip| ≈ 0.385`
  - `|slip angle| ≈ 0.179 rad`
  - `tilt_deg ≈ 0.123`
  - `ball_joint_limit_rate ≈ 0.075`
  - `progress ≈ 0.0281`
  - `gated_progress ≈ 0.0233`
- 当前判断：
  - 显式 `long slip cost` 的确强力压低了纵滑和侧滑
  - 但策略并没有学会“低滑移且持续推进”
  - 而是学成了“少动少滑、基本不前进”的保守策略
- 与 `2026-04-17_22-34-48_exp3_goal8_explicit_slip_cost_v1` 对照看：
  - 当前分支 traction 指标更低
  - 但任务完成度显著更差
  - 因此这版 reward 不能直接提升为主线默认

已完成：
- 围绕用户提出的“为什么总是在高滑移和到达目标之间 tradeoff”做了一次结构性根因分析。
- 对齐检查了以下代码路径：
  - `mdp/actions.py`
  - `base/env.py`
  - `kinematics/wheel_speed_allocator.py`
  - `mdp/rewards.py`
  - `mdp/terminations.py`
  - `mdp/commands.py`
- 同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

产出/结论：
- 当前反复出现的“高滑移换一些接近目标”与“低滑移但走不过去”并不只是 reward 权重问题。
- 更深层主因是：
  - Stage0 任务要求 policy 学“稳定到点”
  - 但执行层只提供了开环的高层底盘命令到 wheel speed 的运动学映射
  - 对实际底盘 twist、附着、滑移和牵引没有闭环责任
- 因此 policy 最容易学到的不是“干净地滚动到点”，而是：
  - 利用球铰姿态改变接触几何和法向载荷
  - 通过横滚、抬前车、硬挪和拖拽去换一点距离缩短
- 当前 Stage0 也还不是“目标频繁变化下协同转向”的任务：
  - `resampling_time = episode_length = 16 s`
  - 所以现有环境并不能验证“快速协同转向到新目标”这个更强的问题

已完成：
- 按用户要求重写并扩充 `docs/RL阶段训练参数一览表.md`，使其与当前 Stage0 实际源码完全对齐。
- 新文档现在系统记录了当前 RL 环境的：
  - 任务定义
  - scene / sim / actuator 参数
  - command 采样公式
  - action 语义与映射公式
  - measured-geometry wheel allocator 的输入、输出、几何常数与 Jacobian 结构
  - observation 拼接项、公式、scale、噪声状态
  - reward 全部公式
  - termination 公式
  - reset / terrain / sensor / PPO 配置
- 新建问题分析文档：
  - `docs/Stage0问题演化与当前瓶颈分析.md`
- 该文档基于 `conversation_history.md` 与近期代表性训练结论，集中整理了：
  - 问题如何一步步暴露
  - 做过哪些 reward / action / allocator / task-geometry 改动
  - 哪些改动改善了局部现象
  - 为什么仍然没有得到健康主线
  - 当前真正的结构性瓶颈是什么

修改文件：
- `docs/RL阶段训练参数一览表.md`
- `docs/Stage0问题演化与当前瓶颈分析.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 的长文档环境说明已经和源码对齐，不再沿用旧 reward / 旧 allocator / 旧 run 口径。
- 当前 Stage0 的问题演化与失败模式也已经有集中整理文档，后续不需要再从聊天记录中反复回溯。

已完成：
- 按用户要求将 Stage0 默认环境从同日 `2m` 重构分支回退到之前最健康的 `8m` 版本。
- 回退并对齐了以下源码：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- 将当前默认口径重新同步到文档：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `docs/RL阶段训练参数一览表.md`
  - `docs/Stage0问题演化与当前瓶颈分析.md`
- 完成静态检查：
  - `python3 -m py_compile`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `docs/RL阶段训练参数一览表.md`
- `docs/Stage0问题演化与当前瓶颈分析.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前默认 Stage0 已恢复为：
  - `8m / 16s / 66obs / 8动作 / measured-geometry allocator / 单段 tracking reward`
- 当前默认 reward 已恢复为：
  - `total_reward = target_bonus + gated_progress`
  - `gated_progress = progress * composite_gate * roll_gate`
  - `composite_gate = (heading_gate + longitudinal_slip_gate + lateral_slip_gate) / 3`
- 当前默认 termination 已恢复为：
  - `bad_orientation`
  - `head_tail_roll_out_of_bounds`
  - `ball_joint_out_of_bounds`
  - `time_out`
- `2m` 的 pose/capture/traction-aware 重构分支仍保留为同日实验记录，但不再是当前继承的默认主线。

已完成：
- 按用户确认继续重构当前 Stage0：
  - 动作空间从 `8` 维改成 `12` 维
  - 语义从：
    - `6球铰 + 2底盘平面命令 + allocator`
    改成：
    - `6球铰 + 6轮速直驱`
- 当前执行链路已经不再使用速度分配模型：
  - 删除了 env 里的 `base_planar_command -> transform -> allocator` 活跃路径
  - 改为 wheel action 直接映射到轮速目标
- 当前 wheel action 映射公式：
  - `wheel_speed_target = action * wheel_action_scale * wheel_joint_velocity_limit_sim`
  - 默认：
    - `wheel_action_scale = 1.0`
    - `wheel_joint_velocity_limit_sim = 12.0`
- 同时按用户要求把 `longitudinal slip` 从 gate 中移出，改为显式阈值后二次惩罚：
  - `longitudinal_slip_cost = mean(abs(long_slip_6))`
  - `longitudinal_slip_cost_penalty = 0.25 * relu(longitudinal_slip_cost - 0.3)^2`
- reward 当前已改为：
  - `total_reward = target_bonus + gated_progress - longitudinal_slip_cost_penalty`
  - `gated_progress = progress * composite_gate * roll_gate`
  - `composite_gate = (heading_gate + lateral_slip_gate) / 2`
- 由于 `last_action` 维度变化，Actor / Critic 观测维度同步从：
  - `66 / 66`
  - 改为：
  - `70 / 70`
- 本轮还同步更新了 step 指标和 TensorBoard tag：
  - 去掉旧的 `longitudinal_slip_gate`
  - 增加：
    - `Reward/longitudinal_slip_cost`
    - `Reward/longitudinal_slip_cost_penalty`
    - `Action/wheel_velocity_target_abs_mean_raw`
- 完成静态检查：
  - `python3 -m py_compile`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `docs/RL阶段训练参数一览表.md`
- `docs/Stage0问题演化与当前瓶颈分析.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前默认主线已不再和旧 `8动作 allocator` 分支同口径。
- 当前默认 Stage0 已变为：
  - `8m / 16s / 70obs / 12动作直驱 / long slip显式代价`
- 这轮只完成了代码与文档重构，还没有基于新主线启动训练。

已完成：
- 按用户要求对新主线 `12动作直驱 + long slip显式代价` 启动首轮真实 GPU 训练：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-18_16-05-54_stage0_direct12_longslipcost_v1`
- 训练参数：
  - `task = CompleteCar-Stage0`
  - `num_envs = 64`
  - `max_iterations = 300`
- 实际在失败模式明确后主动停止：
  - `iteration 16 / 300`
- 已导出 TensorBoard：
  - `tensorboard_export/latest_values.csv`
  - `tensorboard_export/summary.json`
- 当前“综述背景主线/补充/球并联灵感来源”这批文献，已经与旧的 `RL + Sim-to-Real` 核心集合分离。
- 后续写背景综述、补 related work、继续加读书笔记时，应优先从新集合：
  - `综述背景候选-复杂地形_铰接_RL_球并联-2026-04-17`
 继续展开。

已完成：
- 按用户要求对“基于强化学习的关节式地面移动轮式机器人”做一轮 Scholar + CNKI 联合检索。
- Google Scholar 当前使用的两条主检索式为：
  - `"rough terrain" vehicle "deep reinforcement learning"`
  - `"actively articulated suspension" rough terrain robot`
- 当前在 Scholar 侧再次确认的高相关主线文献包括：
  - `Control of rough terrain vehicles using deep reinforcement learning`
  - `Deep reinforcement learning for safe local planning of a ground vehicle in unknown rough terrain`
  - `A sim-to-real pipeline for deep reinforcement learning for autonomous robot navigation in cluttered rough terrain`
  - `Actively articulated wheeled architectures for autonomous ground vehicles-opportunities and challenges`
  - `Design and field testing of a rover with an actively articulated suspension system in a Mars analog terrain`
  - `Actively articulated suspension for a wheel-on-leg rover operating on a martian analog surface`
- CNKI 当前原计划使用 `kns.cnki.net` / `www.cnki.net` 直接检索：
  - 但浏览器访问时遇到证书错误
  - 因此本轮改为通过：
    - CNKI 关联官方期刊门户
    - CNKI 镜像索引页
    做保守抓取
- CNKI 侧当前抓到的更可复用文献主要集中在两类：
  - 强化学习/深度强化学习与移动机器人路径规划、运动控制综述或方法
  - 关节式/轮腿式/越障移动机器人结构设计与仿真
- 当前可复用的中文侧代表文献包括：
  - `基于深度强化学习的机器人运动控制研究进展`
  - `基于强化学习的移动机器人路径规划研究综述`
  - `基于深度强化学习的移动机器人三维路径规划方法`
  - `轮腿式移动机器人的设计与研究`
  - `基于ADAMS的六轮自适应越障机器人的设计与研究`
  - `一种小型移动机器人行走机构的设计与分析`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 这轮训练没有数值炸掉，也没有姿态终止：
  - `time_out_rate = 1.0`
  - `terminated_rate = 0`
  - `bad_orientation / head_tail_roll / ball_joint_limit = 0`
- 但很快形成了稳定坏平衡，而不是健康收敛：
  - `goal_pos_error: 8.05 m -> 6.72 m`
  - `goal_completion_pct: 0.13% -> 16.02%`
  - `goal_success_rate = 0`
  - `target_bonus = 0`
  - `|longitudinal slip|: 2.46 -> 2.26`
  - `|slip angle|: 0.44 -> 0.52 rad`
  - `lateral_slip_gate: 0.0249 -> 0.0102`
  - `gated_progress: -0.013 -> 0.080`
  - `longitudinal_slip_cost_penalty: 1.20 -> 1.01`
  - `Reward/total: -1.21 -> -0.93`
  - `Train/mean_reward: -162 -> -995`
- 当前判断：
  - 主要问题不是翻车或不稳定，而是：
    - 高纵滑
    - 有少量前进
    - 始终不到点
    - 长期超时
  - 最可能原因是：
    - 轮速直驱把动作语义压得过低，policy 需要同时学六轮协调和球铰协调，缺少车辆级运动先验
    - 显式 `long slip` 惩罚没有把策略拉进低滑移区，只是把总回报压成持续负值

## 2026-04-19

已完成：
- 按用户给定数值重设当前 Stage0 PPO 超参数，并把 `adam_eps` 接入本地 PPO 实现。
- 本轮 PPO 配置修改为：
  - `num_steps_per_env = 512`
  - `max_iterations = 700`
  - `save_interval = 100`
  - actor / critic hidden dims：
    - `[256, 256] / [256, 256]`
  - `activation = relu`
  - `init_std = 0.20`
  - `log_std_min = -4.0`
  - `log_std_max = 0.0`
  - `value_loss_coef = 0.5`
  - `entropy_coef = 5e-4`
  - `num_learning_epochs = 5`
  - `num_mini_batches = 16`
  - `learning_rate = 1e-4`
  - `gamma = 0.99`
  - `lam = 0.95`
  - `desired_kl = 0.008`
  - `max_grad_norm = 0.5`
  - `adam_eps = 1e-5`
- 同时修改本地 PPO 优化器构造逻辑：
  - 当 optimizer 为 `adam / adamw` 时显式把 `eps` 传入优化器
- 本轮同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `docs/RL阶段训练参数一览表.md`
- 已完成静态检查：
  - `python3 -m py_compile`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/algorithms/ppo.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `docs/RL阶段训练参数一览表.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 active Stage0 PPO 配置已经不再是上一轮 bounded-policy 切换后的默认值，而是用户刚指定的新一组参数。
- 当前训练前还没有新 run，因此这次变更结论仍停留在“配置已生效、静态检查通过”，尚未进入训练效果判断。

已完成：
- 按用户要求对当前 Stage0 PPO 动作分布与动作执行链做稳定性整改，不再继续沿用“无界高斯采样 + 多重事后 clip”的旧路径。
- 本轮 PPO / 动作链源码修改：
  - 新增本地 `SquashedGaussianDistribution`
    - 采用 `tanh` squashed Gaussian 有界动作语义
    - `log_prob` 已加入 squashing 的变量替换修正
  - 将 actor 的 `std` 改为 `log_std` 参数化：
    - `std = exp(log_std)`
    - 当前 clamp 区间：
      - `log_std_min = -4.0`
      - `log_std_max = 0.5`
  - 取消 PPO wrapper 的前置 `clip_actions`
  - 取消 env preprocess 的前置动作 clip
  - 环境内部仅保留末端 safeguard：
    - 球铰目标映射时的范围保护
    - 轮速目标写入前的物理上限保护
- 本轮同步更新：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `docs/RL阶段训练参数一览表.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/modules/__init__.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/modules/distribution.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `docs/RL阶段训练参数一览表.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 PPO 动作语义已经切到 bounded policy 口径，旧的 wrapper / env 双前置 clip 不再是 active path。
- 已完成静态检查：
  - `python3 -m py_compile`
- 这轮还没有新训练 run，因此当前结论只到源码与静态检查层。
- 下一步应做短程训练验证：
  - rollout / KL / entropy / policy std 是否正常
  - `tanh` squashed log-prob 与真实执行动作是否保持一致
- 当前精确交集“关节式轮式地面机器人 + 强化学习 + 粗糙地形”在中文侧文献密度明显低于英文侧。
- 后续 related work 写作时，应以英文文献承担主技术主线，中文文献主要补：
  - RL 方法综述
  - 移动机器人路径规划综述
  - 关节式/轮腿式越障机构背景

已完成：
- 按用户要求，继续在 Google Scholar 上仅用英文检索词收缩“基于强化学习的关节式小车/关节式地面车辆”文献。
- 本轮新增检索式：
  - `"articulated vehicle" "reinforcement learning"`
  - `"articulated wheeled robot" "reinforcement learning"`
  - `"center-articulated vehicle" "reinforcement learning"`
- 当前直接命中的代表结果包括：
  - `Reinforcement learning for autonomous navigation of articulated vehicles`
  - `Advanced Kinematic Control and Reinforcement Learning Optimization for Center-Articulated Agricultural Rovers`
  - `DDPG-based controller of enhanced adaptive cruise control with lane-change assistance for an articulated vehicle`
- 当前更重要的检索判断：
  - 如果把英文检索词过度收紧到：
    - `articulated wheeled robot + reinforcement learning`
  - Google Scholar 召回会明显变少
  - 当前最有效的英文检索策略仍然是双线并行：
    - `rough terrain + vehicle + deep reinforcement learning`
    - `actively articulated suspension / articulated vehicle`
  - 再从两条线中人工筛出真正贴近“关节式小车”的文献

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 后续如果继续做英文检索，不应只盯着单一精确短语。
- 默认应保留：
  - 一条 RL 控制主线
  - 一条 articulated 结构主线
共同筛文献。

已完成：
- 按用户要求，将本轮 Google Scholar 精筛出的 8 篇“基于强化学习的关节式小车 / articulated vehicle”英文文献导入 Zotero 集合：
  - `核心参考-RL、Sim-to-Real`
  - `collection_key = P3ZIJTVJ`
- 本轮导入结果：
  - `3` 篇为新建条目
  - `5` 篇为 Zotero 库中已有条目归入该集合
- 新建条目包括：
  - `Actively articulated wheeled architectures for autonomous ground vehicles-opportunities and challenges`
  - `Reinforcement learning for autonomous navigation of articulated vehicles`
  - `Advanced Kinematic Control and Reinforcement Learning Optimization for Center-Articulated Agricultural Rovers: A Comparative Study of Tracking Accuracy and Energy Efficiency`
- 已归入现有条目的文献包括：
  - `Control of rough terrain vehicles using deep reinforcement learning`
  - `Deep reinforcement learning for safe local planning of a ground vehicle in unknown rough terrain`
  - `A sim-to-real pipeline for deep reinforcement learning for autonomous robot navigation in cluttered rough terrain`
  - `Design and field testing of a rover with an actively articulated suspension system in a Mars analog terrain`
  - `Actively articulated suspension for a wheel-on-leg rover operating on a martian analog surface`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前“关节式小车 / articulated vehicle + RL”这条英文文献线已经正式并入核心 Zotero 集合。
- 后续如果要继续做 cited-by 扩展或读书笔记，可以直接从 `核心参考-RL、Sim-to-Real` 接着做。

已完成：
- 按用户要求，将当前 RL 环境动作空间与论文第 3 章底层模型重新对齐：
  - 当前 policy 动作改为 `8` 维统一高层动作：
    - 前 `2` 维为中模块期望平面运动命令分支
    - 后 `6` 维为球铰期望构型分支
  - 环境内部不再让 policy 直接输出六轮轮速
  - 当前轮速由 `wheel_speed_allocator.py` 根据：
    - 当前实际构型 `q`
    - 平面运动命令 `u_v`
    - 固定结构参数
    解析得到
- 已按论文当前推导重写 `wheel_speed_allocator.py`：
  - 当前实现为 `J_w(q) ∈ R^{6×2}`
  - 不再使用旧的 `qdot` 输入与 `12` 列广义速度 Jacobian
  - 不再使用 `transform_planar_command`
  - 输出顺序已对齐环境轮关节顺序：
    - `body L/R`
    - `head L/R`
    - `tail L/R`
- 已同步修改：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `docs/RL阶段训练参数一览表.md`
  - `logs/daily_work_log.md`
- 已完成验证：
  - `python3 -m py_compile` 通过
  - `python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py` 通过
- 当前结论：
  - RL 主线动作语义已经切换到与论文一致的：
    - `u = [u_v, q^d]`
  - 当前单帧观测维度随 `last_action` 同步变为：
    - actor / critic = `18 / 18`
  - 这次改动已经完成源码接线与数值校验，但还没有做新的真实训练 run

已完成：
- 按用户要求增强 Isaac Sim 键盘控制脚本的终端状态输出：
  - 修改 `scripts/isaac_sim/control_keyboard.py`
  - 当前脚本会按固定周期回读仿真中的实际球铰关节位置，而不是只打印启动信息
  - 终端新增输出：
    - 前球铰 / 后球铰当前关节角 `z/y/x`
    - 前车 / 后车相对中车姿态角 `yaw/pitch/roll`
  - 当前打印周期：
    - `0.5 s`
- 本轮实现口径：
  - 当前等效串联模型下：
    - `spm*_platform_joint_z -> yaw`
    - `spm*_platform_joint_y -> pitch`
    - `spm*_platform_joint_x -> roll`
  - 因此终端里的两组输出是同一实际状态的两种命名方式，不是两套独立状态量
- 已完成验证：
  - `python3 -m py_compile scripts/isaac_sim/control_keyboard.py` 通过
- 修改文件：
  - `scripts/isaac_sim/control_keyboard.py`
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

## 2026-04-20

已完成：
- 按用户要求，将论文第 3 章正式回写为保留球铰完整 `6` 自由度的通用口径，不再沿用此前 `Stage0` 候选推导稿中的偏航约化写法。
- 已在 `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex` 中新增球铰姿态规划器建模：
  - `\dot{\mathbf q}^{cmd} = \operatorname{sat}(\mathbf K_q(\mathbf q^d - \mathbf q))`
  - `\mathbf q^{cmd} = \operatorname{sat}(\mathbf q + \Delta t\,\dot{\mathbf q}^{cmd})`
- 已将六轮轮速解析分配由静态形式扩展为：
  - `\boldsymbol\Omega^d = \mathbf J_w(\mathbf q)\mathbf u_v + \mathbf J_q(\mathbf q)\dot{\mathbf q}^{cmd}`
- 已在第 3 章“代入具体结构参数向量后的最终解析结果”小节中补入：
  - 静态分配矩阵 `\mathbf J_w(\mathbf q)`
  - 构型变化率修正矩阵 `\mathbf J_q(\mathbf q)`
  - 六个车轮角速度目标的显式表达式
- 已完成论文主文件编译验证：
  - `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `chapter03.tex` 当前默认模型已经切换为“6 自由度球铰姿态规划器 + 构型变化率修正轮速分配”的通用口径。
- `docs/Stage0球铰姿态规划器与底层运动学模型推导.md` 仍保留为平地 `Stage0` 偏航约化候选稿，但不再代表论文主文默认模型。
- 本轮编译通过；当前剩余的 LaTeX 警告仅包含论文原有的两条缺失文献引用：
  - `fang2015survey`
  - `MATSUMURA2017566`

下一步建议：
- 若继续推进 RL 主线，需要明确当前环境是否回接论文新版中的 `\mathbf J_q(\mathbf q)\dot{\mathbf q}^{cmd}` 项，还是暂时保留静态 `\mathbf J_w(\mathbf q)\mathbf u_v` 作为 `Stage0` 平地主线实现。

## 2026-04-21

已完成：
- 按用户要求新增“终端 / 对话输出公式记法”规则：
  - 后续默认使用可直接阅读的数学符号
  - 不再默认直接输出原始 LaTeX 源记法
  - 仅在用户明确要求 LaTeX 源码，或任务本身就在处理 LaTeX / Markdown 数学源码时，才展示原始 LaTeX
- 已将该规则写入：
  - `AGENTS.md`
- 已同步更新项目记忆：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `AGENTS.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 以后终端里的公式讲解应优先写成可直接阅读的数学符号，例如：
  - `q`
  - `qᵈ`
  - `q̇_cmd`
  - `u_v*`
  - `Ω_ref`
  - `τ_cmd`
- 仓库 Markdown 公式规则与论文 LaTeX 源文件写法不受本轮影响。

## 2026-04-21

已完成：
- 按用户要求对 `chapter03.tex` 做整章级重写与润色：
  - 重写了章节开头总述，明确区分：
    - 名义运动学参考层
    - 接触感知低滑移执行层
  - 统一了全章关键符号口径：
    - `\mathbf u_v^d`
    - `\mathbf q`
    - `\mathbf q^d`
    - `\mathbf q^{cmd}`
    - `\dot{\mathbf q}^{cmd}`
    - `\boldsymbol\Omega^d`
    - `\boldsymbol\Omega_{ref}`
    - `\boldsymbol\tau^{cmd}`
  - 重写了“高层命令与底层输出定义”小节，使名义参考层与最终执行层的边界更清楚
  - 重写了“面向低滑移的接触感知轮级牵引分配”小节：
    - 明确写清 `\mathbf J_w(\mathbf q)` 与 `\mathbf J_q(\mathbf q)` 没有失效
    - 它们仍通过轮心速度表达、整形系数 `\mathbf a_w,b_w` 与 `\boldsymbol\Omega_{ref}` 进入低滑移执行层
    - 明确写清当前车轮执行层是“以轮速参考为中间量的力矩驱动”
  - 重写了章节结尾总结：
    - 输入输出总结与正文分层口径一致
    - 不再混写 `\boldsymbol\Omega^d`、`\boldsymbol\Omega_{ref}` 与 `\boldsymbol\tau^{cmd}`
- 已完成编译验证：
  - `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 通过
- 当前仍保留的论文既有问题：
  - `fang2015survey` 文献缺失
  - `MATSUMURA2017566` 文献缺失

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 第 3 章当前已经从“公式正确但层次容易混淆”的写法，收敛为“符号唯一、层次清晰、推导不断裂”的统一版本。
- 当前第 3 章可直接按以下顺序讲解：
  - 高层期望量
  - 球铰姿态规划器
  - 名义轮速参考层
  - 低滑移执行层
  - 最终轮级扭矩命令
- 当前编译通过；本轮没有引入新的 LaTeX 报错，剩余 warning 仍是历史遗留文献问题。

## 2026-04-21

已完成：
- 按用户要求清理 Stage0 动作链与车轮执行链中的死代码：
  - 删除 no-op 的 `preprocess_policy_actions(...)`
  - 删除旧的 `apply_wheel_velocity_targets(...)`
  - 删除环境中未使用的：
    - `_policy_actions`
    - `_processed_actions`
    - `_joint_vel_targets`
- 已将环境动作链收敛为：
  - policy 原始动作直接进入动作映射
  - 球铰输出 `q_cmd`
  - 车轮输出 `τ_cmd`
- 已同步清理相关日志与文档口径：
  - 不再记录 `Action/processed_abs_mean`、`Action/processed_std`
  - 更新 `docs/RL阶段训练参数一览表.md`
  - 更新 `docs/current_status.md`
  - 更新 `docs/complete_car_direct_workflow_architecture.md`
  - 更新 `docs/conversation_history.md`
- 已完成静态检查：
  - `python3 -m py_compile RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/complete_car_direct_workflow_architecture.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 已不存在独立动作预处理层，`last_action` 记录的是上一时刻 policy 原始动作。
- 当前车轮执行器只保留 effort / torque 写入路径，旧 wheel velocity target 写入残留已清理。
- 后续代码讲解与训练审查都应直接按“原始动作 -> 映射 -> 球铰位置目标 / 车轮力矩目标”解释。

## 2026-04-21

已完成：
- 按用户要求重写 `docs/RL阶段训练参数一览表.md`，使其与当前 `CompleteCar-Stage0` 实际运行链完全对齐。
- 已按当前 active path 重新梳理并写清：
  - 动作空间与高层命令映射
  - 球铰姿态规划器
  - 低滑移接触感知 allocator
  - 命令采样
  - 观测构造
  - reward
  - termination
  - reset / randomization
  - terrain / sensors
  - PPO / train entry
- 已在文档中明确区分：
  - 当前真正进入训练闭环的量
  - 只用于低层执行与日志诊断的量
  - 虽然配置存在但当前未进入 active path 的字段
- 已同步更新项目记忆：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `docs/RL阶段训练参数一览表.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `docs/RL阶段训练参数一览表.md` 当前可以直接作为 Stage0 RL 环境逐环节审查的统一入口。
- 文档口径已经与当前“高层动作 -> 球铰姿态规划器 -> 低滑移 allocator -> 球铰位置目标 + 车轮力矩目标”的主线一致。
- 后续若继续查训练行为异常，应优先从该文档核对 active path，而不是回到旧版参数总表。

## 2026-04-21

已完成：
- 按用户要求从当前 Stage0 active reward 中删除 `oscillation`。
- 已同步清理奖励主链中的活跃引用：
  - `mdp/rewards.py`
  - `base/env.py`
  - `base/complete_car_cfg.py`
  - `baseline/complete_car_stage0_cfg.py`
  - `rsl_rl/utils/logger.py`
- 已同步更新项目记忆与参数文档：
  - `docs/current_status.md`
  - `docs/RL阶段训练参数一览表.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `docs/current_status.md`
- `docs/RL阶段训练参数一览表.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 reward 只保留 5 项：
  - `distance_to_target`
  - `reached_target`
  - `angle_to_target`
  - `far_from_target`
  - `angle_diff`
- `compute_reward_terms(...)` 已不再依赖 `current_actions` 和 `last_actions`。
- `last_action` 当前仅作为 48 维观测中的上一时刻动作信息保留，不再承担动作振荡惩罚的输入角色。

## 2026-04-21

已完成：
- 按用户要求核对“step metrics 不打印项”是否会进入 TensorBoard。
- 已确认：
  - 当前绝大多数不进终端的 raw diagnostics 仍会写入 TensorBoard
  - 当前 Stage0 明确不会产出的只有：
    - `Critic/height_patch_mean`
    - `Critic/height_patch_max`
- 已从 `base/env.py` 中删除上述两个 dead step metrics。
- 已同步更新项目记忆：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 里，不进终端不等于不写 TensorBoard。
- 保留下来的 step metrics 仍可用于后续逐项筛查。
- 不会产出的 critic 高度 patch 两个空白项已清理。

## 2026-04-21

已完成：
- 按用户指定顺序重构 Stage0 终端日志打印顺序与 TensorBoard 输出口径。
- 已将终端打印固定为用户指定的 24 个高信号 tag 顺序。
- 已将 TensorBoard extras 写入改为独立白名单，不再默认把所有 extras 都写入面板。
- 已按用户要求同步删除未列出的 active step metrics：
  - `Observation/turn_radius_raw`
  - step 级 `Command/goal_target_*_world`
  - `Observation/head_roll_pitch_abs_mean_raw`
  - `Observation/tail_roll_pitch_abs_mean_raw`
  - `Observation/goal_rel_*_raw`
  - `Observation/last_action_abs_mean_raw`
- `Termination/terminated_rate` 当前保留终端打印，但已不再写入 TensorBoard。
- 同时清理了观测辅助函数中的失活项：
  - `head_roll_pitch`
  - `tail_roll_pitch`
- 已同步更新：
  - `docs/current_status.md`
  - `docs/RL阶段训练参数一览表.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `docs/current_status.md`
- `docs/RL阶段训练参数一览表.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 的终端面板与 TensorBoard 面板已不再共用同一套 tag 保留规则。
- 终端、TensorBoard、环境 step metrics 三处日志口径已经重新对齐到用户指定集合。

## 2026-04-21

已完成：
- 按用户要求停止使用 `MinerU`，改用 `opendataloader-pdf` 执行 PDF 转 Markdown：
  - 仓库已克隆到：
    - `/home/lbz/opendataloader-pdf-fulltty`
  - 本机源码构建受 `mvn` 缺失阻塞，因此本轮采用：
    - `/tmp/opendataloader-pdf-venv` 虚拟环境
    - 安装已发布的 `opendataloader-pdf` 包
  - 在当前终端环境下，已确认必须使用：
    - `JAVA_TOOL_OPTIONS=-Djava.awt.headless=true`
    否则会因 `DISPLAY=:0` 触发 Java AWT/X11 报错
- 已完成研究背景/综述第一批与第二批共 `22` 篇核心文献的 Markdown 转换：
  - 输出目录：
    - `docs/literature/opendataloader_output/`
  - 已核对结果：
    - 预期 `22` 篇
    - 实际 `22` 篇
    - 缺失 `0` 篇
- 本轮完成的文献包括：
  - 第一批 `15` 篇：
    - `Borges 2022`
    - `Papadakis 2013`
    - `Prado 2018`
    - `Iagnemma 2003`
    - `Kayacan 2018`
    - `Lei 2021`
    - `Li 2021`
    - `Bai 2019`
    - `Gosselin & Hamel 1994`
    - `Abe 2021`
    - `Josef & Degani 2020`
    - `Hu 2021`
    - `Wiberg 2022`
    - `Wiberg 2024`
    - `Henderson 2019`
  - 第二批 `7` 篇：
    - `Cordes 2017`
    - `Cordes 2018`
    - `Lim 2009`
    - `Huang 2024`
    - `Xu 2024`
    - `Mortensen & Bøgh 2024`
    - `Patterson 2024`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前研究背景/综述的主干文献已经具备可直接阅读的 Markdown 工作底稿。
- 后续文献阅读应优先读取：
  - `docs/literature/opendataloader_output/*.md`
  再回查原始 PDF 做图表、公式、页码核对。

下一步：
- 进入这 `22` 篇文献的结构化阅读，按七个综述模块提炼可直接写入论文的背景与相关工作骨架。

已完成：
- 按用户给定的 7 个综述写作模块，对 `docs/literature/` 本地文献库完成首轮筛选与分层：
  - 主干文献池
  - 近年补充文献
  - 延后阅读/暂不作为主干的论文
- 已核对本地文献库形态：
  - 当前基本仍为 PDF
  - 存在重复文件与 `_zh-CN_dual` 双语版本
  - 存在少量学位论文与预印本，不适合直接作为主干引用
- 已形成首轮主干清单：
  - 复杂地形/可通行性综述：
    - `Borges 2022`
    - `Papadakis 2013`
  - 铰接/主动悬架/传统控制代表文献：
    - `Iagnemma 2003`
    - `Cordes 2017`
    - `Kayacan 2018`
    - `Lei 2021`
    - `Li 2021`
  - 球面并联启发文献：
    - `Bai 2019`
    - `Gosselin & Hamel 1994`
    - `Abe 2021`
  - RL 主干文献：
    - `Josef & Degani 2020`
    - `Hu 2021`
    - `Wiberg 2022`
    - `Wiberg 2024`
    - `Xu 2024`
    - `Mortensen & Bøgh 2024`
  - RL 方法学局限文献：
    - `Henderson 2019`
    - `Patterson 2024`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前研究背景/综述的文献处理方式已明确：
  - 不再对整库 PDF 无差别处理
  - 先围绕七模块建立主干文献池
  - 再按优先级把核心文献转为 `md`
- 当前不建议先作为主干的文献包括：
  - 学位论文：
    - `Attard 2023`
    - `Mehta 2025`
  - 预印本：
    - `Fue 2026`
  - 纯机构学闭式解细节论文：
    - 暂留待机构章节再用

下一步：
- 先对主干文献去重并确定 canonical 版本，再优先转换第一批 `md`，随后进入结构化阅读与综述笔记。

已完成：
- 修正 `Tracking/goal_success_rate` 的统计时序：
  - 已改为和 `Termination/success_rate` 一样，使用 reset 批次的 `_last_done_terms["is_success"]`
  - 已从 step metrics 中移除旧的 post-reset 重算路径
- 清理 rollout 热路径：
  - 删除 `_get_rewards()` 中未被 reward 使用的 contact-force / `raw_obs_terms` 死开销
  - 在 `_get_observations()` 中缓存 post-reset `relative_goal_commands` 与 `raw_obs_terms`
  - 让 `_collect_step_metrics()` 复用缓存，避免同一步重复 contact 查询
- 新增 Stage0 reward：
  - `progress_to_target`
  - `progress_to_target_clip_m = 0.25`
  - `progress_to_target_weight = 6.0`
- 更新日志与文档：
  - `Reward/progress_to_target` 已进入终端 / TensorBoard
  - `docs/RL阶段训练参数一览表.md` 已同步更新为 6 项 reward 口径
- 完成真实训练 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-21_16-56-14_success_fix_perf_fix_progress_reward_v1`
  - 共跑满 `150` 轮

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `docs/current_status.md`
- `docs/RL阶段训练参数一览表.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- success 统计口径已修正：
  - 新 run 中 `Tracking/goal_success_rate` 与 `Termination/success_rate` 逐轮完全一致
  - `max_abs_diff = 0`
- throughput 断崖已消失：
  - 旧 run 在 `110-130` 窗口内 `collection_time` 平均约 `12.69 s`
  - 新 run 同窗口内 `collection_time` 平均约 `7.89 s`
  - 新 run 到 `126-149` 窗口仍稳定在约 `7.86 s`
- progress reward 明显提升了逼近与成功率：
  - `goal_pos_error` 最低约 `1.51 m`
  - `goal_completion_pct` 最高约 `81.17%`
  - `goal_success_rate` 最高约 `0.5156`
  - 末轮 `goal_success_rate ≈ 0.2305`
  - 末轮 `time_out_rate ≈ 0.7695`
- 当前新的主问题：
  - 近目标朝向误差仍偏大
  - 中后段纵滑率重新升高
  - 策略已从“不会逼近”转成“会逼近且常有 success 脉冲，但还不能稳定、低滑移地完成”

## 2026-04-21

已完成：
- 跑满第三轮终点捕获导向 reward 的长回合真实训练：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-21_19-11-12_reward_terminal_capture_v2_250iter`
  - `max_iterations = 250`
  - `num_envs = 64`
- 全程监控训练终端日志，确认训练过程中：
  - 无启动报错或中途崩溃
  - `Tracking/goal_success_rate` 与 `Termination/success_rate` 一直一致
  - `iteration 100-128` 出现一次集中性的 `collection_time` spike，之后自行恢复
- 完成该 run 的 TensorBoard 标量导出与离线诊断：
  - 已生成 `tensorboard_export/summary.json`
  - 已生成 `tensorboard_export/latest_values.csv`

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 本轮训练完整跑满 `250` 轮，训练总时长约 `2473.55 s`
- 关键结果：
  - `Train/mean_reward`：
    - `0.706 -> 16.935`
    - 最高约 `17.94`
  - `goal_success_rate`：
    - 末轮约 `0.3125`
    - 最高约 `0.5576`
    - 最后 `50` 轮平均约 `0.3672`
  - `time_out_rate`：
    - 末轮约 `0.6875`
    - 最低约 `0.4424`
    - 最后 `50` 轮平均约 `0.6328`
  - `goal_pos_error`：
    - 末轮约 `1.859 m`
    - 最低约 `1.484 m`
  - `goal_heading_error_abs`：
    - 末轮约 `0.172 rad`
    - 最低约 `0.155 rad`
- 当前主问题：
  - 成功率已明显提升，但超时仍是主终止模式
  - `100+` 轮后位置误差不再继续收敛，terminal position capture 仍不稳定
  - 终端 heading 已较上一轮明显改善，但纵滑与侧滑仍偏高：
    - `wheel_longitudinal_slip_abs_mean_raw` 末轮约 `5.29`
    - `wheel_slip_angle_abs_mean_raw` 末轮约 `0.600 rad`
  - reward 后段仍以 `progress_to_target` 为最强 dense 项：
    - `progress ≈ 0.00712`
    - `distance ≈ 0.00513`
    - `angle_diff ≈ 0.00360`
  - `iteration 100-128` 存在暂态性能异常：
    - `collection_time` 平均约 `12.37 s`
    - `fps` 约 `2.6k`
    - 后续又恢复到 `~8.68 s / 3.69k`

## 2026-04-22

已完成：
- 按用户要求将 `far_from_target` 从 Stage0 reward 中删除，只保留为 termination 护栏。
- 同步清理 reward 配置、episode logger 与参数文档中的旧口径：
  - active reward 现固定为 `7` 项
  - `Reward/far_from_target`、`episode/far_from_target`、`episode_per_step/far_from_target` 已移除
- 补跑静态检查：
  - `python3 -m py_compile ...` 通过

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`
- `docs/current_status.md`
- `docs/RL阶段训练参数一览表.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 reward 口径为：
  - `distance_to_target`
  - `progress_to_target`
  - `reached_target`
  - `angle_diff`
  - `turn_speed_penalty`
  - `slip_penalty`
  - `differential_turn_cost`
- `far_from_target` 现在只负责：
  - `termination` 判定
  - `Termination/far_from_target_rate` 诊断统计
- 当前代码主线中不再存在 `far_from_target_weight`。
- 本轮未补跑 Isaac Lab runtime smoke：
  - 当前终端环境仍缺少 `isaaclab`
  - 运行 `scripts/train.py` 仍会卡在环境依赖，而不是 reward 代码本身

## 2026-04-23

已完成：
- 使用 `opendataloader-pdf` 将以下 `3` 篇中文铰接车辆相关文献转换为 Markdown：
  - `双铰接轮式越野工程车辆机液复合驱动系统研究_宁悦.pdf`
  - `具有二自由度铰接式车体的轮式机器人稳定性研究_李阳.pdf`
  - `具有二自由度铰接车体轮式机器人牵引力对稳定性的影响研究_马玉玺.pdf`
- 转换产物已写入：
  - `docs/literature/opendataloader_output/双铰接轮式越野工程车辆机液复合驱动系统研究_宁悦.md`
  - `docs/literature/opendataloader_output/具有二自由度铰接式车体的轮式机器人稳定性研究_李阳.md`
  - `docs/literature/opendataloader_output/具有二自由度铰接车体轮式机器人牵引力对稳定性的影响研究_马玉玺.md`
- 已根据这 `3` 篇文献的参考文献，整理出“铰接式车辆相关文献名称”清单，并按“国内 / 国外 + 年份升序”排序：
  - `docs/literature/三篇文献参考文献中的铰接式车辆相关文献整理.md`
- 已重新生成 `docs/literature/catalog.md`，使新生成的 Markdown 能在目录中被索引到。
- 对 `马玉玺` 一文的参考文献区做了额外校核：
  - 由于文本层存在编码污染，使用原 PDF 参考文献页图进行人工复核，再与 `宁悦 / 李阳` 两篇交叉去重。

修改文件：
- `docs/literature/opendataloader_output/双铰接轮式越野工程车辆机液复合驱动系统研究_宁悦.md`
- `docs/literature/opendataloader_output/具有二自由度铰接式车体的轮式机器人稳定性研究_李阳.md`
- `docs/literature/opendataloader_output/具有二自由度铰接车体轮式机器人牵引力对稳定性的影响研究_马玉玺.md`
- `docs/literature/三篇文献参考文献中的铰接式车辆相关文献整理.md`
- `docs/literature/catalog.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 本轮共整理出：
  - 国内相关条目 `21` 条
  - 国外相关条目 `15` 条
- 当前最适合继续扩展的两条引用链为：
  - 国内：`铰接式装载机 / 铰接式车辆稳定性 / 铰接式拖拉机`
  - 国外：`articulated frame steer vehicle / articulated mobile robot / articulated rover`

## 2026-04-23

已完成：
- 按用户要求，未在本地文献库或 CNKI 中继续补搜，而是直接在谷歌浏览器中使用 `Google Scholar` 对 `2014` 年及之后的铰接式车辆相关文献做了补充检索。
- 本轮补检关键词覆盖：
  - `双铰接车辆`
  - `双轴铰接式车辆`
  - `二自由度铰接车体`
  - `三自由度铰接车体`
  - `articulated frame steer vehicle`
  - `double articulated vehicle`
  - `center-articulated vehicle`
  - `articulated mobile robot`
  - `articulated rover`
- 已将补检结果按“国内 / 国外 + 年份升序”补写到：
  - `docs/literature/三篇文献参考文献中的铰接式车辆相关文献整理.md`
- 已同时把原表的最后一列从只适用于三篇源文献的 `被引用于` 扩成了通用的 `条目归属`：
  - `宁 / 李 / 马` 表示源文献参考文献条目
  - `GS 后补` 表示本轮 Google Scholar 新增条目
- 已在同一文档中补写 `2014` 年后的发展趋势总结。

修改文件：
- `docs/literature/三篇文献参考文献中的铰接式车辆相关文献整理.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前该整理文件已不再只覆盖 `2013` 年前老文献，而是补齐了 `2014` 年后国内外铰接式车辆、铰接式移动机器人、center-articulated rover/vehicle 的代表性发展条目。
- 这轮 Google Scholar 补检后，能够看出的主线是：
  - 国内：
    - `折腰液压转向`
    - `路径跟踪与 MPC`
    - `分布式驱动协同控制`
    - `矿山重载铰接车辆`
    - `多级铰接移动机器人`
  - 国外：
    - `active stability`
    - `path-following / MPC / trajectory planning`
    - `center-articulated rover`
    - `articulated mobile robot`
- `双铰接 / 三自由度铰接车体` 这类显式命名论文在 `2014` 年后数量仍不算多；后续若继续扩展，更适合沿 `控制 / 规划 / 稳定性 / 场景应用` 向下追文献，而不是只按结构命名检索。

## 2026-04-23

已完成：
- 按用户要求，将：
  - `docs/literature/三篇文献参考文献中的铰接式车辆相关文献整理.md`
  中整理出的全部文献导入 Zotero 集合：
  - `铰接车辆发展历程`
- 本轮为此新增本地导入脚本：
  - `scripts/literature/import_markdown_refs_to_zotero_collection.py`
- 脚本工作流为：
  - 解析 Markdown 表格
  - 读取 `zotero.sqlite`
  - 复用库内已有同题名条目
  - 为缺失条目创建标准 Zotero 条目并归入指定 collection
- 实际导入前后共生成两份数据库备份：
  - `/home/lbz/Zotero/zotero.sqlite.backup_2026-04-23_21-59-07`
  - `/home/lbz/Zotero/zotero.sqlite.backup_2026-04-23_22-02-13_before_attachment`
- 导入完成后，又对该集合执行了一轮本地 PDF 自动回填：
  - 使用：
    - `scripts/literature/attach_local_pdfs_to_zotero_collection.py`
  - 从 `docs/literature/` 自动补挂成功 `1` 个 PDF：
    - `分布式驱动—转向多级铰接移动机器人构形设计及控制方法_胡喆熙.pdf`
  - 新增附件 parent key：
    - `U6BT9Y4Z`
  - 新增附件 key：
    - `IZ9LFFPG`

修改文件：
- `scripts/literature/import_markdown_refs_to_zotero_collection.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `铰接车辆发展历程` 集合当前共 `82` 条文献：
  - 复用已有条目 `6` 条
  - 新建条目 `76` 条
- 当前该集合 PDF 覆盖情况为：
  - 已带 PDF 条目 `7` 条
  - 暂无 PDF 条目 `75` 条
- 本地目录自动匹配目前基本已跑尽；后续若继续补 PDF，更适合对剩余无 PDF 条目做单篇下载与定向补挂，而不是重复跑本地目录扫描。

已完成：
- 按用户要求，将 `chapter03.tex` 从上一轮“运动学参考层 + 动力学响应层”版本恢复为原来的“运动学模型 + 轮速分配”版本。
- 已恢复以下原有章节主线：
  - `球铰姿态规划器`
  - `名义轮速解析分配`
  - `六轮轮速分配矩阵`
  - `面向低滑移的接触感知轮级牵引分配`
  - `代入具体结构参数向量后的最终解析结果`
- 已恢复原有关键符号与接口：
  - `\mathbf q`
  - `\mathbf q^{d}`
  - `\mathbf q^{cmd}`
  - `\dot{\mathbf q}^{cmd}`
  - `\boldsymbol\Omega^{d}`
  - `\boldsymbol\Omega_{\mathrm{ref}}`
  - `\boldsymbol\tau^{cmd}`
- 已执行：
  - `latexmk -xelatex -interaction=nonstopmode main.tex`
- 已确认 `main.pdf` 可正常生成。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `chapter03` 的默认口径已重新回到“原运动学模型 + 轮速分配”，不再沿用上一轮纯动力学替换版。
- 若后续继续修改第 3 章，下一步应在当前已恢复的运动学章节之后追加动力学模型，而不是再次覆盖现有正文。

已完成：
- 按用户要求重写毕业论文 `chapter03.tex`，将原“球铰姿态规划器 + 轮速解析分配”主线改写为“运动学参考层 + 动力学响应层”主线。
- 已删除旧版章节中的：
  - `球铰姿态规划器`
  - `\mathbf q^{cmd}`
  - `\dot{\mathbf q}^{cmd}`
- 已统一球铰状态符号为：
  - `\mathbf q_a=[\phi_1,\theta_1,\psi_1,\phi_2,\theta_2,\psi_2]^T`
- 已在 `chapter03.tex` 中写入以下动力学内容：
  - 建模目标与基本假设
  - 坐标系、轮索引与状态/输入定义
  - 几何接口与运动学层输出
  - 车轮转动动力学
  - 轮胎与地面接触模型
  - 整车平面动力学
  - 球铰执行动力学
  - 总体状态空间表达
  - 与现有控制链路的对应关系
  - 参数辨识与实现建议
- 已执行：
  - `latexmk -xelatex -interaction=nonstopmode main.tex`
- 已确认 `main.pdf` 可正常生成。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `chapter03` 的 canonical 接口已改为：
  - 运动学层输出 `(\boldsymbol\omega^{\mathrm{ref}}, \mathbf q_a^{\mathrm{ref}})`
  - 动力学层显式描述 `车轮转动 + 轮胎/接触 + 平面动力学 + 球铰执行`
- 后续论文写作默认不应再回到 `q^{cmd}` / `\dot q^{cmd}` 的旧链路。
- 当前章节已能作为后续轮端力矩分配、防滑控制与横摆稳定补偿的统一模型基础。

下一步：
- 若继续论文正文，优先检查 `chapter03` 与 `chapter04` 的术语、符号和控制链路衔接是否一致。

## 2026-04-24

已完成：
- 按用户给定的建模目标与方程结构，重写 `chapter03.tex` 中 `整车动力学模型` 一节。
- 保留前文原有运动学主线不动，仅替换动力学部分正文，使其改为：
  - `中车质心平面运动 + 六轮转动 + 两处球铰执行动态`
- 已将动力学层外部输入统一为：
  - `(\boldsymbol\omega^{\mathrm{ref}}, \mathbf q_a^{\mathrm{ref}})`
- 已在正文中显式补入球铰状态与前文运动学变量的对应关系：
  - `\phi_1=\phi_f, \theta_1=\theta_f, \psi_1=\psi_f`
  - `\phi_2=\phi_r, \theta_2=\theta_r, \psi_2=\psi_r`
- 已按用户要求写入并统一以下动力学子模块：
  - 几何接口 `x_i(\mathbf q_a), y_i(\mathbf q_a), \chi_i(\mathbf q_a)`
  - 轮速跟踪生成轮端力矩
  - 线性刚度 + 摩擦圆饱和轮胎模型
  - `u,v,r` 三自由度平面动力学
  - `PD` 球铰执行动力学
  - 总体状态空间表达与控制链路
- 已执行：
  - `latexmk -xelatex -interaction=nonstopmode main.tex`
- 已确认：
  - `main.pdf` 可正常生成

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `chapter03` 已不再是单纯的“恢复旧运动学版本”状态，而是：
  - 前半段保留原运动学推导
  - 后半段动力学部分采用新控制导向写法
- 当前动力学部分的 canonical 接口为：
  - `(\boldsymbol\omega^{\mathrm{ref}}, \mathbf q_a^{\mathrm{ref}}) -> 动力学响应`
- 当前球铰对平面动力学的影响默认通过：
  - `x_i(\mathbf q_a), y_i(\mathbf q_a), \chi_i(\mathbf q_a), F_{z,i}`
  进入模型，不再额外手工添加独立的“球铰横摆力矩输入项”。
- 当前章节内部仍保留 `\boldsymbol\Omega^{d}` / `\boldsymbol\Omega_{\mathrm{ref}}` 与 `\boldsymbol\omega^{\mathrm{ref}}` 的桥接表述；若后续继续润色，应把这一映射关系再写得更直接。

下一步：
- 若继续论文主线，优先统一 `chapter03` 与 `chapter04` 对动力学输入接口、轮速参考符号和球铰状态符号的写法。

已完成：
- 在用户明确确认后，继续收敛 `chapter03.tex` 的章节结构，删除运动学部分中已不再适合保留的两块内容：
  - `球铰规划器`
  - `面向低滑移的接触感知轮级牵引分配`
- 已将第 3 章结构统一为：
  - 运动学解析分配
  - 动力学响应模型
- 已将运动学层接口明确为：
  - `(\boldsymbol\Omega^{d}, \mathbf q_a^{\mathrm{ref}})`
- 已将动力学层接口明确为：
  - `(\boldsymbol\omega^{\mathrm{ref}}, \mathbf q_a^{\mathrm{ref}})`
  - 且 `\boldsymbol\omega^{\mathrm{ref}}=\boldsymbol\Omega^{d}`
- 已同步修改并清理 `chapter03.tex` 中与旧链路相关的表述，使其不再保留：
  - `q^{cmd}`
  - `\dot q^{cmd}`
  - `\boldsymbol\Omega_{\mathrm{ref}}`
  - `\boldsymbol\tau^{cmd}`
  作为第 3 章当前主线接口
- 已同步更新项目记忆文件，使当前仓库默认状态不再沿用“保留旧运动学主线的混合版”描述：
  - `docs/current_status.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 本轮未新增代码或仿真运行；论文主文档编译状态继续沿用上一轮确认结果：
  - `latexmk -xelatex -interaction=nonstopmode main.tex`
  - `main.pdf` 可正常生成

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `chapter03` 的 canonical 结构已不再是“旧运动学 + 新动力学”的混合版，而是“运动学解析分配 + 动力学响应模型”的纯模型版。
- 后续若继续撰写 `chapter04`、控制链说明或答辩材料，应直接沿用：
  - `高层命令 -> (\boldsymbol\Omega^{d}, \mathbf q_a^{\mathrm{ref}}) -> (\boldsymbol\omega^{\mathrm{ref}}, \mathbf q_a^{\mathrm{ref}}) -> 动力学响应`
  的链路说明。

下一步：
- 若继续论文主线，优先检查 `chapter04`、控制框图和实验描述中是否仍残留旧符号与旧接口表述。

已完成：
- 按用户逐条给出的符号统一要求，继续修改 `chapter03.tex` 中动力学推导部分，使其与前文运动学模型的符号体系保持一致。
- 已将动力学部分的主坐标系从独立的 `\{B\}` 统一回前文的 `\{B_2\}`。
- 已将动力学部分的车轮编号从：
  - `\mathrm{fL},\mathrm{fR},\mathrm{mL},\mathrm{mR},\mathrm{rL},\mathrm{rR}`
  统一改为：
  - `1L,1R,2L,2R,3L,3R`
- 已将动力学部分的平面状态从：
  - `u,v,r`
  统一改为：
  - `V_x,V_y,\Omega_z`
- 已将动力学部分的车轮半径从：
  - `R_w`
  统一改为：
  - `\rho_w`
- 已将动力学输入记号从：
  - `\mathbf u_c`
  统一改为：
  - `\mathbf u_{\mathrm{dyn}}`
- 已将整车质量与附加阻尼记号从：
  - `M,c_u,c_v,c_r`
  统一改为：
  - `m,c_x,c_y,c_{\Omega}`
- 已取消动力学部分中新引入的球铰角重排记号：
  - `\mathbf q_a`
  - `\psi_1,\theta_1,\phi_1,\psi_2,\theta_2,\phi_2`
- 已改为直接沿用前文构型向量：
  - `\mathbf q=[\psi_f,\theta_f,\phi_f,\psi_r,\theta_r,\phi_r]^T`
  - `\mathbf q^{\mathrm{ref}}=\mathbf q^{d}`
- 已将动力学中的轮心平面位置与滚动方向改为直接复用前文运动学结果：
  - `${}^{2}\mathbf p_w`
  - `${}^{2}\mathbf p_{w,xy}`
  - `${}^{2}\mathbf t_w`
  - `\chi_w=\operatorname{atan2}({}^{2}t_{y,w},{}^{2}t_{x,w})`
- 已同步修改运动学部分的接口表述，使其不再输出重排后的 `q_a^{\mathrm{ref}}`，而是直接采用：
  - `(\boldsymbol\Omega^{d}, \mathbf q^{\mathrm{ref}})`
- 已同步修改动力学部分接口为：
  - `(\boldsymbol\omega^{\mathrm{ref}}, \mathbf q^{\mathrm{ref}})`
  - 且 `\boldsymbol\omega^{\mathrm{ref}}=\boldsymbol\Omega^{d}`
- 已重新执行：
  - `latexmk -xelatex -interaction=nonstopmode main.tex`
- 已确认：
  - `main.pdf` 可正常生成

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `chapter03` 的动力学推导已不再使用与前文运动学分离的一套独立符号，而是统一回整章单一符号体系。
- 当前第 3 章的 canonical 接口链已明确为：
  - `高层命令 -> (\boldsymbol\Omega^{d}, \mathbf q^{\mathrm{ref}}) -> (\boldsymbol\omega^{\mathrm{ref}}, \mathbf q^{\mathrm{ref}}) -> 动力学响应`

下一步：
- 若继续论文主线，优先检查 `chapter04`、控制框图与答辩材料是否仍残留 `\mathbf q_a`、`q_a^{\mathrm{ref}}`、`u,v,r` 等旧记号。

已完成：
- 按用户要求，重排 `docs/RL运动学，动力学参数符号定义.md` 中的整篇数学表达，使其符合仓库要求的 Obsidian 可编译格式。
- 已将文件中原有的伪公式块、断裂矩阵和非标准显示写法统一改写为：
  - 行内公式使用 `$...$`
  - 块级公式使用 `$$...$$`
- 已保留原文件的章节结构与符号内容主旨，仅重写公式与排版，不额外改变文档讨论主题。
- 已检查并确认该文件中不再残留：
  - `\(...\)`
  - `\[...\]`
  这类不符合仓库 Markdown 规则的数学写法。

修改文件：
- `docs/RL运动学，动力学参数符号定义.md`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- `docs/RL运动学，动力学参数符号定义.md` 当前已经可以直接在 Obsidian 中按标准数学语法渲染，不再是上一版那种混有伪公式标记的不可直接编译状态。

下一步：
- 若继续处理该文档，可进一步根据当前 `chapter03` 的最新符号体系，决定是否把文中 `v_x/v_y/\omega_z`、`R_k` 等记号再和论文正文逐项对齐。

已完成：
- 按用户要求删除 `chapter03.tex` 中整段动力学模型推导，并将第 3 章从“运动学 + 动力学”版本回切为旧的运动学/执行层主线。
- 已将第 3 章标题改回：
  - `整车底层运动学模型与轮速分配`
- 已恢复并重写以下章节主线：
  - `球铰姿态规划器`
  - `名义轮速解析分配`
  - `面向低滑移的接触感知轮级牵引分配`
- 已恢复 canonical 符号链：
  - `\mathbf q`
  - `\mathbf q^{d}`
  - `\mathbf q^{cmd}`
  - `\dot{\mathbf q}^{cmd}`
  - `\boldsymbol\Omega^{d}`
  - `\boldsymbol\Omega_{\mathrm{ref}}`
  - `\boldsymbol\tau^{cmd}`
- 已按当前 `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py` 的逻辑写回 low-slip 执行层，包括：
  - 接触权重 `\gamma_w`
  - 侧向速度仿射项 `\mathbf a_w,b_w`
  - 平面命令整形 `\mathbf u_v^{\ast}`
  - 轮速参考 `\boldsymbol\Omega_{\mathrm{ref}}`
  - 纵滑抑制轮端力矩 `\boldsymbol\tau^{cmd}`
- 已重新执行：
  - `latexmk -xelatex -interaction=nonstopmode main.tex`
- 已确认：
  - `main.pdf` 可正常生成

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `chapter03` 已不再保留动力学段，默认应按“球铰姿态规划器 + 名义轮速解析分配 + 低滑移执行层”理解。
- 当前第 3 章默认接口已恢复为：
  - `(\mathbf u,\mathbf q,\mathcal P) \mapsto (\boldsymbol\Omega^{d}, \mathbf q^{cmd})`
  - `(\mathbf u_v^{d}, \mathbf q, \dot{\mathbf q}^{cmd}, \mathbf F_n, \boldsymbol\Omega, \mathbf v_{\parallel}^{\mathrm{act}}) \mapsto (\mathbf u_v^{\ast}, \boldsymbol\Omega_{\mathrm{ref}}, \boldsymbol\tau^{cmd}, \mathbf q^{cmd})`

下一步：
- 若继续论文主线，优先检查 `chapter04`、控制框图和答辩材料中是否仍残留 `\mathbf q^{\mathrm{ref}}`、`\boldsymbol\omega^{\mathrm{ref}}`、`\mathbf u_{\mathrm{dyn}}` 等上一版动力学口径。

已完成：
- 按用户要求，用当前已知最佳真实 run 的环境配置覆写现有 Stage0 环境主线：
  - 目标 run：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-21_21-51-09_stage0_waypoint_quality_goal10_v1_150iter`
- 已将 Stage0 环境回退到与该 run 对应的实际口径：
  - 观测从 `55 / 55` 回退为 `54 / 54`
  - 删除 `next_turn_delta`
  - 删除 `differential_turn_cost`
  - 恢复 `far_from_target` 为 reward 项
  - 取消 `min_segment_turn_deg = 20.0°`
  - 取消按 turn-demand 缩放的 `turn_speed_penalty / slip_penalty`
- 已核对并恢复该 run 的关键参数：
  - `base_allow_reverse = True`
  - `distance_to_target_weight = 6.0`
  - `progress_to_target_weight = 8.0`
  - `progress_to_target_relax_radius_m = 4.0`
  - `reached_target_weight = 6.0`
  - `far_from_target_weight = -2.0`
  - `angle_diff_weight = 6.0`
  - `turn_speed_penalty_weight = -2.0`
  - `slip_penalty_weight = -2.0`
- 已同步更新：
  - `complete_car_cfg.py`
  - `complete_car_stage0_cfg.py`
  - `observations.py`
  - `rewards.py`
  - `env.py`
  - `io_descriptors.py`
  - `math_utils.py`
  - `logger.py`
  - `docs/current_status.md`
  - `docs/RL阶段训练参数一览表.md`
  - `docs/conversation_history.md`
  - `logs/daily_work_log.md`
- 已完成静态检查：
  - `python3 -m py_compile ...` 通过

产出/结论：
- 当前 Stage0 active baseline 已重新固定为最佳 run 对应的 `54 / 54` 双 waypoint 环境。
- 后续若继续推进 `next_turn preview / differential_turn_cost`，应明确视为新分支，而不是当前默认环境。

下一步：
- 先恢复 Isaac Lab 运行环境，再用这条已回退 baseline 补跑 smoke 和真实训练复现。

已完成：
- 回答并核对当前 Stage0 active baseline 的奖励函数。
- 以当前源码为准，将 `docs/RL阶段训练参数一览表.md` 更新为详细版本，补充：
  - Stage0 总览
  - waypoint 与相对命令含义
  - 动作空间与低层执行链
  - `54 / 54` 观测项明细
  - `7` 项 reward 的公式、权重、工程含义和终止关系
  - PPO 参数与 TensorBoard 重点观测量
  - 当前配置的使用边界
- 已特别澄清：
  - 当前 `angle_diff` 使用的是当前目标点在车体系下的视线方向误差，不是额外的终点航向误差。

修改文件：
- `docs/RL阶段训练参数一览表.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 奖励函数已在参数表中固化为源码级详细说明。
- 当前 reward 仍为 `distance_to_target / progress_to_target / reached_target / far_from_target / angle_diff / turn_speed_penalty / slip_penalty` 七项，不包含 `next_turn_delta` 与 `differential_turn_cost`。

下一步：
- 若继续 RL 主线，先恢复 Isaac Lab 运行环境并补跑当前 `54 / 54` baseline 的 smoke run。

已完成：
- 按用户要求，对 `chapter03` 进行一轮毕业论文风格语言润色。
- 润色重点：
  - 将引言从“控制模块流程说明”改为“建模对象、建模目的与模型层次”说明。
  - 强化坐标系、构型变量、轮心位置、轮心速度、无滑移约束和六轮轮速分配之间的承接关系。
  - 将低滑移执行层改写为“名义运动学之后为什么还需要执行整形”的叙述。
  - 减少术语堆叠，保留公式、符号、接口和技术口径不变。
- 已重新执行：
  - `latexmk -xelatex -interaction=nonstopmode main.tex`
- 编译结果：
  - `main.pdf` 正常生成。
- 已核对当前 `RL_Training/` 源码状态：
  - 当前 action space 为 `1 + 6 = 7`。
  - `map_base_actions_to_planar_command()` 将 policy 的单个纵向速度动作补为 `[vx_cmd, 0]`。
  - 已对相关 Python 文件执行 `py_compile` 静态检查，语法检查通过。
  - 仍存在模板既有字体与 overfull 警告，但无本次润色导致的 LaTeX 错误。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `chapter03` 当前技术结构仍保持为“球铰姿态规划器 + 名义轮速解析分配 + 低滑移执行层”。
- 本轮只调整写作风格和段落组织，不改变模型公式、接口和符号体系。

下一步：
- 若继续论文侧工作，优先检查 `chapter04` 与第 3 章当前模型接口、符号和写作风格是否一致。

已完成：
- 对当前 Stage0 reward 进行作用边界分析。
- 明确当前 reward 主导学习的是：
  - 向当前 active waypoint 推进
  - 命中 waypoint
  - 不远离目标
- 明确当前 reward 不能直接证明：
  - 低侧滑已经实现
  - 低纵滑已经实现
  - 球铰协同转向已经学成
  - 前中后车体形成类似“贪吃蛇”的连续跟随运动
- 已同步更新当前状态和跨会话结论。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 可以作为平地双 waypoint baseline，但不能作为低滑移蛇形协同转向的最终证据。
- 后续若要支撑该类论文结论，需要新增明确的行为质量指标和对应训练验证。

下一步：
- 先复现当前 baseline，再讨论是否引入下一段转向预告、低滑移成功判据或球铰协同转向评价指标。

已完成：
- 按用户要求，对 `chapter03` 进行一轮符号一致性修订。
- 主要修订内容：
  - 重新写明 `d / cmd / ref / act` 的含义，避免把所有带 `d` 的量都说成“高层策略直接给出”。
  - 中模块偏航角速度由 `\Omega_z` 改为 `\omega_z`，车轮角速度继续使用 `\Omega`。
  - 低滑移整形中的优化变量由无上标 `\mathbf u_v` 改为 `\tilde{\mathbf u}_v`。
  - 低滑移侧向速度仿射系数由 `\mathbf a_w,b_w` 改为 `\boldsymbol\alpha_w,\beta_w`。
  - 删除第二次对 `\boldsymbol\Omega^{d}` 的重复堆叠定义，改为引用前文排列顺序。
  - 补充 `${}^{2}\mathbf v_w^{\mathrm{act}}` 的来源说明。
  - 将低滑移牵引分配层接口输出改为 `(\mathbf u_v^{\ast},\boldsymbol\Omega_{\mathrm{ref}},\boldsymbol\tau^{cmd})`，不再把 `\mathbf q^{cmd}` 写成低滑移层自身输出。
  - 论文中纵向滑移 `\kappa_w` 按“车轮圆周速度大于实际纵向滚动速度时为正滑转”的口径定义。
- 已重新执行：
  - `latexmk -xelatex -interaction=nonstopmode main.tex`
- 编译结果：
  - `main.pdf` 正常生成。
  - 仍存在模板既有字体、overfull 和 BibTeX 字段警告，但无本次符号修订导致的 LaTeX 错误。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 第 3 章后续默认采用本轮修订后的符号口径。
- 若后续要求源码注释或实现公式与论文完全同符号，需要单独核对 `wheel_speed_allocator.py` 中纵向滑移符号方向。

下一步：
- 检查 `chapter04`、控制框图和答辩材料是否仍使用旧符号 `\Omega_z`、`\mathbf a_w,b_w` 或把 `\mathbf q^{cmd}` 写成低滑移层输出。

已完成：
- 按用户要求，将 `chapter03` 中的高层动作口径改为“不输出 `yaw_rate_cmd`”。
- 已重新推导并修改第 3 章运动学模型：
  - 高层动作由原来的平面命令口径改为 `V_x^d + q^d` 的 `7` 维动作。
  - 名义轮心速度改为由中模块纵向平动和球铰构型速度项组成，不再包含独立中模块偏航角速度项。
  - 六轮名义轮速分配改为 `Omega^d = J_w(q) V_x^d + J_q(q) qdot_cmd`，其中 `J_w(q)` 为 `6 x 1`。
  - 低滑移执行层由二维平面速度整形改为标量纵向速度整形，输出 `V_x^*`、`Omega_ref` 和 `tau_cmd`。
- 已重新执行：
  - `latexmk -xelatex -interaction=nonstopmode main.tex`
- 编译结果：
  - `main.pdf` 正常生成。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 论文第 3 章当前默认采用“不含 `yaw_rate_cmd`”的运动学模型。
- 当前仓库中的 `RL_Training/` active baseline 已是 `7` 维动作口径：policy 输出 `vx_cmd + q^d`，环境内部将底盘命令补成 `[vx_cmd, 0]` 后交给 allocator；该源码口径尚未完成 Isaac Lab smoke 或真实训练复现。

下一步：
- 检查 `chapter04`、控制框图和答辩材料是否仍按旧的 `yaw_rate_cmd` 或二维平面命令口径描述第 3 章模型。

已完成：
- 按用户要求修改 `RL_Training/` Stage0 动作空间，去掉 policy 输出的 `yaw_rate_cmd`。
- 已将动作维度从 `8` 改为 `7`：
  - 第 `1` 维为底盘纵向速度命令 `vx_cmd`
  - 后 `6` 维为球铰期望姿态 `q^d`
- 已同步环境动作切片：
  - `planar_actions = actions[:, :1]`
  - `ball_joint_actions = actions[:, 1:]`
- 已将动作映射改为只读取 `vx_cmd`，并在环境内部补成 `[vx_cmd, 0]` 传给低层 allocator。
- 因 `last_action` 随动作维度变化，当前 actor / critic 观测维度从 `54 / 54` 改为 `53 / 53`。
- 已同步更新当前状态、跨会话结论和 RL 阶段训练参数表。
- 已执行：
  - `python3 -m py_compile ...`
- 静态检查结果：
  - 相关环境文件语法通过。
- 当前终端环境缺少 `torch` 和 `isaaclab`，因此未完成张量级动作映射测试或 Isaac Lab smoke。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `docs/current_status.md`
- `docs/RL阶段训练参数一览表.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 源码和参数文档已经与“不含 policy `yaw_rate_cmd`”的 `7` 维动作口径一致。
- 低层 allocator 接口暂时保持二维平面命令输入，第二维固定为 `0`，不是 policy 动作。

下一步：
- 恢复 Isaac Lab / torch 运行环境后，优先补跑当前 `53 / 53`、`7` 维动作 Stage0 smoke。

## 2026-04-25

已完成：
- 按用户最新要求，将 `yaw_rate_cmd` 加回 `RL_Training/` Stage0 policy 动作空间。
- 已将动作维度从 `7` 恢复为 `8`：
  - 前 `2` 维为底盘平面命令 `[vx_cmd, yaw_rate_cmd]`
  - 后 `6` 维为球铰期望姿态 `q^d`
- 已同步环境动作切片：
  - `planar_actions = actions[:, :2]`
  - `ball_joint_actions = actions[:, 2:]`
- 已将动作映射恢复为同时读取 `vx_cmd` 与 `yaw_rate_cmd`，并使用 `base_forward_velocity_max` 与 `base_yaw_rate_max` 映射物理命令。
- 因 `last_action` 随动作维度变化，当前 actor / critic 观测维度从 `53 / 53` 恢复为 `54 / 54`。
- 已同步更新当前状态、跨会话结论和 RL 阶段训练参数表。
- 已执行：
  - `python3 -m py_compile ...`
- 静态检查结果：
  - 相关环境文件语法通过。
- 当前终端环境缺少 `torch` 和 `isaaclab`，因此未完成张量级动作映射测试或 Isaac Lab smoke。

修改文件：
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py`
- `docs/current_status.md`
- `docs/RL阶段训练参数一览表.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 Stage0 源码和参数文档已恢复到包含 policy `yaw_rate_cmd` 的 `8` 维动作口径。
- 当前 actor / critic 观测维度为 `54 / 54`。

下一步：
- 恢复 Isaac Lab / torch 运行环境后，优先补跑当前 `54 / 54`、`8` 维动作 Stage0 smoke。

已完成：
- 按用户要求，将当前仓库中的已跟踪文件改动同步到 GitHub。
- 同步范围限定为 tracked files：
  - 使用 `git add -u` 暂存已跟踪文件的新增修改和删除。
  - 未跟踪文件、PDF/DOC、`results/` 下载产物和未跟踪脚本未纳入提交。

修改文件：
- 本次提交包含当前已跟踪文件中的 RL 代码、项目状态文档、训练参数表、README、日志和相关文献脚本改动。

产出/结论：
- 当前同步操作不会把工作区中未跟踪的大文件和临时下载结果推送到 GitHub。
