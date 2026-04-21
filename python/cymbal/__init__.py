"""
Python bindings for Cymbal code indexing and symbol discovery tool.

This module provides Python bindings for the Cymbal tool, allowing
programmatic access to code symbol analysis, search, and reference finding.
"""
import os
import sys
import platform
import subprocess
import json
import shutil

class CymbalError(Exception):
    """Exception raised for errors in the Cymbal CLI execution."""
    pass

def _get_cymbal_binary():
    """Locate the platform-specific Cymbal binary."""
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    system = platform.system().lower()
    
    bin_name = "cymbal"
    if system == "linux":
        bin_name = "cymbal-linux"
    elif system == "windows":
        bin_name = "cymbal-windows.exe"
    elif system == "darwin":
        bin_name = "cymbal-darwin"
        
    bin_path = os.path.join(pkg_dir, "bin", bin_name)
    
    if not os.path.exists(bin_path):
        raise FileNotFoundError(f"Cymbal binary not found at {bin_path}. Ensure it is installed correctly.")
        
    return bin_path

class Cymbal:
    """Main interface to Cymbal functionality."""
    
    def __init__(self, repo_path=None):
        """
        Initialize a Cymbal instance.
        
        Args:
            repo_path (str, optional): Path to repository to index immediately.
        """
        self._bin_path = _get_cymbal_binary()
        self._db_path = None
        
        if repo_path:
            self.index(repo_path)
            
    def _run_cli(self, args, parse_json=True):
        """Run the Cymbal CLI and optionally parse JSON output."""
        cmd = [self._bin_path] + args
        if parse_json and "--json" not in cmd:
            cmd.append("--json")
            
        if self._db_path:
            cmd.extend(["--db", self._db_path])
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if parse_json:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    raise CymbalError(f"Failed to parse JSON output from Cymbal: {result.stdout}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise CymbalError(f"Cymbal command failed (exit code {e.returncode}):\nStdout: {e.stdout}\nStderr: {e.stderr}")
            
    def index(self, repo_path):
        """
        Index a repository.
        
        Args:
            repo_path (str): Path to repository to index.
            
        Returns:
            str: Output from the indexing operation.
            
        Raises:
            CymbalError: If indexing fails.
        """
        # The index command might not output JSON cleanly, so we parse manually or just return text
        cmd = ["index", repo_path]
        return self._run_cli(cmd, parse_json=False)
        
    def search(self, query, limit=20):
        """
        Search for symbols matching the query.
        
        Args:
            query (str): Search query text.
            limit (int): Maximum number of results to return (ignored in CLI for now unless mapped).
            
        Returns:
            list: List of symbol results (as dictionaries).
            
        Raises:
            CymbalError: If search fails.
        """
        res = self._run_cli(["search", query])
        return res.get("results", [])
        
    def investigate(self, symbol_name, file_hint=""):
        """
        Investigate a specific symbol.
        
        Args:
            symbol_name (str): Name of symbol to investigate.
            file_hint (str, optional): Filter matches to symbols in this file path.
            
        Returns:
            dict: Investigation result with definition and references.
            
        Raises:
            CymbalError: If investigation fails.
        """
        # Form the query
        query = symbol_name
        if file_hint:
            query = f"{file_hint}:{symbol_name}"
            
        res = self._run_cli(["investigate", query])
        return res
        
    def find_references(self, symbol_name, limit=50):
        """
        Find references to a symbol.
        
        Args:
            symbol_name (str): Name of symbol to find references for.
            limit (int): Maximum number of references to return.
            
        Returns:
            list: List of reference results (as dictionaries).
            
        Raises:
            CymbalError: If reference finding fails.
        """
        res = self._run_cli(["refs", symbol_name])
        return res.get("references", [])
        
    @property
    def db_path(self):
        """Get current database path."""
        return self._db_path
        
    @db_path.setter
    def db_path(self, path):
        """Set database path directly."""
        self._db_path = path
        
    def close(self):
        """Close Cymbal instance and release resources (No-op in subprocess mode)."""
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
