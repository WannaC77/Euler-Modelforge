"""指数平滑预测模板（Holt-Winters 三参数季节模型）。

适用场景：带「趋势 + 季节」成分的中短期时间序列预测（月度/季度数据），如销量、
客流量、发电量、吞吐量。是灰色预测(GM)和 ARIMA 之外的经典预测方法（国赛/美赛通用）。

模型：ExponentialSmoothing = 水平α + 趋势β + 季节γ 三参数（Holt-Winters），
      smoothing 参数由 statsmodels 内置优化自动确定（也可手工给定）。
输入：历史序列 y（一维 list/np.ndarray，等间隔、无缺失、长度 ≥ 2 个完整季节周期）；
      seasonal_periods 季节周期长度（月度 12 / 季度 4 / 周 7）。
输出：训练期内拟合值、拟合优度指标(RMSE/MAPE)、未来 n_pred 期预测值、平滑参数。
依赖：numpy、statsmodels（画图可选 matplotlib）。
⚠️ 局限：本质是"顺势外推"，对趋势突变/拐点不敏感；外推期越长误差越大，
   建议预测期数不超过 1~2 个季节周期；乘法季节模型要求数据恒为正。
"""

import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# ========================== 问题参数（比赛时改这里换数据） ==========================
np.random.seed(42)  # 固定随机种子，保证示例可复现（噪声扰动）

# 示例：某地区近 4 年(48 个月)的月度售电量（万 kWh），冬季 + 盛夏双峰、总体缓升
N_YEARS = 4
SEASONAL_PERIODS = 12      # 季节周期长度：月度数据 = 12
month_idx = np.arange(N_YEARS * SEASONAL_PERIODS)
TREND = 2.0                # 每月线性增量（kWh）
season_prof = np.array([10, 6, -4, -12, -16, -8, 10, 22, 15, 2, -6, 5])  # 12 个月季节增量
y_data = (170 + TREND * month_idx
          + np.tile(season_prof, N_YEARS)
          + np.random.normal(0, 6, N_YEARS * SEASONAL_PERIODS))  # 噪声 σ=6

N_FUTURE = 12              # 未来预测期数（示例预测未来一整年 12 期）
# ================================================================================


def exp_smoothing_fit(y, seasonal_periods, trend="add", seasonal="add", n_pred=12):
    """Holt-Winters 季节指数平滑拟合 + 预测。

    返回 (res, y_fit, y_fc)，res 为拟合结果对象（可继续取 AIC 等），
    y_fit 为训练期拟合值，y_fc 为未来 n_pred 期预测值。
    """
    y = np.asarray(y, dtype=float)
    # 加法趋势 + 加法季节（若数据波动幅度随水平放大，可把 seasonal 改为 "mul"，需数据恒正）
    # initialization_method="heuristic" 用经典启发式初值，平滑参数优化结果更直观
    # （"estimated" 会同时估计状态初值，可能把平滑参数压向 0）
    model = ExponentialSmoothing(y, trend=trend, seasonal=seasonal,
                                 seasonal_periods=seasonal_periods,
                                 initialization_method="heuristic")
    res = model.fit(optimized=True)          # 自动优化平滑参数
    y_fit = res.fittedvalues                 # 训练期内拟合值
    y_fc = res.forecast(n_pred)              # 未来 n_pred 期预测
    return res, np.asarray(y_fit), np.asarray(y_fc)


def fit_metrics(y, y_fit):
    """拟合优度指标：RMSE、MAE、MAPE（y、y_fit 等长，MAPE 要求 y>0）。"""
    resid = np.asarray(y) - np.asarray(y_fit)
    rmse = np.sqrt(np.mean(resid ** 2))
    mae = np.mean(np.abs(resid))
    mape = np.mean(np.abs(resid) / np.asarray(y)) * 100
    return rmse, mae, mape


if __name__ == "__main__":
    res, y_fit, y_fc = exp_smoothing_fit(y_data, SEASONAL_PERIODS, n_pred=N_FUTURE)
    n = len(y_data)

    # ---- 平滑参数（statsmodels≥0.15 存于 params 字典；旧版为属性，两种都兼容）----
    prm = res.params
    if isinstance(prm, dict):          # 新版: 按名取
        alpha = float(np.asarray(prm["smoothing_level"]))
        beta = float(np.asarray(prm["smoothing_trend"]))
        gamma = float(np.asarray(prm["smoothing_seasonal"]))
    else:                              # 旧版: 属性形式
        alpha = float(getattr(res, "smoothing_level", np.nan))
        beta = float(getattr(res, "smoothing_trend", np.nan))
        gamma = float(getattr(res, "smoothing_seasonal", np.nan))
    print("[Holt-Winters 参数]")
    print(f"  α(水平)={alpha:.3f}  β(趋势)={beta:.3f}  γ(季节)={gamma:.3f}  (极大似然自动优化)")
    if gamma < 0.005:
        print("  ※ γ≈0 表示该序列季节形态稳定、无需逐年自适应更新（正常现象，非模型故障）")
    print(f"  模型: trend='add', seasonal='add', 季节周期={SEASONAL_PERIODS}, AIC={res.aic:.2f}")

    # ---- 拟合优度 ----
    rmse, mae, mape = fit_metrics(y_data, y_fit)
    print("\n[训练期拟合优度]  (近因含噪声扰动, RMSE/MAPE 越小越好)")
    print(f"  RMSE = {rmse:.3f}   MAE = {mae:.3f}   MAPE = {mape:.2f}%")

    # ---- 逐期输出：历史(最后 8 期拟合) + 未来预测 ----
    print("\n[近期拟合值 + 未来预测]  (单位: 万 kWh)")
    start = max(0, n - 8)
    for t in range(start, n):
        print(f"  t={t+1:>2d}: 实际 {y_data[t]:8.2f}  拟合 {y_fit[t]:8.2f}")
    print("  " + "-" * 40)
    for k, v in enumerate(y_fc, start=1):
        print(f"  t={n+k:>2d}: 预测 {v:8.2f}  (未来第 {k} 期)")

    # ---- 结论提示 ----
    print(f"\n[结论] 未来 {N_FUTURE} 期整体呈上升趋势，且仍保留明显的季节峰谷（盛夏 {n+7} 期附近峰值）")
    print("  比赛用法：把预测区间线画进论文图，并给出 MAPE 说明精度（可加置信带）。")
