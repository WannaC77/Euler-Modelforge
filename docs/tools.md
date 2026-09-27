# 工具索引

## 命令（pip 安装后直接可用）

| 命令 | 用途 |
|---|---|
| `euler-env-check` | 环境档位判读（T0/T1/T2）+ 缺件降级清单；`--selftest` 自检 |
| `euler-smoke-chain` | 端到端冒烟：环境 → 模板 → 求解 → 图件 → 论文装配（含黄金数值断言）；`--selftest` |
| `euler-smoke-templates` | 35 模板库批量冒烟（`--quick` 快速模式） |
| `euler-precheck-paper` | 论文提交预检（结构 / 图注 / 合规项）；退出码契约 `2 = 用法` |
| `euler-verify-manifest` | 文档-磁盘一致性自证（`--root <树根>`） |

源码模式下对应 `python tools/<名>.py` 与 `python scripts/<名>.py`。

## 模板库（templates-library/）

8 大类 35 个可运行模板：优化 / 预测 / 评价 / 统计与机器学习 / 微分方程 / 图论 / 仿真 / 智能算法。
批量冒烟：`python templates-library/smoke_all.py`（缺依赖项以 SKIP 诚实标注）。

## 图件车间（templates-library/utils/figkit/）

- 5 个样张脚本：`figkit_demo1_grouped_bar.py` … `figkit_demo5_schematic.py`
- 灰度/色盲可辨机检：`gray_cb_check.py`
- 产物落在 `_out/`（png / pdf / svg 三件）

## 脚本（scripts/）

- `precheck_paper.py` —— 论文提交预检（退出码契约：`0` PASS · `1` FAIL · `2` usage）
- `verify_manifest.py` —— 文档引用的仓内路径逐条对质（`--root .`）

## 退出码约定

全仓统一：`0` 通过 · `1` 失败 · `2` 用法错误 · `3` 依赖缺失未执行（未执行 ≠ 通过）。
