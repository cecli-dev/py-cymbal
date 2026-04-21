#!/bin/bash
# Build script for py-cymbal Python bindings

set -e  # Exit on error

echo "Building py-cymbal Python bindings..."

# Set up environment
export PATH=$HOME/go/bin:$HOME/.local/bin:$(go env GOPATH 2>/dev/null)/bin:/usr/local/go/bin:$PATH
export CGO_CFLAGS="-DSQLITE_ENABLE_FTS5 $(python3 -c 'import sysconfig; print("-I" + sysconfig.get_path("include"))')"
# Clean previous builds
echo "Cleaning previous builds..."
rm -rf python/cymbal/_pycymbal* python/cymbal/*.pyc __pycache__ build dist *.egg-info

# Build Go wrapper and generate Python bindings
echo "Building Go wrapper and generating Python bindings..."
# We will cd into go inside build_target or for gopy gen

# Clean generated files
rm -f pycymbal.go pycymbal.py go.py __init__.py build.py Makefile pycymbal.c pycymbal_go.* _pycymbal.*

# Generate Python bindings with gopy
echo "Generating Python bindings with gopy..."
cd go
gopy gen -vm=python3 ./pycymbal
cd ..

OS_NAME=$(uname -s)
# Inject rpath fix into the generated Makefile (Linux/macOS only)
if [[ "$OS_NAME" == "Darwin" ]]; then
    sed -i '' "s|pycymbal_go\$(LIBEXT) -o _pycymbal\$(LIBEXT) |pycymbal_go\$(LIBEXT) -o _pycymbal\$(LIBEXT) -Wl,-rpath,'\$\$ORIGIN' |" go/Makefile
elif [[ "$OS_NAME" == "Linux" ]]; then
    sed -i "s|pycymbal_go\$(LIBEXT) -o _pycymbal\$(LIBEXT) |pycymbal_go\$(LIBEXT) -o _pycymbal\$(LIBEXT) -Wl,-rpath,'\$\$ORIGIN' |" go/Makefile
fi
# Build
echo "Building for host platform..."
cd go

# Use standard LIBEXT for the current platform
if [[ "$OS_NAME" == "Linux" ]]; then
    make build LIBEXT=.so
    [ -f _pycymbal.so ] && mv _pycymbal.so ../python/cymbal/_pycymbal.linux.so
    [ -f pycymbal_go.so ] && mv pycymbal_go.so ../python/cymbal/pycymbal_go.linux.so
elif [[ "$OS_NAME" == *"MINGW"* ]] || [[ "$OS_NAME" == *"MSYS"* ]] || [[ "$OS_NAME" == *"CYGWIN"* ]] || [[ "$OS_NAME" == "Windows_NT" ]]; then
    echo "Building for Windows (manual)..."
    # Manual build for Windows to avoid Makefile 'missing separator' issues
    goimports -w pycymbal.go
    # Fix 'two or more data types in declaration specifiers' error for bool on Windows
    sed -i 's/typedef uint8_t bool;/\/\/ typedef uint8_t bool;/' pycymbal.go
    go build -buildmode=c-shared -o pycymbal_go.dll pycymbal.go
    python3 build.py
    
    # Get Python include and lib paths
    PY_INC=$(python3 -c "import sysconfig; print(sysconfig.get_path('include'))")
    PY_LIB=$(python3 -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR') or '')")
    PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')")
    
    # Compile the C extension
    gcc pycymbal.c pycymbal_go.dll -o _pycymbal.pyd -I"$PY_INC" -L"$PY_LIB" -lpython$PY_VER -shared -w
    
    [ -f _pycymbal.pyd ] && mv _pycymbal.pyd ../python/cymbal/_pycymbal.windows.pyd
    [ -f pycymbal_go.dll ] && mv pycymbal_go.dll ../python/cymbal/pycymbal_go.windows.dll
elif [[ "$OS_NAME" == "Darwin" ]]; then
    make build LIBEXT=.dylib
    ls -la
    [ -f _pycymbal.so ] && mv _pycymbal.so ../python/cymbal/_pycymbal.darwin.dylib
    [ -f _pycymbal.dylib ] && mv _pycymbal.dylib ../python/cymbal/_pycymbal.darwin.dylib
    [ -f pycymbal_go.dylib ] && mv pycymbal_go.dylib ../python/cymbal/pycymbal_go.darwin.dylib
else
    make build
fi
mkdir -p ../python/cymbal
mv pycymbal.py go.py ../python/cymbal/
cd ..
rm -f python/cymbal/pycymbal.c

# Move files to python directory
echo "Organizing Python module..."
cd ..
# Files are already moved by build_target or the mv commands above
# Do NOT copy pycymbal.c to python/cymbal/ to avoid setuptools auto-detection failure
rm -f python/cymbal/pycymbal.c

# Fix rpath for Linux and macOS binaries if they exist
if [ -f python/cymbal/_pycymbal.linux.so ]; then
    if command -v patchelf >/dev/null 2>&1; then
        echo "Patching rpath for Linux..."
        patchelf --set-rpath '$ORIGIN' python/cymbal/_pycymbal.linux.so
    fi
fi
if [ -f python/cymbal/_pycymbal.darwin.dylib ]; then
    echo "Patching rpath for macOS..."
    install_name_tool -change pycymbal_go.dylib @loader_path/pycymbal_go.darwin.dylib python/cymbal/_pycymbal.darwin.dylib
fi
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
    version="0.1.7",
    description="Python bindings for Cymbal code indexing and symbol discovery",
    author="Cymbal Contributors",
    author_email="contact@example.com",
    url="https://github.com/dwash/py-cymbal",
    packages=["cymbal"],
    package_dir={"": "python"},
    package_data={"cymbal": ["*.so", "*.pyd", "*.dll", "*.dylib", "*.py"]},
    ext_modules=[],
    zip_safe=False,
    install_requires=[],
    python_requires=">=3.7",
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
