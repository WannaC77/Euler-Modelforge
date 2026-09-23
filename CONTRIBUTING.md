# 贡献指南 / Contributing · Euler-Modelforge

感谢你考虑为本项目做贡献。本仓库是「工作流 + 求解模板 + 可执行工具」的开源包，质量门槛偏**可复核**：
凡结论都要能复跑，凡数值都要有**黄金断言**，凡判据都要**能失败**。

## 可以贡献什么

| 类型 | 例子 | 需要带的证据 |
|---|---|---|
| 缺陷报告 | 工具报错、模板跑不通、文档与磁盘不符 | 复现命令 + 实际输出 + 期望输出（见 issue 模板） |
| 求解模板 | 新增一类模型的可用模板、参数校验、已知答案算例 | 模板自带 `--selftest` / 已知答案对照（误差与容差写明） |
| 工作流改进 | 选题、建模、检验、论文装配、提交闸的步骤修正 | 与 `Euler-CORE.md` 铁律、`references/scoring-rubric.md` 判准不冲突 |
| 文档 | 题型映射、术语表、故障速查 | 与包内正本（`references/路径与资产清单.md` / `Euler-ENGINE.md`）不冲突 |
| 赛事适配 | 把工作流改写到你的目标赛事 | 只改口径与匿名面，不改机制 |

## 硬性要求（review 会直接打回）

1. **不改私有数据**：不要提交真实赛题数据、他人论文、机构名、个人身份信息、获奖材料原文。
2. **不引入私有依赖**：本包不依赖任何特定 agent / CLI / 调度器 / API key。
3. **模板必须可自检**：`templates-library/**` 下的模板要能在 `templates-library/smoke_all.py` 里跑通；
   涉及数值的模板请附**已知答案**（解析解或标准算例）与容差。
4. **退出码语义统一**：`0` 通过 · `1` 失败 · `2` 用法/输入错误 · `3` 依赖缺失未执行（**未执行 ≠ 通过**）。
5. **文本件**：UTF-8 无 BOM、LF 行尾、包内相对路径（正斜杠）、不写绝对路径与本机路径。
6. **不在包内留生成物**：自检 / 冒烟产物落 `_smoke_out/`、`templates-library/data/*.png`（均已 gitignore），提交前清理。

## 开发与自检（本地）

```bash
python -m venv <venv> && <venv>/bin/pip install -r templates-library/requirements.txt   # Windows: <venv>\Scripts\pip
python tools/env_check.py --selftest        # 环境档位 T0/T1/T2
python tools/smoke_chain.py --selftest      # 全链冒烟 M1→M4→M6→M7（含黄金数值断言）
python templates-library/smoke_all.py --quick   # 35 模板冒烟
python scripts/precheck_paper.py            # 论文提交预检（退出码契约 0/1/2）
```

CI（`.github/workflows/ci.yml`）执行同一组命令，本地等价脚本见 `QUICKSTART.md`。

## 提交规范

- 一个提交只做一件事；提交信息说清**动机**（中文一句话即可）。
- 涉及口径变更的提交，请同步更新受影响的 `workflows/`、`references/路径与资产清单.md`、`CHANGELOG.md`。
- 提交前自查：`git status` 里不应出现自检产物（`_smoke_out/`）、Python 缓存目录（`__pycache__`）、生成图、本机路径。

## 评审口径

- 结论要有证据（复跑命令 + 输出）；「我觉得」不是证据。
- 判据要能失败：只证明「能通过」的测试不算测试。
- 允许 `SKIP`（缺件降级），但必须写明缺件原因，且 `SKIP` 不得被读成通过。
- 国赛（CUMCM）模板**不随包分发**（第三方许可待核，见 `THIRD-PARTY.md`）；相关贡献请勿提交该模板本体。

## 许可

提交即表示你同意按本仓库许可分发你的贡献：代码 MIT（`LICENSE`）、文档 CC BY 4.0（`LICENSE-DOCS`）。
