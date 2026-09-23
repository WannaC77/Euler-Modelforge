#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""env_check —— Euler 环境自检（E-R 底座 · 环境档位卡）

适用场景 / Purpose
    任何会话/agent 装载 Euler 引擎（`Euler-ENGINE.md` §0 三步装载）的第一步：
    一键核验「求解解释器 / 依赖包 / LaTeX / 字体 / 目录在位」，输出
    **档位（T0/T1/T2）+ 缺件清单**，支撑 E-R 门禁「env_check 过」。
    口径对齐 `references/路径与资产清单.md` §3 环境档位表。

档位 / Tiers
    T0 核心：可用解释器（venv 优先，缺则系统 Python）带 numpy/scipy；Euler 根（workflows/references）在位
    T1 数据/图件线：+ venv 四包齐 / matplotlib / pandas / 模板库 35 / utils 图件机检 / 论文模板（美赛随包；国赛模板位需自备）
    T2 论文线：+ xelatex（PATH）/ 中文字体 / pymupdf（PDF 回读）
    缺件均为「降级可走」：按 `Euler-ENGINE.md` §1 模块表「降级」列执行并标 `[降级]`。

用法 / Usage
    python env_check.py [--root <包根|系统根>] [--json]
    python env_check.py --selftest        # 自证：断言根解析 / 解释器栈 / workflows 在位
    exit 0 = 达到 T0 及以上；1 = 未达 T0

路径 / Paths（探测链 · 顺序固定 · 全部相对脚本自身位置）
    1. 环境变量覆盖（最高优先）：`MODELFORGE_ROOT`（未设则兼容 `OPENLAB_ROOT`）—— 指向包根
    2. 自脚本位置向上逐级：某父目录**同时**含 `templates-library/` 与 `workflows/` → 该目录＝包根（major；
       包内布局 system_root 与 major 合一）
    3. 旧布局兼容：某父目录含 `Euler` 子目录（其下 `workflows/` 在位）→ system_root＝该父目录，
       major＝该父目录下的 `Euler`
    4. 全失败 → major＝脚本父目录的父目录（`tools/` 的上一级），system_root 同值，
       后续检查项允许 FAIL（诚实降级，不假装成功）
    包内布局下：euler 根 = major（`workflows/` · `references/` · `scripts/` 直接在包根下）；
    模板库 = `major/templates-library`；论文模板 = `major/paper-templates`。
    源码内**不写死任何用户绝对路径**——解释器候选只经 PATH、`py` 启动器、环境变量展开
    （%LOCALAPPDATA% / %ProgramFiles% 等）发现；所有目录检查都相对包根拼接。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

VERSION = 'v1.1 (2026-09-22)'   # v1.1：根解析改「探测链」（包内布局 + 环境变量覆盖 + 旧布局兼容 + 诚实降级）
SUBPROC_TIMEOUT = 240          # 每个解释器探测的超时（首次导入 matplotlib 可能较慢）
SYSTEM_PROBE_MAX = 2           # 系统解释器最多探测几个（venv 另计）
UTILS_4 = ('plot_style.py', 'sensitivity.py', 'latex_table.py', 'figcheck.py')
PKG_SET = ('numpy', 'scipy', 'pandas', 'matplotlib', 'pymupdf')

# 子进程探测脚本：一次返回「版本 + 包版本 + 字体」；结果用哨兵行回传，避免被噪声干扰。
PROBE_SRC = r'''
import json, sys
out = {"exe": sys.executable, "ver": "%d.%d.%d" % sys.version_info[:3],
       "ok_version": sys.version_info >= (3, 10), "pkgs": {}, "cjk_font": None, "n_fonts": 0}
for name in ("numpy", "scipy", "pandas", "matplotlib", "pymupdf"):
    try:
        out["pkgs"][name] = getattr(__import__(name), "__version__", "?")
    except Exception:
        out["pkgs"][name] = None
try:
    from matplotlib import font_manager
    names = {f.name for f in font_manager.fontManager.ttflist}
    out["n_fonts"] = len(names)
    for c in ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Source Han Sans SC",
              "SimSun", "KaiTi", "FangSong"):
        if c in names:
            out["cjk_font"] = c
            break
except Exception:
    pass
print("__EULER_PROBE__" + json.dumps(out, ensure_ascii=False))
'''


# ---------------------------------------------------------------- 定位（探测链 · 无绝对路径）

SCRIPT_DIR = Path(__file__).resolve().parent            # `tools/`
ENV_ROOT_KEYS = ('MODELFORGE_ROOT', 'OPENLAB_ROOT')     # 探测链第 1 档：包根覆盖（环境变量）
PKG_MARKS = ('templates-library', 'workflows')          # 包内布局标记：同一父目录下并存 → 该目录＝包根
EULER_DIR, WF_DIR = 'Euler', 'workflows'                # 旧布局标记：<系统根>/Euler/workflows 在位


def env_root() -> 'Path | None':
    """探测链第 1 档：环境变量覆盖（`MODELFORGE_ROOT`，未设则 `OPENLAB_ROOT`）。未设/不存在 → None。"""
    for key in ENV_ROOT_KEYS:
        val = os.environ.get(key)
        if not val:
            continue
        try:
            p = Path(val).expanduser()
        except Exception:
            continue
        if p.is_dir():
            return p.resolve()
    return None


def upward(start: Path) -> list:
    """自 start 向上逐级（含 start 自身）的目录序列。"""
    s = Path(start)
    return [s] + list(s.parents)


def probe_chain(start: Path, use_env: bool = True) -> 'tuple[Path, Path, str]':
    """根解析探测链 → (系统根, major, 来源)。顺序固定，任何判断都相对 start（脚本自身位置）推导。"""
    if use_env:
        envr = env_root()
        if envr is not None:                                        # ① 环境变量覆盖（最高优先）
            return envr, envr, 'env:MODELFORGE_ROOT/OPENLAB_ROOT'
    for p in upward(start):                                         # ② 包内布局（major 与 system_root 合一）
        if all((p / m).is_dir() for m in PKG_MARKS):
            return p, p, 'probe:templates-library+workflows'
    for p in upward(start):                                         # ③ 旧布局兼容
        if (p / EULER_DIR / WF_DIR).is_dir():
            return p, p / EULER_DIR, 'probe:旧布局（Euler 子目录 workflows 在位）'
    base = Path(start)                                              # ④ 诚实降级：tools/ 的上一级
    fallback = base.parent if base.name == 'tools' else base
    return fallback, fallback, 'fallback:tools/ 上一级'


def euler_root(major: Path) -> Path:
    """euler 根：旧布局（`major/Euler/workflows` 在位）＝ `major/Euler`；包内布局＝ major 本身。"""
    return major / EULER_DIR if (major / EULER_DIR / WF_DIR).is_dir() else major


def layout_label(major: Path, euler: Path) -> str:
    """euler 根在报告里的稳定标签：包内布局 =「包根」，旧布局 =「Euler」（不随包目录改名漂移）。"""
    try:
        rel = euler.relative_to(major).as_posix()
    except Exception:
        return EULER_DIR
    return EULER_DIR if rel != '.' else '包根'


def resolve_roots(root: 'Path | None' = None) -> 'tuple[Path, Path, str]':
    """解析 (系统根, major, 来源)。

    root=None → 自脚本位置走探测链（含环境变量档）；显式 root → 以该路径为起点（用户显式优先，
    跳过环境变量档）。接受包根 / 系统根 / 任意子级（向上探测）；指定更高层父目录时按探测链第 4 档
    降级，并在「来源」字段如实标注（诚实降级，不猜）。
    """
    if root is None:
        return probe_chain(SCRIPT_DIR, use_env=True)
    try:
        r = Path(root).expanduser().resolve()
    except Exception:
        r = Path(root)
    return probe_chain(r if r.is_dir() else r.parent, use_env=False)


# ---------------------------------------------------------------- 解释器发现与探测

def _resolved(p) -> 'Path | None':
    try:
        return Path(p).resolve()
    except Exception:
        return None


def is_venv_python(exe: Path) -> bool:
    """venv 判定：解释器上一级或上两级存在 pyvenv.cfg。"""
    try:
        return (exe.parent / 'pyvenv.cfg').is_file() or (exe.parent.parent / 'pyvenv.cfg').is_file()
    except Exception:
        return False


def discover_interpreters(prog: Path) -> 'tuple[Path | None, list]':
    """返回 (项目 venv 解释器或 None, 系统解释器候选列表)。全相对/PATH 发现。"""
    venv_py = None
    for rel in ('Scripts/python.exe', 'bin/python', 'bin/python3'):
        e = prog / '<venv>' / rel
        if e.is_file():
            venv_py = _resolved(e)
            break

    system = []
    if os.name == 'nt':
        py = shutil.which('py')                   # Windows 启动器：py -0p 列全部已装解释器
        if py:
            try:
                out = subprocess.run([py, '-0p'], capture_output=True, text=True,
                                     encoding='utf-8', errors='replace', timeout=30)
                for ln in (out.stdout or '').splitlines():
                    for tok in ln.replace('*', ' ').split():
                        # 只认「真实存在」的 …/python.exe 整路径 token（避开 -V: 前缀噪声）
                        c = Path(tok) if tok.lower().endswith('python.exe') else None
                        if c is not None and c.is_file():
                            system.append(c)
            except Exception:
                pass
    for env_key, pat in (('LOCALAPPDATA', 'Programs/Python/Python3*/python.exe'),
                         ('ProgramFiles', 'Python3*/python.exe'),
                         ('ProgramFiles(x86)', 'Python3*/python.exe')):
        base = os.environ.get(env_key)
        if not base:
            continue
        for hit in sorted(glob.glob(os.path.join(base, pat))):
            system.append(Path(hit))
    for name in ('python', 'python3', 'python3.13', 'python3.12', 'python3.11'):
        w = shutil.which(name)
        if w:
            system.append(Path(w))
    system.append(Path(sys.executable))            # 兜底：当前解释器

    seen, out_list = set(), []
    for p in system:
        rp = _resolved(p)
        if not rp or rp in seen:
            continue
        seen.add(rp)
        if is_venv_python(rp):                     # 任何 venv 都不计入「系统 Python」
            continue
        if venv_py and rp == venv_py:
            continue
        out_list.append(rp)
    return venv_py, out_list


def probe_interpreter(exe: Path, role: str) -> dict:
    """子进程探测一个解释器：版本 + 五个包 + 中文字体。失败不抛，只标 ok=False。"""
    rec = dict(role=role, exe=str(exe), ver=None, ok_version=False, pkgs={}, cjk_font=None,
               n_fonts=0, ok=False, note='', secs=0.0)
    t0 = time.time()
    try:
        p = subprocess.run([str(exe), '-c', PROBE_SRC], capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=SUBPROC_TIMEOUT)
    except Exception as e:                          # 超时/权限/损坏解释器
        rec['note'] = '探测失败：%s' % e
        return rec
    rec['secs'] = round(time.time() - t0, 1)
    payload = ''
    for ln in (p.stdout or '').splitlines():
        if ln.startswith('__EULER_PROBE__'):
            payload = ln[len('__EULER_PROBE__'):]
    if not payload:
        tail = [l for l in ((p.stderr or '') + (p.stdout or '')).splitlines() if l.strip()]
        rec['note'] = '无探测输出（rc=%d）%s' % (p.returncode, (tail[-1][:120] if tail else ''))
        return rec
    try:
        rec.update(json.loads(payload))
    except Exception as e:
        rec['note'] = '探测输出解析失败：%s' % e
        return rec
    rec['ok'] = True
    rec['note'] = 'rc=0 · %.1fs' % rec['secs']
    return rec


def probe_stack(prog: Path) -> 'tuple[list, dict | None]':
    """探测 venv + 若干系统解释器；返回 (全部探测记录, 首个满足 numpy+scipy 的记录)。"""
    venv_py, system_cands = discover_interpreters(prog)
    recs, core = [], None

    def satisfies(r: dict) -> bool:
        pk = r.get('pkgs') or {}
        return bool(pk.get('numpy')) and bool(pk.get('scipy'))

    if venv_py:
        r = probe_interpreter(venv_py, 'venv')
        recs.append(r)
        if satisfies(r):
            core = r
    for cand in system_cands[:SYSTEM_PROBE_MAX]:
        r = probe_interpreter(cand, 'system')
        recs.append(r)
        if core is None and satisfies(r):
            core = r
        if satisfies(r):
            break
    return recs, core


def has_pkg(rec: dict, name: str) -> bool:
    return bool((rec or {}).get('pkgs', {}).get(name))


def pick_rec(recs: list, name: str) -> 'dict | None':
    for r in recs:
        if has_pkg(r, name):
            return r
    return None


# ---------------------------------------------------------------- 目录清点（相对包根）

def count_numbered_workflows(euler: Path) -> int:
    """workflows/ 正本计数：`NN-*.md`（00–10），排除 .bak 历史档。"""
    wf = euler / 'workflows'
    if not wf.is_dir():
        return 0
    return len([f for f in wf.iterdir() if f.is_file() and re.match(r'^\d\d-.+\.md$', f.name)])


def count_templates(prog: Path) -> 'tuple[int, int]':
    """模板库计数：8 个分类目录下 maxdepth=1 的 *.py（口径 = 35 模板 + utils 另计）。"""
    n = g = 0
    if prog.is_dir():
        for d in sorted(prog.iterdir()):
            if d.is_dir() and re.match(r'^0[1-8]-', d.name):
                g += 1
                n += len([f for f in d.glob('*.py') if f.is_file()])
    return n, g


def count_files(p: Path) -> int:
    if not p.is_dir():
        return 0
    return len([f for f in p.rglob('*') if f.is_file() and '.bak' not in f.name])


def find_dirs(parent: Path, suffix: str) -> list:
    if not parent.is_dir():
        return []
    return sorted([d for d in parent.iterdir() if d.is_dir() and d.name.endswith(suffix)])


# ---------------------------------------------------------------- 主检查

def run(root: 'Path | None' = None) -> dict:
    system_root, major, src = resolve_roots(root)
    euler = euler_root(major)                     # 包内布局 = major；旧布局 = major/Euler
    disp = layout_label(major, euler)
    prog = major / 'templates-library'
    paper = major / 'paper-templates'

    recs, core = probe_stack(prog)
    venv_rec = next((r for r in recs if r['role'] == 'venv'), None)

    r: dict = dict(version=VERSION, system_root=str(system_root), major_root=str(major),
                   euler_dir=str(euler), root_source=src,
                   python=sys.version.split()[0], self_python=sys.executable,
                   items=[], missing=[], interpreters=recs)

    def item(name: str, ok: bool, note: str, tier: str) -> None:
        r['items'].append(dict(name=name, ok=bool(ok), note=note or ('OK' if ok else '缺'), tier=tier))
        if not ok:
            r['missing'].append(name)

    # ---- T0 核心
    wf_n = count_numbered_workflows(euler)
    item('系统根解析（Euler 根 workflows 在位）', (euler / 'workflows').is_dir(),
         '系统根=%s｜主根=%s｜来源=%s' % (system_root, major, src), 'T0')

    if core is not None:
        pk = core['pkgs']
        item('核心求解栈 numpy/scipy（venv 或系统 Python）', True,
             '%s Python %s · numpy %s / scipy %s' % (core['role'], core['ver'], pk.get('numpy'), pk.get('scipy')), 'T0')
    else:
        probed = '、'.join('%s(%s)' % (rec['role'], rec['ver'] or '不可用') for rec in recs) or '无'
        item('核心求解栈 numpy/scipy（venv 或系统 Python）', False, '已探测：%s —— 全部缺 numpy/scipy' % probed, 'T0')

    item('解释器 Python>=3.10', bool(core and core.get('ok_version')),
         '核验解释器 Python %s' % (core['ver'] if core else r['python']), 'T0')

    item('目录 workflows（00–10 正本 11 件）', wf_n >= 11,
         '%d 件正本（含 _SHARED/W-ABSORB 不计）' % wf_n if wf_n else '目录不存在（%s/%s）' % (disp, 'workflows'), 'T0')

    ref_n = count_files(euler / 'references')
    item('目录 references', (euler / 'references').is_dir() and ref_n >= 4, '%d 文件' % ref_n, 'T0')

    # ---- T1 数据 / 图件线
    if venv_rec:
        cfg = prog / '<venv>' / 'pyvenv.cfg'
        home = ''
        if cfg.is_file():
            for ln in cfg.read_text(encoding='utf-8', errors='replace').splitlines():
                if ln.lower().startswith('version_info'):
                    home = '｜pyvenv.cfg %s' % ln.split('=', 1)[-1].strip()
                    break
        item('venv <venv>', venv_rec['ok'], 'Python %s%s' % (venv_rec['ver'] or '?', home), 'T1')
        pk = venv_rec['pkgs']
        four = [n for n in ('numpy', 'scipy', 'pandas', 'matplotlib') if pk.get(n)]
        item('venv 四包 numpy/scipy/pandas/matplotlib', len(four) == 4,
             '、'.join('%s %s' % (n, pk[n]) for n in four) or '四包全缺', 'T1')
    else:
        item('venv <venv>', False, '不存在（降级：系统 Python 直跑，依赖按 requirements.txt 自备）', 'T1')
        item('venv 四包 numpy/scipy/pandas/matplotlib', False, 'venv 不存在', 'T1')

    for pkg, label, tier in (('matplotlib', 'matplotlib（图件线 E-M6）', 'T1'),
                             ('pandas', 'pandas（数据线 E-M4）', 'T1')):
        rec = pick_rec(recs, pkg)
        item(label, rec is not None,
             ('%s Python %s · %s' % (rec['role'], rec['ver'], rec['pkgs'][pkg])) if rec else '所有已探测解释器均缺', tier)

    tpl_n, tpl_g = count_templates(prog)
    item('目录 templates-library 模板库（8 类 35 模板）', tpl_n >= 35 and (prog / 'MODEL_GUIDE.md').is_file(),
         '%d 模板 / %d 类%s' % (tpl_n, tpl_g, '' if (prog / 'MODEL_GUIDE.md').is_file() else '｜MODEL_GUIDE.md 缺'), 'T1')

    miss_utils = [f for f in UTILS_4 if not (prog / 'utils' / f).is_file()]
    item('目录 templates-library/utils（图件机检 4 件）', not miss_utils,
         'plot_style / sensitivity / latex_table / figcheck 齐' if not miss_utils else '缺：%s' % '、'.join(miss_utils), 'T1')

    gs = [d for d in find_dirs(paper, '-CUMCM') if any(d.glob('*.cls'))]
    ms = [d for d in find_dirs(paper, '-MCM-ICM') if any(d.glob('*.cls'))]
    bat = (paper / '编译自检.bat').is_file()
    # 国赛模板位（07 整改）：第三方件许可待核 → **不随包**（目录内留获取指引）。
    # T1 判据只看「美赛模板 + 编译自检.bat」；国赛位只报状态（外置/已自备），不作为缺件 —— 与 README/CHANGELOG 口径一致。
    item('目录 paper-templates（美赛模板随包 + 编译自检.bat）', bool(ms and bat),
         '美赛 %s｜编译自检.bat %s｜国赛模板位 %s' % (
             ms[0].name if ms else '缺', '在' if bat else '缺',
             ('已自备：%s' % gs[0].name) if gs else '外置（第三方许可待核，不随包；需自备，见 paper-templates/国赛-CUMCM/README.md）'),
         'T1')

    pre = euler / 'scripts' / 'precheck_paper.py'
    item('scripts/precheck_paper.py（E-M8 预检）', pre.is_file(),
         '%d B' % pre.stat().st_size if pre.is_file() else '不存在', 'T1')

    # ---- T2 论文线
    xl = shutil.which('xelatex')
    pd = shutil.which('pdflatex')
    item('LaTeX xelatex（PATH）', bool(xl),
         '%s%s' % (xl, '｜pdflatex %s' % pd if pd else '') if xl else '不在 PATH（论文线降级：纯文本装配 + 清单）', 'T2')

    font_rec = next((rec for rec in recs if rec.get('cjk_font')), None)
    item('中文字体（图件 matplotlib 探测）', font_rec is not None,
         '%s（%s Python %s 命中）' % (font_rec['cjk_font'], font_rec['role'], font_rec['ver']) if font_rec
         else '未探测到（图件线降级：英文标签 + 人检）', 'T2')

    pm_rec = pick_rec(recs, 'pymupdf')
    item('pymupdf（PDF 回读 / 渲染复核）', pm_rec is not None,
         'pymupdf %s（%s Python %s）' % (pm_rec['pkgs']['pymupdf'], pm_rec['role'], pm_rec['ver']) if pm_rec
         else '所有已探测解释器均缺（PDF 复核降级）', 'T2')

    # ---- 档位
    def tier_ok(t: str) -> bool:
        return all(i['ok'] for i in r['items'] if i['tier'] == t)

    t0 = tier_ok('T0')
    t1 = t0 and tier_ok('T1')
    t2 = t1 and tier_ok('T2')
    r['tier'] = 'T2' if t2 else ('T1' if t1 else ('T0' if t0 else '未达 T0'))
    return r


# ---------------------------------------------------------------- 输出

def fmt_interp(rec: dict) -> str:
    pk = rec.get('pkgs') or {}
    pk_txt = '、'.join('%s %s' % (n, pk[n]) for n in PKG_SET if pk.get(n)) or '无包'
    return '| %s | `%s` | %s | %s | %s |' % (rec['role'], rec['exe'], rec['ver'] or '不可用', pk_txt, rec['note'])


def render(r: dict) -> str:
    lines = ['# Euler 环境自检（env_check %s）' % r['version'], '',
             '- 系统根：`%s`｜主根：`%s`｜来源：%s' % (r['system_root'], r['major_root'], r.get('root_source', '')),
             '- 自检解释器：%s（Python %s）' % (r['self_python'], r['python']), '',
             '## 解释器探测', '',
             '| role | 解释器 | 版本 | 已装包 | 备注 |', '|---|---|---|---|---|']
    lines += [fmt_interp(rec) for rec in r['interpreters']] or ['| — | — | — | — | 无 |']
    lines += ['', '## 检查项', '', '| 项 | 状态 | 说明 | 档 |', '|---|---|---|---|']
    for i in r['items']:
        lines.append('| %s | %s | %s | %s |' % (i['name'], 'PASS' if i['ok'] else 'MISS', i['note'], i['tier']))
    def _tier_avail(t):
        miss = [i['name'] for i in r['items'] if i['tier'] == t and not i['ok']]
        return '%s: %s' % (t, '可用' if not miss else '缺 %d 项（%s）' % (len(miss), '、'.join(miss)))
    lines += ['', '**档位：%s**｜%s' % (r['tier'],
              ('缺件：' + '、'.join(r['missing'])) if r['missing'] else '无缺件'),
              '- 分档可用性：' + '｜'.join(_tier_avail(t) for t in ('T0', 'T1', 'T2')),
              '  （档位按 T0→T1→T2 连续判定：低档缺件把整体档位压到该档；高档项全绿不代表整体档位，见逐档可用性）']
    return '\n'.join(lines)


# ---------------------------------------------------------------- 自证

def selftest() -> int:
    ok = True
    system_root, major, src = resolve_roots()          # 自脚本位置走探测链
    euler = euler_root(major)
    r = run()                                          # 同一路径（run(None) 内部同款解析）
    by_name = {i['name']: i for i in r['items']}

    def say(cond: bool, label: str, detail: str) -> None:
        nonlocal ok
        ok &= bool(cond)
        print('[%s] %s：%s' % ('PASS' if cond else 'FAIL', label, detail))

    def find(key: str) -> dict:
        """按关键字取检查项（不锁死全名，改名不破自证）。"""
        for i in r['items']:
            if key in i['name']:
                return i
        return dict(name=key, ok=False, note='（未找到检查项：%s）' % key)

    say((euler / 'workflows').is_dir(), '根解析（Euler 根 workflows 在位）',
        '系统根=%s｜主根=%s｜来源=%s' % (system_root, major, src))
    core_item = find('核心求解栈 numpy/scipy')
    say(core_item['ok'], 'venv 或系统 Python 可用', core_item['note'])
    wf_item = find('workflows（00–10')
    say(wf_item['ok'], 'workflows 在位', wf_item['note'])
    print('SELFTEST', 'OK' if ok else 'FAILED', '｜档位=%s' % r['tier'])
    return 0 if ok else 1


def main(argv=None) -> int:
    try:                                            # 中文输出到非 UTF-8 控制台时不炸
        getattr(sys.stdout, 'reconfigure')(encoding='utf-8', errors='replace')
    except Exception:
        pass
    ap = argparse.ArgumentParser(description='Euler 环境自检（E-R 底座）')
    ap.add_argument('--root', help='包根或系统根（默认：环境变量 MODELFORGE_ROOT → 脚本位置向上探测链）')
    ap.add_argument('--json', action='store_true', help='输出 JSON（供门禁/脚本消费）')
    ap.add_argument('--selftest', action='store_true', help='自证：断言根解析 / 解释器栈 / workflows 在位')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    r = run(Path(a.root) if a.root else None)       # 显式 --root 优先；否则走探测链
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(render(r))
    return 0 if r['tier'] in ('T0', 'T1', 'T2') else 1


if __name__ == '__main__':
    sys.exit(main())
