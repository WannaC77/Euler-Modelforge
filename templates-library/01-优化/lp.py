"""线性规划/整数规划/混合整数规划通用模板。

适用场景：求最大利润/最小成本/最优分配等约束优化问题（国赛 B 类、美赛 B/D 常见）。
输入格式：目标函数系数 c、约束矩阵 A、约束上下界（见示例）。
依赖：PuLP（requirements.txt 已含）。

比赛用法：
    1. 打开文件，改 PROBLEM 常量区的 c / A / b_ub / b_eq / bounds
    2. 运行 python lp.py
    3. 输出最优值 + 决策变量取值（可直接写进论文）
"""
import pulp

# ============ 问题参数（改这里即可）============
# 例：生产计划——两种产品 x1, x2，利润 3 和 5
#   约束: x1 + 2x2 <= 8  (工时)
#         3x1 + 2x2 <= 12 (原料)
#         x1, x2 >= 0
# 若 x 需整数 → INTEGER = True

INTEGER = False      # True = 整数规划 (IP)
VARS = ["x1", "x2"]  # 变量名
OBJ_COEF = [3, 5]    # 目标系数 (最大化)
MAXIMIZE = True      # False = 最小化

# 不等式约束: A_ub @ x <= b_ub
A_UB = [[1, 2],
        [3, 2]]
B_UB = [8, 12]

# 等式约束: A_eq @ x == b_eq （无则空表）
A_EQ = []
B_EQ = []

# 变量上下界: (low, up)，None = 无界
BOUNDS = [(0, None), (0, None)]
# ==============================================


def solve_lp():
    n = len(VARS)
    prob = pulp.LpProblem("LP", pulp.LpMaximize if MAXIMIZE else pulp.LpMinimize)

    # 建变量
    if INTEGER:
        xs = [pulp.LpVariable(VARS[i], lowBound=BOUNDS[i][0] if BOUNDS[i][0] is not None else None,
                              upBound=BOUNDS[i][1] if BOUNDS[i][1] is not None else None,
                              cat="Integer") for i in range(n)]
    else:
        xs = [pulp.LpVariable(VARS[i], lowBound=BOUNDS[i][0] if BOUNDS[i][0] is not None else None,
                              upBound=BOUNDS[i][1] if BOUNDS[i][1] is not None else None)
              for i in range(n)]

    # 目标
    prob += pulp.lpSum(OBJ_COEF[i] * xs[i] for i in range(n)), "Objective"

    # 约束
    for r, row in enumerate(A_UB):
        prob += pulp.lpSum(row[i] * xs[i] for i in range(n)) <= B_UB[r], f"ub_{r}"
    for r, row in enumerate(A_EQ):
        prob += pulp.lpSum(row[i] * xs[i] for i in range(n)) == B_EQ[r], f"eq_{r}"

    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[status] == "Optimal":
        print(f"[最优值] {pulp.value(prob.objective):.4f}")
        for i in range(n):
            print(f"  {VARS[i]} = {pulp.value(xs[i]):.4f}")
    else:
        print(f"[状态] {pulp.LpStatus[status]}（无最优解，检查约束是否矛盾）")
    return prob


if __name__ == "__main__":
    solve_lp()
