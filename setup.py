from distutils.core import setup

setup(
    name='BlinkStick',
    version='0.1.0',
    author='Arvydas Juskevicius',
    author_email='arvydas@arvydas.co.uk',
    packages=['blinkstick'],
    scripts=["bin/blinkstick-connect.py",
             "bin/blinkstick-cpu.py",
             "bin/blinkstick-find.py",
             "bin/blinkstick-info.py",
             "bin/blinkstick-infoblock.py",
             "bin/blinkstick-off.py",
             "bin/blinkstick-random.py"],
    url='http://pypi.python.org/pypi/BlinkStick/',
    license='LICENSE.txt',
    description='Python package to control BlinkStick USB devices.',
    long_description=open('README.rst').read(),
    install_requires=[
        "grapefruit",
        "pyusb"
        ],
    )