#!/usr/bin/env python

from distutils.core import setup
import re

from setuptools import setup, find_packages
import sys

long_description = """
A Pure-Python library built as a PDF toolkit.  It is capable of:

- extracting document information (title, author, ...)
- splitting documents page by page
- merging documents page by page
- cropping pages
- merging multiple pages into a single page
- encrypting and decrypting PDF files
- and more!

By being Pure-Python, it should run on any Python platform without any
dependencies on external libraries.  It can also work entirely on StringIO
objects rather than file streams, allowing for PDF manipulation in memory.
It is therefore a useful tool for websites that manage or manipulate PDFs.
"""

VERSIONFILE="XCCPyPDF/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE))

setup(
        name="XCCPyPDF",
        version=verstr,
        description="PDF toolkit",
        long_description=long_description,
        author="white.tie",
        author_email="",
        maintainer="Phaseit, Inc.",
        maintainer_email="",
        url="",
        classifiers = [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Libraries :: Python Modules",
            ],
        packages=["XCCPyPDF"],
    )
