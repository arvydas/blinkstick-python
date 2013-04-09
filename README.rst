BlinkStick Python
=================

BlinkStick Python interface to control devices connected to the
computer.

What is BlinkStick? It's a DIY USB RGB LED device. More info 
about it here:

http://www.blinkstick.com

Requirements
------------

-  Python
-  BlinkStick pip module

Depends on modules
------------------

-  webcolors
-  grapefruit - package for color manipulations
-  pyusb - package to access USB devices
-  psutil - only for example-cpu.py
-  websocket-client - only for example-connect.py to connect to
   BlinkStick.com

Installation
------------

Install all required packages with pip:

::

    [sudo] pip install blinkstick


If you would like to run the example scripts, you may also need to install
the extra dependencies

::

    [sudo] pip install psutil websocket-client

If websocket-client fails to install, please make sure you run the
following command:

::

    sudo apt-get install python-dev

Replace *python-dev* with *python2.7-dev* if you are installing on
Raspberry Pi.

Description
-----------

Description of files:

-  /blinkstick - main BlinkStick module
-  /bin/blinkstick-info.py - displays information of each BlinkStick
-  /bin/blinkstick-infoblock.py - read/write info block sample
-  /bin/blinkstick-off.py - turn all blinksticks off
-  /bin/blinkstick-random.py - set random color to all BlinkSticks
-  /bin/blinkstick-cpu.py - displays CPU usage with a BlinkStick (transitions
   from green as 0% to red as 100%)
-  /bin/blinkstick-connect.py - sample code to connect to BlinkStick.com and
   control it remotely

Running examples:

::

    [sudo] blinkstick-info.py

Permission problems
-------------------

If the script returns with an error

::

    Access denied (insufficient permissions)

You can either run the script with sudo, for example:

::

    sudo blinkstick-info.py

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

