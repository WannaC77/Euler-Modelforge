# -*- coding: utf-8 -*-
"""示例 1 —— 调模板库求解一个线性规划合成题。

运行：python examples/solve_lp.py
判据：模板输出含「[最优值]」→ rc=0；缺依赖按仓库约定 rc=3。
"""
import os
import subprocess
import sys
from pathlib import Path


def tree() -> Path:
    """定位工具树：MODELFORGE_ROOT 优先；否则从本文件向上找（仓库 checkout 或安装包 _tree）。"""
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
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    p = subprocess.run(
        [sys.executable, str(t / "templates-library" / "01-优化" / "lp.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
    )
    print(p.stdout, end="")
    if p.returncode == 3:
        print("[提示] 依赖缺失未执行：pip install euler-modelforge[all]"
              "（仓库内可 pip install -r templates-library/requirements.txt）")
        return 3
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr, end="")
        return p.returncode
    if "[最优值]" not in p.stdout:
        print("[示例] FAIL：模板输出缺少 [最优值] 判据行", file=sys.stderr)
        return 1
    print("[示例] solve_lp 完成 ✓（树根：%s）" % t)
    return 0


if __name__ == "__main__":
    sys.exit(main())
