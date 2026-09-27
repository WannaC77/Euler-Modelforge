# examples —— 可运行示例（Euler-Modelforge）

本目录是「5 分钟上手」的最小可跑示例，全部使用**合成数据**，不含任何真实素材。

| 示例 | 演示 | 依赖 |
|---|---|---|
| `solve_lp.py` | 调模板库求解线性规划合成题（判据：输出含 `[最优值]`） | `pip install euler-modelforge[all]`（或仓库内 `pip install -r templates-library/requirements.txt`） |
| `plot_results.py` | 调 figkit 样张 1（两组对比柱状图）出 PNG/SVG/PDF | 同上（需 matplotlib / scipy） |
| `mini_chain.py` | 全链 mini：题卡 → 求解 → 出图 → 薄报告 `_out/mini_report.md` | 同上 |

## 运行

```bash
# ① 仓库内（推荐先在仓库根装好依赖）
python examples/solve_lp.py
python examples/plot_results.py
python examples/mini_chain.py

# ② pip 安装后：同一份示例随包在 euler_modelforge/_tree/examples/，
#    直接对该目录里的同名脚本运行即可（python <path>/solve_lp.py）。
```

## 退出码约定

`0` 通过 · `1` 失败 · `2` 用法错误 · `3` 依赖缺失未执行（未执行 ≠ 通过）。
缺依赖时示例会打印补装提示并按 `3` 退出。
