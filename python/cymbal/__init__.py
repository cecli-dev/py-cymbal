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

from typing import Optional, List, Dict, Any
from pathlib import Path

# Platform-specific binary names
PLATFORM_BINARIES = {
    "linux": "cymbal-linux",
    "windows": "cymbal-windows.exe", 
    "darwin": "cymbal-darwin"
}

class CymbalSubprocess:
    """Subprocess-based interface to Cymbal binary."""
    
    def __init__(self, binary_path: Optional[str] = None):
        """
        Initialize Cymbal subprocess interface.
        
        Args:
            binary_path: Optional path to Cymbal binary. If not provided,
                        will look in package's bin directory.
        """
        self.binary_path = binary_path or self._find_binary()
        self.temp_dir = None
        self.db_path = None
        
    def _find_binary(self) -> str:
        """Find the Cymbal binary for the current platform."""
        pkg_dir = Path(__file__).parent
        bin_dir = pkg_dir / "bin"
        system = platform.system().lower()
        
        # Map system to binary name
        binary_name = PLATFORM_BINARIES.get(system)
        if not binary_name:
            raise RuntimeError(f"Unsupported platform: {system}")
        
        # Check in bin directory first
        binary_path = bin_dir / binary_name
        if binary_path.exists():
            if system != "windows":
                binary_path.chmod(0o755)
            return str(binary_path)
        
        # Check if binary exists without bin directory (legacy location)
        binary_path = pkg_dir / binary_name
        if binary_path.exists():
            if system != "windows":
                binary_path.chmod(0o755)
            return str(binary_path)
        
        raise RuntimeError(
            f"Cymbal binary not found for {system}. "
            f"Expected at: {bin_dir / binary_name} or {pkg_dir / binary_name}"
        )
    
    def _run_command(self, args: List[str], input_data: Optional[str] = None) -> Dict[str, Any]:
        """Run Cymbal command and parse JSON output."""
        cmd = [self.binary_path] + args
        
        # Add db_path if set
        if self.db_path:
            cmd.extend(["--db", self.db_path])
            
        if "--json" not in cmd:
            cmd.append("--json")
        
        try:
            result = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                error_output = result.stderr + result.stdout
                if "no results found" in error_output.lower():
                    return {}
                raise RuntimeError(
                    f"Cymbal command failed: {result.stderr or result.stdout}"
                )
            
            # Parse JSON output
            try:
                # Sometime cymbal outputs extra plain text, try to extract json from the output.
                output_str = result.stdout.strip()
                if not output_str.startswith("{") and not output_str.startswith("["):
                    # try to find the start of json
                    json_start = output_str.find("{")
                    array_start = output_str.find("[")
                    if json_start != -1 and (array_start == -1 or json_start < array_start):
                         output_str = output_str[json_start:]
                    elif array_start != -1:
                        output_str = output_str[array_start:]
                
                if not output_str:
                    return {}
                    
                return json.loads(output_str)
            except json.JSONDecodeError as e:
                # If it's still not valid JSON, but the command succeeded, maybe it doesn't output JSON for this action.
                if result.returncode == 0:
                    return {"result": result.stdout}
                raise RuntimeError(f"Failed to parse Cymbal output: {e}. Output: {result.stdout}")
        except Exception as e:
            raise RuntimeError(f"Failed to execute Cymbal: {e}")
    
    def index(self, repo_path: str) -> Dict[str, Any]:
        """Index a repository."""
        return self._run_command(["index", repo_path])
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for symbols."""
        return self._run_command(["search", query, "--limit", str(limit)])
    
    def investigate(self, symbol_name: str, file_hint: str = "") -> Dict[str, Any]:
        """Investigate a symbol."""

        if file_hint:
            symbol_name = f"{file_hint}:{symbol_name}"

        args = ["investigate", symbol_name]

        return self._run_command(args)
    
    def find_references(self, symbol_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Find references to a symbol."""
        return self._run_command(["refs", symbol_name, "--limit", str(limit)])
    
    def close(self):
        """Clean up resources."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class Cymbal:
    """Main interface to Cymbal functionality."""
    
    def __init__(self, repo_path=None):
        """
        Initialize a Cymbal instance.
        
        Args:
            repo_path (str, optional): Path to repository to index immediately.
        """
        self._cymbal = CymbalSubprocess()
        if repo_path:
            self.index(repo_path)
    
    @property
    def db_path(self):
        return self._cymbal.db_path
        
    @db_path.setter
    def db_path(self, path):
        self._cymbal.db_path = path

    def index(self, repo_path):
        return self._cymbal.index(repo_path)
        
    def search(self, query, limit=20):
        res = self._cymbal.search(query, limit)
        if isinstance(res, dict):
            return res.get("results", [])
        return res if res else []
        
    def investigate(self, symbol_name, file_hint=""):
        res = self._cymbal.investigate(symbol_name, file_hint)
        return res
        
    def find_references(self, symbol_name, limit=50):
        res = self._cymbal.find_references(symbol_name, limit)
        if isinstance(res, dict):
            return res.get("results", [])
        return res if res else []
    def close(self):
        self._cymbal.close()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
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
def find_references(symbol_name, limit=50, db_path=None):
    """Convenience function to find references to a symbol."""
    c = Cymbal()
    if db_path:
        c.db_path = db_path
    try:
        return c.find_references(symbol_name, limit)
    finally:
        c.close()

# Export main classes and functions
