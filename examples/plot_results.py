# -*- coding: utf-8 -*-
"""示例 2 —— 调 figkit 样张 1（两组对比柱状图 + 误差棒 + 显著性）出图。

运行：python examples/plot_results.py
判据：样张 rc=0 且 _out 下 png/svg/pdf 三件齐 → rc=0；缺依赖按约 rc=3。
"""
import os
import subprocess
import sys
from pathlib import Path


def tree() -> Path:
    cands = []
    env = os.environ.get("MODELFORGE_ROOT")
    if env:
        cands.append(Path(env))
    cands += list(Path(__file__).resolve().parents)
    for c in cands:
        if (c / "templates-library").is_dir() and (c / "tools").is_dir():
            return c
    raise SystemExit("[错误] 未找到工具树：请在仓库根运行，或设置 MODELFORGE_ROOT。")


def main() -> int:
    t = tree()
    demo = t / "templates-library" / "utils" / "figkit" / "figkit_demo1_grouped_bar.py"
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    p = subprocess.run([sys.executable, str(demo)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    print(p.stdout, end="")
    if p.returncode == 3:
        print("[提示] 依赖缺失未执行：pip install euler-modelforge[all]")
        return 3
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr, end="")
        return p.returncode
    outdir = demo.parent / "_out"
    made = sorted(outdir.glob("figkit_demo1_grouped_bar.*"))
    if len(made) < 3:
        print("[示例] FAIL：_out 下应有三件（png/svg/pdf），实得 %d" % len(made), file=sys.stderr)
        return 1
    for f in made:
        print("[产物] %s" % f)
    print("[示例] plot_results 完成 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
