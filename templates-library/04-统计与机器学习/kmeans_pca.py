"""KMeans 聚类 + PCA 降维可视化模板。

适用场景：无标签样本分类（国赛 C、美赛 C/E 数据题常见）；先 PCA 看结构、再聚类。
依赖：scikit-learn。
"""
import numpy as np


def kmeans_pca(X, n_clusters=3, n_components=2, seed=42):
    """X: (n 样本 × m 特征)。返回 (labels, 聚类中心, PCA后的坐标)。"""
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA

    km = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10).fit(X)
    pca = PCA(n_components=n_components).fit(X)
    X_pca = pca.transform(X)
    return km.labels_, km.cluster_centers_, X_pca, pca.explained_variance_ratio_


if __name__ == "__main__":
    from sklearn.datasets import make_blobs
    # 示例：3 类二维数据（换成你的数据即可）
    X, _ = make_blobs(n_samples=300, centers=3, n_features=6, random_state=42)

    labels, centers, X_pca, var_ratio = kmeans_pca(X, n_clusters=3)
    print(f"[聚类] 各类样本数: {np.bincount(labels)}")
    print(f"[PCA] 前两主成分方差解释率: {np.round(var_ratio[:2], 4)}")

    import matplotlib.pyplot as plt
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils.plot_style import style_plot, save_fig
    style_plot()
    fig, ax = plt.subplots()
    for k in range(labels.max() + 1):
        ax.scatter(X_pca[labels == k, 0], X_pca[labels == k, 1], s=15, label=f"Cluster {k+1}")
    ax.set_xlabel("PC1"); ax.set_ylabel("PC2"); ax.legend()
    save_fig(fig, os.path.join(os.path.dirname(__file__), "..", "data", "kmeans.png"))
