# py-cymbal: Python Bindings for Cymbal

Python bindings for the Cymbal code indexing and symbol discovery tool, wrapping the standalone binaries via a clean Python API.

## Overview

Cymbal is a Go-based tool that uses tree-sitter for multi-language AST parsing and SQLite for indexed storage, providing fast symbol search, cross-references, impact analysis, and scoped diffs. These Python bindings allow Python developers to programmatically access Cymbal's powerful code analysis capabilities.

## Features

- **Repository Indexing**: Index code repositories for fast symbol lookup
- **Symbol Search**: Search for functions, classes, variables, and other symbols
- **Symbol Investigation**: Get detailed information about specific symbols including definitions and references
- **Reference Finding**: Find all references to a particular symbol
- **Multi-language Support**: Works with all languages supported by Cymbal (via tree-sitter)
- **Clean Python API**: Pythonic interface with context managers and convenience functions

## Installation

### Prerequisites

3. **Bash/Curl/Unzip**: Used by the build script to download binaries.
4. **Cymbal**: The Go library being wrapped

### Building from Source

```bash
# Clone the repository
git clone <repository-url>
cd py-cymbal

# Download the Cymbal binaries and create the Python package
./build.sh

# Install in development mode
pip install -e .
```

### Build Script

The `build.sh` script automates the entire build process:
1. Downloads the appropriate pre-compiled Cymbal binaries for Linux, macOS, and Windows.
2. Places the binaries in the `python/cymbal/bin/` directory.
3. Creates a `setup.py` for pip installation that bundles the correct binary for your platform.
## Usage

### Basic Example

```python
import cymbal

# Create a Cymbal instance
with cymbal.Cymbal() as c:
    # Index a repository
    stats = c.index("/path/to/your/repository")
    print(f"Indexing result: {stats}")
    
    # Search for symbols
    results = c.search("handleAuth", limit=10)
    for symbol in results:
        print(f"{symbol['name']} ({symbol['kind']}) at {symbol['file']}:{symbol['start_line']}")
    
    # Investigate a specific symbol
    investigation = c.investigate("UserModel")
    print(f"Symbol: {investigation['symbol']['name']}")
    print(f"References: {len(investigation['refs'])}")
    
    # Find references to a symbol
    references = c.find_references("DatabaseConnection", limit=20)
    for ref in references:
        print(f"Reference at {ref['file']}:{ref['line']}")
```

### Convenience Functions

```python
import cymbal

# Index a repository (one-liner)
stats = cymbal.index_repository("/path/to/repo")

# Search with existing database path
results = cymbal.search_symbols("config", limit=15, db_path="/path/to/index.db")

# Investigate a symbol
investigation = cymbal.investigate_symbol("ApiClient", db_path="/path/to/index.db")
```

### Advanced Usage

```python
import cymbal

# Reuse an existing index
try:
    c = cymbal.Cymbal()
    c.db_path = "/path/to/existing/index.db"  # Set path to existing database
    
    # Perform searches
    results = c.search("test", limit=5)
    
    # Process results
    for symbol in results:
        print(f"Found: {symbol['name']} in {symbol['file']}")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    c.close()
```

## API Reference

### `cymbal.Cymbal` Class

#### `__init__(repo_path=None)`
Create a new Cymbal instance. Optionally index a repository immediately.

#### `index(repo_path)`
Index a repository. Returns statistics about the indexing operation.

#### `search(query, limit=20)`
Search for symbols matching the query. Returns a list of symbol results.

#### `investigate(symbol_name)`
Investigate a specific symbol. Returns an investigation result with definition and references.

#### `find_references(symbol_name, limit=50)`
Find references to a symbol. Returns a list of reference results.

#### `db_path` (property)
Get or set the current database path.

#### `close()`
Close the Cymbal instance and release resources.

### Convenience Functions

#### `index_repository(repo_path)`
Convenience function to index a repository.

#### `search_symbols(query, limit=20, db_path=None)`
Convenience function to search for symbols.

#### `investigate_symbol(symbol_name, db_path=None)`
Convenience function to investigate a symbol.

## Architecture

The Python package uses a subprocess-based architecture to wrap the standalone Cymbal binaries:

1. **Pre-compiled Binaries**: Downloaded directly from the upstream Cymbal releases.
2. **Subprocess Wrapper**: The Python API executes the binary with the appropriate flags (e.g., `--json`) and parses the output.
3. **Python API Layer** (`python/cymbal/__init__.py`): Pythonic wrapper that provides a clean, intuitive interface.
### File Structure

```
py-cymbal/
├── python/              # Python bindings
│   └── cymbal/          # Python module
│       ├── __init__.py  # Python API layer
│       └── bin/         # Downloaded Cymbal binaries
├── examples/            # Usage examples
│   └── basic_usage.py  # Basic usage demonstration
├── build.sh            # Build automation script
├── setup.py            # pip installation configuration
└── README.md           # This file
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments
- [Cymbal](https://github.com/1broseidon/cymbal) for the excellent code indexing tool
- [gopy](https://github.com/go-python/gopy) for making Go-Python bindings possible
- [tree-sitter](https://tree-sitter.github.io/tree-sitter/) for robust parsing of multiple languages