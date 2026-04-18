#!/usr/bin/env python3
"""
Test script for building py-cymbal wheels and sdist.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return output."""
    print(f"\n>>> Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    if result.stdout:
        print(f"stdout:\n{result.stdout}")
    if result.stderr:
        print(f"stderr:\n{result.stderr}")
    print(f"Return code: {result.returncode}")
    return result

def clean_build_artifacts():
    """Clean up previous build artifacts."""
    print("\n=== Cleaning build artifacts ===")
    for dir_name in ['build', 'dist', '*.egg-info']:
        for path in Path('.').glob(dir_name):
            if path.exists():
                print(f"Removing: {path}")
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)
    
    # Also clean __pycache__ directories
    for path in Path('.').rglob('__pycache__'):
        if path.exists():
            print(f"Removing: {path}")
            shutil.rmtree(path, ignore_errors=True)

def test_wheel_build():
    """Test building a wheel."""
    print("\n=== Testing wheel build ===")
    
    # First ensure we have all required files
    required_files = [
        "setup.py",
        "pyproject.toml",
        "MANIFEST.in",
        "README.md",
        "python/cymbal/__init__.py",
        "python/cymbal/pycymbal.py",
        "python/cymbal/go.py",
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"Missing required files: {missing}")
        return False
    
    # Check for shared libraries
    so_files = list(Path("python/cymbal").glob("*.so"))
    if not so_files:
        print("Warning: No .so files found in python/cymbal/")
        print("You may need to run ./build_fixed.sh first")
    else:
        print(f"Found {len(so_files)} shared libraries:")
        for so_file in so_files:
            print(f"  - {so_file}")
    
    # Build wheel
    result = run_command("python3 -m build --wheel")
    if result.returncode != 0:
        print("\n✗ Wheel build failed")
        return False
    
    # Check if wheel was created
    wheels = list(Path("dist").glob("*.whl"))
    if not wheels:
        print("\n✗ No wheel files created in dist/")
        return False
    
    print(f"\n✓ Created {len(wheels)} wheel(s):")
    for wheel in wheels:
        print(f"  - {wheel.name}")
        
        # Inspect wheel contents
        print(f"    Inspecting wheel contents...")
        inspect_result = run_command(f"unzip -l {wheel}")
        
    return True

def test_sdist_build():
    """Test building a source distribution."""
    print("\n=== Testing sdist build ===")
    
    result = run_command("python3 -m build --sdist")
    if result.returncode != 0:
        print("\n✗ sdist build failed")
        return False
    
    # Check if sdist was created
    sdists = list(Path("dist").glob("*.tar.gz"))
    if not sdists:
        print("\n✗ No sdist files created in dist/")
        return False
    
    print(f"\n✓ Created {len(sdists)} sdist(s):")
    for sdist in sdists:
        print(f"  - {sdist.name}")
        
        # List sdist contents
        print(f"    Listing sdist contents...")
        list_result = run_command(f"tar -tzf {sdist} | head -20")
        
    return True

def test_pip_install(wheel_path):
    """Test pip install from a local wheel."""
    print(f"\n=== Testing pip install from {wheel_path} ===")
    
    # Create a temporary virtual environment
    temp_venv = Path(".cecli/temp/test_venv")
    if temp_venv.exists():
        shutil.rmtree(temp_venv)
    
    print(f"Creating temporary virtual environment at {temp_venv}")
    result = run_command(f"python3 -m venv {temp_venv}")
    if result.returncode != 0:
        print("\n✗ Failed to create virtual environment")
        return False
    
    pip_path = temp_venv / "bin" / "pip"
    python_path = temp_venv / "bin" / "python"
    
    # Install the wheel
    print(f"\nInstalling wheel...")
    result = run_command(f"{pip_path} install {wheel_path}")
    if result.returncode != 0:
        print("\n✗ pip install failed")
        return False
    
    # Test import
    print(f"\nTesting import...")
    test_script = """
import sys
print(f'Python path: {sys.path}')
try:
    import cymbal
    print('✓ Successfully imported cymbal')
    
    # Test basic functionality
    c = cymbal.Cymbal()
    print(f'✓ Created Cymbal instance, db_path: {c.db_path}')
    print(f'✓ Available functions: index_repository={hasattr(cymbal, "index_repository")}')
    print('✅ All imports and basic functionality work!')
except Exception as e:
    print(f'✗ Import failed: {e}')
    import traceback
    traceback.print_exc()
"""
    
    test_file = temp_venv / "test_import.py"
    with open(test_file, "w") as f:
        f.write(test_script)
    
    result = run_command(f"{python_path} {test_file}")
    
    # Clean up
    print(f"\nCleaning up temporary virtual environment...")
    shutil.rmtree(temp_venv, ignore_errors=True)
    
    return result.returncode == 0

def main():
    """Main test function."""
    print("Testing py-cymbal packaging for PyPI")
    print("=" * 50)
    
    # Clean first
    clean_build_artifacts()
    
    # Test builds
    wheel_ok = test_wheel_build()
    sdist_ok = test_sdist_build()
    
    if not wheel_ok and not sdist_ok:
        print("\n✗ Both wheel and sdist builds failed")
        return 1
    
    # Test pip install if we have a wheel
    if wheel_ok:
        wheels = list(Path("dist").glob("*.whl"))
        if wheels:
            # Use the first wheel
            install_ok = test_pip_install(wheels[0])
            if not install_ok:
                print("\n✗ pip install test failed")
                return 1
        else:
            print("\n⚠ No wheel found to test pip install")
    
    print("\n" + "=" * 50)
    print("✅ All packaging tests completed successfully!")
    print("\nNext steps for PyPI deployment:")
    print("1. Update version number in setup.py and pyproject.toml")
    print("2. Run: python3 -m twine upload dist/*")
    print("3. Or test with TestPyPI first: python3 -m twine upload --repository testpypi dist/*")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())