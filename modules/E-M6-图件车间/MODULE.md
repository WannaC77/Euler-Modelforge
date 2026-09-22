# MODULE · E-M6 图件车间（FIG）

> 所属：`modules/E-M6-图件车间/`｜层：L0｜版本：v1.0（2026-09-21）｜引擎：`Euler-ENGINE.md` §1

## 目的 / Purpose
数据 → 论文级图：三格式输出、黑白色盲友好、图注齐。

## 输入 → 输出 / IO
- 输入：结果数据/求解产物
- 输出：PNG+PDF+SVG + 图注

## 接口字段 / Interface
图注四要素（`references/图注模板.md`）；样例：`templates-library/utils/figkit/`（对比/热图/网络/多面板/示意 + gray_cb_check）。

## 装载 / Loading（指针，细节在正本）
`references/图件管线.md`；`templates-library/utils/plot_style.py`（v2）+ `figcheck.py`

## 门禁 / Gates
三闸：audit_fig（越界）/ figcheck（文件层）/ vision 复核（无 vision 则双闸+人检）；黑白色盲检查（gray_cb_check，可选降级为目视）

## 降级 / Fallback
双闸 + 人检；无图件管线 → plot_style 直出

## 样例 / Example（合成或去敏）
figkit 5 demo 均固定 seed 合成数据出三格式
