from _version import __version__
from grapefruit import Color
import time
import webcolors

import usb.core
import usb.util
from random import randint

VENDOR_ID = 0x20a0
PRODUCT_ID = 0x41e5


class BlinkStickException(Exception):
    pass


class BlinkStick(object):
    def __init__(self, device=None):

        if device:
            self.device = device
            self.open_device(device)

    def get_serial(self):
        """Returns the serial number of device.

        BSnnnnnn-1.0
        ||  |    | |- Software minor version
        ||  |    |--- Software major version
        ||  |-------- Denotes sequential number
        ||----------- Denotes BlinkStick device

        Software version defines the capabilities of the device
        """
        return usb.util.get_string(self.device, 256, 3)

    def get_manufacturer(self):
        """Get the manufacturer of the device"""
        return usb.util.get_string(self.device, 256, 1)

    def get_description(self):
        """Get the description of the device"""
        return usb.util.get_string(self.device, 256, 2)

    def set_color(self, red=0, green=0, blue=0, name=None, hex=None):
        """Set the color to the device as RGB

        Args:
            red: Red color intensity 0 is off, 255 is full red intensity
            green: Green color intensity 0 is off, 255 is full green intensity
            blue: Blue color intensity 0 is off, 255 is full blue intensity
            name: Use CSS colour name as defined here: http://www.w3.org/TR/css3-color/
            hex: Specify color using hexadecimal color value e.g. '#FF3366'
        """

        red, green, blue = self._determine_rgb(red=red, green=green, blue=blue, name=name, hex=hex)

        self.device.ctrl_transfer(0x20, 0x9, 0x0001, 0, "\x00" + chr(int(round(red, 3)))
                                                        + chr(int(round(green, 3)))
                                                        + chr(int(round(blue, 3))))

    def _get_color(self):

        """
        Get the current color settings as a grapefruit Color object
        """
        device_bytes = self.device.ctrl_transfer(0x80 | 0x20, 0x1, 0x0001, 0, 33)
        # Color object requires RGB values in range 0-1, not 0-255
        color = Color.NewFromRgb(float(device_bytes[1]) / 255,
                                 float(device_bytes[2]) / 255,
                                 float(device_bytes[3]) / 255)

        return color

    def _determine_rgb(self, red=0, green=0, blue=0, name=None, hex=None):

        try:
            if name:
                # Special case for name="random"
                if name is "random":
                    red = randint(0, 255)
                    green = randint(0, 255)
                    blue = randint(0, 255)
                else:
                    red, green, blue = webcolors.name_to_rgb(name)
            elif hex:
                red, green, blue = webcolors.hex_to_rgb(hex)
        except ValueError:
            red = green = blue = 0

        # TODO - do smarts to determine input type from red var in case it is not int

        return red, green, blue

    def _get_color_rgb(self):
        r, g, b = self._get_color().rgb
        return int(r * 255), int(g * 255), int(b * 255)

    def _get_color_hex(self):
        return self._get_color().html

    def get_color(self, color_format='rgb'):

        """
        Get the current device color in the defined format. Default format is (r,g,b).

        Currently supported formats:
        rgb (default) - Returns values as 3-tuple (r,g,b)
        hex - returns current device color as hexadecimal string

        Example:
            b = BlinkStick.find_first()
            b.set_color(red=255,0,0)
            # Get color as rbg tuple
            (r,g,b) = b.get_color() # (255,0,0)
            # Get color as hex string
            hex = b.get_color() # '#ff0000'

        """

        # Attempt to find a function to return the appropriate format
        get_color_func = getattr(self, "_get_color_%s" % color_format, self._get_color_rgb)
        if callable(get_color_func):
            return get_color_func()
        else:
            # Should never get here, as we should always default to self._get_color_rgb
            raise BlinkStickException("Could not return current color in format %s" % color_format)


    def get_info_block1(self):
        """Get the infoblock1 of the device.

        This is a 32 byte array that can contain any data. It's supposed to 
        hold the "Name" of the device making it easier to identify rather than
        a serial number.
        """
        device_bytes = self.device.ctrl_transfer(0x80 | 0x20, 0x1, 0x0002, 0, 33)
        result = ""
        for i in device_bytes[1:]:
            if i == 0:
                break
            result += chr(i)
        return result

    def get_info_block2(self):
        """Get the infoblock2 of the device.

        This is a 32 byte array that can contain any data.
        """
        device_bytes = self.device.ctrl_transfer(0x80 | 0x20, 0x1, 0x0003, 0, 33)
        result = ""
        for i in device_bytes[1:]:
            if i == 0:
                break
            result += chr(i)
        return result

    def data_to_message(self, data):
        """Helper method to convert a string to byte array of 32 bytes. 

        Args: 
            data (str): The data to convert to byte array

        Returns:
            byte[32]: array
        
        It fills the rest of bytes with zeros.
        """
        bytes = [1]
        for c in data:
            bytes.append(ord(c))

        for i in range(32 - len(data)):
            bytes.append(0)

        return bytes

    def set_info_block1(self, data):
        """Sets the infoblock1 with specified string.
        
        It fills the rest of bytes with zeros.
        """
        self.device.ctrl_transfer(0x20, 0x9, 0x0002, 0, self.data_to_message(data))

    def set_info_block2(self, data):
        """Sets the infoblock2 with specified string.
        
        It fills the rest of bytes with zeros.
        """
        self.device.ctrl_transfer(0x20, 0x9, 0x0003, 0, self.data_to_message(data))

    def set_random_color(self):
        """Sets random color to the device."""
        self.set_color(name="random")

    def turn_off(self):
        self.set_color()

    def pulse(self, red=0, green=0, blue=0, name=None, hex=None, duration=1000, steps=50):
        """
        Morph to the specified color from black and back again.
        :param red: color intensity 0 is off, 255 is full red intensity
        :param green: color intensity 0 is off, 255 is full green intensity
        :param blue: color intensity 0 is off, 255 is full blue intensity
        :param name: Use CSS colour name as defined here:- http://www.w3.org/TR/css3-color/
        :param hex: Specify color using hexadecimal color value e.g. '#FF3366'
        :param duration: Duration for pulse in milliseconds
        :param steps: Number of gradient steps (default 50)
        """
        r, g, b = self._determine_rgb(red=red, green=green, blue=blue, name=name, hex=hex)

        self.turn_off()
        self.morph(red=r, green=g, blue=b, duration=duration, steps=steps)
        self.morph(red=0, green=0, blue=0, duration=duration, steps=steps)

    def blink(self, red=0, green=0, blue=0, name=None, hex=None, repeats=1, delay=500):
        """
        Blink the specified color.
        :param red: color intensity 0 is off, 255 is full red intensity
        :param green: color intensity 0 is off, 255 is full green intensity
        :param blue: color intensity 0 is off, 255 is full blue intensity
        :param name: Use CSS colour name as defined here:- http://www.w3.org/TR/css3-color/
        :param hex: Specify color using hexadecimal color value e.g. '#FF3366'
        :param repeats: Number of times to blink the LED
        :param delay: time in milliseconds to light LED for, and also between blinks
        """
        r, g, b = self._determine_rgb(red=red, green=green, blue=blue, name=name, hex=hex)
        ms_delay = float(delay)/float(1000)
        for x in range(repeats):
            if x:
                time.sleep(ms_delay)
            self.set_color(red=r, green=g, blue=b)
            time.sleep(ms_delay)
            self.set_color()

    def morph(self, red=0, green=0, blue=0, name=None, hex=None, duration=1000, steps=50):
        """
        Morph to the specified color.
        :param red: color intensity 0 is off, 255 is full red intensity
        :param green: color intensity 0 is off, 255 is full green intensity
        :param blue: color intensity 0 is off, 255 is full blue intensity
        :param name: Use CSS colour name as defined here:- http://www.w3.org/TR/css3-color/
        :param hex: Specify color using hexadecimal color value e.g. '#FF3366'
        :param duration: Duration for morph in milliseconds
        :param steps: Number of gradient steps (default 50)
        """
        r, g, b = self._determine_rgb(red=red, green=green, blue=blue, name=name, hex=hex)

        current_color = self._get_color()

        target_color = Color.NewFromRgb(float(r) / 255, float(g) / 255, float(b) / 255)

        gradient_list = current_color.Gradient(target_color, steps=steps)

        for grad in gradient_list:
            grad_r, grad_g, grad_b = grad.rgb
            self.set_color(grad_r * 255, grad_g * 255, grad_b * 255)
            ms_delay = float(duration)/float(1000 * steps)
            time.sleep(ms_delay)

    #     set target colour

        self.set_color(red=r, green=g, blue=b)

    def open_device(self, d):
        """Open device.
        :param d:
        """
        if self.device is None:
            raise BlinkStickException("Could not find BlinkStick...")

        if self.device.is_kernel_driver_active(0):
            try:
                self.device.detach_kernel_driver(0)
            except usb.core.USBError as e:
                raise BlinkStickException("Could not detach kernel driver: %s" % str(e))

        return True


def _find_blicksticks(find_all=True):
    return usb.core.find(find_all=find_all, idVendor=VENDOR_ID, idProduct=PRODUCT_ID)


def find_all():
    """Find all attached BlinkStick devices.

    Returns a list of BlinkStick objects or None if no devices found
    """
    return [BlinkStick(device=d) for d in _find_blicksticks()]


def find_first():
    """Find first attached BlinkStick.

    Returns BlinkStick object or None if no devices are found
    """
    d = _find_blicksticks(find_all=False)

    if d:
        return BlinkStick(device=d)


def find_by_serial(serial=None):
    """Find BlinkStick device based on serial number.

    Returns BlinkStick object or None if no devices found"""
    devices = [d for d in _find_blicksticks()
               if usb.util.get_string(d, 256, 3) == serial]

    if devices:
        return BlinkStick(device=devices[0])

def get_blinkstick_package_version():
    return __version__
