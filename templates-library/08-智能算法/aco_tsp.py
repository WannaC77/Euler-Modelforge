"""蚁群算法 (ACO) 求解旅行商问题 (TSP) 模板。

适用场景：需访问所有城市一次并回到起点的最短环路（配送路线、巡检路径、
         物流网络设计等组合优化问题；国赛/美赛路径类问题的标配解法之一）。
算法流程：初始化信息素 -> 每轮 N_ANTS 只蚂蚁按概率
          p ∝ tau^alpha * (1/d)^beta 逐步构造环路 -> 蒸发 + 释放信息素
          -> 精英蚂蚁加强全局最优路径 -> 迭代收敛到最优环。
输入格式：N_CITIES + 城市坐标列表（本模板用固定种子随机生成 10 城，可直接换成比赛数据；
          CITIES 留空则由 SEED 生成，保证可复现）。
输出：最优路径（城市编号序列）与总长度、收敛过程、与穷举最优的相对误差。
依赖：numpy（requirements.txt 已含）。

比赛用法：
    1. 把 CITIES 换成你题目的城市坐标（或从 Excel/CSV 读入，见注释）
    2. 运行 python aco_tsp.py
    3. 论文引用最优路径与总长度；画路线图用 matplotlib 连线 CITIES[bij]
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy",):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import itertools

import numpy as np

# ============ 问题参数（改这里即可）============
SEED = 2024                   # 随机种子（城市生成 + 蚁群过程，保证可复现）
N_CITIES = 10                 # 城市数
CITIES = []                   # 城市坐标 [(x0,y0), ...]；留空 = 用 SEED 随机生成

# ACO 超参
N_ANTS = 30                   # 每轮蚂蚁数
N_ITER = 40                   # 迭代轮数（信息素更新轮数）
ALPHA = 1.0                   # 信息素权重（越大越倾向跟"大家走过的路"）
BETA = 2.0                    # 距离启发权重（越大越贪近邻）
RHO = 0.5                     # 信息素蒸发率 (0,1)
Q = 1.0                       # 信息素总量常数
ELITE = 3                     # 精英蚂蚁数（每轮额外加强历史最优路径）

VERIFY_BRUTE = True           # True: 穷举对比（n<=10 时启用），评估 ACO 解的质量
# ==============================================


class AntColonyTSP:
    """蚁群算法 TSP 求解器。"""

    def __init__(self, coords, n_ants=N_ANTS, n_iter=N_ITER, alpha=ALPHA, beta=BETA,
                 rho=RHO, q=Q, elite=ELITE, seed=SEED):
        self.xy = np.array(coords, dtype=float)
        self.n = len(self.xy)
        self.n_ants, self.n_iter = n_ants, n_iter
        self.alpha, self.beta, self.rho, self.q, self.elite = alpha, beta, rho, q, elite
        self.rng = np.random.default_rng(seed)
        # 距离矩阵（欧氏）
        d = self.xy[:, None, :] - self.xy[None, :, :]
        self.dist = np.sqrt(np.sum(d ** 2, axis=2))
        np.fill_diagonal(self.dist, 1e-9)        # 对角线置小量防除零
        # 启发信息 eta_ij = 1 / d_ij
        self.eta = 1.0 / self.dist
        # 信息素初值：取最近邻启发解长度的量级
        tau0 = self.q / max(self._nn_length(), 1e-9)
        self.tau = np.full((self.n, self.n), tau0)

    def _nn_length(self):
        """最近邻贪心启发解的长度（用于信息素初值 + 作为对比基线）。"""
        tour, cur, total = [0], 0, 0.0
        unvisited = set(range(1, self.n))
        while unvisited:
            nxt = min(unvisited, key=lambda j: self.dist[cur, j])
            total += self.dist[cur, nxt]
            cur = nxt
            unvisited.remove(nxt)
            tour.append(cur)
        return total + self.dist[cur, 0]

    def tour_length(self, tour):
        """计算一条环路的闭合总长度。"""
        return float(sum(self.dist[tour[i], tour[(i + 1) % self.n]] for i in range(self.n)))

    def _build_tour(self):
        """一只蚂蚁按状态转移概率构造一条完整环路，返回城市序列。"""
        start = int(self.rng.integers(self.n))
        tour = [start]
        unvisited = set(range(self.n))
        unvisited.remove(start)
        cur = start
        while unvisited:
            rest = list(unvisited)
            # p_ij ∝ tau^alpha * eta^beta（eta = 1/d，即距离越短权重越大）
            w = self.tau[cur, rest] ** self.alpha * self.eta[cur, rest] ** self.beta
            p = w / w.sum()
            nxt = self.rng.choice(rest, p=p)
            tour.append(nxt)
            unvisited.remove(nxt)
            cur = nxt
        return tour

    def run(self, verbose=True):
        """迭代求解，返回 (最优环路, 最优长度, 每轮最优长度历史)。"""
        best_tour, best_len = None, np.inf
        best_iter = 0                          # 最优最后更新的轮数（收敛判断用）
        history = []
        for it in range(1, self.n_iter + 1):
            tours, lens = [], []
            for _ in range(self.n_ants):       # 1) 所有蚂蚁构造环路
                t = self._build_tour()
                tours.append(t)
                lens.append(self.tour_length(t))
            # 2) 信息素蒸发（全局）
            self.tau *= (1.0 - self.rho)
            # 3) 每只蚂蚁在自己走过的边上释放 Q/L_k
            for t, L in zip(tours, lens):
                for i in range(self.n):
                    self.tau[t[i], t[(i + 1) % self.n]] += self.q / L
            # 4) 精英蚂蚁：额外加强历史最优路径，加速收敛
            if best_tour is not None:
                for i in range(self.n):
                    self.tau[best_tour[i], best_tour[(i + 1) % self.n]] += self.elite * self.q / best_len

            i_best = int(np.argmin(lens))
            if lens[i_best] < best_len:        # 更新历史最优
                best_tour, best_len, best_iter = tours[i_best], lens[i_best], it
            history.append(best_len)
            if verbose and (it % 5 == 0 or it == self.n_iter):
                print(f"  第 {it:2d}/{self.n_iter} 轮: 本轮最优 {lens[i_best]:.2f}，"
                      f"历史最优 {best_len:.2f}")
        return best_tour, best_len, history, best_iter


def brute_force_tsp(dist):
    """穷举求最短环路（n<=10 时用，评估启发式解质量）。固定 0 为起点枚举其余排列。"""
    n = len(dist)
    if n > 10:
        return None, None
    best_len, best_tour = np.inf, None
    for perm in itertools.permutations(range(1, n)):       # (n-1)! 种
        tour = (0,) + perm
        L = sum(dist[tour[i], tour[(i + 1) % n]] for i in range(n))
        if L < best_len:
            best_len, best_tour = L, tour
    return best_len, best_tour


if __name__ == "__main__":
    # 城市坐标：留空则用固定种子生成 10 个 [0,100]^2 内的点（换成题目数据只需改 CITIES）
    if not CITIES:
        rng = np.random.default_rng(SEED)
        CITIES = list(zip(rng.uniform(0, 100, N_CITIES), rng.uniform(0, 100, N_CITIES)))
    coords = CITIES
    n = len(coords)

    print(f"蚁群算法 TSP: {n} 个城市, {N_ANTS} 蚂蚁 × {N_ITER} 轮, seed={SEED}")
    print("[城市坐标]")
    for i, (x, y) in enumerate(coords):
        print(f"  城{i}: ({x:.1f}, {y:.1f})")

    aco = AntColonyTSP(coords)
    tour, length, hist, best_it = aco.run()

    # 收敛判断 + 结果输出
    stall = aco.n_iter - best_it
    print(f"\n[最优路径] {' -> '.join(str(c) for c in tour)} -> {tour[0]}")
    print(f"[总长度] {length:.4f}")
    print(f"[收敛判断] 最优在第 {best_it} 轮产生，其后 {stall} 轮无改进（已收敛）；"
          f"历史最优随轮次: 首轮 {hist[0]:.2f} → 末轮 {hist[-1]:.2f}（单调不增 ✓）")

    # 穷举校验（n<=10）：给出真实最优，量化 ACO 解质量
    if VERIFY_BRUTE:
        b_len, b_tour = brute_force_tsp(aco.dist)
        if b_len is not None:
            gap = (length - b_len) / b_len * 100
            print(f"[穷举校验] 真实最优长度 {b_len:.4f}，ACO 相对误差 {gap:.3f}% —— "
                  f"{'PASS（ACO 找到最优/接近最优）' if gap < 1e-6 else ('质量良好 ' + ('PASS' if gap <= 1.0 else 'FAIL，请调大 N_ITER/ELITE'))}")
