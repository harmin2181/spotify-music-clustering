#!/usr/bin/env python
"""
Batch analysis script for processing multiple playlists and generating reports.
"""
import sys
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
from tqdm import tqdm

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import Config
from src.spotify_client import SpotifyClient
from src.data_fetcher import DataFetcher
from src.cluster_analyzer import ClusterAnalyzer
from src.visualizer import Visualizer
from src.playlist_manager import PlaylistManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.OUTPUT_DIR / 'batch_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BatchAnalyzer:
    """Batch analysis of multiple playlists."""
    
    def __init__(self):
        self.client = SpotifyClient()
        self.fetcher = DataFetcher(self.client)
        self.analyzer = ClusterAnalyzer()
        self.visualizer = Visualizer()
        self.playlist_manager = PlaylistManager(self.client)
    
    def analyze_playlist_batch(self, playlist_ids: list, n_clusters: int = None):
        """Analyze multiple playlists and generate reports."""
        results = {}
        
        for playlist_id in tqdm(playlist_ids, desc="Processing playlists"):
            try:
                logger.info(f"Processing playlist: {playlist_id}")
                
                # Fetch playlist data
                df = self.fetcher.get_playlist_tracks(playlist_id)
                
                if df.empty:
                    logger.warning(f"No data found for playlist {playlist_id}")
                    continue
                
                # Perform clustering
                df_clustered, cluster_results = self.analyzer.cluster_songs(
                    df, n_clusters=n_clusters
                )
                
                # Generate visualizations
                vis_dir = Config.OUTPUT_DIR / f"playlist_{playlist_id}"
                vis_dir.mkdir(exist_ok=True)
                
                self.visualizer.plot_clusters_matplotlib(df_clustered, save=True)
                self.visualizer.plot_feature_radar(df_clustered, save=True)
                self.visualizer.plot_cluster_sizes(df_clustered, save=True)
                
                # Generate report
                report_path = self.visualizer.create_report(
                    df_clustered, cluster_results['statistics']
                )
                
                # Save results
                output_file = vis_dir / 'clustering_results.csv'
                df_clustered.to_csv(output_file, index=False)
                
                results[playlist_id] = {
                    'tracks': len(df),
                    'clusters': len(df_clustered['cluster_id'].unique()),
                    'report': str(report_path),
                    'data': df_clustered
                }
                
                logger.info(f"Completed analysis for playlist {playlist_id}")
                
            except Exception as e:
                logger.error(f"Error processing playlist {playlist_id}: {e}")
                results[playlist_id] = {'error': str(e)}
        
        return results
    
    def generate_summary_report(self, results):
        """Generate a summary report for all analyzed playlists."""
        summary_data = []
        
        for playlist_id, result in results.items():
            if 'error' in result:
                summary_data.append({
                    'playlist_id': playlist_id,
                    'status': 'Error',
                    'tracks': 0,
                    'clusters': 0,
                    'error': result['error']
                })
            else:
                summary_data.append({
                    'playlist_id': playlist_id,
                    'status': 'Success',
                    'tracks': result['tracks'],
                    'clusters': result['clusters'],
                    'report': result['report']
                })
        
        summary_df = pd.DataFrame(summary_data)
        summary_file = Config.OUTPUT_DIR / 'batch_summary.csv'
        summary_df.to_csv(summary_file, index=False)
        
        logger.info(f"Summary report saved to {summary_file}")
        return summary_df

def main():
    """Main entry point for batch analysis."""
    print("\n🎵 Spotify Batch Playlist Analysis")
    print("=" * 50)
    
    # Get playlist IDs
    playlist_input = input("Enter playlist URLs or IDs (comma-separated): ").strip()
    playlist_ids = [pid.strip() for pid in playlist_input.split(',') if pid.strip()]
    
    if not playlist_ids:
        print("❌ No playlist IDs provided.")
        return
    
    # Get number of clusters
    n_clusters = input("Number of clusters (default: auto-detect): ").strip()
    n_clusters = int(n_clusters) if n_clusters else None
    
    # Initialize analyzer
    analyzer = BatchAnalyzer()
    
    # Process playlists
    print(f"\n📊 Processing {len(playlist_ids)} playlists...")
    results = analyzer.analyze_playlist_batch(playlist_ids, n_clusters)
    
    # Generate summary
    summary = analyzer.generate_summary_report(results)
    
    print("\n✅ Batch analysis complete!")
    print(f"📁 Results saved to: {Config.OUTPUT_DIR}")
    print("\nSummary:")
    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()