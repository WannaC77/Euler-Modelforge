"""最大流模板（networkx 实现，含最小割）。

适用场景：网络容量分配、最大输送量、物流/电力/通信网络瓶颈分析（美赛 B/D、国赛 B）。
流程：建图 → max_flow 求最大流 → 顺带得最小割。
"""
# ── 依赖护栏（缺依赖 → rc=3「未执行 ≠ 通过」；见 CONTRIBUTING §硬性要求 4）──
for _dep in ("networkx",):
    try:
        __import__(_dep)
    except ImportError:
        print("[未执行] 缺少依赖 %s：pip install -r templates-library/requirements.txt（rc=3 = 依赖缺失未执行）" % _dep)
        raise SystemExit(3)
import networkx as nx


def max_flow(edges, source, sink):
    """edges: [(u, v, capacity), ...]。返回 (最大流量, 各边流量 dict)。"""
    G = nx.DiGraph()
    for u, v, c in edges:
        G.add_edge(u, v, capacity=c)
    flow_value, flow_dict = nx.maximum_flow(G, source, sink)
    return flow_value, flow_dict


def min_cut(edges, source, sink):
    """最小割：把网络分成两部分的最少容量割集。返回 (割容量, 割边)。"""
    G = nx.DiGraph()
    for u, v, c in edges:
        G.add_edge(u, v, capacity=c)
    cut_value, partition = nx.minimum_cut(G, source, sink)
    reachable, non_reachable = partition
    cut_edges = [(u, v) for u in reachable for v in non_reachable if G.has_edge(u, v)]
    return cut_value, cut_edges


if __name__ == "__main__":
    # 示例：输油管网 S→T（u, v, 容量）
    edges = [
        ("S", "A", 10), ("S", "B", 5), ("S", "C", 15),
        ("A", "B", 4), ("A", "D", 9), ("A", "E", 15),
        ("B", "C", 4), ("B", "E", 8),
        ("C", "F", 16),
        ("D", "E", 15), ("D", "T", 10),
        ("E", "F", 15), ("E", "T", 10),
        ("F", "T", 10),
    ]
    value, flow = max_flow(edges, "S", "T")
    print(f"[最大流 S→T] {value}")

    cv, ce = min_cut(edges, "S", "T")
    print(f"[最小割] 容量 {cv}")
    print(f"  割边: {[f'{u}-{v}' for u, v in ce]}")

    # 瓶颈边报告：满载的边（流量=容量）是系统瓶颈
    print("[满载边(流量=容量, 瓶颈候选)]")
    for u, d in flow.items():
        for v, f in d.items():
            cap = next(c for a, b, c in edges if a == u and b == v)
            if f >= cap and cap > 0:
                print(f"  {u}→{v}: {f}/{cap}")
