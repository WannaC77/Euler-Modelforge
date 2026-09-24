# -*- coding: utf-8 -*-
"""论文级图表风格（统一入口）· v2（2026-09-19）

用法：
    from utils.plot_style import style_plot, save_fig, save_pub, audit_fig, add_units
    style_plot("cumcm")            # 国赛（中文）｜ style_plot("mcm") 美赛（英文盒式）
    fig, ax = plt.subplots()
    ...
    audit_fig(fig, insert_cm=13.0) # 字号门禁（按论文实际插入宽度）——图不通过不得交付
    save_pub(fig, "assets/图3-综合对比")   # 一次导出 PNG + PDF + SVG（三格式）
    # 兼容旧调用：save_fig(fig, "xxx.png")

v2 吸收（自研落地，2026-09-19；来源仅取方法与配置思路）：
- Figure Contract 四步法（做图前定论证逻辑）→ 见 references/图件管线.md
- 三格式导出 + pdf.fonttype/svg.fonttype 可编辑文本（自 Lupynow/math-modeling-skills 摘译）
- 「Origin 风」盒式坐标（四边框 + 内向刻度，美赛）自 Gunp-666/MCM-AI-Starter-Kit font_standard 摘译
- 字号门禁（标题≥10pt/节点≥8pt/边标签≥7.5pt@最终插入宽度）理念（自 xxszyh/cumcm-visualization 摘译）
- 调色板三原则：同族深浅 > 色相跳跃；灰度打印安全；红绿仅方向信号
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("matplotlib", "numpy"):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as _fm

# ---------- 字体注册（Windows CJK/西文，显式 addfont 最稳） ----------
_CJK_FONTS = [r"<系统字体目录>\msyh.ttc", r"<系统字体目录>\simhei.ttf"]
_SERIF_FONTS = [r"<系统字体目录>\times.ttf", r"<系统字体目录>\timesbd.ttf", r"<系统字体目录>\arial.ttf"]
for _fp in _CJK_FONTS + _SERIF_FONTS:
    if os.path.exists(_fp):
        try:
            _fm.fontManager.addfont(_fp)
        except Exception:
            pass

# ---------- 色板 ----------
# v1 兼容色（色盲友好取向）
COLORS = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd",
          "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

PALETTE = {
    # 国赛学术风：蓝主 / 砖红 / 森绿 / 赭金 / 紫灰 / 冷灰（同族可深浅微调）
    "cumcm": ["#1F4E79", "#C0504D", "#2E7D32", "#B8860B", "#6A4C93", "#5B6770"],
    # 低饱和度多面板（NMI pastel 思路）
    "nmi": ["#7EA8C4", "#C4A47E", "#A4C47E", "#C47EA8", "#7EC4A8", "#A87EC4"],
    # 灰度打印安全底序（配合线型/标记区分）
    "gray": ["#222222", "#555555", "#888888", "#AAAAAA", "#CCCCCC"],
}
# 灰度安全辅助：配合色板轮流使用，保证去色后仍可区分
LINESTYLES = ["-", "--", "-.", ":"]
MARKERS = ["o", "s", "^", "D", "v", "P"]

_CURRENT = {"kind": "cumcm"}


def style_plot(kind="cumcm", font_size=None, dpi=300, grid=None):
    """设置全局 matplotlib 风格。

    kind="cumcm"：国赛（中文）——CJK 无衬线优先、左/下轴、浅网格、学术蓝系。
    kind="mcm"  ：美赛（英文）——Times/Arial 衬线、四边框盒式、内向刻度、无网格。
    """
    kind = kind.lower()
    assert kind in ("cumcm", "mcm"), "kind 只支持 'cumcm' / 'mcm'"
    _CURRENT["kind"] = kind

    if kind == "mcm":
        base = font_size or 10
        matplotlib.rcParams.update({
            "figure.dpi": dpi,
            "savefig.dpi": dpi,
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Nimbus Roman", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "font.size": base,
            "axes.titlesize": base + 1,
            "axes.labelsize": base,
            "xtick.labelsize": base - 1,
            "ytick.labelsize": base - 1,
            "legend.fontsize": base - 1,
            "axes.linewidth": 1.1,
            "axes.spines.top": True,
            "axes.spines.right": True,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": False,
            "ytick.right": False,
            "axes.grid": False if grid is None else grid,
            "figure.figsize": (6, 4),
            "axes.unicode_minus": False,
        })
    else:  # cumcm（默认）
        base = font_size or 10.5
        matplotlib.rcParams.update({
            "figure.dpi": dpi,
            "savefig.dpi": dpi,
            "font.family": ["sans-serif"],
            # 注意：本机 mpl 单字体解析——CJK 字体必须放首位（Arial/DejaVu 在前会 tofu）
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
            "mathtext.fontset": "dejavusans",
            "font.size": base,
            "axes.titlesize": base + 1,
            "axes.labelsize": base,
            "xtick.labelsize": base - 1,
            "ytick.labelsize": base - 1,
            "legend.fontsize": base - 1,
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True if grid is None else grid,
            "grid.alpha": 0.3,
            "axes.prop_cycle": plt.cycler(color=PALETTE["cumcm"]),
            "figure.figsize": (6, 4),
            "axes.unicode_minus": False,
        })

    # 可编辑矢量文本（Word/PPT/LaTeX 场景重要；两风格通用）
    matplotlib.rcParams.update({
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    })


# 别名：旧文档中的 apply_style == style_plot（两种叫法均可）
apply_style = style_plot


def save_fig(fig, path: str):
    """（v1 兼容）保存单个位图（dpi 取 rcParams，bbox_inches='tight' 裁白边）。"""
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[图已保存] {path}")


def save_pub(fig, base_path: str, formats=("png", "pdf", "svg")):
    """（v2）一次三格式导出：PNG（位图）+ PDF（LaTeX）+ SVG（Word/PPT 可编辑）。
    base_path 不带扩展名，例如 'assets/图3-综合对比'。"""
    outs = []
    for fmt in formats:
        p = f"{base_path}.{fmt}"
        fig.savefig(p, bbox_inches="tight")
        outs.append(p)
    plt.close(fig)
    print("[三格式已保存] " + " | ".join(outs))
    return outs


def text_renderable(tx, fig):
    """判断一个 Text 是否属于「会出现在成品里」的内容（与 mpl tight bbox 同口径）。

    2026-09-19：三类「不进入成品」的文本会造成假越界/假计数，审计与自检均须跳过——
    ① Text 自身不可见（get_visible() False，轴复用 Tick 的残影）；
    ② 轴视界外 tick 标签（LogLocator 会生成视界外刻度并保持可见；mpl 自己的
       tight bbox 也排除它们。实测：xlim=(0.06,32) 时 10^-2/10^2 两枚标签
       仍 vis=True 且悬在画布外——它们从不进成品）；
    ③ 轴已关闭（axis('off')）的轴的装饰文本（刻度标签/轴标签/offset 文本
       不绘制）。注：ax.text()/annotate() 的内容即使轴关闭也照常绘制，不受影响。
    """
    if not tx.get_visible():
        return False
    for ax in fig.axes:
        for axis, lim in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
            lo, hi = (min(lim), max(lim))
            if tx is axis.label or tx is axis.get_offset_text():
                if not getattr(ax, "axison", True):
                    return False
                continue
            for locs, labs in ((axis.get_ticklocs(), axis.get_ticklabels()),
                               (axis.get_minorticklocs(), axis.get_minorticklabels())):
                for loc, lab in zip(locs, labs):
                    if lab is tx:
                        if not getattr(ax, "axison", True):
                            return False
                        return lo <= loc <= hi
    return True


def audit_fig(fig, insert_cm=None, min_pt=7.5, warn_pt=9.0,
              raise_on_violation=False, name=""):
    """（v2）字号门禁 + 裁剪检测——图**交付前必过**（对齐「不含版本号的分数不作数」纪律）。

    insert_cm: 论文中实际插入宽度（cm，如国赛 A4 正文 15.8/16、图栏 13）。
              给定时按缩放折算各个文字在纸面的实际字号；不给则按画布原尺寸。
    min_pt:    纸面最小字号红线（默认 7.5pt，理由：缩印 A4 可读下限）。
    warn_pt:   警告线（默认 9pt）。
    raise_on_violation=True 时违规即 SystemExit(1)（脚本管线用）。
    返回 dict：min_eff_pt / violations / warns / clipped / n_texts
    """
    from matplotlib.text import Text
    fig.canvas.draw()
    try:
        renderer = fig.canvas.get_renderer()
    except AttributeError:
        renderer = None

    W_cm = fig.get_figwidth() * 2.54
    scale = (insert_cm / W_cm) if insert_cm else 1.0
    fb = fig.bbox

    rows, clipped = [], []
    n_skipped = 0
    for t in fig.findobj(Text):
        s = (t.get_text() or "").strip()
        if not s:
            continue
        if not text_renderable(t, fig):
            n_skipped += 1
            continue
        try:
            fs = float(t.get_fontsize())
        except Exception:
            continue
        rows.append((fs * scale, fs, s[:26]))
        if renderer is not None:
            try:
                bb = t.get_window_extent(renderer)
                if bb.x0 < -1 or bb.y0 < -1 or bb.x1 > fb.width + 1 or bb.y1 > fb.height + 1:
                    clipped.append(s[:26])
            except Exception:
                pass

    eff = [r[0] for r in rows]
    minv = min(eff) if eff else float("inf")
    violations = [r for r in rows if r[0] < min_pt]
    warns = [r for r in rows if min_pt <= r[0] < warn_pt]

    tag = f"[{name}] " if name else ""
    scope = f"（插入宽 {insert_cm} cm）" if insert_cm else "（画布原尺寸）"
    print(f"{tag}字号审计{scope}: 文本 {len(rows)} 处, 纸面最小 {minv:.2f} pt"
          + (f"（跳过不绘制 {n_skipped} 处）" if n_skipped else ""))
    for r in violations[:8]:
        print(f"  ✗ 违规 <{min_pt}pt: {r[0]:.2f}pt | {r[2]}")
    for r in warns[:6]:
        print(f"  ⚠ 偏小 <{warn_pt}pt: {r[0]:.2f}pt | {r[2]}")
    if clipped:
        print(f"  ⚠ 疑被裁剪: {clipped[:6]}")
    if not violations and not warns:
        print("  ✓ 全部达标")
    if raise_on_violation and (violations or clipped):
        raise SystemExit(1)
    return {"min_eff_pt": minv, "violations": violations, "warns": warns,
            "clipped": clipped, "n_texts": len(rows)}


def add_units(ax, xlabel: str = "", ylabel: str = "", xtitle: str = "", ytitle: str = ""):
    """给坐标轴加标签（v1 兼容）。示例: add_units(ax, xtitle="Time", ytitle="Population")"""
    if xtitle:
        ax.set_xlabel(f"{xlabel} ({xtitle})" if xlabel else xtitle)
    else:
        ax.set_xlabel(xlabel)
    if ytitle:
        ax.set_ylabel(f"{ylabel} ({ytitle})" if ylabel else ytitle)
    else:
        ax.set_ylabel(ylabel)


def next_style(i: int):
    """轮换取「第 i 条系列」的 (颜色, 线型, 标记)——灰度安全组合。"""
    return (PALETTE["cumcm"][i % len(PALETTE["cumcm"])],
            LINESTYLES[(i // len(PALETTE["cumcm"])) % len(LINESTYLES)],
            MARKERS[i % len(MARKERS)])


__all__ = ["style_plot", "apply_style", "save_fig", "save_pub", "audit_fig",
           "text_renderable", "add_units", "next_style", "COLORS", "PALETTE",
           "LINESTYLES", "MARKERS"]
