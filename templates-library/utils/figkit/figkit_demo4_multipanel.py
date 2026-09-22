# -*- coding: utf-8 -*-
"""figkit 样例 4 —— 多面板 2×2（(a)(b)(c)(d) 标号）。

适用场景
--------
一张图放四类信息（趋势 / 拟合 / 对比 / 分布）——论文里省版面、答辩里一屏讲完
的标准做法。四个面板共用一套字号与配色，避免「四个图风格各不同」的廉价感。

本样例同时演示两个细节
----------------------
① 面板标号 (a)(b)(c)(d) 用 ``transform=ax.transAxes`` + ``clip_on=False`` 贴在
   轴外左上，位置不随数据变化；(a)(b)(c)(d) 是**图注里能引用**的编号，比在标题
   里写 "左上图" 专业得多。
② 线条样式统一取 ``plot_style.next_style(i)``（颜色/线型/标记三元组）——灰度
   打印下靠线型和标记区分，不只靠颜色。

数据
----
合成数据（固定 seed）：(a) 双序列时序；(b) 散点 + 线性拟合；(c) 五方案柱状；
(d) 直方图 + 正态拟合曲线（解析公式，不需要 scipy）。

产出
----
    utils/figkit/_out/figkit_demo4_multipanel.{png,pdf,svg}

运行
----
    python utils/figkit/figkit_demo4_multipanel.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

try:                                     # 包内运行：python -m utils.figkit.xxx
    from ..plot_style import next_style, save_pub, style_plot
except ImportError:                      # 直跑回退：python utils/figkit/xxx.py
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from utils.plot_style import next_style, save_pub, style_plot

save_fig = save_pub                      # plot_style v2 三格式出口（PNG+PDF+SVG）

# ============ 数据区 ============
SEED = 20260922
N_TIME = 12                              # (a) 时序长度
N_SCAT = 40                              # (b) 散点个数
N_HIST = 400                             # (d) 直方图样本量
BAR_LABELS = ["M1", "M2", "M3", "M4", "M5"]               # (c) 五个方案
BAR_VALUES = np.array([0.71, 0.83, 0.62, 0.90, 0.77])
TRUE_SLOPE, TRUE_INTERCEPT = 2.30, 5.0   # (b) 真值（用于对照估计精度）

OUT_DIR = Path(__file__).resolve().parent / "_out"
FIG_NAME = "figkit_demo4_multipanel"


def gauss(x, mu, sigma):
    """正态密度解析式（避免为一根拟合曲线引入 scipy 依赖）。"""
    return np.exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / (sigma * np.sqrt(2 * np.pi))


def panel_letter(ax, letter):
    """轴外左上角面板标号（clip_on=False：允许画到轴外，tight_layout 会预留空间）。"""
    ax.text(-0.17, 1.05, f"({letter})", transform=ax.transAxes,
            fontsize=10.5, fontweight="bold", va="bottom", ha="left", clip_on=False)


def main():
    style_plot("mcm")                    # 英文图取美赛盒式风格
    rng = np.random.default_rng(SEED)

    # ---- (a) 双序列时序 ----
    t = np.arange(N_TIME)
    # 两条不同斜率的趋势线：Proposed 起点低、终点反超（示意「改进方法随时间体现优势」）
    series = [30 + 1.8 * t + rng.normal(0, 1.6, N_TIME),
              26 + 2.4 * t + rng.normal(0, 1.6, N_TIME)]
    series_lbl = ["Baseline", "Proposed"]

    # ---- (b) 散点 + 线性拟合 ----
    xs = rng.uniform(0, 10, N_SCAT)
    ys = TRUE_SLOPE * xs + TRUE_INTERCEPT + rng.normal(0, 2.6, N_SCAT)
    slope, intercept = np.polyfit(xs, ys, 1)
    resid = ys - (slope * xs + intercept)
    ss_res = float((resid ** 2).sum())
    ss_tot = float(((ys - ys.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot

    # ---- (d) 直方图样本 ----
    samp = rng.normal(50.0, 6.0, N_HIST)

    fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.6))
    axa, axb, axc, axd = axes.ravel()

    # ======== (a) 趋势 ========
    for i, (y, lb) in enumerate(zip(series, series_lbl)):
        c, ls, mk = next_style(i)        # 染色+线型+标记三元组，灰度安全
        axa.plot(t, y, color=c, linestyle=ls, marker=mk, markersize=3.6,
                 linewidth=1.3, label=lb, markeredgewidth=0)
    axa.set_xlabel("Time step (month)")
    axa.set_ylabel("Output (a.u.)")
    axa.legend(loc="upper left", fontsize=8)
    panel_letter(axa, "a")

    # ======== (b) 拟合 ========
    axb.scatter(xs, ys, s=14, facecolor="#1F4E79", edgecolor="white",
                linewidth=0.4, alpha=0.85, label="Observations")
    xfit = np.linspace(0, 10, 100)
    axb.plot(xfit, slope * xfit + intercept, color="#C0504D", linewidth=1.6,
             label="Least-squares fit")
    axb.text(0.05, 0.94,
             f"y = {slope:.2f}x + {intercept:.2f}\n$R^2$ = {r2:.4f}",
             transform=axb.transAxes, va="top", ha="left", fontsize=8.5)
    axb.set_xlabel("Predictor x")
    axb.set_ylabel("Response y")
    axb.legend(loc="lower right", fontsize=8)
    panel_letter(axb, "b")

    # ======== (c) 对比柱 ========
    xpos = np.arange(len(BAR_LABELS))
    axc.bar(xpos, BAR_VALUES, width=0.62, color="#2E7D32",
            edgecolor="black", linewidth=0.7)
    for xi, v in zip(xpos, BAR_VALUES):
        axc.text(xi, v + 0.018, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
    axc.set_xticks(xpos)
    axc.set_xticklabels(BAR_LABELS)
    axc.set_xlabel("Candidate method")
    axc.set_ylabel("Score (-)")
    axc.set_ylim(0, float(BAR_VALUES.max()) * 1.18)
    panel_letter(axc, "c")

    # ======== (d) 分布 ========
    mu, sd = float(samp.mean()), float(samp.std(ddof=1))
    axd.hist(samp, bins=22, density=True, color="#A9B7C6",
             edgecolor="black", linewidth=0.6, label=f"Sample (n = {N_HIST})")
    xg = np.linspace(samp.min() - 4, samp.max() + 4, 300)
    axd.plot(xg, gauss(xg, mu, sd), color="#1F4E79", linewidth=1.6,
             label=f"Normal fit ($\\mu$={mu:.1f}, $\\sigma$={sd:.1f})")
    axd.set_xlabel("Value (units)")
    axd.set_ylabel("Density (-)")
    axd.legend(loc="upper left", fontsize=8)
    panel_letter(axd, "d")

    fig.tight_layout(rect=(0, 0, 1, 0.97))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(OUT_DIR / FIG_NAME))

    # ---------- 关键数值 ----------
    print(f"[合成数据] seed={SEED}｜(a) {N_TIME} 期 x2 序列｜(b) {N_SCAT} 点｜"
          f"(c) {len(BAR_LABELS)} 方案｜(d) n={N_HIST}")
    print(f"[a] 终点值 Baseline={series[0][-1]:.2f} / Proposed={series[1][-1]:.2f}；"
          f"Proposed 领先 {series[1][-1] - series[0][-1]:+.2f}")
    print(f"[b] 估计 y = {slope:.4f}x + {intercept:.4f}（真值 {TRUE_SLOPE}/{TRUE_INTERCEPT}）"
          f"｜R²={r2:.5f}｜残差 SD={resid.std(ddof=1):.3f}")
    print(f"[c] 最优 {BAR_LABELS[int(BAR_VALUES.argmax())]}={BAR_VALUES.max():.2f}｜"
          f"最劣 {BAR_LABELS[int(BAR_VALUES.argmin())]}={BAR_VALUES.min():.2f}｜"
          f"极差 {BAR_VALUES.max() - BAR_VALUES.min():.2f}")
    print(f"[d] 样本 μ={mu:.3f} σ={sd:.3f}｜偏度 {float(((samp - mu) ** 3).mean() / sd ** 3):+.3f}"
          f"（|偏度|<0.5 可视为对称）")
    print("[提示] 面板标号 (a)-(d) 可在图注里引用；线条三元组取 next_style(i) 保灰度可辨")


if __name__ == "__main__":
    main()
