#!/bin/bash
# Build script for py-cymbal Python bindings

set -e  # Exit on error

echo "Building py-cymbal Python bindings..."

# Set up environment
export PATH=$HOME/go/bin:$HOME/.local/bin:$(go env GOPATH)/bin:$PATH
export CGO_CFLAGS="-DSQLITE_ENABLE_FTS5 $(python3 -c 'import sysconfig; print("-I" + sysconfig.get_path("include"))')"
# Clean previous builds
echo "Cleaning previous builds..."
rm -rf python/cymbal/_pycymbal*.so python/cymbal/*.pyc __pycache__ build dist *.egg-info

# Build Go wrapper and generate Python bindings
echo "Building Go wrapper and generating Python bindings..."
cd go

# Clean generated files
rm -f pycymbal.go pycymbal.py go.py __init__.py build.py Makefile pycymbal.c pycymbal_go.so _pycymbal.so

# Generate Python bindings with gopy
echo "Generating Python bindings with gopy..."
gopy gen -vm=python3 ./pycymbal
# Inject rpath fix into the generated Makefile
sed -i "s|pycymbal_go\$(LIBEXT) -o _pycymbal\$(LIBEXT) |pycymbal_go\$(LIBEXT) -o _pycymbal\$(LIBEXT) -Wl,-rpath,'\$\$ORIGIN' |" Makefile
make build

# Move files to python directory
echo "Organizing Python module..."
cd ..
mv go/_pycymbal*.so go/pycymbal.py go/go.py python/cymbal/ 2>/dev/null || true
mv go/pycymbal_go.so python/cymbal/ 2>/dev/null || true
# Do NOT copy pycymbal.c to python/cymbal/ to avoid setuptools auto-detection failure
rm -f python/cymbal/pycymbal.c

# Fix rpath so _pycymbal.so can find pycymbal_go.so without LD_LIBRARY_PATH
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v patchelf >/dev/null 2>&1; then
        echo "Patching rpath for Linux..."
        patchelf --set-rpath '$ORIGIN' python/cymbal/_pycymbal.so
    else
        echo "Warning: patchelf not found. LD_LIBRARY_PATH will be required."
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Patching rpath for macOS..."
    install_name_tool -change pycymbal_go.so @loader_path/pycymbal_go.so python/cymbal/_pycymbal.so
fi
# Create setup.py for pip installation
echo "Creating setup.py..."
cat > setup.py << 'SETUPEOF'
from setuptools import setup, Extension
import os

# Check if we have the compiled extension
ext_files = []
if os.path.exists("python/cymbal/_pycymbal.so"):
    ext_files = ["python/cymbal/_pycymbal.so"]

setup(
    name="py-cymbal",
    version="0.1.2",
    description="Python bindings for Cymbal code indexing and symbol discovery",
    author="Cymbal Contributors",
    author_email="contact@example.com",
    url="https://github.com/dwash/py-cymbal",
    packages=["cymbal"],
    package_dir={"": "python"},
    package_data={"cymbal": ["*.so", "*.py"]},
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
