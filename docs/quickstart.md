# 5 分钟上手

## 1. 安装（三种方式任选）

**pip（推荐）**

```bash
pip install euler-modelforge[all]   # [all] = 模板库全套依赖（numpy/scipy/matplotlib/pulp/…）
```

**pip（最小）**

```bash
pip install euler-modelforge        # 只装命令入口；跑模板缺依赖时按契约 rc=3 诚实退出
```

**源码**

```bash
git clone https://github.com/WannaC77/Euler-Modelforge
cd Euler-Modelforge
python -m venv .venv
# 下文用 <venv> 指代虚拟环境目录（本仓示例目录名 .venv）
<venv>/Scripts/python -m pip install -r templates-library/requirements.txt   # Windows
<venv>/bin/python     -m pip install -r templates-library/requirements.txt   # Linux/macOS
```

## 2. 第一条命令：看环境档位

```bash
euler-env-check
```

输出本机档位：**T0**（全套可用）· **T1**（部分降级）· **T2**（裸环境）。缺什么、降级走什么路径，都会列清楚。

## 3. 跑一次端到端冒烟

```bash
euler-smoke-chain --selftest      # 全链冒烟 + 黄金数值断言（含一次最小 LaTeX 编译）
```

看到 `判定：PASS` 说明：环境、模板库、求解器、图件、论文装配线在这台机器上全部可用。

## 4. 跑示例

```bash
python examples/solve_lp.py
```

## 退出码约定（全仓统一）

| 码 | 含义 |
|---|---|
| 0 | 通过 |
| 1 | 失败 |
| 2 | 用法 / 输入错误 |
| 3 | **依赖缺失未执行**（未执行 ≠ 通过） |

## 自定义根路径（进阶）

安装态默认使用随包数据；要指向自己的工作树时设 `MODELFORGE_ROOT=<树根>`。
