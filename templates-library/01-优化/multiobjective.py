"""多目标优化模板 — 加权求和法（Weighted Sum Method）。

适用场景：同时优化两个以上相互冲突的目标（成本 vs 性能、利润 vs 风险、
         精度 vs 速度、碳排放 vs 经济性等），需在目标间做权衡或画 Pareto 前沿。
方法原理：把多目标 f1, f2, ... 用权重线性加权成单目标
         min  w1*f1(x) + w2*f2(x) + ...   (wi >= 0, 和为 1)，
         每给一组权重解一次单目标 NLP，即可得 Pareto 前沿上的一个点；
         扫过所有权重 -> 完整 Pareto 前沿，供决策者挑选折中方案。
输入格式：定义目标函数 f1(x)/f2(x)、决策变量边界 bounds、权重扫描点数。
输出：各权重下的最优解与目标值（表格摘要）、Pareto 前沿图（png 保存）。
依赖：numpy + scipy + matplotlib（requirements.txt 均已含）。

比赛用法：
    1. 改写下方 obj1 / obj2 与 bounds 为你的多目标问题
    2. 运行 python multiobjective.py
    3. 论文可用图 + 表中"拐点/端点"作为推荐折中方案
"""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")                       # 无显示环境可跑；本地想弹窗可改 "TkAgg"
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy.optimize import minimize

# 中文字体设置：优先 Windows 自带黑体/雅黑，避免图上中文变方块
_zh_font = None
for _f in ("Microsoft YaHei", "SimHei", "SimSun"):
    if any(_f == ft.name for ft in font_manager.fontManager.ttflist):
        _zh_font = _f
        break
if _zh_font:
    plt.rcParams["font.sans-serif"] = [_zh_font, "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False   # 正常显示负号

# ============ 问题参数（改这里即可）============
# 示例：双目标，x = (x0, x1)，两目标各自想靠近不同端点，天然冲突
#   f1: 距点 (1,-1) 越近越小（最小值 1）;  f2: 距点 (-1,1) 越近越小（最小值 1）
N_WEIGHTS = 101          # 权重扫描点数（越大 Pareto 前沿越密）
X0 = np.array([0.0, 0.0])   # 每个子问题的初值
BOUNDS = [(-2.0, 2.0), (-2.0, 2.0)]   # 决策变量边界
OUT_PNG = "multiobjective_pareto.png"   # 出图文件名（存到本文件同目录）


def obj1(x):
    """目标 1（越小越好）。"""
    return (x[0] - 1.0) ** 2 + (x[1] + 1.0) ** 2 + 1.0


def obj2(x):
    """目标 2（越小越好）。"""
    return (x[0] + 1.0) ** 2 + (x[1] - 1.0) ** 2 + 1.0
# ==============================================


def solve_weighted(w1, w2):
    """给定权重 (w1, w2)，解单目标 min w1*f1 + w2*f2，返回 (x, f1, f2)。"""
    def obj_w(x):
        return w1 * obj1(x) + w2 * obj2(x)
    res = minimize(obj_w, X0, method="L-BFGS-B", bounds=BOUNDS)
    if not res.success:
        print(f"  [警告] 权重 ({w1:.2f},{w2:.2f}) 未收敛: {res.message}")
    x = res.x
    return x, obj1(x), obj2(x)


if __name__ == "__main__":
    print(f"加权求和法: 双目标, 权重扫描 {N_WEIGHTS} 点, 决策变量 x ∈ {BOUNDS}")

    # 扫描权重 w1 从 0 -> 1（w2 = 1 - w1），收集 Pareto 前沿点
    ws = np.linspace(0.0, 1.0, N_WEIGHTS)
    pareto_x, pareto_f1, pareto_f2 = [], [], []
    for w1 in ws:
        x, f1, f2 = solve_weighted(w1, 1.0 - w1)
        pareto_x.append(x)
        pareto_f1.append(f1)
        pareto_f2.append(f2)
    pareto_x = np.array(pareto_x)
    pareto_f1 = np.array(pareto_f1)
    pareto_f2 = np.array(pareto_f2)

    # 数值结果摘要：端点（只优化单目标）与若干折中点
    print("\n[结果摘要] w1 权重 | 最优 x | 目标 f1 | 目标 f2")
    for k in [0, 10, 50, 90, N_WEIGHTS - 1]:
        print(f"  w1={ws[k]:.2f} | x={np.round(pareto_x[k], 3)} "
              f"| f1={pareto_f1[k]:.4f} | f2={pareto_f2[k]:.4f}")
    print(f"\n[单目标极值] 只优化 f1 (w1=1): f1 最小 = {pareto_f1[-1]:.4f}，此时 f2 = {pareto_f2[-1]:.4f}")
    print(f"              只优化 f2 (w1=0): f2 最小 = {pareto_f2[0]:.4f}，此时 f1 = {pareto_f1[0]:.4f}")
    print(f"  Pareto 前沿共 {len(pareto_f1)} 个点，中间点即两目标折中（如 w1=0.5 处 f1=f2=3.0）")

    # 画 Pareto 前沿（目标空间 f1-f2 曲线，越靠近原点越好）
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(pareto_f1, pareto_f2, "o-", ms=3, color="tab:blue", label="Pareto 前沿")
    ax.plot(pareto_f1[0], pareto_f2[0], "s", color="tab:red", label="只优化 f1")
    ax.plot(pareto_f1[-1], pareto_f2[-1], "^", color="tab:green", label="只优化 f2")
    ax.set_xlabel("目标 f1（越小越好）")
    ax.set_ylabel("目标 f2（越小越好）")
    ax.set_title("加权求和法得到的 Pareto 前沿")
    ax.legend()
    ax.grid(alpha=0.3)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUT_PNG)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\n[图] Pareto 前沿已保存: {out_path}  PASS")
