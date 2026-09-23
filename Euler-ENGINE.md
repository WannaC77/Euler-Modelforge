# Euler-ENGINE — 生成引擎（模块注册 · 门禁 · runbook · 装载）

> **用途 / Purpose**：数学建模竞赛（美赛 MCM/ICM + 国赛 CUMCM）生成引擎；哲学＝**冲刺可执行；倒计时砍范围不砍深度**。
> **装载 / Mount**：任何可读文件 + 跑 Python 的人或 agent 按 §0 三步装载；不依赖任何 agent 私有机制。
> **正本 / SSOT**：细节正本在 `workflows/` 与各模块规格件；**本文件只索引，不复制正文**。
> **版本 / Version**：v1.2（2026-09-22）· 模块 10 + 底座 · 执行方：任何可读文件 + 跑 Python 者（无私有依赖）
> **分层 / Layers**：L0 领域能力（本文件 · `modules/` · `templates/` · `tools/` · `templates-library/**` 模板库 · `paper-templates/**`）｜L1 配置剖面（`Euler-CORE.md` 双赛事节 = 美赛/国赛 profile）｜L2（`<校准台账>` · `<锚注册卡>/` · <校准标准> 个人校准——只读引用）
> **开源兼容**：新建 L0 全部系统相对路径；L0 不依赖个人判档线/锚分；赛事参数在 L1 profile 小节。

## 0 · 装载协议（三步 · 任意 agent）

1. 读 `Euler-CORE.md`（人格与铁律）→ 读本文件（模块与 runbook）。
2. 按所选 runbook 的装载清单加载 **L0/L1**；环境优先 `<venv>`。缺件按模块表「降级」列执行并标 `[降级]`。
3. 产物落盘 → 过对应门禁（§3）→ 记交接卡（§7）。

**环境自检**：`tools/env_check.py`（已落盘；`--selftest` 可自证；档位 T0/T1/T2）；链级冒烟 `tools/smoke_chain.py`（v1.2）；模板冒烟 `templates-library/smoke_all.py`。

**路径基点（SSOT · 双基准写死）**：

| 写法 | 基点 | 实际 |
|---|---|---|
| `**`（仓内一切） | **仓根** | references / workflows / scripts / templates / tools / modules / templates-library / paper-templates |
| 模板库 / 论文模板 / kb | **仓根** | `templates-library/…`、`paper-templates/…`、`kb/…` |
| `<锚注册卡>/` | 共享根 | 锚注册卡（L2） |

## 1 · 模块注册表（L0 · interface: loading → output → gates → fallback）

| # | 模块 | 一句话 | 装载（指针） | 产物 | 门禁要点 | 降级 |
|---|---|---|---|---|---|---|
| E-M1 | 读题定位器 | 题目→拆题卡 | `workflows/02–03`；`references/获奖级方法论/problem-decomposition.md` | 拆题卡 / 选题评估矩阵 | 字段完整；子问题有题型/模型族初判；数据可得性 | 手工拆题 + CORE 铁律 |
| E-M2 | 假设与符号台 | 假设/符号→两表 | `workflows/03`·`04` 回写区 | 假设表 / 符号表.tex | 三段式（表述+依据+对应环节）；黑名单零命中；符号与代码/论文一致 | 手工两表 + 一致性人检 |
| E-M3 | 建模选型器 | 问题→模型卡 | `workflows/04`；`references/获奖级方法论/model-selection-matrix.md`；KB concepts | 模型卡 | 模型卡齐；名词清单穷尽；融合同验证集对照；无映射模型删除 | 手工选型 + 决策记录 |
| E-M4 | 求解工坊 | 模型→求解+复现 | `workflows/05`；`templates-library/`（35 模板 + utils + <venv>） | 求解报告 + artifacts | 模板冒烟 rc=0；种子固定；报告卡齐；改进四件事（基线/改动/量化/公平） | 手写脚本 + 人检 |
| E-M5 | 检验台 | 解→敏感性+互验 | `workflows/06`；`templates-library/utils/sensitivity.py` | 敏感性报告卡 | scan_report 在；互验 ≥1 处 E3；量纲过；题型 ≥2 种检验 | 手工敏感性分析 |
| E-M6 | 图件车间 | 数据→出版级图 | `references/图件管线.md`；`templates-library/utils/plot_style.py`（v2）+ `figcheck.py` | PNG+PDF+SVG + 图注 | 三闸（audit_fig / figcheck / vision；无 vision 则双闸+人检） | 双闸 + 人检 |
| E-M7 | 论文装配线 | 求解→论文 | `workflows/07`；`paper-templates/`（双模板 + `编译自检.bat`） | 论文 + 自查 + Claim-Evidence 表 | 摘要五要素；四轮自审 + CE 映射；引用一一对应；编译 exit 0；去 AI 味清单 | 纯文本装配 + 清单 |
| E-M8 | 提交合规闸 | 论文→提交包 | `workflows/08`·`10`；`scripts/precheck_paper.py`（v2.3） | 提交包 + AI 记录表 | precheck C1/B1 无 FAIL；MD5 + 打包清单；AI 记录提醒 | 清单人工核 |
| E-M9 | 校准与锚（L2 挂接） | 只声明边界 | `<校准台账>`（存在性） | 无 | 只声明「存在校准台账、备赛期只读挂接」；**赛中禁跑**；个人判档线不入门禁 | 不挂接亦可走全链 |
| E-M10 | 编排器 | runbook+交接卡 | 本文件 §4/§7 | 交接卡 | 每交付一次交接记录 | 口述交接 + 记录 |
| E-R | 底座 | 环境/冒烟/故障/路径卡 | `references/路径与资产清单.md`；`tools/{env_check,smoke_chain}.py`；`templates-library/smoke_all.py` | 环境档位 / 冒烟表 / 故障卡 | env_check；smoke_all 全 PASS 表（35/35） | 手工核 §6 |

## 2 · 数据流

```text
M1 拆题卡 → M2 假设/符号 → M3 模型卡 → M4 求解报告 + artifacts
→ M5 敏感性 → M6 图 → M7 论文 → M8 提交包
M9 校准：备赛期挂接、赛中禁跑（L2）
```

## 3 · 门禁矩阵

| 阶段 | 机检/清单 | 通过线 |
|---|---|---|
| 拆题 / 建模 / 求解 / 检验 / 图件 / 论文 / 提交 | 同模块门禁；`precheck_paper.py`；`编译自检.bat`；`smoke_all.py`（35 模板） | 见 §1 |
| 底座自检 | `env_check.py`（档位）+ `smoke_chain.py`（链冒烟） | rc=0（SKIP 不算 FAIL；WARN 需登记） | 输出 + `_smoke_out/` 报告 |
| **未来兼容** | 新建 L0 无用户绝对路径；`W-ABSORB` 在装载清单；模板数与 README 一致（或已勘误） | grep / 清单 |

## 4 · Runbooks

| # | 线 | 说明 | 产物 |
|---|---|---|---|
| RB-E1 | 备赛模拟全流程 | M1→…→M8 + 时间盒 / AI 记录 | 全链产物 |
| RB-E2 | 单题建模快线 | 拆题 → 模型卡 → 骨架（白名单 / 训练） | 骨架 + 卡 |
| RB-E3 | 论文定稿线 | 图 → 装配 → 预检 → 自审 → 编译 | 论文 + 自检输出 |
| RB-E4 | 生成锚线（组织者 / L2） | 台账纪律；**赛中禁用** | 锚记录 |
| RB-E5 | 复盘线 | learnings → KB → 台账 | 复盘条目 |

## 5 · 资产清单（L0 抬包清单 · 新增件落盘即登记）

| 件名 | 相对路径 | 版本 | 模块 | 层 | 状态 |
|---|---|---|---|---|---|
| 引擎（本文件） | `Euler-ENGINE.md` | v1.0 | E-M10 | L0 | ✅ |
| SSOT 卡 | `references/路径与资产清单.md` | v1.0 | E-R | L0 | ✅ |
| 工作流正本 00–10 | `workflows/00–10` | — | 全域 | L0 既有·**正文冻结** | ✅ |
| 工作流共享层 + 吸收层 | `workflows/_SHARED.md` · `W-ABSORB.md` | — | 全域 | L0 既有 | ✅ |
| 冷水 | `references/cold-water.md` | — | 全域 | L0 既有 | ✅ |
| 评分协议 | `references/scoring-rubric.md` | v2.1 | E-M7/M8 | L0(协议) / L2(校准数据) | ✅ |
| 图件管线 | `references/图件管线.md` | — | E-M6 | L0 既有 | ✅ |
| 获奖级方法论 | `references/获奖级方法论/`（6 件：abstract-writing / de-ai-writing / model-selection-matrix / problem-decomposition / self-review-framework / _来源与可选资源） | — | E-M1/M3/M7 | L0 既有 | ✅ |
| 预检脚本 | `scripts/precheck_paper.py` | v2.3 | E-M8 | L0 既有 | ✅ |
| 模板库 35 | `templates-library/`（8 类 35 模板 + `MODEL_GUIDE.md` + `requirements.txt`） | — | E-M4 | L0 既有 | ✅ |
| utils 4 | `templates-library/utils/`（plot_style v2 / sensitivity / latex_table / figcheck） | — | E-M4/M5/M6 | L0 既有 | ✅ |
| 论文模板双轨 | `paper-templates/`（美赛-MCM-ICM 随包；国赛-CUMCM 第三方许可待核**不随包**，目录内留 README 指引 / `编译自检.bat` / 两份说明） | — | E-M7 | L0 既有 | ✅ |
| 生成侧训练台账 | `<校准台账>`（changelog v1.4） | v1.4 | E-M9 | L2 | ✅ |
| 锚注册卡 | `<锚注册卡>/`（11 件） | — | E-M9 | L2 | ✅ |
| 模块规格件 ×11 | `modules/E-M*/MODULE.md`（四件：目的/接口/门禁/降级） | v1.0 | 各模块 | L0 | ✅ |
| 模板集 ×10 | `templates/`（拆题卡 / 选题评估矩阵 / 假设表 / 符号表.tex / 模型卡 / 复现卡 / 敏感性报告卡 / Claim-Evidence 映射表 / 提交包清单卡 / AI 记录模板） | v1.0 | E-M1–M8 | L0 | ✅ |
| 工具集 | `tools/{env_check,smoke_chain}.py`（v1.2）；`templates-library/smoke_all.py`；`templates-library/utils/figkit/`（5 demo + gray_cb_check） | v1.0/1.1 | E-M4/M6/R | L0 | ✅ |
| 参考卡 ×4 | `references/`（求解报告规范 / 论文装配SOP / 图注模板 / 故障速查卡） | v1.0 | 各模块 | L0 | ✅ |

## 6 · 环境卡（以本机 `env_check` 实测为准）

| 项 | 值 |
|---|---|
| 参考解释器 | Python 3.11+（推荐 3.13；`tools/env_check.py` 自探测依赖最全的解释器，不写死路径） |
| 虚拟环境（可选） | 自建 `<venv>`；缺件时回退系统 Python 并按模块「降级」列声明 |
| LaTeX | 双模板 + `编译自检.bat`（xelatex）；缺字体按降级记录 |
| 可选件 | TeX 全套 / Word COM——缺件按模块降级列声明 |

> **档位以本机 `env_check.py` 输出为准**：本卡不记录任何特定机器的实测值（T0/T1/T2 为连续达标口径——低档缺件会把整体档位压到该档；报告另给「分档可用性」逐档说明）。

## 7 · 交接卡模板（E-M10）

```markdown
## 交接卡 <日期> · <模块>
- 输入：<上游产物 + 路径>
- 产物：<落盘路径 + 版本>
- 门禁：<过了哪条 + 留证路径>
- 降级/未决：<[降级] 标记项；待裁定项>
- 下一步：<runbook / 节点>
```

## 8 · 维护纪律

- 新增 L0 件：四件齐（目的 / 接口 / 门禁 / 降级）→ 落盘 → 登记 §5 → 过「未来兼容」门。
- 本文件**禁止抄写 workflows 正文**；模块细节进 `modules/` 规格件。
- L2（锚/判档/生成锚）**不阻塞 L0**；门禁不得把个人判档线写成必要通过条件；**赛中禁跑校准**。
- 每次修改本文件，在文末追加一行变更记录。

---

**变更记录**
- v1.0（2026-09-21 · 生成侧强化批 2）：骨架建立（装载协议 / 双基准 SSOT / 模块注册 ×11 / 数据流 / 门禁矩阵 / runbooks RB-E1–E5 / 资产清单 / 环境卡 / 交接卡 / 维护纪律）。
- v1.1（2026-09-22 · 生成侧强化批 4 · 总装）：模块规格件 ×11 / 模板集 ×10 / 工具集（env_check · smoke_chain v1.1 · smoke_all · figkit）/ 参考卡 ×4 全部落盘并登记；smoke_all 35/35、smoke_chain 全 PASS；门禁行挂接实路径。
- v1.2（2026-09-22 · 开源发布批）：资产清单版本对齐（smoke_chain v1.1→v1.2，与脚本自报 VERSION 一致）；`scripts/precheck_paper.py` 退出码契约修正（输入错误 → 2 且不再抛栈；`--help` → 0）；QUICKSTART/AGENTS 补「无 venv 时的解释器选择」与「自检产物落盘位置」；环境卡改为以本机 env_check 实测为准。
