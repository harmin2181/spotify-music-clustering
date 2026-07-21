import logging
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

logger = logging.getLogger(__name__)

class ClusterAnalyzer:
    def __init__(self, n_clusters=4):
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = None
        self.pca = None
    
    def preprocess_features(self, df):
        features = ['danceability', 'energy', 'acousticness', 'valence', 'tempo', 'instrumentalness']
        X = df[features].fillna(0)
        return self.scaler.fit_transform(X)
    
    def find_optimal_clusters(self, X, max_k=10):
        inertias = []
        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X)
            inertias.append(kmeans.inertia_)
        return 4, {'inertias': inertias}
    
    def cluster_songs(self, df, n_clusters=None):
        X = self.preprocess_features(df)
        if n_clusters is None:
            n_clusters = self.n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = self.kmeans.fit_predict(X)
        df_clustered = df.copy()
        df_clustered['cluster_id'] = labels
        self.pca = PCA(n_components=2, random_state=42)
        pca_result = self.pca.fit_transform(X)
        df_clustered['PC1'] = pca_result[:, 0]
        df_clustered['PC2'] = pca_result[:, 1]
        stats = {}
        for c in df_clustered['cluster_id'].unique():
            stats[c] = {'size': len(df_clustered[df_clustered['cluster_id'] == c])}
        return df_clustered, {'statistics': stats}