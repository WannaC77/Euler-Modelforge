"""多元线性回归预测模板（statsmodels OLS）。

适用场景：多个自变量 X 预测/解释因变量 y（连续型），如房价预测、需求预测、
影响因素分析（回归系数解释边际效应）。数模预测/评价类题目的通用"基线模型"。

原理：y = β0 + β1x1 + ... + βk xk + ε，最小二乘估计 + 显著性检验（t 检验逐系数、
F 检验整体），可用 R² 判断拟合优度。

输入：X 为 n×k 矩阵（自变量，列名可给）、y 为 n 维向量、new_X 为待预测的新样本矩阵。
输出：R²、调整 R²、整体 F 检验、各系数(含常数项)的系数/标准误/t 值/p 值/显著性星号、
      新样本的点预测与 95% 预测区间。
依赖：numpy、pandas、statsmodels。
⚠️ 局限：要求线性关系；自变量间高度相关(多重共线性)会使系数不稳定（可先算 VIF 筛查）；
   解释变量显著 ≠ 因果关系；异常值对最小二乘影响大（先画散点/箱线图排查）。
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm

# ========================== 问题参数（比赛时改这里换数据） ==========================
np.random.seed(123)          # 固定随机种子，保证示例可复现

# 示例：房屋总价(万元) ~ 面积/卧室数/楼龄/距地铁 4 个自变量（n=40 套）
# 比赛时换成真实数据即可，例如:
#   df = pd.read_excel("data.xlsx");  X = df[["面积","卧室数","楼龄","距地铁"]];  y = df["总价"]
N = 40
X_names = ["面积(㎡)", "卧室数(间)", "楼龄(年)", "距地铁(km)"]     # 自变量列名
_x1 = np.random.uniform(60, 160, N)                              # 面积 60~160 ㎡
_x2 = np.random.randint(2, 6, N).astype(float)                   # 卧室 2~5 间
_x3 = np.random.uniform(0, 30, N)                                # 楼龄 0~30 年
_x4 = np.random.exponential(2.5, N)                              # 距地铁站 km
X_example = np.column_stack([_x1, _x2, _x3, _x4])
# 真实关系: 总价 = 20 + 0.7*面积 + 4.5*卧室 - 1.3*楼龄 - 3.0*距地铁 + 噪声
y_example = (20 + 0.7 * _x1 + 4.5 * _x2 - 1.3 * _x3
             - 3.0 * _x4 + np.random.normal(0, 8, N))

# 待预测的新样本（比赛时改为要预测的行）
NEW_X = np.array([
    [120.0, 3, 5, 1.2],      # 新样本 1：120㎡ 三室 5 年楼龄 距地铁 1.2km
    [85.0,  2, 18, 3.5],     # 新样本 2：85㎡  两室 18 年楼龄 距地铁 3.5km
])
# ================================================================================


def p_stars(p):
    """显著性星号：*** p<0.001, ** p<0.01, * p<0.05, . p<0.1"""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    if p < 0.1:
        return "."
    return ""


def fit_ols(X, y, names=None):
    """OLS 拟合。X: n×k 矩阵(自动加常数项)；names: 自变量名列表；返回 fitted 结果。"""
    X_df = pd.DataFrame(np.asarray(X, dtype=float), columns=names)
    Xc = sm.add_constant(X_df, has_constant="add")     # 加常数项 β0
    y = np.asarray(y, dtype=float)
    return sm.OLS(y, Xc).fit()


def print_regression_result(res, Xc_columns):
    """打印回归核心结果：整体检验 + 系数表 + 显著性星号。"""
    n, k = int(res.nobs), int(res.df_model) + 1        # 样本量、总参数个数(含常数)
    print("[模型整体拟合]")
    print(f"  样本量 n = {n}，自变量个数 k = {k - 1}（含常数项共 {k} 个参数）")
    print(f"  R²      = {res.rsquared:.4f}   （越接近 1 拟合越好）")
    print(f"  调整 R² = {res.rsquared_adj:.4f}   （惩罚自变量个数后的 R²）")
    print(f"  F 检验  = F({int(res.df_model)}, {int(res.df_resid)}) = {res.fvalue:.2f}, "
          f"P 值 = {res.f_pvalue:.3e}  → 模型整体{'显著' if res.f_pvalue < 0.05 else '不显著'}")
    print(f"  残差标准差 σ = {np.sqrt(res.mse_resid):.3f}")

    print("\n[回归系数表]  (常数项为 Intercept)")
    print(f"  {'变量':<12}{'系数':>10}{'标准误':>10}{'t 值':>10}{'P>|t|':>12}{'显著性':>6}")
    for name, coef, se, t, p in zip(Xc_columns, res.params, res.bse, res.tvalues, res.pvalues):
        print(f"  {name:<12}{coef:>10.4f}{se:>10.4f}{t:>10.3f}{p:>12.2e}{p_stars(p):>6}")
    print("  显著性: *** p<0.001  ** p<0.01  * p<0.05  . p<0.1")
    eq = " ".join(f"{'+' if c >= 0 else '-'} {abs(c):.4f}×{nm}"
                  for c, nm in zip(res.params.iloc[1:], Xc_columns[1:]))
    print(f"  → 回归方程: y = {res.params.iloc[0]:.2f} {eq}")


def predict_new(res, new_X, names):
    """对新样本 new_X(k×m) 做点预测并给出 95% 预测区间（含观测噪声带宽）。"""
    new_df = pd.DataFrame(np.asarray(new_X, dtype=float), columns=names)
    new_df = sm.add_constant(new_df, has_constant="add")      # 保持与训练时一致的列序
    pf = res.get_prediction(new_df).summary_frame(alpha=0.05)
    print("\n[新样本预测]  (mean=点预测, obs 区间=95% 预测区间)")
    for i, (_, row) in enumerate(pf.iterrows(), start=1):
        print(f"  样本{i}: 点预测 {row['mean']:9.2f} 万元   95% 区间 "
              f"[{row['obs_ci_lower']:.2f}, {row['obs_ci_upper']:.2f}]")


if __name__ == "__main__":
    res = fit_ols(X_example, y_example, names=X_names)
    # 拟合结果的系数名（含 "const" 常数项，展示时改成中文 "常数项"）
    cols = ["常数项" if c == "const" else c for c in res.params.index]
    print_regression_result(res, cols)
    predict_new(res, NEW_X, X_names)
