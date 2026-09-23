"""模拟退火 (SA) 模板 — 连续函数全局最小值搜索。

适用场景：多峰/非凸连续优化、梯度法易陷入局部最优的问题（模型参数标定、函数拟合、
         布局/调度设计）；决策变量离散化后亦可解组合优化（如 TSP，可参考 aco_tsp.py）。
降温方式：线性降温  T(k) = T0 + (T_END - T0) * k / K   （直观稳定，比赛常用）。
收敛判断：记录"历史最优最后更新的迭代号"，末段最优值长期不改进即视为收敛；
          另用多次独立重启（不同随机起点）降低陷入局部最优的概率。
示例：Rastrigin 二维函数（多峰、全局最小 f=0 在原点），验证收敛到接近全局最优。
输入格式：在"问题参数区"改目标函数 fun_rastrigin / 边界 LB~UB / 退火超参。
输出：每段重启的最优值与收敛位置、全局最优解 x 与最优值 f、PASS 判定。
依赖：numpy（requirements.txt 已含）。

比赛用法：
    1. 把 fun_rastrigin 换成你的目标函数（或子类覆盖 fitness）
    2. 运行 python sa.py
    3. 收敛后把 x* 与 f(x*) 写入论文（可配一张降温-收敛曲线图）
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy",):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np

# ============ 问题参数（改这里即可）============
SEED = 42                     # 随机种子（保证可复现）
N_VAR = 2                     # 决策变量维数
LB, UB = -5.12, 5.12          # 每维变量的下界 / 上界
T0 = 50.0                     # 初始温度
T_END = 0.001                 # 终止温度（线性降温的终点）
K_ITER = 30000                # 每段重启内的迭代步数（线性降温总步数）
N_RESTART = 3                 # 独立重启段数（多起点，提高全局收敛概率）
STEP0 = 1.2                   # 初始邻域步长尺度；随温度收缩 s = STEP0 * sqrt(T/T0)
PASS_F = 0.05                 # 判定"已接近全局最优"的最优值阈值


def fun_rastrigin(x):
    """目标函数：Rastrigin。多峰，大量局部极小，用于检验全局搜索能力。

    全局最小 f=0 @ x=(0,0,...,0)。换问题只需改本函数。
    """
    return 10.0 * len(x) + float(np.sum(x ** 2 - 10.0 * np.cos(2.0 * np.pi * x)))
# ==============================================


class SimulatedAnnealing:
    """模拟退火求解器。默认目标 fun_rastrigin，可子类覆盖 fitness() 换问题。"""

    def __init__(self, n_var=N_VAR, lb=LB, ub=UB, t0=T0, t_end=T_END,
                 k_iter=K_ITER, step0=STEP0, seed=SEED):
        self.n = n_var
        self.lb, self.ub = lb, ub
        self.t0, self.t_end = t0, t_end
        self.k = k_iter
        self.step0 = step0
        self.rng = np.random.default_rng(seed)

    def fitness(self, x):
        """目标函数值（越小越好）。换问题：子类覆盖或直接改 fun_rastrigin。"""
        return fun_rastrigin(x)

    def _reflect(self, x):
        """把越界的试探点按边界反射回可行域（比截断更利于边界搜索）。"""
        for i in range(self.n):
            while x[i] < self.lb or x[i] > self.ub:
                if x[i] < self.lb:
                    x[i] = 2.0 * self.lb - x[i]
                if x[i] > self.ub:
                    x[i] = 2.0 * self.ub - x[i]
        return x

    def run_restart(self, x_start, verbose=True):
        """跑一段完整的线性降温（K_ITER 步），返回该段 (best_x, best_f, last_improve_k)。

        last_improve_k: 该段内最后一次刷新历史最优的迭代号，用于收敛判断。
        """
        x = np.array(x_start, dtype=float)
        f = self.fitness(x)
        best_x, best_f, last_improve = x.copy(), f, 0
        for k in range(1, self.k + 1):
            # 线性降温：温度从 T0 均匀降到 T_END
            T = self.t0 + (self.t_end - self.t0) * k / self.k
            # 邻域步长随温度收缩：高温大步探索，低温小步精细爬坡
            s = self.step0 * np.sqrt(max(T, 1e-9) / self.t0)
            x_new = self._reflect(x + self.rng.normal(0.0, s, self.n))
            f_new = self.fitness(x_new)
            # Metropolis 接受准则：更优必接受；更差按 exp(-Δ/T) 概率接受（跳出局部最优）
            delta = f_new - f
            if delta < 0 or self.rng.random() < np.exp(-delta / T):
                x, f = x_new, f_new
                if f < best_f:
                    best_f, best_x, last_improve = f, x.copy(), k
        if verbose:
            stall = self.k - last_improve
            print(f"  段最优 f = {best_f:.2e} @ x={np.round(best_x, 5)}，"
                  f"第 {last_improve} 步后不再改进（末段 {stall} 步无更新 → 已收敛）")
        return best_x, best_f, last_improve

    def run(self):
        """多段独立重启，返回全局 (best_x, best_f, 各段最优列表)。"""
        rng0 = self.rng
        all_best = []
        global_x, global_f = None, np.inf
        for r in range(N_RESTART):
            print(f"--- 第 {r + 1}/{N_RESTART} 段重启 ---")
            # 每段随机初始点（在可行域内均匀抽样）
            x0 = rng0.uniform(self.lb, self.ub, self.n)
            bx, bf, _ = self.run_restart(x0)
            all_best.append(bf)
            if bf < global_f:
                global_f, global_x = bf, bx
        return global_x, global_f, all_best


if __name__ == "__main__":
    print(f"模拟退火: Rastrigin {N_VAR} 维, 线性降温 {T0} -> {T_END}, "
          f"每段 {K_ITER} 步 × {N_RESTART} 段, seed={SEED}")
    sa = SimulatedAnnealing()
    x, f, seg = sa.run()
    print(f"\n[SA 全局最优] x = {np.round(x, 6)}, f(x) = {f:.6e}")
    print(f"[理论全局最优] x = [0, 0], f = 0（Rastrigin 全局最小）")
    print(f"[收敛判定] |f - 0| = {abs(f):.2e} "
          f"{'< 阈值 ' + str(PASS_F) + ' → 接近全局最优 PASS' if abs(f) < PASS_F else '≥ 阈值 FAIL（增大 K_ITER/N_RESTART 或调 STEP0）'}")
