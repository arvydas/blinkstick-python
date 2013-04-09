from grapefruit import Color
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

        try:
            if name:
                red, green, blue = webcolors.name_to_rgb(name)
            elif hex:
                red, green, blue = webcolors.hex_to_rgb(hex)
        except ValueError:
            red = green = blue = 0

        self.device.ctrl_transfer(0x20, 0x9, 0x0001, 0, "\x00" + chr(red) + chr(green) + chr(blue))

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

    def get_color(self):
        """Get the color to the device as Color namedtuple

        Returns:
            Color - the current color of the device as a 3-tuple of integers

        Example:
            b = BlinkStick.find_first()
            (r,g,b) = b.get_color()
            print r
            print g
            print b
        """
        r, g, b = self._get_color().rgb
        return int(r * 255), int(g * 255), int(b * 255)

    def get_color_string(self):
        """Get the current device color as hexadecimal string

        Returns:
            String - current color of the device as HEX encoded string #rrggbb

        Examples:
            #FF0000 - red
            #00FF00 - green
            #0000FF - blue
            #008000 - 50% intensity green
        """
        return self._get_color().html

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
        self.set_color(red=randint(0, 255), green=randint(0, 255), blue=randint(0, 255))

    def turn_off(self):
        self.set_color()

    def pulse_color(self, red=0, green=0, blue=0):
        """Pulses specified RGB color."""
        cr = 0
        cg = 0
        cb = 0

        for i in range(max(red, green, blue)):
            if cr < red:
                cr += 1
            if cg < green:
                cg += 1
            if cb < blue:
                cb += 1

            self.set_color(red=cr, green=cg, blue=cb)

        cr = red
        cg = green
        cb = blue

        while cr > 0 or cg > 0 or cb > 0:
            if cr > 0:
                cr -= 1
            if cb > 0:
                cb -= 1
            if cg > 0:
                cg -= 1

            self.set_color(red=cr, green=cg, blue=cb)

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

        try:
            self.device.set_configuration()
            self.device.reset()
        except usb.core.USBError as e:
            raise BlinkStickException("Could not set configuration: %s" % str(e))

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
