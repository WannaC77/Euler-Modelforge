"""微分方程模型：传染病 SIR/SEIR 求解模板。

适用场景：传播/扩散/动力学类问题（美赛 E 环境、国赛 A 连续题；传染病、舆情、创新扩散都可用 SIR 框架）。
流程：写 ODE → scipy 数值求解 → 画图 → 参数敏感性（扫 beta/gamma）。

依赖：scipy。
"""
import numpy as np
from scipy.integrate import solve_ivp


def sir(t, y, beta, gamma):
    """SIR 模型右端。y = [S, I, R]。"""
    S, I, R = y
    dS = -beta * S * I / (S + I + R)
    dI = beta * S * I / (S + I + R) - gamma * I
    dR = gamma * I
    return [dS, dI, dR]


def solve_sir(N=1000, I0=1, R0=0, beta=0.3, gamma=0.1, days=100):
    """求解 SIR。返回 (t, S, I, R)。"""
    y0 = [N - I0 - R0, I0, R0]
    t_span = (0, days)
    t_eval = np.linspace(0, days, days + 1)
    sol = solve_ivp(sir, t_span, y0, args=(beta, gamma), t_eval=t_eval, method="RK45")
    return sol.t, sol.y[0], sol.y[1], sol.y[2]


def peak_info(t, I):
    """报告感染峰值时刻与峰值人数。"""
    idx = np.argmax(I)
    return t[idx], I[idx]


if __name__ == "__main__":
    N, beta, gamma = 10000, 0.35, 0.12
    t, S, I, R = solve_sir(N=N, beta=beta, gamma=gamma)

    tp, ip = peak_info(t, I)
    print(f"[SIR] N={N}, beta={beta}, gamma={gamma}")
    print(f"  感染峰值: t={tp:.0f} 天, 峰值感染 {ip:.0f} 人")
    print(f"  终局: 感染总数 {N - S[-1]:.0f} (感染率 {(N - S[-1])/N*100:.1f}%)")

    # 敏感性: 扫描 beta
    print("\n[敏感性分析] beta 变化对感染峰值的影响:")
    for b in [0.25, 0.30, 0.35, 0.40, 0.45]:
        _, _, I_b, _ = solve_sir(N=N, beta=b, gamma=gamma)
        print(f"  beta={b:.2f}: 峰值 {I_b.max():.0f} 人")

    import matplotlib.pyplot as plt
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils.plot_style import style_plot, save_fig
    style_plot()
    fig, ax = plt.subplots()
    ax.plot(t, S, label="Susceptible")
    ax.plot(t, I, label="Infected")
    ax.plot(t, R, label="Recovered")
    ax.set_xlabel("Time (day)"); ax.set_ylabel("Population"); ax.legend()
    save_fig(fig, os.path.join(os.path.dirname(__file__), "..", "data", "sir.png"))
