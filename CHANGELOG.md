# Changelog · Euler-Modelforge

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## v1.1.0 — 特性批（2026-09-27）

**定位**：可安装 / 可上手 / 可浏览三件套——`pip install` 直装（含命令入口）、`examples/` 可运行示例、文档站（GitHub Pages）。内容与 v1.0.x 全兼容。

**新增**
- **pip 可安装**：`pyproject.toml` + 命令入口（`euler-env-check` / `euler-smoke-chain` / `euler-precheck-paper` / `euler-verify-manifest` / `euler-smoke-templates`）；安装态数据落包内 `_tree/`，`MODELFORGE_ROOT` 可覆盖根路径
- **examples/**：3 个全合成数据示例（真跑判据；随 CI 冒烟）
- **文档站**：mkdocs-material 六页（首页 / 5 分钟上手 / 示例 / 工作流索引 / 工具索引 / 治理与许可）；`.github/workflows/docs.yml` 自动部署
- **CI**：新增「示例冒烟」步骤

**维护**
- 模板库格式微调（依赖护栏注释与 import 次序；语义中性，与上游工作树对齐）
- 模块表两处表述更新（工具件覆盖 / 断言计数）

**兼容性**：无破坏性变更；退出码契约不变（`0` 通过 · `1` 失败 · `2` 用法 · `3` 依赖缺失未执行）。

## v1.0.1 — 验收整改（2026-09-27）

**定位**：第三方验收（《11-全量扫描》）+ 复核后的整改公开发行——内容与 v1.0.0 全兼容，无新增功能。

**整改**
- 敏感信息收口：抽象已上市参比注册号、理化指纹与代谢谱组合描述，机制描述保留（第三方扫描 §4.1 收编）
- 新增五条语义级防复发判据并同步到防复发闸（结构自检与防复发闸双保险）
- 收窄兼容别名：环境变量收窄为本包前缀，去除另一系统前缀兼容位
- 修订记录与资产表版本一致性订正（首部版本 = 资产表登记版本）
- 修订记录与模块表若干笔误/塌陷订正（靶向性评价字段按 workflows/06 填写等）
- README：相关项目（姊妹项目）互引、相关排期表述排期通用化、README.en 相关表述同步
- schema：交付门禁模板与机器化核对脚本版本名同步中性化

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
