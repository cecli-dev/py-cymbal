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
