"""模糊综合评价模板（Fuzzy Comprehensive Evaluation, FCE）。

适用场景：多因素、评语带模糊性的综合评价问题——学生/教师/水质/服务质量/项目/方案
等"好中差"式评价（国赛/美赛评价类题、与 AHP 组合用：AHP 定权重、FCE 算隶属度）。
原理：因素集 U + 评语集 V + 权重向量 W + 隶属度矩阵 R → 模糊合成 B = W ∘ R，
     再按最大隶属度原则(或加权打分)给出结论。支持一级与二级(多级)评价。

输入：评语标签 v_labels；一级: 权重 w 与隶属度矩阵 R（R[i][j]=因素i 属于评语j 的程度，
      每行和为 1）；二级: 一级因素权重 w2，各一级因素下子因素权重列表 w1_list、
      隶属度矩阵列表 R_list（每个子矩阵行和为 1）。
输出：各级综合隶属度 B、最大隶属度结论、加权综合得分(给评语打分后加权)。
依赖：numpy。
⚠️ 注意：① 隶属度矩阵每行代表一个因素对评语集的隶属分布，行和应为 1（否则先归一）；
   ② 权重向量和应为 1；③ 打分法把评语等级折算成分值(如优=95)，便于横向比较与论文输出。
"""

# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy",):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np

# ========================== 问题参数（比赛时改这里换数据） ==========================
# ---------- 公共评语集（两种示例共用）----------
GRADE_LABELS = ["优", "良", "中", "较差", "差"]
GRADE_SCORES = [95, 80, 65, 45, 30]          # 评语等级 → 分（打分法用，可自定）

# ---------- 示例 1：一级评价——某课程"课堂教学质量" ----------
FACTORS1 = ["教学态度", "教学内容", "教学方法", "教学效果"]
W1 = np.array([0.20, 0.30, 0.30, 0.20])      # 各因素权重（和=1）
# 隶属度矩阵：行=因素，列=评语(优/良/中/较差/差)，每行和=1
R1 = np.array([
    [0.50, 0.30, 0.15, 0.05, 0.00],          # 教学态度
    [0.40, 0.35, 0.20, 0.05, 0.00],          # 教学内容
    [0.30, 0.30, 0.25, 0.10, 0.05],          # 教学方法
    [0.20, 0.25, 0.30, 0.15, 0.10],          # 教学效果
])

# ---------- 示例 2：二级评价——某课程"课程建设质量" ----------
# 一级因素(准则层)及其权重
FACTORS2 = ["教学资源", "课堂教学", "课程组织"]
W2 = np.array([0.30, 0.50, 0.20])
# 每个一级因素下的子因素名、子因素权重(和=1)、隶属度矩阵(行=子因素, 列=评语, 行和=1)
SUB_FACTORS2 = [
    (["资料丰富", "更新及时"],        np.array([0.60, 0.40])),
    (["内容准确", "生动有趣", "互动充分"], np.array([0.35, 0.35, 0.30])),
    (["进度合理", "考核公平"],        np.array([0.50, 0.50])),
]
R2 = [
    np.array([[0.60, 0.25, 0.10, 0.05, 0.00],   # 资料丰富
              [0.40, 0.35, 0.15, 0.10, 0.00]]), # 更新及时
    np.array([[0.50, 0.30, 0.15, 0.05, 0.00],   # 内容准确
              [0.35, 0.30, 0.20, 0.10, 0.05],   # 生动有趣
              [0.40, 0.40, 0.10, 0.10, 0.00]]), # 互动充分
    np.array([[0.45, 0.35, 0.15, 0.05, 0.00],   # 进度合理
              [0.30, 0.35, 0.20, 0.10, 0.05]]), # 考核公平
]
# ================================================================================


def fuzzy_compose(w, R, mode="weighted"):
    """模糊合成算子 B = W ∘ R。
    mode="weighted": 加权平均型 M(·,⊕)，b_j = Σ w_i r_ij（最常用，信息利用充分，推荐）；
    mode="maxmin":   主因素决定型 M(∧,∨)，b_j = max_i min(w_i, r_ij)（突出主要因素）。
    返回 B（一维数组，长度 = 评语个数；weighted 模式下 ΣB≈1，可视为综合隶属分布）。
    """
    w = np.asarray(w, dtype=float)
    R = np.asarray(R, dtype=float)
    assert w.ndim == 1 and R.ndim == 2 and len(w) == R.shape[0], "权重长度须 = 因素(行)数"
    assert np.isclose(w.sum(), 1.0), "权重之和应 = 1"
    if mode == "weighted":
        return w @ R
    if mode == "maxmin":
        # 逐评语取 min(w_i, r_ij) 后横向取 max
        return np.max(np.minimum(w[:, None], R), axis=0)
    raise ValueError(f"未知算子 mode={mode}，可选 'weighted' / 'maxmin'")


def conclude(B, labels=GRADE_LABELS):
    """最大隶属度原则定结论：隶属度最大的评语即综合评价等级。返回 (等级名, 隶属度)。"""
    B = np.asarray(B, dtype=float)
    idx = int(np.argmax(B))
    return labels[idx], B[idx]


def fuzzy_score(B, scores=GRADE_SCORES):
    """打分法：给评语等级赋分后加权，得 0~100 的量化综合得分（便于排序比较）。"""
    return float(np.asarray(B) @ np.asarray(scores, dtype=float))


def _print_B(title, B, labels):
    """打印一条综合隶属度分布 + 结论 + 得分。"""
    Bn = np.asarray(B, dtype=float)
    grade, mem = conclude(Bn, labels)
    print(f"\n[{title}]")
    row = "  " + "  ".join(f"{lb}: {v:.4f}" for lb, v in zip(labels, Bn))
    print(row + f"    (和={Bn.sum():.3f})")
    print(f"  最大隶属度结论: 属于「{grade}」 (隶属度 {mem:.4f})")
    print(f"  加权综合得分:   {fuzzy_score(Bn):.2f} 分 (评语分值 {GRADE_SCORES})")


def fuzzy_eval_level1(w, R, factors, labels=GRADE_LABELS):
    """一级模糊综合评价：输出综合隶属度 B、结论与得分。"""
    _print_B("一级评价结果 B = W∘R", fuzzy_compose(w, R), labels)
    return fuzzy_compose(w, R)


def fuzzy_eval_level2(w2, w1_list, R_list, factor_names, labels=GRADE_LABELS):
    """二级(多级)模糊综合评价。
    w2: 一级因素权重; w1_list/R_list: 各一级因素下的子权重与隶属矩阵;
    factor_names: 一级因素名。流程: 先逐一级因素做一级评价得 B_i → 以 B_i 为行组成
    二级隶属矩阵 → 再与 w2 合成得最终 B。返回最终 B。"""
    n_g = len(w2)
    B_level1 = []
    for i in range(n_g):
        # 第 i 个一级因素内部的子因素评价（先把行归一防浮点误差）
        Ri = np.asarray(R_list[i], dtype=float)
        Ri = Ri / Ri.sum(axis=1, keepdims=True)
        Bi = fuzzy_compose(w1_list[i], Ri)          # 一级(子层)综合隶属度
        B_level1.append(Bi)
        _print_B(f"一级因素「{factor_names[i]}」综合隶属度 B{i+1}", Bi, labels)
    B1_mat = np.array(B_level1)                     # 二级评价的隶属度矩阵
    _print_B(f"二级评价结果 B = W₂∘[B1;B2;B3]  — {factor_names}", fuzzy_compose(w2, B1_mat), labels)
    return fuzzy_compose(w2, B1_mat)


if __name__ == "__main__":
    print("=" * 68)
    print("【示例 1：一级模糊综合评价 —— 课堂教学质量】")
    print(f"因素集 U = {FACTORS1}")
    print(f"评语集 V = {GRADE_LABELS}")
    print(f"权重 W = {W1}")
    # 校验: 权重和 = 1, 隶属度行和 = 1
    assert np.isclose(W1.sum(), 1), "权重和应为 1"
    assert np.allclose(R1.sum(axis=1), 1), "隶属度矩阵每行和应为 1"
    B = fuzzy_eval_level1(W1, R1, FACTORS1)
    print("\n  → 加权平均算子 M(·,⊕) 信息利用充分，为论文默认；主因素决定型 M(∧,∨)")
    print("    可用 fuzzy_compose(W1, R1, mode='maxmin') 切换做敏感性对比。")

    print("\n" + "=" * 68)
    print("【示例 2：二级模糊综合评价 —— 课程建设质量】")
    print(f"一级因素集 U = {FACTORS2}，一级权重 W₂ = {W2}")
    print("  (每个一级因素下有若干子因素；评语集同上)")
    B2 = fuzzy_eval_level2(W2, [s[1] for s in SUB_FACTORS2], R2, FACTORS2)
    print("\n  → 二级结论即最终评价；若需三级以上，逐层把上层 B 当隶属度行重复合成即可。")
