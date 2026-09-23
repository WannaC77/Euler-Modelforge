# 国赛 CUMCM 模板（第三方件 · 未随本包分发）

本目录在**公开发行包中为空**：`cumcmthesis.cls` 与 `cumcm2026.sty`（上游 latexstudio/CUMCMThesis 发行，实查无许可头）**许可待核**，因此**不随本仓库分发**（来源与许可说明见根目录 `THIRD-PARTY.md` §1.3/1.4）。

## 如何启用国赛模板

1. 从上游获取模板（任一途径）：
   - GitHub `latexstudio/CUMCMThesis`（含 `cumcmthesis.cls` + `cumcm2026.sty`）
   - 或竞赛官方模板包 / 你所在学校的 LaTeX 模板镜像
2. 把 `cumcmthesis.cls`、`cumcm2026.sty` 放进本目录；
3. 准备论文主文件（如 `<论文主文件>.tex`），首行 `\documentclass{cumcmthesis}`；
4. 编译（必须 **XeLaTeX**，跑两遍）：
   ```bash
   cd paper-templates/国赛-CUMCM
   xelatex -interaction=nonstopmode <论文主文件>.tex
   xelatex -interaction=nonstopmode <论文主文件>.tex
   ```
   判定：log 里出现 `Output written on`（缺中文字体会报 `SimHei`/`SimSun` undefined 警告，不影响出 PDF）。
5. 一键复验：回上层目录跑 `编译自检.bat`——国赛分支在缺少模板时输出 `[SKIP]`（不算失败），模板就位后照常编译并断言 PDF。

## 说明

- 本包**只含流程与方法论**：模板、字体、竞赛规则原文等第三方内容一律由使用者自备（见 `THIRD-PARTY.md`）。
- 美赛模板（`paper-templates/美赛-MCM-ICM/`）随包分发（LPPL 1.3+，已附修改说明），可直接编译。
- 许可闭合后本目录可重新随包分发（维护者操作：解除对应排除条目并重建）。
