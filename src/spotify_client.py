import time
import logging
from typing import Optional, Dict, List
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from src.config import Config

logger = logging.getLogger(__name__)

class SpotifyClient:
    """Wrapper class for Spotify API client with rate limiting and error handling."""
    
    def __init__(self):
        """Initialize Spotify client with credentials from config."""
        Config.validate()
        
        self.client = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=Config.SPOTIFY_CLIENT_ID,
                client_secret=Config.SPOTIFY_CLIENT_SECRET,
                redirect_uri=Config.SPOTIFY_REDIRECT_URI,
                scope='user-top-read playlist-modify-private playlist-read-private'
            )
        )
        self.rate_limit_delay = 0.1  # Seconds between requests
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Apply rate limiting to API calls."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, func, *args, **kwargs):
        """Make API request with error handling and retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                return func(*args, **kwargs)
            except spotipy.exceptions.SpotifyException as e:
                if e.http_status == 429:  # Rate limit
                    retry_after = int(e.headers.get('Retry-After', 5))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                elif e.http_status in [401, 403]:  # Auth errors
                    logger.error(f"Authentication error: {e}")
                    raise
                else:
                    logger.error(f"Spotify API error: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def get_user_top_tracks(self, limit: int = 50, time_range: str = 'medium_term') -> List[Dict]:
        """Get user's top tracks."""
        response = self._make_request(
            self.client.current_user_top_tracks,
            limit=limit,
            time_range=time_range
        )
        return response['items']
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Get all tracks from a playlist."""
        tracks = []
        offset = 0
        limit = 100
        
        while True:
            response = self._make_request(
                self.client.playlist_tracks,
                playlist_id,
                offset=offset,
                limit=limit
            )
            
            items = response['items']
            if not items:
                break
                
            tracks.extend([item['track'] for item in items if item.get('track')])
            offset += limit
            
            if len(items) < limit:
                break
                
        return tracks
    
    def get_audio_features(self, track_ids: List[str]) -> List[Dict]:
        """Get audio features for tracks."""
        features = []
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i+100]
            response = self._make_request(
                self.client.audio_features,
                batch
            )
            features.extend(response)
        return features
    
    def create_playlist(self, user_id: str, name: str, description: str = '', public: bool = False) -> Dict:
        """Create a new playlist."""
        return self._make_request(
            self.client.user_playlist_create,
            user_id,
            name,
            public=public,
            description=description
        )
    
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> Dict:
        """Add tracks to a playlist."""
        # Spotify limits to 100 tracks per request
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i+100]
            self._make_request(
                self.client.playlist_add_items,
                playlist_id,
                batch
            )
        return {'success': True}
    
    def get_current_user_id(self) -> str:
        """Get current user's ID."""
        user_info = self._make_request(self.client.current_user)
        return user_info['id']