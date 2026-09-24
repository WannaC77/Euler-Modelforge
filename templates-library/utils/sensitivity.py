"""通用敏感性分析工具 — 论文"敏感性分析"章节一键产出。

适用场景：任何模型拿到关键参数后，扫描参数变化对结果的影响，输出表格+图。
（评委标配追问"换个参数结果还成立吗"——本工具直接回答。）

用法：
    from utils.sensitivity import scan_1d, scan_report
    结果 = scan_1d(func, param_name="beta", base=0.35, ranges=[0.25,0.30,...,0.45], other={"gamma":0.1})
    scan_report(结果, "beta")
其中 func 是"给定某参数值 + 其他参数 → 返回单一目标值(如峰值/成本/得分)"的函数。
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy", "SALib", "matplotlib"):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np


def scan_1d(func, param_name, base_value, values=None, pct=0.2, n=9, **fixed_kwargs):
    """单参数扫描：围绕 base_value 在 ±pct 范围内取 n 个点，逐个调 func(param=值, **fixed) 求目标。

    func(param_name=某值, **fixed_kwargs) → float 目标值。
    返回 dict: {"参数": [...], "结果": [...]}。
    """
    if values is None:
        lo, hi = base_value * (1 - pct), base_value * (1 + pct)
        values = np.linspace(lo, hi, n)
    results = []
    for v in values:
        kw = dict(fixed_kwargs)
        kw[param_name] = v
        results.append(float(func(**kw)))
    return {"参数名": param_name, "参数": np.asarray(values), "结果": np.asarray(results)}


def scan_2d(func, p1_name, p1_base, p2_name, p2_base, pct=0.2, n=7, **fixed_kwargs):
    """双参数网格扫描（敏感性热图用）。"""
    vals = [p1_base * (1 - pct) + (p1_base * 2 * pct) * i / (n - 1) for i in range(n)]
    rows = []
    for v1 in vals:
        row = []
        for v2 in [p2_base * (1 - pct) + (p2_base * 2 * pct) * i / (n - 1) for i in range(n)]:
            kw = dict(fixed_kwargs)
            kw[p1_name], kw[p2_name] = v1, v2
            row.append(float(func(**kw)))
        rows.append(row)
    return {"p1": p1_name, "p2": p2_name, "x": vals, "y": [p2_base * (1 - pct) + (p2_base * 2 * pct) * i / (n - 1) for i in range(n)], "Z": np.array(rows)}


def _relative_change(res):
    """结果相对基准的相对变化率（%）。"""
    base = res[len(res) // 2]
    return (res - base) / abs(base) * 100


def scan_report(s, target_name="目标值", decimals=4):
    """打印单参数扫描报告（数值表格风格，可直接抄进论文）。"""
    pname = s["参数名"]
    pars, res = s["参数"], s["结果"]
    base = res[len(res) // 2]
    print(f"[敏感性分析] 参数 {pname} 对 {target_name} 的影响")
    print(f"  {'参数值':>10} | {'结果':>12} | {'相对基准变化':>12}")
    for p, r in zip(pars, res):
        chg = (r - base) / abs(base) * 100 if base != 0 else float("nan")
        print(f"  {p:>10.4f} | {r:>12.{decimals}f} | {chg:>+11.2f}%")
    max_chg = np.max(np.abs(_relative_change(res))) if base != 0 else float("nan")
    print(f"\n[结论] 参数 ±变动范围内，{target_name} 最大相对变化 {max_chg:.2f}%")
    if max_chg < 5:
        print("  → 结果对参数不敏感（稳健）✓")
    elif max_chg < 30:
        print("  → 中等敏感，论文中如实讨论")
    else:
        print("  → 高度敏感！必须重点讨论，建议参数取值给依据/做更细扫描")
    return max_chg


# ---------------------------------------------------------------- 龙卷风图 ----

def tornado(func, params, pct=0.2, target_name="目标值", ax=None, save=None):
    """多参数 OAT 龙卷风图（论文敏感性分析标配图）。

    params: {"参数名": 基准值, ...}（2-4 个核心参数，见 Euler 06 入选标准）
    func(param_name=值, **其余基准值) → float 目标值（与 scan_1d 同约定）。
    逐参数 ±pct 扰动（其余参数固定在基准值），按影响幅度降序画水平条形图。

    返回 dict: {"排序": [(参数名, 低值结果, 高值结果, 相对基准变化幅度%), ...]}。
    """
    import matplotlib.pyplot as plt
    try:
        from utils.plot_style import style_plot
        style_plot()  # 全局论文级风格（plot_style 统一出口，见 Euler 07 图表规范）
    except Exception:
        pass  # plot_style 不可用时退回默认样式，不阻塞计算

    base_val = float(func(**{k: v for k, v in params.items()}))
    rows = []
    for name, base in params.items():
        lo = float(func(**{**params, name: base * (1 - pct)}))
        hi = float(func(**{**params, name: base * (1 + pct)}))
        amp = max(abs(lo - base_val), abs(hi - base_val)) / abs(base_val) * 100
        rows.append((name, lo, hi, amp))
    rows.sort(key=lambda r: r[3], reverse=True)

    if ax is None:
        _, ax = plt.subplots(figsize=(7, 0.9 * len(rows) + 1.8))
    y = np.arange(len(rows))[::-1]
    for yi, (name, lo, hi, amp) in zip(y, rows):
        ax.barh(yi, hi - base_val, left=base_val, height=0.55,
                color="#4878CF", edgecolor="black", linewidth=0.6)
        ax.barh(yi, lo - base_val, left=base_val, height=0.55,
                color="#EE854A", edgecolor="black", linewidth=0.6)
        ax.text(base_val, yi + 0.42, f"{name} (±{amp:.1f}%)",
                ha="center", va="bottom", fontsize=9)
    ax.axvline(base_val, color="black", lw=1)
    ax.set_yticks(y)
    ax.set_yticklabels([f"基准±{pct:.0%}" for _ in rows])
    ax.set_xlabel(f"{target_name}（基准 {base_val:.4g}）")
    ax.set_title(f"参数敏感性龙卷风图（蓝=+{pct:.0%}，橙=-{pct:.0%}）")
    if save:
        plt.tight_layout()
        plt.savefig(save, dpi=300)
    return {"排序": rows, "基准": base_val}


# ------------------------------------------------------------ Sobol 全局 ----

def sobol_indices(func, params, n=512, calc_second_order=False, target_name="目标值"):
    """Sobol 全局敏感性一阶/总阶指数（冲 O 奖/国一可选，见 Euler 06 第 3 步升级项）。

    params: {"参数名": (下界, 上界), ...}，均匀分布假设（其他分布自行改 Saltelli 问题定义）。
    func(参数名=值, ...) → float 目标值。
    n: 基准样本量（实际模型评估次数 = n*(k+2) 量级，k 为参数个数，别开太大）。

    需要 SALib（pip install SALib），缺失时抛出带安装提示的 ImportError。
    返回 dict: {"参数名": {"S1": 一阶指数, "ST": 总阶指数}, ...}
    解读：ST 越大该参数总影响越大；S1<<ST 说明存在参数交互。
    """
    try:
        from SALib.sample import saltelli
        from SALib.analyze import sobol as _sobol
    except ImportError as e:
        raise ImportError("需要 SALib：pip install SALib（已写入 05-编程求解 技术栈）") from e

    names = list(params)
    problem = {
        "num_vars": len(names),
        "names": names,
        "bounds": [list(params[k]) for k in names],
    }
    X = saltelli.sample(problem, n, calc_second_order=calc_second_order)
    Y = np.array([float(func(**dict(zip(names, row)))) for row in X])
    Si = _sobol.analyze(problem, Y, calc_second_order=calc_second_order)
    out = {nm: {"S1": float(s1), "ST": float(st)}
           for nm, s1, st in zip(names, Si["S1"], Si["ST"])}
    print(f"[Sobol 全局敏感性] {target_name}（n={n}，共评估 {len(Y)} 次）")
    for nm, d in out.items():
        tag = "主导参数" if d["ST"] >= 0.3 else ("有影响" if d["ST"] >= 0.1 else "次要")
        inter = "（存在交互）" if d["ST"] - d["S1"] > 0.1 else ""
        print(f"  {nm:>10}: S1={d['S1']:.3f}  ST={d['ST']:.3f}  {tag}{inter}")
    return out
