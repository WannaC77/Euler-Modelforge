# MODULE · E-M5 检验台（TEST）

> 所属：`modules/E-M5-检验台/`｜层：L0｜版本：v1.0（2026-09-21）｜引擎：`Euler-ENGINE.md` §1

## 目的 / Purpose
解 → 敏感性 + 互验：扫描报告、E1–E3 互验、量纲量级核对。

## 输入 → 输出 / IO
- 输入：求解产物（E-M4）
- 输出：敏感性报告卡 + 互验记录

## 接口字段 / Interface
敏感性报告卡：参数范围|方法（scan_1d/2d/tornado/sobol）|结果表|拐点/稳健区间|对结论影响|必要性声明（`templates/敏感性报告卡.md`）。

## 装载 / Loading（指针，细节在正本）
`workflows/06-模型检验与敏感性分析.md`；`templates-library/utils/sensitivity.py`

## 门禁 / Gates
scan_report 在；互验 ≥1 处 E3；量纲/量级清单过；按题型 ≥2 种检验

## 降级 / Fallback
手工敏感性（Excel/双跑）并声明

## 样例 / Example（合成或去敏）
scan_1d 合成示例输出（拐点位置打印）
