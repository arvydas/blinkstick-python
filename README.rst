BlinkStick Python
=================

BlinkStick Python interface to control devices connected to the
computer.

What is BlinkStick? Check it out here:

http://www.blinkstick.com

Requirements
------------

-  Python
-  PyUSB
-  grapefruit - package for color manipulations
-  pyusb - package to access USB devices
-  psutil - only for example-cpu.py
-  websocket-client - only for example-connect.py to connect to
   BlinkStick.com

Installation
------------

Install all required packages with pip:

::

    [sudo] pip install grapefruit pyusb psutil websocket-client

If websocket-client fails to install, please make sure you run the
following command:

::

    sudo apt-get install python-dev

Replace *python-dev* with *python2.7-dev* if you are installing on
Raspberry Pi.

Description
-----------

Description of files:

-  blinkstick.py - main BlinkStick class definition
-  example-info.py - displays information of each BlinkStick
-  example-infoblock.py - read/write info block sample
-  example-off.py - turn all blinksticks off
-  example-random.py - set random color to all BlinkSticks
-  example-cpu.py - displays CPU usage with a BlinkStick (transitions
   from green as 0% to red as 100%)
-  example-connect.py - sample code to connect to BlinkStick.com and
   control it remotely

Running examples:

::

    python example-info.py

Permission problems
-------------------

If the script returns with an error

::

    Access denied (insufficient permissions)

You can either run the script with sudo, for example:

::

    sudo python example-info.py

Or you can add a udev rule to allow any user to access the device
without root permissions with this single command:

::

    echo "SUBSYSTEM==\"usb\", ATTR{idVendor}==\"20a0\", ATTR{idProduct}==\"41e5\", MODE:=\"0666\"" | sudo tee /etc/udev/rules.d/85-blinkstick.rules

Reboot computer after you have added the command and all users will have
permissions to access the device without the need of root permissions.

Maintainers
-----------

-  Arvydas Juskevicius - http://twitter.com/arvydev
-  Rob Berwick - http://twitter.com/robberwick

