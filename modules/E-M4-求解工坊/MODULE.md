# MODULE · E-M4 求解工坊（SOLVE）

> 所属：`modules/E-M4-求解工坊/`｜层：L0｜版本：v1.0（2026-09-21）｜引擎：`Euler-ENGINE.md` §1

## 目的 / Purpose
模型 → 求解 + 复现：模板库直用、artifacts 落盘、报告卡齐。

## 输入 → 输出 / IO
- 输入：模型卡（E-M3）+ 数据
- 输出：求解报告 + artifacts + 复现卡

## 接口字段 / Interface
求解报告规范：`references/求解报告规范.md`；复现卡：环境|数据版本|命令|产物列|预期数值|差异容忍（`templates/复现卡.md`）。

## 装载 / Loading（指针，细节在正本）
`workflows/05-编程求解.md`；`templates-library/`（35 模板 + utils + `<venv>`）；`templates-library/MODEL_GUIDE.md`

## 门禁 / Gates
模板冒烟 rc=0（`smoke_all.py`）；种子固定；报告卡齐；改进四件事（基线/改动/量化/公平对照）

## 降级 / Fallback
手写脚本 + 人检；缺 venv → 系统 Python 并声明

## 样例 / Example（合成或去敏）
`smoke_all.py` 全量 35/35 rc=0（合成/自示例数据）
