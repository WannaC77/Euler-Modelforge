"""通用 ODE 系统求解模板（用户写右端函数即可用）。

适用场景：任何"随时间演化"的连续系统——传染病、种群、化学反应、物资流、物理过程等。
用法三步：
    1) 定义右端函数  def rhs(t, y, *params): ...（y 是状态向量，返回各分量的导数）；
    2) 调用 sol = solve_ode(rhs, y0, t_span, t_eval, args=(参数...))；
    3) 画时序图 / 相图。
输入格式：右端函数、初值向量 y0、时间范围 (t0, t1)。
输出格式：数值解 t 与状态矩阵 Y；控制台打印关键指标。
依赖：scipy、numpy、matplotlib。
"""
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import find_peaks


def solve_ode(rhs, y0, t_span, t_eval=None, args=(), method="RK45"):
    """通用 ODE 求解器：包装 scipy.solve_ivp。
    rhs(t, y, *args) 为用户右端函数；返回 (t, Y)，Y 形状 (变量数 × 时间点数)。"""
    sol = solve_ivp(rhs, t_span, np.asarray(y0, float), args=args,
                    t_eval=t_eval, method=method, rtol=1e-6, atol=1e-9)
    return sol.t, sol.y


def lotka_volterra(t, y, a, b, c, d):
    """Lotka-Volterra 捕食-食饵模型右端。y = [x 食饵, z 捕食者]。
    dx/dt = a x − b x z      （食饵：无捕食时指数增长 a，被捕食损失 b x z）
    dz/dt = c x z − d z      （捕食者：无食饵时指数死亡 d，捕食转化收益 c x z）
    非平凡平衡点: (x*, z*) = (d/c, a/b)。"""
    x, z = y
    return [a * x - b * x * z,
            c * x * z - d * z]


def plot_time_series(t, Y, labels, path):
    """画时序图：每条状态分量一条曲线（Y: 变量数 × 时间点数）。"""
    import matplotlib.pyplot as plt
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils.plot_style import save_fig, style_plot

    style_plot()
    fig, ax = plt.subplots()
    for row, lab in zip(Y, labels):
        ax.plot(t, row, label=lab, lw=2)
    ax.set_xlabel("Time"); ax.set_ylabel("Population size")
    ax.legend(); ax.set_title("Time series")
    save_fig(fig, path)


def plot_phase(Y, labels, path):
    """画相图：两变量系统的 y1−y2 相平面轨迹（起点用 ● 标注）。"""
    import matplotlib.pyplot as plt
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils.plot_style import save_fig, style_plot

    style_plot()
    fig, ax = plt.subplots()
    ax.plot(Y[0], Y[1], lw=1.8, label="trajectory")
    ax.plot(Y[0, 0], Y[1, 0], "o", ms=7, label="start")
    ax.set_xlabel(labels[0]); ax.set_ylabel(labels[1])
    ax.legend(); ax.set_title("Phase portrait")
    save_fig(fig, path)


if __name__ == "__main__":
    # ===== 示例参数（改这里换数据：想算自己的系统 → 仿照 lotka_volterra 写右端函数）=====
    a, b, c, d = 1.1, 0.4, 0.1, 0.4      # LV 参数（改这里）
    y0 = [6.0, 4.0]                       # 初值: [食饵 x0, 捕食者 z0]
    t0, t1 = 0.0, 60.0                    # 模拟时间范围
    n_pts = 601

    t = np.linspace(t0, t1, n_pts)
    t_sol, Y = solve_ode(lotka_volterra, y0, (t0, t1), t_eval=t,
                         args=(a, b, c, d))
    x, z = Y[0], Y[1]                     # x: 食饵, z: 捕食者

    # 理论结果对照：非平凡平衡点即时间平均
    x_star, z_star = d / c, a / b
    print("=" * 62)
    print("【Lotka-Volterra 捕食者-食饵】a=1.1, b=0.4, c=0.1, d=0.4, "
          f"初值 x0=6, z0=4, 模拟 {t1:.0f} 单位时间")
    print(f"  理论平衡点/时间均值: 食饵 x* = d/c = {x_star:.2f}, "
          f"捕食者 z* = a/b = {z_star:.2f}")
    print(f"  数值均值:            食饵 x̄ = {x.mean():.2f}, 捕食者 z̄ = {z.mean():.2f}")
    print(f"  食饵  范围: [{x.min():.2f}, {x.max():.2f}], 终值 {x[-1]:.2f}")
    print(f"  捕食者范围: [{z.min():.2f}, {z.max():.2f}], 终值 {z[-1]:.2f}")

    # 用捕食者峰值间隔估计振荡周期
    peaks, _ = find_peaks(z)
    if len(peaks) >= 2:
        periods = np.diff(t_sol[peaks])
        print(f"  捕食者出现 {len(peaks)} 个峰值, 平均周期 ≈ {periods.mean():.2f} 单位时间")
    print("  验证: 曲线不发散且周期性振荡 → 数值解合理")

    # 画图：左时序图 + 右相图（同一 figure 双面板）
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils.plot_style import save_fig, style_plot

    style_plot()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.plot(t, x, label="Prey x", lw=2)
    ax1.plot(t, z, label="Predator z", lw=2)
    ax1.set_xlabel("Time"); ax1.set_ylabel("Population size")
    ax1.legend(); ax1.set_title("Time series")
    ax2.plot(x, z, lw=1.8, label="trajectory")
    ax2.plot(x[0], z[0], "o", ms=7, label="start")
    ax2.set_xlabel("Prey x"); ax2.set_ylabel("Predator z")
    ax2.legend(); ax2.set_title("Phase portrait")
    fig.tight_layout()
    save_fig(fig, os.path.join(os.path.dirname(__file__), "..", "data", "ode_general.png"))
