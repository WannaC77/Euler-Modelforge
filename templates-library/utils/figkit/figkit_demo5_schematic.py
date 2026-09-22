# -*- coding: utf-8 -*-
"""figkit 样例 5 —— 机理示意图（纯 matplotlib patch/arrow 拼装）。

适用场景
--------
技术路线图、模型机理图、算法流程图——论文里「讲清楚思路」的图。用 Visio/PPT
画的图进 LaTeX 会变糊、字号也不统一；本样例证明**纯代码就能拼出矢量示意图**，
改一个常量即整图重排，且字体/配色与其它图完全一致。

要点
----
- 圆角框：``FancyBboxPatch(boxstyle="round,pad=..,rounding_size=..")``
- 箭头：``FancyArrowPatch(arrowstyle="-|>", connectionstyle="arc3,rad=..")``；
  ``rad`` 给一点点弧度，回环箭头才不会和直线叠在一起。
- 实线框 = 主流程，虚线框 = 内部/校验环节；图内注明该约定，读者不用猜。
- 坐标系取「示意坐标」（x 0-10, y 0-6）而非数据坐标——示意图不标刻度，
  一律 ``axis("off")``，排版由常量控制，改坐标即挪位置。

产出
----
    utils/figkit/_out/figkit_demo5_schematic.{png,pdf,svg}

运行
----
    python utils/figkit/figkit_demo5_schematic.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

try:                                     # 包内运行：python -m utils.figkit.xxx
    from ..plot_style import PALETTE, save_pub, style_plot
except ImportError:                      # 直跑回退：python utils/figkit/xxx.py
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from utils.plot_style import PALETTE, save_pub, style_plot

save_fig = save_pub                      # plot_style v2 三格式出口（PNG+PDF+SVG）

# ============ 版式区（改这里即整图重排）============
BOX_W, BOX_H = 1.86, 1.06                # 方框尺寸
Y_MAIN = 3.40                            # 主流程中线 y
X_MAIN = [1.20, 3.55, 5.95, 8.35]        # 四个主环节中心 x
Y_CHECK = 1.24                           # 校验回路中线 y
BLUE = PALETTE["cumcm"][0]               # 主色（框线/箭头）
RED = PALETTE["cumcm"][1]                # 强调色（回环）
FS_TITLE, FS_BODY = 9.0, 8.0             # 框内字号

OUT_DIR = Path(__file__).resolve().parent / "_out"
FIG_NAME = "figkit_demo5_schematic"


def box(ax, cx, cy, title, sub=(), fc="white", ec=BLUE, dashed=False):
    """圆角框 + 框内标题/副行文字。返回 patch（便于统计与后续微调）。"""
    p = FancyBboxPatch((cx - BOX_W / 2, cy - BOX_H / 2), BOX_W, BOX_H,
                       boxstyle="round,pad=0.03,rounding_size=0.14",
                       linewidth=1.15, facecolor=fc, edgecolor=ec, zorder=2,
                       linestyle=("--" if dashed else "-"))
    ax.add_patch(p)
    n = len(sub)
    # 标题与副行整体垂直居中：标题在上，副行平分下方空间
    ax.text(cx, cy + (0.16 if n else 0.0), title, ha="center", va="center",
            fontsize=FS_TITLE, fontweight="bold", color=ec, zorder=3)
    for k, s in enumerate(sub):
        ax.text(cx, cy + 0.02 - 0.26 * (k + 1) + (0.05 if n else 0.0), s,
                ha="center", va="center", fontsize=FS_BODY - 0.8,
                color="#333333", zorder=3)
    return p


def arrow(ax, p1, p2, label="", rad=0.0, dashed=False, color=BLUE,
          lab_dx=0.0, lab_dy=0.16, lab_rot=0):
    """带弧度的箭头 + 沿线标注（标注默认放在中点上方一点）。"""
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=11,
                        linewidth=1.25, color=color, zorder=1, shrinkA=0, shrinkB=0,
                        linestyle=("--" if dashed else "-"),
                        connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)
    if label:
        mx, my = (p1[0] + p2[0]) / 2 + lab_dx, (p1[1] + p2[1]) / 2 + lab_dy
        ax.text(mx, my, label, ha="center", va="center", fontsize=FS_BODY - 0.8,
                color=color, rotation=lab_rot, zorder=3)
    return a


def main():
    style_plot("mcm")                    # 英文图取美赛盒式风格
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    x1, x2, x3, x4 = X_MAIN
    # ---- 主流程四环节 ----
    box(ax, x1, Y_MAIN, "Data", ("observations", "$X \\in R^{n \\times d}$"))
    box(ax, x2, Y_MAIN, "Preprocess", ("clean / scale", "feature select"))
    box(ax, x3, Y_MAIN, "Model", ("parameters $\\theta$", "solve / fit"))
    box(ax, x4, Y_MAIN, "Decision", ("policy / report", "sensitivity check"))
    # ---- 主流程箭头 ----
    arrow(ax, (x1 + BOX_W / 2, Y_MAIN), (x2 - BOX_W / 2, Y_MAIN))
    arrow(ax, (x2 + BOX_W / 2, Y_MAIN), (x3 - BOX_W / 2, Y_MAIN))
    arrow(ax, (x3 + BOX_W / 2, Y_MAIN), (x4 - BOX_W / 2, Y_MAIN))

    # ---- 校验回路（Model <-> Validation，虚线示「内部环节」）----
    box(ax, x3, Y_CHECK, "Validation", ("held-out test", "error metrics"),
        fc="#F4F6F8", dashed=True)
    arrow(ax, (x3 - 0.55, Y_MAIN - BOX_H / 2), (x3 - 0.55, Y_CHECK + BOX_H / 2),
          color="#5B6770")
    arrow(ax, (x3 + 0.55, Y_CHECK + BOX_H / 2), (x3 + 0.55, Y_MAIN - BOX_H / 2),
          label="model selection", color="#5B6770", lab_dx=0.98, lab_dy=0.0,
          lab_rot=0, dashed=True)

    # ---- 迭代回环：Decision 不达标则回到 Preprocess（拱形走上方）----
    arrow(ax, (x4, Y_MAIN + BOX_H / 2), (x2, Y_MAIN + BOX_H / 2),
          label="iterative refinement (if metrics fail)", rad=-0.34,
          color=RED, lab_dy=0.58)

    ax.set_title("Modeling workflow: main pipeline, validation loop and refinement",
                 pad=14)
    ax.text(0.5, -0.035, "Solid = main pipeline   |   Dashed = internal loop   |   "
                         "Red = refinement feedback",
            transform=ax.transAxes, ha="center", va="top", fontsize=FS_BODY - 0.8,
            color="#5B6770")
    fig.tight_layout()

    # 先量占用范围再落盘——save_pub 会 plt.close(fig)，关图后 canvas 拿不到 renderer
    fig.canvas.draw()
    renderer = getattr(fig.canvas, "get_renderer", lambda: None)()
    bb = ax.get_tightbbox(renderer) if renderer is not None else fig.bbox

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(OUT_DIR / FIG_NAME))

    # ---------- 关键数值 ----------
    n_boxes = sum(isinstance(p, FancyBboxPatch) for p in ax.patches)
    n_arrows = sum(isinstance(p, FancyArrowPatch) for p in ax.patches)
    n_texts = len([t for t in ax.texts if t.get_text().strip()])
    print(f"[版式] 方框 {n_boxes} 个（实线 {n_boxes - 1} + 虚线 1）｜箭头 {n_arrows} 条｜"
          f"轴内文字 {n_texts} 条")
    print(f"[坐标] 示意坐标 x∈[0,10] y∈[0,6]（无刻度）；主流程 y={Y_MAIN}，"
          f"校验回路 y={Y_CHECK}，主环节 x={X_MAIN}")
    print(f"[画布] 图形 {fig.get_size_inches()[0]:.2f}x{fig.get_size_inches()[1]:.2f} in"
          f"｜实际占用 {bb.width:.0f}x{bb.height:.0f} px（tight bbox）")
    print(f"[配色] 主色 {BLUE}｜强调 {RED}｜校验回路 #5B6770（同族冷灰，不与主流程抢视线）")


if __name__ == "__main__":
    main()
