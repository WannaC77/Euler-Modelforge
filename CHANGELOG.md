# Changelog · Euler-Modelforge

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## v1.0.0 — 首次公开发行

**定位**：数模竞赛生成引擎（MCM/ICM 与 CUMCM 双赛事）——赛题到可提交论文的全链工作流。

**包含**
- 模块体系：10 个模块（读题定位 / 假设与符号 / 建模选型 / 求解工坊 / 检验台 / 图件车间 / 论文装配线 / 提交合规闸 / 校准与锚（L2）/ 编排器）+ 底座
- 运行手册：`workflows/00–10` + `_SHARED.md`（共享纪律）+ `W-ABSORB.md`（吸收门）
- 模板库：35 个求解模板（优化 / 预测 / 评价 / 统计与机器学习 / 微分方程 / 图论 / 仿真 / 智能算法；`smoke_all.py` 冒烟覆盖）+ `utils/`（图件与敏感性工具）
- 论文模板：LaTeX（美赛 `mcmthesis` **随包**；国赛 `cumcmthesis` 第三方许可待核 → **不随包**，目录内留获取与启用指引）
- 工具：`tools/env_check.py`（环境自检与降级探测）、`tools/smoke_chain.py`（端到端冒烟 + 已知答案数值断言）
- 门禁脚本：`scripts/precheck_paper.py`（提交前检查）· `scripts/verify_manifest.py`（文档引用 ↔ 磁盘一致性自证；缺件 → rc=1，用法错误 → rc=2）
- 装载件：`BOOT.md` / `AGENTS.md` / `README.md` / `README.en.md` / `QUICKSTART.md`
- 合规件：`LICENSE`（MIT）/ `LICENSE-DOCS`（CC BY 4.0）/ `THIRD-PARTY.md`
- 社区件：`CONTRIBUTING.md` / `CODE_OF_CONDUCT.md` / `SECURITY.md` / `.github/ISSUE_TEMPLATE/`
- 支持与治理：`SUPPORT.md`（支持路径与首应承诺）/ `MAINTAINERS.md` / `.github/CODEOWNERS` / `.github/PULL_REQUEST_TEMPLATE.md` / `.github/ISSUE_TEMPLATE/config.yml` / `.github/dependabot.yml`
- 开发约定：`.editorconfig` / `.gitattributes` / `.pre-commit-config.yaml`（可选装的提交前钩子；清单与免责说明在文件内）
- 样张：`docs/images/`（figkit demo1/demo2 两图 + `smoke_chain --selftest` 输出文本；均由真实运行生成，合成数据固定 seed）
- 中英同步承诺：`CONTRIBUTING.md`「双语同步 SLA」（中文为正本，英文版 ≤ 7 天内同步）

**设计要点**
- 诚实性优先：模块表含**降级列**，缺件一律 `[降级]`/`SKIP` 并留证
- 时间盒纪律：倒计时砍范围不砍深度；赛中禁跑校准
- 可复现：模板冒烟固定 seed，冒烟链含数值断言（非仅字符串检查）
- 零私有依赖：不依赖任何特定 agent / CLI / 调度器 / API key

**已知边界**
- `paper-templates/国赛-CUMCM/` 的第三方模板（`cumcmthesis.cls` / `cumcm2026.sty`，许可待核）**不随本包分发**——
  该目录内只留获取与启用指引（`paper-templates/国赛-CUMCM/README.md`）；美赛模板随包分发
- 缺失 LaTeX / 依赖时论文链降级为 `.tex` 交付（不生成 PDF）

## 版本与 tag 约定

- 版本号遵循 **SemVer**（`vMAJOR.MINOR.PATCH`）；首次公开发行为 `v1.0.0`，tag 与提交同批打（`git tag -a v1.0.0`）。
- **PATCH**：文案/口径纠错、断言补注（不改契约）；**MINOR**：新增模块/模板/判据（向后兼容）；
  **MAJOR**：判据或契约**不兼容**变更（如退出码语义、必需件集合、目录结构）。
- 每个 tag 的说明直接用本文件对应小节的条目；`CHANGELOG.md` 与 tag 一一对应，改名/移动件须在同一小节登记。
