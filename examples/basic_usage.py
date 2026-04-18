#!/usr/bin/env python3
"""
Basic usage example for py-cymbal Python bindings.

This example demonstrates how to use the Cymbal Python bindings
for code indexing and symbol discovery.
"""

import os
import sys

# Add the parent directory to the path to import cymbal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

# Note: For the bindings to work properly, you may need to set LD_LIBRARY_PATH
# to include the directory containing the shared libraries.
# Example:
# export LD_LIBRARY_PATH=/path/to/py-cymbal/python/cymbal:$LD_LIBRARY_PATH

try:
    import cymbal
    print("✓ Successfully imported cymbal module")
except ImportError as e:
    print(f"✗ Failed to import cymbal: {e}")
    print("\nMake sure you have built the Python bindings first:")
    print("  1. Run './build.sh' to build the bindings")
    print("  2. Set LD_LIBRARY_PATH to include the python/cymbal directory")
    print("  3. Install with 'pip install -e .' or add to PYTHONPATH")
    sys.exit(1)

def demonstrate_basic_functionality():
    """Demonstrate basic Cymbal functionality."""
    print("\n=== Basic Cymbal Functionality ===")
    
    # Create a Cymbal instance
    print("1. Creating Cymbal instance...")
    c = cymbal.Cymbal()
    print(f"   ✓ Instance created. DB path: {c.db_path}")
    
    # Note: In a real scenario, you would index a repository first
    # For this example, we'll show the API without actual indexing
    
    print("\n2. Available methods:")
    print(f"   - c.index(repo_path): Index a repository")
    print(f"   - c.search(query, limit=20): Search for symbols")
    print(f"   - c.investigate(symbol_name): Investigate a symbol")
    print(f"   - c.find_references(symbol_name, limit=50): Find references")
    
    # Example of using context manager
    print("\n3. Using context manager:")
    with cymbal.Cymbal() as c2:
        print(f"   ✓ Context manager works. DB path: {c2.db_path}")
    
    print("\n4. Convenience functions:")
    print(f"   - cymbal.index_repository(repo_path)")
    print(f"   - cymbal.search_symbols(query, limit=20, db_path=None)")
    print(f"   - cymbal.investigate_symbol(symbol_name, db_path=None)")
    
    return c

def demonstrate_advanced_usage():
    """Demonstrate more advanced usage patterns."""
    print("\n=== Advanced Usage Patterns ===")
    
    # Example 1: Setting database path for existing index
    print("1. Reusing an existing index:")
    print("   c = cymbal.Cymbal()")
    print("   c.db_path = '/path/to/existing/index.db'")
    print("   results = c.search('function_name')")
    
    # Example 2: Error handling
    print("\n2. Error handling:")
    print("   try:")
    print("       c = cymbal.Cymbal()")
    print("       results = c.search('test')  # Will fail without index")
    print("   except Exception as e:")
    print("       print(f'Search failed: {e}')")
    
    # Example 3: Processing search results
    print("\n3. Processing search results:")
    print("   results = c.search('handle', limit=5)")
    print("   for symbol in results:")
    print("       print(f'{symbol.name} ({symbol.kind}) at {symbol.file}:{symbol.start_line}')")

def main():
    """Main function to run the example."""
    print("py-cymbal Python Bindings Example")
    print("=" * 40)
    
    # Check if we're in a development environment
    dev_env = os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'go'))
    
    if dev_env:
        print("\nDevelopment environment detected.")
        print("To build and test the bindings:")
        print("  1. cd /path/to/py-cymbal")
        print("  2. ./build.sh")
        print("  3. export LD_LIBRARY_PATH=$(pwd)/python/cymbal:$LD_LIBRARY_PATH")
        print("  4. python examples/basic_usage.py")
    else:
        print("\nAssuming installed package.")
        print("If installed via pip, simply import and use.")
    
    # Demonstrate functionality
    demonstrate_basic_functionality()
    demonstrate_advanced_usage()
    
    print("\n" + "=" * 40)
    print("Example completed successfully!")
    print("\nNext steps:")
    print("1. Index a repository: c.index('/path/to/your/code')")
    print("2. Search for symbols: c.search('function_name')")
    print("3. Investigate specific symbols: c.investigate('ClassName')")

if __name__ == "__main__":
    main()