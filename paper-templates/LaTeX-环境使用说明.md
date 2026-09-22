# LaTeX 环境使用说明（数模竞赛）

> 2026-09-15 重写并实测 | 上一版（9-04）写着「TeX Live 安装中 / MiKTeX 包管理被墙」，两条都已过时且是错的根因判断。

## 一、本机环境事实（2026-09-15 实测）

| 组件 | 路径 / 版本 | 状态 |
|------|------------|------|
| **TeX Live 2026**（主） | `<TeX 安装目录>/`（scheme-full，清华镜像装） | 🔄 重装中：9-04 是断点安装（仅 411MB、无 xelatex/tlmgr），已留档 `<TeX 安装目录>/` 并重装 |
| **MiKTeX**（备） | `<TeX 安装目录>`（或用环境变量 `MODELFORGE_TEX` 直接指定 xelatex 路径） | 探测到即可用：xelatex/pdflatex 双模板出 PDF |
| MiKTeX 包源 | 国内 CTAN 镜像（TUNA/BFSU…），`AutoInstall=1` | ✅ 「包管理不可用」已修复（被墙的只是默认源 api.miktex.org） |
| Graphviz | dot 16.0.0 | ✅ |
| TeXworks | MiKTeX 自带 | ✅ |

**一句话**：9-04 的破局点不是「TeX Live 没装完」，而是 ①TeX Live 断点未续 ②MiKTeX 没换源 ③**美赛模板本身是坏件**（见第四节）。现在前三项已解决，双模板实测可编译。

## 二、编译（实测命令与产出）

```bash
# 国赛（中文，必须 XeLaTeX）—— 编译成功即得到 example.pdf
cd "paper-templates/国赛-CUMCM"
xelatex -interaction=nonstopmode example.tex
xelatex -interaction=nonstopmode example.tex

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
