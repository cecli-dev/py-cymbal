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
    pkg_dir = os.path.dirname(__file__)
    if pkg_dir:
        os.add_dll_directory(pkg_dir)

from . import pycymbal
from . import go

class Cymbal:
    """Main interface to Cymbal functionality."""
    
    def __init__(self, repo_path=None):
        """
        Initialize a Cymbal instance.
        
        Args:
            repo_path (str, optional): Path to repository to index immediately.
        """
        self._cymbal = pycymbal.NewCymbal()
        if repo_path:
            self.index(repo_path)
    
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
        return self._cymbal.Index(repo_path)
    
    def search(self, query, limit=20):
        """
        Search for symbols matching the query.
        
        Args:
            query (str): Search query text.
            limit (int): Maximum number of results to return.
            
        Returns:
            list: List of symbol results (as Go objects).
            
        Raises:
            Exception: If search fails or no database is available.
        """
        return self._cymbal.Search(query, limit)
    
    def investigate(self, symbol_name):
        """
        Investigate a specific symbol.
        
        Args:
            symbol_name (str): Name of symbol to investigate.
            
        Returns:
            object: Investigation result with definition and references.
            
        Raises:
            Exception: If investigation fails or no database is available.
        """
        return self._cymbal.Investigate(symbol_name)
    
    def find_references(self, symbol_name, limit=50):
        """
        Find references to a symbol.
        
        Args:
            symbol_name (str): Name of symbol to find references for.
            limit (int): Maximum number of references to return.
            
        Returns:
            list: List of reference results.
            
        Raises:
            Exception: If reference finding fails or no database is available.
        """
        return self._cymbal.FindReferences(symbol_name, limit)
    
    @property
    def db_path(self):
        """Get current database path."""
        return self._cymbal.GetDBPath()
    
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

def investigate_symbol(symbol_name, db_path=None):
    """Convenience function to investigate a symbol."""
    c = Cymbal()
    if db_path:
        c.db_path = db_path
    try:
        return c.investigate(symbol_name)
    finally:
        c.close()

# Export main classes and functions
__all__ = ['Cymbal', 'index_repository', 'search_symbols', 'investigate_symbol']
