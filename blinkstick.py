#!/usr/bin/python

import usb.core
import usb.util
from time import time, sleep
from collections import namedtuple
from random import randint

Color = namedtuple("Color", "R G B")

class BlinkStick(object):
    VENDOR_ID = 0x20a0
    PRODUCT_ID = 0x41e5

    def __init__(self):
        return None

    @classmethod
    def find_all(cls):
        """A class method to find all BlinkStick devices.

        Returns a list of BlinkStick objects.
        """
        for d in usb.core.find(find_all=True, idVendor=cls.VENDOR_ID, idProduct=cls.PRODUCT_ID):
            bstick = BlinkStick()
            bstick.open_device(d)
            yield bstick

    @classmethod
    def find_first(cls):
        """A class method to find first BlinkStick.

        Returns first device found as BlinkStick object.
        """
        d = usb.core.find(idVendor=cls.VENDOR_ID, idProduct=cls.PRODUCT_ID)
        if d is None:
            return None
        else:
            bstick = BlinkStick()
        bstick.open_device(d)

        return bstick

    @classmethod
    def find_by_serial(cls, serial):
        """A class method to find BlinkStick device based on serial number."""
        for d in usb.core.find(find_all=True, idVendor=cls.VENDOR_ID, idProduct=cls.PRODUCT_ID):
            if serial == usb.util.get_string(d, 256, 3):
                bstick = BlinkStick()
                bstick.open_device(d)
                return bstick

        return None

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

    def set_color(self, r, g, b):
        """Set the color to the device as RGB

        Args:
            r (byte): Red color intensity 0 is off, 255 is full red intensity
            g (byte): Green color intensity 0 is off, 255 is full green intensity
            b (byte): Blue color intensity 0 is off, 255 is full blue intensity
        """
        self.device.ctrl_transfer(0x20, 0x9, 0x0001, 0, "\x00" + chr(r) + chr(g) + chr(b))

    def get_color(self):
        """Get the color to the device as Color namedtuple

        Returns:
            Color - the current color of the device

        Example:
            b = BlinkStick.find_first()
            color = b.get_color()
            print color.R
            print color.G
            print color.B
        """
        bytes = self.device.ctrl_transfer(0x80 | 0x20, 0x1, 0x0001, 0, 33)
        return Color(bytes[1], bytes[2], bytes[3])

    def get_color_string(self):
        """Get the color to the device as Color namedtuple

        Returns:
            String - current color of the device as HEX encoded string #rrggbb

        Examples:
            #FF0000 - red
            #00FF00 - green
            #0000FF - blue
            #008000 - 50% intensity green
        """
        c = self.get_color()
        return '#{0}{1}{2}'.format('%02X'%c.R, '%02X'%c.G, '%02X'%c.B)

    def get_info_block1(self):
        """Get the infoblock1 of the device.

        This is a 32 byte array that can contain any data. It's supposed to 
        hold the "Name" of the device making it easier to identify rather than
        a serial number.
        """
        bytes = self.device.ctrl_transfer(0x80 | 0x20, 0x1, 0x0002, 0, 33)
        result = ""
        for i in bytes[1:]:
            if i == 0:
                break
            result = result + chr(i)
        return result

    def get_info_block2(self):
        """Get the infoblock2 of the device.

        This is a 32 byte array that can contain any data.
        """
        bytes = self.device.ctrl_transfer(0x80 | 0x20, 0x1, 0x0003, 0, 33)
        result = ""
        for i in bytes[1:]:
            if i == 0:
                break
            result = result + chr(i)
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
        self.set_color(randint(0, 255), randint(0, 255), randint(0, 255))

    def turn_off(self):
        self.set_color(0, 0, 0)

    def pulse_color(self, r, g, b):
        """Pulses specified RGB color."""
        cr = 0
        cg = 0
        cb = 0

        for i in range(max(r, g, b)):
            if cr < r:
                 cr = cr + 1
            if cg < g:
                 cg = cg + 1
            if cb < b:
                 cb = cb + 1

            set_color(cr, cg, cb)

        cr = r
        cg = g
        cb = b

        while (cr > 0 or cg > 0 or cb > 0):
            if cr > 0:
                cr = cr - 1
            if cb > 0:
                cb = cb - 1
            if cg > 0:
                cg = cg - 1

            set_color(cr, cg, cb)

    def open_device(self, d):
        """Open device."""
        self.device = d
        return self.open()

    def open(self):
        """Open currently assigned device."""
        if self.device is None:
            sys.exit("Could not find BlinkStick...")

        if self.device.is_kernel_driver_active(0):
            try:
                self.device.detach_kernel_driver(0)
            except usb.core.USBError as e:
                sys.exit("Could not detatch kernel driver: %s" % str(e))

        try:
            self.device.set_configuration()
            self.device.reset()
        except usb.core.USBError as e:
            sys.exit("Could not set configuration: %s" % str(e))

        return True
