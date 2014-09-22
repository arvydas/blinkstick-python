BlinkStick Python
=================

BlinkStick Python interface to control devices connected to the
computer.

What is BlinkStick? It's a smart USB LED pixel. More info about it here:

http://www.blinkstick.com

Source code repository
-------------

https://github.com/arvydas/blinkstick-python

API Reference
-------------

https://arvydas.github.io/blinkstick-python

Requirements
------------

-  Python
-  BlinkStick pip module
-  Libusb for Mac OSX

Requirements Installation
-------------------------

Linux
`````

Install requirement for websocket-client package:

::

    sudo apt-get install python-dev

Note: Replace *python-dev* with *python2.7-dev* if you are installing on Raspberry Pi.

Install pip (Python package management software):

::

    sudo apt-get install python-pip

Mac OS X
````````

Install libusb with `homebrew <http://mxcl.github.io/homebrew/>`_:

::

    brew install libusb

Install pip

:: 

    sudo easy_install pip

Known Errors
^^^^^^^^^^^^

::

    ValueError: No backend available

This means that the Python usb module cannot find your installation of libusb.
It seems to be an issue when you have ``homebrew`` installed somewhere that is
not expected.

It can be mitigated with

::

    sudo ln -s `brew --prefix`/lib/libusb-* /usr/local/lib/

Microsoft Windows
`````````````````

Download and install Python 2.7.x:

http://www.python.org/download/releases/

Install setuptools:

http://www.lfd.uci.edu/~gohlke/pythonlibs/#setuptools

Install pip:

http://www.lfd.uci.edu/~gohlke/pythonlibs/#pip

BlinkStick package Installation
-------------------------------

Linux and Mac OS X
``````````````````

Install blinkstick Python package with pip:

::

    sudo pip install blinkstick


Microsoft Windows
`````````````````

Open commandline environment by using Win+R keyboard shortcut and typing in:

::

    cmd

Assuming that Python was installed into C:\\Python27 folder, type in the 
following into the command window:

::
    
    C:\Python27\Scripts\pip.exe install blinkstick

Code Examples
-------------

Code examples are available in the wiki:

https://github.com/arvydas/blinkstick-python/wiki


Description
-----------

Together with the Python module an additional command line tool is 
installed to control BlinkSticks. 

Note: this tool is not available in Windows. 

Use the following command to see all available options:


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
      --inverse             control BlinkSticks in inverse mode
      --channel=CHANNEL     Select channel
      --index=INDEX         Select index
      --set-color=COLOR     set the color for the device. The value can either be
                            a named color, hex value, 'random' or 'off'.
                            CSS color names are defined
                            http://www.w3.org/TR/css3-color/ e.g. red, green,
                            blue.Specify color using hexadecimal color value e.g.
                            '#FF3366'
      --duration=DURATION   Set duration of transition in milliseconds (use with
                            --morph and --pulse).
      --delay=DELAY         Set time in milliseconds to light LED for (use with
                            --blink).
      --repeats=REPEATS     Number of repetitions (use with --blink and --pulse).
      --blink               Blink LED (requires --set-color, and optionally
                            --delay)
      --pulse               Pulse LED (requires --set-color, and optionally
                            --duration).
      --morph               Morph to specified color (requires --set-color, and
                            optionally --duration).
      --set-infoblock1=INFOBLOCK1
                            set the first info block for the device.
      --set-infoblock2=INFOBLOCK2
                            set the second info block for the device.
      -v, --verbose         Display debug output
      --add-udev-rule       Add udev rule to access BlinkSticks without root
                            permissions. Must be run as root.
      --set-mode=MODE       Set mode for BlinkStick Pro. 0 - default, 1 - inverse,
                            2 - ws2812

Command Line Examples
---------------------

Set random color all BlinkSticks:

::

    blinkstick --set-color random

Set blue color for the blinkstick with serial number BS000001-1.0:

::

    blinkstick --serial BS000001-1.0 --set-color blue

Blink red color twice

::

    blinkstick --set-color red --blink --repeats 2


Blink pulse green color three times

::

    blinkstick --set-color green --pulse --repeats 2

Morph to red, green and blue

::

    blinkstick --set-color red --morph
    blinkstick --set-color gree --morph
    blinkstick --set-color blue --morph

Connect to blinkstick.com and CPU usage command line options are no longer available. Please read this
notice about `module simplification <https://github.com/arvydas/blinkstick-python/wiki/Module-Simplification>`_.

Control individual pixels on BlinkStick Pro. First you will need to set
`BlinkStick Pro mode <http://mxcl.github.io/homebrew/>`_ to WS2812.

::

    blinkstick --set-mode 2


Now you can set color of individual LEDs connected to R, G or B channels.

::

    blinkstick --channel 0 --index 5 --set-color red

More code examples for controlling BlinkStick Pro are available in the 
`wiki <https://github.com/arvydas/blinkstick-python/wiki>`_.

Permission problems in Linux and Mac OS X
-----------------------------------------

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

