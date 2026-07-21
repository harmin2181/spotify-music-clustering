
### **setup.py** (Your version - fixed Python version)

```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="spotify-music-clustering",
    version="1.0.0",
    author="Harminder Singh",
    author_email="singh_harmin@outlook.com",
    description="AI-powered Spotify playlist clustering and analysis tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/harmin2181/spotify-music-clustering",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "spotipy>=2.22.1",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "python-dotenv>=1.0.0",
        "plotly>=5.15.0",
        "tqdm>=4.65.0",
    ],
    entry_points={
        "console_scripts": [
            "spotify-cluster=scripts.run_clustering:main",
        ],
    },
)