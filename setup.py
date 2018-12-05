#!usr/bin/env python

from setuptools import setup,find_packages

setup(
    name="games.jong",
    version="0.1.0",
    packages = find_packages() ,
    install_requires=[],
    extras_require={
        "develop": []
    },
    entry_points={
    }
)

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

setup(
    cmdclass={'build_ext': build_ext},
    ext_modules=[Extension("games.jong.judge.shanten", ["./games/jong/judge/shanten.py"])],
    include_dirs=[numpy.get_include()],
    extra_compile_args=['-fopenmp'],
    extra_link_args=['-fopenmp'],
)