# 示例（examples/）

三个最小示例，**全部合成数据**、真跑判据、可直接进 CI：

| 示例 | 演示 | 命令 |
|---|---|---|
| `solve_lp.py` | 调模板库求解线性规划合成题（判据：输出含 `[最优值]`） | `python examples/solve_lp.py` |
| `plot_results.py` | 调 figkit 样张 1（两组对比柱状图）出 PNG/SVG/PDF | `python examples/plot_results.py` |
| `mini_chain.py` | 全链 mini：题卡 → 求解 → 出图 → 薄报告（`examples/_out/mini_report.md`） | `python examples/mini_chain.py` |

## 运行前的依赖

- pip 安装：`pip install euler-modelforge[all]`
- 源码：`pip install -r templates-library/requirements.txt`

缺依赖时示例按仓库契约以 `rc=3` 退出并给出补装提示（诚实降级，不假装通过）。

## 安装态如何跑

同一份示例随包分发在 `euler_modelforge/_tree/examples/`，直接对该目录里的同名脚本运行即可：

```bash
python <site-packages>/euler_modelforge/_tree/examples/solve_lp.py
```
