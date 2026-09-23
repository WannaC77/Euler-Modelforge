"""灰色关联分析模板（Grey Relational Analysis）。

适用场景：小样本方案选优 / 因素关联度分析（国赛 B/C 高频）。
原理：构造理想参考序列（各指标最优值），计算每个方案与它的灰色关联度，越大越优。
流程：正向化 → 无量纲化（均值像）→ 灰色关联系数 → 等权关联度 → 排序。

输入：X (n 方案 × m 指标) + 每列指标类型（'max'/'min'）+ 分辨系数 rho（默认 0.5）。
输出：各方案与理想参考的关联度及排名。
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy",):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np


def forward(X, types):
    """正向化：极小型转极大型。"""
    X = np.asarray(X, dtype=float)
    Y = X.copy()
    for j, t in enumerate(types):
        if t == "min":
            Y[:, j] = X[:, j].max() - X[:, j]
    return Y


def grey_relation(Y, rho=0.5):
    """灰色关联度方案选优。Y 已正向化（全为越大越好）。

    参考序列自动取各指标最优值（理想方案），返回 (关联度数组, 排名)。
    """
    Y = np.asarray(Y, dtype=float)
    x0 = Y.max(axis=0)                             # 理想参考序列（各列最优，原始量纲）
    orig_mean = Y.mean(axis=0) + 1e-12
    Y = Y / orig_mean                              # 无量纲化：均值像
    x0 = x0 / orig_mean                            # 参考序列按同一规则无量纲化
    d = np.abs(Y - x0)                             # |x0 - xi|
    d_min, d_max = d.min(), d.max()
    coef = (d_min + rho * d_max) / (d + rho * d_max + 1e-12)
    degree = coef.mean(axis=1)                     # 每个方案的等权关联度
    rank = np.argsort(-degree)
    return degree, rank


if __name__ == "__main__":
    # 示例：4 家供应商 × 3 指标（价格[极小], 质量[极大], 交付[极大]）
    X = [
        [85, 90, 70],   # 供应商 A
        [92, 78, 85],   # B
        [70, 95, 60],   # C
        [80, 88, 92],   # D
    ]
    types = ["min", "max", "max"]

    Y = forward(X, types)
    degree, rank = grey_relation(Y)

    print("[灰色关联度]（理想参考序列）")
    for i in range(len(X)):
        print(f"  方案{i+1}: 关联度={degree[i]:.4f}  排名={np.where(rank == i)[0][0] + 1}")
    print(f"  最优方案 = 方案{rank[0] + 1}（与理想参考关联度最大）")
