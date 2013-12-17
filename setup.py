#!/usr/bin/env python
import sys

SETUPTOOLS_VERSION = '2.0.1'

try:
    from setuptools.version import __version__
    assert __version__ == SETUPTOOLS_VERSION
except (ImportError, AssertionError) as e:
    print >> sys.stderr, (
    "The required version of setuptools (==%s) is not available.\n"
    "Please install a more recent version first, using 'pip install --upgrade"
    " setuptools'.") % SETUPTOOLS_VERSION
    sys.exit(2)

from setuptools import setup, find_packages

from mod_utils.get_version import get_version
from mod_utils.pip import get_pip_git_requirements, get_pip_requirements


setup(
      name='w3af',

      version=get_version(),
      license = 'GNU General Public License v2 (GPLv2)',
      platforms='Linux',
      
      description=('w3af is an open source web application security scanner.'),
      long_description=file('README.rst').read(),
      
      author='Andres Riancho',
      author_email='andres.riancho@gmail.com',
      url='https://github.com/andresriancho/w3af/',
      
      packages=find_packages(where='.', exclude=['tests*', 'mod_utils*']),

      # include everything in source control, depends on setuptools_git==1.0
      include_package_data = True,

      # This allows w3af plugins to read the data_files which we deploy with
      # data_files.
      zip_safe = False,

      # Run the module tests using nose
      test_suite = 'nose.collector',
      
      # Require at least the easiest PIP requirements from w3af
      setup_requires = ['setuptools==%s' % SETUPTOOLS_VERSION,
                        "setuptools_git==1.0"],
      install_requires = get_pip_requirements(),
      dependency_links = get_pip_git_requirements(),
      
      # https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Security'
        ],
      
     )
