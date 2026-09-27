# -*- coding: utf-8 -*-
"""示例 3 —— 全链 mini：合成题卡 → 模板求解 → figkit 出图 → 薄报告。

运行：python examples/mini_chain.py
产出：examples/_out/mini_report.md（安装态同目录）。
判据：全链各步 rc=0 且报告落盘 → rc=0；缺依赖按约 rc=3。
"""
import json
import os
import subprocess
import sys
from pathlib import Path

CARD = {  # 合成演示题卡（读题定位器口径的最小集）
    "id": "demo-lp-01",
    "type": "线性规划 · 产量排产",
    "goal": "最大化总利润",
    "vars": ["产品A", "产品B"],
    "note": "合成演示；求解调用模板库 01-优化/lp.py 的内置合成数据",
}


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


def run(script: Path, env) -> "subprocess.CompletedProcess":
    return subprocess.run([sys.executable, str(script)], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=env)


def main() -> int:
    t = tree()
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    print("== 题卡 ==")
    print(json.dumps(CARD, ensure_ascii=False, indent=2))

    print("== 求解（模板 01-优化/lp.py）==")
    r1 = run(t / "templates-library" / "01-优化" / "lp.py", env)
    print(r1.stdout, end="")
    if r1.returncode == 3:
        print("[提示] 依赖缺失未执行：pip install euler-modelforge[all]")
        return 3
    if r1.returncode != 0:
        print(r1.stderr, file=sys.stderr, end="")
        return r1.returncode
    best = next((ln.strip() for ln in r1.stdout.splitlines() if "[最优值]" in ln), "")
    if not best:
        print("[示例] FAIL：求解输出缺 [最优值]", file=sys.stderr)
        return 1

    print("== 出图（figkit 样张 2：热力图）==")
    demo2 = t / "templates-library" / "utils" / "figkit" / "figkit_demo2_heatmap.py"
    r2 = run(demo2, env)
    fig_note = "（未出图）"
    if r2.returncode == 0:
        figs = sorted((demo2.parent / "_out").glob("figkit_demo2_heatmap.*"))
        if figs:
            fig_note = str(figs[0])
        print("[产物] %s" % fig_note)
    elif r2.returncode == 3:
        fig_note = "（缺依赖，跳过出图）"
        print("[提示] 出图跳过：依赖缺失（rc=3）")
    else:
        print(r2.stderr, file=sys.stderr, end="")
        return r2.returncode

    outdir = Path(__file__).resolve().parent / "_out"
    outdir.mkdir(exist_ok=True)
    rep = outdir / "mini_report.md"
    rep.write_text(
        "# mini 全链报告（示例）" + chr(10) + chr(10)
        + "- 题卡：" + CARD["type"] + "（" + CARD["id"] + "）" + chr(10)
        + "- " + best + chr(10)
        + "- 图件：" + fig_note + chr(10)
        + "- 说明：本报告由 examples/mini_chain.py 生成（合成数据）。" + chr(10),
        encoding="utf-8")
    print("== 薄报告 ==")
    print("[产物] %s" % rep)
    print("[示例] mini_chain 完成 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
