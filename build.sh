#!/bin/bash
set -e

# Build cross-platform wheels for py-cymbal by downloading pre-compiled binaries
# and packaging them into appropriate platform-specific wheels.

VERSION="0.1.18"
CYMBAL_VERSION="0.11.6"
BASE_URL="https://github.com/1broseidon/cymbal/releases/download/v${CYMBAL_VERSION}"

echo "Building py-cymbal v${VERSION} wheels using Cymbal v${CYMBAL_VERSION} binaries..."

# Ensure directories exist
mkdir -p dist
mkdir -p python/cymbal/bin
mkdir -p .tmp

# Clean previous builds
rm -rf build python/cymbal/bin/* .tmp/*

# Map python platform tags to cymbal release assets and binary names
# Format: "plat_tag:archive_name:bin_in_archive:dest_name"
declare -a PLATFORMS=(
    "manylinux_2_17_x86_64:cymbal_v${CYMBAL_VERSION}_linux_x86_64.tar.gz:cymbal:cymbal-linux"
    "manylinux_2_17_aarch64:cymbal_v${CYMBAL_VERSION}_linux_arm64.tar.gz:cymbal:cymbal-linux"
    "macosx_10_9_x86_64:cymbal_v${CYMBAL_VERSION}_darwin_x86_64.tar.gz:cymbal:cymbal-darwin"
    "macosx_11_0_arm64:cymbal_v${CYMBAL_VERSION}_darwin_arm64.tar.gz:cymbal:cymbal-darwin"
    "win_amd64:cymbal_v${CYMBAL_VERSION}_windows_x86_64.zip:cymbal.exe:cymbal-windows.exe"
)

# Temporary setup.py template for building platform-specific wheels
cat << 'SETUPEOF' > setup.py
from setuptools import setup
from setuptools.dist import Distribution
import os

class BinaryDistribution(Distribution):
    def has_ext_modules(foo):
        return True

plat_name = os.environ.get('WHEEL_PLATFORM_NAME', 'any')

setup(
    distclass=BinaryDistribution,
    options={'bdist_wheel': {'plat_name': plat_name}}
)
SETUPEOF

for plat_info in "${PLATFORMS[@]}"; do
    IFS=':' read -r plat_tag archive_name bin_in_archive dest_name <<< "$plat_info"
    
    echo -e "\n=== Building wheel for $plat_tag ==="
    
    # Clean bin dir
    rm -rf python/cymbal/bin/*
    
    # Download archive if not exists
    archive_path=".tmp/$archive_name"
    if [ ! -f "$archive_path" ]; then
        url="${BASE_URL}/${archive_name}"
        echo "Downloading $url"
        curl -sL -o "$archive_path" "$url"
    fi
    
    # Extract binary
    bin_path="python/cymbal/bin/$dest_name"
    echo "Extracting $bin_in_archive to $bin_path"
    
    if [[ "$archive_name" == *.zip ]]; then
        unzip -p "$archive_path" "$bin_in_archive" > "$bin_path"
    else
        tar -xzf "$archive_path" -O "$bin_in_archive" > "$bin_path"
    fi
    
    # Make executable if not Windows
    if [[ "$dest_name" != *.exe ]]; then
        chmod +x "$bin_path"
    fi
    
    # Build wheel
    echo "Running python -m build"
    export WHEEL_PLATFORM_NAME="$plat_tag"
    python -m build --wheel --no-isolation
done

# Clean up
rm setup.py
rm -rf .tmp build

echo -e "\n=== Build complete! Wheels are in dist/ ==="
ls -lh dist/
