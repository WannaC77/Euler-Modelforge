"""TOPSIS + 熵权法组合模板（客观赋权 + 逼近理想解排序）。

适用场景：多指标综合评价排序（国赛、美赛 E/F 常见）。熵权法定权重（客观），TOPSIS 排序。
流程：正向化（极小型→极大型）→ 归一化 → 熵权法求权重 → 加权 → 与正负理想解距离 → 贴近度排序。

输入：X (n 方案 × m 指标) + 每列指标类型（极大/极小/区间）。
输出：各方案得分与排名。
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy",):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np


def normalize(X, types):
    """正向化 + 极差归一化。types[i]='max' 或 'min'。"""
    X = np.asarray(X, dtype=float)
    Y = X.copy()
    for j, t in enumerate(types):
        col = X[:, j]
        if t == "min":
            Y[:, j] = col.max() - col           # 极小型转极大型
        # 区间型可扩展（这里只处理极值型）
    # 极差归一化
    mins, maxs = Y.min(axis=0), Y.max(axis=0)
    Z = (Y - mins) / (maxs - mins + 1e-12)
    return Z


def entropy_weight(Z):
    """熵权法求指标权重。Z: 已归一化(非负)。"""
    Z = np.asarray(Z, dtype=float)
    P = Z / (Z.sum(axis=0) + 1e-12)                       # 比重
    k = 1.0 / np.log(Z.shape[0])
    e = -k * np.sum(P * np.log(P + 1e-12), axis=0)        # 信息熵
    d = 1 - e                                             # 差异系数
    w = d / d.sum()
    return w


def topsis(Z, w):
    """TOPSIS 排序。返回 (贴近度数组, 排名)。"""
    n = Z.shape[0]
    V = Z * w                                            # 加权
    ideal_pos = V.max(axis=0)
    ideal_neg = V.min(axis=0)
    d_pos = np.sqrt(((V - ideal_pos) ** 2).sum(axis=1))
    d_neg = np.sqrt(((V - ideal_neg) ** 2).sum(axis=1))
    score = d_neg / (d_pos + d_neg + 1e-12)              # 贴近度
    rank = np.argsort(-score)
    return score, rank


if __name__ == "__main__":
    # 示例：4 家供应商 × 3 指标（价格[极小], 质量[极大], 交付[极大]）
    X = [
        [85, 90, 70],   # 供应商 A
        [92, 78, 85],   # B
        [70, 95, 60],   # C
        [80, 88, 92],   # D
    ]
    types = ["min", "max", "max"]

    Z = normalize(X, types)
    w = entropy_weight(Z)
    score, rank = topsis(Z, w)

    print(f"[熵权法权重] {np.round(w, 4)}")
    for i in range(len(X)):
        print(f"  方案{i+1}: 贴近度={score[i]:.4f}  排名={np.where(rank == i)[0][0] + 1}")
