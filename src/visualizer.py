import logging
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, List
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from src.config import Config

logger = logging.getLogger(__name__)

class Visualizer:
    """Handles visualization of clustering results."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def plot_elbow(self, inertias: List[float], save: bool = True) -> plt.Figure:
        """Plot elbow curve for K-means."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        k_values = range(2, len(inertias) + 2)
        ax.plot(k_values, inertias, 'bo-', linewidth=2, markersize=8)
        ax.set_xlabel('Number of Clusters (K)', fontsize=12)
        ax.set_ylabel('Inertia', fontsize=12)
        ax.set_title('Elbow Method for Optimal K', fontsize=14)
        ax.grid(True, alpha=0.3)
        
        # Highlight the elbow point
        if len(inertias) > 2:
            deltas = np.diff(inertias)
            elbow_k = np.argmin(deltas) + 2
            ax.axvline(x=elbow_k, color='red', linestyle='--', alpha=0.5,
                      label=f'Elbow at K={elbow_k}')
            ax.legend()
        
        if save:
            plt.savefig(self.output_dir / 'elbow_plot.png', dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_clusters_matplotlib(self, df: pd.DataFrame, 
                                show_labels: bool = True,
                                save: bool = True) -> plt.Figure:
        """Create cluster visualization using matplotlib."""
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Get unique clusters
        clusters = df['cluster_id'].unique()
        colors = sns.color_palette("husl", n_colors=len(clusters))
        
        # Plot each cluster
        for i, cluster_id in enumerate(sorted(clusters)):
            cluster_data = df[df['cluster_id'] == cluster_id]
            ax.scatter(cluster_data['PC1'], cluster_data['PC2'],
                      color=colors[i], label=f'Cluster {cluster_id}',
                      alpha=0.7, s=100)
            
            # Add labels for each point
            if show_labels and len(cluster_data) < 50:
                for _, row in cluster_data.iterrows():
                    ax.annotate(row['name'][:20], 
                               (row['PC1'], row['PC2']),
                               fontsize=8, alpha=0.6)
        
        ax.set_xlabel('Principal Component 1', fontsize=12)
        ax.set_ylabel('Principal Component 2', fontsize=12)
        ax.set_title('Song Clusters Visualization (PCA)', fontsize=14)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        if save:
            plt.savefig(self.output_dir / 'cluster_plot_matplotlib.png',
                       dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_clusters_plotly(self, df: pd.DataFrame, 
                            hover_data: Optional[List[str]] = None) -> go.Figure:
        """Create interactive cluster visualization using Plotly."""
        hover_data = hover_data or ['name', 'artist', 'popularity']
        
        fig = px.scatter(df, x='PC1', y='PC2', color='cluster_id',
                        hover_data=hover_data,
                        title='Interactive Song Clusters',
                        labels={'cluster_id': 'Cluster'},
                        color_continuous_scale='viridis')
        
        fig.update_traces(marker=dict(size=10, opacity=0.7))
        fig.update_layout(
            width=1000,
            height=700,
            showlegend=True,
            hoverlabel=dict(bgcolor="white", font_size=12)
        )
        
        # Save as HTML
        fig.write_html(self.output_dir / 'cluster_plot_interactive.html')
        
        return fig
    
    def plot_feature_radar(self, df: pd.DataFrame, 
                          save: bool = True) -> plt.Figure:
        """Create radar chart for cluster feature comparison."""
        feature_cols = Config.AUDIO_FEATURES
        cluster_means = df.groupby('cluster_id')[feature_cols].mean()
        
        # Normalize features for radar chart
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        normalized = scaler.fit_transform(cluster_means.T)
        normalized_df = pd.DataFrame(normalized.T, columns=cluster_means.index,
                                    index=feature_cols)
        
        # Create radar chart
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))
        
        angles = np.linspace(0, 2 * np.pi, len(feature_cols), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        
        for cluster in normalized_df.columns:
            values = normalized_df[cluster].values
            values = np.concatenate((values, [values[0]]))
            ax.plot(angles, values, 'o-', linewidth=2, label=f'Cluster {cluster}')
            ax.fill(angles, values, alpha=0.1)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(feature_cols, fontsize=10)
        ax.set_title('Feature Comparison Across Clusters', fontsize=14, pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        if save:
            plt.savefig(self.output_dir / 'feature_radar.png',
                       dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_cluster_sizes(self, df: pd.DataFrame, save: bool = True) -> plt.Figure:
        """Create bar chart of cluster sizes."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sizes = df['cluster_id'].value_counts().sort_index()
        colors = sns.color_palette("husl", n_colors=len(sizes))
        
        bars = ax.bar(sizes.index, sizes.values, color=colors, alpha=0.7)
        ax.set_xlabel('Cluster', fontsize=12)
        ax.set_ylabel('Number of Songs', fontsize=12)
        ax.set_title('Cluster Sizes', fontsize=14)
        
        # Add value labels on bars
        for bar, value in zip(bars, sizes.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                   str(value), ha='center', va='bottom')
        
        if save:
            plt.savefig(self.output_dir / 'cluster_sizes.png', dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_report(self, df: pd.DataFrame, cluster_stats: Dict):
        """Generate comprehensive HTML report."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Spotify Clustering Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #1DB954; color: white; padding: 20px; }}
                .section {{ margin: 30px 0; }}
                .cluster {{ background: #f4f4f4; padding: 15px; margin: 10px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #1DB954; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎵 Spotify Music Clustering Report</h1>
                <p>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Total Songs Analyzed: {len(df)}</p>
                <p>Number of Clusters: {len(cluster_stats)}</p>
            </div>
        """
        
        # Add cluster statistics
        html_content += '<div class="section"><h2>Cluster Statistics</h2>'
        for cluster_id, stats in cluster_stats.items():
            html_content += f"""
            <div class="cluster">
                <h3>Cluster {cluster_id} ({stats['size']} songs)</h3>
                <h4>Average Features:</h4>
                <table>
                    <tr>
                        <th>Feature</th>
                        <th>Mean</th>
                        <th>Std</th>
                    </tr>
            """
            for feature, mean in stats['mean_features'].items():
                std = stats['std_features'].get(feature, 0)
                html_content += f"""
                    <tr>
                        <td>{feature}</td>
                        <td>{mean:.3f}</td>
                        <td>{std:.3f}</td>
                    </tr>
                """
            html_content += '</table>'
            
            # Show top songs
            songs = stats['songs'][:5]
            html_content += '<h4>Top Songs:</h4><ul>'
            for song in songs:
                html_content += f"<li>{song['name']} - {song['artist']} (Popularity: {song['popularity']})</li>"
            html_content += '</ul></div>'
        
        html_content += '</div>'
        
        # Add conclusion
        html_content += """
        <div class="section">
            <h2>Summary</h2>
            <p>Analysis complete! Your songs have been grouped into {len(cluster_stats)} clusters based on audio features.</p>
            <p>Check the visualizations in the output directory for more insights.</p>
        </div>
        </body>
        </html>
        """
        
        # Save report
        report_path = self.output_dir / 'clustering_report.html'
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Report saved to {report_path}")
        return report_path