#!/usr/bin/env python

import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

def dune_testtools_scripts():
    return ['./scripts/analysis.py',
            './scripts/expand_metaini.py',
            './scripts/extract_static.py',
            './scripts/has_static_section.py',
            './wrapper/convergencetest.py',
            './wrapper/execute.py',
            './wrapper/execute_parallel.py',
            './wrapper/vtkcompare.py']

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(name='dune-testtools',
      version='0.1',
      description='Python testtools for systemtesting in DUNE',
      author='Dominic Kempf <dominic.kempf@iwr.uni-heidelberg.de>, Timo Koch <timo.koch@iws.uni-stuttgart.de>',
      author_email='no_mailinglist_yet@dune-testtools.de',
      url='http://conan2.iwr.uni-heidelberg.de/git/quality/dune-testtools',
      packages=['dune_testtools', 'dune_testtools.wrapper'],
      install_requires=['pyparsing'],
      tests_require=['pytest'],
      cmdclass={'test': PyTest},
      scripts=dune_testtools_scripts())
