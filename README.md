# Euler-Modelforge · 数学建模竞赛工作流（中文版）

> **英文版 / English version**：`README.en.md`（本文件为中文版正本，两份同构）

---

## 一句话定位

**Euler-Modelforge 是一套「手册 + 工具链」形态的数学建模竞赛工作流**：把「读题 → 假设 → 建模 → 求解 → 检验 → 图件 → 论文 → 提交」拆成 10 个带**门禁**与**降级**路径的模块，方法写在 `workflows/` 与 `references/`，自检交给 `tools/` 与 `templates-library/`——任何能读文件、能跑 Python 的人或 code agent 都能按三步装载直接开工。

## 目标用户

- 参加数学建模竞赛（美赛 MCM/ICM、国赛 CUMCM 及同类赛事）的队伍与指导教师；
- 想用一套可复现、带门禁的流程写建模论文的个人研究者；
- 把方法论交给 code agent 执行、需要明确装载协议与退出码约定的用户。

## 三步装载

| 步 | 读什么 | 拿到什么 |
|---|---|---|
| 1 | `BOOT.md` | 冷启动索引：身份一句话 · 铁律摘要 · 装载路径（≤2KB，先读这个） |
| 2 | `Euler-CORE.md` | 人格与铁律：三模式、9 条铁律、赛事口径、学术诚信红线 |
| 3 | `Euler-ENGINE.md` | 生成引擎：模块注册表（§1）、门禁矩阵（§3）、runbooks（§4）、交接卡（§7） |

之后按所选 runbook 的装载清单**按需加载** `workflows/` 与 `modules/`：细节正本在工作流，引擎只索引、不复制正文。

## 能力清单（10 模块 + 底座）

| 模块 | 一句话 |
|---|---|
| E-M1 读题定位器 | 题目 → 拆题卡 / 选题评估矩阵（子问题拆解、题型与模型族初判、数据可得性） |
| E-M2 假设与符号台 | 假设表 + 符号表：三段式假设，符号↔代码↔论文三处一致 |
| E-M3 建模选型器 | 问题 → 模型卡：模型族选择、模型名词清单穷尽、融合与混搭验证 |
| E-M4 求解工坊 | 模型 → 求解 + 复现：模板库直用、artifacts 落盘、复现卡齐 |
| E-M5 检验台 | 解 → 敏感性分析 + 互验：扫描报告、分级互验、量纲量级核对 |
| E-M6 图件车间 | 数据 → 出版级图：PNG / PDF / SVG 三格式 + 图注，黑白与色盲友好检查 |
| E-M7 论文装配线 | 求解 → 论文：LaTeX 双模板装配、四轮自审、Claim-Evidence 映射、编译自检 |
| E-M8 提交合规闸 | 论文 → 提交包：提交前机检、打包清单、AI 使用记录提醒 |
| E-M9 校准与锚（L2 挂接） | 只声明边界：私有校准数据与锚注册备赛期只读挂接，赛中禁跑 |
| E-M10 编排器 | runbook 选线（RB-E1–E5）+ 交接卡（输入 / 产物 / 门禁 / 降级 / 下一步） |
| E-R 底座 | 环境档位 / 全链冒烟 / 故障速查 / 路径与资产卡 |

## 目录结构

```text
Euler-Modelforge/
├── BOOT.md                    冷启动索引（任何 agent / 人的第一读）
├── README.md / README.en.md   中文 / 英文总入口
├── AGENTS.md                  任意 code agent 的装载协议、CLI 约定、门禁 exit code、降级约定
├── Euler-CORE.md              人格与铁律（三模式 / 9 条铁律 / 赛事口径）
├── Euler-ENGINE.md            模块注册 / 数据流 / 门禁矩阵 / runbooks / 资产清单
├── learnings.md               空白错题本模板 + 提炼机制
├── modules/                   11 个模块规格件（E-M1…E-M10 + E-R 底座）
├── workflows/                 工作流 00–10 + _SHARED.md + W-ABSORB.md
├── templates/                 交付卡模板（拆题卡 / 模型卡 / 复现卡 / CE 映射表 …）
├── references/                参考卡与协议 + 获奖级方法论/
├── tools/                     env_check.py · smoke_chain.py
├── scripts/                   precheck_paper.py
├── templates-library/         求解模板库 + utils/ + MODEL_GUIDE.md + smoke_all.py
├── paper-templates/           LaTeX 论文模板（国赛 / 美赛两套）+ 编译自检
├── kb/                        自建知识库（空目录 + 自建说明）
├── LICENSE / LICENSE-DOCS / THIRD-PARTY.md
└── QUICKSTART.md / CHANGELOG.md / CITATION.cff
```

## 运行前提

- **Python 3.11+**（模板库与工具的运行基线）。
- **依赖**：`templates-library/requirements.txt`（numpy / scipy / pandas / matplotlib / Pillow / statsmodels / scikit-learn / networkx / SALib / pulp）。
- 建议自建虚拟环境（如 `<venv>/`）并在其中安装依赖，避免污染系统解释器。
- **可选**：LaTeX（xelatex）用于论文编译、系统中文字体用于图件与编译。缺件不阻塞——模块表有「降级」列，缺件按降级路径执行并标 `[降级]`。

## 冒烟自检（跑通即装好）

```bash
python tools/env_check.py --selftest            # 环境档位自检
python tools/smoke_chain.py --selftest          # 全链冒烟
python templates-library/smoke_all.py --quick   # 模板库冒烟（每类首件）
```

约定：全 PASS / SKIP 即 rc=0；**SKIP 不算 FAIL**；WARN 需登记；FAIL 非零退出。退出码语义统一为 `0` 通过 · `1` 失败 · `2` 用法错误（含输入错误，**不抛栈**）。

## L2 自建（不随包分发）

| 自建项 | 作用 | 起步方式 |
|---|---|---|
| `kb/` | 你的知识库：模型方法、论文拆解、检索索引 | 按 `workflows/09-知识管理.md` 的 schema 起步 |
| `<共享层>/` | 可选的多 agent / 多人协作层（共享 SOP 与材料） | 单人使用可完全跳过 |
| `<校准台账>` | 私有校准数据（判档线 / 复盘记录 / 整改记录） | `templates/校准台账模板.md`（空白） |
| `<锚注册卡>/` | 私有锚注册（已知答案锚 / 已知档位锚样本） | `templates/锚注册卡模板.md`（空白）+ 填锚规程见 `references/scoring-rubric.md` |

> L2 是**可选增强**：只用 L0 也能跑完整条链；没有 L2 时相关模块走「降级」列。

## 学术诚信与 AI 使用声明

- **绝不编造**数据、求解结果与文献引用；不确定性如实汇报（模型局限、数据缺口、参数敏感性）。
- **核心建模与分析必须由队员独立完成**：工具只提供方法、代码骨架、结构与初稿，最终判断与文本由人负责。
- **AI 使用透明**：按赛事规定声明所用 AI 工具名称与版本、使用范围，并准备支撑材料；未按要求声明可能被取消评奖资格（口径与模板见 `workflows/10-AI使用声明.md`）。
- **竞赛期间独立完成**：不与他人讨论赛题；引用可追溯；原始数据不改、代码可复现、结果可核验。
- 三态标注（事实 / 推断 / 假设）与四大冷水（模型堆砌 / 重结果轻过程 / 摘要写砸 / 假设随意）是论文侧的常驻自查项，见 `Euler-CORE.md` 与 `references/cold-water.md`。

## 许可

- **代码**：MIT（见 `LICENSE`）。
- **文档与模板**：CC-BY-4.0（见 `LICENSE-DOCS`）。
- **第三方件**：来源、许可与修改说明见 `THIRD-PARTY.md`；`references/获奖级方法论/` 内 5 份方法论件来自 Lupynow/math-modeling-skills（MIT）。

> ⚠️ **发布状态提示（重要）**：`paper-templates/国赛-CUMCM/` 下的 `cumcmthesis.cls` 与 `cumcm2026.sty`
> **许可待核**（随附件未见明确许可头，已在 `THIRD-PARTY.md` 标 `[许可待核]`）。
> 在取得上游明确许可之前，**本仓库不得公开发布（no public release）**；
> 如需先行发布，请先移除该目录（或仅在内部分发）。

## 兼容性

本产品不依赖任何特定 agent / CLI / 调度器 / API key。

装载协议、门禁与冒烟全部由「可读文件 + 能跑 Python 的环境」组成——用它的是人还是任意 code agent，流程与产物一致。
