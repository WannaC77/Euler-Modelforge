# MODULE · E-M7 论文装配线（PAPER）

> 所属：`modules/E-M7-论文装配线/`｜层：L0｜版本：v1.0（2026-09-21）｜引擎：`Euler-ENGINE.md` §1

## 目的 / Purpose
求解 → 论文：双模板装配、四轮自审、Claim-Evidence、编译自检。

## 输入 → 输出 / IO
- 输入：求解/检验/图件产物
- 输出：论文 + 自查 + Claim-Evidence 表

## 接口字段 / Interface
装配 SOP：`references/论文装配SOP.md`；CE 表：`templates/Claim-Evidence映射表.md`。

## 装载 / Loading（指针，细节在正本）
`workflows/07-论文撰写.md`；`paper-templates/`（国赛-CUMCM / 美赛-MCM-ICM 双模板 + `编译自检.bat`）；`references/获奖级方法论/{abstract-writing,de-ai-writing,self-review-framework}.md`

## 门禁 / Gates
摘要五要素；四轮自审 + Claim-Evidence；引用一一对应；编译 exit 0；去 AI 味清单

## 降级 / Fallback
纯文本装配 + 人工清单；LaTeX 缺件 → 降级记录

## 样例 / Example（合成或去敏）
编译自检.bat 对最小骨架编译（smoke_chain M7 内实测）
