"""图论：最短路（Dijkstra/Floyd）+ 最小生成树（Kruskal）模板。

适用场景：路径规划、网络连通（美赛 B/D、国赛 B）。
依赖：networkx。
"""
import networkx as nx


def shortest_path(edges, source, target=None, weighted=True):
    """edges: [(u, v, w), ...]。返回最短路径与距离。"""
    G = nx.Graph()
    if weighted:
        G.add_weighted_edges_from(edges)
    else:
        G.add_edges_from((u, v) for u, v, *_ in edges)
    if target is None:
        dist = dict(nx.single_source_dijkstra_path_length(G, source) if weighted
                    else nx.single_source_shortest_path_length(G, source))
        return dist
    path = nx.dijkstra_path(G, source, target) if weighted else nx.shortest_path(G, source, target)
    length = nx.dijkstra_path_length(G, source, target) if weighted else nx.shortest_path_length(G, source, target)
    return path, length


def mst(edges):
    """最小生成树。返回边列表 + 总权重。"""
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    T = nx.minimum_spanning_tree(G)
    total = sum(d["weight"] for _, _, d in T.edges(data=True))
    return list(T.edges(data=True)), total


if __name__ == "__main__":
    # 示例：城市间道路 (u, v, 距离)
    edges = [
        ("A", "B", 4), ("A", "C", 2), ("B", "C", 1), ("B", "D", 5),
        ("C", "D", 8), ("C", "E", 10), ("D", "E", 2), ("D", "F", 6), ("E", "F", 3),
    ]

    path, length = shortest_path(edges, "A", "F")
    print(f"[最短路 A→F] 路径: {' → '.join(path)}  距离: {length}")

    tree, total = mst(edges)
    print(f"\n[最小生成树] 总权重: {total}")
    for u, v, d in tree:
        print(f"  {u} - {v} (w={d['weight']})")
