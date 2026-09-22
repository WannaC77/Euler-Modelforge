# QUICKSTART — 5 分钟上手（Euler-Modelforge）

> 前提：Python 3.11+。全程无需 API key、无需联网、无需任何特定 agent。

## 0. 拿包

```bash
git clone <本仓库 URL> Euler-Modelforge
cd Euler-Modelforge
```

## 1. 装依赖（可选但推荐）

```bash
python -m venv .venv
# 下面用 <venv> 指代你刚建的虚拟环境目录（本仓示例目录名 .venv）
<venv>/Scripts/python -m pip install -r templates-library/requirements.txt   # Windows
<venv>/bin/python     -m pip install -r templates-library/requirements.txt   # Linux/macOS
```

> 不装 venv 也能跑：`tools/` 与 `templates-library/` 会在系统 Python 下回退，
> 缺包时输出 `SKIP` 并说明原因（**不会**假装通过）。
> **用哪个解释器**：任一 Python 3.11+ 均可（本仓不写死路径）。机器上有多个解释器时，`env_check.py` 会自动挑选
> 依赖最全的一个；要显式指定就写在命令里（Windows `py -3.13 tools/env_check.py --selftest`、Linux/macOS `python3.13 tools/env_check.py --selftest`）。

## 2. 自检环境

```bash
python tools/env_check.py --selftest
```

输出各项 `[PASS]/[FAIL]/[SKIP]` 与档位（T0/T1/T2）。**FAIL 必须处理**，SKIP 请记下原因。
档位按 T0→T1→T2 连续判定（低档缺件会把整体档位压到该档），报告末行另给「分档可用性」逐档说明。

> 自检产物落 `<repo>/tools/_smoke_out/`（已在 `.gitignore`，可安全删除）；只读场景请在副本中执行。

## 3. 跑冒烟链（合成数据 · 已知答案）

```bash
python tools/smoke_chain.py --selftest     # 端到端：拆题卡 → 求解 → 图件 → 论文骨架（含数值断言）
python templates-library/smoke_all.py --quick   # 35 个求解模板冒烟
```

## 4. 装载（人 / code agent 通用）

```
1. 读 BOOT.md → Euler-CORE.md → Euler-ENGINE.md
2. 按任务选 runbook：workflows/00-备赛管理.md … 10-AI使用声明.md（+ workflows/_SHARED.md）
3. 产物落盘 → 过门禁（脚本 exit code）→ 记交接卡
```

code agent 请先读 `AGENTS.md`。

## 5. 第一条完整链（备赛期示例）

1. `workflows/02-选题与读题.md` → 用 `templates/拆题卡.md` 拆题
2. `workflows/04-建模.md` + `templates/模型卡.md` → 定模型族
3. `workflows/05-编程求解.md` → 从 `templates-library/` 选模板，改数据跑通（固定 seed）
4. `workflows/06-模型检验与敏感性分析.md` → 敏感性 + 互验
5. `workflows/07-论文撰写.md` → 双轨 LaTeX（`paper-templates/`）装配
6. `workflows/08-提交与答辩.md` → 跑 `scripts/` 提交前检查

## 6. 私有校准（L2 · 可选）

想接入自己的判准与锚样本：

```bash
mkdir -p kb            # 你的知识库（往届题、公开资料笔记）
cp templates/校准台账模板.md <校准台账>.md
cp templates/锚注册卡模板.md <锚注册卡>.md
```

机制说明见 `references/scoring-rubric.md`（含空锚表与**填锚规程**）。
**赛中禁跑校准**——校准只在备赛期/复盘期执行。

## 7. 出问题

- 环境/编译类 → `references/故障速查卡.md`
- 想改样式/图件 → `references/图件管线.md` + `templates-library/utils/`
- 许可与来源 → `THIRD-PARTY.md`
