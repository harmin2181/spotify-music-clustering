#!/usr/bin/env python
"""
Main script to run the Spotify clustering application.
"""
import sys
import logging
from pathlib import Path

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
        logging.FileHandler(Config.OUTPUT_DIR / 'app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point."""
    try:
        # Initialize components
        client = SpotifyClient()
        fetcher = DataFetcher(client)
        analyzer = ClusterAnalyzer()
        visualizer = Visualizer()
        playlist_manager = PlaylistManager(client)
        
        print("\n🎵 Spotify Music Clustering")
        print("=" * 40)
        
        # Get input mode
        mode = input("Mode (top/playlist/batch): ").strip().lower()
        if mode not in ['top', 'playlist', 'batch']:
            print("Invalid mode. Use 'top', 'playlist', or 'batch'")
            return
        
        # Fetch data
        if mode == 'top':
            limit = int(input("Number of top tracks (default 50): ") or "50")
            time_range = input("Time range (short_term/medium_term/long_term): ") or "medium_term"
            df = fetcher.get_top_tracks(limit=limit, time_range=time_range)
        
        elif mode == 'playlist':
            playlist_id = input("Enter playlist URL or ID: ").strip()
            df = fetcher.get_playlist_tracks(playlist_id)
        
        else:  # batch
            playlist_ids = input("Enter playlist IDs (comma-separated): ").strip().split(',')
            df = fetcher.get_multiple_playlists(playlist_ids)
        
        if df.empty:
            print("No data fetched. Please check your inputs.")
            return
        
        print(f"\n✅ Fetched {len(df)} tracks")
        
        # Find optimal clusters
        print("\n🔍 Finding optimal number of clusters...")
        X = analyzer.preprocess_features(df)
        optimal_k, metrics = analyzer.find_optimal_clusters(X)
        print(f"Optimal clusters: {optimal_k}")
        
        # Perform clustering
        print(f"\n📊 Performing clustering with {optimal_k} clusters...")
        df_clustered, results = analyzer.cluster_songs(df, n_clusters=optimal_k)
        
        # Display cluster statistics
        print("\n📈 Cluster Statistics:")
        for cluster_id, stats in results['statistics'].items():
            print(f"Cluster {cluster_id}: {stats['size']} songs")
        
        # Show feature means
        print("\n🎵 Feature Means by Cluster:")
        print(df_clustered.groupby('cluster_id')[Config.AUDIO_FEATURES].mean().round(3))
        
        # Create visualizations
        print("\n🎨 Generating visualizations...")
        visualizer.plot_elbow(metrics['inertias'])
        visualizer.plot_clusters_matplotlib(df_clustered)
        visualizer.plot_clusters_plotly(df_clustered)
        visualizer.plot_feature_radar(df_clustered)
        visualizer.plot_cluster_sizes(df_clustered)
        
        # Create report
        visualizer.create_report(df_clustered, results['statistics'])
        
        # Create playlists
        create_playlists = input("\nCreate Spotify playlists? (y/n): ").strip().lower()
        if create_playlists == 'y':
            base_name = input("Playlist base name (default: 'AI Music Cluster'): ") or "AI Music Cluster"
            playlist_urls = playlist_manager.create_cluster_playlists(df_clustered, base_name)
            print("\n✅ Playlists created:")
            for cluster_id, url in playlist_urls.items():
                print(f"Cluster {cluster_id}: {url}")
        
        # Save results
        output_file = Config.OUTPUT_DIR / 'clustering_results.csv'
        df_clustered.to_csv(output_file, index=False)
        print(f"\n💾 Results saved to {output_file}")
        
        print("\n✨ Analysis complete! Check the 'output' directory for visualizations and report.")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()