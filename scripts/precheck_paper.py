#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Euler 交付前规则化脚本预检（E-T1-3 · v2.3 2026-09-20 · B-T1-5 提示增强：A0/A3/B1/B2/C-art2 文案明确化，语义与权重不变；v2.2 = C-art2 结构级判定）

用途：判分前置的**非 LLM 裁量**检查——摘要要素 / 图表单位 / artifact 存在性 /
结构帽代理指标。把可机械判定的项从「评委记忆」里拿走，只把真正的建模判断留给评审。

用法：
    python precheck_paper.py <paper.txt|paper.docx> [--profile our|ref] [--json]
      --profile our（默认 used for 我方交付）= 硬项 FAIL 会阻断（exit 1）
      --profile ref（用于 holdout/锚样）      = 全部降级为 WARN 画像（exit 0）
    exit 0 = 无 FAIL; 1 = 存在 FAIL; 2 = 输入错误

口径：与 `references/scoring-rubric.md` §2 结构帽（C1–C4）对齐；预检 FAIL
**不直接判档**，但必须进入判分会话的「预检裁决」小节（逐项说明）。
"""
from __future__ import annotations

import json
import re
import sys


def load_text(path: str) -> str:
    if path.lower().endswith(".docx"):
        import xml.etree.ElementTree as ET
        import zipfile
        W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        z = zipfile.ZipFile(path)
        root = ET.fromstring(z.read("word/document.xml"))
        return "\n".join("".join(t.text or "" for t in p.iter(W + "t"))
                         for p in root.iter(W + "p"))
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def find_abstract(text: str) -> str:
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if re.match(r"^\s*[#\s]*摘\s*要", ln) or ln.strip().startswith("摘要") or ln.strip() == "Abstract" \
           or (ln.lstrip().startswith("#") and "摘要" in ln) \
           or re.match(r"^\s*[#\s]*[A-Z]\.?\s*[、.．]?\s*.*摘要", ln):
            buf = []
            for ln2 in lines[i + 1:i + 80]:
                if re.match(r"^\s*(关键词|关键字|目\s*录|Abstract|一、|1\.?\s*引言|引言|Key\s*words)", ln2):
                    break
                buf.append(ln2)
            return "\n".join(buf)
    return ""


NUM_RE = re.compile(r"\d+(?:\.\d+)?\s*%|\d+\.\d+|\d{2,}")
# 单位词表（含中英文常见单位；用于密度与题注扫描）
UNIT_TOKENS = r"mm|cm|m/s|km|kg|mg|μg|mL|μL|L|h\b|min|s\b|%|℃|K\b|kPa|MPa|Pa\b|N\b|N·m|W\b|J\b|万元|亿元|元|件|台|个|度|焦耳|瓦特"
UNIT_RE = re.compile(r"(?:（[^）]{0,30}?(?:%s)[^）]{0,30}?）|\([^)]{0,30}?(?:%s)[^)]{0,30}?\)|单位[:：]|\b(?:%s)\b)" % (UNIT_TOKENS, UNIT_TOKENS, UNIT_TOKENS))
CAP_RE = re.compile(r"^\s*(图|表)\s*\d+")


def precheck(text: str, profile: str) -> dict:
    ref_mode = profile == "ref"

    def grade(level: str) -> str:
        """ref 模式下 FAIL→WARN（画像不判闸）。"""
        if ref_mode and level == "FAIL":
            return "WARN"
        return level

    abstract = find_abstract(text)
    res: dict = {"profile": profile, "checks": [], "fails": 0, "warns": 0}

    def add(level, key, msg):
        level = grade(level)
        res["checks"].append({"level": level, "key": key, "msg": msg})
        if level == "FAIL":
            res["fails"] += 1
        elif level == "WARN":
            res["warns"] += 1

    # ---- A. 摘要五要素（对标 07-论文撰写 摘要标准） ----
    if not abstract:
        add("FAIL", "A0", "未定位到摘要段（标题含「摘要」）——变体标题（【摘要】/「摘 要：」/Abstract）可能漏检，人工核后按 07 摘要标准处理")
    else:
        hit = 0
        items = [
            ("A1 问题", r"问题|背景|目标|针对|本文研究"),
            ("A2 方法", r"模型|方法|算法|求解|建立|提出|设计"),
            ("A3 量化结果", None),
            ("A4 检验", r"检验|敏感性|灵敏度|鲁棒|误差|验证|对照|对比|稳定性"),
            ("A5 结论", r"结论|表明|说明|改进|推广|总结"),
        ]
        for key, pat in items:
            ok = bool(NUM_RE.search(abstract)) if pat is None else bool(re.search(pat, abstract))
            hit += ok
            if key == "A3 量化结果":
                msg = "在位" if ok else "未检出（画像项）——个位数结果（如「提升 8 个百分点」）不计入数字命中，人工核"
            else:
                msg = "在位" if ok else "未检出（画像项）"
            add("OK" if ok else "WARN", key, msg)
        add("OK" if hit >= 4 else ("WARN" if hit >= 3 else "FAIL"), "A*",
            "五要素命中 %d/5（<3 提示摘要空洞风险）" % hit)
        if not NUM_RE.search(abstract):
            add("FAIL", "C1帽", "摘要无任何可点名数字 → 结构帽 C1 触发（A ≤18）")

    # ---- B. 图表单位 ----
    caps = [ln.strip() for ln in text.splitlines() if CAP_RE.match(ln.strip())]
    unit_hits = len(UNIT_RE.findall(text))
    add("OK" if unit_hits >= 20 else ("WARN" if unit_hits >= 5 else "FAIL"), "B1",
        "全文单位记号 %d 处（<5 提示全文无单位，硬门禁；变体单位 °C / m² / 万件 等可能未计入 → 人工核）" % unit_hits)
    if caps:
        wu = [c[:48] for c in caps if not UNIT_RE.search(c)]
        add("OK" if not wu else "WARN", "B2",
            "图/表题注 %d 条，其中 %d 条题内无单位（人工核清单样例：%s）"
            % (len(caps), len(wu), "；".join(wu[:3]) if wu else "—"))
    else:
        add("WARN", "B2", "未检出「图 N/表 N」题注行（格式或提取问题，人工核；加粗/行内题注如「**图 1**」「图1：」可能漏检）")

    # ---- C. artifact 存在性 ----
    # C-art2 结构化判定（v2.2 · 2026-09-20 盲评校准）：仅出现「参考文献」字样不算结构级——
    # 需有参考文献节标题 + ≥3 条目（[N]/N. 起行）；仅有字样 → WARN（防字样级假阳性）
    arts = [
        ("C-art1 代码/复现材料", r"代码|程序|脚本|复现|附录\s*[A-Z]?.*代码|GitHub|仓库"),
        ("C-art3 AI 使用声明", r"AI|人工智能|大模型|辅助工具"),
    ]
    for key, pat in arts:
        ok = bool(re.search(pat, text))
        add("OK" if ok else "WARN", key, "存在" if ok else "缺失")

    has_sec = bool(re.search(r"(^|\n)\s*#{0,6}\s*(参考文献|References)\b", text))
    n_entries = len(re.findall(r"(?m)^\s*(\[\d+\]|\d{1,3}[.、]\s)", text))
    if has_sec and n_entries >= 3:
        add("OK", "C-art2 参考文献", "结构级存在（节标题 + %d 条目）" % n_entries)
    elif has_sec or n_entries >= 3:
        add("WARN", "C-art2 参考文献", "疑似部分（节标题=%s / 条目=%d）——人工核；条目按「[N]」/「N. 」计，无编号条目可能漏计" % (has_sec, n_entries))
    elif re.search(r"参考文献|References|\[1\]", text):
        add("FAIL", "C-art2 参考文献", "仅字样级命中（无节标题/无条目）→ 视为未形成")
    else:
        add("FAIL", "C-art2 参考文献", "缺失")

    # ---- D. 结构帽代理指标（只报风险，不判档） ----
    c2_kw = sum(bool(re.search(p, text)) for p in
                (r"敏感性|灵敏度", r"互验|交叉验证|双方法|解析解|闭式|一致性", r"特例|边界|退化|极端|极限"))
    add("OK" if c2_kw >= 2 else "WARN", "D1",
        "互验/特例/闭式信号 %d/3（<2 提示 T 维画像薄）" % c2_kw)
    models = len(re.findall(r"模型|算法", text))
    compare = len(re.findall(r"对照|对比|基准|baseline", text))
    ratio = compare / max(models, 1)
    add("OK" if ratio >= 0.10 or compare >= 12 else "WARN", "D2",
        "模型/算法词 %d 次 vs 对照/对比词 %d 次（占比 %.2f，<0.10 提示反通胀风险）" % (models, compare, ratio))
    return res


def main() -> int:
    argv = sys.argv[1:]
    args, skip_next = [], False
    for a in argv:
        if skip_next:            # --profile 的值（our|ref）不是文件参数
            skip_next = False
            continue
        if a == "--profile":
            skip_next = True
            continue
        if a.startswith("--"):
            continue
        args.append(a)
    if not args:
        print(__doc__)
        return 2
    profile = "our"
    if "--profile" in sys.argv:
        profile = sys.argv[sys.argv.index("--profile") + 1]
        if profile not in ("our", "ref"):
            print("profile 必须是 our|ref")
            return 2
    text = load_text(args[0])
    res = precheck(text, profile)
    if "--json" in sys.argv:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print("预检对象:", args[0], "| profile:", profile, "| 字符数:", len(text))
        for c in res["checks"]:
            print("[%s] %-16s %s" % (c["level"], c["key"], c["msg"]))
        print("\n%s (OK=%d WARN=%d FAIL=%d)"
              % ("PRECHECK PASS" if res["fails"] == 0 else "PRECHECK HAS FAILURES",
                 sum(1 for c in res["checks"] if c["level"] == "OK"), res["warns"], res["fails"]))
    return 0 if res["fails"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
