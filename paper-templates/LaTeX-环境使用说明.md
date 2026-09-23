# LaTeX 环境使用说明（数模竞赛）

> 本页只给**可移植**的环境要求、探测与编译步骤（不绑定任何一台机器）；编译是否通过以 §二 的日志判定为准。

## 一、环境要求与探测

| 组件 | 要求 | 探测 / 说明 |
|------|------|------------|
| **TeX Live**（推荐主引擎） | 全量或含 xelatex + ctex 的安装 | `xelatex -v`；国赛模板必须 XeLaTeX |
| **MiKTeX**（可作备用） | 用户级安装即可 | `mpm --version`；与 TeX Live 并存时注意 PATH 顺序 |
| 宏包源 | 建议指向国内 CTAN 镜像 | 见 §三（`tlmgr option repository` / `mpm --set-repository`） |
| Graphviz | 可选（画示意图用） | `dot -v` |
| 中文字体 | 国赛模板需要（如 SimHei / SimSun） | 缺字体会报 `SimHei(0)/b/n undefined`（不影响出 PDF） |

**一句话**：本页只给可移植的安装 / 探测 / 编译步骤；环境是否可用，以 §二 的编译判定（日志出现 `Output written on <file>.pdf`）为准。

## 二、编译（实测命令与产出）

```bash
# 国赛（中文，必须 XeLaTeX）—— 模板需自备（见 paper-templates/国赛-CUMCM/README.md）；编译成功即得到 PDF
cd "paper-templates/国赛-CUMCM"
xelatex -interaction=nonstopmode <论文主文件>.tex
xelatex -interaction=nonstopmode <论文主文件>.tex

# 美赛（英文，pdflatex；xelatex 亦可）—— 编译成功即得到 mcmthesis-template.pdf
cd "paper-templates/美赛-MCM-ICM"
pdflatex -interaction=nonstopmode mcmthesis-template.tex
pdflatex -interaction=nonstopmode mcmthesis-template.tex
```

判定通过的唯一标准：log 里出现 `Output written on <file>.pdf`，且**没有** `Fatal error occurred`。只看进程退出码会被交互式警告骗过去。

**赛前冒烟测试**：双击 `paper-templates/编译自检.bat`（自动选引擎、双模板各两遍、断言 PDF 与日志、打印用了哪个引擎、退出码 0/1）。赛前一周必跑。

## 三、包管理（缺宏包时）

```bash
# TeX Live（装好后）
tlmgr install <包名>            # 默认源已是清华镜像
tlmgr option repository         # 查看当前源

# MiKTeX
mpm --install=<包名>            # 缺包也会在编译时自动从镜像拉
mpm --set-repository=https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/win32/miktex/tm/packages/
initexmf --set-config-value="[MPM]AutoInstall=1"
```

注意：MiKTeX 的**用户级安装**命令要在普通权限下跑（不要 `--admin`，否则作用到另一个作用域，编译时看不到）。

## 四、美赛模板为什么「从未编译过」（根因不是环境）

1. `mcmthesis.cls` 是**报废的 DocStrip 抽取物**：文件里混着 `.dtx` 的说明文字（`\end{macrocode}`、`\subsection{Options}`、英文散文），`\begin{macrocode}` 标记被剥掉 → 任何引擎都编不过（报 `Missing \begin{document}` 之后 100 个错）。
   → 已用 CTAN 官方 cls（LPPL 1.3+）覆盖；坏件不随仓库分发。
2. `mcmthesis-template.tex` 第 1 行丢了注释符（`!TEX program = pdflatex|xelatex`）→ 首行被当正文，直接 `Missing \begin{document}`。已补 `%`。
3. 模板引用的 `code/mcmthesis-matlab1.m`、`code/mcmthesis-sudoku.cpp` 没随模板落地 → 已从 CTAN 官方包补齐。

## 五、常见问题

| 现象 | 处理 |
|------|------|
| 编译报 `File 'xxx.sty' not found` | `tlmgr install xxx`（或 MiKTeX 自动装包；确认网络/镜像可用） |
| 中文乱码/豆腐块 | 国赛必须 XeLaTeX + ctex；不要用 pdfLaTeX 编中文 |
| `SimHei(0)/b/n undefined` 警告 | 正常（ctex 假粗体），不影响出 PDF |
| 想确认 PDF 真没坏 | 渲染成图再看：`pymupdf` 打开 → `get_pixmap` 存 PNG（别用 pdftoppm，缺 Adobe-GB1 会把中文渲成空框） |
| 编译器被 PATH 抢了 | `where xelatex` 看实际命中哪个；TeX Live 应排在 MiKTeX 之前 |

## 六、Overleaf（可选，不是主方案）

本地已实测可编译 → 比赛日不必依赖网络。若现场机器坏了才考虑：把 `paper-templates/美赛-MCM-ICM/`（或国赛目录）打包 zip 上传，国赛选 XeLaTeX 编译器。
