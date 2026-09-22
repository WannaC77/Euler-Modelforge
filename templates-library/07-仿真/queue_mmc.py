"""排队论模板（M/M/1 与 M/M/c 解析公式 + 服务台数决策）。

适用场景：服务系统容量设计、窗口/柜台/收费站数量优化（美赛 B/D、国赛 B）。
公式：M/M/c 用 Erlang-C 求等待概率，输出队长/等待时间/利用率。

输入：λ(到达率 人/时), μ(单台服务率 人/时), c(服务台数)。
输出：利用率 ρ、平均队长 Lq、平均等待 Wq、空闲概率 P0。
"""
import math


def mm1(lambda_, mu):
    """M/M/1：单服务台。返回指标 dict。ρ<1 才有稳态。"""
    rho = lambda_ / mu
    if rho >= 1:
        return {"有效": False, "原因": "ρ≥1 系统不稳定（到达率≥服务率）"}
    L = rho / (1 - rho)                 # 平均顾客数
    Lq = rho**2 / (1 - rho)             # 平均排队人数
    W = L / lambda_                     # 平均逗留时间
    Wq = Lq / lambda_                   # 平均等待时间
    P0 = 1 - rho                        # 空闲概率
    return {"有效": True, "ρ": rho, "L": L, "Lq": Lq, "W": W, "Wq": Wq, "P0": P0}


def erlang_c(c, rho):
    """Erlang-C 等待概率（M/M/c）。"""
    # P0
    s = sum((c * rho)**k / math.factorial(k) for k in range(c))
    s += (c * rho)**c / (math.factorial(c) * (1 - rho))
    P0 = 1 / s
    # C(c, rho) 等待概率
    Cw = (c * rho)**c / (math.factorial(c) * (1 - rho)) * P0
    return P0, Cw


def mmc(lambda_, mu, c):
    """M/M/c：多服务台。返回指标 dict。ρ<1 才有稳态。"""
    rho = lambda_ / (c * mu)
    if rho >= 1:
        return {"有效": False, "原因": "ρ≥1 系统不稳定"}
    P0, Cw = erlang_c(c, rho)
    Lq = Cw * rho / (1 - rho)
    Wq = Lq / lambda_
    W = Wq + 1 / mu
    L = Lq + lambda_ / mu
    return {"有效": True, "ρ": rho, "P0": P0, "Cw": Cw, "Lq": Lq, "L": L, "Wq": Wq, "W": W}


if __name__ == "__main__":
    lam, mu = 8.0, 10.0   # 到达 8 人/时，单台服务 10 人/时

    r1 = mm1(lam, mu)
    print(f"[M/M/1] λ={lam}, μ={mu}")
    if r1["有效"]:
        print(f"  利用率 ρ={r1['ρ']:.3f} | 平均队长 Lq={r1['Lq']:.2f} | "
              f"等待时间 Wq={r1['Wq']:.2f} 时 | 逗留 W={r1['W']:.2f} 时")

    print(f"\n[M/M/c] 服务台数决策（目标: 等待<0.1 时 且 利用率<0.8）:")
    for c in range(1, 5):
        r = mmc(lam, mu, c)
        if r["有效"]:
            ok = "✓" if r["Wq"] < 0.1 and r["ρ"] < 0.8 else " "
            print(f"  c={c}: ρ={r['ρ']:.3f} Lq={r['Lq']:.2f} Wq={r['Wq']:.3f} 时 {ok}")
        else:
            print(f"  c={c}: {r['原因']}")
