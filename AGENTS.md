# AGENTS.md — code agent 装载协议（Euler-Modelforge）

> 本文件是**通用入口**：任何 code agent 按本文件即可装载本仓库（**已实测**：纯 shell+Python 执行器、零提示冷启动 agent 会话两路；OpenCode / Trae 为配置就绪说明，**非已完成实测**；Cursor / Codex / Aider / Windsurf 等按 §5 配置）。
> **本产品不依赖**任何特定 agent、私有 skill 注册、junction、cron 或 MCP；装载只依赖「读文件 + 跑 Python」。

## 1. 三步装载（与 BOOT.md 一致）

```
1. 读 BOOT.md → 读 Euler-CORE.md → 读 Euler-ENGINE.md
2. 按用户任务选 runbook，加载对应 workflows/NN-*.md + workflows/_SHARED.md
3. 需要计算/门禁时调用 tools/ 或 scripts/（见 §3）；缺件标 [降级] 并继续
```

**渐进披露预算**：BOOT(≤2 KB) → CORE/ENGINE → workflows/tools。不要把整仓读进上下文。

## 2. 本仓库的结构契约

| 目录 | 作用 | 装载时机 |
|---|---|---|
| `Euler-CORE.md` | 人格、铁律、模块表、装载协议 | 必读 |
| `Euler-ENGINE.md` | 模块能力矩阵、门禁、环境卡 | 必读 |
| `modules/` | 模块说明（每个含门禁要点与**降级列**） | 按需 |
| `workflows/` | 运行手册（`00–10` + `_SHARED.md` + `W-ABSORB.md`） | 按任务 |
| `templates/` | 卡表模板（拆题卡 / 模型卡 / 假设表 / 复现卡 / 校准台账 / 锚注册卡 …） | 按任务 |
| `references/` | 方法论文档（判准 / 图件管线 / 装配 SOP / 故障速查） | 按需 |
| `tools/` | 可执行工具（`env_check` / `smoke_chain`） | 计算与自检 |
| `scripts/` | 门禁脚本（提交前检查） | 交付前 |
| `templates-library/` | 35 个求解模板 + `utils/` + `smoke_all.py` | 求解阶段 |
| `paper-templates/` | LaTeX 论文模板（美赛随包；国赛第三方模板需自备，见 `THIRD-PARTY.md`） | 写作阶段 |
| `kb/` | 用户自建知识库（空目录，见 `kb/README.md`） | 可选 |

## 3. 工具 CLI 契约（统一）

```
python tools/env_check.py [--selftest] [--json]
python tools/smoke_chain.py [--selftest] [--root <路径>]
python tools/<领域工具>.py --selftest
python scripts/<checker>.py <args>        # exit 0=PASS 1=FAIL 2=usage 3=依赖缺失
python templates-library/smoke_all.py [--quick]
```

- 所有脚本：**无用户绝对路径**；`--help` 可用（rc=0）；依赖见 `templates-library/requirements.txt`
- 门禁脚本**必须可失败**（自检里带反例）；`--selftest` 用于验证工具自身
- 退出码语义：`0` 通过 · `1` 失败 · `2` 用法/输入错误（文件不存在 / 参数缺失；**不抛栈**）· `3` 依赖缺失未执行（**未执行 ≠ 通过**）
- 自检产物落盘：`tools/_smoke_out/`、`templates-library/_smoke_out/`（已 `.gitignore`，可安全删除；交付前跑 `clean_delivery` 清理）；只读场景请在副本中执行
- 解释器：任一 Python 3.11+；多个解释器时脚本自探测依赖最全者（不写死路径）

**`--selftest` 支持表**（不支持者传了会走用法错误 rc=2，勿当成失败）：

| 支持 `--selftest` | 说明 |
|---|---|
| `tools/env_check.py` · `tools/smoke_chain.py` | 环境档位 / 全链冒烟（含黄金数值断言） |
| `templates-library/utils/figcheck.py` 等 utils | 按各自 docstring 声明的参数使用；`--help` 一律 rc=0 |

| 不支持（勿传 `--selftest`） |
|---|
| `scripts/precheck_paper.py`（退出码契约：0=PASS / 1=FAIL / 2=输入错误） · `templates-library/smoke_all.py`（用 `--quick` 或全量，另有 `--selftest` 见其 `--help`） · 各模板脚本（`templates-library/0*/*.py`，独立可跑，无自检参数） |

## 4. 降级约定（诚实性要求）

| 缺件 | 处理 |
|---|---|
| LaTeX（xelatex） | 论文产出标 `[降级]`，不生成 PDF；给出 `.tex` 与编译说明 |
| venv / 依赖（pulp / matplotlib / sklearn …） | 回退系统 Python 并声明版本；模板冒烟记 `SKIP` |
| CJK 字体 | 图注 / 标题改英文；在报告里注明 |

**禁止**：假装编译成功、伪造数值、把 SKIP 写成 PASS。

## 5. agent 侧配置片段（可选）

- **Cursor / Windsurf**：把本文件加入工作区规则（`.cursorrules` 或规则文件引用 `AGENTS.md`）。
- **CLI agent（Codex / Aider 等）**：把 `AGENTS.md` 放进 system 上下文，或让 agent 先读它。
- **纯 API / 裸 LLM**：system prompt 注入 `BOOT.md` 全文，再按需读取 `Euler-CORE.md`。

## 6. 禁止项

包内不存在、也不应创建：私有 agent 的正本路由文件、必须安装的私有 skill、cron 正本依赖、任何指向仓库外的绝对路径。
