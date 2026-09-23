"""蒙特卡洛仿真模板。

适用场景：随机性问题/无法解析求解的复杂系统（库存、排队、随机优化、概率估计）。
示例：用蒙特卡洛估计 π + 随机库存仿真。

依赖：numpy。
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy",):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np


def estimate_pi(n_samples=100_000, seed=42):
    """蒙特卡洛估计 π：随机点落在单位圆内的比例。"""
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, n_samples)
    y = rng.uniform(-1, 1, n_samples)
    inside = (x**2 + y**2) <= 1
    return 4 * inside.sum() / n_samples


def inventory_sim(demand_mean=50, demand_std=10, order_cost=100, hold_cost=2,
                  shortage_cost=8, reorder_point=60, order_qty=200, n_days=365, seed=42):
    """(s,Q) 库存策略仿真。返回 (总成本, 缺货天数)。"""
    rng = np.random.default_rng(seed)
    stock, total_cost, shortage_days = 0, 0, 0
    for _ in range(n_days):
        # 若低于再订货点则补货（假设隔天到货）
        if stock < reorder_point:
            total_cost += order_cost
            stock += order_qty
        demand = max(0, rng.normal(demand_mean, demand_std))
        served = min(stock, demand)
        shortage = demand - served
        if shortage > 0:
            total_cost += shortage * shortage_cost
            shortage_days += 1
        stock -= served
        total_cost += stock * hold_cost
    return total_cost, shortage_days


if __name__ == "__main__":
    pi = estimate_pi()
    print(f"[蒙特卡洛] π ≈ {pi:.4f}  (真值 {np.pi:.4f}, 误差 {abs(pi-np.pi):.4f})")

    print("\n[库存仿真] 再订货点扫描:")
    for rp in [40, 50, 60, 70, 80]:
        cost, sd = inventory_sim(reorder_point=rp)
        print(f"  再订货点={rp}: 年成本 {cost:.0f} 元, 缺货 {sd} 天")
