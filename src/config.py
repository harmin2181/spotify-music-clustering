import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Spotify API Configuration
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')
    
    # Application Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_TRACKS = int(os.getenv('MAX_TRACKS', 100))
    DEFAULT_CLUSTERS = int(os.getenv('DEFAULT_CLUSTERS', 4))
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', './output'))
    
    # Cache Settings
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))
    
    # Audio Features
    AUDIO_FEATURES = [
        'danceability',
        'energy', 
        'acousticness',
        'valence',
        'tempo',
        'instrumentalness',
        'speechiness',
        'loudness',
        'liveness'
    ]
    
    # Feature Weights for Clustering
    FEATURE_WEIGHTS = {
        'danceability': 1.0,
        'energy': 1.0,
        'acousticness': 0.8,
        'valence': 0.9,
        'tempo': 0.7,
        'instrumentalness': 0.6,
        'speechiness': 0.5,
        'loudness': 0.4,
        'liveness': 0.3
    }
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        required = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET']
        missing = [r for r in required if not getattr(cls, r)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        return True

# Create output directory if it doesn't exist
Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)