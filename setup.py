import sys

import versioneer
from setuptools import setup

setup_requires = ['setuptools >= 30.3.0']
if {'build_sphinx'}.intersection(sys.argv):
    setup_requires.append('sphinx')
if {'pytest', 'test', 'ptr'}.intersection(sys.argv):
    setup_requires.append('pytest-runner')

setup(setup_requires=setup_requires,
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass())
