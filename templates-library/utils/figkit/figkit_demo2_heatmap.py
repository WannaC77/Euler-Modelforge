# -*- coding: utf-8 -*-
"""figkit 样例 2 —— 热图（带 colorbar + 单元格数值标注）。

适用场景
--------
「参数 × 时刻」「指标 × 方案」这类二维矩阵的强弱格局展示——敏感性分析、
相关矩阵、评价得分矩阵都能套。本样例给出论文热图的两个常见坑的解：
① colorbar 必须带量纲标签（无标签的色条等于没有信息）；② 单元格数字要按
底色深浅自动切黑/白，否则深色格上黑字看不清。

数据
----
合成数据：6 个参数 × 12 个时刻的敏感性指数矩阵（平滑场 + 噪声），固定 seed。
取值域 [-1, 1]，用发散型色阶 RdYlBu_r（红=正相关，蓝=负相关）。

产出
----
    utils/figkit/_out/figkit_demo2_heatmap.{png,pdf,svg}

运行
----
    python utils/figkit/figkit_demo2_heatmap.py
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("matplotlib", "numpy"):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize

try:                                     # 包内运行：python -m utils.figkit.xxx
    from ..plot_style import save_pub, style_plot
except ImportError:                      # 直跑回退：python utils/figkit/xxx.py
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from utils.plot_style import save_pub, style_plot

save_fig = save_pub                      # plot_style v2 三格式出口（PNG+PDF+SVG）

# ============ 数据区 ============
SEED = 20260922
PARAMS = ["k1", "k2", "k3", "k4", "k5", "k6"]                 # 行：参数
TIMES = [f"T{i:02d}" for i in range(1, 13)]                   # 列：时刻
CMAP = "RdYlBu_r"                                             # 发散型：红正蓝负
VMIN, VMAX = -1.0, 1.0                                        # 对称色阶（0 居中才不骗人）
ANNOT_THRESHOLD = 0.10                                        # |v| 小于此值不标数字（免得糊成一片）

OUT_DIR = Path(__file__).resolve().parent / "_out"
FIG_NAME = "figkit_demo2_heatmap"


def make_matrix(seed=SEED):
    """合成敏感性指数矩阵：若干高斯峰叠加 + 小噪声，形状 (len(PARAMS), len(TIMES))。"""
    rng = np.random.default_rng(seed)
    n, m = len(PARAMS), len(TIMES)
    Z = np.zeros((n, m))
    peaks = [(0, 2.0, 0.9, 1.6), (1, 8.5, -1.0, 2.0), (2, 5.0, 0.6, 1.2),
             (3, 10.0, -0.7, 1.8), (4, 3.5, -0.5, 2.4), (5, 7.0, 0.8, 1.5)]
    for r, c0, amp, sig in peaks:
        Z[r] += amp * np.exp(-((np.arange(m) - c0) ** 2) / (2 * sig ** 2))
    Z += rng.normal(0, 0.06, size=(n, m))
    return np.clip(Z, VMIN, VMAX)


def main():
    style_plot("mcm")                    # 英文图取美赛盒式风格
    Z = make_matrix()
    n, m = Z.shape

    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    im = ax.imshow(Z, cmap=CMAP, vmin=VMIN, vmax=VMAX, aspect="auto",
                   interpolation="nearest")

    # 单元格数值标注：按底色相对亮度自动切黑/白（深色格上黑字＝不可读）
    norm = Normalize(vmin=VMIN, vmax=VMAX)
    rgba = im.cmap(norm(Z))
    lum = 0.2126 * rgba[..., 0] + 0.7152 * rgba[..., 1] + 0.0722 * rgba[..., 2]
    for r in range(n):
        for c in range(m):
            if abs(Z[r, c]) < ANNOT_THRESHOLD:
                continue
            ax.text(c, r, f"{Z[r, c]:.2f}", ha="center", va="center",
                    fontsize=6.6, color=("white" if lum[r, c] < 0.55 else "black"))

    ax.set_xticks(np.arange(m))
    ax.set_xticklabels(TIMES, rotation=0, fontsize=7.5)
    ax.set_yticks(np.arange(n))
    ax.set_yticklabels(PARAMS)
    ax.set_xlabel("Time step (month)")
    ax.set_ylabel("Parameter")
    ax.set_title("Parameter sensitivity heat map", pad=10)
    # 网格线：用白色细线切格，比默认灰线更干净
    ax.set_xticks(np.arange(-0.5, m, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.8)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(which="major", length=2.5)

    # colorbar 必须带量纲标签（无标签色条等于没信息）
    cb = fig.colorbar(im, ax=ax, fraction=0.036, pad=0.02)
    cb.set_label("Sensitivity index (-)", fontsize=9)
    cb.ax.tick_params(labelsize=8)
    fig.tight_layout()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(OUT_DIR / FIG_NAME))

    # ---------- 关键数值 ----------
    r_max, c_max = np.unravel_index(int(np.argmax(Z)), Z.shape)
    r_min, c_min = np.unravel_index(int(np.argmin(Z)), Z.shape)
    print(f"[数据] 矩阵 {n} 参数 x {m} 时刻，值域 [{Z.min():.3f}, {Z.max():.3f}]，"
          f"均值 {Z.mean():.4f}（seed={SEED}）")
    print(f"[最强正] {PARAMS[r_max]} @ {TIMES[c_max]} = {Z[r_max, c_max]:+.3f}")
    print(f"[最强负] {PARAMS[r_min]} @ {TIMES[c_min]} = {Z[r_min, c_min]:+.3f}")
    print(f"[格局] |v| > 0.5 的格 {int((np.abs(Z) > 0.5).sum())}/{Z.size}"
          f"（{np.abs(Z).mean():.3f} 平均强度）；标注跳过 |v| < {ANNOT_THRESHOLD} 的格")
    print(f"[色阶] {CMAP}，vmin/vmax = {VMIN:g}/{VMAX:g}（对称：0 才落在色带中点）")


if __name__ == "__main__":
    main()
