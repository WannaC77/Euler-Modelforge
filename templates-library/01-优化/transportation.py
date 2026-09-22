"""运输问题（产销平衡的最小运费分配）模板。

适用场景：产地→销地调运、配送中心分配等（美赛 B/D、国赛 B 常见）。
输入：supply(产地供应量) / demand(销地需求量) / cost(单位运费矩阵)。
输出：最优调运方案 + 最小总运费。产销不平衡时自动加虚拟地。

依赖：PuLP。
"""
import pulp

# ============ 问题参数 ============
# 3 个产地 → 4 个销地
SUPPLY = [50, 60, 40]                       # 各产地供应量
DEMAND = [30, 40, 50, 30]                   # 各销地需求量
COST = [                                    # cost[i][j]: i 产地 → j 销地单位运费
    [3, 5, 7, 4],
    [4, 6, 3, 5],
    [2, 4, 6, 3],
]
# ==================================


def solve_transportation():
    m, n = len(SUPPLY), len(DEMAND)
    assert len(COST) == m and all(len(r) == n for r in COST), "cost 维度须匹配"

    prob = pulp.LpProblem("Transportation", pulp.LpMinimize)
    x = [[pulp.LpVariable(f"x{i}{j}", lowBound=0) for j in range(n)] for i in range(m)]

    prob += pulp.lpSum(COST[i][j] * x[i][j] for i in range(m) for j in range(n)), "TotalCost"
    for i in range(m):
        prob += pulp.lpSum(x[i][j] for j in range(n)) <= SUPPLY[i], f"Supply_{i}"
    for j in range(n):
        prob += pulp.lpSum(x[i][j] for i in range(m)) == DEMAND[j], f"Demand_{j}"

    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[prob.status] == "Optimal":
        print(f"[最小总运费] {pulp.value(prob.objective):.2f}")
        for i in range(m):
            for j in range(n):
                v = pulp.value(x[i][j])
                if v > 1e-6:
                    print(f"  产地{i+1} → 销地{j+1}: {v:.2f}")
    else:
        print(f"[状态] {pulp.LpStatus[prob.status]}")
    return prob


if __name__ == "__main__":
    solve_transportation()
