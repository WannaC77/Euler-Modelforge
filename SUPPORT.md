# 支持 / Support · Euler-Modelforge

## 这是什么

Euler-Modelforge 是一套「手册 + 工具链」形态的数学建模竞赛工作流（详见 [README.md](README.md)）。**这里只回答"用的过程中出了什么问题"**——方法论问题请直接读 `workflows/` 与 `references/` 对应正本，不在支持范围。

## 遇到问题怎么办

1. **先自己跑一遍自检**（能解决大半问题）：

   ```bash
   python tools/env_check.py --selftest          # 环境档位 T0/T1/T2 + 缺件清单
   python tools/smoke_chain.py --selftest        # 全链冒烟（含黄金数值断言）
   python templates-library/smoke_all.py --quick # 模板库冒烟
   ```

   全 PASS / SKIP 即环境正常；FAIL 的那一行就是问题所在。退出码语义：`0` 通过 · `1` 失败 · `2` 用法错误 · `3` 依赖缺失未执行。

2. **搜现有 issue**：你的问题大概率已有人问过——先搜 [Issues](../../issues)，避免重复开帖。

3. **没有现成答案 → 开 issue**：
   - 缺陷/报错：用 [bug_report 模板](../../.github/ISSUE_TEMPLATE/bug_report.md)，**必须带**：复现命令 + 实际输出 + 期望输出。
   - 用法/功能建议：用 [feature_request 模板](../../.github/ISSUE_TEMPLATE/feature_request.md)。
   - **赛前触发问题**：如果在备赛/比赛现场遇到，开 issue 前请先跑上面第 1 步的自检并把输出贴全——缺件导致的 90% 问题（`rc=3` / `[降级]`）自检会直接告诉你装什么，不用等回复。

## 回应时间承诺

| 事项 | 承诺 |
|---|---|
| 首次回应（标签分诊） | ≤ 7 天 |
| 缺陷 triage 结论（确认 / 复现 / 转文档） | ≤ 14 天 |
| 紧急且影响安装自检的缺陷 | 尽力优先，但没有任何"响应时间保证"——本仓库由维护者业余时间维护 |

超过承诺时限无人回应？在原 issue 下礼貌地跟帖催一次即可。

## 安全问题（不要开公开 issue）

漏洞、数据泄露风险、依赖投毒嫌疑 → 走 [SECURITY.md](SECURITY.md) 的私下报告渠道，**不要**在公开 issue 里贴细节。

## 明确不支持的

- 具体赛题的代做/解题（这是能力问题不是缺陷，赛期也没人值守）；
- 与本仓库无关的 Python / LaTeX 环境配置（去对应项目社区）；
- 私有校准与锚数据的接入（`E-M9` 只声明边界，不在开源支持范围）。
