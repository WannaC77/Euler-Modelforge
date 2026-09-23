"""数据预处理工具模板（读取 → 缺失值 → 异常值 → 标准化/归一化 → 独热编码）。

适用场景：拿到原始表格数据后、进入统计/建模前的标准清洗流水线
        （美赛 C/E 数据题、国赛 C 大数据题必备；比赛 72h 内直接改常量区调用）。

输入格式：CSV/Excel 表格（或内存中的 pandas DataFrame），含数值列与分类列。
输出格式：清洗 + 变换后的 DataFrame；控制台分步骤输出统计量（可写进论文预处理章节）。
依赖：pandas、numpy。
"""
import importlib.util
import os
import tempfile

# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy", "pandas"):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np
import pandas as pd


def load_csv(path, **kw):
    """读取 CSV 文件为 DataFrame（path: 文件路径）。"""
    return pd.read_csv(path, **kw)


def load_excel(path, sheet_name=0, **kw):
    """读取 Excel 文件为 DataFrame（sheet_name 指定工作表，需环境装有 openpyxl/xlrd）。"""
    return pd.read_excel(path, sheet_name=sheet_name, **kw)


def missing_summary(df):
    """统计各列缺失数量与缺失率，返回汇总 DataFrame（无缺失则返回空表）。"""
    miss = df.isna().sum()
    miss = miss[miss > 0]
    if miss.empty:
        return pd.DataFrame({"缺失数": [], "缺失率%": []})
    return pd.DataFrame({"缺失数": miss, "缺失率%": (miss / len(df) * 100).round(2)})


def fill_missing(df, cols=None, method="median"):
    """填充缺失值：method ∈ {median, mean, mode}。
    数值列建议 median（抗异常值）；mode 用于分类列（众数填充）。"""
    out = df.copy()
    if cols is None:
        cols = list(out.columns)
    for c in cols:
        if method == "median":
            out[c] = out[c].fillna(out[c].median())
        elif method == "mean":
            out[c] = out[c].fillna(out[c].mean())
        elif method == "mode":
            out[c] = out[c].fillna(out[c].mode().iloc[0])
        else:
            raise ValueError("method 须为 median/mean/mode")
    return out


def drop_missing_rows(df, cols=None):
    """删除指定列含缺失的行（cols=None 表示删掉任何列有缺失的行），行号重置。"""
    return df.dropna(subset=cols).reset_index(drop=True)


def detect_outliers_iqr(s):
    """IQR 法检测异常值：超出 [Q1−1.5·IQR, Q3+1.5·IQR] 判为异常。
    返回 (布尔掩码, 下界, 上界)。"""
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return (s < lo) | (s > hi), lo, hi


def clip_outliers(df, cols):
    """异常值处理（缩尾法）：把越界值截断到 IQR 上下界，保留样本不删行。"""
    out = df.copy()
    for c in cols:
        mask, lo, hi = detect_outliers_iqr(out[c])
        out.loc[mask, c] = np.clip(out.loc[mask, c], lo, hi)
    return out


def zscore_standardize(df, cols):
    """Z-score 标准化：(x−μ)/σ。处理后均值≈0、标准差≈1，适合回归/聚类/距离类算法。"""
    out = df.copy()
    for c in cols:
        out[c] = (out[c] - out[c].mean()) / out[c].std(ddof=0)
    return out


def minmax_normalize(df, cols):
    """Min-Max 归一化：(x−min)/(max−min)。处理后落在 [0,1]，适合神经网络/梯度类算法。"""
    out = df.copy()
    for c in cols:
        out[c] = (out[c] - out[c].min()) / (out[c].max() - out[c].min())
    return out


def one_hot_encode(df, cols, drop_first=False):
    """分类变量独热编码：把分类列展开为 0/1 哑变量列并拼回原表。
    drop_first=True 可去掉首列防共线性（回归用）。"""
    out = df.copy()
    dummies = pd.get_dummies(out[cols], drop_first=drop_first, dtype=int)
    return pd.concat([out.drop(columns=cols), dummies], axis=1)


if __name__ == "__main__":
    # ===== 示例参数（改这里换数据：正式比赛把 df_raw 换成 load_csv("数据.csv")）=====
    rng = np.random.default_rng(42)   # 固定随机种子，保证可复现
    n = 200

    # 生成演示用"脏数据"：数值列 age/income + 分类列 city，人为注入缺失与异常值
    df_raw = pd.DataFrame({
        "age":    rng.normal(35, 8, n).round(),
        "income": rng.normal(9000, 2500, n).round(0),
        "city":   rng.choice(["北京", "上海", "广州", "杭州"], n, p=[0.3, 0.3, 0.2, 0.2]),
    })
    df_raw.loc[rng.choice(n, 15, replace=False), "age"] = np.nan      # 人为造 15 个缺失
    df_raw.loc[rng.choice(n, 12, replace=False), "income"] = np.nan   # 人为造 12 个缺失
    df_raw.loc[rng.choice(n, 10, replace=False), "city"] = np.nan     # 人为造 10 个缺失
    df_raw.loc[rng.choice(n, 4, replace=False), "income"] = 10 ** 5   # 人为造 4 个异常值(10万)

    print("=" * 62)
    print(f"【数据预处理全流程演示】原始数据: {df_raw.shape[0]} 行 x {df_raw.shape[1]} 列")

    # [1] 文件读取：演示 CSV 读写往返；Excel 读取函数已备好（环境缺 openpyxl 时跳过）
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = os.path.join(tmp, "demo.csv")
        df_raw.to_csv(csv_path, index=False, encoding="utf-8-sig")
        df_loaded = load_csv(csv_path)
        print(f"\n[1] CSV 读取演示: 写临时文件后读回成功, 形状 {df_loaded.shape}, "
              f"与原始数据一致 = {df_loaded.equals(df_raw)}")
    if importlib.util.find_spec("openpyxl") is not None:
        print("    Excel 读取可用: load_excel('数据.xlsx', sheet_name=0)")
    else:
        print("    Excel 读取函数 load_excel() 已就绪; 当前环境缺 openpyxl,")
        print("    需要读 .xlsx 时在 requirements.txt 加 openpyxl 即可 (CSV 读取不受影响)")

    # [2] 缺失值：先看分布 → 数值列中位数填充 + 分类列众数填充
    print("\n[2] 缺失值处理:")
    print("    处理前缺失统计:")
    print(missing_summary(df_raw))
    df = fill_missing(df_raw, cols=["age", "income"], method="median")
    df = fill_missing(df, cols=["city"], method="mode")
    print("    处理后剩余缺失数:", int(df.isna().sum().sum()), "(应=0)")

    # [3] 异常值：IQR 检测 → 缩尾处理
    mask, lo, hi = detect_outliers_iqr(df["income"])
    print(f"\n[3] 异常值 IQR 检测 (income): 检出 {int(mask.sum())} 个, "
          f"正常区间 [{lo:.0f}, {hi:.0f}]")
    df = clip_outliers(df, ["income"])
    print(f"    缩尾处理后 income: 最大值 {df['income'].max():.0f} "
          f"(不再出现 100000 量级), 最小值 {df['income'].min():.0f}")

    # [4] 标准化 / 归一化（同一份干净数据出两份变换，按模型选一份）
    df_z = zscore_standardize(df.copy(), ["age", "income"])
    print("\n[4] Z-score 标准化后统计 (期望 mean≈0, std≈1):")
    print("    age:    mean = %.4f, std = %.4f" % (df_z["age"].mean(), df_z["age"].std()))
    print("    income: mean = %.4f, std = %.4f" % (df_z["income"].mean(), df_z["income"].std()))
    df_mm = minmax_normalize(df.copy(), ["age", "income"])
    print("    Min-Max 归一化后范围 (期望 [0,1]): age [%.3f, %.3f], income [%.3f, %.3f]"
          % (df_mm["age"].min(), df_mm["age"].max(), df_mm["income"].min(), df_mm["income"].max()))

    # [5] 分类变量独热编码
    df_final = one_hot_encode(df_z, ["city"])
    print(f"\n[5] 独热编码后: {df_final.shape[0]} 行 x {df_final.shape[1]} 列 "
          f"(city 展开为 4 个哑变量列)")

    # [6] 输出处理后统计（论文"数据预处理"小节可直接引用）
    print("\n[6] 处理后数据统计:")
    print("    年龄 income 均值 = %.1f, 标准差 = %.1f" % (df["income"].mean(), df["income"].std()))
    print("    city 分布(填充后):", dict(df["city"].value_counts()))
    print("    最终数值列描述统计:")
    print(df_final[["age", "income"]].describe().round(3).to_string())
    print("\n[预处理] 全流程 PASS: 读取 → 缺失填充 → 异常缩尾 → 标准化/归一化 → 独热编码")
