"""时间序列 ARIMA 预测模板。

适用场景：有较长历史数据（≥50 点）的单变量时间序列预测（国赛 C、美赛 C 常见）。
流程：ADF 平稳性检验 → 差分 → ACF/PACF 定阶（或 AIC 自动搜索）→ 拟合 → 预测 → 残差检验。

依赖：statsmodels。
"""
import numpy as np
import warnings
warnings.filterwarnings("ignore")


def auto_arima(y, max_p=5, max_q=5, max_d=2):
    """按 AIC 自动搜索 ARIMA(p,d,q)。返回最佳 order。"""
    from statsmodels.tsa.stattools import adfuller
    from statsmodels.tsa.arima.model import ARIMA

    y = np.asarray(y, dtype=float)
    # 确定差分阶数 d：ADF 检验直到平稳
    d = 0
    yt = y.copy()
    while d < max_d:
        p_val = adfuller(yt)[1]
        if p_val < 0.05:
            break
        yt = np.diff(yt)
        d += 1

    best_aic, best_order = np.inf, None
    for p in range(max_p + 1):
        for q in range(max_q + 1):
            try:
                model = ARIMA(y, order=(p, d, q)).fit()
                if model.aic < best_aic:
                    best_aic, best_order = model.aic, (p, d, q)
            except Exception:
                continue
    return best_order, best_aic


def arima_predict(y, n_pred=5, order=None):
    """ARIMA 预测。order=None 时自动搜索。返回 (pred, model)。"""
    from statsmodels.tsa.arima.model import ARIMA
    y = np.asarray(y, dtype=float)
    if order is None:
        order, _ = auto_arima(y)
    model = ARIMA(y, order=order).fit()
    pred = model.forecast(n_pred)
    return np.asarray(pred), model, order


if __name__ == "__main__":
    # 示例：月度数据（可换成你的数据）
    rng = np.random.default_rng(42)
    t = np.arange(120)
    data = 100 + 0.3 * t + 5 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 2, 120)

    n_future = 12
    pred, model, order = arima_predict(data, n_pred=n_future)
    print(f"[自动定阶] ARIMA{order}  AIC={model.aic:.2f}")
    print("[预测]")
    for i, v in enumerate(pred):
        print(f"  t+{i+1}: {v:.2f}")

    import matplotlib.pyplot as plt
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils.plot_style import style_plot, save_fig
    style_plot()
    fig, ax = plt.subplots()
    ax.plot(t, data, label="Observed")
    ax.plot(np.arange(len(data), len(data) + n_future), pred, "o--", label="ARIMA forecast")
    ax.set_xlabel("Period"); ax.set_ylabel("Value"); ax.legend()
    save_fig(fig, os.path.join(os.path.dirname(__file__), "..", "data", "arima.png"))
