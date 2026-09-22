"""灰色预测 GM(1,1) 模板。

适用场景：小样本（≥4 个点）短期预测，数据呈近似指数增长/衰减。数模经典方法（国赛 C、美赛 C/E 可用）。
原理：一阶单变量灰色模型，对原始序列做累加生成 (AGO) 后拟合一阶微分方程。

输入：历史观测序列 y（list/np.ndarray），预测步数 n_pred。
输出：拟合值 + 未来预测值。

⚠️ 局限：长周期预测误差大；数据波动大时慎用（先用后验差检验判断精度）。
"""
import numpy as np


def gm11(y, n_pred=5):
    """GM(1,1) 预测。返回 (pred 含历史拟合+未来预测, a, b)。"""
    y = np.asarray(y, dtype=float)
    n = len(y)

    # 1. 累加生成 AGO
    x1 = np.cumsum(y)

    # 2. 构造 B 矩阵和 Y 向量（紧邻均值生成 z1）
    z1 = (x1[:-1] + x1[1:]) / 2.0
    B = np.column_stack([-z1, np.ones(n - 1)])
    Yn = y[1:]

    # 3. 最小二乘求参数 [a, b]^T = (B^T B)^{-1} B^T Y
    a, b = np.linalg.lstsq(B, Yn, rcond=None)[0]

    # 4. 时间响应式，还原预测
    x1_pred = np.zeros(n + n_pred)
    x1_pred[0] = y[0]
    for k in range(1, n + n_pred):
        x1_pred[k] = (y[0] - b / a) * np.exp(-a * k) + b / a

    y_pred = np.zeros(n + n_pred)
    y_pred[0] = y[0]
    y_pred[1:] = np.diff(x1_pred)          # IAGO 还原
    y_pred = np.maximum(y_pred, 0)         # 非负约束（视问题需要可删）

    return y_pred, a, b


def posterior_check(y, y_pred):
    """后验差检验：C = S2/S1。C<0.35 优, <0.5 合格, <0.65 勉强, >=0.65 不合格。"""
    n = len(y)
    resid = y - y_pred[:n]
    S1 = np.std(y, ddof=1)
    S2 = np.std(resid, ddof=1)
    C = S2 / S1 if S1 > 0 else np.inf
    return C


if __name__ == "__main__":
    # 示例：某指标 8 期观测（可换成你的数据）
    data = [2.874, 3.278, 3.337, 3.390, 3.679, 3.612, 3.903, 4.276]
    n_future = 4

    pred, a, b = gm11(data, n_pred=n_future)
    print("[拟合 + 预测]")
    for i, v in enumerate(pred):
        tag = " (预测)" if i >= len(data) else ""
        print(f"  t={i+1}: {v:.4f}{tag}")

    C = posterior_check(data, pred)
    grade = "优" if C < 0.35 else "合格" if C < 0.5 else "勉强" if C < 0.65 else "不合格"
    print(f"\n[后验差检验] C = {C:.4f} → {grade}")

    # 画图（比赛时导出到论文）
    import matplotlib.pyplot as plt
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils.plot_style import style_plot, save_fig
    style_plot()
    t = np.arange(1, len(data) + 1)
    fig, ax = plt.subplots()
    ax.plot(t, data, "o-", label="Observed")
    ax.plot(np.arange(1, len(pred) + 1), pred, "s--", label="GM(1,1) fit+forecast")
    ax.axvline(len(data) + 0.5, color="gray", ls=":", label="forecast start")
    ax.set_xlabel("Period"); ax.set_ylabel("Value"); ax.legend()
    save_fig(fig, os.path.join(os.path.dirname(__file__), "..", "data", "grey_gm11.png"))
