"""
Unit tests for Spotify client.
"""
import pytest
from unittest.mock import Mock, patch
from src.spotify_client import SpotifyClient
from src.config import Config

@pytest.fixture
def mock_spotify_client():
    """Create a mock Spotify client."""
    with patch('src.spotify_client.spotipy.Spotify') as mock:
        client = SpotifyClient()
        client.client = mock
        return client

def test_client_initialization():
    """Test Spotify client initialization."""
    with patch('src.spotify_client.spotipy.Spotify'):
        client = SpotifyClient()
        assert client is not None
        assert client.rate_limit_delay == 0.1

def test_rate_limit(mock_spotify_client):
    """Test rate limiting functionality."""
    import time
    start = time.time()
    mock_spotify_client._rate_limit()
    end = time.time()
    # Should be at least the delay
    assert end - start >= mock_spotify_client.rate_limit_delay

def test_get_user_top_tracks(mock_spotify_client):
    """Test fetching user top tracks."""
    mock_response = {'items': [{'id': 'track1'}, {'id': 'track2'}]}
    mock_spotify_client.client.current_user_top_tracks.return_value = mock_response
    
    tracks = mock_spotify_client.get_user_top_tracks(limit=10)
    
    assert len(tracks) == 2
    mock_spotify_client.client.current_user_top_tracks.assert_called_with(
        limit=10, time_range='medium_term'
    )

def test_get_audio_features(mock_spotify_client):
    """Test fetching audio features."""
    mock_response = [{'danceability': 0.8, 'energy': 0.7}]
    mock_spotify_client.client.audio_features.return_value = mock_response
    
    features = mock_spotify_client.get_audio_features(['track1'])
    
    assert len(features) == 1
    assert features[0]['danceability'] == 0.8

def test_create_playlist(mock_spotify_client):
    """Test playlist creation."""
    mock_response = {'id': 'playlist123', 'external_urls': {'spotify': 'url'}}
    mock_spotify_client.client.user_playlist_create.return_value = mock_response
    
    playlist = mock_spotify_client.create_playlist(
        'user123', 'Test Playlist', 'Description'
    )
    
    assert playlist['id'] == 'playlist123'
    mock_spotify_client.client.user_playlist_create.assert_called_with(
        'user123', 'Test Playlist', public=False, description='Description'
    )

def test_error_handling(mock_spotify_client):
    """Test error handling for API calls."""
    import spotipy
    mock_spotify_client.client.current_user_top_tracks.side_effect = (
        spotipy.exceptions.SpotifyException(429, 'Rate limit', {})
    )
    
    # Should retry and eventually raise
    with pytest.raises(spotipy.exceptions.SpotifyException):
        mock_spotify_client.get_user_top_tracks()