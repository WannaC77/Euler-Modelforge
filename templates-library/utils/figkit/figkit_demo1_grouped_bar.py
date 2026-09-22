# -*- coding: utf-8 -*-
"""figkit 样例 1 —— 对比柱状图（两组并排 + 误差棒 + 显著性标注）。

适用场景
--------
「我们的方法 vs 基线」在各案例/指标上的对比图——论文实验章第一张图的常用型。
本样例含三件套：并排柱（分组对比）+ 误差棒（重复实验离散度）+ 显著性星号
（Welch t 检验，真算不假标）。柱面另加斜纹填充，保证黑白打印仍可区分。

数据
----
合成数据：4 个案例 × 2 组 × 5 次重复，固定 seed（每次跑结果完全一致）。
显著性用 scipy 的 Welch t 检验（不等方差），按 p 值标 ***/**/*/n.s.。

产出
----
    utils/figkit/_out/figkit_demo1_grouped_bar.{png,pdf,svg}

运行
----
    python utils/figkit/figkit_demo1_grouped_bar.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# 风格与三格式导出统一走 utils/plot_style（相对导入：本文件属 utils.figkit 包）
try:                                     # 包内运行：python -m utils.figkit.xxx
    from ..plot_style import PALETTE, save_pub, style_plot
except ImportError:                      # 直跑回退：python utils/figkit/xxx.py
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from utils.plot_style import PALETTE, save_pub, style_plot

# plot_style v2 的三格式出口叫 save_pub（PNG+PDF+SVG）；v1 的同名 save_fig 只出单张位图
save_fig = save_pub

# ============ 数据区（换成自己题目的数据即可）============
SEED = 20260922                          # 固定 seed：结果可复现
N_REP = 5                                # 每格重复次数（误差棒按 SEM = SD/√n）
CASES = ["Case A", "Case B", "Case C", "Case D"]
GROUPS = ["Baseline", "Proposed"]
GROUP_MEAN = {                           # 各案例的组均值
    "Baseline": np.array([62.0, 55.0, 71.0, 64.0]),
    "Proposed": np.array([66.6, 64.3, 73.6, 75.4]),
}
GROUP_SD = {"Baseline": 3.2, "Proposed": 3.6}     # 组内标准差
HATCHES = ["", "///"]                    # 斜纹填充：灰度/黑白打印下两组仍可区分

OUT_DIR = Path(__file__).resolve().parent / "_out"
FIG_NAME = "figkit_demo1_grouped_bar"


def make_data(seed=SEED):
    """合成重复实验数据。返回 {组名: (n_cases, n_rep) 数组}。"""
    rng = np.random.default_rng(seed)
    # loc 需要 (n_cases, 1) 才能与 size=(n_cases, n_rep) 广播成「每案例 5 次重复」
    return {g: rng.normal(np.asarray(GROUP_MEAN[g])[:, None], GROUP_SD[g],
                          size=(len(CASES), N_REP))
            for g in GROUPS}


def stars(p):
    """p 值 → 显著性星号（论文惯例）。"""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "n.s."


def sig_bracket(ax, x1, x2, y, h, text):
    """在 x1..x2 之间画显著性括号 + 星号（clip_on=False 允许压出轴外）。"""
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y],
            lw=1.0, c="black", clip_on=False, zorder=4)
    ax.text((x1 + x2) / 2, y + h, text, ha="center", va="bottom",
            fontsize=8.5, clip_on=False)


def main():
    style_plot("mcm")                    # 英文图取美赛盒式风格（改中文标签请用 "cumcm"）
    data = make_data()

    mean = {g: data[g].mean(axis=1) for g in GROUPS}
    sd = {g: data[g].std(axis=1, ddof=1) for g in GROUPS}
    sem = {g: sd[g] / np.sqrt(N_REP) for g in GROUPS}
    pvals = [stats.ttest_ind(data["Baseline"][c], data["Proposed"][c],
                             equal_var=False).pvalue for c in range(len(CASES))]

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    x = np.arange(len(CASES))
    bw = 0.34
    for gi, g in enumerate(GROUPS):
        ax.bar(x + (gi - 0.5) * bw, mean[g], bw,
               yerr=sem[g], capsize=3,
               color=PALETTE["cumcm"][gi], edgecolor="black", linewidth=0.7,
               hatch=HATCHES[gi], label=g,
               error_kw=dict(lw=0.9, ecolor="#333333", capthick=0.9))

    # 显著性括号：高度取本案例柱顶上方留白处
    for c in range(len(CASES)):
        top = max(mean["Baseline"][c] + sem["Baseline"][c],
                  mean["Proposed"][c] + sem["Proposed"][c])
        sig_bracket(ax, x[c] - bw / 2, x[c] + bw / 2, top + 0.8, 1.6, stars(pvals[c]))

    ax.set_xticks(x)
    ax.set_xticklabels(CASES)
    ax.set_xlabel("Benchmark case")
    ax.set_ylabel("Performance score (a.u.)")
    ax.set_title("Grouped comparison with error bars and significance", pad=12)
    ax.set_ylim(0, float(max(mean["Proposed"] + sem["Proposed"])) * 1.24)
    ax.legend(loc="upper left", frameon=True, ncol=2, fontsize=8.5)
    # 显著性判读口径写进图内脚注，读者不用翻正文
    ax.text(0.0, -0.16, "Error bars: SEM (n = %d). Welch's t-test: "
                        "*** p<0.001, ** p<0.01, * p<0.05, n.s. not significant."
            % N_REP, transform=ax.transAxes, fontsize=7.5, va="top", ha="left")
    fig.tight_layout()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    save_fig(fig, str(OUT_DIR / FIG_NAME))

    # ---------- 关键数值 ----------
    print(f"[数据] {len(CASES)} 案例 x {len(GROUPS)} 组 x {N_REP} 次重复（seed={SEED}）")
    for c, name in enumerate(CASES):
        d = mean["Proposed"][c] - mean["Baseline"][c]
        print(f"  {name:<7} Baseline {mean['Baseline'][c]:6.2f}±{sd['Baseline'][c]:4.2f} | "
              f"Proposed {mean['Proposed'][c]:6.2f}±{sd['Proposed'][c]:4.2f} | "
              f"delta={d:+6.2f} | p={pvals[c]:.4f} {stars(pvals[c])}")
    ibest = int(np.argmin(pvals))
    print(f"[最显著] {CASES[ibest]}：delta={mean['Proposed'][ibest] - mean['Baseline'][ibest]:+.2f}, "
          f"p={pvals[ibest]:.4f} {stars(pvals[ibest])}")
    print(f"[提示] 柱色取 PALETTE['cumcm']（{PALETTE['cumcm'][0]} / {PALETTE['cumcm'][1]}）"
          f"，另加斜纹以保灰度可辨；灰度/色盲机检请跑 gray_cb_check.py")


if __name__ == "__main__":
    main()
