"""层次分析法 (AHP) 模板。

适用场景：多准则决策（选最优方案/排序），评价类问题首选（国赛、美赛 E/F 常见）。
流程：判断矩阵 → 一致性检验 (CR<0.1) → 特征向量法求权重 → 方案合成总排序。

输入：准则判断矩阵 criteria_matrix + 每个准则下方案判断矩阵 scheme_matrices（或直接用分数）。
输出：各准则权重 + 方案总排序。

⚠️ 评委关注点：判断矩阵一致性必须检验；CR>0.1 说明判断矛盾，需重填矩阵。
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy",):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np


def ahp_weight(A):
    """由判断矩阵 A 求权重向量 + 一致性比率 CR。"""
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    # 特征向量法（主特征向量归一化）
    eigvals, eigvecs = np.linalg.eig(A)
    idx = np.argmax(eigvals.real)
    lam_max = eigvals.real[idx]
    w = np.abs(eigvecs[:, idx].real)
    w = w / w.sum()

    # 一致性检验
    CI = (lam_max - n) / (n - 1)
    RI = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24,
          7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}  # 随机一致性指标
    CR = CI / RI.get(n, 1.49)
    return w, CR, lam_max


def ahp_synthesize(criteria_matrix, scheme_matrices):
    """合成总排序。criteria_matrix: 准则间判断矩阵；
    scheme_matrices: list，每个准则下方案间的判断矩阵。
    返回 (准则权重, 各准则下方案权重, 总排序权重)。"""
    w_c, CR_c, _ = ahp_weight(criteria_matrix)
    print(f"[准则权重] {np.round(w_c, 4)}   CR={CR_c:.4f} {'✓' if CR_c < 0.1 else '✗ 一致性不合格!'}")

    n_scheme = scheme_matrices[0].shape[0]
    W = np.zeros((len(scheme_matrices), n_scheme))
    for k, S in enumerate(scheme_matrices):
        w_s, CR_s, _ = ahp_weight(S)
        W[k] = w_s
        print(f"[准则{k+1}下方案权重] {np.round(w_s, 4)}   CR={CR_s:.4f} {'✓' if CR_s < 0.1 else '✗'}")

    total = w_c @ W
    print(f"\n[方案总排序] {np.round(total, 4)}")
    print(f"  最优方案: 方案{np.argmax(total) + 1} (权重 {total.max():.4f})")
    return w_c, W, total


if __name__ == "__main__":
    # 示例：选方案——3 个方案, 4 个准则（成本/效益/风险/可实施性）
    criteria = [
        [1, 1/3, 1/5, 1/2],
        [3, 1,   1/3, 2],
        [5, 3,   1,   3],
        [2, 1/2, 1/3, 1],
    ]
    schemes = [
        [[1, 3, 1/2], [1/3, 1, 1/5], [2, 5, 1]],      # 准则 1 下
        [[1, 1/2, 1/3], [2, 1, 1/2], [3, 2, 1]],      # 准则 2 下
        [[1, 5, 2], [1/5, 1, 1/3], [1/2, 3, 1]],      # 准则 3 下
        [[1, 1/3, 2], [3, 1, 4], [1/2, 1/4, 1]],      # 准则 4 下
    ]
    ahp_synthesize(np.array(criteria), [np.array(s) for s in schemes])
