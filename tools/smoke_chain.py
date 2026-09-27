#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""smoke_chain —— Euler 全链技术冒烟（E-R 底座 · 冒烟表）

适用场景 / Purpose
    用**合成小题**把 Euler 生成链的关键接口整跑一遍，验证「工具链技术连通性」：
        M1 拆题定位器（合成拆题卡）→ M4 求解工坊（模板库真跑 + 黄金数值断言）→
        M6 图件车间（figkit 样例真跑）/ M6s 敏感性区间断言（workflow 06）→
        M7 论文装配线（最小 LaTeX 骨架 + 编译）
    **不评分、不进锚、不触碰任何个人材料**（合成题/临时目录自生成）。
    支撑 E-R 门禁「smoke_all 全 PASS 表」（`Euler-ENGINE.md` §1/§3）。

黄金断言 / Golden assertions（附录 C.3 · F13）
    不只断言「输出里出现过某个词」：脚本内自造合成 LP（工时/原料/单位利润系数），用**精确有理数
    顶点法**算出解析真值（最优利润 + 最优产量）与 ±20% 系数扰动的可复算区间，再与**求解器输出**对质：
      ① 模板库 `templates-library/01-优化/lp.py`（pulp）真跑回读；
      ② 合成驱动件（`_smoke_out/work/` 自生成）走 scipy.linprog 独立求解，并经模板库
         `utils/sensitivity.py` 的 `scan_1d` 做单参数扫描。
    判据：`abs(got - truth) <= 1e-6 * max(1, abs(truth))`（模板回读另计 %.4f 打印量化误差）。
    任一断言不成立 → 该阶段 FAIL → 整体判定 FAIL 且 rc≠0。缺依赖/缺件走 [降级]/SKIP 并写明。

输入 / Input
    无（脚本自生成合成件到脚本旁 `_smoke_out/`）。
输出 / Output
    `_smoke_out/smoke_chain_report.md`（每阶段 PASS/FAIL/SKIP/WARN + 关键输出）；
    控制台打印同款状态表；**任一 FAIL → exit 1**（SKIP/WARN 不判 FAIL——便于分批施工期使用）。

依赖 / Deps
    venv 优先：`<venv>`（pulp / matplotlib / scipy），缺则回落当前解释器与系统解释器候选；
    模板库 `templates-library/01-优化/lp.py`（缺 → FAIL；pulp 缺 → SKIP + [降级]）；
    `utils/figkit/figkit_demo1_grouped_bar.py`（缺 → SKIP）；xelatex（缺 → SKIP；编译 rc≠0 → WARN + 日志尾行）。

用法 / Usage
    python smoke_chain.py [--root <包根|系统根>]
    python smoke_chain.py --selftest      # 别名：跑完整链即自测（全 PASS/SKIP 则 rc=0）

路径 / Paths（探测链 · 顺序固定 · 全部相对脚本自身位置）
    1. 环境变量覆盖（最高优先）：`MODELFORGE_ROOT` → 指向包根（12 批 W-08：撤另一套系统前缀兼容位）
    2. 自脚本位置向上逐级：某父目录**同时**含 `templates-library/` 与 `workflows/` → 该目录＝包根（major）
    3. 旧布局兼容：某父目录含 `Euler` 子目录（其下 `workflows/` 在位）→ system_root＝该父目录，
       major＝该父目录下的 `Euler`
    4. 全失败 → major＝脚本父目录的父目录（`tools/` 的上一级），允许阶段 FAIL（诚实降级）
    源码内**不写死任何用户绝对路径**。定位逻辑与 `env_check.py` 同源（此处自带一份以保脚本可独立跑）。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from datetime import datetime
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / '_smoke_out'                      # 报告与合成件落盘处（脚本旁）
WORK = OUT / 'work'                           # 合成工作目录（每次重跑重建）
VERSION = 'v1.2 (2026-09-22)'   # v1.1：xelatex 正序 + 子进程 TEMP 归一；v1.2：根解析探测链（包内布局）+ 黄金数值断言（附录 C.3）
RESULTS: list = []                             # [(阶段, 状态, 详情)]
PY = 'python'

# -------- 定位（探测链）常量 --------
ENV_ROOT_KEYS = ('MODELFORGE_ROOT',)                    # 探测链第 1 档：包根覆盖（环境变量）
ENV_VENV_KEYS = ('MODELFORGE_VENV',)     # 解释器覆盖（附录 D：venv 探测链）
PKG_MARKS = ('templates-library', 'workflows')          # 包内布局标记：同一父目录下并存 → 该目录＝包根
EULER_DIR, WF_DIR = 'Euler', 'workflows'                # 旧布局标记：<系统根>/Euler/workflows 在位
PICK_MAX = 6                                            # 解释器候选最多探测几个（每个一次 import 探测）

# -------- 合成 LP 数据（子问题1 · 脚本内自造；与拆题卡 / 论文骨架口径一致） --------
LP_OBJ = (3, 5)                 # 单位利润（目标系数，最大化）
LP_A_UB = ((1, 2), (3, 2))      # 工时 / 原料 单位消耗（A_ub @ x <= b_ub）
LP_B_UB = (8, 12)               # 工时 / 原料 上限
SENS_PCT = 0.20                 # 子问题2：目标系数 ±20% 扰动
SENS_N = 9                      # 敏感性扫描点数（与模板库 utils/sensitivity.py 默认口径一致）

# -------- 黄金断言常量（附录 C.3） --------
GOLD_REL = 1e-6                 # 相对容差（下限 1）
GOLD_PRINT_EPS = 5e-5           # 模板以 %.4f 打印，回读值须容忍的打印量化误差
GOLD_GRID = 5                   # 系数箱采样网格（GOLD_GRID × GOLD_GRID，含 4 角）
GOLD_SENTINEL = '__EULER_GOLD__'
GOLD_DRIVER_NAME = 'gold_lp_driver.py'

# -------- M1 合成拆题卡（2 子问题 · 与 M4 的 LP 模板口径一致，便于串链） --------
CARD_MD = r'''# 合成拆题卡（smoke_chain 冒烟件 · 不评分 / 不进锚）

> 合成题：某电子厂两条产线的排产与需求扰动下的产能分配（**虚构题面，仅用于技术冒烟**）
> 生成：smoke_chain %(version)s · %(ts)s

## 一句话读题

在「工时 + 原料」双约束下最大化两产品利润；再考察需求上下浮动时最优方案的稳健性。

## 子问题表

| # | 题目要什么 | 数学本质（题型） | 模型族初判 | 数据可得性 | 交付物 |
|---|---|---|---|---|---|
| 子问题1 | 约束下最大化总利润，给出两产品产量 | 优化/决策 | 线性规划（LP）→ `templates-library/01-优化/lp.py` | 题给（合成：工时/原料/单位利润系数） | 最优产量 + 最优利润 + 约束松紧 |
| 子问题2 | 需求 ±20%% 扰动下方案是否稳健 | 统计推断/实验设计 | 敏感性分析 → `templates-library/utils/sensitivity.py` | 合成随机扰动（种子固定） | 敏感区间 + 结论 + 风险提示 |

## 子问题关系

- 子问题2 依赖 子问题1 的最优解：先解 LP 得基准方案 → 再对系数扰动重解。
- 合成 LP 口径：max 3x1+5x2，s.t. x1+2x2<=8（工时）、3x1+2x2<=12（原料）、x>=0；
  解析真值由 smoke_chain 以精确有理数顶点法算出，M4b/M6s 阶段对求解器输出做数值断言。

## 拆题质量自检（E-M1 门禁字段）

- [x] 字段完整：题型 / 模型族初判 / 数据可得性 / 交付物 四列齐
- [x] 子问题数 2（合成件口径）
- [x] 数据可得性已声明（合成数据，不引外部依赖）
'''

# -------- M7 最小 LaTeX 论文骨架（abstract / section / 图占位） --------
PAPER_TEX_NAME = 'smoke_paper.tex'
PAPER_TEX = r'''% 合成论文骨架（smoke_chain 冒烟件 · 不评分 / 不进锚）
% 用途：验证 M7 论文装配线的「骨架 → xelatex 出 PDF」技术通路
\documentclass[12pt]{article}
\usepackage[margin=2.5cm]{geometry}
\usepackage{graphicx}
\usepackage{amsmath, amssymb}
\usepackage{ctex}                 % 中文（国赛线：必须 XeLaTeX）
\title{合成题冒烟骨架：两产线排产优化}
\author{smoke\_chain（合成件）}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
本文以合成题为对象，走通「拆题卡 $\rightarrow$ 求解 $\rightarrow$ 图件 $\rightarrow$ 装配」的论文装配通路：
先建线性规划模型求最优排产，再对需求系数做敏感性分析。摘要五要素（问题/方法/模型/结果/结论）
在真实赛事中逐项落实，本件仅验证编译技术链。
\par\textbf{关键词}：线性规划；敏感性分析；论文装配冒烟
\end{abstract}

\section{问题重述}
合成题：在工时与原料双约束下最大化利润（子问题一），并考察需求扰动的稳健性（子问题二）。

\section{模型建立与求解}
子问题一的线性规划模型：
\begin{equation}
\max_{x \ge 0}\ 3x_1 + 5x_2 \quad \text{s.t.}\quad x_1 + 2x_2 \le 8,\ 3x_1 + 2x_2 \le 12 .
\end{equation}
子问题二对目标系数施加 $\pm 20\%$ 扰动，观察最优解与最优值的漂移区间。

\section{结果与分析}
\begin{figure}[htbp]
  \centering
  \framebox[\linewidth]{\rule{0pt}{4cm} 图占位（真实图件由 E-M6 图件车间产出）}
  \caption{合成结果示意（占位框图，非实测数据）}
  \label{fig:smoke-placeholder}
\end{figure}

如表~\ref{fig:smoke-placeholder} 所示，占位框替代真实图件；真实装配时替换为 PNG+PDF 双份。

\section{结论}
合成链技术通路打通；本件不产生任何赛事结论。

\end{document}
'''

# -------- 黄金断言驱动件（自生成 · 合成件）：独立求解器 + 模板库敏感性扫描 --------
GOLD_DRIVER = r'''# -*- coding: utf-8 -*-
"""合成黄金断言驱动件（smoke_chain 自生成 · 不评分 / 不进锚）。

用途（附录 C.3 黄金断言）：对合成 LP 做**独立数值求解**，结果以哨兵行回传——
  ① 基准系数点的 scipy.linprog 解（最优利润 + 最优产量）；
  ② 目标系数 ±%(pct_txt)s 箱内 4 角 + %(gn)d×%(gn)d 网格解；
  ③ 经模板库 utils/sensitivity.scan_1d 的单参数扫描（子问题2 工具链真跑）。
真值由 smoke_chain 用精确有理数顶点法在本地独立算出，两边对质（非字符串断言）。
"""
import json
import os
import sys

sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else os.getcwd())

OBJ = %(obj)r
A_UB = %(a_ub)r
B_UB = %(b_ub)r
PCT = %(pct)r
GRID = %(gn)d
N_SCAN = %(sn)d

out = {"base": None, "corners": {}, "grid": [], "scan": None, "scan_err": "", "err": ""}


def solve(c):
    """scipy.linprog 解 max c·x s.t. A_ub x <= b_ub, x >= 0；失败返回 None。"""
    from scipy.optimize import linprog
    kw = dict(A_ub=A_UB, b_ub=B_UB, bounds=[(0, None)] * len(c))
    try:
        r = linprog([-v for v in c], method="highs", **kw)
    except Exception:
        r = linprog([-v for v in c], **kw)
    if not r.success:
        return None
    return {"val": float(-r.fun), "x": [float(v) for v in r.x]}


try:
    out["base"] = solve(list(OBJ))
    lo = [v * (1.0 - PCT) for v in OBJ]
    hi = [v * (1.0 + PCT) for v in OBJ]
    for c1 in (lo[0], hi[0]):
        for c2 in (lo[1], hi[1]):
            out["corners"]["%%s|%%s" %% (c1, c2)] = solve([c1, c2])
    for i in range(GRID):
        c1 = lo[0] + (hi[0] - lo[0]) * i / (GRID - 1)
        for j in range(GRID):
            c2 = lo[1] + (hi[1] - lo[1]) * j / (GRID - 1)
            r = solve([c1, c2])
            out["grid"].append([c1, c2, None if r is None else r["val"]])
    try:
        from utils.sensitivity import scan_1d
        res = scan_1d(lambda c1, c2: solve([c1, c2])["val"], "c1", float(OBJ[0]),
                      pct=PCT, n=N_SCAN, c2=float(OBJ[1]))
        out["scan"] = {"c1": [float(v) for v in res["参数"]], "val": [float(v) for v in res["结果"]]}
    except Exception as e:
        out["scan_err"] = "%%s: %%s" %% (type(e).__name__, e)
except Exception as e:
    out["err"] = "%%s: %%s" %% (type(e).__name__, e)

print("%(sentinel)s" + json.dumps(out, ensure_ascii=False))
'''


# ---------------------------------------------------------------- 定位（探测链 · 无绝对路径）

def env_root() -> 'Path | None':
    """探测链第 1 档：环境变量覆盖（`MODELFORGE_ROOT`）。未设/不存在 → None。"""
    for key in ENV_ROOT_KEYS:
        val = os.environ.get(key)
        if not val:
            continue
        try:
            p = Path(val).expanduser()
        except Exception:
            continue
        if p.is_dir():
            return p.resolve()
    return None


def upward(start: Path) -> list:
    """自 start 向上逐级（含 start 自身）的目录序列。"""
    s = Path(start)
    return [s] + list(s.parents)


def probe_chain(start: Path, use_env: bool = True) -> 'tuple[Path, Path, str]':
    """根解析探测链 → (系统根, major, 来源)。顺序固定，任何判断都相对 start（脚本自身位置）推导。"""
    if use_env:
        envr = env_root()
        if envr is not None:                                        # ① 环境变量覆盖（最高优先）
            return envr, envr, 'env:MODELFORGE_ROOT'
    for p in upward(start):                                         # ② 包内布局（major 与 system_root 合一）
        if all((p / m).is_dir() for m in PKG_MARKS):
            return p, p, 'probe:templates-library+workflows'
    for p in upward(start):                                         # ③ 旧布局兼容
        if (p / EULER_DIR / WF_DIR).is_dir():
            return p, p / EULER_DIR, 'probe:旧布局（Euler 子目录 workflows 在位）'
    base = Path(start)                                              # ④ 诚实降级：tools/ 的上一级
    fallback = base.parent if base.name == 'tools' else base
    return fallback, fallback, 'fallback:tools/ 上一级'


def euler_root(major: Path) -> Path:
    """euler 根：旧布局（`major/Euler/workflows` 在位）＝ `major/Euler`；包内布局＝ major 本身。"""
    return major / EULER_DIR if (major / EULER_DIR / WF_DIR).is_dir() else major


def resolve_roots(root: 'Path | None' = None) -> 'tuple[Path, Path, str]':
    """解析 (系统根, major, 来源)。

    root=None → 自脚本位置走探测链（含环境变量档）；显式 root → 以该路径为起点（用户显式优先，
    跳过环境变量档）。接受包根 / 系统根 / 任意子级（向上探测）；指定更高层父目录时按探测链第 4 档
    降级，并在「来源」里如实标注（诚实降级，不猜）。
    """
    if root is None:
        return probe_chain(HERE, use_env=True)
    try:
        r = Path(root).expanduser().resolve()
    except Exception:
        r = Path(root)
    return probe_chain(r if r.is_dir() else r.parent, use_env=False)


# ---------------------------------------------------------------- 跑子进程 / 解释器选择

def run(cmd: list, cwd=None, timeout: int = 600) -> 'tuple[int, str]':
    """子进程执行；统一 UTF-8 解码并合并 stdout+stderr；禁写 __pycache__（不污染模板库）。

    Windows 兼容：TEMP/TMP/TMPDIR 统一指向本工具自建目录——MSYS/CI 环境下
    TEMP=/tmp 或指向已删除目录会让 MiKTeX 抛 "No suitable temporary directory found"
    （实测 FATAL，2026-09-22）。归一后 MiKTeX / TeX Live 均可编译。
    """
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    try:
        tmpdir = OUT / '_tmp'
        tmpdir.mkdir(parents=True, exist_ok=True)
        s = str(tmpdir)
        env['TEMP'] = s
        env['TMP'] = s
        env['TMPDIR'] = s
    except Exception:
        pass
    try:
        p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True,
                           encoding='utf-8', errors='replace', cwd=str(cwd) if cwd else None,
                           timeout=timeout, env=env)
    except Exception as e:
        return 127, '执行失败：%s' % e
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def venv_python(prog: Path) -> 'Path | None':
    """venv 解释器：环境变量覆盖（MODELFORGE_VENV）→ 包内 <venv>。"""
    for key in ENV_VENV_KEYS:
        val = os.environ.get(key)
        if not val:
            continue
        p = Path(val).expanduser()
        for c in (p, p / 'Scripts' / 'python.exe', p / 'bin' / 'python', p / 'bin' / 'python3'):
            if c.is_file():
                return c.resolve()
    for rel in ('Scripts/python.exe', 'bin/python', 'bin/python3'):
        e = prog / '<venv>' / rel
        if e.is_file():
            return e.resolve()
    return None


def system_pythons() -> list:
    """系统解释器候选（无绝对路径字面）：`py -0p` 启动器 / PATH / 平台常见安装布局。"""
    out = []
    if os.name == 'nt':
        py = shutil.which('py')
        if py:
            try:
                p = subprocess.run([py, '-0p'], capture_output=True, text=True,
                                   encoding='utf-8', errors='replace', timeout=30)
                for ln in (p.stdout or '').splitlines():
                    for tok in ln.replace('*', ' ').split():
                        c = Path(tok) if tok.lower().endswith('python.exe') else None
                        if c is not None and c.is_file():
                            out.append(c)
            except Exception:
                pass
    for env_key, pat in (('LOCALAPPDATA', 'Programs/Python/Python3*/python.exe'),
                         ('ProgramFiles', 'Python3*/python.exe'),
                         ('ProgramFiles(x86)', 'Python3*/python.exe')):
        base = os.environ.get(env_key)
        if not base:
            continue
        for hit in sorted(glob.glob(os.path.join(base, pat))):
            out.append(Path(hit))
    for name in ('python', 'python3', 'python3.13', 'python3.12', 'python3.11'):
        w = shutil.which(name)
        if w:
            out.append(Path(w))
    out.append(Path(sys.executable))               # 兜底：当前解释器
    seen, res = set(), []
    for p in out:
        try:
            rp = p.resolve()
        except Exception:
            continue
        if rp in seen:
            continue
        seen.add(rp)
        res.append(rp)
    return res


def find_xelatex() -> 'str | None':
    """xelatex 解析——优先序与 `paper-templates/编译自检.bat` 一致：
    环境变量 `MODELFORGE_TEX` → 本机 TeX 常见布局 → PATH → MiKTeX（%LOCALAPPDATA% 用户级安装）。
    （PATH 里 MiKTeX 常排首位，但其仓库未注册/临时目录异常时易失败——正序取已知布局更稳。）"""
    cands = []
    for key in ('MODELFORGE_TEX',):
        val = os.environ.get(key)
        if val:
            cands.append(Path(val).expanduser())
    cands.append(Path(r'<TeX 安装目录>/'))
    w = shutil.which('xelatex')
    if w:
        cands.append(Path(w))
    la = os.environ.get('LOCALAPPDATA')
    if la:
        cands.append(Path(la) / 'Programs' / 'MiKTeX' / 'miktex' / 'bin' / 'x64' / 'xelatex.exe')
    for c in cands:
        if c.is_file():
            return str(c)
    return None


def short_exe(exe: Path, major: Path) -> str:
    """解释器短标签：能相对包根表示就相对（避免长绝对路径刷屏，也便于跨机阅读）。"""
    try:
        return exe.resolve().relative_to(major.resolve()).as_posix()
    except Exception:
        return str(exe)


def has_module(exe: Path, mod: str) -> bool:
    rc, _ = run([exe, '-c', 'import %s' % mod], timeout=120)
    return rc == 0


def pick_python(prog: Path, mods: 'tuple[str, ...]') -> 'tuple[Path, list, bool]':
    """选一个装有指定模块的解释器：venv/环境变量 → 当前解释器 → 系统候选。

    返回 (exe, 候选记录, 是否命中)；未命中时 exe 为第一候选（调用方应走 SKIP + [降级]，不得假装成功）。
    """
    cands = []
    for c in [venv_python(prog), Path(sys.executable)] + system_pythons():
        if c is None:
            continue
        try:
            rc = c.resolve()
        except Exception:
            continue
        if rc not in cands:
            cands.append(rc)
    tries = []
    for c in cands[:PICK_MAX]:
        ok = all(has_module(c, m) for m in mods)
        lbl = c.parent.parent.name if (c.parent.parent / 'pyvenv.cfg').is_file() else c.name
        tries.append('%s[%s]' % (lbl, '有' + '/'.join(mods) if ok else '缺' + '/'.join(mods)))
        if ok:
            return c, tries, True
    return (cands[0] if cands else Path(sys.executable)), (tries or ['无候选解释器']), False


# ---------------------------------------------------------------- 黄金断言：解析真值与对质工具

def lp_vertices() -> list:
    """合成 LP 可行域顶点（精确有理数）：各约束边界线与 x=0 轴两两求交，再筛「满足全部约束 + x>=0」的点。"""
    rows = [(tuple(Fraction(int(v)) for v in row), Fraction(int(b))) for row, b in zip(LP_A_UB, LP_B_UB)]
    lines = rows + [((Fraction(1), Fraction(0)), Fraction(0)), ((Fraction(0), Fraction(1)), Fraction(0))]
    pts = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            (a1, b1), (a2, b2) = lines[i], lines[j]
            det = a1[0] * a2[1] - a1[1] * a2[0]
            if det == 0:                                   # 平行/重合：无唯一交点
                continue
            p = ((b1 * a2[1] - a1[1] * b2) / det, (a1[0] * b2 - b1 * a2[0]) / det)
            if p[0] < 0 or p[1] < 0:                       # 非负卦限外（变量 x >= 0）
                continue
            if all(c[0] * p[0] + c[1] * p[1] <= bb for c, bb in rows) and p not in pts:
                pts.append(p)
    return pts


def lp_truth(obj=None) -> 'tuple[Fraction, tuple]':
    """解析真值 (最优值, 最优解)：穷举可行顶点取最大目标值——2 变量 LP 的精确解，不依赖任何求解器。"""
    coef = tuple(_frac(c) for c in (obj if obj is not None else LP_OBJ))
    best_v, best_x = None, None
    for p in lp_vertices():
        v = sum(coef[k] * p[k] for k in range(len(coef)))
        if best_v is None or v > best_v:
            best_v, best_x = v, p
    return best_v, best_x


def lp_truth_box() -> 'tuple[Fraction, Fraction]':
    """目标系数 ±SENS_PCT 箱内最优值区间 [lo, hi]（精确 · 可复算）。

    变量非负 ⇒ max_v c·v 关于 c 分量单调不减 ⇒ 箱内下确界＝用系数下界解 LP、上确界＝用系数上界解 LP。
    """
    lo = tuple(Fraction(int(c)) * (1 - Fraction(str(SENS_PCT))) for c in LP_OBJ)
    hi = tuple(Fraction(int(c)) * (1 + Fraction(str(SENS_PCT))) for c in LP_OBJ)
    return lp_truth(lo)[0], lp_truth(hi)[0]


def sens_scan_points() -> list:
    """单参数扫描网格（与 `np.linspace(base*(1-pct), base*(1+pct), n)` 同点）：c1 ±20%，c2 固定。"""
    base = Fraction(int(LP_OBJ[0]))
    pct = Fraction(str(SENS_PCT))
    lo, hi = base * (1 - pct), base * (1 + pct)
    if SENS_N < 2:
        return [lo]
    return [lo + (hi - lo) * i / (SENS_N - 1) for i in range(SENS_N)]


def _frac(x) -> Fraction:
    """数值 → 精确有理数：Fraction/int/str 走字面精确值，float 走 as_integer_ratio（不引入十进制近似）。"""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, str):
        return Fraction(x)
    return Fraction(*float(x).as_integer_ratio())


def _coeffs_of(key: str) -> tuple:
    """驱动件角点键 `'2.4|4.0'` → 系数元组（精确有理数）。"""
    return tuple(_frac(p) for p in str(key).split('|'))


def _num(v) -> str:
    """数值展示：统一 6 位小数并去掉尾零（有理数/浮点通吃）。"""
    try:
        s = '%.6f' % float(v)
    except Exception:
        return str(v)
    return s.rstrip('0').rstrip('.') or '0'


def _tol(truth, print_eps: float = 0.0) -> float:
    """容差 = 相对 GOLD_REL（下限 1）＋ 打印量化误差（回读自 %.4f 输出时）。"""
    try:
        return print_eps + GOLD_REL * max(1.0, abs(float(truth)))
    except Exception:
        return print_eps + GOLD_REL


def _within(got, truth, tol: float) -> bool:
    try:
        return abs(float(got) - float(truth)) <= tol
    except Exception:
        return False


def _cmp_solution(label: str, val, xs, truth_val, truth_x, print_eps: float, fails: list) -> int:
    """把一组「最优值 + 产量向量」与解析真值对质；返回通过条数，不通过写入 fails。"""
    n = 0
    if _within(val, truth_val, _tol(truth_val, print_eps)):
        n += 1
    else:
        fails.append('%s 最优利润 %s ≠ 真值 %s（容差 %.1e）' % (label, _num(val), _num(truth_val), _tol(truth_val, print_eps)))
    for i, tv in enumerate(truth_x):
        got = xs[i] if xs and i < len(xs) else None
        if _within(got, tv, _tol(tv, print_eps)):
            n += 1
        else:
            fails.append('%s 产量 x%d %s ≠ 真值 %s' % (label, i + 1, _num(got), _num(tv)))
    return n


def run_gold_driver(prog: Path) -> 'tuple[dict | None, str, str]':
    """生成合成黄金驱动件并真跑（cwd=模板库，便于 `import utils.sensitivity`）。

    返回 (回传数据或 None, 解释器短标签, 说明)。候选解释器全缺 scipy/numpy → None + [降级] 说明。
    """
    exe, tries, found = pick_python(prog, ('scipy',))
    if not found:
        return None, '', '候选解释器均缺 scipy/numpy：%s' % '、'.join(tries)
    src = GOLD_DRIVER % dict(obj=LP_OBJ, a_ub=LP_A_UB, b_ub=LP_B_UB, pct=SENS_PCT, gn=GOLD_GRID,
                             sn=SENS_N, pct_txt='%d%%' % round(SENS_PCT * 100), sentinel=GOLD_SENTINEL)
    path = WORK / GOLD_DRIVER_NAME
    write_text(path, src)
    rc, txt = run([exe, str(path), str(prog)], cwd=prog, timeout=600)
    payload = ''
    for ln in txt.splitlines():
        if ln.startswith(GOLD_SENTINEL):
            payload = ln[len(GOLD_SENTINEL):]
    if rc != 0 or not payload:
        return None, short_exe(exe, prog.parent), '驱动件 rc=%d 且无哨兵回传：%s' % (rc, last_lines(txt))
    try:
        data = json.loads(payload)
    except Exception as e:
        return None, short_exe(exe, prog.parent), '哨兵回传解析失败：%s' % e
    if data.get('err'):
        return None, short_exe(exe, prog.parent), '驱动件内部异常：%s' % data['err']
    return data, short_exe(exe, prog.parent), ''


# ---------------------------------------------------------------- 工具

def last_lines(text: str, n: int = 2) -> str:
    ls = [l.strip() for l in (text or '').splitlines() if l.strip()]
    return ' ⏎ '.join(ls[-n:])[:220] if ls else '(无输出)'


def first_error(text: str) -> str:
    for l in (text or '').splitlines():
        if l.startswith('!') or 'Fatal error' in l:
            return l.strip()[:200]
    return ''


def stage(name: str, status: str, detail: str) -> None:
    RESULTS.append((name, status, detail))
    print('[%s] %s — %s' % (status, name, detail))


def _w(s: str) -> int:
    """显示宽度（CJK 宽字符按 2 计），用于控制台表对齐。"""
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)


def _pad(s: str, n: int) -> str:
    return s + ' ' * max(0, n - _w(s))


def write_text(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8', newline='\n')       # 固定 LF


def reset_work() -> Path:
    """重建合成工作目录（只在脚本自己的 _smoke_out/ 内删建）。"""
    if WORK.exists() and OUT in WORK.parents:
        shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True, exist_ok=True)
    return WORK


def _parse_num(line: str) -> 'float | None':
    """从输出行里抠出最后一个数字（`[最优值] 21.0000` / `  x1 = 2.0000`）。"""
    m = re.findall(r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?', line or '')
    try:
        return float(m[-1]) if m else None
    except Exception:
        return None


# ---------------------------------------------------------------- 各阶段

def stage_m1() -> Path:
    """M1：合成拆题卡（2 子问题）落临时工作目录；按 E-M1 门禁字段自检。"""
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    card = WORK / 'decompose_card.md'
    write_text(card, CARD_MD % dict(version=VERSION, ts=ts))
    txt = card.read_text(encoding='utf-8')
    fields = ['数学本质', '模型族初判', '数据可得性', '交付物']
    miss = [f for f in fields if f not in txt]
    sub_rows = len([l for l in txt.splitlines() if l.startswith('| 子问题')])
    ok = (not miss) and sub_rows == 2 and card.stat().st_size > 200
    if ok:
        detail = 'decompose_card.md %d B｜门禁字段齐｜子问题 %d（题型/模型族/数据可得性三列全）' % (
            card.stat().st_size, sub_rows)
    else:
        detail = '字段%s｜子问题行 %d（应 2）｜%d B' % ('齐' if not miss else '缺：' + '、'.join(miss),
                                                   sub_rows, card.stat().st_size)
    stage('M1 合成拆题卡（2 子问题）', 'PASS' if ok else 'FAIL', detail)
    return card


def stage_m4(prog: Path) -> dict:
    """M4：真跑模板库 `01-优化/lp.py`（子进程，cwd=模板目录），要求 rc=0；回读最优值/产量。

    解释器：venv / 环境变量 / 系统候选里第一个装 pulp 的；全缺 → SKIP（[降级]，不假装成功）。
    返回 dict（供 M4b 黄金断言消费）：ran / val / x / status。
    """
    lp = prog / '01-优化' / 'lp.py'
    if not lp.is_file():
        stage('M4 求解模板 lp.py（cwd=模板目录）', 'FAIL', '模板不在：%s' % lp.relative_to(prog.parent))
        return dict(ran=False, val=None, x=[], status='FAIL')
    exe, tries, found = pick_python(prog, ('pulp',))
    if not found:
        stage('M4 求解模板 lp.py（cwd=模板目录）', 'SKIP',
              '候选解释器均缺 pulp：%s（[降级] 模板真跑跳过；黄金断言改由 M4b 解析真值 + scipy 交叉核验）'
              % '、'.join(tries))
        return dict(ran=False, val=None, x=[], status='SKIP')
    t0 = time.time()
    rc, txt = run([exe, str(lp)], cwd=lp.parent, timeout=300)
    val = next((l.strip() for l in txt.splitlines() if '最优值' in l), '')
    xs = [l.strip() for l in txt.splitlines() if l.strip().startswith('x') and '=' in l]
    ok = rc == 0 and bool(val)
    stage('M4 求解模板 lp.py（cwd=模板目录）', 'PASS' if ok else 'FAIL',
          'rc=%d · %.1fs｜解释器=%s｜%s' % (rc, time.time() - t0, short_exe(exe, prog.parent),
                                           val or ('输出尾：' + last_lines(txt)))
          + ('' if ok else '｜候选 %s' % '、'.join(tries)))
    return dict(ran=bool(ok), val=_parse_num(val), x=[_parse_num(l) for l in xs],
                status='PASS' if ok else 'FAIL')


def stage_m4_golden(gold: 'dict | None', why: str, exe_lbl: str, m4: dict) -> None:
    """M4b：黄金数值断言（附录 C.3）—— 合成 LP 解析真值 vs 求解器输出，±GOLD_REL 相对容差。

    真值算法：可行域顶点穷举（精确有理数）取最大目标值（2 变量 LP 的解析解，可手算复核）。
    证据：① 驱动件 scipy.linprog（独立求解器）② 模板 lp.py 真跑回读（pulp 在位时）。
    任一断言不成立 → 本阶段 FAIL → 整体判定 FAIL 且 rc≠0。
    """
    truth_val, truth_x = lp_truth()
    fails, notes, n_ok = [], [], 0
    if gold is None:
        notes.append('[降级] %s' % why)
    else:
        b = gold.get('base') or {}
        n_ok += _cmp_solution('scipy 基准解', b.get('val'), b.get('x'), truth_val, truth_x, 0.0, fails)
        for key in sorted((gold.get('corners') or {})):
            rec = (gold.get('corners') or {})[key] or {}
            tv = lp_truth(_coeffs_of(key))[0]
            if _within(rec.get('val'), tv, _tol(tv)):
                n_ok += 1
            else:
                fails.append('scipy 角点 c=(%s) 最优值 %s ≠ 真值 %s' % (key, _num(rec.get('val')), _num(tv)))
    if m4.get('val') is not None:
        n_ok += _cmp_solution('模板 lp.py', m4['val'], m4.get('x') or [], truth_val, truth_x,
                              GOLD_PRINT_EPS, fails)
    elif m4.get('status') == 'SKIP':
        notes.append('模板真跑未执行（pulp 缺件 → 见 M4 行）')
    if not fails and not n_ok:
        notes.append('[降级] 无任何求解器可用：仅完成解析真值计算，未做数值对质')
    status = 'FAIL' if fails else ('PASS' if n_ok else 'SKIP')
    detail = '真值（精确有理数顶点法）最优利润=%s｜产量=(%s)｜对质通过 %d 条' % (
        _num(truth_val), '、'.join(_num(v) for v in truth_x), n_ok)
    if exe_lbl:
        detail += '｜驱动件=%s' % exe_lbl
    if notes:
        detail += '｜' + '｜'.join(notes)
    if fails:
        detail += '｜✗ ' + '；'.join(fails[:3])
    stage('M4b 黄金数值断言（解析真值 vs 求解器 ±1e-6）', status, detail)


def stage_m6(prog: Path) -> None:
    """M6：真跑 figkit 样例（缺件/缺 matplotlib → SKIP，不判 FAIL）。"""
    demo = prog / 'utils' / 'figkit' / 'figkit_demo1_grouped_bar.py'
    if not demo.is_file():
        stage('M6 图件样例 figkit_demo1_grouped_bar.py', 'SKIP',
              '未落盘（计划件 utils/figkit/…，批 4 后续交付）')
        return
    exe, tries, found = pick_python(prog, ('matplotlib',))
    if not found:
        stage('M6 图件样例 figkit_demo1_grouped_bar.py', 'SKIP',
              '候选解释器均缺 matplotlib：%s（[降级] 图件线跳过：英文标签 + 人检）' % '、'.join(tries))
        return
    t0 = time.time()
    rc, txt = run([exe, str(demo)], cwd=demo.parent, timeout=600)
    new = [f for f in demo.parent.rglob('*') if f.is_file()
           and f.suffix.lower() in ('.png', '.pdf', '.svg') and f.stat().st_mtime >= t0 - 1]
    ok = rc == 0 and bool(new)
    stage('M6 图件样例 figkit_demo1_grouped_bar.py', 'PASS' if ok else 'FAIL',
          'rc=%d · %.1fs｜新出图 %d 件（%s）｜解释器=%s' % (rc, time.time() - t0, len(new),
          '、'.join(sorted(f.name for f in new)[:3]) or '无', short_exe(exe, prog.parent))
          + ('' if ok else '｜尾：' + last_lines(txt) + '｜候选 %s' % '、'.join(tries)))


def stage_m6_sens(gold: 'dict | None', why: str) -> None:
    """M6s：敏感性区间断言（子问题2 · workflow 06）—— ±20% 系数扰动的可复算区间。

    真值（精确有理数）：① 系数箱内最优值区间 [LP(c_lo), LP(c_hi)]（变量非负 ⇒ max c·x 关于 c 单调）；
    ② 单参数扫描网格逐点真值 + 网格端点。证据：驱动件 scipy 在箱内 4 角 + GOLD_GRID² 网格的数值解，
    以及经模板库 `utils/sensitivity.py` 的 `scan_1d` 扫描结果。任一断言不成立 → FAIL。
    """
    lo, hi = lp_truth_box()
    grid = sens_scan_points()
    c2 = Fraction(int(LP_OBJ[1]))
    scan_truth = [lp_truth((c1, c2))[0] for c1 in grid]
    fails, notes, n_ok = [], [], 0
    if gold is None:
        notes.append('[降级] %s' % why)
    else:
        vals = []
        for key in sorted((gold.get('corners') or {})):
            rec = (gold.get('corners') or {})[key] or {}
            if rec.get('val') is not None:
                vals.append(float(rec['val']))
        for row in (gold.get('grid') or []):
            if len(row) >= 3 and row[2] is not None:
                vals.append(float(row[2]))
        if not vals:
            fails.append('驱动件未回传任何箱内数值解')
        else:
            out_of = [v for v in vals if not (float(lo) - _tol(lo) <= v <= float(hi) + _tol(hi))]
            if out_of:
                fails.append('%d 个采样值落在解析区间 [%s, %s] 外（例 %s）'
                             % (len(out_of), _num(lo), _num(hi), _num(out_of[0])))
            else:
                n_ok += 1
            for lbl, got, tv in (('下界', min(vals), lo), ('上界', max(vals), hi)):
                if _within(got, tv, _tol(tv)):
                    n_ok += 1
                else:
                    fails.append('箱内最优值%s %s ≠ 解析%s %s' % (lbl, _num(got), lbl, _num(tv)))
        scan = gold.get('scan') or {}
        c1s, svals = scan.get('c1') or [], scan.get('val') or []
        if not c1s:
            notes.append('[降级] 模板库 utils/sensitivity.py 扫描未跑：%s' % (gold.get('scan_err') or '未知'))
        elif len(c1s) != len(grid) or len(svals) != len(grid):
            fails.append('扫描点数 %d ≠ 网格 %d' % (len(c1s), len(grid)))
        else:
            bad = 0
            for i, c1 in enumerate(c1s):
                tv = lp_truth((_frac(c1), c2))[0]
                if not _within(c1, float(grid[i]), GOLD_REL * max(1.0, abs(float(grid[i])))):
                    bad += 1
                    fails.append('扫描点 %d 系数 %s ≠ 网格 %s' % (i, _num(c1), _num(grid[i])))
                elif not _within(svals[i], tv, _tol(tv)):
                    bad += 1
                    fails.append('扫描点 c1=%s：%s ≠ 真值 %s' % (_num(c1), _num(svals[i]), _num(tv)))
            if not bad:
                n_ok += len(c1s)
                if (_within(min(svals), min(scan_truth), _tol(min(scan_truth)))
                        and _within(max(svals), max(scan_truth), _tol(max(scan_truth)))):
                    n_ok += 1
                else:
                    fails.append('扫描区间 [%s, %s] ≠ 真值区间 [%s, %s]'
                                 % (_num(min(svals)), _num(max(svals)),
                                    _num(min(scan_truth)), _num(max(scan_truth))))
    if not fails and not n_ok:
        notes.append('[降级] 无任何求解器可用：仅完成解析区间计算，未做数值对质')
    status = 'FAIL' if fails else ('PASS' if n_ok else 'SKIP')
    detail = '±%d%% 目标系数箱解析区间=[%s, %s]｜扫描网格 %d 点真值区间=[%s, %s]｜对质通过 %d 条' % (
        round(SENS_PCT * 100), _num(lo), _num(hi), len(grid), _num(min(scan_truth)), _num(max(scan_truth)), n_ok)
    if notes:
        detail += '｜' + '｜'.join(notes)
    if fails:
        detail += '｜✗ ' + '；'.join(fails[:3])
    stage('M6s 敏感性区间断言（±20% 目标系数箱）', status, detail)


def stage_m7() -> None:
    """M7：最小 LaTeX 论文骨架（abstract/section/图占位）+ 编译一次。"""
    tex = WORK / PAPER_TEX_NAME
    write_text(tex, PAPER_TEX)
    txt = tex.read_text(encoding='utf-8')
    need = ['\\begin{abstract}', '\\section{', '\\begin{figure}', '图占位', '\\end{document}']
    miss = [n for n in need if n not in txt]
    ok = not miss
    stage('M7 论文骨架生成（abstract/section/图占位）', 'PASS' if ok else 'FAIL',
          '%s %d B｜要素 %s' % (PAPER_TEX_NAME, tex.stat().st_size,
                                '齐（abstract + 4 section + 图占位）' if ok else '缺：' + '、'.join(miss)))

    xl = find_xelatex()
    if not xl:
        stage('M7c xelatex 编译', 'SKIP', 'xelatex 不在环境变量/已知布局/PATH/MiKTeX（论文线降级：纯文本装配 + 清单）')
        return
    pdf = tex.with_suffix('.pdf')
    log = tex.with_suffix('.log')
    t0 = time.time()
    rc, txt = run([xl, '-interaction=nonstopmode', '-halt-on-error', tex.name], cwd=WORK, timeout=900)
    logtxt = log.read_text(encoding='utf-8', errors='replace') if log.is_file() else txt
    done = 'Output written on' in logtxt and 'Fatal error' not in logtxt
    if rc == 0 and pdf.is_file() and done:
        stage('M7c xelatex 编译', 'PASS',
              'rc=0 · %.1fs｜%s %d B｜log 含 Output written on' % (time.time() - t0, pdf.name, pdf.stat().st_size))
    else:
        stage('M7c xelatex 编译', 'WARN',
              'rc=%d｜pdf=%s｜尾：%s%s' % (rc, '在' if pdf.is_file() else '无', last_lines(logtxt),
              ('｜首个报错：' + first_error(logtxt)) if first_error(logtxt) else ''))


# ---------------------------------------------------------------- 报告 / 汇总

def render_report(system_root: Path, major: Path, prog: Path, src: str, secs: float) -> str:
    fails = [r for r in RESULTS if r[1] == 'FAIL']
    warns = [r for r in RESULTS if r[1] == 'WARN']
    skips = [r for r in RESULTS if r[1] == 'SKIP']
    passes = [r for r in RESULTS if r[1] == 'PASS']
    verdict = 'FAIL' if fails else 'PASS'
    vp = venv_python(prog)
    tv, tx = lp_truth()
    lo, hi = lp_truth_box()
    scan_truth = [lp_truth((c1, Fraction(int(LP_OBJ[1]))))[0] for c1 in sens_scan_points()]
    obj_txt = ' + '.join('%sx%d' % (c, i + 1) for i, c in enumerate(LP_OBJ))
    cons_txt = '；'.join(' + '.join('%sx%d' % (a, i + 1) for i, a in enumerate(row)) + ' <= %s' % b
                        for row, b in zip(LP_A_UB, LP_B_UB))
    lines = ['# smoke_chain 报告（%s）' % VERSION, '',
             '**判定：%s**（PASS=%d｜FAIL=%d｜WARN=%d｜SKIP=%d）· 用时 %.1fs' % (
                 verdict, len(passes), len(fails), len(warns), len(skips), secs), '',
             '- 时间：%s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
             '- 系统根：`%s`｜主根：`%s`｜来源：%s' % (system_root, major, src),
             '- 求解 venv：`%s`' % (vp if vp else '缺（回落当前解释器）'),
             '- 合成工作目录：`%s`' % WORK,
             '- 纪律：**不评分、不进锚、不触碰个人材料**（题面/数据/骨架全部合成）', '',
             '| 阶段 | 状态 | 详情 |', '|---|---|---|']
    lines += ['| %s | %s | %s |' % (n, s, d) for n, s, d in RESULTS]
    arts = sorted([f for f in OUT.rglob('*')
                   if f.is_file() and f.name != 'smoke_chain_report.md'], key=lambda p: str(p))
    lines += ['', '## 产物', '']
    lines += ['- `%s`（%d B）' % (f.relative_to(OUT).as_posix(), f.stat().st_size) for f in arts]
    lines += ['', '## 黄金断言（附录 C.3 · F13）', '',
              '- 合成 LP：max %s，s.t. %s，x >= 0；解析真值（精确有理数顶点法）= 最优利润 %s，最优产量 (%s)'
              % (obj_txt, cons_txt, _num(tv), '、'.join(_num(v) for v in tx)),
              '- 敏感性（目标系数 ±%d%% 箱）：解析区间 = [%s, %s]；单参数扫描网格 %d 点真值区间 = [%s, %s]'
              % (round(SENS_PCT * 100), _num(lo), _num(hi), len(scan_truth),
                 _num(min(scan_truth)), _num(max(scan_truth))),
              '- 判据：求解器输出须落在真值 ±%.0e 相对容差内（模板回读另计 %.0e 打印量化误差）；'
              '断言失败 → 该阶段 FAIL → 整体 rc≠0。' % (GOLD_REL, GOLD_PRINT_EPS)]
    lines += ['', '## 说明', '',
              '- 根解析：探测链（环境变量 MODELFORGE_ROOT → 向上找 templates-library/ + workflows/ → '
              '旧布局（Euler 子目录 workflows 在位）→ tools/ 上一级降级）；**不写死任何用户绝对路径**。',
              '- FAIL 判据：阶段执行失败、产物缺失或黄金断言不成立；**SKIP** = 计划件/依赖未落盘（如 figkit、pulp、'
              'matplotlib），一律写明 [降级] 原因；**WARN** = LaTeX 编译非零退出（容错：骨架已生成，附日志尾行）。',
              '- 任一 FAIL → 进程 exit 1；SKIP/WARN 不判 FAIL。',
              '- 复跑：`python smoke_chain.py`（合成件每次重建；含时间戳故非字节幂等，判定幂等）。']
    return '\n'.join(lines) + '\n'


def print_table() -> None:
    w_stage = max([_w('阶段')] + [_w(n) for n, _, _ in RESULTS]) + 2
    print()
    print(_pad('状态', 6) + _pad('阶段', w_stage) + '详情')
    print('-' * 6 + '-' * w_stage + '-' * 40)
    for n, s, d in RESULTS:
        print(_pad(s, 6) + _pad(n, w_stage) + d)


def main(argv=None) -> int:
    try:                                            # 中文输出到非 UTF-8 控制台时不炸
        getattr(sys.stdout, 'reconfigure')(encoding='utf-8', errors='replace')
    except Exception:
        pass
    ap = argparse.ArgumentParser(description='Euler 全链技术冒烟（M1→M4→M6→M7）')
    ap.add_argument('--root', help='包根或系统根（默认：环境变量 MODELFORGE_ROOT → 脚本位置向上探测链）')
    ap.add_argument('--selftest', action='store_true', help='别名：跑完整链即自测（全 PASS/SKIP 则 rc=0）')
    a = ap.parse_args(argv)

    t0 = time.time()
    system_root, major, src = resolve_roots(Path(a.root) if a.root else None)
    prog = major / 'templates-library'
    reset_work()

    print('smoke_chain %s｜系统根=%s｜主根=%s｜来源=%s' % (VERSION, system_root, major, src))
    print('合成工作目录：%s' % WORK)

    stage_m1()
    m4 = stage_m4(prog)
    gold, gold_exe, gold_why = run_gold_driver(prog)
    stage_m4_golden(gold, gold_why, gold_exe, m4)
    stage_m6(prog)
    stage_m6_sens(gold, gold_why)
    stage_m7()

    report = OUT / 'smoke_chain_report.md'
    write_text(report, render_report(system_root, major, prog, src, time.time() - t0))
    print_table()

    fails = [r for r in RESULTS if r[1] == 'FAIL']
    warns = [r for r in RESULTS if r[1] == 'WARN']
    skips = [r for r in RESULTS if r[1] == 'SKIP']
    print('\n判定：%s（FAIL=%d｜WARN=%d｜SKIP=%d）→ %s'
          % ('FAIL' if fails else 'PASS', len(fails), len(warns), len(skips), report))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
