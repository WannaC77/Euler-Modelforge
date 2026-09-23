"""微分方程模型：SEIR 传染病模型（含潜伏期 E 与死亡 D）。

适用场景：传染病/舆情/创新扩散的传播动力学（美赛 E、国赛 A 连续题）。
模型：S→E(潜伏,σ)→I(发病)→R(康复,γ) 或 D(死亡,μ)；人群总数 N 守恒。
输入格式：人群规模 N、初始 E0/I0、传播率 beta、潜伏转阳率 sigma、
        康复率 gamma、死亡率 mu（单位均为 1/天），改下方常量区即可。
输出格式：控制台打印 基本再生数、潜伏/感染峰值与时刻、终局各仓室人数、病死率。
依赖：scipy、numpy、matplotlib。
"""
import os
import sys

# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy", "scipy", "matplotlib"):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np
from scipy.integrate import solve_ivp

# ===== 模型参数（改这里换数据/情景）=====
N = 100000          # 总人口
E0 = 20             # 初始潜伏者（输入病例）
I0 = 5              # 初始感染者
BETA = 0.45         # 传染率：每个感染者每天传染人数（越大传播越快）
SIGMA = 1 / 5.2     # 潜伏转阳率：平均潜伏期 5.2 天 → σ≈0.192/天
GAMMA = 1 / 7.0     # 康复率：平均病程 7 天 → γ≈0.143/天
MU = 0.005          # 因病死亡率：感染者每天死亡概率 μ=0.005
DAYS = 200          # 模拟天数


def seird(t, y, beta, sigma, gamma, mu):
    """SEIRD 模型右端函数。y = [S, E, I, R, D]。"""
    S, E, I, R, D = y
    n = S + E + I + R + D            # 守恒总量（求解中保持常数）
    dS = -beta * S * I / n
    dE = beta * S * I / n - sigma * E
    dI = sigma * E - gamma * I - mu * I
    dR = gamma * I
    dD = mu * I
    return [dS, dE, dI, dR, dD]


def solve_seir(N=N, E0=E0, I0=I0, beta=BETA, sigma=SIGMA,
               gamma=GAMMA, mu=MU, days=DAYS):
    """求解 SEIRD，返回 (t, S, E, I, R, D) 曲线。"""
    y0 = [N - E0 - I0, E0, I0, 0, 0]
    t_eval = np.linspace(0, days, days + 1)
    sol = solve_ivp(seird, (0, days), y0, args=(beta, sigma, gamma, mu),
                    t_eval=t_eval, method="RK45", rtol=1e-6, atol=1e-9)
    return sol.t, sol.y[0], sol.y[1], sol.y[2], sol.y[3], sol.y[4]


def peak_info(t, curve):
    """报告曲线峰值时刻与峰值。返回 (峰值时刻, 峰值)。"""
    idx = int(np.argmax(curve))
    return t[idx], curve[idx]


if __name__ == "__main__":
    t, S, E, I, R, D = solve_seir()

    # 关键数值结果
    r0 = BETA / (GAMMA + MU)                     # 基本再生数
    tp_E, pk_E = peak_info(t, E)
    tp_I, pk_I = peak_info(t, I)
    total_infected = R[-1] + D[-1]               # 全程累计感染者（已康复+已死亡）
    cfr = D[-1] / total_infected * 100           # 病死率
    print("=" * 62)
    print(f"【SEIR 传染病模型】N = {N}, β = {BETA}/天, 潜伏期 1/σ = {1 / SIGMA:.1f} 天, "
          f"病程 1/γ = {1 / GAMMA:.1f} 天")
    print(f"  基本再生数 R0 = β/(γ+μ) = {r0:.2f} (>1 才会暴发)")
    print(f"  潜伏峰值: t = {tp_E:.0f} 天, E = {pk_E:.0f} 人")
    print(f"  感染峰值: t = {tp_I:.0f} 天, I = {pk_I:.0f} 人")
    print(f"  终局 (t = {t[-1]:.0f} 天):")
    print(f"    S(未感染) = {S[-1]:.0f}, E = {E[-1]:.0f}, I = {I[-1]:.0f}, "
          f"R(康复) = {R[-1]:.0f}, D(死亡) = {D[-1]:.0f}")
    print(f"    累计感染 = {total_infected:.0f} 人 (感染率 {total_infected / N * 100:.1f}%), "
          f"病死率 = {cfr:.2f}%")
    print(f"    守恒检查 S+E+I+R+D = {S[-1] + E[-1] + I[-1] + R[-1] + D[-1]:.6f} (应 = {N})")

    # 敏感性：扫描 beta（对应防控力度/病毒毒株差异），比较感染峰值与累计感染
    print("\n[敏感性分析] β 对疫情结局的影响:")
    for b in [0.30, 0.45, 0.60]:
        _, Sb, Eb, Ib, Rb, Db = solve_seir(beta=b)
        print(f"  β = {b:.2f}: 峰值 I = {Ib.max():.0f} 人 (第 {t[np.argmax(Ib)]:.0f} 天), "
              f"累计感染率 = {(Rb[-1] + Db[-1]) / N * 100:.1f}%")

    # 画图：五条仓室曲线 + 标注感染峰值
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils.plot_style import save_fig, style_plot

    style_plot()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    # 图内文字用英文（DejaVu 无中文字形，与 sir.py 模板一致，避免缺字告警）
    ax.plot(t, S, label="Susceptible")
    ax.plot(t, E, label="Exposed")
    ax.plot(t, I, label="Infectious", lw=2.2)
    ax.plot(t, R, label="Recovered")
    ax.plot(t, D, label="Deceased", lw=2.0)
    ax.axvline(tp_I, color="gray", ls="--", lw=1)
    ax.plot(tp_I, pk_I, "o", ms=6)
    ax.annotate(f"Peak I = {pk_I:.0f} (day {tp_I:.0f})", xy=(tp_I, pk_I),
                xytext=(tp_I + 10, pk_I * 0.85))
    ax.set_xlabel("Time (day)"); ax.set_ylabel("Population")
    ax.legend(ncol=3)
    ax.set_title(f"SEIR model (R0 = {r0:.2f})")
    save_fig(fig, os.path.join(os.path.dirname(__file__), "..", "data", "seir.png"))
