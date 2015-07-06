#!/usr/bin/env python

from distutils.core import setup

setup(name='DUNETesttools',
      version='0.1',
      description='Python testtools for systemtesting in DUNE',
      author='Dominic Kempf <dominic.kempf@iwr.uni-heidelberg.de>, Timo Koch <timo.koch@iws.uni-stuttgart.de>',
      author_email='no_mailinglist_yet@dune-testtools.de',
      url='http://conan2.iwr.uni-heidelberg.de/git/dominic/dune-testtools',
      packages=['dune_testtools', 'dune_testtools.wrapper', 'dune_testtools.tests'],
      package_dir={'dune_testtools.tests': 'dune_testtools/tests'},
      package_data={'dune_testtools.tests': ['*.ini', '*.vtu']},
      requires=['pyparsing', 'xml.etree.ElementTree'],
     )