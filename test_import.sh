#!/bin/bash
set -e

echo "Testing py-cymbal import..."
echo "==========================="

# Set LD_LIBRARY_PATH to find the shared libraries
export LD_LIBRARY_PATH="$(pwd)/python/cymbal:$LD_LIBRARY_PATH"
echo "LD_LIBRARY_PATH set to: $LD_LIBRARY_PATH"

# Test import
cd python
python3 -c "
import sys
print('Python path:', sys.path)

try:
    import cymbal
    print('✓ Successfully imported cymbal module')
    
    # Test creating an instance
    c = cymbal.Cymbal()
    print('✓ Cymbal instance created')
    print(f'  DB path: {c.db_path}')
    
    # Test the convenience functions exist
    print('\\nAvailable functions:')
    print(f'  index_repository: {hasattr(cymbal, \"index_repository\")}')
    print(f'  search_symbols: {hasattr(cymbal, \"search_symbols\")}')
    print(f'  investigate_symbol: {hasattr(cymbal, \"investigate_symbol\")}')
    
    print('\\n✅ All tests passed!')
    
except ImportError as e:
    print(f'✗ ImportError: {e}')
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f'✗ Other error: {e}')
    import traceback
    traceback.print_exc()
"
