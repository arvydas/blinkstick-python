BlinkStick Python
=================

BlinkStick Python interface to control devices connected to the computer.

What is BlinkStick? Check it out here:

http://www.blinkstick.com

Requirements
------------

* Python
* PyUSB

Download and install PyUSB from here:

http://sourceforge.net/projects/pyusb/files/latest/download

```sh
[sudo] python setup.py install
```

Description
-----------

Description of files:

* blinkstick.py - main BlinkStick class definition
* example-info.py - displays information of each BlinkStick
* example-infoblock.py - read/write info block sample 
* example-off.py - turn all blinksticks off
* example-random.py - set random color to all blinksticks

Running examples:

```sh
python example-info.py
```
