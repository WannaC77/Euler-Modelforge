"""遗传算法 (GA) 模板 — 求解通用优化问题。

适用场景：非线性/组合优化、无解析解、传统算法难解的问题（调度、路径、多峰函数）。
流程：编码 → 初始化种群 → 适应度 → 选择/交叉/变异 → 迭代 → 最优解。

自定义方法：改 fitness() 与解码；示例为 Rastrigin 函数最小值。
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy",):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np


class GeneticAlgorithm:
    def __init__(self, n_var=2, bounds=(-5.12, 5.12), pop_size=50,
                 n_generations=200, crossover_prob=0.8, mutation_prob=0.1, seed=42):
        self.n_var = n_var
        self.lb, self.ub = bounds
        self.pop_size = pop_size
        self.n_gen = n_generations
        self.pc, self.pm = crossover_prob, mutation_prob
        self.rng = np.random.default_rng(seed)

    def fitness(self, x):
        """适应度 = 目标函数值（GA 找最小）。子类可覆盖。默认 Rastrigin。"""
        return 10 * self.n_var + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))

    def init_pop(self):
        return self.rng.uniform(self.lb, self.ub, (self.pop_size, self.n_var))

    def selection(self, pop, fits):
        """锦标赛选择。"""
        idx = np.array([self.rng.choice(self.pop_size, 2, replace=False) for _ in range(self.pop_size)])
        winners = np.array([idx[i, 0] if fits[idx[i, 0]] < fits[idx[i, 1]] else idx[i, 1]
                            for i in range(self.pop_size)])
        return pop[winners]

    def crossover(self, pop):
        child = pop.copy()
        for i in range(0, self.pop_size - 1, 2):
            if self.rng.random() < self.pc:
                alpha = self.rng.uniform(0, 1, self.n_var)
                child[i] = alpha * pop[i] + (1 - alpha) * pop[i + 1]
                child[i + 1] = alpha * pop[i + 1] + (1 - alpha) * pop[i]
        return child

    def mutate(self, pop):
        mask = self.rng.random(pop.shape) < self.pm
        noise = self.rng.normal(0, 0.1 * (self.ub - self.lb), pop.shape)
        pop = pop + mask * noise
        return np.clip(pop, self.lb, self.ub)

    def run(self, verbose=True):
        pop = self.init_pop()
        best_fit, best_x = np.inf, None
        history = []
        for gen in range(self.n_gen):
            fits = np.array([self.fitness(x) for x in pop])
            i_best = np.argmin(fits)
            if fits[i_best] < best_fit:
                best_fit, best_x = fits[i_best], pop[i_best].copy()
            history.append(best_fit)
            pop = self.crossover(self.selection(pop, fits))
            pop = self.mutate(pop)
            if verbose and (gen + 1) % 50 == 0:
                print(f"  第 {gen+1} 代: 最优 {best_fit:.4f}")
        return best_x, best_fit, history


if __name__ == "__main__":
    ga = GeneticAlgorithm(n_var=2)
    x, f, history = ga.run()
    print(f"\n[GA 结果] x = {np.round(x, 4)}, f(x) = {f:.6f}")
    print(f"[理论最优] x = [0, 0], f = 0")
