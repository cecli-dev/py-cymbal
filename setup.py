from setuptools import setup, Extension
import os

# Check if we have the compiled extension
ext_files = []
if os.path.exists("python/cymbal/_pycymbal.so"):
    ext_files = ["python/cymbal/_pycymbal.so"]

setup(
    name="py-cymbal",
    version="0.1.16",
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
