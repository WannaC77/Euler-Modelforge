# -*- coding: utf-8 -*-
"""figcheck —— 图纸文件级体检（命令行）
用法：
    python utils/figcheck.py <图.png> [--min-width 800] [--min-dpi 150] [--min-content 0.005]
    python utils/figcheck.py --help

检查（对应「图交付前必过」门禁的文件层）：
  1) 能真实打开且为 PNG/JPEG（防 404 页面/半损坏文件冒充）
  2) 宽或 DPI 达门槛（论文插图清晰度下限）
  3) 白底可见内容占比（防「纯白空图」「误存全透明」）
exit code: 0=全过 / 1=有 FAIL / 2=文件或参数错误。
说明：本工具做**文件层**检查；内容/越界/字号请配合 plot_style.audit_fig 与主模型 vision 复核。
"""
import sys
import os


def main(argv):
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = argv[1]
    opts = {"min_width": 800, "min_dpi": 150, "min_content": 0.005}
    i = 2
    while i < len(argv) - 1:
        k = argv[i].lstrip("-").replace("-", "_")
        if k in opts:
            opts[k] = float(argv[i + 1])
        i += 2

    if not os.path.exists(path):
        print(f"FAIL | 文件不存在: {path}")
        return 2

    fails, warns = [], []
    try:
        from PIL import Image
        im = Image.open(path)
        fmt, size = im.format, im.size
        dpi = im.info.get("dpi", (None, None))
    except Exception as e:
        print(f"FAIL | 无法以图片打开（可能不是图片或已损坏）: {e}")
        return 1

    print(f"[figcheck] {os.path.basename(path)}  fmt={fmt} size={size[0]}x{size[1]} dpi={dpi}")

    # 1) 格式
    if fmt not in ("PNG", "JPEG", "TIFF"):
        fails.append(f"格式 {fmt} 非 PNG/JPEG/TIFF")
    if fmt == "JPEG":
        warns.append("JPEG 有损压缩，正式图建议 PNG/PDF")

    # 2) 尺寸/DPI
    w, h = size
    dpi_x = dpi[0] if dpi and dpi[0] else None
    if w < opts["min_width"] and (dpi_x is None or dpi_x < opts["min_dpi"]):
        fails.append(f"宽 {w}px 且 DPI {dpi_x} 均低于门槛（{opts['min_width']}px / {opts['min_dpi']}dpi）")

    # 3) 白底内容占比（用 numpy 直读，避免 matplotlib 依赖链）
    try:
        import numpy as np
        arr = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
        gray = arr.mean(axis=2)
        content = float((gray < 0.95).mean())
        if content < opts["min_content"]:
            fails.append(f"可见内容占比 {content*100:.3f}% < {opts['min_content']*100:.2f}%（疑似空图/纯色图）")
        else:
            print(f"  ✓ 内容占比 {content*100:.2f}%")
    except Exception as e:
        warns.append(f"内容占比检查跳过（{e}）")

    for m in fails:
        print(f"  ✗ FAIL: {m}")
    for m in warns:
        print(f"  ⚠ {m}")
    if not fails:
        print("  ✓ PASS（文件层）")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
