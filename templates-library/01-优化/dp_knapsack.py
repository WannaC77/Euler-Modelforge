"""0-1 背包问题动态规划模板。

适用场景：有限容量/预算下从若干物品中选子集使总价值最大，每件物品只能选一次
         （物资装载、投资组合、任务取舍、装箱等离散选择问题）。
输入格式：VALUES[i] = 第 i 件物品价值，WEIGHTS[i] = 第 i 件物品重量，CAPACITY = 背包容量。
输出：最大总价值 + 具体选了哪些物品（编号/价值/重量清单）+ 穷举法校验结果。
依赖：无第三方依赖（纯 Python）。

比赛用法：
    1. 改下方常量区的 VALUES / WEIGHTS / CAPACITY（数量不限，容量可为整数）
    2. 运行 python dp_knapsack.py
    3. 读最大价值与所选物品方案，写入论文"方案设计"部分

说明：二维 DP O(n·W) 便于回溯方案；n 大而 W 大时可用一维滚动数组（见函数内注释）。
"""
import itertools

# ============ 问题参数（改这里即可）============
# 第 i 件物品的价值与重量（示例 8 件，容量 65）
VALUES = [60, 100, 120, 55, 70, 90, 45, 80]
WEIGHTS = [10, 20, 30, 8, 12, 25, 6, 15]
CAPACITY = 65
# 可选：物品名称（长度需 = n，留空自动命名 物品0..）
ITEM_NAMES = []
# ==============================================


def knapsack_01(values, weights, capacity):
    """0-1 背包 DP：返回 (max_value, chosen)。

    chosen: 所选物品下标列表（升序）。算法 O(n·capacity) 时间、O(n·capacity) 空间。
    若容量极大、物品多（n 上万、W 百万），可把 dp 改成一维滚动数组（只保留 dp[w]），
    但回溯方案需要另存每步决策或改用贪心/分支限界。
    """
    n = len(values)
    # dp[i][c]: 只考虑前 i 件物品、容量 c 时能获得的最大价值
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        wi, vi = weights[i - 1], values[i - 1]
        for c in range(1, capacity + 1):
            if c >= wi:
                # 不选 vs 选第 i 件
                dp[i][c] = max(dp[i - 1][c], dp[i - 1][c - wi] + vi)
            else:
                dp[i][c] = dp[i - 1][c]

    # 回溯方案：倒推哪些物品被选中
    chosen = []
    c = capacity
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:        # 第 i 件被选了
            chosen.append(i - 1)
            c -= weights[i - 1]
    chosen.reverse()
    return dp[n][capacity], chosen


def verify_brute(values, weights, capacity):
    """穷举所有子集求最优（n<=20 时校验 DP 结果；2^n 枚举）。"""
    n = len(values)
    if n > 20:
        return None
    best = 0
    for mask in range(1 << n):              # mask 的二进制位 = 是否选该物品
        w = v = 0
        for i in range(n):
            if mask >> i & 1:
                w += weights[i]
                v += values[i]
        if w <= capacity and v > best:
            best = v
    return best


if __name__ == "__main__":
    n = len(VALUES)
    item_names = ITEM_NAMES or [f"物品{i}" for i in range(n)]
    max_v, chosen = knapsack_01(VALUES, WEIGHTS, CAPACITY)
    used_w = sum(WEIGHTS[i] for i in chosen)

    print(f"背包容量: {CAPACITY}，物品数: {n}")
    print(f"[最大总价值] {max_v}")
    print("[所选物品方案]")
    for i in chosen:
        print(f"  {item_names[i]}: 价值 {VALUES[i]}，重量 {WEIGHTS[i]}")
    print(f"[总重量] {used_w}（<= 容量 {CAPACITY}）")

    # 校验：穷举所有子集（n<=20 自动执行）
    brute_v = verify_brute(VALUES, WEIGHTS, CAPACITY)
    if brute_v is not None:
        if brute_v == max_v:
            print(f"[穷举校验] 最优价值 {brute_v} 与 DP 一致 ✓  PASS")
        else:
            print(f"[穷举校验] 不一致! 穷举={brute_v}, DP={max_v}  FAIL")
    else:
        print(f"[穷举校验] n={n}>20 跳过（DP 仍为多项式时间 O(n·W)）")
