# -*- coding: utf-8 -*-
"""figkit 样例 3 —— 网络图（节点/边纯 matplotlib 自绘，零额外依赖）。

适用场景
--------
物流/供应链网络、节点重要性、社区结构、路径与流量示意。论文里的网络图常
被画成「软件截图风」，本样例给出可直接进论文的规范画法。

为什么不用 networkx
-------------------
网络图只需三件事：**布局 + 画线 + 画点**。本文件所以自实现（不引新依赖）：
① 布局：Fruchterman-Reingold 力导向（斥力 k²/d、引力 d²/k、线性降温），
   初值取「分层初值」——供应链的层级关系是题目给定的先验，纯随机初值会
   被力导向搅乱，分层初值让层级结构保留、只让同层节点自己散开；
② 画边：LineCollection 一次画完，线宽 ∝ 权重（粗细即信息，不靠颜色）；
③ 画点：scatter 面积 ∝ 加权度，颜色标层级，标签自带层前缀（S/P/W/R/C）
   ——黑白打印下光看标签也能读出层级，不依赖颜色。
另外 graphviz/pygraphviz 不在 requirements.txt，系里机器不一定装得上——自绘版
在只有 matplotlib+numpy 的环境里照样能跑，这是「可交付」的硬要求。

产出
----
    utils/figkit/_out/figkit_demo3_network.{png,pdf,svg}

运行
----
    python utils/figkit/figkit_demo3_network.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

try:                                     # 包内运行：python -m utils.figkit.xxx
    from ..plot_style import PALETTE, save_pub, style_plot
except ImportError:                      # 直跑回退：python utils/figkit/xxx.py
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from utils.plot_style import PALETTE, save_pub, style_plot

save_fig = save_pub                      # plot_style v2 三格式出口（PNG+PDF+SVG）

# ============ 数据区 ============
SEED = 20260922
LAYERS = ["Supplier", "Plant", "Warehouse", "Retailer", "Customer"]   # 供应链五层
NODES = [                                # (节点名, 层序号)
    ("S1", 0), ("S2", 0),
    ("P1", 1), ("P2", 1),
    ("W1", 2), ("W2", 2), ("W3", 2),
    ("R1", 3), ("R2", 3), ("R3", 3), ("R4", 3),
    ("C1", 4), ("C2", 4), ("C3", 4),
]
EDGES = [                                # (起点, 终点, 权重=流量/运量)
    ("S1", "P1", 3), ("S1", "P2", 1), ("S2", "P1", 2), ("S2", "P2", 3),
    ("P1", "W1", 4), ("P1", "W2", 2), ("P1", "W3", 1), ("P2", "W2", 3), ("P2", "W3", 4),
    ("W1", "R1", 3), ("W1", "R2", 2), ("W1", "R3", 1),
    ("W2", "R2", 3), ("W2", "R3", 2),
    ("W3", "R3", 3), ("W3", "R4", 4),
    ("R1", "C1", 4), ("R2", "C1", 2), ("R2", "C2", 3),
    ("R3", "C2", 2), ("R3", "C3", 3), ("R4", "C3", 4),
]
ITERS = 250                              # 力导向迭代次数
EDGE_COLOR = "#6E7880"                   # 边色（比纯灰深一点：w=1 的细线也要看得见）


def edge_lw(w):
    """边宽映射：权重 → 线宽（全图唯一定义处，图例与数据线共用，避免两处写歪）。"""
    return 0.55 + 0.55 * w


OUT_DIR = Path(__file__).resolve().parent / "_out"
FIG_NAME = "figkit_demo3_network"


def weighted_degree(n, edges):
    """加权度 = 该节点所有关联边的权重之和。"""
    deg = np.zeros(n)
    for i, j, w in edges:
        deg[i] += w
        deg[j] += w
    return deg


def layer_init(n, node_layer, n_layers):
    """分层初值：第 L 层节点排在 x = L 的竖列上，同层沿 y 铺开。"""
    xs_by_layer = {}
    for idx, L in enumerate(node_layer):
        xs_by_layer.setdefault(L, []).append(idx)
    pos = np.zeros((n, 2))
    for L, idxs in xs_by_layer.items():
        ys = np.linspace(0.0, 1.0, len(idxs) + 2)[1:-1]
        for k, idx in enumerate(idxs):
            pos[idx] = (L / max(1, n_layers - 1), ys[k])
    return pos


def spring_layout(n, edges, init, iters=ITERS, seed=SEED):
    """Fruchterman-Reingold 力导向布局（自实现，不依赖 networkx）。

    斥力（所有节点对）：k² / d  ；引力（仅沿边，权重 w）：w · d² / k
    位移按线性降温截断 t = t0·(1 - iter/iters)，避免后期来回震荡。
    """
    rng = np.random.default_rng(seed)
    pos = np.array(init, dtype=float) + rng.normal(0.0, 0.015, size=(n, 2))
    k = np.sqrt(1.0 / n)                 # 理想边长
    t0 = 0.30
    for it in range(iters):
        diff = pos[:, None, :] - pos[None, :, :]
        dist = np.sqrt((diff ** 2).sum(axis=-1))
        np.fill_diagonal(dist, np.inf)   # 自身斥力置零
        dist = np.maximum(dist, 1e-6)
        disp = ((k * k / dist)[..., None] * (diff / dist[..., None])).sum(axis=1)
        for i, j, w in edges:            # 引力只作用于有边的点对
            d = pos[i] - pos[j]
            dl = float(np.linalg.norm(d)) + 1e-9
            fa = (dl * dl) / k
            disp[i] -= (d / dl) * fa * w
            disp[j] += (d / dl) * fa * w
        dl_disp = np.linalg.norm(disp, axis=1) + 1e-9
        lim = t0 * (1.0 - it / iters)
        pos += np.minimum(dl_disp, lim)[:, None] * (disp / dl_disp[:, None])
    pos -= pos.min(axis=0)               # 归一化到 [0,1]，便于排版
    span = pos.max(axis=0).max()
    return pos / (span if span > 1e-9 else 1.0)


def main():
    style_plot("mcm")                    # 英文图取美赛盒式风格（本图 axis off，主要取字体）
    names = [nm for nm, _ in NODES]
    idx = {nm: i for i, nm in enumerate(names)}
    node_layer = np.array([L for _, L in NODES])
    edges = [(idx[a], idx[b], w) for a, b, w in EDGES]
    n = len(names)

    pos = spring_layout(n, edges, layer_init(n, node_layer, len(LAYERS)))
    wdeg = weighted_degree(n, edges)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))

    # ---- 边：LineCollection 一次画完，线宽 ∝ 权重（粗细即信息） ----
    segs = [[pos[i], pos[j]] for i, j, _ in edges]
    ax.add_collection(LineCollection(segs, colors=EDGE_COLOR,
                                     linewidths=[edge_lw(w) for _, _, w in edges],
                                     zorder=1, alpha=0.9))

    # ---- 节点：面积 ∝ 加权度，颜色标层级 ----
    fig.canvas.draw()                    # 取 axe 尺寸前先让画布就位（s 用 pt² 与 dpi 无关）
    sizes = 45.0 + 16.0 * wdeg
    colors = [PALETTE["cumcm"][L % len(PALETTE["cumcm"])] for L in node_layer]
    ax.scatter(pos[:, 0], pos[:, 1], s=sizes, c=colors,
               edgecolors="black", linewidths=0.8, zorder=3)

    # ---- 标签：一律黑字（黑白打印可读），放在节点右上方 ----
    for i, nm in enumerate(names):
        ax.annotate(nm, (pos[i, 0], pos[i, 1]), textcoords="offset points",
                    xytext=(0, 7.5), ha="center", fontsize=7.5, zorder=4)

    ax.set_xlim(-0.09, 1.09)
    ax.set_ylim(-0.13, 1.13)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Layered supply-chain network (node size = weighted degree, "
                 "edge width = flow)", pad=6)

    # ---- 两个图例：层级（颜色）与线宽（流量），都用代理图元 ----
    # 层级图例放到坐标区**外侧**右边：网络经力导向后节点可能占到左上角，
    # 图例压在节点上会把它和标签糊掉（且图例底色半透明会让节点看着「发白」）。
    h_layer = [Line2D([], [], marker="o", linestyle="none", markersize=5.5,
                      markerfacecolor=PALETTE["cumcm"][L % len(PALETTE["cumcm"])],
                      markeredgecolor="black", markeredgewidth=0.6, label=nm)
               for L, nm in enumerate(LAYERS)]
    # add_artist：同一 Axes 上放两个图例必须如此——否则第二次 ax.legend() 会把
    # 第一个（ax.legend_ 指向的那个）移除，只剩一个图例。
    leg_layer = ax.legend(handles=h_layer, loc="upper left",
                          bbox_to_anchor=(1.005, 1.02), fontsize=7.5, ncol=1,
                          frameon=True, borderaxespad=0.0,
                          title="Layer", title_fontsize=8)
    ax.add_artist(leg_layer)
    h_w = [Line2D([], [], color=EDGE_COLOR, lw=edge_lw(w), label=f"w = {w}")
           for w in (1, 4)]
    ax.legend(handles=h_w, loc="lower right", fontsize=7.5, frameon=True,
              title="Flow weight", title_fontsize=8)
    fig.tight_layout()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(OUT_DIR / FIG_NAME))

    # ---------- 关键数值 ----------
    order = np.argsort(-wdeg)
    n_edge = len(edges)
    density = 2.0 * n_edge / (n * (n - 1))
    layer_cnt = {LAYERS[L]: int((node_layer == L).sum()) for L in range(len(LAYERS))}
    print(f"[网络] {n} 节点 / {n_edge} 边 / {len(LAYERS)} 层｜密度 {density:.3f}"
          f"｜总流量 {sum(w for *_, w in edges)}")
    print(f"[层级] " + "、".join(f"{k} {v}" for k, v in layer_cnt.items()))
    print(f"[加权度] top3: "
          + "、".join(f"{names[i]}={wdeg[i]:.0f}" for i in order[:3])
          + f"｜最低 {names[order[-1]]}={wdeg[order[-1]]:.0f}")
    print(f"[布局] FR 力导向 {ITERS} 迭代（seed={SEED}）+ 分层初值；"
          f"坐标域 [{pos.min():.3f}, {pos.max():.3f}]")


if __name__ == "__main__":
    main()
