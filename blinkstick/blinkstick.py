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
    error_reporting = True

    def __init__(self, device=None, error_reporting=True):

        self.error_reporting = error_reporting

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

    def set_error_reporting(self, error_reporting):
        self.error_reporting = error_reporting

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
            report_id = 0x0001
        else:
            control_string = bytes(bytearray([5, channel, index, r, g, b]))
            report_id = 0x0005

        if self.error_reporting:
            self._usb_ctrl_transfer(0x20, 0x9, report_id, 0, control_string)
        else:
            try:
                self._usb_ctrl_transfer(0x20, 0x9, report_id, 0, control_string)
            except Exception as e:
                pass

    def _get_color(self, index=0):

        """
        Get the current color settings as a grapefruit Color object
        """
        if index == 0:
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
        else:
            data = self.get_led_data(index + 1)

            # Color object requires RGB values in range 0-1, not 0-255
            color = Color(red=float(data[index * 3 + 1]) / 255,
                          green=float(data[index * 3]) / 255,
                          blue=float(data[index * 3 + 2]) / 255)

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

    def _get_color_rgb(self, index=0):
        r, g, b = self._get_color(index).rgb
        return int(r * 255), int(g * 255), int(b * 255)

    def _get_color_hex(self, index=0):
        return self._get_color(index).hex

    def get_color(self, channel=0, index=0, color_format='rgb'):

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
            return get_color_func(index)
        else:
            # Should never get here, as we should always default to self._get_color_rgb
            raise BlinkStickException("Could not return current color in format %s" % color_format)

    def _determine_report_id(self, led_count):
        report_id = 9
        max_leds = 64

        if led_count <= 8 * 3:
            max_leds = 8
            report_id = 6
        elif led_count <= 16 * 3:
            max_leds = 16
            report_id = 7
        elif led_count <= 32 * 3:
            max_leds = 32
            report_id = 8
        elif led_count <= 64 * 3:
            max_leds = 64
            report_id = 9

        return report_id, max_leds

    def set_led_data(self, channel, data):
        report_id, max_leds = self._determine_report_id(len(data))

        report = [0, channel]

        for i in range(0, max_leds * 3):
            if len(data) > i:
                report.append(data[i])
            else:
                report.append(0)

        self.device.ctrl_transfer(0x20, 0x9, report_id, 0, bytes(bytearray(report)))

    def get_led_data(self, count):
        report_id, max_leds = self._determine_report_id(count)

        device_bytes = self._usb_ctrl_transfer(0x80 | 0x20, 0x1, report_id, 0, max_leds * 3 + 1)

        return device_bytes[2: 2 + count * 3]

    def set_mode(self, mode):
        """Set device mode

        0 - (default) use R, G and B channels to control single RGB LED
        1 - same as 0, but inverse mode
        2 - control up to 64 WS2812 individual LEDs per each R, G and B channel
        3 - WS2812 mirror for BlinkStick Nano
        """
        control_string = bytes(bytearray([4, mode]))

        self.device.ctrl_transfer(0x20, 0x9, 0x0004, 0, control_string)

    def get_mode(self):
        """Get current device mode

        0 - (default) use R, G and B channels to control single RGB LED
        1 - same as 0, but inverse mode
        2 - control up to 64 WS2812 individual LEDs per each R, G and B channel
        3 - WS2812 mirror for BlinkStick Nano
        """

        device_bytes = self.device.ctrl_transfer(0x80 | 0x20, 0x1, 0x0004, 0, 2)

        if len(device_bytes) >= 2:
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

    def pulse(self, channel=0, index=0, red=0, green=0, blue=0, name=None, hex=None, repeats=1, duration=1000, steps=50):
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
            self.morph(channel=channel, index=index, red=r, green=g, blue=b, duration=duration, steps=steps)
            self.morph(channel=channel, index=index, red=0, green=0, blue=0, duration=duration, steps=steps)

    def blink(self, channel=0, index=0, red=0, green=0, blue=0, name=None, hex=None, repeats=1, delay=500):
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
            self.set_color(channel=channel, index=index, red=r, green=g, blue=b)
            time.sleep(ms_delay)
            self.set_color(channel=channel, index=index)

    def morph(self, channel=0, index=0, red=0, green=0, blue=0, name=None, hex=None, duration=1000, steps=50):
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

        r_start, g_start, b_start = self._get_color(index).rgb
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

        self.set_color(channel=channel, index=index, red=r_start, green=g_start, blue=b_start)

        for grad in gradient:
            grad_r, grad_g, grad_b = grad

            self.set_color(channel=channel, index=index, red=grad_r, green=grad_g, blue=grad_b)
            time.sleep(ms_delay)

        self.set_color(channel=channel, index=index, red=r_end, green=g_end, blue=b_end)

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

class BlinkStickPro(object):
    def __init__(self, r_led_count=0, g_led_count=0, b_led_count=0, delay=0.002, max_rgb_value=255):
        """
        Initialize class

        Args:
            r_led_count: number of LEDs on R channel
            g_led_count: number of LEDs on G channel
            b_led_count: number of LEDs on B channel
            delay: default transmission delay between frames
            max_rgb_value: maximum color value for RGB channels
        """
        self.r_led_count = r_led_count
        self.g_led_count = g_led_count
        self.b_led_count = b_led_count

        self.fps_count = -1

        self.data_transmission_delay = delay

        self.max_rgb_value = max_rgb_value

        # initialise data store for each channel
        # pre-populated with zeroes

        self.data = [[], [], []]

        for i in range(0, r_led_count):
            self.data[0].append([0, 0, 0])

        for i in range(0, g_led_count):
            self.data[1].append([0, 0, 0])

        for i in range(0, b_led_count):
            self.data[2].append([0, 0, 0])

        self.bstick = None

    def _remap(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return int(rightMin + (valueScaled * rightSpan))

    def _remap_color(self, value):
        return self._remap(value, 0, 255, 0, self.max_rgb_value)

    def _remap_rgb_value(self, rgb_val):
        return [self._remap_color(rgb_val[0]), self._remap_color(rgb_val[1]), self._remap_color(rgb_val[2])]

    def set_color(self, channel, index, r, g, b, remap_values=True):
        """
        Set the color of a single pixel

        Args:
            channel: R, G or B channel
            x: the index of LED on the channel
            r: red color byte
            g: green color byte
            b: blue color byte
        """

        if remap_values:
            r, g, b = [self._remap_color(val) for val in [r, g, b]]

        self.data[channel][index] = [g, r, b]

    def get_color(self, channel, index):
        """Get the current color of a single pixel.

        Returns values as 3-tuple (r,g,b)
        """

        val = self.data[channel][index]
        return [val[1], val[0], val[2]]

    def clear(self):
        """
        Set all pixels to black in the frame buffer
        """
        for x in range(0, self.r_led_count):
            self.set_color(0, x, 0, 0, 0)

        for x in range(0, self.g_led_count):
            self.set_color(1, x, 0, 0, 0)

        for x in range(0, self.b_led_count):
            self.set_color(2, x, 0, 0, 0)

    def off(self):
        """
        Set all pixels to black in on the device
        """
        self.clear()
        self.send_data_all()

    def connect(self, serial=None):
        """
        Connect to the first BlinkStick found

        Args:
            serial: Select the serial number of BlinkStick
        """

        if serial is None:
            self.bstick = find_first()
        else:
            self.bstick = find_by_serial(serial=serial)

        return self.bstick is not None

    def send_data(self, channel):
        """
        Send data to the channel.

        Args:
            channel: 0 - R pin on BlinkStick Pro board
                     1 - G pin on BlinkStick Pro board
                     2 - B pin on BlinkStick Pro board
        """
        packet_data = [item for sublist in self.data[channel] for item in sublist]

        try:
            self.bstick.set_led_data(channel, packet_data)
            time.sleep(self.data_transmission_delay)
        except Exception as e:
            print "Exception: {0}".format(e)

    def send_data_all(self):
        """
        Send data to all channels
        """
        if self.r_led_count > 0:
            self.send_data(0)

        if self.g_led_count > 0:
            self.send_data(1)

        if self.b_led_count > 0:
            self.send_data(2)

class BlinkStickProMatrix(BlinkStickPro):
    def __init__(self, r_columns=0, r_rows=0, g_columns=0, g_rows=0, b_columns=0, b_rows=0, delay=0.002, max_rgb_value=255):
        """
        Initialize class

        Args:
            columns: number of columns
            rows: number of rows
            channels: how many channels are used in r, g and b order
            delay: default transmission delay between frames
            max_rgb_value: maximum color value for RGB channels
        """
        r_leds = r_columns * r_rows
        g_leds = g_columns * g_rows
        b_leds = b_columns * b_rows

        self.r_columns = r_columns
        self.r_rows = r_rows
        self.g_columns = g_columns
        self.g_rows = g_rows
        self.b_columns = b_columns
        self.b_rows = b_rows

        super(BlinkStickProMatrix, self).__init__(r_led_count=r_leds, g_led_count=g_leds, b_led_count=b_leds, delay=delay, max_rgb_value=max_rgb_value)

        self.rows = max(r_rows, g_rows, b_rows)
        self.cols = r_columns + g_columns + b_columns

        # initialise data store for matrix pre-populated with zeroes
        self.matrix_data = []

        for i in range(0, self.rows * self.cols):
            self.matrix_data.append([0, 0, 0])

    def set_color(self, x, y, r, g, b, remap_values=True):
        """
        Set the color of a single pixel

        Args:
            x: the x location in the matrix
            y: the y location in the matrix
            r: red color byte
            g: green color byte
            b: blue color byte
        """

        if remap_values:
            r, g, b = [self._remap_color(val) for val in [r, g, b]]

        self.matrix_data[self._coord_to_index(x, y)] = [g, r, b]

    def _coord_to_index(self, x, y):
        return y * self.cols + x

    def get_color(self, x, y):
        """Get the current color of a single pixel.

        Returns values as 3-tuple (r,g,b)
        """

        val = self.matrix_data[self._coord_to_index(x, y)]
        return [val[1], val[0], val[2]]

    def shift_left(self, remove=False):
        """
        Shift all LED values in the matrix to the left

        Args:
            remove: whether to remove the pixels on the last column or move the to the first column
        """
        if not remove:
            temp = []
            for y in range(0, self.rows):
                temp.append(self.get_color(0, y))

        for y in range(0, self.rows):
            for x in range(0, self.cols - 1):
                r, g, b = self.get_color(x + 1, y)

                self.set_color(x, y, r, g, b, False)

        if remove:
            for y in range(0, self.rows):
                self.set_color(self.cols - 1, y, 0, 0, 0, False)
        else:
            for y in range(0, self.rows):
                col = temp[y]
                self.set_color(self.cols - 1, y, col[0], col[1], col[2], False)

    def shift_right(self, remove=False):
        """Shift all LED values in the matrix to the right

        Args:
            remove: whether to remove the pixels on the last column or move the to the first column
        """

        if not remove:
            temp = []
            for y in range(0, self.rows):
                temp.append(self.get_color(self.cols - 1, y))

        for y in range(0, self.rows):
            for x in reversed(range(1, self.cols)):
                r, g, b = self.get_color(x - 1, y)

                self.set_color(x, y, r, g, b, False)

        if remove:
            for y in range(0, self.rows):
                self.set_color(0, y, 0, 0, 0, False)
        else:
            for y in range(0, self.rows):
                col = temp[y]
                self.set_color(self.cols - 1, y, col[0], col[1], col[2], False)

    def shift_down(self, remove=False):
        """Shift all LED values in the matrix down

        Args:
            remove: whether to remove the pixels on the last row or move the to the first row
        """

        if not remove:
            temp = []
            for x in range(0, self.cols):
                temp.append(self.get_color(x, self.rows - 1))

        for x in range(0, self.cols):
            for y in reversed(range(1, self.rows)):
                r, g, b = self.get_color(x, y - 1)

                self.set_color(x, y, r, g, b, False)

        if remove:
            for x in range(0, self.cols):
                self.set_color(x, 0, 0, 0, 0, False)
        else:
            for x in range(0, self.cols):
                col = temp[y]
                self.set_color(x, 0, col[0], col[1], col[2], False)


    def shift_up(self, remove=False):
        """Shift all LED values in the matrix up

        Args:
            remove: whether to remove the pixels on the first row or move the to the first row
        """

        if not remove:
            temp = []
            for x in range(0, self.cols):
                temp.append(self.get_color(x, 0))

        for x in range(0, self.cols):
            for y in range(0, self.rows - 1):
                r, g, b = self.get_color(x, y + 1)

                self.set_color(x, y, r, g, b, False)

        if remove:
            for x in range(0, self.cols):
                self.set_color(x, self.rows - 1, 0, 0, 0, False)
        else:
            for x in range(0, self.cols):
                col = temp[y]
                self.set_color(x, self.rows - 1, col[0], col[1], col[2], False)

    def number(self, x, y, n, r, g, b):
        """
        Render a 3x5 number n at location x,y and r,g,b color
        """
        if n == 0:
            self.rectangle(x, y, x + 2, y + 4, r, g, b)
        elif n == 1:
            self.line(x + 1, y, x + 1, y + 4, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x, y + 1, r, g, b)
        elif n == 2:
            self.line(x, y, x + 2, y, r, g, b)
            self.line(x, y + 2, x + 2, y + 2, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x + 2, y + 1, r, g, b)
            self.set_color(x, y + 3, r, g, b)
        elif n == 3:
            self.line(x, y, x + 2, y, r, g, b)
            self.line(x, y + 2, x + 2, y + 2, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x + 2, y + 1, r, g, b)
            self.set_color(x + 2, y + 3, r, g, b)
        elif n == 4:
            self.line(x, y, x, y + 2, r, g, b)
            self.line(x + 2, y, x + 2, y + 4, r, g, b)
            self.set_color(x + 1, y + 2, r, g, b)
        elif n == 5:
            self.line(x, y, x + 2, y, r, g, b)
            self.line(x, y + 2, x + 2, y + 2, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x, y + 1, r, g, b)
            self.set_color(x + 2, y + 3, r, g, b)
        elif n == 6:
            self.line(x, y, x + 2, y, r, g, b)
            self.line(x, y + 2, x + 2, y + 2, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x, y + 1, r, g, b)
            self.set_color(x + 2, y + 3, r, g, b)
            self.set_color(x, y + 3, r, g, b)
        elif n == 7:
            self.line(x + 1, y + 2, x + 1, y + 4, r, g, b)
            self.line(x, y, x + 2, y, r, g, b)
            self.set_color(x + 2, y + 1, r, g, b)
        elif n == 8:
            self.line(x, y, x + 2, y, r, g, b)
            self.line(x, y + 2, x + 2, y + 2, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x, y + 1, r, g, b)
            self.set_color(x + 2, y + 1, r, g, b)
            self.set_color(x + 2, y + 3, r, g, b)
            self.set_color(x, y + 3, r, g, b)
        elif n == 9:
            self.line(x, y, x + 2, y, r, g, b)
            self.line(x, y + 2, x + 2, y + 2, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x, y + 1, r, g, b)
            self.set_color(x + 2, y + 1, r, g, b)
            self.set_color(x + 2, y + 3, r, g, b)

    def rectangle(self, x1, y1, x2, y2, r, g, b):
        """
        Draw a rectangle with it's corners at x1:y1 and x2:y2
        """

        self.line(x1, y1, x1, y2, r, g, b)
        self.line(x1, y1, x2, y1, r, g, b)
        self.line(x2, y1, x2, y2, r, g, b)
        self.line(x1, y2, x2, y2, r, g, b)

    def line(self, x1, y1, x2, y2, r, g, b):
        """
        Draw a line from x1:y1 and x2:y2
        """
        points = []
        is_steep = abs(y2 - y1) > abs(x2 - x1)
        if is_steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        rev = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            rev = True
        delta_x = x2 - x1
        delta_y = abs(y2 - y1)
        error = int(delta_x / 2)
        y = y1
        y_step = None

        if y1 < y2:
            y_step = 1
        else:
            y_step = -1
        for x in range(x1, x2 + 1):
            if is_steep:
                #print y, "~", x
                self.set_color(y, x, r, g, b)
                points.append((y, x))
            else:
                #print x, " ", y
                self.set_color(x, y, r, g, b)
                points.append((x, y))
            error -= delta_y
            if error < 0:
                y += y_step
                error += delta_x
                # Reverse the list if the coordinates were reversed
        if rev:
            points.reverse()
        return points

    def clear(self):
        """
        Set all pixels to black in the cached matrix
        """
        for y in range(0, self.rows):
            for x in range(0, self.cols):
                self.set_color(x, y, 0, 0, 0)

    def send_data(self, channel):
        """
        Send data to the channel.

        Args:
            channel: 0 - R pin on BlinkStick Pro board
                     1 - G pin on BlinkStick Pro board
                     2 - B pin on BlinkStick Pro board
        """

        start_col = 0
        end_col = 0

        if channel == 0:
            start_col = 0
            end_col = self.r_columns

        if channel == 1:
            start_col = self.r_columns
            end_col = start_col + self.g_columns

        if channel == 2:
            start_col = self.r_columns + self.g_columns
            end_col = start_col + self.b_columns

        self.data[channel] = []

        #slice the huge array to individual packets
        for y in range(0, self.rows):
            start = y * self.cols + start_col
            end = y * self.cols + end_col

            self.data[channel].extend(self.matrix_data[start: end])

        super(BlinkStickProMatrix, self).send_data(channel)

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
    result = []
    for d in _find_blicksticks():
        try:
            result.extend([BlinkStick(device=d)])
        except usb.USBError:
            print "Skipping device"
    return result


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
    
    devices = []
    if sys.platform == "win32":
        devices = [d for d in _find_blicksticks()
                   if d.serial_number == serial]
    else:
        for d in _find_blicksticks():
            try:
                if usb.util.get_string(d, 256, 3) == serial:
                    devices = [d]
                    break
            except:
                print "Skipping..."
    
    if devices:
        return BlinkStick(device=devices[0])


def get_blinkstick_package_version():
    return __version__
