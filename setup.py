__author__ = 'Robert Cope'
__version__ = '0.0.2'

from setuptools import setup
import os

setup(name='Python Hantek 6022BE Wrapper',
      author=__author__,
      author_email='rpcope1@gmail.com',
      description='A Python API for using the inexpensive Hantek 6022BE USB Oscilloscope in Windows and Linux',
      version=__version__,
      license='GPLv2',
      packages=['PyHT6022', 'PyHT6022.HantekFirmware'],
      package_data={'PyHT6022': [os.path.join('HantekSDK', 'HTMarch.dll'),
                                 os.path.join('HantekSDK', 'HTDisplayDll.dll')]},
      include_package_data=True,
      install_requires=['libusb1'])