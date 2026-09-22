# MODULE · E-M8 提交合规闸（SUBMIT）

> 所属：`modules/E-M8-提交合规闸/`｜层：L0｜版本：v1.0（2026-09-21）｜引擎：`Euler-ENGINE.md` §1

## 目的 / Purpose
论文 → 提交包：预检机检、MD5 打包、AI 记录提醒。

## 输入 → 输出 / IO
- 输入：论文定稿 + 附件
- 输出：提交包 + AI 记录表

## 接口字段 / Interface
提交包清单卡：`templates/提交包清单卡.md`；AI 记录：`templates/AI记录模板.md`。

## 装载 / Loading（指针，细节在正本）
`workflows/08-提交与答辩.md`·`10-AI使用声明.md`；`scripts/precheck_paper.py`（v2.3）

## 门禁 / Gates
precheck C1/B1 无 FAIL；MD5 + 打包清单；AI 记录提醒（国赛须声明）

## 降级 / Fallback
清单人工核 + 官方规则对照

## 样例 / Example（合成或去敏）
precheck 对合成样本 rc/输出一览（三样本回归零漂移为既有先例）
