# -*- coding: utf-8 -*-
"""35 个模板一键冒烟 runner（数模代码仓 / templates-library）。

用途
----
一条命令验证 ``0*/`` 下 8 类共 35 个模板「能不能跑通、有没有报错」，产出可归档的
Markdown 报告。比赛前、改模板后各跑一次，避免「模板在盘但一跑就炸」的暗雷。

用法
----
    python smoke_all.py                # 全量跑（35 件，超时 120s/件）
    python smoke_all.py --quick        # 每类只跑首件（8 件，最快冒烟）
    python smoke_all.py --json         # 额外产出 JSON 报告
    python smoke_all.py --selftest     # 自证：跑 3 件代表 + 校验发现机制本身
    python smoke_all.py --timeout 60   # 改单件超时上限

产出
----
    ① 控制台表格：件名 | 类别 | rc | 判定 | 耗时 | 输出摘要
    ② ``_smoke_out/smoke_all_report.md``：件名|类别|rc|判定|输出摘要 + 汇总
    ③ ``_smoke_out/smoke_all_report.json``（仅 ``--json``）
       ``--selftest`` 模式写 ``_smoke_out/smoke_all_selftest.{md,json}``，不覆盖正式报告。

退出码
------
    0 = 全部 PASS
    1 = 存在 FAIL / TIMEOUT / ERROR（任一非 0 即失败，便于串进 CI 或上游命令）
    2 = 参数或环境错误（如一件模板都没发现）

解释器解析
----------
    优先「本脚本所在目录/<venv>/Scripts/python.exe」（Windows venv 布局），
    其次「bin/python」（POSIX venv 布局），两者都不在则退回 ``sys.executable``。
    全部按脚本位置相对解析——本文件不含任何绝对路径，可整仓搬移。

判定口径
--------
    只看子进程 returncode：rc==0 → PASS，否则 FAIL。**不做数值断言**——模板打印的
    内容是给人判读的，数值正确性由模板自身验收用例保证（见 README 验收状态）。
    超时（默认 120s）单独记 TIMEOUT，不误判成 FAIL。

输出摘要取法
------------
    取子进程输出最后 1 行非空文本（PASS 取 stdout，FAIL 优先取 stderr），
    截断到 120 字符并转义 Markdown 表格竖线；JSON 里另存 3 行尾部便于排查。
"""
import argparse
import json
import os
import subprocess
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

# ============ 常量（改这里即可）============
HERE = Path(__file__).resolve().parent          # templates-library/
OUT_DIR = HERE / "_smoke_out"                   # 报告落盘目录
REPORT_MD = "smoke_all_report.md"
REPORT_JSON = "smoke_all_report.json"
TIMEOUT_S = 120                                 # 单件超时（秒）
TAIL_LINES = 3                                  # JSON 里保留的尾部行数
SUMMARY_LIMIT = 120                             # 摘要字符上限
CATEGORY_GLOB = "0*"                            # 8 类子目录（01-优化 ... 08-智能算法）
# --selftest 的三件代表：优化 / 评价 / 智能算法各一（跨依赖栈，最能暴露环境问题）
SELFTEST_TARGETS = ("01-优化/lp.py", "03-评价/grey_relation.py", "08-智能算法/ga.py")
EXPECTED_TEMPLATES = 35                         # 期望模板总数（少于此数即环境异常）


# ---------------------------------------------------------------- 解释器解析 ----
def resolve_python(verbose=True):
    """按「venv 优先，退回当前解释器」解析要用的 python。返回 (Path, 来源说明)。

    venv 路径全部相对本脚本目录拼出，不写死绝对路径：
      Windows venv → <here>/<venv>/Scripts/python.exe
      POSIX   venv → <here>/<venv>/bin/python
    """
    for rel, tag in (("<venv>/Scripts/python.exe", "venv(Windows 布局)"),
                     ("<venv>/bin/python", "venv(POSIX 布局)")):
        cand = HERE / rel
        if cand.exists():
            if verbose:
                print(f"[解释器] {cand}  ← {tag}（相对本脚本目录解析）")
            return cand, tag
    if verbose:
        print(f"[解释器] {sys.executable}  ← 未发现 <venv>，退回当前解释器 sys.executable")
    return Path(sys.executable), "sys.executable"


# ---------------------------------------------------------------- 模板发现 ----
def discover_templates(quick=False):
    """扫描 ``0*/*.py``，返回 [(类别, 模板路径), ...]（类别按名排序，类内按名排序）。

    quick=True 时每类只留首件（8 件），用于「改完模板先看有没有整体炸」。
    """
    items = []
    for cdir in sorted(p for p in HERE.glob(CATEGORY_GLOB) if p.is_dir()):
        pys = sorted(p for p in cdir.glob("*.py") if p.is_file())
        if quick:
            pys = pys[:1]
        items.extend((cdir.name, p) for p in pys)
    return items


# ---------------------------------------------------------------- 单件执行 ----
def _tail_lines(text, n=TAIL_LINES):
    """取输出最后 n 行非空文本（去首尾空白）。"""
    if not text:
        return []
    lines = [ln.strip() for ln in str(text).splitlines()]
    return [ln for ln in lines if ln][-n:]


def run_one(py, category, path, timeout=TIMEOUT_S):
    """跑单个模板：cwd=模板所在目录，超时 timeout 秒。返回结果 dict。"""
    rel = path.relative_to(HERE).as_posix()
    env = dict(os.environ)
    # 强制子进程 UTF-8 输出，避免中文模板在 cp936 控制台下抛 UnicodeEncodeError
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    t0 = time.perf_counter()
    try:
        cp = subprocess.run([str(py), path.name], cwd=str(path.parent),
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=timeout, env=env)
        rc, status = cp.returncode, ("PASS" if cp.returncode == 0 else "FAIL")
        out, err = cp.stdout or "", cp.stderr or ""
    except subprocess.TimeoutExpired as e:
        rc, status = None, "TIMEOUT"
        out, err = _dec(e.stdout), _dec(e.stderr)
    except OSError as e:  # 解释器不可执行 / 路径异常
        rc, status = None, "ERROR"
        out, err = "", f"{type(e).__name__}: {e}"
    elapsed = time.perf_counter() - t0

    tail_out, tail_err = _tail_lines(out), _tail_lines(err)
    if status == "TIMEOUT":
        summary = f"超时 >{timeout:g}s 被终止"
    elif status == "PASS":
        summary = tail_out[-1] if tail_out else "(无输出)"
    else:  # FAIL / ERROR：优先看 stderr（异常栈尾行最有用）
        summary = tail_err[-1] if tail_err else (tail_out[-1] if tail_out else "(无输出)")

    return {
        "name": path.name,
        "rel": rel,
        "category": category,
        "dir": path.parent.as_posix(),
        "rc": rc,
        "status": status,
        "seconds": round(elapsed, 3),
        "summary": _squash(summary),
        "tail_stdout": tail_out,
        "tail_stderr": tail_err,
    }


def _dec(b):
    """TimeoutExpired 携带的可能是 bytes；统一解成 str。"""
    if b is None:
        return ""
    if isinstance(b, bytes):
        return b.decode("utf-8", errors="replace")
    return str(b)


def _squash(s):
    """压缩成单行、去多余空白、截断——供表格摘要列使用。"""
    s = " ".join(str(s).split())
    return s[:SUMMARY_LIMIT - 1] + "…" if len(s) > SUMMARY_LIMIT else s


# ---------------------------------------------------------------- 控制台表格 ----
def _disp_width(s):
    """终端显示宽度：东亚宽/全角字符按 2 列计，保证中文列对齐。"""
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in s)


def _pad(s, width):
    """按显示宽度左对齐补空格（超宽则截断加省略号）。"""
    s = str(s)
    w = _disp_width(s)
    if w > width:
        while _disp_width(s) > width - 1 and s:
            s = s[:-1]
        s += "…"
        w = _disp_width(s)
    return s + " " * max(0, width - w)


def print_table(results):
    """打印控制台表格（含表头与分组分隔线）。"""
    cols = [("件名", 26), ("类别", 18), ("rc", 4), ("判定", 8), ("耗时", 8), ("输出摘要", 62)]
    header = "  ".join(_pad(t, w) for t, w in cols)
    line = "-" * _disp_width(header)
    print("\n" + header)
    print(line)
    prev = None
    for r in results:
        if prev is not None and r["category"] != prev:
            print("-" * _disp_width(header))  # 类间分隔线
        prev = r["category"]
        mark = {"PASS": "PASS", "FAIL": "FAIL", "TIMEOUT": "TIMEOUT", "ERROR": "ERROR"}[r["status"]]
        print("  ".join(_pad(x, w) for x, w in (
            (r["name"], cols[0][1]),
            (r["category"], cols[1][1]),
            ("-" if r["rc"] is None else r["rc"], cols[2][1]),
            (mark, cols[3][1]),
            (f"{r['seconds']:.2f}s", cols[4][1]),
            (r["summary"], cols[5][1]),
        )))
    print(line)


# ---------------------------------------------------------------- 报告落盘 ----
def _md_cell(s):
    """Markdown 表格单元格转义（竖线 + 换行）。"""
    return str(s).replace("|", "\\|").replace("\n", " ").strip() or "—"


def _counts(results):
    c = {"PASS": 0, "FAIL": 0, "TIMEOUT": 0, "ERROR": 0}
    for r in results:
        c[r["status"]] = c.get(r["status"], 0) + 1
    return c


def build_markdown(results, py, py_tag, mode, started, elapsed):
    """生成 Markdown 报告文本（件名|类别|rc|判定|输出摘要 + 汇总 + 分类小计）。"""
    c = _counts(results)
    n = len(results)
    bad = n - c["PASS"]
    L = []
    L.append("# 模板冒烟报告（smoke_all.py）")
    L.append("")
    L.append(f"- 开始时间：{started}")
    L.append(f"- 解释器：`{py}`（{py_tag}）")
    L.append(f"- 模式：{mode}｜件数：{n}｜单件超时：{TIMEOUT_S}s｜总耗时：{elapsed:.2f}s")
    L.append(f"- 结果：**{c['PASS']}/{n} PASS**"
             + (f"；FAIL {c['FAIL']}，TIMEOUT {c['TIMEOUT']}，ERROR {c['ERROR']}" if bad else "")
             + (" － 全部通过" if bad == 0 else " － 存在失败项"))
    L.append("")
    L.append("| 件名 | 类别 | rc | 判定 | 输出摘要（末行） |")
    L.append("|---|---|---|---|---|")
    for r in results:
        rc = "-" if r["rc"] is None else r["rc"]
        L.append(f"| `{_md_cell(r['rel'])}` | {_md_cell(r['category'])} | {rc} | "
                 f"{r['status']} | {_md_cell(r['summary'])} |")
    L.append("")
    L.append("## 分类小计")
    L.append("")
    L.append("| 类别 | 件数 | PASS | 非 PASS |")
    L.append("|---|---|---|---|")
    cats = []
    for r in results:                      # 保持出现顺序
        if r["category"] not in cats:
            cats.append(r["category"])
    for cat in cats:
        rows = [r for r in results if r["category"] == cat]
        p = sum(1 for r in rows if r["status"] == "PASS")
        L.append(f"| {_md_cell(cat)} | {len(rows)} | {p} | {len(rows) - p} |")
    L.append("")
    if bad:
        L.append("## 失败明细")
        L.append("")
        for r in results:
            if r["status"] == "PASS":
                continue
            L.append(f"### `{r['rel']}` — {r['status']}（rc={r['rc']}）")
            L.append("")
            L.append("```text")
            for ln in (r["tail_stderr"] or r["tail_stdout"]):
                L.append(ln)
            L.append("```")
            L.append("")
    L.append("---")
    L.append("")
    L.append("判定口径：只看子进程 rc（0=PASS）。数值正确性不在本 runner 范围内。")
    L.append("")
    return "\n".join(L)


def write_text(path: Path, text: str):
    """写 UTF-8 + LF 文本（显式 newline='\\n'，Windows 下不产生 CRLF）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def emit(results, py, py_tag, mode, tag="", want_json=False):
    """落盘 md（+ 可选 json），返回报告路径列表。"""
    started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elapsed = sum(r["seconds"] for r in results)
    c = _counts(results)
    n = len(results)
    base = REPORT_MD if not tag else REPORT_MD.replace(".md", f"_{tag}.md")
    jbase = REPORT_JSON if not tag else REPORT_JSON.replace(".json", f"_{tag}.json")
    md_path = OUT_DIR / base

    write_text(md_path, build_markdown(results, py, py_tag, mode, started, elapsed))
    outs = [md_path]

    if want_json:
        payload = {
            "started": started,
            "interpreter": str(py),
            "interpreter_source": py_tag,
            "mode": mode,
            "timeout_s": TIMEOUT_S,
            "total": n,
            "pass": c["PASS"], "fail": c["FAIL"],
            "timeout": c["TIMEOUT"], "error": c["ERROR"],
            "elapsed_s": round(elapsed, 3),
            "results": results,
        }
        jp = OUT_DIR / jbase
        write_text(jp, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        outs.append(jp)
    return outs


# ---------------------------------------------------------------- main ----
def main(argv=None):
    # 控制台按 UTF-8 输出（管道重定向时避免中文乱码；失败则不影响主流程）
    _reconf = getattr(sys.stdout, "reconfigure", None)   # 兼容被替换的 stdout 对象
    if callable(_reconf):
        try:
            _reconf(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(
        description="35 个模板一键冒烟 runner（数模代码仓 / templates-library）")
    ap.add_argument("--quick", action="store_true", help="每类只跑首件（8 件）")
    ap.add_argument("--json", action="store_true", help="额外产出 JSON 报告")
    ap.add_argument("--selftest", action="store_true",
                    help="自证：跑 3 件代表（lp / grey_relation / ga）+ 校验发现机制")
    ap.add_argument("--timeout", type=float, default=TIMEOUT_S, help=f"单件超时秒数（默认 {TIMEOUT_S}）")
    args = ap.parse_args(argv)

    print("=" * 78)
    print("模板冒烟 runner｜数模代码仓 templates-library")
    print("=" * 78)
    py, py_tag = resolve_python()

    # ---- 选择目标 ----
    if args.selftest:
        all_items = discover_templates(quick=False)
        by_rel = {p.relative_to(HERE).as_posix(): (c, p) for c, p in all_items}
        items, missing = [], []
        for rel in SELFTEST_TARGETS:
            if rel in by_rel:
                items.append(by_rel[rel])
            else:
                missing.append(rel)
        mode = f"SELFTEST（3 件代表 + 发现机制校验）"
        print(f"[自证] 发现模板 {len(all_items)} 件（期望 {EXPECTED_TEMPLATES} 件）；"
              f"选中代表 {len(items)} 件")
        if missing:
            print(f"[自证] ✗ 目标缺失：{missing}")
        # 发现机制自证：全量扫描必须能找齐 8 类 35 件
        cats = sorted({c for c, _ in all_items})
        ok_discovery = (len(all_items) == EXPECTED_TEMPLATES and len(cats) == 8)
        print(f"[自证] 类别 {len(cats)} 个：{'、'.join(cats)}")
        print(f"[自证] 发现机制：{'✓ 8 类 35 件齐全' if ok_discovery else '✗ 数量异常'}")
    else:
        items = discover_templates(quick=args.quick)
        mode = "QUICK（每类首件）" if args.quick else "FULL（全量）"
        ok_discovery = None

    if not items:
        print("[×] 未发现任何模板（期望 0*/*.py）——检查是否在 templates-library 目录下运行。")
        return 2

    print(f"[模式] {mode}｜即将执行 {len(items)} 件｜单件超时 {args.timeout:g}s")

    # ---- 逐件执行 ----
    results = []
    for i, (cat, path) in enumerate(items, 1):
        print(f"[{i:>2}/{len(items)}] {path.relative_to(HERE).as_posix()} ... ", end="", flush=True)
        r = run_one(py, cat, path, timeout=args.timeout)
        results.append(r)
        print(f"{r['status']} rc={r['rc']} {r['seconds']:.2f}s")

    # ---- 控制台汇总 ----
    print_table(results)
    c = _counts(results)
    n = len(results)
    print(f"\n汇总：{c['PASS']}/{n} PASS"
          + (f"｜FAIL {c['FAIL']}｜TIMEOUT {c['TIMEOUT']}｜ERROR {c['ERROR']}" if n - c['PASS'] else "｜无失败项")
          + f"｜总耗时 {sum(r['seconds'] for r in results):.2f}s")

    # ---- 落盘 ----
    # 只有全量跑写正式名（smoke_all_report.*）；quick/selftest 用后缀名，避免部分结果
    # 覆盖掉「全量报告」这件权威产物（否则事后翻报告会误以为模板只有 8 件）。
    tag = "selftest" if args.selftest else ("quick" if args.quick else "")
    outs = emit(results, py, py_tag, mode, tag=tag, want_json=args.json)
    for p in outs:
        print(f"[报告] {p.relative_to(HERE).as_posix()}")

    ok = (c["PASS"] == n)
    if args.selftest:
        ok = ok and (ok_discovery is True) and len(results) == len(SELFTEST_TARGETS)
        print(f"\n[SELFTEST] {'✓ 通过' if ok else '✗ 未通过'}"
              f"（3 件代表全 PASS + 8 类 35 件可发现）")
    print(f"[退出码] {0 if ok else 1}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
