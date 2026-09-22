# Changelog · Euler-Modelforge

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## v1.0.0 — 首次公开发行

**定位**：数模竞赛生成引擎（MCM/ICM 与 CUMCM 双轨）——赛题到可提交论文的全链工作流。

**包含**
- 模块体系：10 个模块（读题定位 / 假设与符号 / 建模选型 / 求解工坊 / 检验台 / 图件车间 / 论文装配线 / 提交合规闸 / 校准与锚（L2）/ 编排器）+ 底座
- 运行手册：`workflows/00–10` + `_SHARED.md`（共享纪律）+ `W-ABSORB.md`（吸收门）
- 模板库：35 个已验证求解模板（优化 / 预测 / 评价 / 统计与机器学习 / 微分方程 / 图论 / 仿真 / 智能算法）+ `utils/`（图件与敏感性工具）
- 论文模板：双轨 LaTeX（美赛 `mcmthesis` / 国赛 `cumcmthesis`）
- 工具：`tools/env_check.py`（环境自检与降级探测）、`tools/smoke_chain.py`（端到端冒烟 + 已知答案数值断言）
- 门禁脚本：`scripts/precheck_paper.py`（提交前检查）
- 装载件：`BOOT.md` / `AGENTS.md` / `README.md` / `README.en.md` / `QUICKSTART.md`
- 合规件：`LICENSE`（MIT）/ `LICENSE-DOCS`（CC BY 4.0）/ `THIRD-PARTY.md`

**设计要点**
- 诚实性优先：模块表含**降级列**，缺件一律 `[降级]`/`SKIP` 并留证
- 时间盒纪律：倒计时砍范围不砍深度；赛中禁跑校准
- 可复现：模板冒烟固定 seed，冒烟链含数值断言（非仅字符串检查）
- 零私有依赖：不依赖任何特定 agent / CLI / 调度器 / API key

**已知边界**
- `paper-templates/国赛-CUMCM/` 的 `cumcmthesis.cls` 与 `cumcm2026.sty` 许可待核（`THIRD-PARTY.md` 标注）——
  该目录在许可闭合前**不随公开发行分发**
- 缺失 LaTeX / 依赖时论文链降级为 `.tex` 交付（不生成 PDF）
