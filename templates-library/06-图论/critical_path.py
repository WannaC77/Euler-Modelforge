"""关键路径法 CPM 模板（项目管理/工期优化）。

适用场景：工程排程、任务调度——求项目最短工期、关键路径、各活动时差（美赛 B/D、国赛 B）。
流程：活动网络（前驱关系+工期）→ 正推最早时间 → 逆推最晚时间 → 总时差=0 的活动构成关键路径。
"""
from collections import defaultdict


def critical_path(activities):
    """activities: dict {活动名: (工期, [前驱活动列表])}。
    返回 (最短工期, 关键路径活动列表, 各活动时差 dict)。"""
    # 拓扑排序（活动只依赖前驱，按前驱迭代推进）
    duration = {a: d for a, (d, _) in activities.items()}
    preds = {a: p for a, (_, p) in activities.items()}
    succs = defaultdict(list)
    for a, (_, p) in activities.items():
        for pr in p:
            succs[pr].append(a)

    # 正推：最早开始 ES / 最早完成 EF
    ES, EF = {}, {}
    done = set()
    # 反复处理：前驱都算完的活动
    remaining = set(activities)
    while remaining:
        progressed = False
        for a in list(remaining):
            if all(pr in done for pr in preds[a]):
                es = max((EF[pr] for pr in preds[a]), default=0)
                ES[a] = es
                EF[a] = es + duration[a]
                done.add(a)
                remaining.remove(a)
                progressed = True
        if not progressed:  # 有环，报错
            raise ValueError(f"活动网络存在环或非法依赖: {remaining}")

    project_end = max(EF.values())
    # 终点的最晚完成 = 项目工期；逆推最晚完成 LF / 最晚开始 LS
    LF = {a: project_end for a in activities if not succs[a]}
    LS = {}
    for a in sorted(activities, key=lambda x: -EF[x]):
        lf = min((LS[s] for s in succs[a]), default=project_end)
        LF[a] = lf
        LS[a] = lf - duration[a]

    # 时差 = 最晚开始 - 最早开始（0 = 关键活动）
    slack = {a: LS[a] - ES[a] for a in activities}
    crit = sorted([a for a in activities if slack[a] < 1e-9])
    return project_end, crit, slack


if __name__ == "__main__":
    # 示例：工程项目（活动, (工期, 前驱)）
    activities = {
        "A": (3, []),      # 地基
        "B": (2, ["A"]),   # 结构
        "C": (4, ["A"]),   # 管线
        "D": (3, ["B"]),   # 内部装修
        "E": (2, ["B", "C"]),  # 设备安装
        "F": (2, ["D", "E"]),  # 收尾
    }
    end, crit, slack = critical_path(activities)
    print(f"[最短工期] {end} 天")
    print(f"[关键路径] {' → '.join(crit)}")
    print("\n[各活动时差]")
    for a, s in slack.items():
        mark = " ★关键" if s < 1e-9 else ""
        print(f"  {a}: 时差 {s:.0f}{mark}")

    # 若工期紧，压缩关键路径上成本最低的活动（提示）
    print("\n[压缩提示] 缩短工期只能压缩关键路径上的活动。")
