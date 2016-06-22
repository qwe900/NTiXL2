import os
from setuptools import setup, find_packages

PATH = os.path.dirname(__file__)

def read(fname):
    return open(os.path.join(PATH, fname)).read()

setup(
      name='ntixl2',
      version='1.0',
      description="A Python API for the Remote Measurement usage of the NTi XL2 sound level meter.",
      long_description=read('README.md'),
      author='esr',
      author_email='',
      url='aaa',
      license='LICENSE',
      packages=find_packages(exclude=["tests"]),
      package_dir = {'ntixl2': 'ntixl2'}
      )
