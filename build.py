__author__ = 'rcope'

from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize(['PyHT6022Scope/scope_proc.py', 'PyHT6022/LibUsbScope.py',
                             'PyHT6022Scope/app.py']))