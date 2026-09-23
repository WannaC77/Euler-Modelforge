"""监督学习套件（回归 RandomForestRegressor；分类 LogisticRegression vs RandomForestClassifier）。

适用场景：有标签数据建预测模型——国赛 C/美赛 C 的"给出指标预测结果/分类判断"类问题。
流程：切分训练测试 → 训练 → 指标评估 → 特征重要性排序（指导降维与解释）。
输入格式：X（n×m 数值特征矩阵，numpy 或 pandas）、y（回归连续值 / 分类 0,1,2…标签）。
输出格式：控制台打印回归 R²/MAE、分类 accuracy/F1/混淆矩阵、Top 特征重要性。
依赖：scikit-learn、numpy。
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy", "sklearn"):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np


def evaluate_regression(X, y, test_size=0.2, seed=42, n_estimators=200):
    """回归评估：随机森林回归。返回 {r2, mae, rmse, 特征重要性数组}。
    用途：X→连续值预测（销量、价格、指标值）。"""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import train_test_split

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size, random_state=seed)
    model = RandomForestRegressor(n_estimators=n_estimators, random_state=seed).fit(Xtr, ytr)
    pred = model.predict(Xte)
    return {
        "r2": r2_score(yte, pred),
        "mae": mean_absolute_error(yte, pred),
        "rmse": float(np.sqrt(mean_squared_error(yte, pred))),
        "importance": model.feature_importances_,
        "model": model,
    }


def evaluate_classifiers(X, y, test_size=0.2, seed=42):
    """分类评估与对比：LogisticRegression（线性基准）vs RandomForestClassifier。
    返回 {accuracy, f1, 混淆矩阵, 特征重要性} 的字典列表，按模型名索引。
    用途：X→离散类别预测（是否违约、等级判定）。"""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
    from sklearn.model_selection import train_test_split

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size, random_state=seed)
    results = {}
    for name, model in [
        ("LogisticRegression",
         LogisticRegression(max_iter=2000, random_state=seed)),
        ("RandomForest",
         RandomForestClassifier(n_estimators=200, random_state=seed)),
    ]:
        model.fit(Xtr, ytr)
        pred = model.predict(Xte)
        results[name] = {
            "accuracy": accuracy_score(yte, pred),
            "f1_macro": f1_score(yte, pred, average="macro"),
            "confusion": confusion_matrix(yte, pred),
            "importance": (model.feature_importances_ if hasattr(model, "feature_importances_")
                           else np.zeros(X.shape[1])),
            "model": model,
        }
    return results


def top_features(importance, feature_names=None, k=5):
    """特征重要性排序：返回 (排名前 k 的特征名或下标, 对应重要性) 两个数组。"""
    idx = np.argsort(importance)[::-1][:k]
    names = (np.asarray(feature_names)[idx] if feature_names is not None
             else np.asarray([f"特征{i}" for i in idx]))
    return names, importance[idx]


if __name__ == "__main__":
    # ===== 示例参数（改这里换数据：X=你的特征表, y=你的目标列）=====
    from sklearn.datasets import make_classification, make_regression

    print("=" * 62)
    print("【监督学习演示】")

    # ---- 回归部分：造 300 样本、8 特征（6 个有用）的回归数据 ----
    Xr, yr = make_regression(n_samples=300, n_features=8, n_informative=6,
                             noise=30, random_state=42)
    res_r = evaluate_regression(Xr, yr)
    names, imp = top_features(res_r["importance"], k=5)
    print("\n[回归] RandomForestRegressor  (300 样本, 8 特征)")
    print(f"    测试集 R²  = {res_r['r2']:.4f}  (越接近 1 越好)")
    print(f"    测试集 MAE = {res_r['mae']:.2f}")
    print(f"    测试集 RMSE = {res_r['rmse']:.2f}")
    print("    Top-5 特征重要性:")
    for n_, v_ in zip(names, imp):
        print(f"      {n_}: {v_:.4f}")

    # ---- 分类部分：造 500 样本、8 特征、2 类的分类数据（约 85% 可分）----
    Xc, yc = make_classification(n_samples=500, n_features=8, n_informative=6,
                                 n_redundant=2, n_classes=2, flip_y=0.05,
                                 random_state=42)
    cls = evaluate_classifiers(Xc, yc)
    print("\n[分类] LogisticRegression vs RandomForestClassifier  (500 样本, 2 类)")
    for name, r in cls.items():
        print(f"    {name}:")
        print(f"      accuracy = {r['accuracy']:.4f}, F1(macro) = {r['f1_macro']:.4f}")
        print(f"      混淆矩阵 (行=真实, 列=预测):\n{r['confusion']}")
        if r["importance"].any():
            names_c, imp_c = top_features(r["importance"], k=3)
            print("      Top-3 特征重要性:",
                  ", ".join(f"{n_}={v_:.3f}" for n_, v_ in zip(names_c, imp_c)))

    # 结论判读：RF 是否优于线性基线？(非线性数据一般 RF 更高)
    best = max(cls, key=lambda k: cls[k]["f1_macro"])
    print(f"\n[结论] F1 更高的分类器: {best}")
    print(f"    回归 R² = {res_r['r2']:.3f} 说明模型解释了 "
          f"{res_r['r2'] * 100:.1f}% 的方差（写论文直接引用）")
    print("\n[监督] PASS: 回归 R²/MAE + 分类 accuracy/F1/混淆矩阵 + 特征重要性排序")
