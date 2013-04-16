#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='BlinkStick',
    version='0.3.0',
    author='Arvydas Juskevicius',
    author_email='arvydas@arvydas.co.uk',
    packages=find_packages(),
    scripts=["bin/blinkstick"],
    url='http://pypi.python.org/pypi/BlinkStick/',
    license='LICENSE.txt',
    description='Python package to control BlinkStick USB devices.',
    long_description=read('README.rst'),
    install_requires=[
        "grapefruit",
        "webcolors",
        "pyusb",
        "websocket-client",
        "psutil"
    ],
)
