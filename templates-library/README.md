# 数模代码仓（Python 模板库）

> 位置：`templates-library/`
> 状态：**35 个模板在盘：全量验收 34/34 PASS（2026-09-04）＋ `grey_relation.py` 补测 PASS（2026-09-21）**
> 比赛用法：先查 `MODEL_GUIDE.md`（题型→选模板），改参数即跑。
> 环境：`<venv>` 已建好（venv python 运行），依赖见 `requirements.txt`。

## 8 大类 × 35 个模板

| 目录 | 模板 | 覆盖场景 |
|------|------|---------|
| `01-优化/` (6) | `lp.py` `transportation.py` `assignment.py` `dp_knapsack.py` `nlp.py` `multiobjective.py` | 线性/整数规划、运输、指派(匈牙利)、0-1背包DP、非线性规划、多目标Pareto |
| `02-预测/` (5) | `grey_gm11.py` `arima.py` `exp_smoothing.py` `linear_regression.py` `markov_chain.py` | 灰色GM(1,1)、ARIMA、Holt-Winters季节、多元回归(显著性)、马尔可夫 |
| `03-评价/` (5) | `ahp.py` `topsis_entropy.py` `fuzzy_eval.py` `dea.py` `grey_relation.py` | 层次分析、TOPSIS+熵权、模糊综合评价、DEA效率、灰色关联 |
| `04-统计与机器学习/` (4) | `data_preprocess.py` `hypothesis_tests.py` `supervised_ml.py` `kmeans_pca.py` | 预处理、假设检验套件、监督学习(RF/LR)、KMeans+PCA |
| `05-微分方程/` (4) | `sir.py` `seir.py` `ode_general.py` `logistic_growth.py` | SIR、SEIRD、通用ODE(LV)、Logistic拟合 |
| `06-图论/` (4) | `shortest_path_mst.py` `max_flow.py` `critical_path.py` `network_metrics.py` | 最短路+MST、最大流/最小割、CPM关键路径、网络中心性/社区 |
| `07-仿真/` (3) | `monte_carlo.py` `queue_mmc.py` `cellular_automata.py` | 蒙特卡洛、M/M/c排队、元胞自动机(交通流) |
| `08-智能算法/` (4) | `ga.py` `pso.py` `sa.py` `aco_tsp.py` | 遗传、粒子群、模拟退火、蚁群TSP |

## 工具库 utils/

| 文件 | 用途 |
|------|------|
| `plot_style.py` | 论文级图表风格（`style_plot()` + `save_fig()` + `add_units()`） |
| `latex_table.py` | 数据 → LaTeX 表格（直接贴进论文） |
| `sensitivity.py` | **通用敏感性分析**（`scan_1d`/`scan_2d`/`scan_report`）——论文"敏感性分析"章节一键产出 |
| `figcheck.py` | 图件文件层机检（打开性/宽度/DPI/内容占比；配 `plot_style.audit_fig` 与 vision 复核） |

## 使用方式

```bash
# 运行任意模板（自带示例数据，改文件头参数区即换数据）
"<venv>/Scripts/python.exe" "01-优化/lp.py"

# 在代码里调用工具库（模板同目录运行时自动注入路径，参照现有模板）
from utils.plot_style import style_plot, save_fig
from utils.sensitivity import scan_1d, scan_report
```

一键冒烟：`python smoke_all.py`（35 模板全量跑 → `_smoke_out/smoke_all_report.md` 全 PASS 表；`--quick` 每类首件；`--selftest` 三件快检）。

每个模板文件结构统一：头部 docstring（适用场景/输入输出/依赖）→ 参数常量区（改这里换数据）→ 函数化实现（中文注释）→ `__main__` 自带示例 → 输出可判读数值。随机算法固定 seed 可复现。

## 参考来源

获奖队伍代码（美赛 O/F 奖 GitHub 仓库：Nahuyiur/2025-MCM-ICM-Problem-C、ydchen0806/24ICM_E_O_Award_Paper_code 等）+ 标准教材实现 + 自研封装。
