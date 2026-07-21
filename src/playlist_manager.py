import logging
from typing import Dict, List
import pandas as pd
from src.spotify_client import SpotifyClient

logger = logging.getLogger(__name__)

class PlaylistManager:
    """Manages playlist creation and updates."""
    
    def __init__(self, client: SpotifyClient):
        self.client = client
        
    def create_cluster_playlists(self, df: pd.DataFrame, 
                                base_name: str = 'AI Music Cluster',
                                description_template: str = 'Cluster {cluster_id}: {size} songs with similar audio features',
                                public: bool = False) -> Dict[int, str]:
        """Create playlists for each cluster."""
        user_id = self.client.get_current_user_id()
        playlist_urls = {}
        
        for cluster_id in sorted(df['cluster_id'].unique()):
            cluster_songs = df[df['cluster_id'] == cluster_id]
            track_ids = cluster_songs['id'].tolist()
            
            # Create playlist
            name = f"{base_name} {cluster_id}"
            description = description_template.format(
                cluster_id=cluster_id,
                size=len(cluster_songs)
            )
            
            try:
                playlist = self.client.create_playlist(
                    user_id=user_id,
                    name=name,
                    description=description,
                    public=public
                )
                
                # Add tracks
                self.client.add_tracks_to_playlist(playlist['id'], track_ids)
                
                playlist_urls[cluster_id] = playlist['external_urls']['spotify']
                logger.info(f"Created playlist '{name}' with {len(track_ids)} tracks")
                
            except Exception as e:
                logger.error(f"Failed to create playlist for cluster {cluster_id}: {e}")
        
        return playlist_urls
    
    def update_existing_playlist(self, playlist_id: str, track_ids: List[str]):
        """Update an existing playlist with new tracks."""
        self.client.add_tracks_to_playlist(playlist_id, track_ids)
        logger.info(f"Updated playlist {playlist_id} with {len(track_ids)} tracks")
    
    def recommend_playlist_from_cluster(self, df: pd.DataFrame, 
                                      cluster_id: int,
                                      recommendation_limit: int = 10) -> List[Dict]:
        """Get recommendations based on a cluster."""
        # Get tracks from cluster
        cluster_tracks = df[df['cluster_id'] == cluster_id]
        if cluster_tracks.empty:
            raise ValueError(f"No tracks found in cluster {cluster_id}")
        
        # Use top 5 tracks as seeds
        seed_tracks = cluster_tracks.head(5)['id'].tolist()
        
        # Get recommendations
        recommendations = self.client.client.recommendations(
            seed_tracks=seed_tracks,
            limit=recommendation_limit
        )
        
        return recommendations['tracks']