# MODULE · E-M1 读题定位器（READ）

> 所属：`modules/E-M1-读题定位器/`｜层：L0｜版本：v1.0（2026-09-21）｜引擎：`Euler-ENGINE.md` §1

## 目的 / Purpose
题目 → 拆题卡 / 选题评估：子问题拆解、题型与模型族初判、数据可得性。

## 输入 → 输出 / IO
- 输入：赛题原文（含附件数据）
- 输出：拆题卡 / 选题评估矩阵

## 接口字段 / Interface
子问题表（题号|要求|题型初判|模型族初判|数据可得性|难点）+ 全局约束 + 交付物清单。模板：`templates/拆题卡.md`、`选题评估矩阵.md`。

## 装载 / Loading（指针，细节在正本）
`workflows/02-选题与读题.md`·`03-问题分析与假设.md`（正本）；`references/获奖级方法论/problem-decomposition.md`

## 门禁 / Gates
字段完整；子问题有题型/模型族初判；数据可得性逐项列明（缺数据=显式风险）

## 降级 / Fallback
手工拆题 + CORE 铁律；无方法论文件时按 workflows 参数表逐项填卡

## 样例 / Example（合成或去敏）
拆题卡示例行：子问题→题型（优化/预测/评价）→模型族（LP/ARIMA/TOPSIS）占位
