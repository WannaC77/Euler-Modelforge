"""元胞自动机模板（一维交通流/扩散 示例）。

适用场景：离散时空演化系统——交通流、疾病空间传播、森林火灾、博弈演化（美赛 B/E/F）。
示例：一维交通流（规则 184：车前进条件）与简单二维扩散。

规则 184（交通流）：cell=1 有车。t→t+1：车看前方是否空，空则前进，否则等待。
"""
import numpy as np


def traffic_rule184(road, steps=50, density=None, seed=42, road_len=100):
    """一维交通流仿真。road: 0/1 数组(1=有车)。返回演化历史 (steps+1 × len)。"""
    rng = np.random.default_rng(seed)
    if road is None:
        if density is None:
            density = 0.4
        road = (rng.random(road_len) < density).astype(int)
    history = [road.copy()]
    for _ in range(steps):
        nxt = np.zeros_like(road)
        L = len(road)
        # 环形道路：车前进当且仅当 前方为空
        for i in range(L):
            if road[i] == 1 and road[(i + 1) % L] == 0:
                nxt[(i + 1) % L] = 1
            elif road[i] == 1:
                nxt[i] = 1
        road = nxt
        history.append(road.copy())
    return np.array(history)


def avg_speed(history):
    """统计平均速度（每步移动的车占比）。"""
    speeds = []
    for t in range(history.shape[0] - 1):
        # 计算 t 时刻有车且 t+1 前进了的比例
        ahead_empty = np.roll(history[t], -1) == 0
        car_ahead_empty = (history[t] == 1) & ahead_empty
        speeds.append(car_ahead_empty.sum() / max(history[t].sum(), 1))
    return np.mean(speeds)


if __name__ == "__main__":
    # 密度扫描：密度越高平均车速越低（相变）
    print("[交通流] 密度 vs 平均速度（规则184, 环形道路100格, 100步）:")
    for density in [0.2, 0.4, 0.6, 0.8]:
        hist = traffic_rule184(None, steps=100, density=density, seed=42, road_len=100)
        v = avg_speed(hist)
        print(f"  密度 {density:.1f}: 平均速度 {v:.3f}")

    # 可视化一次演化
    hist = traffic_rule184(None, steps=60, density=0.4, seed=42, road_len=100)
    import matplotlib.pyplot as plt
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils.plot_style import style_plot, save_fig
    style_plot(font_size=10)
    fig, ax = plt.subplots()
    ax.imshow(hist, aspect="auto", cmap="Greys", interpolation="nearest")
    ax.set_xlabel("Position (cell)")
    ax.set_ylabel("Time step")
    ax.set_title("Traffic flow CA (Rule 184)")
    save_fig(fig, os.path.join(os.path.dirname(__file__), "..", "data", "cellular_automata.png"))
