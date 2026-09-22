"""复杂网络指标模板（度分布/中心性/社区/小世界）。

适用场景：社交网络、交通网络、关系网络分析（美赛 B/D/E/F 网络类题）。
输出：网络基础指标 + 各节点中心性 + 社区划分 + 图。
"""
import networkx as nx


def network_report(edges, source=None):
    """edges: [(u, v)]（无权）或 [(u, v, w)]（有权）。返回指标 dict。"""
    G = nx.Graph()
    try:
        G.add_weighted_edges_from(edges)
    except Exception:
        G.add_edges_from((u, v) for u, v, *_ in edges)

    report = {
        "节点数": G.number_of_nodes(),
        "边数": G.number_of_edges(),
        "平均度": sum(d for _, d in G.degree()) / G.number_of_nodes(),
        "连通分量数": nx.number_connected_components(G),
        "平均聚类系数": nx.average_clustering(G),
        "图直径": nx.diameter(G) if nx.is_connected(G) else None,
        "度中心性": nx.degree_centrality(G),
        "介数中心性": nx.betweenness_centrality(G),
        "接近中心性": nx.closeness_centrality(G),
    }
    # 社区检测（Louvain 近似：greedy modularity）
    communities = list(nx.community.greedy_modularity_communities(G))
    report["社区数"] = len(communities)
    report["模块度"] = nx.community.modularity(G, communities)
    report["社区划分"] = [sorted(c) for c in communities]
    return report


if __name__ == "__main__":
    # 示例：小社交网络
    edges = [
        ("A", "B"), ("A", "C"), ("A", "D"), ("B", "C"), ("B", "D"),
        ("C", "D"), ("D", "E"), ("E", "F"), ("E", "G"), ("F", "G"),
        ("G", "H"), ("H", "I"), ("H", "J"), ("I", "J"),
    ]
    r = network_report(edges)
    print(f"[基础] 节点 {r['节点数']} / 边 {r['边数']} / 平均度 {r['平均度']:.2f} / "
          f"连通分量 {r['连通分量数']} / 聚类系数 {r['平均聚类系数']:.3f}")
    print(f"[社区] 数 {r['社区数']} / 模块度 {r['模块度']:.3f}")
    for i, c in enumerate(r["社区划分"]):
        print(f"  社区{i+1}: {c}")

    print("\n[中心性 top3]")
    for name in ["度中心性", "介数中心性", "接近中心性"]:
        top = sorted(r[name].items(), key=lambda kv: -kv[1])[:3]
        print(f"  {name}: " + ", ".join(f"{k}({v:.3f})" for k, v in top))

    import matplotlib.pyplot as plt
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils.plot_style import style_plot, save_fig
    style_plot()
    G = nx.Graph()
    G.add_edges_from(edges)
    fig, ax = plt.subplots(figsize=(7, 5))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx(G, pos, ax=ax, with_labels=True, node_color="#1f77b4",
                     node_size=400, font_color="white")
    ax.set_title("Network Visualization")
    save_fig(fig, os.path.join(os.path.dirname(__file__), "..", "data", "network.png"))
