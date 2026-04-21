#!/bin/bash
# Build script for py-cymbal Python bindings

set -e  # Exit on error

echo "Building py-cymbal Python bindings..."

# Set up environment
export PATH=$HOME/go/bin:$HOME/.local/bin:$(go env GOPATH 2>/dev/null)/bin:/usr/local/go/bin:$PATH
export CGO_CFLAGS="-DSQLITE_ENABLE_FTS5 $(python3 -c 'import sysconfig; print("-I" + sysconfig.get_path("include"))')"
# Clean previous builds
echo "Cleaning previous builds..."
rm -rf python/cymbal/_pycymbal* python/cymbal/*.pyc __pycache__ build dist *.egg-info python/cymbal/bin

# Download pinned Cymbal binaries
echo "Downloading pinned Cymbal v0.11.6 binaries..."
mkdir -p python/cymbal/bin

VERSION="v0.11.6"
BASE_URL="https://github.com/1broseidon/cymbal/releases/download/$VERSION"

# We use tar/unzip to extract the 'cymbal' binary and rename it

# Linux x86_64
curl -sL "$BASE_URL/cymbal_${VERSION}_linux_x86_64.tar.gz" | tar xz -C python/cymbal/bin cymbal
mv python/cymbal/bin/cymbal python/cymbal/bin/cymbal-linux
chmod +x python/cymbal/bin/cymbal-linux

# Windows x86_64
curl -sL "$BASE_URL/cymbal_${VERSION}_windows_x86_64.zip" -o /tmp/cymbal_win.zip
unzip -p /tmp/cymbal_win.zip cymbal.exe > python/cymbal/bin/cymbal-windows.exe
rm /tmp/cymbal_win.zip

# macOS (Intel)
curl -sL "$BASE_URL/cymbal_${VERSION}_darwin_x86_64.tar.gz" | tar xz -C python/cymbal/bin cymbal
mv python/cymbal/bin/cymbal python/cymbal/bin/cymbal-darwin
chmod +x python/cymbal/bin/cymbal-darwin

echo "Binaries downloaded successfully."

# Skip gopy/CGO build steps
echo "Skipping CGO build steps, using subprocess architecture..."

# Create dummy files if needed for backward compatibility during transition
touch python/cymbal/go.py python/cymbal/pycymbal.py

OS_NAME=$(uname -s)

# Create MANIFEST.in to ensure binary files are included in the wheel
echo "Creating MANIFEST.in..."
cat > MANIFEST.in << 'MANIFESTEOF'
include python/cymbal/bin/*
include python/cymbal/*.py
MANIFESTEOF

# Create setup.py for pip installation
echo "Creating setup.py..."
cat > setup.py << 'SETUPEOF'
from setuptools import setup
import os

setup(
    name="py-cymbal",
    version="0.1.17",
    description="Python bindings for Cymbal code indexing and symbol discovery",
    author="Cymbal Contributors",
    author_email="contact@example.com",
    url="https://github.com/dwash/py-cymbal",
    packages=["cymbal"],
    package_dir={"": "python"},
    package_data={"cymbal": ["bin/*", "*.py"]},
    zip_safe=False,
    install_requires=[],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
SETUPEOF

echo "Build complete!"
exit 0
include python/cymbal/*.so
include python/cymbal/*.pyd
include python/cymbal/*.dll
include python/cymbal/*.dylib
include python/cymbal/_pycymbal*
MANIFESTEOF

# Create setup.py for pip installation
echo "Creating setup.py..."
cat > setup.py << 'SETUPEOF'
from setuptools import setup, Extension
import os

# Check if we have the compiled extension
import glob
ext_files = glob.glob("python/cymbal/_pycymbal*")
dll_files = glob.glob("python/cymbal/pycymbal_go*")

setup(
    name="py-cymbal",
    version="0.1.17",
    description="Python bindings for Cymbal code indexing and symbol discovery",
    author="Cymbal Contributors",
    author_email="contact@example.com",
    url="https://github.com/dwash/py-cymbal",
    packages=["cymbal"],
    package_dir={"": "python"},
    package_data={"cymbal": ["*.so", "*.pyd", "*.dll", "*.dylib", "*.py", "_pycymbal*"]},
    ext_modules=[],
    zip_safe=False,
    install_requires=[],
    python_requires=">=3.7",
    license="MIT",
    license_files=[],
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
)
SETUPEOF

echo "Build complete!"
echo ""
echo "To install in development mode:"
echo "  pip install -e ."
echo ""
echo "To test the installation:"
echo "  python3 -c \"import cymbal; print('Cymbal Python bindings loaded successfully')\""
