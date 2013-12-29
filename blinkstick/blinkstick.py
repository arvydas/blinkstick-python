from ._version import  __version__
from colour import Color
import time
import webcolors
import sys

if sys.platform == "win32":
    import pywinusb.hid as hid
    from ctypes import *
else:
    import usb.core
    import usb.util

from random import randint

VENDOR_ID = 0x20a0
PRODUCT_ID = 0x41e5


class BlinkStickException(Exception):
    pass


class BlinkStick(object):
    inverse = False

    def __init__(self, device=None):

        if device:
            self.device = device
            if sys.platform == "win32":
                self.device.open()
                self.reports = self.device.find_feature_reports()
            else:
                self.open_device(device)

            self.bs_serial = self.get_serial()

    def _usb_get_string(self, device, length, index):
        try:
            return usb.util.get_string(device, length, index)
        except usb.USBError:
            # Could not communicate with BlinkStick device
            # attempt to find it again based on serial

            if self._refresh_device():
                return usb.util.get_string(self.device, length, index)
            else:
                raise BlinkStickException("Could not communicate with BlinkStick {0} - it may have been removed".format(self.bs_serial))

    def _usb_ctrl_transfer(self, bmRequestType, bRequest, wValue, wIndex, data_or_wLength):
        if sys.platform == "win32":
            if bmRequestType == 0x20:
                data = (c_ubyte * len(data_or_wLength))(*[c_ubyte(ord(c)) for c in data_or_wLength])
                data[0] = wValue
                if not self.device.send_feature_report(data):
                    if self._refresh_device():
                        self.device.send_feature_report(data)
                    else:
                        raise BlinkStickException("Could not communicate with BlinkStick {0} - it may have been removed".format(self.bs_serial))

            elif bmRequestType == 0x80 | 0x20:
                return self.reports[wValue - 1].get()
        else:
            try:
                return self.device.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength)
            except usb.USBError:
                # Could not communicate with BlinkStick device
                # attempt to find it again based on serial

                if self._refresh_device():
                    return self.device.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength)
                else:
                    raise BlinkStickException("Could not communicate with BlinkStick {0} - it may have been removed".format(self.bs_serial))

    def _refresh_device(self):
        d = find_by_serial(self.bs_serial)
        if d:
            self.device = d.device
            return True

    def get_serial(self):
        """Returns the serial number of device.

        BSnnnnnn-1.0
        ||  |    | |- Software minor version
        ||  |    |--- Software major version
        ||  |-------- Denotes sequential number
        ||----------- Denotes BlinkStick device

        Software version defines the capabilities of the device
        """
        if sys.platform == "win32":
            return self.device.serial_number
        else:
            return self._usb_get_string(self.device, 256, 3)

    def get_manufacturer(self):
        """Get the manufacturer of the device"""
        if sys.platform == "win32":
            return self.device.vendor_name
        else:
            return self._usb_get_string(self.device, 256, 1)


    def get_description(self):
        """Get the description of the device"""
        if sys.platform == "win32":
            return self.device.product_name
        else:
            return self._usb_get_string(self.device, 256, 2)


    def set_color(self, channel=0, index=0, red=0, green=0, blue=0, name=None, hex=None):
        """Set the color to the device as RGB

        Args:
            red: Red color intensity 0 is off, 255 is full red intensity
            green: Green color intensity 0 is off, 255 is full green intensity
            blue: Blue color intensity 0 is off, 255 is full blue intensity
            name: Use CSS colour name as defined here: http://www.w3.org/TR/css3-color/
            hex: Specify color using hexadecimal color value e.g. '#FF3366'
        """

        red, green, blue = self._determine_rgb(red=red, green=green, blue=blue, name=name, hex=hex)

        r = int(round(red, 3))
        g = int(round(green, 3))
        b = int(round(blue, 3))

        if self.inverse:
            r, g, b = 255 - r, 255 - g, 255 - b

        if index == 0 and channel == 0:
            control_string = bytes(bytearray([0, r, g, b]))

            self._usb_ctrl_transfer(0x20, 0x9, 0x0001, 0, control_string)
        else:
            control_string = bytes(bytearray([0, channel, index, r, g, b]))

            self._usb_ctrl_transfer(0x20, 0x9, 0x0005, 0, control_string)


    def _get_color(self):

        """
        Get the current color settings as a grapefruit Color object
        """
        device_bytes = self._usb_ctrl_transfer(0x80 | 0x20, 0x1, 0x0001, 0, 33)
        # Color object requires RGB values in range 0-1, not 0-255
        if self.inverse:
            color = Color(red=float(255 - device_bytes[1]) / 255,
                          green=float(255 - device_bytes[2]) / 255,
                          blue=float(255 - device_bytes[3]) / 255)
        else:
            color = Color(red=float(device_bytes[1]) / 255,
                          green=float(device_bytes[2]) / 255,
                          blue=float(device_bytes[3]) / 255)

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
        return self._get_color().hex

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

    def set_led_data(self, channel, data):
        reportId = 9
        max_leds = 64

        if len(data) <= 8 * 3:
            max_leds = 8
            reportId = 6
        elif len(data) <= 16 * 3:
            max_leds = 16
            reportId = 7
        elif len(data) <= 32 * 3:
            max_leds = 32
            reportId = 8
        elif len(data) <= 64 * 3:
            max_leds = 64
            reportId = 9

        report = [0, channel]

        for i in range(0, max_leds * 3):
            if len(data) > i:
                report.append(data[i])
            else:
                report.append(0)

        self.device.ctrl_transfer(0x20, 0x9, reportId, 0, bytes(bytearray(report)))

    def get_led_data(self):
        #return self.device.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength)
        #device_bytes = self._usb_ctrl_transfer(0x80 | 0x20, 0x1, 0x0005, 0, 6)
        device_bytes = self._usb_ctrl_transfer(0x80 | 0x20, 0x1, 0x0006, 0, 25)
        return device_bytes 

    def set_mode(self, mode):
        """Set device mode

        0 - (default) use R, G and B channels to control single RGB LED
        1 - same as 0, but inverse mode
        2 - control up to 64 WS2812 individual LEDs per each R, G and B channel
        """
        control_string = bytes(bytearray([4, mode]))

        self.device.ctrl_transfer(0x20, 0x9, 0x0004, 0, control_string)

    def get_mode(self):
        """Get current device mode

        0 - (default) use R, G and B channels to control single RGB LED
        1 - same as 0, but inverse mode
        2 - control up to 64 WS2812 individual LEDs per each R, G and B channel
        """

        device_bytes = self.device.ctrl_transfer(0x80 | 0x20, 0x1, 0x0004, 0, 2)

        if (len(device_bytes) >= 2):
            return device_bytes[1]
        else:
            return -1

    def get_info_block1(self):
        """Get the infoblock1 of the device.

        This is a 32 byte array that can contain any data. It's supposed to 
        hold the "Name" of the device making it easier to identify rather than
        a serial number.
        """
        device_bytes = self._usb_ctrl_transfer(0x80 | 0x20, 0x1, 0x0002, 0, 33)
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
        device_bytes = self._usb_ctrl_transfer(0x80 | 0x20, 0x1, 0x0003, 0, 33)
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
        self._usb_ctrl_transfer(0x20, 0x9, 0x0002, 0, self.data_to_message(data))

    def set_info_block2(self, data):
        """Sets the infoblock2 with specified string.
        
        It fills the rest of bytes with zeros.
        """
        self._usb_ctrl_transfer(0x20, 0x9, 0x0003, 0, self.data_to_message(data))

    def set_random_color(self):
        """Sets random color to the device."""
        self.set_color(name="random")

    def turn_off(self):
        self.set_color()

    def pulse(self, red=0, green=0, blue=0, name=None, hex=None, repeats=1, duration=1000, steps=50):
        """
        Morph to the specified color from black and back again.

        @param red: color intensity 0 is off, 255 is full red intensity
        @param green: color intensity 0 is off, 255 is full green intensity
        @param blue: color intensity 0 is off, 255 is full blue intensity
        @param name: Use CSS colour name as defined here:- http://www.w3.org/TR/css3-color/
        @param hex: Specify color using hexadecimal color value e.g. '#FF3366'
        @param repeats: Number of times to pulse the LED
        @param duration: Duration for pulse in milliseconds
        @param steps: Number of gradient steps (default 50)
        """
        r, g, b = self._determine_rgb(red=red, green=green, blue=blue, name=name, hex=hex)

        self.turn_off()
        for x in range(repeats):
            self.morph(red=r, green=g, blue=b, duration=duration, steps=steps)
            self.morph(red=0, green=0, blue=0, duration=duration, steps=steps)

    def blink(self, red=0, green=0, blue=0, name=None, hex=None, repeats=1, delay=500):
        """
        Blink the specified color.

        @param red: color intensity 0 is off, 255 is full red intensity
        @param green: color intensity 0 is off, 255 is full green intensity
        @param blue: color intensity 0 is off, 255 is full blue intensity
        @param name: Use CSS colour name as defined here:- http://www.w3.org/TR/css3-color/
        @param hex: Specify color using hexadecimal color value e.g. '#FF3366'
        @param repeats: Number of times to blink the LED
        @param delay: time in milliseconds to light LED for, and also between blinks
        """
        r, g, b = self._determine_rgb(red=red, green=green, blue=blue, name=name, hex=hex)
        ms_delay = float(delay) / float(1000)
        for x in range(repeats):
            if x:
                time.sleep(ms_delay)
            self.set_color(red=r, green=g, blue=b)
            time.sleep(ms_delay)
            self.set_color()

    def morph(self, red=0, green=0, blue=0, name=None, hex=None, duration=1000, steps=50):
        """
        Morph to the specified color.

        @param red: color intensity 0 is off, 255 is full red intensity
        @param green: color intensity 0 is off, 255 is full green intensity
        @param blue: color intensity 0 is off, 255 is full blue intensity
        @param name: Use CSS colour name as defined here:- http://www.w3.org/TR/css3-color/
        @param hex: Specify color using hexadecimal color value e.g. '#FF3366'
        @param duration: Duration for morph in milliseconds
        @param steps: Number of gradient steps (default 50)
        """

        r_end, g_end, b_end = self._determine_rgb(red=red, green=green, blue=blue, name=name, hex=hex)

        r_start, g_start, b_start = self._get_color().rgb
        r_start, g_start, b_start = 255 * r_start, 255 * g_start, 255 * b_start

        gradient = []

        steps += 1
        for n in range(1, steps):
            d = 1.0 * n / steps
            r = (r_start * (1 - d)) + (r_end * d)
            g = (g_start * (1 - d)) + (g_end * d)
            b = (b_start * (1 - d)) + (b_end * d)

            gradient.append((r, g, b))

        ms_delay = float(duration) / float(1000 * steps)

        self.set_color(red=r_start, green=g_start, blue=b_start)

        for grad in gradient:
            grad_r, grad_g, grad_b = grad

            self.set_color(red=grad_r, green=grad_g, blue=grad_b)
            time.sleep(ms_delay)

        self.set_color(red=r_end, green=g_end, blue=b_end)



    def open_device(self, d):
        """Open device.
        @param d:
        """
        if self.device is None:
            raise BlinkStickException("Could not find BlinkStick...")

        if self.device.is_kernel_driver_active(0):
            try:
                self.device.detach_kernel_driver(0)
            except usb.core.USBError as e:
                raise BlinkStickException("Could not detach kernel driver: %s" % str(e))

        return True

    def get_inverse(self):
        """Get the value of inverse mode
        """
        return self.inverse

    def set_inverse(self, value):
        """Set the value of inverse mode
        @param value: True/False to set the inverse mode
        """
        self.inverse = value


def _find_blicksticks(find_all=True):
    if sys.platform == "win32":
        devices = hid.HidDeviceFilter(vendor_id = VENDOR_ID, product_id = PRODUCT_ID).get_devices()
        if find_all:
            return devices
        elif len(devices) > 0:
            return devices[0]
        else:
            return None

    else:
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
    
    if sys.platform == "win32":
        devices = [d for d in _find_blicksticks()
                   if d.serial_number == serial]
    else:
        devices = [d for d in _find_blicksticks()
                   if usb.util.get_string(d, 256, 3) == serial]
    
    if devices:
        return BlinkStick(device=devices[0])


def get_blinkstick_package_version():
    return __version__
