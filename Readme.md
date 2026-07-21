# 🎵 Spotify Music Clustering - AI Playlist Generator

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Spotify API](https://img.shields.io/badge/Spotify-API-1ED760?logo=spotify)](https://developer.spotify.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📊 Project Overview

An intelligent music analysis tool that uses machine learning to cluster your Spotify songs based on audio features. Discover hidden patterns in your listening habits and automatically generate themed playlists.

### 🎯 Key Features
- **Smart Clustering**: Groups songs using K-Means based on 6+ audio features
- **Interactive Visualizations**: PCA plots and elbow method for optimal cluster selection
- **Automated Playlists**: Creates personalized Spotify playlists for each cluster
- **Flexible Input**: Analyze your top tracks or any playlist
- **Batch Processing**: Process multiple playlists simultaneously
- **Export Results**: CSV export with cluster assignments and statistics

### 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/spotify-music-clustering.git
cd spotify-music-clustering

#Output
https://developer.spotify.com/dashboard/47583edf712f4c1bb955e3d4bb92bb78/metrics


# Install dependencies
pip install -r requirements.txt

# Configure Spotify credentials
cp .env.example .env
# Edit .env with your Spotify API credentials

# Run the application
python scripts/run_clustering.py
