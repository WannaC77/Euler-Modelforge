# Euler-Modelforge · 数学建模竞赛工作流（中文版）

![python](https://img.shields.io/badge/python-3.11%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![docs](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey)
![smoke](https://img.shields.io/badge/smoke-35%2F35%20PASS-brightgreen)
[![CI](https://github.com/WannaC77/Euler-Modelforge/actions/workflows/ci.yml/badge.svg)](https://github.com/WannaC77/Euler-Modelforge/actions/workflows/ci.yml)

> **从赛题到可提交论文的硬时间盒流程**：每一步有门禁，每一个结论留证据，缺件照实标 `[降级]`。
> **英文版 / English version**：`README.en.md`（本文件为中文正本；同步承诺见 `CONTRIBUTING.md`「双语同步 SLA」）
> **CI**：`.github/workflows/ci.yml` 在每次 push / PR 上跑自检与冒烟（Python 3.11 + 3.13 双版本）——上方 CI 徽章为实时状态。
> **仓库 / Releases**：<https://github.com/WannaC77/Euler-Modelforge> · <https://github.com/WannaC77/Euler-Modelforge/releases>

---

## 一句话定位

**Euler-Modelforge 是一套「手册 + 工具链」形态的数学建模竞赛工作流**：把「读题 → 假设 → 建模 → 求解 → 检验 → 图件 → 论文 → 提交」拆成 10 个带**门禁**与**降级**路径的模块，方法写在 `workflows/` 与 `references/`，自检交给 `tools/` 与 `templates-library/`——任何能读文件、能跑 Python 的人或 code agent 都能按三步装载直接开工。

## 为什么需要它（Why）

- 竞赛论文的分数，不是由「用了多少模型」决定的，而是由**过程能不能复核、结论能不能追溯**决定的——但倒计时里没人有空临时搭一套流程；
- 流程散在聊天记录、往届论文和脑子里 → 换个题型、换批队友就重来一遍：本包把它固化成一棵**按需装载的文件树**，而不是又一个模板合集；
- 备赛期最常见的挫败不是「不会建模」，而是「跑不通、装不上、不知道缺什么」——本包把缺件写成制度：`[降级]` / `SKIP` 一律如实标注并给出替代路径，**绝不假称通过**。

## 目标用户

- 参加数学建模竞赛（美赛 MCM/ICM、国赛 CUMCM 及同类赛事）的队伍与指导教师；
- 想用一套可复现、带门禁的流程写建模论文的个人研究者；
- 把方法论交给 code agent 执行、需要明确装载协议与退出码约定的用户。

**门槛**：不需要会 LaTeX、不需要预先学一套新工具——会读文件、能跑 `python` 就能走完全链（求解模板与自检都是现成脚本）；建模判断与论文文本仍由你本人负责。

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
| E-M7 论文装配线 | 求解 → 论文：LaTeX 装配（**美赛模板随包；国赛模板需自备**）、四轮自审、Claim-Evidence 映射、编译自检 |
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
├── scripts/                   precheck_paper.py · verify_manifest.py（文档-磁盘一致性自证）
├── templates-library/         求解模板库 + utils/ + MODEL_GUIDE.md + smoke_all.py
├── paper-templates/           LaTeX 论文模板（美赛随包；国赛为外置位，需自备）+ 编译自检
├── kb/                        自建知识库（空目录 + 自建说明）
├── docs/images/               真实运行生成的样张（本文件「5 分钟你会拿到什么」引用）
├── LICENSE / LICENSE-DOCS / THIRD-PARTY.md
├── CONTRIBUTING.md / CODE_OF_CONDUCT.md / SECURITY.md / SUPPORT.md   贡献 / 行为准则 / 安全 / 支持
├── MAINTAINERS.md / .editorconfig / .gitattributes / .pre-commit-config.yaml   维护者 / 开发约定
├── .github/                   CI（workflows/ci.yml）· issue 与 PR 模板 · CODEOWNERS · dependabot
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

约定：全 PASS / SKIP 即 rc=0；**SKIP 不算 FAIL**；WARN 需登记；FAIL 非零退出。退出码语义统一为 `0` 通过 · `1` 失败 · `2` 用法错误（含输入错误，**不抛栈**）· `3` 依赖缺失未执行（**未执行 ≠ 通过**）。

### 验收状态（可复跑）

| 面 | 判据 | 命令 |
|---|---|---|
| 模板库 35 件 | 8 类逐件跑通（rc=0；缺依赖 → rc=3 未执行，单列 SKIP） | `python templates-library/smoke_all.py`（CI 跑 `--quick` 8 件） |
| 关键数值 | 合成 LP 解析真值（精确有理数顶点法）±1e-6 + 敏感性区间 | `python tools/smoke_chain.py --selftest` |
| 环境档位 | T0/T1/T2 降级探测 | `python tools/env_check.py --selftest` |
| 提交预检 | 退出码契约 0/1/2 | `python scripts/precheck_paper.py` |

> 模板层只判「跑通 / 未执行」，**数值真值断言集中在 `tools/smoke_chain.py`**（不逐件复制真值，避免 35 份重复断言各自漂移）。

## L2 自建（不随包分发）

| 自建项 | 作用 | 起步方式 |
|---|---|---|
| `kb/` | 你的知识库：模型方法、论文拆解、检索索引 | 按 `workflows/09-知识管理.md` 的 schema 起步 |
| `<共享层>/` | 可选的多 agent / 多人协作层（共享 SOP 与材料） | 单人使用可完全跳过 |
| `<校准台账>` | 私有校准数据（判档线 / 复盘记录 / 整改记录） | `templates/校准台账模板.md`（空白） |
| `<锚注册卡>/` | 私有锚注册（已知答案锚 / 已知档位锚样本） | `templates/锚注册卡模板.md`（空白）+ 填锚规程见 `references/scoring-rubric.md` |

> L2 是**可选增强**：只用 L0 也能跑完整条链；没有 L2 时相关模块走「降级」列。

## 它从哪里长出来（实战演变）

**Origin timeline**：本包骨架脱胎于本人 2026 年 8 月起搭的数模备赛工作流，经备赛期两轮评委尺子校准（rubric v1.5 → v2.1）与模板库冒烟补齐；开源剥离工作自 2026-09-22 启动（本包 v1.0.0）。

本包的方法与门禁同样有实战由来，每条都能在评审台账与冒烟报告里复现：

**成功案例**
- **35 个求解模板全量冒烟 35/35 PASS**，LP 黄金数值断言对出解析最优值 21.0（解析真值 vs 数值解差 <1e-6）；报告落 `templates-library/_smoke_out/`，可复跑。
- **评委尺子校准机制**：独立 holdout（12 篇获奖论文）判档一致性由私有校准台账独立自证（含逐维控制对照）——台账不随包，但校准流程与失败案例的整改闭环（见下）就是这套机制的直接产物。

**失败典型**
- **评委初评 10 篇只对 7 篇**：三个跨级判错案例（三道往届题各一）没有掩盖，而是写进台账，成为 rubric v2.0 → v2.1 的整改依据。
- **生成臂自证循环**：一段建模文风目标在同题对照下暴露"构念错配"（片段强但全文档位被错判）——如实登记为「限缩放行」而非硬咽，生成侧锁到独立验证前置状态。
- **holdout 惟一失手（脱敏叙事）**：一篇往届赛题被高估一档——未刷绿、留档待样本扩容后重校（具体赛题与分数在私有台账）。

> 更多原记录见 `learnings.md`（错题本，机制与格式随包，条目不随包）。

## 学术诚信与 AI 使用声明

- **绝不编造**数据、求解结果与文献引用；不确定性如实汇报（模型局限、数据缺口、参数敏感性）。
- **核心建模与分析必须由队员独立完成**：工具只提供方法、代码骨架、结构与初稿，最终判断与文本由人负责。
- **AI 使用透明**：按赛事规定声明所用 AI 工具名称与版本、使用范围，并准备支撑材料；未按要求声明可能被取消评奖资格（口径与模板见 `workflows/10-AI使用声明.md`）。
- **竞赛期间独立完成**：不与他人讨论赛题；引用可追溯；原始数据不改、代码可复现、结果可核验。
- 三态标注（事实 / 推断 / 假设）与四大冷水（模型堆砌 / 重结果轻过程 / 摘要写砸 / 假设随意）是论文侧的常驻自查项，见 `Euler-CORE.md` 与 `references/cold-water.md`。

## 5 分钟你会拿到什么

不读参数、不听承诺——直接看真跑出来的样子。以下产物都是**本仓库真实运行生成**（合成数据、固定 seed）：

| 产物 | 它是什么 | 你怎么拿到它 |
|---|---|---|
| ![分组柱状图（Baseline vs Proposed，含显著性标注与灰度斜纹）](docs/images/figkit_demo1_grouped_bar.png) | 出自 `templates-library/utils/figkit/` 的分组柱状图样例 | `QUICKSTART.md` 第 3 步 `python tools/smoke_chain.py --selftest` 里跑出来的东西（smoke 的 M6 阶段跑的就是这个脚本） |
| ![敏感性热图（6 参数 × 12 时刻，对称色阶）](docs/images/figkit_demo2_heatmap.png) | 出自 figkit 的热图样例 | 同一条链里 M6 敏感性的图型参照（figkit demo2） |
| ![smoke_chain 自检输出（PASS/SKIP 明细与判定行）](docs/images/smoke_chain_selftest_output.txt) | 冒烟链的**文本输出**（判定：FAIL=0 → PASS） | `QUICKSTART.md` 第 3 步命令在你终端里的样子——跑完判断装没装好，就是看这段 |

看完如果觉得「这就是我要的」：回 `QUICKSTART.md` 从第 0 步开始跑。

## 维护与发布

- **维护者 / 支持**：`MAINTAINERS.md`（守门范围）· `SUPPORT.md`（提问前先跑自检；首应 ≤ 7 天）
- **版本与回滚**：`CHANGELOG.md`（SemVer tag 约定 + 逐版条目）——按 tag 回退到已知可用版本
- **中英同步**：中文正本 → 英文版 ≤ 7 天（承诺见 `CONTRIBUTING.md`「双语同步 SLA」）
- **提交 PR 前**：`pip install pre-commit && pre-commit run --all-files`（钩子清单见 `.pre-commit-config.yaml`）
- **文档-磁盘一致性**：`python scripts/verify_manifest.py --root .`（缺件 → rc=1；用法错误 → rc=2；判据自带 `--selftest`）

## 相关项目（姊妹项目）

**[Vesi-Labflow](https://github.com/WannaC77/Vesi-Labflow)** 是本包的姊妹项目：同一套「单核多轨 + 装载纪律 + 可失败门禁」架构方法论在**生命科学 / 制剂-PK 领域**的实现（文献-设计-记录-统计-图件-论文-交付全链）。两包架构同源、领域不同，可独立使用。
## 许可

- **代码**：MIT（见 `LICENSE`）。
- **文档与模板**：CC-BY-4.0（见 `LICENSE-DOCS`）。
- **第三方件**：来源、许可与修改说明见 `THIRD-PARTY.md`；`references/获奖级方法论/` 内 5 份方法论件来自 Lupynow/math-modeling-skills（MIT）。

> ℹ️ **发布状态提示**：`paper-templates/国赛-CUMCM/` 的第三方模板（`cumcmthesis.cls` / `cumcm2026.sty`，许可待核）
> **不随本包分发**——该目录内只留一份获取与启用指引（`paper-templates/国赛-CUMCM/README.md`），
> 需要国赛模板请自行从上游获取。**除此之外本仓库可直接公开发布**；美赛模板随包分发（LPPL 1.3+）。

## 兼容性

本产品不依赖任何特定 agent / CLI / 调度器 / API key。

装载协议、门禁与冒烟全部由「可读文件 + 能跑 Python 的环境」组成——用它的是人还是任意 code agent，流程与产物一致。
