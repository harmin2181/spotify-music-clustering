"""
Simple test script to verify imports work.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing imports...")

try:
    from config import Config
    print("✅ Config imported")
except Exception as e:
    print(f"❌ Config failed: {e}")

try:
    from spotify_client import SpotifyClient
    print("✅ SpotifyClient imported")
except Exception as e:
    print(f"❌ SpotifyClient failed: {e}")

try:
    from cluster_analyzer import ClusterAnalyzer
    print("✅ ClusterAnalyzer imported")
except Exception as e:
    print(f"❌ ClusterAnalyzer failed: {e}")

try:
    from visualizer import Visualizer
    print("✅ Visualizer imported")
except Exception as e:
    print(f"❌ Visualizer failed: {e}")

try:
    from playlist_manager import PlaylistManager
    print("✅ PlaylistManager imported")
except Exception as e:
    print(f"❌ PlaylistManager failed: {e}")

print("\nAll imports tested!")