# 论文装配 SOP（E-M7 · 07 论文装配流程）

> **用途 / Purpose**：把求解产物装配成一篇可提交论文的标准流程——节次清单、模板使用（美赛模板随包；国赛模板需自备）、编译自检、Claim-Evidence 步骤、引用格式、预检脚本衔接，按顺序执行。
> **对应工作流 / Workflow**：`workflows/07-论文撰写.md`（正本）；模板 `paper-templates/`（美赛-MCM-ICM 随包；国赛-CUMCM 不随包、留 README 指引 + `编译自检.bat`）；方法层 `references/获奖级方法论/{abstract-writing,self-review-framework,de-ai-writing}.md`
> **门禁指针 / Gates**：`Euler-ENGINE.md` §1 **E-M7**（论文装配线）——摘要五要素；四轮自审 + CE 映射；引用一一对应；编译 exit 0；去 AI 味清单；§3「论文」行
> **降级 / Fallback**：纯文本装配 + 清单（LaTeX 不可用时用 Word 手工排版 + 逐页人检，标 `[降级]`；本包不随附 Word 模板）

---

## 1 · 节次清单（标准结构）

（正本：`workflows/07` §论文结构）

```text
摘要（Summary Sheet / 摘要页）
一、问题重述
二、问题分析
三、模型假设
四、符号说明
五、模型建立与求解（核心，按子问题分节）
六、模型检验与敏感性分析
七、模型评价（优缺点 + 改进）
八、参考文献
附录（代码）
AI 使用声明（位置以官方规定为准 → 见 workflows/10）
```

**两种组织方式，选一种贯穿全文（不得混用）**：

| 方式 | 结构 | 适用 |
|---|---|---|
| A. 按问题 | 每个问题一节，节内含「分析 → 假设（增量）→ 模型 → 求解 → 检验」 | 子问题界限清晰、各问差异大 |
| B. 按阶段 | 建模 → 求解 → 检验，每阶段内部按问题展开 | 模型高度复用、方法主线强 |

**问题间衔接**（问题 2/3/4 沿用前问时必须写）：沿用 / 修正 / 拓展——三选一，措辞对号入座（`workflows/07` §问题间衔接）；每个问题的节首一句衔接说明。

## 2 · 各节素材来源（谁产出什么）

| 节 | 素材来源 | 关键要求 |
|---|---|---|
| 摘要 | 全文 + 求解结果 | **先写摘要再写正文**；五要素；每问带具体数字 |
| 一、问题重述 | `templates/拆题卡.md` §1/§2 | 用自己的一句话重述，不抄题 |
| 二、问题分析 | `templates/拆题卡.md` §4 数据流图 + 模型卡 §1 映射 | 含整体建模框架图；难点识别；模型选择理由（含替代方案） |
| 三、模型假设 | `templates/假设表.md` | 三段式；文内编号 A1… 与表一致 |
| 四、符号说明 | `templates/符号表.tex` | `\input` 进论文；符号 ↔ 代码 ↔ 论文三处一致 |
| 五、建立与求解 | `templates/模型卡.md` + `templates/复现卡.md` + 产物 | 每节「本节要解决什么」；每个图表后有讨论 |
| 六、检验与敏感性 | `templates/敏感性报告卡.md` | 判定标准先于扫描；扫了几个呈现几个；优缺点各 ≥3 条 |
| 七、模型评价 | 模型卡 §7 + 复现卡 §8 | 缺点针对本模型具体选择；每条缺点对应改进方向 |
| 八、参考文献 | 引用登记 | 与正文一一对应；非学术来源禁入 |
| 附录 | 复现卡产物列汇总 | 核心代码摘录 + 一行注释；禁整屏截图 |
| AI 使用声明 | `templates/AI记录模板.md` | 模板 A/B；位置按官方最新规定 |

## 3 · 双模板使用（国赛模板需自备，见 §2 对照表）

| 项 | 国赛 CUMCM（`paper-templates/国赛-CUMCM/`，**模板需自备**） | 美赛 MCM-ICM（`paper-templates/美赛-MCM-ICM/`） |
|---|---|---|
| 主文件 | `<论文主文件>.tex`（`cumcmthesis.cls` + `cumcm2026.sty`，模板需自备） | `mcmthesis-template.tex`（`mcmthesis.cls` v6.3.3） |
| 编译引擎 | **必须 XeLaTeX**（pdfLaTeX 报错） | pdfLaTeX 或 XeLaTeX 均可 |
| 实测页数（基线） | 12 页 | 11 页 |
| 开赛前必改 | 队号/学校/日期等封面字段；电子版提交去掉封面编号页（`withoutpreface` 选项）；按规则注释/删除 `\tableofcontents` | `\mcmsetup{...}` 三处：`tcn=0000` → 控制号、`problem=A` → 题号、`\title{...}` → 标题 |
| 摘要位置 | `\begin{abstract} … \end{abstract}`（含 `\keywords{}`） | `\begin{abstract}` 内（自动生成 Summary Sheet 页） |
| 图片 / 代码 | 图片放 `figures/` | 图片放 `figures/`（已在 `\graphicspath`）；代码清单用 `code/` + `\lstinputlisting` |
| 语言 | 全中文，规范书面语 | 全英文，术语准确，避免中式英语 |
| 特别提醒 | 国赛官方以 Word 提交为主流 → 导出 PDF 前核对当年提交系统是否接受 PDF；AI 声明位置见 `workflows/10` | 摘要含 Hook 句 → 见 `abstract-writing.md` §美赛 Summary Sheet 模板 |

- **图片与表格**：论文图统一由 `templates-library/utils/plot_style.py` 输出 PDF（LaTeX 插入）；表格用 `utils/latex_table.py` 生成三线表后粘贴。
- 符号表按 `templates/符号表.tex` 的用法块 `\input`（包依赖 longtable/booktabs；随包的美赛 cls 已载，国赛 cls 需自备）。

## 4 · 编译自检（`编译自检.bat`）流程

| 步 | 动作 | 说明 |
|---|---|---|
| 1 | 双击 `paper-templates/编译自检.bat`（或 cmd 里运行） | 脚本自动选引擎：TeX Live 优先，缺则回落 MiKTeX |
| 2 | 脚本对**两个模板**各编译两遍 | 国赛 `xelatex`（2 pass）；美赛 `pdflatex`（2 pass） |
| 3 | 断言：PDF 生成 + 日志含 `Output written on` + 无 `Fatal error` | 三项全过 → `[PASS]` |
| 4 | 看退出码 | **exit 0 = 可用模板全 PASS（缺件分支打印 SKIP，不算失败）**；exit 1 = 有 FAIL；exit 2 = 未找到 TeX 引擎 |
| 5 | 记录留证 | 退出码 + 打印的引擎/路径/文件大小写入交接卡（`Euler-ENGINE.md` §7） |

**已知无害警告**（不用管，`LaTeX-环境使用说明.md`）：`Font shape 'TU/SimHei(0)/b/n' undefined`、`Label 'LastPage' multiply defined`、`float specifier changed to ht`——只要 log 有 `Output written on *.pdf` 且无 `Fatal error` 即通过。

**论文本体编译**（自有文件，不是 example）：

```bash
# 国赛（2 遍，生成目录/交叉引用）
cd paper-templates/国赛-CUMCM && xelatex -interaction=nonstopmode <论文主文件>.tex   # 模板需自备（见该目录 README）
# 美赛
cd paper-templates/美赛-MCM-ICM && pdflatex -interaction=nonstopmode <论文主文件>.tex
```

- 赛前一周必跑一次 `编译自检.bat`（对冲环境失效）；赛中首日再跑一次确认。

## 5 · Claim-Evidence 步骤（四轮自审第一轮）

（正本：`self-review-framework.md` §第一轮；填表：`templates/Claim-Evidence映射表.md`）

| 步 | 动作 | 通过线 |
|---|---|---|
| 1 | 通读论文，提取所有带主张性质的句子（含摘要结果句），逐条登记 | 无漏项 |
| 2 | 每条给证据（图/表/artifact/文献）+ 强度 ✅/⚠️/❌ | 证据可点开 |
| 3 | 修所有 **❌**（补证据或删主张），再修 ⚠️（注明缺哪个维度并补齐） | **❌ = 0** |
| 4 | 核心结论过「反方测试」；对比类主张有同验证集同指标对照 | 能回答反面结论 |
| 5 | 通过后进入第二轮（章节结构）→ 第三轮（表述质量 + 去 AI 味）→ 第四轮（格式规范） | 每轮通过才前进 |

- 任何 ❌ → 回对应环节补证据，**不做表面润色**（`workflows/07` §交付前四轮自审）。
- 第三轮配 `de-ai-writing.md` 八类痕迹清单；第四轮用本 SOP §7 格式卡。

## 6 · 引用与格式卡

| 项 | 国赛 CUMCM | 美赛 MCM/ICM |
|---|---|---|
| 引用格式 | **GB/T 7714-2015**（顺序编码制；专著/期刊/学位论文/电子资源著录格式区分） | COMAP 不强制单一格式，但**全文一种风格**（数字制或 author-year） |
| 数据/软件 | 数据集、软件须注明来源与版本（版本可放附录） | 同 |
| 一一对应 | 引了没列、列了没引都不行 | 同 |
| 禁入来源 | CSDN、知乎、百度百科、博客园等非学术来源不进参考文献 | 同 |
| AI 工具 | 按 `workflows/10` 列入参考文献；**不替代真实文献** | 另附 Report on Use of AI（`workflows/10` §美赛） |

**格式细节卡**（`workflows/07` §格式细节 + `self-review-framework.md` §第四轮）：

- [ ] 页码连续、位置依模板；页眉依竞赛模板，不自行增删
- [ ] 行距、页边距依模板，不自行改动；纸型正确（国赛 A4 / 美赛 US Letter）
- [ ] 字体统一（国赛：宋体正文 + 黑体标题；美赛：Times New Roman）
- [ ] 公式编号右对齐、连续；正文引用为「式(N)」；符号与符号表一致
- [ ] 图「图 N」连续编号、**图题在图下方**；表「表 N」连续编号、**表题在表上方**、三线表
- [ ] 每个图表在正文被引用（无孤图孤表）；图片靠近首次引用处；图题不跨页截断
- [ ] 图表要素齐全（图例、坐标轴标签 + 单位、误差棒）；灰度打印可区分；≥300dpi 或矢量
- [ ] 图注语言：中文（国赛）/ 英文（美赛），措辞与符号表一致 → 见 `references/图注模板.md`
- [ ] 附录：核心代码摘录 + 一行注释，禁整屏截图堆砌
- [ ] 数值一致性：同一指标在摘要/正文/图表/支撑材料中一致，精度位数统一

## 7 · 预检脚本衔接（判分/自审前置）

```bash
# 我方材料（默认）：硬项 FAIL 会阻断（exit 1）
python scripts/precheck_paper.py <paper.txt|paper.docx> --profile our

# 锚样/参考材料：全部降级为 WARN 画像（exit 0）
python scripts/precheck_paper.py <paper.txt|paper.docx> --profile ref
# 加 --json 可取结构化输出
```

| 项 | 口径 |
|---|---|
| 退出码 | 0 = 无 FAIL；1 = 存在 FAIL；2 = 输入错误 |
| 判定对齐 | 与 `references/scoring-rubric.md` §2 结构帽 **C1–C4** 对齐 |
| 硬要求 | **C1 帽 / B1 项无 FAIL**（`workflows/07` checklist：摘要「可点名数字」硬自查） |
| 输出用途 | 预检输出必须**附入判分/自审会话的「预检裁决」小节**（逐项 OK/WARN/FAIL 与处理） |
| 摘要变体风险 | 变体标题（【摘要】/「摘 要：」/Abstract）可能漏检 → 人工核后按 07 摘要标准处理 |
| 参考文献判定 | 节标题 + ≥3 条目才算形成；仅字样命中视为未形成 |
| 与图注相关项 | 检出「图 N/表 N」题注行数量；加粗/行内题注（`**图 1**`、`图1：`）可能漏检 → 人工核 |

**装配顺序（推荐）**：图（三闸过）→ 表格生成 → 正文装配（含 `\input` 符号表）→ 摘要定稿 → 预检脚本 → 四轮自审（CE 映射先行）→ `编译自检.bat` / 本体编译 → 逐页人检 → `templates/提交包清单卡.md`。

## 8 · 自检

（`workflows/07` checklist 摘要）

- [ ] 摘要含五要素；结果句带具体数字（预检 C1 帽无 FAIL）
- [ ] 结构完整、逻辑链不断；不引用后文；术语一致（一个概念一个词）
- [ ] 问题间衔接写清（沿用/修正/拓展）
- [ ] 每个图表自解释 + 正文有引用 + 单位齐全
- [ ] 核心论述由队员完成；已过八类 AI 痕迹清单（中英分别自检）
- [ ] CE 映射表无 ❌ 主张
- [ ] 参考文献按赛事规则；与正文引用一一对应
- [ ] 敏感性、优缺点已入正文
- [ ] 格式细节已查（§6 卡）
- [ ] 缺陷谱系扫描完成（七族：摘要空洞/模型堆砌/改进通胀/敏感性缺失/图表缺陷/结果-代码脱钩/AI 声明漏填）
- [ ] 编译 exit 0（或 Word 导出逐页检查）；预检输出已附「预检裁决」
- [ ] 备赛期/复盘场：锚校准 + 台账回写已做（赛中跳过）
