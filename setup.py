#!/usr/bin/env python

import distutils.core

distutils.core.setup(
    name='openbci',
    version='0.1',
    url='http://github.com/strob/openbci-python',
    description='python module for interfacing with OpenBCI',
    author='Robert M Ochshorn',
    author_email='rmo@numm.org',
    packages=['openbci'],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        ],
    license='GPL')
