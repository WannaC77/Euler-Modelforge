# THIRD-PARTY.md — 第三方件登记（来源 · 许可 · 修改说明）

> 本文件逐件登记仓库内的第三方素材。**未登记即不得入库**。
> 本项目自身：代码 MIT（`LICENSE`）· 文档 CC BY 4.0（`LICENSE-DOCS`）。

## 1. LaTeX 模板类

### 1.1 `paper-templates/美赛-MCM-ICM/mcmthesis.cls`
- **来源**：https://github.com/latexstudio/LaTeX-Templates （作者 latexstudio / Liam Huang）
- **许可**：LaTeX Project Public License 1.3+（LPPL 1.3+）—— 文件头许可声明保留原样
- **修改**：未修改类文件本体
- **状态**：可分发

### 1.2 `paper-templates/美赛-MCM-ICM/mcmthesis-template.tex`
- **来源**：同 1.1（模板示例件）
- **许可**：随 `mcmthesis.cls`（LPPL 1.3+）
- **修改**：**移除第三方推广段**（公众号引导句与二维码引用、推广站链接），改为中性注释；
  移除处不影响编译（已重编译验证）
- **状态**：可分发（修改说明如上）

### 1.3 `paper-templates/国赛-CUMCM/cumcmthesis.cls`
- **来源**：上游 latexstudio/CUMCMThesis（ctan 无独立包）；实查全文**无许可头**，上游仓库亦未见明确许可声明
- **许可**：**[许可待核]** —— 因此该件**已从本包移出，不随分发**（保留于作者本地；需要者自行从上游获取）
- **修改**：未修改类文件本体
- **状态**：**已移出本包**（原 G5 HOLD 解除；获取与启用指引见 `paper-templates/国赛-CUMCM/README.md`）

### 1.4 `paper-templates/国赛-CUMCM/cumcm2026.sty`
- **来源/许可/状态**：与 1.3 相同（同批发行的样式文件，实查无许可头）→ **[许可待核] · 已移出本包，不随分发**

### 1.5 `paper-templates/国赛-CUMCM/example.tex`（及 `figures/`）
- **来源**：同 1.3 模板示例件（含其插图）
- **许可**：随 `cumcmthesis.cls`（**[许可待核]**）
- **修改**：**移除第三方推广段**（公众号二维码 / QQ 群号 / 推广站链接 minipage 整块）与推广性参考文献条目，改为许可署名；其余示例内容保留
- **状态**：**已随 1.3 移出本包，不随分发**（许可闭合后可重新纳入）

## 2. 方法论文档（MIT）

来源仓库：https://github.com/Lupynow/math-modeling-skills （MIT）

以下文件位于 `references/获奖级方法论/`，均随附 MIT 许可与版权行：

| 文件 | 说明 |
|---|---|
| `abstract-writing.md` | 摘要写作方法论 |
| `de-ai-writing.md` | 去 AI 腔写作要点 |
| `model-selection-matrix.md` | 模型选型矩阵 |
| `problem-decomposition.md` | 问题分解框架 |
| `self-review-framework.md` | 自评审框架 |

**MIT 许可全文（随附）**：

```
MIT License

Copyright (c) 2026 Lupynow

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

> `references/获奖级方法论/_来源与可选资源.md` 为**自撰索引**（本仓库文档许可 CC BY 4.0），
> 仅用于标注来源与可选扩展资源。

## 3. 求解模板库与工具

| 件 | 来源 | 许可 | 说明 |
|---|---|---|---|
| `templates-library/**`（35 个模板 + `utils/`） | 本项目自研 | MIT | 依赖见 `templates-library/requirements.txt`（numpy / scipy / matplotlib / pulp / scikit-learn / statsmodels 等，均为各自开源许可） |
| `templates-library/utils/plot_style.py` · `figcheck.py` | 本项目自研（**思路级参考**公开可视化实践，未复制第三方代码） | MIT | 如需替换为你自己的样式体系，直接改本文件 |
| `tools/` · `scripts/` | 本项目自研 | MIT | stdlib + 上述依赖 |

## 4. 未入库（明确排除）

| 内容 | 原因 |
|---|---|
| 往届获奖论文库、官方规则原文（PDF / 截图） | 第三方版权 / 官方材料，不再分发 |
| 他人公众号二维码、推广图 | 他人推广物 |
| 官方申报书模板原件 | 官方材料 |
| 竞赛参赛数据与队伍材料 | 隐私与合规 |

## 5. 许可边界声明

- 本仓库**不包含**任何竞赛官方材料、他人论文或真实参赛数据；
- 引用到的公开竞赛题名、赛事名称仅作方法论举例，权利归各自权利人；
- 使用本仓库产出论文时，请自行核对目标赛事对 AI 使用、模板与署名的要求
  （见 `workflows/10-AI使用声明.md`）。
