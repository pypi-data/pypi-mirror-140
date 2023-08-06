from Cython.Build import cythonize
from distutils.extension import Extension
import numpy

extensions = [
    Extension("*", ["cython_packages/*.pyx"],
        include_dirs=[numpy.get_include()],
    ),
]

def build(setup_kwargs):
    setup_kwargs.update(
        {"ext_modules": cythonize(extensions)},
    )