#!/usr/bin/env python

import re
from setuptools import setup

VERSIONFILE="porc/version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^VERSION = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    VERSION = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(name='porc',
      version=VERSION,
      description='Asynchronous Orchestrate.io Interface',
      author='Max Thayer',
      author_email='max@orchestrate.io',
      url='https://github.com/orchestrate-io/porc',
      packages=['porc'],
      license='ASLv2',
      install_requires=[
          'requests-futures==0.9.4',
          'vcrpy==1.1.0',
          'lucene-querybuilder==0.2'
      ],
      test_suite="tests",
      classifiers=[
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4'
      ],
      )
