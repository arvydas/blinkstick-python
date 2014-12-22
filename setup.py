#!/usr/bin/env python
import os
import re
import sys
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


PKG = 'blinkstick'
VERSIONFILE = os.path.join(PKG, "_version.py")
verstr = "unknown"
try:
    verstrline = open(VERSIONFILE, "rt").read()
except EnvironmentError:
    pass  # Okay, there is no version file.
else:
    VSRE = r"(\d+\.\d+\.\d+)"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
    else:
        print("unable to find version in {0}").format(VERSIONFILE)
        raise RuntimeError("if {0}.py exists, it is required to be well-formed".format(VERSIONFILE))

if sys.platform == "win32":
    os_requires = [
        "pywinusb"
    ]
else:
    os_requires = [
        "pyusb==1.0.0b1"
    ]

setup(
    name='BlinkStick',
    version=verstr,
    author='Arvydas Juskevicius',
    author_email='arvydas@arvydas.co.uk',
    packages=find_packages(),
    scripts=["bin/blinkstick"],
    url='http://pypi.python.org/pypi/BlinkStick/',
    license='LICENSE.txt',
    description='Python package to control BlinkStick USB devices.',
    long_description=read('README.rst'),
    install_requires=os_requires,
)
