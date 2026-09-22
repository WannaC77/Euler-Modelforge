"""匈牙利算法求解指派问题（最小成本匹配）模板。

适用场景：n 个任务分给 n 个人，每个任务必须且只能由一人完成、每人最多承担一个任务，
         求总成本最小的指派方案（仪器分配、流水线排班、装卸点选址、车辆-任务匹配等）。
输入格式：COST[i][j] = 第 i 个任务交给第 j 个人完成所需成本（n×n 方阵，行=任务，列=人）。
输出：最小总成本 + 每个任务指派给谁的方案（可直接写进论文）+ 穷举法校验结果。
依赖：无第三方依赖（纯 Python，scipy 可选做交叉验证）。

比赛用法：
    1. 改下方常量区的 COST（n 可任意，只要方阵）
    2. 运行 python assignment.py
    3. 读"任务 → 人（成本）"方案与最小总成本

说明：算法为经典 O(n^3) 匈牙利算法（可行标号 + 增广路），对 0/整数/浮点成本均适用。
"""
import itertools

# ============ 问题参数（改这里即可）============
# COST[i][j]: 任务 i 由人 j 完成的成本（示例 4 任务 × 4 人）
COST = [[9, 2, 7, 8],
        [6, 4, 3, 7],
        [5, 8, 1, 8],
        [7, 6, 9, 4]]

# 可选：自定义任务/人员名称（长度需 = n；留空则用 "任务0.. / 人0.." 自动命名）
TASK_NAMES = []
PERSON_NAMES = []
# ==============================================


def hungarian_assign(cost):
    """匈牙利算法求最小成本指派。

    参数 cost: n×n 成本矩阵（可 int/float）。
    返回: (assignment, total)，assignment[i] = 分给任务 i 的人（0-based），total = 最小总成本。
    """
    n = len(cost)
    # u/v: 行列可行标号；p[j] = 当前匹配到列 j 的行（0 表示空）；way: 增广路回溯
    u = [0.0] * (n + 1)
    v = [0.0] * (n + 1)
    p = [0] * (n + 1)
    way = [0] * (n + 1)
    INF = float("inf")

    for i in range(1, n + 1):           # 逐行(任务)加入匹配
        p[0] = i                        # 虚拟列 0 指向当前行，作为增广路起点
        j0 = 0
        minv = [INF] * (n + 1)          # minv[j]: 从已访问集合到列 j 的最小 slack
        used = [False] * (n + 1)
        while True:                     # 找最短增广路（Dijkstra 式标号更新）
            used[j0] = True
            i0 = p[j0]
            delta, j1 = INF, 0
            for j in range(1, n + 1):   # 遍历未访问列，更新 slack
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(n + 1):      # 标号整体平移，保证至少一条边进入相等子图
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:              # 增广路到达未匹配列，结束
                break
        while True:                     # 沿 way 回溯翻转匹配
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break

    assignment = [0] * n
    for j in range(1, n + 1):           # 列 j 匹配到行 p[j]
        if p[j] > 0:
            assignment[p[j] - 1] = j - 1
    total = sum(cost[i][assignment[i]] for i in range(n))
    return assignment, total


def verify_brute(cost):
    """穷举法求最小总成本（n<=9 时用于校验匈牙利算法结果）。"""
    n = len(cost)
    if n > 9:
        return None, None
    best_total, best_perm = float("inf"), None
    for perm in itertools.permutations(range(n)):   # 每个排列 = 一种任务->人指派
        t = sum(cost[i][perm[i]] for i in range(n))
        if t < best_total:
            best_total, best_perm = t, perm
    return best_total, best_perm


if __name__ == "__main__":
    n = len(COST)
    task_names = TASK_NAMES or [f"任务{i}" for i in range(n)]
    person_names = PERSON_NAMES or [f"人{i}" for i in range(n)]

    # 求解：匈牙利算法
    assign, total = hungarian_assign(COST)
    print(f"指派问题规模: {n} 任务 × {n} 人")
    print(f"[最小总成本] {total}")
    print("[指派方案]  （任务 → 人，单件成本）")
    for i in range(n):
        j = assign[i]
        print(f"  {task_names[i]} → {person_names[j]}  (成本 {COST[i][j]})")

    # 校验：穷举法（n<=9 时自动执行）
    brute_total, _ = verify_brute(COST)
    if brute_total is not None:
        if brute_total == total:
            print(f"[穷举校验] 最优总成本 {brute_total} 与匈牙利算法一致 ✓  PASS")
        else:
            print(f"[穷举校验] 不一致! 穷举={brute_total}, 算法={total}  FAIL")
    else:
        print(f"[穷举校验] n={n}>9 跳过（算法仍为多项式时间 O(n^3)）")
