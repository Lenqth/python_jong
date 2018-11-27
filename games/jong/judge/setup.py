from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

setup(
    ext_modules=[
        Extension("shanten", ["shanten.c"],
                  include_dirs=[numpy.get_include()]),
    ],
)
