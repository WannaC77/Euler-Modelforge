"""Logistic 阻滞增长模型拟合与预测模板（给定观测数据 → 估计 r 与 K）。

适用场景：种群/销量/用户数/传播量的"S 型增长"观测数据（国赛、美赛预测与拟合题常见）。
模型：dP/dt = r·P·(1 − P/K)，解析解 P(t) = K / [1 + (K/P0 − 1)·e^(−rt)]。
方法：① 差分最小二乘粗估 r、K（把离散增长方程 y=ΔP/P 对 P 回归）；
      ② 解析解非线性最小二乘精修（curve_fit），输出拟合误差与未来预测。
输入格式：两个等长一维数组 t（时刻）与 P（观测值，P>0）。
输出格式：控制台打印 差分粗估 / 精修 r±std、K±std、RMSE、未来预测、达 K 95% 时间。
依赖：numpy、scipy、matplotlib。
"""
import os
import sys

import numpy as np
from scipy.optimize import curve_fit

# ===== 观测数据（改这里换数据：t=观测时刻, P=观测值）=====
# 示例用"真值 r=0.45, K=1000, P0=10"的解析曲线 + 3% 随机噪声生成 41 个观测点
RNG = np.random.default_rng(42)          # 固定随机种子，保证可复现
TRUE_R, TRUE_K, P0_TRUE = 0.45, 1000.0, 10.0
T_MAX, HORIZON = 40, 5                    # 观测到第 40 天，向前预测 5 天


def logistic_curve(t, P0, r, K):
    """Logistic 解析解：P(t) = K / (1 + (K/P0 − 1)·e^(−r·t))。"""
    return K / (1 + (K / P0 - 1) * np.exp(-r * np.asarray(t)))


def make_synthetic_data(seed=42):
    """生成带噪声的观测序列（真实比赛里换成读入的数据）。返回 (t, P)。"""
    rng = np.random.default_rng(seed)
    t = np.arange(T_MAX + 1, dtype=float)
    P_true = logistic_curve(t, P0_TRUE, TRUE_R, TRUE_K)
    P = P_true * (1 + rng.normal(0, 0.03, len(t)))   # 乘性噪声 3%
    return t, np.maximum(P, 1.0)                      # 保证观测值恒正


def estimate_by_difference(t, P):
    """差分最小二乘粗估：离散化 ΔP/P ≈ r − (r/K)·P。
    把 y = ΔP/P 对 x = P 做一元线性回归: 截距 = r, 斜率 = −r/K。
    返回 (r_hat, K_hat)。"""
    x = P[:-1]                              # 用 t 时刻的 P 预测一步增长
    y = np.diff(P) / x                      # ΔP / P
    slope, intercept = np.polyfit(x, y, 1)
    r_hat = intercept
    K_hat = -intercept / slope              # K = r / (r/K)
    return r_hat, K_hat


def refine_by_curve_fit(t, P, r0, K0):
    """非线性最小二乘精修：直接对解析解拟合 3 参数 (P0, r, K)。
    返回 (popt, perr)，perr 为各参数标准误。K 下界取观测最大的一半以容忍噪声。"""
    K_lb = max(P) * 0.5
    popt, pcov = curve_fit(logistic_curve, t, P,
                           p0=[P[0], r0, max(K0, max(P))],
                           bounds=([0, 0, K_lb],
                                   [np.inf, 100.0, np.inf]), maxfev=20000)
    return popt, np.sqrt(np.diag(pcov))


def fit_rmse_r2(t, P, P0, r, K):
    """拟合优度：RMSE 与 R²（相对"取均值"的基准模型）。"""
    pred = logistic_curve(t, P0, r, K)
    rmse = float(np.sqrt(np.mean((P - pred) ** 2)))
    r2 = 1 - np.sum((P - pred) ** 2) / np.sum((P - P.mean()) ** 2)
    return rmse, r2, pred


if __name__ == "__main__":
    t, P = make_synthetic_data()
    print("=" * 62)
    print(f"【Logistic 增长模型拟合】观测 {len(t)} 个点, t = 0~{T_MAX} 天")
    print(f"  (示例数据由真值 r = {TRUE_R}, K = {TRUE_K} 加 3% 噪声生成, 便于对照)")

    # 第 1 步：差分最小二乘粗估
    r1, K1 = estimate_by_difference(t, P)
    print(f"\n[1] 差分最小二乘粗估: r ≈ {r1:.3f}, K ≈ {K1:.0f}")

    # 第 2 步：解析解精修
    (P0f, rf, Kf), (eP0, er, eK) = refine_by_curve_fit(t, P, r1, K1)
    print(f"[2] 非线性最小二乘精修:")
    print(f"    P0 = {P0f:.2f} ± {eP0:.2f}")
    print(f"    r  = {rf:.4f} ± {er:.4f}   (真值 {TRUE_R})")
    print(f"    K  = {Kf:.1f} ± {eK:.1f}   (真值 {TRUE_K})")

    # 第 3 步：拟合优度 + 未来预测
    rmse, r2, pred = fit_rmse_r2(t, P, P0f, rf, Kf)
    print(f"[3] 拟合优度: RMSE = {rmse:.2f}, R² = {r2:.4f}")
    t_pred = float(T_MAX + HORIZON)
    P_future = logistic_curve(t_pred, P0f, rf, Kf)
    print(f"    未来预测: 第 {t_pred:.0f} 天 P = {P_future:.0f} "
          f"(观测最后一天 P = {P[-1]:.0f})")
    t95 = np.log(19 * (Kf / P0f - 1)) / rf      # 解 P(t)=0.95K 的时刻
    print(f"    达环境容量 95% (K·0.95 ≈ {Kf * 0.95:.0f}) 约在第 {t95:.0f} 天")

    # 画图：观测点 + 拟合曲线 + 预测段 + K 渐近线
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils.plot_style import save_fig, style_plot

    style_plot()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    tt = np.linspace(0, t_pred, 400)
    curve = logistic_curve(tt, P0f, rf, Kf)
    ax.plot(t, P, "o", ms=4, label="Observed data", zorder=3)
    ax.plot(tt, curve, lw=2, label="Fitted logistic")
    ax.axvspan(T_MAX, t_pred, color="gray", alpha=0.15, label="Forecast region")
    ax.axhline(Kf, color="C3", ls="--", lw=1.2, label=f"K = {Kf:.0f}")
    ax.annotate(f"P({t_pred:.0f}) = {P_future:.0f}", xy=(t_pred, P_future),
                xytext=(t_pred - 16, P_future * 0.55),
                arrowprops=dict(arrowstyle="->", lw=1))
    ax.set_xlabel("Time (day)"); ax.set_ylabel("Population P(t)")
    ax.legend(); ax.set_title(f"Logistic growth fit (r = {rf:.3f}, K = {Kf:.0f})")
    save_fig(fig, os.path.join(os.path.dirname(__file__), "..", "data", "logistic_growth.png"))

    print(f"\n[Logistic] PASS: 差分粗估 + 曲线精修, r/K 估计接近真值 "
          f"(|Δr| = {abs(rf - TRUE_R):.4f}, |ΔK| = {abs(Kf - TRUE_K):.0f})")
