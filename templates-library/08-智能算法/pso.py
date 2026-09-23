"""粒子群优化 (PSO) 模板 — 连续优化。

适用场景：非线性连续优化、参数寻优（神经网络权重、模型参数标定）。
原理：粒子追踪个体最优 pbest 与全局最优 gbest 更新速度与位置。

自定义：改 fitness()；示例为 Sphere 函数最小值。
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy",):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np


class ParticleSwarm:
    def __init__(self, n_var=2, bounds=(-10, 10), n_particles=40,
                 n_iterations=200, w=0.7, c1=1.5, c2=1.5, seed=42):
        self.n_var = n_var
        self.lb, self.ub = bounds
        self.n = n_particles
        self.n_iter = n_iterations
        self.w, self.c1, self.c2 = w, c1, c2
        self.rng = np.random.default_rng(seed)

    def fitness(self, x):
        """目标（找最小）。默认 Sphere: sum(x^2)。"""
        return np.sum(x**2)

    def run(self, verbose=True):
        lb, ub = self.lb, self.ub
        x = self.rng.uniform(lb, ub, (self.n, self.n_var))
        v = self.rng.uniform(-(ub - lb), ub - lb, (self.n, self.n_var)) * 0.1
        pbest = x.copy()
        pbest_f = np.array([self.fitness(xi) for xi in x])
        gbest = pbest[np.argmin(pbest_f)].copy()
        gbest_f = pbest_f.min()
        history = []
        for it in range(self.n_iter):
            r1, r2 = self.rng.random((self.n, self.n_var)), self.rng.random((self.n, self.n_var))
            v = self.w * v + self.c1 * r1 * (pbest - x) + self.c2 * r2 * (gbest - x)
            x = np.clip(x + v, lb, ub)
            for i in range(self.n):
                f = self.fitness(x[i])
                if f < pbest_f[i]:
                    pbest_f[i], pbest[i] = f, x[i].copy()
                if f < gbest_f:
                    gbest_f, gbest = f, x[i].copy()
            history.append(gbest_f)
            if verbose and (it + 1) % 50 == 0:
                print(f"  第 {it+1} 次迭代: 最优 {gbest_f:.6f}")
        return gbest, gbest_f, history


if __name__ == "__main__":
    pso = ParticleSwarm(n_var=2, bounds=(-10, 10))
    x, f, history = pso.run()
    print(f"\n[PSO 结果] x = {np.round(x, 4)}, f(x) = {f:.6f}")
    print(f"[理论最优] x = [0, 0], f = 0")
