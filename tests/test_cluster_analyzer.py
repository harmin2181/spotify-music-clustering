import pytest
import pandas as pd
import numpy as np
from src.cluster_analyzer import ClusterAnalyzer
from src.config import Config

@pytest.fixture
def sample_data():
    """Create sample music data for testing."""
    data = {
        'id': [f'track_{i}' for i in range(10)],
        'name': [f'Song {i}' for i in range(10)],
        'artist': ['Artist'] * 10,
    }
    
    # Add random features
    for feature in Config.AUDIO_FEATURES:
        data[feature] = np.random.rand(10)
    
    return pd.DataFrame(data)

def test_preprocess_features(sample_data):
    """Test feature preprocessing."""
    analyzer = ClusterAnalyzer()
    X = analyzer.preprocess_features(sample_data)
    
    assert isinstance(X, np.ndarray)
    assert X.shape == (10, len(Config.AUDIO_FEATURES))
    assert np.allclose(X.mean(axis=0), 0, atol=1e-10)

def test_cluster_songs(sample_data):
    """Test clustering functionality."""
    analyzer = ClusterAnalyzer(n_clusters=3)
    df_clustered, results = analyzer.cluster_songs(sample_data, n_clusters=3)
    
    assert 'cluster_id' in df_clustered.columns
    assert len(df_clustered['cluster_id'].unique()) == 3
    assert 'statistics' in results
    assert len(results['statistics']) == 3

def test_predict_cluster(sample_data):
    """Test cluster prediction."""
    analyzer = ClusterAnalyzer(n_clusters=2)
    df_clustered, _ = analyzer.cluster_songs(sample_data, n_clusters=2)
    
    # Get features for prediction
    features = {f: 0.5 for f in Config.AUDIO_FEATURES}
    predicted_cluster = analyzer.predict_cluster(features)
    
    assert predicted_cluster in [0, 1]