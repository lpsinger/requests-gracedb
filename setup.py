import sys

import versioneer
import pkg_resources
from setuptools import setup


def get_requirements(filename):
    with open(filename, 'r') as f:
        return [str(r) for r in pkg_resources.parse_requirements(
            line for line in f if not line.startswith('-r'))]


setup_requires = ['setuptools >= 30.3.0']
if {'build_sphinx'}.intersection(sys.argv):
    setup_requires.append('sphinx')
if {'pytest', 'test', 'ptr'}.intersection(sys.argv):
    setup_requires.append('pytest-runner')

setup(setup_requires=setup_requires,
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass())
