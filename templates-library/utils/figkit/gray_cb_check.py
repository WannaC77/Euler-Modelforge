# -*- coding: utf-8 -*-
"""gray_cb_check —— 黑白/色盲机检辅助（灰度预览 + 红绿色盲模拟 + 亮度差告警）。

为什么需要它
------------
论文/竞赛材料大量以黑白缩印或灰度 PDF 形式送到评委手里。一张在屏幕上「颜色分明」
的图，去色后可能只剩一片相近的灰——**图和图之间靠颜色区分的信息全部丢失**。
本工具把这件事做成可机检的三件套，图的作者不用自己想象灰度效果。

用法
----
    python utils/figkit/gray_cb_check.py [图片路径] [选项]

    图片路径缺省 = ``utils/figkit/_out/figkit_demo1_grouped_bar.png``
    选项：
      --min-dl  0.10   灰度亮度差告警阈值（见下「判定阈值」）
      --top     6      最多认定几个「主要序列色」
      --strict         出现告警时退出码 1（默认只提示、退出码 0）
      --outdir  <dir>  预览图输出目录（缺省 figkit/_out/）

    产出：
      <outdir>/<图名>_gray.png   ① 灰度化预览（判据同源，见下）
      <outdir>/<图名>_cb.png     ② 红绿色盲（deuteranopia）模拟预览
      控制台：主要序列色表 + 两两亮度差表 + 判定

机检做法（三段，全部只用 matplotlib + numpy）
--------------------------------------------
① **灰度化预览**：按 WCAG 2.x 相对亮度 ``L = 0.2126R' + 0.7152G' + 0.0722B'``
   （R'G'B' 为 sRGB→线性光后的分量）求 L，再把 L 编回 sRGB 存成灰度 PNG。
   注意：**不用**常见的伽马空间加权 ``0.299R+0.587G+0.114B``（那是电视亮度口径，
   比真实感知偏亮）；预览与下面 ③ 的判据取自同一套 L，避免「预览和结论各用一套
   灰度口径」这种自欺。
② **红绿色盲模拟**：Machado et al. (2009) 严重度 1.0 的 deuteranopia 线性矩阵
       [[ 0.367322,  0.860646, -0.227968],
        [ 0.280085,  0.672501,  0.047413],
        [-0.011820,  0.042940,  0.968881]]
   在**线性光**空间做矩阵乘（该矩阵的定义域就是线性 RGB，直接在伽马空间乘是错的），
   再编回 sRGB。红绿色盲约占男性 6%——评委里碰上的概率不低。
③ **主要序列色亮度差自动检查**：
   a. 取「有彩色」像素：HSV 下 ``S >= 0.20`` 且 ``0.15 <= V <= 0.98``
      （滤掉白底、黑字、纯灰网格线——它们去色后本来就还在）。
   b. 按色相做 10° 桶直方图，贪心取峰：按像素占比降序，且与已选色相的**最小环距**
      ``>= 20°``（避免同一系列被抗锯齿过渡色拆成两个「主色」）；占比 < 0.5% 的桶丢弃。
   c. 每个色相桶取桶内像素的**中位 RGB** 作代表色（中位数抗抗锯齿过渡色，比均值稳）。
   d. 两两算 ``ΔL = |L1 - L2|``（WCAG 相对亮度差，0-1）；取最小者与阈值比。
      同时给出 8-bit 灰阶值（``round(L*255)``）便于直观对照，以及 WCAG 对比度比
      ``(L1+0.05)/(L2+0.05)``。

判定阈值（默认 --min-dl 0.10）
------------------------------
``ΔL < 0.10`` → **告警**。理由：ΔL=0.10 时 8-bit 灰阶差约 25 级、WCAG 对比度比
约 1.8:1；缩印后相邻序列的灰度块开始糊在一起，读者需凑近才能分辨——低于此值即
判定「灰度下不可靠」。该阈值下再设一条 **1.25 倍预警带**：``min ΔL < 0.125`` 时
提示「勉强可辨」，建议叠加线型/标记/斜纹等冗余编码（颜色之外的第二条通道）。
阈值可用 ``--min-dl`` 调；口径写死在 docstring 里，避免不同人算出不同结论。

退出码
------
    0 = 检查完成（无告警，或告警但未加 --strict）
    1 = --strict 且出现告警
    2 = 参数/文件错误（路径不存在、读不出图）
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("matplotlib", "numpy"):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                     # 纯文件读写，用无界面后端（无显示环境也能跑）
import matplotlib.pyplot as plt           # noqa: E402
import numpy as np                        # noqa: E402
from matplotlib import colors as mcolors  # noqa: E402

HERE = Path(__file__).resolve().parent
DEFAULT_IMG = HERE / "_out" / "figkit_demo1_grouped_bar.png"
DEFAULT_OUTDIR = HERE / "_out"

# WCAG 2.x 相对亮度权重（线性光空间）
_LUMA_W = np.array([0.2126, 0.7152, 0.0722])
# Machado et al. (2009) deuteranopia（严重度 1.0）线性 RGB 变换矩阵
M_DEUTERANOPIA = np.array([
    [0.367322, 0.860646, -0.227968],
    [0.280085, 0.672501, 0.047413],
    [-0.011820, 0.042940, 0.968881],
])
# 有彩色像素筛选门（HSV）
SAT_MIN, VAL_MIN, VAL_MAX = 0.20, 0.15, 0.98
# 色相聚类参数
HUE_BIN_DEG, HUE_GAP_DEG, MIN_SHARE = 10.0, 20.0, 0.005


# ---------------------------------------------------------------- 色彩空间 ----
def srgb_to_linear(c):
    """sRGB(0-1) → 线性光(0-1)。"""
    c = np.clip(np.asarray(c, dtype=float), 0.0, 1.0)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c):
    """线性光(0-1) → sRGB(0-1)。"""
    c = np.clip(np.asarray(c, dtype=float), 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1.0 / 2.4) - 0.055)


def relative_luminance(rgb):
    """WCAG 相对亮度 L（0=黑, 1=白）。输入 sRGB(0-1)，形状 (...,3)。"""
    return srgb_to_linear(rgb) @ _LUMA_W


def simulate_deuteranopia(rgb):
    """红绿色盲模拟（线性光矩阵变换后编回 sRGB）。"""
    lin = srgb_to_linear(rgb)
    return np.clip(linear_to_srgb(lin @ M_DEUTERANOPIA.T), 0.0, 1.0)


# ---------------------------------------------------------------- 读图 ----
def load_rgb(path):
    """读图为白底 sRGB 浮点数组 (H,W,3)，值域 0-1。"""
    arr = np.asarray(plt.imread(str(path)), dtype=float)
    if arr.ndim == 2:                       # 灰度图 → 复制成三通道
        arr = np.dstack([arr] * 3)
    if arr.size and arr.max() > 1.0:        # 个别格式给 0-255
        arr = arr / 255.0
    if arr.shape[2] == 4:                   # RGBA：透明底合成到白底再判色
        a = arr[..., 3:4]
        arr = arr[..., :3] * a + (1.0 - a)
    return np.clip(arr[..., :3], 0.0, 1.0)


# ---------------------------------------------------------------- 主色提取 ----
def dominant_colors(rgb, top=6):
    """返回 [(代表色 RGB, 像素占比), ...]，按占比降序。做法见模块 docstring ③。"""
    hsv = mcolors.rgb_to_hsv(rgb)
    H, S, V = hsv[..., 0] * 360.0, hsv[..., 1], hsv[..., 2]
    mask = (S >= SAT_MIN) & (V >= VAL_MIN) & (V <= VAL_MAX)
    n_color = int(mask.sum())
    if n_color == 0 or top < 2:
        return [], n_color

    hues = H[mask]
    px = rgb[mask]
    edges = np.arange(0.0, 360.0 + HUE_BIN_DEG, HUE_BIN_DEG)
    cnt, _ = np.histogram(hues, bins=edges)

    picked = []                              # [(色相中心, 桶内像素数)]
    for bi in np.argsort(-cnt):
        if cnt[bi] < MIN_SHARE * n_color:
            break
        center = edges[bi] + HUE_BIN_DEG / 2.0
        if any(min(abs(center - c), 360.0 - abs(center - c)) < HUE_GAP_DEG
               for c, _ in picked):
            continue
        picked.append((center, int(cnt[bi])))
        if len(picked) >= top:
            break

    out = []
    for center, c in picked:
        d = np.abs(hues - center)
        d = np.minimum(d, 360.0 - d)         # 色相环距离
        sel = d <= HUE_BIN_DEG / 2.0
        if not sel.any():
            continue
        rep = np.median(px[sel], axis=0)     # 中位数：抗抗锯齿过渡色
        out.append((rep, c / n_color))
    return out, n_color


# ---------------------------------------------------------------- 报告 ----
def hex_of(c):
    return "#" + "".join(f"{int(round(v * 255)):02x}" for v in np.clip(c, 0, 1))


def main(argv=None):
    ap = argparse.ArgumentParser(description="灰度/色盲可辨性机检（黑白打印与红绿色盲）")
    ap.add_argument("image", nargs="?", default=None, help="待检 PNG（缺省 demo1 产物）")
    ap.add_argument("--min-dl", type=float, default=0.10,
                    help="灰度亮度差告警阈值（WCAG 相对亮度差，默认 0.10）")
    ap.add_argument("--top", type=int, default=6, help="最多认定几个主要序列色（默认 6）")
    ap.add_argument("--strict", action="store_true", help="出现告警时退出码 1")
    ap.add_argument("--outdir", default=None, help="预览图输出目录（缺省 figkit/_out/）")
    args = ap.parse_args(argv)

    img = Path(args.image).resolve() if args.image else DEFAULT_IMG
    outdir = Path(args.outdir).resolve() if args.outdir else DEFAULT_OUTDIR
    if not img.exists():
        print(f"[×] 找不到图片：{img}")
        print(f"    先跑一次 demo 生成，例如：python utils/figkit/figkit_demo1_grouped_bar.py")
        return 2
    try:
        rgb = load_rgb(img)
    except Exception as e:
        print(f"[×] 读图失败（{type(e).__name__}: {e}）")
        return 2

    h, w = rgb.shape[:2]
    print(f"[输入] {img.name}  {w}x{h} px")
    print(f"[口径] 灰度与亮度差均取 WCAG 相对亮度（线性光加权）；"
          f"告警阈值 ΔL < {args.min_dl:g}")

    # ---- ① 灰度预览 / ② 色盲模拟预览 ----
    lum = relative_luminance(rgb)                                    # (H,W)
    gray_srgb = linear_to_srgb(np.dstack([lum] * 3))                 # 编回 sRGB，与判据同源
    cb_srgb = simulate_deuteranopia(rgb)
    outdir.mkdir(parents=True, exist_ok=True)
    gray_path = outdir / f"{img.stem}_gray.png"
    cb_path = outdir / f"{img.stem}_cb.png"
    plt.imsave(str(gray_path), gray_srgb, vmin=0.0, vmax=1.0)
    plt.imsave(str(cb_path), cb_srgb, vmin=0.0, vmax=1.0)

    # ---- ③ 主要序列色 + 亮度差检查 ----
    colors, n_color = dominant_colors(rgb, top=args.top)
    print(f"[主色] 有彩色像素 {n_color}/{rgb.shape[0] * rgb.shape[1]}"
          f"（{n_color / rgb.shape[0] / rgb.shape[1] * 100:.2f}%），"
          f"色相聚类得主要序列色 {len(colors)} 个"
          f"（S>={SAT_MIN}, {VAL_MIN}<=V<={VAL_MAX}, 占比>={MIN_SHARE*100:g}%）")

    if len(colors) < 2:
        print("[判定] 不足 2 个主要序列色，无法做两两亮度差检查——"
              "本图可能是灰度/单色图，或序列色饱和度太低（灰系配色）。")
        print(f"[落盘] {gray_path.name} | {cb_path.name}")
        return 0

    L = np.array([float(relative_luminance(c)) for c, _ in colors])   # colors 项为 (RGB, 占比)
    print(f"  {'序号':<5}{'代表色':<10}{'占比':>8}{'相对亮度 L':>12}{'8bit 灰阶':>10}")
    for k, (c, share) in enumerate(colors, 1):
        print(f"  #{k:<4}{hex_of(c):<10}{share*100:>7.1f}%{L[k-1]:>12.4f}"
              f"{int(round(float(L[k-1]) * 255)):>10}")

    pairs = []
    for i in range(len(colors)):
        for j in range(i + 1, len(colors)):
            dl = abs(L[i] - L[j])
            cr = (max(L[i], L[j]) + 0.05) / (min(L[i], L[j]) + 0.05)
            pairs.append((dl, i, j, cr))
    pairs.sort()
    warn_th = args.min_dl
    near_th = warn_th * 1.25
    print(f"[亮度差] 两两共 {len(pairs)} 对，列出最接近的 {min(3, len(pairs))} 对"
          f"（ΔL 越大越安全；对比度比按 WCAG 公式 (L1+.05)/(L2+.05)）")
    for dl, i, j, cr in pairs[:3]:
        tag = ("⚠ 低于阈值" if dl < warn_th
               else ("· 勉强可辨" if dl < near_th else "✓ 安全"))
        print(f"  {hex_of(colors[i][0])} vs {hex_of(colors[j][0])}: "
              f"ΔL={dl:.4f}（灰阶 {int(round(float(L[i])*255))} vs "
              f"{int(round(float(L[j])*255))}）"
              f" 对比度比 {cr:.2f}:1  {tag}")

    min_dl, mi, mj, mcr = pairs[0]
    warn = min_dl < warn_th
    if warn:
        verdict = (f"⚠ 告警：最小亮度差 ΔL={min_dl:.4f} < 阈值 {warn_th:g}"
                   f"（{hex_of(colors[mi][0])} vs {hex_of(colors[mj][0])}）"
                   f"——灰度/黑白缩印下这两条序列会糊在一起；"
                   f"请改用亮度拉开（同族深浅）或叠加线型/标记/斜纹做冗余编码。")
    elif min_dl < near_th:
        verdict = (f"⚠ 提示：最小亮度差 ΔL={min_dl:.4f} 仅略高于阈值 {warn_th:g}"
                   f"（灰阶 {int(round(float(L[mi])*255))} vs "
                   f"{int(round(float(L[mj])*255))}）"
                   f"——勉强可辨；建议再叠一种颜色之外的编码（线型/标记/斜纹）保险。")
    else:
        verdict = (f"✓ 灰度安全：最小亮度差 ΔL={min_dl:.4f} >= 阈值 {warn_th:g}"
                   f"（{hex_of(colors[mi][0])} vs {hex_of(colors[mj][0])}，"
                   f"对比度比 {mcr:.2f}:1）")
    print(f"[判定] {verdict}")
    print(f"[预览] 灰度 {gray_path.name}｜色盲 {cb_path.name}"
          f"（两图仅 ① 灰度化 ② deuteranopia 模拟，未做任何锐化/裁剪）")

    if warn and args.strict:
        print("[退出码] 1（--strict 且出现告警）")
        return 1
    print("[退出码] 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
