"""
Setup script for building Elara's C++ native extensions.

This script configures the build process for high-performance
C++ components using pybind11.
"""

from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
import pybind11

# Define the C++ extension module
ext_modules = [
    Pybind11Extension(
        "elara.native.elara_native",
        [
            "elara/native/pybind/bindings.cpp",
            # Add more C++ source files here as needed
        ],
        include_dirs=[
            pybind11.get_include(),
            "elara/native/src",
        ],
        language='c++',
        cxx_std=17,  # Use C++17 standard
    ),
]

setup(
    name="elara",
    version="0.1.0",
    description="A world-class poker analysis engine",
    author="Elara Team",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.8",
) 