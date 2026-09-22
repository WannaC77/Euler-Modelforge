# MODULE · E-R 底座（BASE）

> 所属：`modules/E-R-底座/`｜层：L0｜版本：v1.0（2026-09-21）｜引擎：`Euler-ENGINE.md` §1

## 目的 / Purpose
环境/冒烟/故障/路径卡：可装载、可自检、可排障。

## 输入 → 输出 / IO
- 输入：—（基础设施）
- 输出：环境档位 / 冒烟表 / 故障卡

## 接口字段 / Interface
`tools/env_check.py`（档位）｜`tools/smoke_chain.py`（链冒烟）｜`templates-library/smoke_all.py`（35 模板冒烟）｜`references/路径与资产清单.md`｜`references/故障速查卡.md`。

## 装载 / Loading（指针，细节在正本）
同上 + `references/故障速查卡.md`

## 门禁 / Gates
env_check 可跑（档位明示）；smoke_all 全 PASS 表；smoke_chain FAIL=0

## 降级 / Fallback
手工核 ENGINE §6 环境卡；按故障卡处置

## 样例 / Example（合成或去敏）
smoke_all --quick / smoke_chain --selftest（合成，不评分不进锚）
