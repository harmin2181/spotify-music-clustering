import logging
from typing import List, Dict, Optional
import pandas as pd
from tqdm import tqdm
from src.config import Config
from src.spotify_client import SpotifyClient

logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetches and processes music data from Spotify."""
    
    def __init__(self, client: Optional[SpotifyClient] = None):
        self.client = client or SpotifyClient()
        self.features = Config.AUDIO_FEATURES
        
    def fetch_tracks_data(self, tracks: List[Dict]) -> pd.DataFrame:
        """Fetch audio features and create dataframe from track list."""
        if not tracks:
            raise ValueError("No tracks provided")
        
        # Extract track information
        track_info = []
        track_ids = []
        
        for track in tracks:
            if track and track.get('id'):
                track_info.append({
                    'id': track['id'],
                    'name': track['name'],
                    'artist': track['artists'][0]['name'] if track.get('artists') else 'Unknown',
                    'album': track['album']['name'] if track.get('album') else 'Unknown',
                    'popularity': track.get('popularity', 0)
                })
                track_ids.append(track['id'])
        
        # Fetch audio features
        logger.info(f"Fetching audio features for {len(track_ids)} tracks...")
        audio_features = self.client.get_audio_features(track_ids)
        
        # Combine data
        data = []
        for info, features in zip(track_info, audio_features):
            if features:
                row = {**info}
                for feature in self.features:
                    row[feature] = features.get(feature, 0)
                data.append(row)
        
        df = pd.DataFrame(data)
        logger.info(f"Successfully fetched data for {len(df)} tracks")
        return df
    
    def get_top_tracks(self, limit: int = 50, time_range: str = 'medium_term') -> pd.DataFrame:
        """Fetch user's top tracks."""
        logger.info(f"Fetching top {limit} tracks ({time_range})...")
        tracks = self.client.get_user_top_tracks(limit=limit, time_range=time_range)
        return self.fetch_tracks_data(tracks)
    
    def get_playlist_tracks(self, playlist_id: str) -> pd.DataFrame:
        """Fetch all tracks from a playlist."""
        logger.info(f"Fetching tracks from playlist: {playlist_id}")
        tracks = self.client.get_playlist_tracks(playlist_id)
        return self.fetch_tracks_data(tracks)
    
    def get_multiple_playlists(self, playlist_ids: List[str]) -> pd.DataFrame:
        """Fetch and combine tracks from multiple playlists."""
        all_dfs = []
        for playlist_id in tqdm(playlist_ids, desc="Processing playlists"):
            try:
                df = self.get_playlist_tracks(playlist_id)
                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Error fetching playlist {playlist_id}: {e}")
        
        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)
        return pd.DataFrame()
    
    def save_data(self, df: pd.DataFrame, filename: str = 'spotify_data.csv'):
        """Save dataframe to CSV."""
        output_path = Config.OUTPUT_DIR / filename
        df.to_csv(output_path, index=False)
        logger.info(f"Data saved to {output_path}")