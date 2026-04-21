"""
Python bindings for Cymbal code indexing and symbol discovery tool.

This module provides Python bindings for the Cymbal tool, allowing
programmatic access to code symbol analysis, search, and reference finding.
"""
import os
import sys

# Windows DLL support: Since Python 3.8, we must explicitly add the package 
# directory to the DLL search path so _pycymbal.pyd can find pycymbal_go.dll
if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    pkg_dir = os.path.abspath(os.path.dirname(__file__))
    if pkg_dir and os.path.isdir(pkg_dir):
        os.add_dll_directory(pkg_dir)
        # Also add to PATH for older Python versions or specific environments
        os.environ['PATH'] = pkg_dir + os.path.pathsep + os.environ.get('PATH', '')

cwd = os.getcwd()

# Platform-specific binary loading
def _load_binary():
    import importlib.util
    import platform
    
    pkg_dir = os.path.dirname(__file__)
    system = platform.system().lower()
    
    # Map platform to our specific binary names
    ext_map = {
        "linux": ".linux.so",
        "windows": ".windows.pyd",
        "darwin": ".darwin.dylib"
    }
    
    suffix = ext_map.get(system)
    if not suffix:
        raise ImportError(f"Unsupported platform: {system}")
        
    binary_path = os.path.join(pkg_dir, f"_pycymbal{suffix}")
    if not os.path.exists(binary_path):
        # Fallback to standard name if platform-specific one isn't found
        # (useful for local development/single-platform builds)
        for fallback in [".so", ".pyd", ".dylib"]:
            p = os.path.join(pkg_dir, f"_pycymbal{fallback}")
            if os.path.exists(p):
                binary_path = p
                break
        else:
            raise ImportError(f"Could not find _pycymbal binary at {pkg_dir}")

    # Load the module
    spec = importlib.util.spec_from_file_location("cymbal._pycymbal", binary_path)
    mod = importlib.util.module_from_spec(spec)
    # Inject into sys.modules and the current package's namespace
    # to satisfy 'from . import _pycymbal' in generated submodules
    sys.modules["cymbal._pycymbal"] = mod
    setattr(sys.modules[__name__], "_pycymbal", mod)
    
    # Also inject into 'cymbal' in case it's known by its absolute name
    if "cymbal" in sys.modules:
        setattr(sys.modules["cymbal"], "_pycymbal", mod)
    
    spec.loader.exec_module(mod)
    return mod

try:
    _load_binary()
except Exception:
    pass

# Move imports inside to avoid circular dependencies with generated submodules
# which do 'from . import _pycymbal'
def _get_go():
    from . import go
    return go

def _get_pycymbal():
    from . import pycymbal
    return pycymbal

class Cymbal:
    """Main interface to Cymbal functionality."""
    
    def __init__(self, repo_path=None):
        """
        Initialize a Cymbal instance.
        
        Args:
            repo_path (str, optional): Path to repository to index immediately.
        """
        cwd = os.getcwd()
        try:
            pycymbal = _get_pycymbal()
            self._cymbal = pycymbal.NewCymbal()
            if repo_path:
                self.index(repo_path)
        finally:
            os.chdir(cwd)
    
    def _symbol_to_dict(self, symbol):
        """Convert a SymbolResult to a dictionary."""
        if not symbol:
            return None
        return {
            "name": symbol.Name,
            "kind": symbol.Kind,
            "file": symbol.File,
            "start_line": symbol.StartLine,
            "end_line": symbol.EndLine,
            "language": symbol.Language
        }

    def _ref_to_dict(self, ref):
        """Convert a RefResult to a dictionary."""
        if not ref:
            return None
        return {
            "file": ref.File,
            "line": ref.Line,
            "rel_path": ref.RelPath,
            "name": ref.Name
        }

    def _impact_to_dict(self, impact):
        """Convert an ImpactResult to a dictionary."""
        if not impact:
            return None
        return {
            "symbol": self._symbol_to_dict(impact.Symbol),
            "reason": impact.Reason,
            "severity": impact.Severity
        }

    def index(self, repo_path):
        """
        Index a repository.
        
        Args:
            repo_path (str): Path to repository to index.
            
        Returns:
            str: Statistics about the indexing operation.
            
        Raises:
            Exception: If indexing fails.
        """
        return str(self._cymbal.Index(repo_path))
    
    def search(self, query, limit=20):
        """
        Search for symbols matching the query.
        
        Args:
            query (str): Search query text.
            limit (int): Maximum number of results to return.
            
        Returns:
            list: List of symbol results (as dictionaries).
            
        Raises:
            Exception: If search fails or no database is available.
        """
        results = self._cymbal.Search(query, limit)
        return [self._symbol_to_dict(s) for s in results]
    
    def investigate(self, symbol_name, file_hint=""):
        """
        Investigate a specific symbol.
        
        Args:
            symbol_name (str): Name of symbol to investigate.
            file_hint (str, optional): Filter matches to symbols in this file path.
            
        Returns:
            dict: Investigation result with definition and references.
            
        Raises:
            Exception: If investigation fails or no database is available.
        """
        res = self._cymbal.Investigate(symbol_name, file_hint)
        if not res:
            return None
            
        return {
            "symbol": self._symbol_to_dict(res.Symbol),
            "source": res.Source,
            "kind": res.Kind,
            "refs": [self._ref_to_dict(r) for r in res.Refs],
            "impact": [self._impact_to_dict(i) for i in res.Impact],
            "members": [self._symbol_to_dict(m) for m in res.Members],
            "outline": [self._symbol_to_dict(o) for o in res.Outline]
        }
    
    def find_references(self, symbol_name, limit=50):
        """
        Find references to a symbol.
        
        Args:
            symbol_name (str): Name of symbol to find references for.
            limit (int): Maximum number of references to return.
            
        Returns:
            list: List of reference results (as dictionaries).
            
        Raises:
            Exception: If reference finding fails or no database is available.
        """
        refs = self._cymbal.FindReferences(symbol_name, limit)
        return [self._ref_to_dict(r) for r in refs]
    
    @property
    def db_path(self):
        """Get current database path."""
        return str(self._cymbal.GetDBPath())
    
    @db_path.setter
    def db_path(self, path):
        """Set database path directly."""
        self._cymbal.SetDBPath(path)
    
    def close(self):
        """Close Cymbal instance and release resources."""
        # Note: The Go wrapper doesn't have a Close method yet
        pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

# Convenience functions
def index_repository(repo_path):
    """Convenience function to index a repository."""
    with Cymbal() as c:
        return c.index(repo_path)

def search_symbols(query, limit=20, db_path=None):
    """Convenience function to search for symbols."""
    c = Cymbal()
    if db_path:
        c.db_path = db_path
    try:
        return c.search(query, limit)
    finally:
        c.close()

def investigate_symbol(symbol_name, file_hint="", db_path=None):
    """Convenience function to investigate a symbol."""
    c = Cymbal()
    if db_path:
        c.db_path = db_path
    try:
        return c.investigate(symbol_name, file_hint)
    finally:
        c.close()

# Export main classes and functions
__all__ = ['Cymbal', 'index_repository', 'search_symbols', 'investigate_symbol']
