# LaTeX 模板使用说明（数模竞赛）

> 本页给模板的编译方法与一键复验；编译判定标准：日志出现 `Output written on <file>.pdf` 且无 `Fatal error occurred`。

## 环境要求

| 组件 | 要求 |
|------|------|
| LaTeX 引擎 | 任一可用安装：TeX Live（含 xelatex + ctex）或 MiKTeX（用户级即可） |
| 中文字体 | 国赛模板需要（如 SimHei / SimSun） |
| 宏包 | 缺包按报错装（TeX Live `tlmgr install` / MiKTeX `mpm --install`，见 `LaTeX-环境使用说明.md` §三） |

引擎选择：`编译自检.bat` 自动探测 xelatex / pdflatex 并打印实际使用的引擎；多个安装并存时注意 PATH 顺序（先命中的先用）。

## 编译命令

```bash
# 国赛 CUMCM（中文，必须 XeLaTeX；模板需自备 —— 见 国赛-CUMCM/README.md）
cd paper-templates/国赛-CUMCM
xelatex -interaction=nonstopmode <论文主文件>.tex          # 跑 2 遍生成目录/交叉引用

# 美赛 MCM/ICM（英文，pdfLaTeX 或 XeLaTeX 均可）
cd paper-templates/美赛-MCM-ICM
pdflatex -interaction=nonstopmode mcmthesis-template.tex
```

一键复验（对已就位的模板各两遍编译 + 断言 PDF 与日志；缺件分支打印 `[SKIP]`，退出码 0=通过）：

```bash
paper-templates/编译自检.bat        # 双击也行；赛前一周必跑一次
```

## 美赛 MCM/ICM（`美赛-MCM-ICM/`）

- 模板：`mcmthesis.cls` v6.3.3（2024-01-22，CTAN 官方包，已用官方件覆盖 9-04 的坏件）
- 示例骨架：`mcmthesis-template.tex`（实测 pdfLaTeX 出 **11 页** PDF）
- 开赛前要改的三处（在 `\mcmsetup{...}`）：`tcn = 0000` → 控制号、`problem = A` → 题号、`\title{...}` → 标题
- 摘要写在 `\begin{abstract}` 内，自动生成 Summary Sheet 页
- 代码清单用 `code/` 目录（`\lstinputlisting`），图片用 `figures/`（已在 `\graphicspath` 里）

## 国赛 CUMCM（`国赛-CUMCM/`）

- 模板：`cumcmthesis.cls` + `cumcm2026.sty`（第三方件，许可待核 → **不随本包分发**；按本目录 `README.md` 从上游获取后放入即可）
- 预期适用（**未在本包实测**：该模板不随包；自备后请自行跑一遍编译自检，页数以你的实测为准）
- **必须 XeLaTeX**（模板强制，pdfLaTeX 会报错）
- ⚠️ 国赛官方以 Word 提交为主流，LaTeX 导出 PDF 前先核对当年提交系统是否接受 PDF
- ⚠️ AI 使用声明位置见 `workflows/10-AI使用声明.md`（以当年官方规定为准）

## 已知无害警告（不用管）

- `Font shape 'TU/SimHei(0)/b/n' undefined` → ctex 用假粗体渲染汉字，正常
- `Label 'LastPage' multiply defined` / `float specifier changed to ht` → 模板自带用法，正常
- 只要 log 里有 `Output written on *.pdf`、且没有 `Fatal error`，就算通过

## 缺宏包怎么办

- TeX Live 装好后：`tlmgr install <包名>`（默认已指向清华镜像）
- 用 MiKTeX 时：`mpm --install=<包名>`，且已开自动装包（编译时缺包自动从镜像拉）
- 换镜像：`mpm --set-repository=https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/win32/miktex/tm/packages/`

## Overleaf（可选备份，不再是主方案）

比赛场地网络不稳时它反而是风险；若要用，把本目录打包 zip 上传（国赛模板自备后选 XeLaTeX 编译器即可）。**美赛模板本包实测可编译；国赛模板不随包，自备后须自行实测**，日常以本地为准。

## 与代码库联动

- `templates-library/utils/latex_table.py` 的 `to_latex()` 可把 DataFrame 直接转成三线表 LaTeX 代码，粘贴进论文即可
- 图片统一放 `figures/`，用 `templates-library/utils/plot_style.py` 输出保证风格统一
