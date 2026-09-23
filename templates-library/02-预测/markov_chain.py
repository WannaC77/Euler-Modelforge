"""马尔可夫链预测模板。

适用场景：系统状态按概率转移、且"未来只依赖当前状态"（无后效性/马尔可夫性），
如天气状态、顾客购买习惯、市场份额转移、设备运行状态、人才流动等。
经典应用：短中期状态概率预测 + 长期(稳态)占比求解。

原理：π_{t+1} = π_t · P（行向量左乘转移矩阵）。
  · 多步预测: π_{t+k} = π_t · P^k
  · 稳态分布 π*: 满足 π*·P = π* 且 Σπ* = 1（长期各状态占比，与初始状态无关）

输入：转移概率矩阵 P（n×n，行和为 1，行=当前状态，列=下一状态）、
      初始分布 π0（行向量，和为 1）或已知"今天状态"。
输出：未来各期状态概率分布、稳态分布、模型校验(行和=1 / 稳态残差≈0)。
依赖：numpy。
⚠️ 局限：要求状态转移随时间平稳（转移矩阵固定）；若数据可算出经验转移频率
  直接用；状态划分过多时样本量要够。稳态存在性：不可约 + 非周期链必有唯一稳态。
"""

# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy",):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np

# ========================== 问题参数（比赛时改这里换数据） ==========================
# 示例：某地天气 3 状态（晴/阴/雨）转移概率矩阵，行 = 今天，列 = 明天
# P[0][1] = 0.2 表示"今天晴 → 明天阴"的概率为 0.2
STATE_NAMES = ["晴", "阴", "雨"]
P = np.array([
    [0.7, 0.2, 0.1],    # 今天晴
    [0.3, 0.4, 0.3],    # 今天阴
    [0.2, 0.3, 0.5],    # 今天雨
])
TODAY_STATE = 0          # 今天状态（0=晴）：以此为起点预测未来
N_STEP = 10              # 预测未来多少期
# ================================================================================


def check_stochastic(P, tol=1e-9):
    """校验转移矩阵合法性：元素非负且每行和为 1。"""
    P = np.asarray(P, dtype=float)
    ok = (P >= 0).all() and np.allclose(P.sum(axis=1), 1.0, atol=tol)
    if not ok:
        raise ValueError("转移矩阵不合法：元素须非负且每行和为 1！")
    return True


def multi_step_dist(P, pi0, k):
    """k 步后的状态分布: π_k = π0 · P^k（k 可为标量，返回一维行向量）。"""
    return pi0 @ np.linalg.matrix_power(np.asarray(P, dtype=float), k)


def forecast(P, start_state=None, pi0=None, horizon=10):
    """从初始分布(或某已知状态)出发，预测未来 1..horizon 期逐期分布。
    返回列表 [π_1, π_2, ..., π_horizon]。"""
    P = np.asarray(P, dtype=float)
    check_stochastic(P)
    n = P.shape[0]
    if pi0 is None:
        pi0 = np.zeros(n)
        pi0[start_state] = 1.0               # 已知今天处于哪个状态 → one-hot
    pi0 = np.asarray(pi0, dtype=float)
    assert np.isclose(pi0.sum(), 1.0), "初始分布须和为 1"
    return [multi_step_dist(P, pi0, k) for k in range(1, horizon + 1)]


def steady_state(P):
    """求稳态分布 π*：π·P = π, Σπ=1。用转移矩阵转置的特征值法求解。
    返回 (π*, 残差 ||π·P - π||∞)。"""
    P = np.asarray(P, dtype=float)
    check_stochastic(P)
    eigvals, eigvecs = np.linalg.eig(P.T)
    idx = int(np.argmin(np.abs(eigvals - 1.0)))          # 找特征值≈1 的特征向量
    pi = np.abs(eigvecs[:, idx].real)
    pi = pi / pi.sum()                                   # 归一化使概率和为 1
    resid = np.max(np.abs(pi @ P - pi))                  # 稳态方程残差
    return pi, resid


if __name__ == "__main__":
    P = np.asarray(P, dtype=float)
    n = P.shape[0]

    # ---- 0) 模型合法性校验 ----
    check_stochastic(P)
    print("[转移矩阵 P]  (行=今天, 列=明天)")
    print("        " + "".join(f"{s:>6}" for s in STATE_NAMES))
    for i in range(n):
        print(f"  {STATE_NAMES[i]:<3} " + "".join(f"{v:6.2f}" for v in P[i]))
    print("  ✓ 各行和为 1，矩阵合法")

    # ---- 1) 多步预测：从"今天状态"出发 ----
    pi0 = np.zeros(n)
    pi0[TODAY_STATE] = 1.0
    dists = forecast(P, pi0=pi0, horizon=N_STEP)
    print(f"\n[多步预测]  今天 = {STATE_NAMES[TODAY_STATE]}，未来 {N_STEP} 期各状态概率")
    print(f"  {'期数':<6}" + "".join(f"{s:>9}" for s in STATE_NAMES))
    for k, d in enumerate(dists, start=1):
        probs = "".join(f"{v:9.2%}" for v in d)
        print(f"  t+{k:<4}" + probs)
        # 校验: 每期分布概率和 = 1
        assert np.isclose(d.sum(), 1.0), f"第 {k} 期分布概率和不为 1"
    print("  ✓ 每期概率和均为 1")

    # ---- 2) 稳态分布（长期占比）----
    pi_star, resid = steady_state(P)
    print("\n[稳态分布 π*]  (长期各状态占比, 与初始状态无关)")
    for s, v in zip(STATE_NAMES, pi_star):
        print(f"  长期{s}概率 = {v:.4f} ({v:.2%})")
    print(f"  校验: Σπ* = {pi_star.sum():.6f}  {'✓' if np.isclose(pi_star.sum(), 1) else '✗'}"
          f"，稳态残差 ||π*·P−π*|| = {resid:.2e}  {'✓ 满足 π*·P=π*' if resid < 1e-8 else '✗'}")

    # ---- 3) 收敛性验证: 远期分布应逼近稳态 ----
    far = multi_step_dist(P, pi0, 200)
    print(f"\n[收敛验证]  t+200 分布 {np.round(far, 4)} vs 稳态 {np.round(pi_star, 4)}")
    print(f"  最大偏差 = {np.max(np.abs(far - pi_star)):.2e}  "
          f"{'✓ 已收敛到稳态（链遍历）' if np.max(np.abs(far - pi_star)) < 1e-6 else '✗'}")

    print("\n[结论] 长期看天气以 晴≈%.1f%% / 阴≈%.1f%% / 雨≈%.1f%% 的比例分布。"
          % tuple(v * 100 for v in pi_star))
    print("  比赛用法：用经验转移频率估计 P（频数/行和），再套本模板预测与求稳态。")
