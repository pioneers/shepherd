from setuptools import Extension, setup
from Cython.Build import cythonize
import sys

sourcefiles = [
    "shm_wrapper.c",
    "shepherd_util.c",
    "shm_api.pyx"
]

if sys.platform == 'linux':
    libraries = ['rt']
elif sys.platform == 'darwin':
    libraries = []
else:
    raise NotImplementedError("Cython not implemented for OS other than Linux or MacOS")

setup(
    name="shm_api",
    ext_modules = cythonize([
        Extension("shm_api", sources=sourcefiles, libraries=libraries)
    ], compiler_directives={'language_level' : '3', 'boundscheck': False}),
    zip_safe=False,
)
