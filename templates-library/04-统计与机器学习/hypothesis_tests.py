"""假设检验速查套件（正态性 / t 检验 / ANOVA / 卡方 / 相关）。

适用场景：比赛里"两组差异是否显著 / 多组是否有别 / 两变量是否相关"类问题。
        拿到数据先看分布类型再选检验，p<0.05 拒绝 H0 已按惯例实现。

输入格式：一维数组（检验样本）或分组列表；卡方需传入列联表(二维)。
输出格式：控制台打印每个检验的 统计量 + p 值 + 结论(α=0.05)。
依赖：numpy、scipy。
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy", "scipy"):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np
from scipy import stats


def conclude(p, alpha=0.05):
    """按 p 值下结论: p<α 拒绝 H0，否则不能拒绝 H0。"""
    return "拒绝 H0（差异显著）" if p < alpha else "不能拒绝 H0（差异不显著）"


def shapiro_test(x):
    """正态性检验 Shapiro-Wilk。H0: 样本来自正态总体。
    返回 (W 统计量, p 值)。注意样本量需 3<=n<=5000。"""
    return stats.shapiro(np.asarray(x, dtype=float))


def t_test_two_samples(a, b, equal_var=None):
    """两独立样本 t 检验。H0: 两组均值相等。
    equal_var=None 时先做 Levene 方差齐性检验自动选择:
    方差不齐→Welch t 检验; 方差齐→Student t 检验。返回 (t, p, 所用方法)。"""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if equal_var is None:
        equal_var = stats.levene(a, b).pvalue > 0.05   # 方差齐则用 Student
    method = "Welch t (方差不齐)" if not equal_var else "Student t (方差齐)"
    t, p = stats.ttest_ind(a, b, equal_var=equal_var)
    return t, p, method


def paired_t_test(before, after):
    """配对样本 t 检验（同一对象前后测/两种处理）。H0: 差值的均值=0。返回 (t, p)。"""
    return stats.ttest_rel(np.asarray(before, float), np.asarray(after, float))


def oneway_anova(*groups):
    """单因素方差分析。H0: 多组（≥3）均值全相等。返回 (F, p)。"""
    return stats.f_oneway(*[np.asarray(g, float) for g in groups])


def chi2_independence(table):
    """卡方独立性检验（列联表）。H0: 行/列两分类变量相互独立。
    table: 二维计数表。返回 (chi2, p, 自由度)。"""
    chi2, p, dof, _ = stats.chi2_contingency(np.asarray(table))
    return chi2, p, dof


def pearson_corr(x, y):
    """Pearson 相关（两变量均近似正态、线性关系时用）。H0: r=0。返回 (r, p)。"""
    return stats.pearsonr(x, y)


def spearman_corr(x, y):
    """Spearman 秩相关（不要求正态，捕捉单调关系；有异常值更稳健）。H0: ρ=0。返回 (ρ, p)。"""
    return stats.spearmanr(x, y)


if __name__ == "__main__":
    # ===== 示例参数（改这里换你的数据：x/y 传一维数组即可）=====
    rng = np.random.default_rng(42)   # 固定随机种子，保证可复现
    n = 60
    alpha = 0.05

    print("=" * 62)
    print(f"【假设检验速查演示】显著性水平 α = {alpha}")

    # [1] 正态性 Shapiro：一组正态样本(应不拒绝) + 一组偏态样本(应拒绝)
    normal_x = rng.normal(50, 10, n)
    skewed_x = rng.exponential(scale=5, size=n)   # 指数分布，明显右偏
    for name, x in [("正态样本(对照组)", normal_x), ("指数分布样本(偏态)", skewed_x)]:
        W, p = shapiro_test(x)
        print(f"\n[1] Shapiro-Wilk 正态性检验 | {name}")
        print(f"    W = {W:.4f}, p = {p:.4g} → {conclude(p, alpha)}")

    # [2] 两独立样本 t：制造均值差 12 的两组 → 期望显著
    grp_a = rng.normal(100, 15, n)
    grp_b = rng.normal(112, 15, n)
    t, p, method = t_test_two_samples(grp_a, grp_b)
    print(f"\n[2] 两独立样本 t 检验 | 组A(μ≈100) vs 组B(μ≈112), 各 {n} 人")
    print(f"    {method}: t = {t:.3f}, p = {p:.4g} → {conclude(p, alpha)}")
    print(f"    组均值: A = {grp_a.mean():.2f}, B = {grp_b.mean():.2f}")

    # [3] 配对 t：同 60 人"训练前后"成绩，制造约 +6 分效果 → 期望显著
    before = rng.normal(70, 10, n)
    after = before + rng.normal(6, 4, n)
    t, p = paired_t_test(before, after)
    print(f"\n[3] 配对样本 t 检验 | 训练前后成绩, 前后均值差 = {(after - before).mean():.2f}")
    print(f"    t = {t:.3f}, p = {p:.4g} → {conclude(p, alpha)}")

    # [4] 单因素 ANOVA：三组均值 10/12/16 → 期望显著
    g = [rng.normal(mu, 4, 50) for mu in (10, 12, 16)]
    F, p = oneway_anova(*g)
    print(f"\n[4] 单因素 ANOVA | 三组样本量各 50, 组均值 = "
          f"{[round(float(x.mean()), 2) for x in g]}")
    print(f"    F = {F:.3f}, p = {p:.4g} → {conclude(p, alpha)}")

    # [5] 卡方独立性：药物×疗效 2x2 表（疗效依赖用药）→ 期望拒绝独立
    tbl = np.array([[70, 30],   # 用药组: 有效70 无效30
                    [40, 60]])  # 安慰剂: 有效40 无效60
    chi2, p, dof = chi2_independence(tbl)
    print(f"\n[5] 卡方独立性检验 | 药物×疗效列联表:\n{tbl}")
    print(f"    chi2 = {chi2:.3f}, 自由度 = {dof}, p = {p:.4g} → {conclude(p, alpha)}")

    # [6] 相关：正相关(线性)用 Pearson, 单调(非线性)用 Spearman
    x = rng.normal(0, 1, n)
    y_lin = 2 * x + rng.normal(0, 0.5, n)        # 强线性正相关
    y_mono = np.exp(x)                            # 单调非线性（指数关系）
    r_p, p_p = pearson_corr(x, y_lin)
    r_s, p_s = spearman_corr(x, y_mono)
    print(f"\n[6] 相关分析:")
    print(f"    Pearson  (线性关系 y=2x+ε):   r = {r_p:.3f}, p = {p_p:.4g} → {conclude(p_p, alpha)}")
    print(f"    Spearman  (指数关系 y=e^x):    ρ = {r_s:.3f}, p = {p_s:.4g} → {conclude(p_s, alpha)}")

    print("\n[检验] 全套 PASS: Shapiro / 独立t / 配对t / ANOVA / 卡方 / Pearson / Spearman")
