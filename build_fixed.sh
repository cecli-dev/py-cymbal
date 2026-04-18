#!/bin/bash
# Build script for py-cymbal Python bindings with rpath fix

set -e  # Exit on error

echo "Building py-cymbal Python bindings with rpath fix..."

# Set up environment
export PATH=/home/dwash/go/bin:$PATH
export CGO_CFLAGS="-DSQLITE_ENABLE_FTS5 -I/usr/include/python3.12"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf python/cymbal/_pycymbal*.so python/cymbal/pycymbal_go.so python/cymbal/*.pyc __pycache__ build dist *.egg-info

# Build Go wrapper and generate Python bindings
echo "Building Go wrapper and generating Python bindings..."
cd go

# Clean generated files
rm -f pycymbal.go pycymbal.py go.py __init__.py build.py Makefile pycymbal.c pycymbal_go.so _pycymbal.so

# Generate Python bindings with gopy
echo "Generating Python bindings with gopy..."
gopy gen -vm=python3 ./pycymbal

# Patch Makefile to add rpath
echo "Patching Makefile to add rpath..."
sed -i 's/\$(GCC) pycymbal\.c  pycymbal_go\$(LIBEXT) -o _pycymbal\$(LIBEXT) \$(CFLAGS) \$(LDFLAGS) -fPIC --shared -w/\$(GCC) pycymbal.c  pycymbal_go\$(LIBEXT) -o _pycymbal\$(LIBEXT) \$(CFLAGS) \$(LDFLAGS) -Wl,-rpath,\\\$\$ORIGIN -fPIC --shared -w/' Makefile

# Build the extension
echo "Building Python extension..."
make build

# Move files to python directory
echo "Organizing Python module..."
cd ..
mv go/_pycymbal*.so go/pycymbal.py go/go.py python/cymbal/ 2>/dev/null || true
mv go/pycymbal_go.so python/cymbal/ 2>/dev/null || true

echo "Build complete with rpath fix!"
echo ""
echo "To test without LD_LIBRARY_PATH:"
echo "  cd python && python3 -c \"import cymbal; print('Success')\""
