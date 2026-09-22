# Euler-Modelforge · BOOT（冷启动件 · ≤2 KB）

> **一句话**：数模竞赛生成引擎——从赛题到可提交论文的全链工作流（MCM/ICM 与 CUMCM 双轨），含 35 个已验证求解模板与双 LaTeX 论文模板。
> **本产品不依赖**任何特定 agent、CLI、调度器或 API key：任何能读文件 + 跑 Python 3.11+ 的人或 agent 都可用。

## 五条铁律（摘要）

1. **时间盒优先**：倒计时砍范围、不砍深度；赛中禁跑校准（L2）。
2. **诚实降级**：缺件（LaTeX / venv / 依赖）标 `[降级]` 并留证，**禁止**假装成功。
3. **三态标注**：结论标 事实 / 推断 / 假设，不混用。
4. **Claim-Evidence**：论文每处主张可回溯到证据件（图 / 表 / 代码 / 日志）。
5. **学术诚信**：AI 只做辅助，核心建模与结论由队伍独立完成（见 `workflows/10-AI使用声明.md`）。

## 三步装载

1. 读本文件 → 读 `Euler-CORE.md` → 读 `Euler-ENGINE.md`
2. 按任务选 runbook，加载对应 `workflows/NN-*.md` + `workflows/_SHARED.md`
3. 需要计算 / 门禁时调用 `tools/` 或 `scripts/`；缺件按模块表「降级」列执行并标 `[降级]`

## 指针

| 用途 | 文件 |
|---|---|
| 5 分钟上手 | `QUICKSTART.md` |
| 完整说明 | `README.md`（英文 `README.en.md`） |
| code agent 装载 | `AGENTS.md` |
| 模块表 / 门禁 | `Euler-ENGINE.md` · `Euler-CORE.md` |
| 求解模板库（35 个） | `templates-library/` |
| 论文模板（双轨） | `paper-templates/` |
| 私有校准（L2 · 可选自建） | `kb/` · `<共享层>/` · `<校准台账>` · `<锚注册卡>/` |
