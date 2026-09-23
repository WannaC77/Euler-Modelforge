"""数据包络分析 DEA —— CCR 模型模板（规模报酬不变, CRS）。

适用场景：多投入多产出的相对效率评价——医院/银行网点/高校院系/公交线路等一组
"决策单元 DMU"谁更"高效"，并能给低效单元算改进目标（国赛评价类题常用，与 AHP/熵权
互补：DEA 不需要人为定权重，权重由各 DMU 自选最优）。

原理（投入导向 CCR，乘法形式）：对每个 DMU 求解——
  max  θ = Σ_r u_r y_{rj0}            (效率 = 加权产出)
  s.t. Σ_i v_i x_{ij0} = 1            (加权投入归一)
       Σ_r u_r y_{rj} − Σ_i v_i x_{ij} ≤ 0,  ∀j      (任何 DMU 产出 ≤ 投入)
       u_r, v_i ≥ 0
θ* = 1 且所有松弛为 0 → DEA 有效；θ* < 1 → 无效，投入可同比例压缩到 θ*·x。
第二阶段(包络形式)再解松弛变量，给出各无效 DMU 的投入/产出改进目标。

输入：投入矩阵 X（n_DMU × m）、产出矩阵 Y（n_DMU × s），全部元素 > 0，n_DMU ≥ m+s。
输出：各 DMU 效率值 θ、有效性判定(含强/弱有效)、排名、平均效率、无效单元改进目标；
      内置校验：θ ∈ [0,1] 且有效单元 θ = 1。
依赖：numpy、scipy。
⚠️ 注意：① 投入/产出需均为正数（有零值可整体平移或换模型）；② CCR 隐含规模报酬不变，
   规模差异大时用 BCC(VRS) 更合适（可扩展，参考 scipy linprog 同法）；③ 效率值仅代表
   "相对"效率——有效单元只是在本组数据内最优，不代表绝对优秀。
"""

# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy", "scipy"):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np
from scipy.optimize import linprog

# ========================== 问题参数（比赛时改这里换数据） ==========================
# 示例：7 家医院（DMU）相对效率评价。投入 = 员工数、床位-面积(营业面积，百㎡)，
#       产出 = 月门诊人次(百)、出院人数(十)
DMU_NAMES = ["医院A", "医院B", "医院C", "医院D", "医院E", "医院F", "医院G"]
INPUT_NAMES = ["员工数", "面积(百㎡)"]
OUTPUT_NAMES = ["门诊(百人次)", "出院(十人)"]
X = np.array([              # 投入矩阵: 每行一家医院
    [20, 151],              # 医院A
    [19, 131],              # 医院B
    [25, 160],              # 医院C
    [27, 168],              # 医院D
    [22, 158],              # 医院E
    [55, 255],              # 医院F
    [33, 235],              # 医院G
], dtype=float)
Y = np.array([              # 产出矩阵: 每行一家医院
    [100, 90],              # 医院A
    [150, 50],              # 医院B
    [160, 55],              # 医院C
    [180, 72],              # 医院D
    [94, 66],               # 医院E
    [230, 90],              # 医院F
    [220, 88],              # 医院G
], dtype=float)
# ================================================================================


def dea_ccr_theta(X, Y):
    """投入导向 CCR 效率（乘法形式，逐 DMU 解 LP）。返回效率值数组 θ。"""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    n, m = X.shape
    s = Y.shape[1]
    theta = np.zeros(n)
    for j0 in range(n):
        # 变量 = [u(产出权, s个), v(投入权, m个)]；目标 = max u·y_{j0} → min -u·y_{j0}
        c = np.concatenate([-Y[j0], np.zeros(m)])
        # 约束 Σ u_r y_{rj} - Σ v_i x_{ij} ≤ 0 （所有 DMU）
        A_ub = np.hstack([Y, -X])
        b_ub = np.zeros(n)
        # 等式 Σ v_i x_{ij0} = 1
        A_eq = np.hstack([np.zeros((1, s)), X[j0:j0 + 1]])
        b_eq = np.ones(1)
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                      bounds=[(0, None)] * (s + m), method="highs")
        if not res.success:
            raise RuntimeError(f"DMU {j0} 的 LP 求解失败: {res.message}")
        theta[j0] = -res.fun                       # 效率 = 最优目标值
    return theta


def dea_ccr_slacks(X, Y, theta):
    """第二阶段(包络形式)求松弛变量与改进目标。
    返回 (slack_in, slack_out)：各 DMU 投入冗余 s⁻、产出不足 s⁺（形状同 X/Y），
    其中有效单元二者≈0。投入目标 = θ·x − s⁻, 产出目标 = y + s⁺。"""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    n, m = X.shape
    s = Y.shape[1]
    slack_in = np.zeros_like(X)
    slack_out = np.zeros_like(Y)
    for j0 in range(n):
        # 变量 = [λ(组合权重, n个), s⁻(投入松弛, m个), s⁺(产出松弛, s个)]
        # 目标 = max (Σs⁻ + Σs⁺) → min -(Σs⁻ + Σs⁺)
        c = np.concatenate([np.zeros(n), -np.ones(m), -np.ones(s)])
        # Σλ x_{ij} + s_i⁻ = θ x_{ij0}；  Σλ y_{rj} − s_r⁺ = y_{rj0}
        A_eq = np.zeros((m + s, n + m + s))
        A_eq[:m, :n] = X.T
        A_eq[:m, n:n + m] = np.eye(m)
        A_eq[m:, :n] = Y.T
        A_eq[m:, n + m:] = -np.eye(s)
        b_eq = np.concatenate([theta[j0] * X[j0], Y[j0]])
        res = linprog(c, A_eq=A_eq, b_eq=b_eq,
                      bounds=[(0, None)] * (n + m + s), method="highs")
        if not res.success:
            raise RuntimeError(f"DMU {j0} 第二阶段 LP 求解失败: {res.message}")
        x = res.x
        slack_in[j0] = x[n:n + m]
        slack_out[j0] = x[n + m:]
    return slack_in, slack_out


def efficiency_status(theta, slack_in, slack_out, tol=1e-6):
    """有效性判定: 强有效(θ≈1 且无松弛) / 弱有效(θ≈1 但有松弛) / 无效(θ<1)。"""
    n = len(theta)
    status = []
    for j in range(n):
        eff = abs(theta[j] - 1.0) <= tol
        slack_free = (slack_in[j].max() <= tol) and (slack_out[j].max() <= tol)
        if eff and slack_free:
            status.append("强有效")
        elif eff:
            status.append("弱有效")
        else:
            status.append("无效")
    return status


if __name__ == "__main__":
    n = len(DMU_NAMES)
    assert (X > 0).all() and (Y > 0).all(), "CCR 要求投入/产出全部 > 0"
    assert X.shape[0] == Y.shape[0] == n, "X、Y 行数须一致"

    # ---- 1) 求解效率（第一阶段）----
    theta = dea_ccr_theta(X, Y)
    # ---- 2) 求解松弛与改进目标（第二阶段）----
    s_in, s_out = dea_ccr_slacks(X, Y, theta)
    status = efficiency_status(theta, s_in, s_out)

    print("[CCR(投入导向) 效率评价结果]")
    print(f"  {'DMU':<6}{'效率θ':>10}{'判定':>8}{'排名':>6}")
    order = np.argsort(-theta)
    rank_map = {j: r + 1 for r, j in enumerate(order)}
    for j in range(n):
        mark = "★" if abs(theta[j] - 1) < 1e-6 else " "
        print(f"  {DMU_NAMES[j]:<5}{theta[j]:>10.4f}{status[j]:>10}{rank_map[j]:>5}  {mark}")
    print(f"\n  平均效率 = {theta.mean():.4f}；有效单元数 = "
          f"{sum(1 for st in status if st in ('强有效', '弱有效'))} 个")

    # ---- 3) 数值校验：效率 ∈ [0,1]；有效单元效率 = 1 ----
    lo, hi = theta.min(), theta.max()
    ok_range = (lo >= -1e-9) and (hi <= 1 + 1e-9)
    eff_ones = [DMU_NAMES[j] for j in range(n) if abs(theta[j] - 1.0) <= 1e-6]
    ok_one = len(eff_ones) > 0 and all(abs(theta[j] - 1.0) <= 1e-6
                                       for j, st in enumerate(status) if "有效" in st)
    print("\n[数值校验]")
    print(f"  效率范围 [{lo:.6f}, {hi:.6f}]  {'✓ 全部 ∈ [0,1]' if ok_range else '✗ 越界!'}")
    print(f"  有效单元 {eff_ones} 效率均为 1  {'✓' if ok_one else '✗'}")
    print(f"  强有效单元: {[DMU_NAMES[j] for j in range(n) if status[j] == '强有效']}")

    # ---- 4) 无效单元的改进目标 ----
    print("\n[无效单元改进目标]  (投入压缩 + 产出提升的标杆方向)")
    print(f"  {'DMU':<6}{'效率θ':>9}  投入目标(θ·x−s⁻)        产出目标(y+s⁺)")
    for j in range(n):
        if status[j] == "无效":
            x_t = theta[j] * X[j] - s_in[j]
            y_t = Y[j] + s_out[j]
            print(f"  {DMU_NAMES[j]:<5}{theta[j]:>9.4f}  "
                  + " ".join(f"{IN} {v:7.2f}" for IN, v in zip(INPUT_NAMES, x_t))
                  + "  |  "
                  + " ".join(f"{OUT} {v:7.2f}" for OUT, v in zip(OUTPUT_NAMES, y_t)))
    print("\n[结论] θ=1 且无松弛者为 DEA 有效（本组数据内相对最优）；θ<1 者按上式压缩投入、")
    print("  提升产出可达到标杆水平。比赛建议：与熵权/AHP 排序结果交叉对比后写进论文。")
