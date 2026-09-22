"""非线性规划 (NLP) 通用模板 — scipy.optimize.minimize。

适用场景：目标函数或约束含非线性项的最优化问题（产量-成本模型、参数拟合、
         投资分配、几何极值、含约束的资源分配等；国赛 C/D 类、美赛常见）。
输入格式：在下方"目标函数区 / 约束区"写目标与约束；在"问题参数区"填初值/边界/方法。
输出：是否收敛 success、最优目标值、最优解 x（含每次迭代函数调用次数）。
依赖：scipy（requirements.txt 已含）。

比赛用法：
    1. 无约束问题 -> 填 UNCONSTRAINED 示例的目标函数与 x0
    2. 有约束问题 -> 填 CONSTRAINED 示例的目标、bounds、constraints
    3. 运行 python nlp.py，输出 fun/x/success 直接写进论文

要点：
    - bounds   = [(下界, 上界), ...]，None 表示无界（本模板只演示变量 >= 0 的下界）
    - constraints 列表里每个 dict 是一个约束：
        {'type': 'ineq', 'fun': f} 表示 f(x) >= 0；{'type': 'eq', 'fun': f} 表示 f(x) == 0
    - 给 fun 传入可选 'jac'（解析梯度）可显著加快收敛；不给则自动有限差分
"""
import numpy as np
from scipy.optimize import minimize

# ============ 目标函数区（改这里换问题）============

# 示例 1（无约束）：Rosenbrock 香蕉函数，全局最小 f=0 在 (1,1)
def obj_rosenbrock(x):
    return 100.0 * (x[1] - x[0] ** 2) ** 2 + (1.0 - x[0]) ** 2

# 示例 2（有约束）：标准测试算例 min (x0-1)^2 + (x1-2.5)^2
#   约束:  x0 - 2*x1 + 2 >= 0;  -x0 - 2*x1 + 6 >= 0;  -x0 + 2*x1 + 2 >= 0;  x0, x1 >= 0
#   已知最优: f = 0.8, x = (1.4, 1.7)（约束 1 取等号）
def obj_constrained(x):
    return (x[0] - 1.0) ** 2 + (x[1] - 2.5) ** 2

# ============ 问题参数（改这里即可）============
# ---- 无约束示例参数 ----
X0_FREE = np.array([-1.2, 1.0])     # 初值
# ---- 有约束示例参数 ----
X0_CONS = np.array([0.0, 0.0])      # 初值
BOUNDS = [(0.0, None), (0.0, None)]  # x0, x1 >= 0（None = 无上界）


def cons_constrained(x):
    """有约束示例的不等式约束（每个返回 >= 0 表示可行），含符号演示。"""
    return np.array([x[0] - 2.0 * x[1] + 2.0,      # 约束1: x0 - 2x1 + 2 >= 0
                     -x[0] - 2.0 * x[1] + 6.0,     # 约束2: -x0 - 2x1 + 6 >= 0
                     -x[0] + 2.0 * x[1] + 2.0])    # 约束3: -x0 + 2x1 + 2 >= 0
# ==============================================


def solve(obj_fun, x0, bounds=None, constraints=(), method="SLSQP", label=""):
    """通用 NLP 求解入口：包装 scipy.optimize.minimize 并打印结果。"""
    res = minimize(obj_fun, x0, method=method,
                   bounds=bounds, constraints=constraints)
    print(f"\n===== {label} =====")
    print(f"[是否收敛] {res.success}（{'是' if res.success else '否，检查初值/约束'}）")
    print(f"[最优值 fun] {res.fun:.6f}")
    print(f"[最优解 x] {np.round(res.x, 6)}")
    print(f"[迭代信息] {res.nit} 次迭代, {res.nfev} 次函数调用, 停止原因: {res.message}")
    return res


if __name__ == "__main__":
    # 示例 1：无约束最小化（用拟牛顿 BFGS，适合光滑问题；不可导可用 Nelder-Mead）
    r1 = solve(obj_rosenbrock, X0_FREE, label="无约束示例: Rosenbrock 函数")
    print(f"  [参考] 全局最优 f=0 @ (1,1)，求得 f={r1.fun:.2e} —— "
          f"{'PASS' if abs(r1.fun) < 1e-6 else 'FAIL'}")

    # 示例 2：带 bounds + 不等式约束的最小化（SLSQP 处理约束，也可换 trust-constr）
    constraints = [{"type": "ineq", "fun": cons_constrained}]
    r2 = solve(obj_constrained, X0_CONS, bounds=BOUNDS, constraints=constraints,
               label="有约束示例: min (x0-1)^2+(x1-2.5)^2, x>=0")
    ok = abs(r2.fun - 0.8) < 1e-4 and np.allclose(r2.x, [1.4, 1.7], atol=1e-3)
    print(f"  [参考] 理论最优 f=0.8 @ (1.4, 1.7)，求得 f={r2.fun:.6f} —— "
          f"{'PASS' if ok else 'FAIL'}")
