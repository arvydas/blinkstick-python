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

Installation
------------

Install blinkstick Python package with pip:

::

    [sudo] pip install blinkstick

If websocket-client fails to install, please make sure you run the
following command:

::

    sudo apt-get install python-dev

Replace *python-dev* with *python2.7-dev* if you are installing on
Raspberry Pi.

Description
-----------

Together with the Python module an additional command line tool is 
installed to control BlinkSticks. Use the following command to see all
available options:

::

    blinkstick -h

::

    Usage: blinkstick [options]

    Options:
      -h, --help            show this help message and exit
      -i, --info            display BlinkStick info
      -s SERIAL, --serial=SERIAL
                            select device by serial number. If unspecified, action
                            will be performed on all BlinkSticks.
      --set-color=COLOR     set the color for the device. The value can either be
                            a named color, hex value, 'random' or 'off'.
                            CSS color names are defined
                            http://www.w3.org/TR/css3-color/ e.g. red, green,
                            blue.Specify color using hexadecimal color value e.g.
                            '#FF3366'
      --set-infoblock1=INFOBLOCK1
                            set the first info block for the device.
      --set-infoblock2=INFOBLOCK2
                            set the second info block for the device.
      --cpu-usage           Use BlinkStick to display CPU usage.
      --connect=ACCESS_CODE
                            Connect to blinkstick.com and control the device
                            remotely.
      -v, --verbose         Display debug output
      --add-udev-rule       Add udev rule to access BlinkSticks without root
                            permissions. Must be run as root.

Command Line Examples
---------------------

Set random color all BlinkSticks:

::

    blinkstick --set-color random

Set blue color for the blinkstick with serial number BS000001-1.0:

::

    blinkstick --serial BS000001-1.0 --set-color blue

Connect to blinkstick.com with access code:

::

    blinkstick --connect 9ad4ca313f41330cad6c219d

Use BlinkStick to display CPU usage:

::

    blinkstick --cpu-usage

Code Examples
-------------

Code examples are available in the wiki:

https://github.com/arvydas/blinkstick-python/wiki


Permission problems
-------------------

If the script returns with an error

::

    Access denied (insufficient permissions)

You can either run the script with sudo, for example:

::

    sudo blinkstick --set-color random 

Or you can add a udev rule to allow any user to access the device
without root permissions with this single command.

::

    sudo blinkstick --add-udev-rule

There is also another equivalent command that does exactly the same thing:

::

    echo "SUBSYSTEM==\"usb\", ATTR{idVendor}==\"20a0\", ATTR{idProduct}==\"41e5\", MODE:=\"0666\"" | sudo tee /etc/udev/rules.d/85-blinkstick.rules

Reboot computer after you have added the command and all users will have
permissions to access the device without the need of root permissions.

Maintainers
-----------

-  Arvydas Juskevicius - http://twitter.com/arvydev
-  Rob Berwick - http://twitter.com/robberwick

