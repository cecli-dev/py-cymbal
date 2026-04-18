#!/usr/bin/env python3
import sys
import os

# Add the python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

# Set LD_LIBRARY_PATH to find the shared libraries
cymbal_dir = os.path.join(os.path.dirname(__file__), 'python', 'cymbal')
os.environ['LD_LIBRARY_PATH'] = cymbal_dir + (':' + os.environ.get('LD_LIBRARY_PATH', '') if os.environ.get('LD_LIBRARY_PATH') else '')

try:
    import cymbal
    print("✓ Cymbal module imported successfully")
    
    # Test creating an instance
    c = cymbal.Cymbal()
    print("✓ Cymbal instance created")
    
    # Test getting DB path
    print(f"  DB path: {c.db_path}")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
