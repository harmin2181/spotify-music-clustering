import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    # Try importing from the fixed module
    from cluster_analyzer import ClusterAnalyzer
    print("✅ ClusterAnalyzer imported successfully")
    print("Class exists and is ready to use!")
    
    # Test creating an instance
    analyzer = ClusterAnalyzer()
    print("✅ ClusterAnalyzer instance created")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()