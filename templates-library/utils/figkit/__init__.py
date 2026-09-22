# -*- coding: utf-8 -*-
"""figkit —— 数模论文图型样例库（可直接抄改的「图型 → 代码」对照集）。

定位
----
模板库解决「算法怎么写」，本库解决「图画成什么样」。每个 ``figkit_demo*.py``
都是**自包含**的单图样例：合成数据（固定 seed）→ 论文级风格 → 三格式导出
（PNG/PDF/SVG）到 ``figkit/_out/``。改数据区即可套到自己的题目上。

目录
----
    figkit_demo1_grouped_bar.py   对比柱状：两组并排 + 误差棒 + 显著性标注
    figkit_demo2_heatmap.py       热图：带 colorbar + 单元格数值标注
    figkit_demo3_network.py       网络图：节点/边纯 matplotlib 自绘（零额外依赖）
    figkit_demo4_multipanel.py    多面板 2×2：(a)(b)(c)(d) 标号
    figkit_demo5_schematic.py     机理示意图：纯 patch + arrow 拼装（无需绘图软件）
    gray_cb_check.py              黑白/色盲机检辅助（灰度预览 + 红绿色盲模拟 + 亮度差告警）

运行方式（两种都行）
----
    # ① 直跑（脚本自身会按位置补 sys.path）
    python utils/figkit/figkit_demo1_grouped_bar.py
    # ② 包内运行（走 ``from ..plot_style import ...`` 相对导入）
    python -m utils.figkit.figkit_demo1_grouped_bar

约定
----
- 图内文字**统一英文**（中文 Windows 字体缺字形风险高、且英文图可直接进美赛/SCI）。
  风格取 ``plot_style.style_plot("mcm")``（英文盒式）；要中文标签时改回 ``style_plot("cumcm")``。
- 只依赖 matplotlib + numpy（requirements.txt 既有），不引入新依赖。
- 固定 seed：同一份代码每次跑出的数值与图完全一致，便于论文复现声明。
"""
