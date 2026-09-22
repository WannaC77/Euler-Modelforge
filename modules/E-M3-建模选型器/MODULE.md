# MODULE · E-M3 建模选型器（MODEL）

> 所属：`modules/E-M3-建模选型器/`｜层：L0｜版本：v1.0（2026-09-21）｜引擎：`Euler-ENGINE.md` §1

## 目的 / Purpose
问题 → 模型卡：模型族选择、名义清单穷尽、融合验证。

## 输入 → 输出 / IO
- 输入：子问题（E-M1）+ 假设/符号（E-M2）
- 输出：模型卡（每题一卡）

## 接口字段 / Interface
模型卡：模型名|模型族|假设链接|输入输出|求解器|验证（E1/E2/E3）|名词清单条目|混搭说明。模板：`templates/模型卡.md`。

## 装载 / Loading（指针，细节在正本）
`workflows/04-建模.md`；`references/获奖级方法论/model-selection-matrix.md`；`../kb/` concepts（存在者）

## 门禁 / Gates
模型卡齐；模型名词清单穷尽；融合/混搭须同验证集对照；无映射模型删除

## 降级 / Fallback
手工选型 + 决策记录入 <共享层>/决策日志

## 样例 / Example（合成或去敏）
模型卡示例：多目标选址=NSGA-II / 加权和（混搭说明占位）
