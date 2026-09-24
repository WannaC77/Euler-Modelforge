"""LaTeX 表格输出（论文直接可用）。

用法：
    from utils.latex_table import to_latex
    latex = to_latex(data, headers=["Item", "Value"], caption="...")
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("numpy",):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import numpy as np


def to_latex(data, headers=None, caption=None, label=None, fmt="%.4f",
             align=None, booktabs=True):
    """把 2D 数据转成 LaTeX tabular 字符串。

    data: 二维 list/ndarray；headers: 表头 list；fmt: 数值格式。
    返回可直接粘贴进 LaTeX 论文的表格代码。
    """
    arr = np.asarray(data, dtype=object)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    nrow, ncol = arr.shape
    if headers is not None:
        assert len(headers) == ncol, "headers 长度须等于列数"

    col_type = "c" if align is None else align
    rule = "\\toprule" if booktabs else "\\hline"
    midrule = "\\midrule" if booktabs else "\\hline"
    botrule = "\\bottomrule" if booktabs else "\\hline"

    lines = []
    if caption:
        lines.append(f"\\begin{{table}}[htbp]\n\\centering")
    lines.append(f"\\caption{{{caption}}}\n\\label{{{label}}}\n" if caption and label else "")
    lines.append(f"\\begin{{tabular}}{{{col_type * ncol}}}")
    lines.append(rule)
    if headers:
        lines.append(" & ".join(headers) + " \\\\")
        lines.append(midrule)
    for row in arr:
        cells = []
        for v in row:
            if isinstance(v, (int, np.integer)):
                cells.append(str(v))
            elif isinstance(v, (float, np.floating)):
                cells.append(fmt % v)
            else:
                cells.append(str(v))
        lines.append(" & ".join(cells) + " \\\\")
    lines.append(botrule)
    lines.append("\\end{tabular}")
    if caption:
        lines.append("\n\\end{table}")
    return "\n".join(lines)
