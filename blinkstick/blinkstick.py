from ._version import  __version__
import time
import sys
import re
import collections

if sys.platform == "win32":
    import pywinusb.hid as hid
    from ctypes import *
else:
    import usb.core
    import usb.util

from random import randint

"""
Main module to control BlinkStick and BlinkStick Pro devices.
"""

VENDOR_ID = 0x20a0
PRODUCT_ID = 0x41e5

class BlinkStickException(Exception):
    pass


class BlinkStick(object):
    """
    BlinkStick class is designed to control regular BlinkStick devices, or BlinkStick Pro
    devices in Normal or Inverse modes. Please refer to L{BlinkStick.set_mode} for more details
    about BlinkStick Pro device modes.

    Code examples on how you can use this class are available here:

    U{https://github.com/arvydas/blinkstick-python/wiki}
    """

    _names_to_hex = {'aliceblue': '#f0f8ff',
                     'antiquewhite': '#faebd7',
                     'aqua': '#00ffff',
                     'aquamarine': '#7fffd4',
                     'azure': '#f0ffff',
                     'beige': '#f5f5dc',
                     'bisque': '#ffe4c4',
                     'black': '#000000',
                     'blanchedalmond': '#ffebcd',
                     'blue': '#0000ff',
                     'blueviolet': '#8a2be2',
                     'brown': '#a52a2a',
                     'burlywood': '#deb887',
                     'cadetblue': '#5f9ea0',
                     'chartreuse': '#7fff00',
                     'chocolate': '#d2691e',
                     'coral': '#ff7f50',
                     'cornflowerblue': '#6495ed',
                     'cornsilk': '#fff8dc',
                     'crimson': '#dc143c',
                     'cyan': '#00ffff',
                     'darkblue': '#00008b',
                     'darkcyan': '#008b8b',
                     'darkgoldenrod': '#b8860b',
                     'darkgray': '#a9a9a9',
                     'darkgrey': '#a9a9a9',
                     'darkgreen': '#006400',
                     'darkkhaki': '#bdb76b',
                     'darkmagenta': '#8b008b',
                     'darkolivegreen': '#556b2f',
                     'darkorange': '#ff8c00',
                     'darkorchid': '#9932cc',
                     'darkred': '#8b0000',
                     'darksalmon': '#e9967a',
                     'darkseagreen': '#8fbc8f',
                     'darkslateblue': '#483d8b',
                     'darkslategray': '#2f4f4f',
                     'darkslategrey': '#2f4f4f',
                     'darkturquoise': '#00ced1',
                     'darkviolet': '#9400d3',
                     'deeppink': '#ff1493',
                     'deepskyblue': '#00bfff',
                     'dimgray': '#696969',
                     'dimgrey': '#696969',
                     'dodgerblue': '#1e90ff',
                     'firebrick': '#b22222',
                     'floralwhite': '#fffaf0',
                     'forestgreen': '#228b22',
                     'fuchsia': '#ff00ff',
                     'gainsboro': '#dcdcdc',
                     'ghostwhite': '#f8f8ff',
                     'gold': '#ffd700',
                     'goldenrod': '#daa520',
                     'gray': '#808080',
                     'grey': '#808080',
                     'green': '#008000',
                     'greenyellow': '#adff2f',
                     'honeydew': '#f0fff0',
                     'hotpink': '#ff69b4',
                     'indianred': '#cd5c5c',
                     'indigo': '#4b0082',
                     'ivory': '#fffff0',
                     'khaki': '#f0e68c',
                     'lavender': '#e6e6fa',
                     'lavenderblush': '#fff0f5',
                     'lawngreen': '#7cfc00',
                     'lemonchiffon': '#fffacd',
                     'lightblue': '#add8e6',
                     'lightcoral': '#f08080',
                     'lightcyan': '#e0ffff',
                     'lightgoldenrodyellow': '#fafad2',
                     'lightgray': '#d3d3d3',
                     'lightgrey': '#d3d3d3',
                     'lightgreen': '#90ee90',
                     'lightpink': '#ffb6c1',
                     'lightsalmon': '#ffa07a',
                     'lightseagreen': '#20b2aa',
                     'lightskyblue': '#87cefa',
                     'lightslategray': '#778899',
                     'lightslategrey': '#778899',
                     'lightsteelblue': '#b0c4de',
                     'lightyellow': '#ffffe0',
                     'lime': '#00ff00',
                     'limegreen': '#32cd32',
                     'linen': '#faf0e6',
                     'magenta': '#ff00ff',
                     'maroon': '#800000',
                     'mediumaquamarine': '#66cdaa',
                     'mediumblue': '#0000cd',
                     'mediumorchid': '#ba55d3',
                     'mediumpurple': '#9370d8',
                     'mediumseagreen': '#3cb371',
                     'mediumslateblue': '#7b68ee',
                     'mediumspringgreen': '#00fa9a',
                     'mediumturquoise': '#48d1cc',
                     'mediumvioletred': '#c71585',
                     'midnightblue': '#191970',
                     'mintcream': '#f5fffa',
                     'mistyrose': '#ffe4e1',
                     'moccasin': '#ffe4b5',
                     'navajowhite': '#ffdead',
                     'navy': '#000080',
                     'oldlace': '#fdf5e6',
                     'olive': '#808000',
                     'olivedrab': '#6b8e23',
                     'orange': '#ffa500',
                     'orangered': '#ff4500',
                     'orchid': '#da70d6',
                     'palegoldenrod': '#eee8aa',
                     'palegreen': '#98fb98',
                     'paleturquoise': '#afeeee',
                     'palevioletred': '#d87093',
                     'papayawhip': '#ffefd5',
                     'peachpuff': '#ffdab9',
                     'peru': '#cd853f',
                     'pink': '#ffc0cb',
                     'plum': '#dda0dd',
                     'powderblue': '#b0e0e6',
                     'purple': '#800080',
                     'red': '#ff0000',
                     'rosybrown': '#bc8f8f',
                     'royalblue': '#4169e1',
                     'saddlebrown': '#8b4513',
                     'salmon': '#fa8072',
                     'sandybrown': '#f4a460',
                     'seagreen': '#2e8b57',
                     'seashell': '#fff5ee',
                     'sienna': '#a0522d',
                     'silver': '#c0c0c0',
                     'skyblue': '#87ceeb',
                     'slateblue': '#6a5acd',
                     'slategray': '#708090',
                     'slategrey': '#708090',
                     'snow': '#fffafa',
                     'springgreen': '#00ff7f',
                     'steelblue': '#4682b4',
                     'tan': '#d2b48c',
                     'teal': '#008080',
                     'thistle': '#d8bfd8',
                     'tomato': '#ff6347',
                     'turquoise': '#40e0d0',
                     'violet': '#ee82ee',
                     'wheat': '#f5deb3',
                     'white': '#ffffff',
                     'whitesmoke': '#f5f5f5',
                     'yellow': '#ffff00',
                     'yellowgreen': '#9acd32'}

    HEX_COLOR_RE = re.compile(r'^#([a-fA-F0-9]{3}|[a-fA-F0-9]{6})$')

    inverse = False
    error_reporting = True
    max_rgb_value = 255

    def __init__(self, device=None, error_reporting=True):
        """
        Constructor for the class.

        @type  error_reporting: Boolean
        @param error_reporting: display errors if they occur during communication with the device
        """
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
        """
        Returns the serial number of device.::

            BSnnnnnn-1.0
            ||  |    | |- Software minor version
            ||  |    |--- Software major version
            ||  |-------- Denotes sequential number
            ||----------- Denotes BlinkStick device

        Software version defines the capabilities of the device

        @rtype: str
        @return: Serial number of the device
        """
        if sys.platform == "win32":
            return self.device.serial_number
        else:
            return self._usb_get_string(self.device, 256, 3)

    def get_manufacturer(self):
        """
        Get the manufacturer of the device

        @rtype: str
        @return: Device manufacturer's name
        """
        if sys.platform == "win32":
            return self.device.vendor_name
        else:
            return self._usb_get_string(self.device, 256, 1)


    def get_description(self):
        """
        Get the description of the device

        @rtype: str
        @return: Device description
        """
        if sys.platform == "win32":
            return self.device.product_name
        else:
            return self._usb_get_string(self.device, 256, 2)

    def set_error_reporting(self, error_reporting):
        """
        Enable or disable error reporting

        @type  error_reporting: Boolean
        @param error_reporting: display errors if they occur during communication with the device
        """
        self.error_reporting = error_reporting

    def set_color(self, channel=0, index=0, red=0, green=0, blue=0, name=None, hex=None):
        """
        Set the color to the device as RGB

        @type  red: int
        @param red: Red color intensity 0 is off, 255 is full red intensity
        @type  green: int
        @param green: Green color intensity 0 is off, 255 is full green intensity
        @type  blue: int
        @param blue: Blue color intensity 0 is off, 255 is full blue intensity
        @type  name: str
        @param name: Use CSS color name as defined here: U{http://www.w3.org/TR/css3-color/}
        @type  hex: str
        @param hex: Specify color using hexadecimal color value e.g. '#FF3366'
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
            except Exception:
                pass

    def _determine_rgb(self, red=0, green=0, blue=0, name=None, hex=None):

        try:
            if name:
                # Special case for name="random"
                if name is "random":
                    red = randint(0, 255)
                    green = randint(0, 255)
                    blue = randint(0, 255)
                else:
                    red, green, blue = self._name_to_rgb(name)
            elif hex:
                red, green, blue = self._hex_to_rgb(hex)
        except ValueError:
            red = green = blue = 0

        red, green, blue = _remap_rgb_value([red, green, blue], self.max_rgb_value)

        # TODO - do smarts to determine input type from red var in case it is not int

        return red, green, blue

    def _get_color_rgb(self, index=0):
        if index == 0:
            device_bytes = self._usb_ctrl_transfer(0x80 | 0x20, 0x1, 0x0001, 0, 33)
            if self.inverse:
                return [255 - device_bytes[1], 255 - device_bytes[2], 255 - device_bytes[3]]
            else:
                return [device_bytes[1], device_bytes[2], device_bytes[3]]
        else:
            data = self.get_led_data((index + 1) * 3)

            return [data[index * 3 + 1], data[index * 3], data[index * 3 + 2]]

    def _get_color_hex(self, index=0):
        r, g, b = self._get_color_rgb(index)
        return '#%02x%02x%02x' % (r, g, b)

    def get_color(self, index=0, color_format='rgb'):
        """
        Get the current device color in the defined format.

        Currently supported formats:

            1. rgb (default) - Returns values as 3-tuple (r,g,b)
            2. hex - returns current device color as hexadecimal string

            >>> b = blinkstick.find_first()
            >>> b.set_color(red=255,green=0,blue=0)
            >>> (r,g,b) = b.get_color() # Get color as rbg tuple
            (255,0,0)
            >>> hex = b.get_color(color_format='hex') # Get color as hex string
            '#ff0000'

        @type  index: int
        @param index: the index of the LED
        @type  color_format: str
        @param color_format: "rgb" or "hex". Defaults to "rgb".

        @rtype: (int, int, int) or str
        @return: Either 3-tuple for R, G and B values, or hex string
        """

        # Attempt to find a function to return the appropriate format
        get_color_func = getattr(self, "_get_color_%s" % color_format, self._get_color_rgb)
        if isinstance(get_color_func, collections.Callable):
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
        """
        Send LED data frame.

        @type  channel: int
        @param channel: the channel which to send data to (R=0, G=1, B=2)
        @type  data: int[0..64*3]
        @param data: The LED data frame in GRB format
        """

        report_id, max_leds = self._determine_report_id(len(data))

        report = [0, channel]

        for i in range(0, max_leds * 3):
            if len(data) > i:
                report.append(data[i])
            else:
                report.append(0)

        self.device.ctrl_transfer(0x20, 0x9, report_id, 0, bytes(bytearray(report)))

    def get_led_data(self, count):
        """
        Get LED data frame on the device.

        @type  count: int
        @param count: How much data to retrieve. Can be in the range of 0..64*3
        @rtype: int[0..64*3]
        @return: LED data currently stored in the RAM of the device
        """

        report_id, max_leds = self._determine_report_id(count)

        device_bytes = self._usb_ctrl_transfer(0x80 | 0x20, 0x1, report_id, 0, max_leds * 3 + 2)

        return device_bytes[2: 2 + count * 3]

    def set_mode(self, mode):
        """
        Set device mode for BlinkStick Pro. Device currently supports the following modes:

            - 0 - (default) use R, G and B channels to control single RGB LED
            - 1 - same as 0, but inverse mode
            - 2 - control up to 64 WS2812 individual LEDs per each R, G and B channel

        You can find out more about BlinkStick Pro modes:

        U{http://www.blinkstick.com/help/tutorials/blinkstick-pro-modes}

        @type  mode: int
        @param mode: Device mode to set
        """
        control_string = bytes(bytearray([4, mode]))

        self.device.ctrl_transfer(0x20, 0x9, 0x0004, 0, control_string)

    def get_mode(self):
        """
        Get BlinkStick Pro mode. Device currently supports the following modes:

            - 0 - (default) use R, G and B channels to control single RGB LED
            - 1 - same as 0, but inverse mode
            - 2 - control up to 64 WS2812 individual LEDs per each R, G and B channel

        You can find out more about BlinkStick Pro modes:

        U{http://www.blinkstick.com/help/tutorials/blinkstick-pro-modes}

        @rtype: int
        @return: Device mode
        """

        device_bytes = self.device.ctrl_transfer(0x80 | 0x20, 0x1, 0x0004, 0, 2)

        if len(device_bytes) >= 2:
            return device_bytes[1]
        else:
            return -1

    def get_info_block1(self):
        """
        Get the infoblock1 of the device.

        This is a 32 byte array that can contain any data. It's supposed to
        hold the "Name" of the device making it easier to identify rather than
        a serial number.

        @rtype: str
        @return: InfoBlock1 currently stored on the device
        """

        device_bytes = self._usb_ctrl_transfer(0x80 | 0x20, 0x1, 0x0002, 0, 33)
        result = ""
        for i in device_bytes[1:]:
            if i == 0:
                break
            result += chr(i)
        return result

    def get_info_block2(self):
        """
        Get the infoblock2 of the device.

        This is a 32 byte array that can contain any data.

        @rtype: str
        @return: InfoBlock2 currently stored on the device
        """
        device_bytes = self._usb_ctrl_transfer(0x80 | 0x20, 0x1, 0x0003, 0, 33)
        result = ""
        for i in device_bytes[1:]:
            if i == 0:
                break
            result += chr(i)
        return result

    def _data_to_message(self, data):
        """
        Helper method to convert a string to byte array of 32 bytes.

        @type  data: str
        @param data: The data to convert to byte array

        @rtype: byte[32]
        @return: It fills the rest of bytes with zeros.
        """
        bytes = [1]
        for c in data:
            bytes.append(ord(c))

        for i in range(32 - len(data)):
            bytes.append(0)

        return bytes

    def set_info_block1(self, data):
        """
        Sets the infoblock1 with specified string.

        It fills the rest of 32 bytes with zeros.

        @type  data: str
        @param data: InfoBlock1 for the device to set
        """
        self._usb_ctrl_transfer(0x20, 0x9, 0x0002, 0, self._data_to_message(data))

    def set_info_block2(self, data):
        """
        Sets the infoblock2 with specified string.

        It fills the rest of 32 bytes with zeros.

        @type  data: str
        @param data: InfoBlock2 for the device to set
        """
        self._usb_ctrl_transfer(0x20, 0x9, 0x0003, 0, self._data_to_message(data))

    def set_random_color(self):
        """
        Sets random color to the device.
        """
        self.set_color(name="random")

    def turn_off(self):
        """
        Turns off LED.
        """
        self.set_color()

    def pulse(self, channel=0, index=0, red=0, green=0, blue=0, name=None, hex=None, repeats=1, duration=1000, steps=50):
        """
        Morph to the specified color from black and back again.

        @type  red: int
        @param red: Red color intensity 0 is off, 255 is full red intensity
        @type  green: int
        @param green: Green color intensity 0 is off, 255 is full green intensity
        @type  blue: int
        @param blue: Blue color intensity 0 is off, 255 is full blue intensity
        @type  name: str
        @param name: Use CSS color name as defined here: U{http://www.w3.org/TR/css3-color/}
        @type  hex: str
        @param hex: Specify color using hexadecimal color value e.g. '#FF3366'
        @type  repeats: int
        @param repeats: Number of times to pulse the LED
        @type  duration: int
        @param duration: Duration for pulse in milliseconds
        @type  steps: int
        @param steps: Number of gradient steps
        """
        r, g, b = self._determine_rgb(red=red, green=green, blue=blue, name=name, hex=hex)

        self.turn_off()
        for x in range(repeats):
            self.morph(channel=channel, index=index, red=r, green=g, blue=b, duration=duration, steps=steps)
            self.morph(channel=channel, index=index, red=0, green=0, blue=0, duration=duration, steps=steps)

    def blink(self, channel=0, index=0, red=0, green=0, blue=0, name=None, hex=None, repeats=1, delay=500):
        """
        Blink the specified color.

        @type  red: int
        @param red: Red color intensity 0 is off, 255 is full red intensity
        @type  green: int
        @param green: Green color intensity 0 is off, 255 is full green intensity
        @type  blue: int
        @param blue: Blue color intensity 0 is off, 255 is full blue intensity
        @type  name: str
        @param name: Use CSS color name as defined here: U{http://www.w3.org/TR/css3-color/}
        @type  hex: str
        @param hex: Specify color using hexadecimal color value e.g. '#FF3366'
        @type  repeats: int
        @param repeats: Number of times to pulse the LED
        @type  delay: int
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

        @type  red: int
        @param red: Red color intensity 0 is off, 255 is full red intensity
        @type  green: int
        @param green: Green color intensity 0 is off, 255 is full green intensity
        @type  blue: int
        @param blue: Blue color intensity 0 is off, 255 is full blue intensity
        @type  name: str
        @param name: Use CSS color name as defined here: U{http://www.w3.org/TR/css3-color/}
        @type  hex: str
        @param hex: Specify color using hexadecimal color value e.g. '#FF3366'
        @type  duration: int
        @param duration: Duration for morph in milliseconds
        @type  steps: int
        @param steps: Number of gradient steps (default 50)
        """

        r_end, g_end, b_end = self._determine_rgb(red=red, green=green, blue=blue, name=name, hex=hex)

        r_start, g_start, b_start = _remap_rgb_value_reverse(self._get_color_rgb(index), self.max_rgb_value)

        if r_start > 255 or g_start > 255 or b_start > 255:
            r_start = 0
            g_start = 0
            b_start = 0

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
        @param d: Device to open
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
        """
        Get the value of inverse mode. This applies only to BlinkStick. Please use L{set_mode} for BlinkStick Pro
        to permanently set the inverse mode to the device.

        @rtype: bool
        @return: True if inverse mode, otherwise false
        """
        return self.inverse

    def set_inverse(self, value):
        """
        Set inverse mode. This applies only to BlinkStick. Please use L{set_mode} for BlinkStick Pro
        to permanently set the inverse mode to the device.

        @type  value: bool
        @param value: True/False to set the inverse mode
        """
        self.inverse = value

    def set_max_rgb_value(self, value):
        """
        Set RGB color limit. {set_color} function will automatically remap
        the values to maximum supplied.

        @type  value: int
        @param value: 0..255 maximum value for each R, G and B color
        """
        self.max_rgb_value = value

    def get_max_rgb_value(self, max_rgb_value):
        """
        Get RGB color limit. {set_color} function will automatically remap
        the values to maximum set.

        @rtype: int
        @return: 0..255 maximum value for each R, G and B color
        """
        return self.max_rgb_value

    def _name_to_hex(self, name):
        """
        Convert a color name to a normalized hexadecimal color value.

        The color name will be normalized to lower-case before being
        looked up, and when no color of that name exists in the given
        specification, ``ValueError`` is raised.

        Examples:

        >>> _name_to_hex('white')
        '#ffffff'
        >>> _name_to_hex('navy')
        '#000080'
        >>> _name_to_hex('goldenrod')
        '#daa520'
        """
        normalized = name.lower()
        try:
            hex_value = self._names_to_hex[normalized]
        except KeyError:
            raise ValueError("'%s' is not defined as a named color." % (name))
        return hex_value

    def _hex_to_rgb(self, hex_value):
        """
        Convert a hexadecimal color value to a 3-tuple of integers
        suitable for use in an ``rgb()`` triplet specifying that color.

        The hexadecimal value will be normalized before being converted.

        Examples:

        >>> _hex_to_rgb('#fff')
        (255, 255, 255)
        >>> _hex_to_rgb('#000080')
        (0, 0, 128)

        """
        hex_digits = self._normalize_hex(hex_value)
        return tuple([int(s, 16) for s in (hex_digits[1:3], hex_digits[3:5], hex_digits[5:7])])

    def _normalize_hex(self, hex_value):
        """
        Normalize a hexadecimal color value to the following form and
        return the result::

            #[a-f0-9]{6}

        In other words, the following transformations are applied as
        needed:

        * If the value contains only three hexadecimal digits, it is expanded to six.

        * The value is normalized to lower-case.

        If the supplied value cannot be interpreted as a hexadecimal color
        value, ``ValueError`` is raised.

        Examples:

        >>> _normalize_hex('#0099cc')
        '#0099cc'
        >>> _normalize_hex('#0099CC')
        '#0099cc'
        >>> _normalize_hex('#09c')
        '#0099cc'
        >>> _normalize_hex('#09C')
        '#0099cc'
        >>> _normalize_hex('0099cc')
        Traceback (most recent call last):
            ...
        ValueError: '0099cc' is not a valid hexadecimal color value.

        """
        try:
            hex_digits = self.HEX_COLOR_RE.match(hex_value).groups()[0]
        except AttributeError:
            raise ValueError("'%s' is not a valid hexadecimal color value." % hex_value)
        if len(hex_digits) == 3:
            hex_digits = ''.join([2 * s for s in hex_digits])
        return '#%s' % hex_digits.lower()

    def _name_to_rgb(self, name):
        """
        Convert a color name to a 3-tuple of integers suitable for use in
        an ``rgb()`` triplet specifying that color.

        The color name will be normalized to lower-case before being
        looked up, and when no color of that name exists in the given
        specification, ``ValueError`` is raised.

        Examples:

        >>> _name_to_rgb('white')
        (255, 255, 255)
        >>> _name_to_rgb('navy')
        (0, 0, 128)
        >>> _name_to_rgb('goldenrod')
        (218, 165, 32)

        """
        return self._hex_to_rgb(self._name_to_hex(name))

class BlinkStickPro(object):
    """
    BlinkStickPro class is specifically designed to control the individually
    addressable LEDs connected to the device. The tutorials section contains
    all the details on how to connect them to BlinkStick Pro.

    U{http://www.blinkstick.com/help/tutorials}

    Code example on how you can use this class are available here:

    U{https://github.com/arvydas/blinkstick-python/wiki#code-examples-for-blinkstick-pro}
    """

    def __init__(self, r_led_count=0, g_led_count=0, b_led_count=0, delay=0.002, max_rgb_value=255):
        """
        Initialize BlinkStickPro class.

        @type r_led_count: int
        @param r_led_count: number of LEDs on R channel
        @type g_led_count: int
        @param g_led_count: number of LEDs on G channel
        @type b_led_count: int
        @param b_led_count: number of LEDs on B channel
        @type delay: int
        @param delay: default transmission delay between frames
        @type max_rgb_value: int
        @param max_rgb_value: maximum color value for RGB channels
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

    def set_color(self, channel, index, r, g, b, remap_values=True):
        """
        Set the color of a single pixel

        @type channel: int
        @param channel: R, G or B channel
        @type index: int
        @param index: the index of LED on the channel
        @type r: int
        @param r: red color byte
        @type g: int
        @param g: green color byte
        @type b: int
        @param b: blue color byte
        """

        if remap_values:
            r, g, b = [_remap_color(val, self.max_rgb_value) for val in [r, g, b]]

        self.data[channel][index] = [g, r, b]

    def get_color(self, channel, index):
        """
        Get the current color of a single pixel.

        @type  channel: int
        @param channel: the channel of the LED
        @type  index: int
        @param index: the index of the LED

        @rtype: (int, int, int)
        @return: 3-tuple for R, G and B values
        """

        val = self.data[channel][index]
        return [val[1], val[0], val[2]]

    def clear(self):
        """
        Set all pixels to black in the frame buffer.
        """
        for x in range(0, self.r_led_count):
            self.set_color(0, x, 0, 0, 0)

        for x in range(0, self.g_led_count):
            self.set_color(1, x, 0, 0, 0)

        for x in range(0, self.b_led_count):
            self.set_color(2, x, 0, 0, 0)

    def off(self):
        """
        Set all pixels to black in on the device.
        """
        self.clear()
        self.send_data_all()

    def connect(self, serial=None):
        """
        Connect to the first BlinkStick found

        @type serial: str
        @param serial: Select the serial number of BlinkStick
        """

        if serial is None:
            self.bstick = find_first()
        else:
            self.bstick = find_by_serial(serial=serial)

        return self.bstick is not None

    def send_data(self, channel):
        """
        Send data stored in the internal buffer to the channel.

        @param channel:
            - 0 - R pin on BlinkStick Pro board
            - 1 - G pin on BlinkStick Pro board
            - 2 - B pin on BlinkStick Pro board
        """
        packet_data = [item for sublist in self.data[channel] for item in sublist]

        try:
            self.bstick.set_led_data(channel, packet_data)
            time.sleep(self.data_transmission_delay)
        except Exception as e:
            print("Exception: {0}".format(e))

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
    """
    BlinkStickProMatrix class is specifically designed to control the individually
    addressable LEDs connected to the device and arranged in a matrix. The tutorials section contains
    all the details on how to connect them to BlinkStick Pro with matrices.

    U{http://www.blinkstick.com/help/tutorials/blinkstick-pro-adafruit-neopixel-matrices}

    Code example on how you can use this class are available here:

    U{https://github.com/arvydas/blinkstick-python/wiki#code-examples-for-blinkstick-pro}

    Matrix is driven by using L{BlinkStickProMatrix.set_color} with [x,y] coordinates and class automatically
    divides data into subsets and sends it to the matrices.

    For example, if you have 2 8x8 matrices connected to BlinkStickPro and you initialize
    the class with

        >>> matrix = BlinkStickProMatrix(r_columns=8, r_rows=8, g_columns=8, g_rows=8)

    Then you can set the internal framebuffer by using {set_color} command:

        >>> matrix.set_color(x=10, y=5, r=255, g=0, b=0)
        >>> matrix.set_color(x=6, y=3, r=0, g=255, b=0)

    And send data to both matrices in one go:

        >>> matrix.send_data_all()

    """

    def __init__(self, r_columns=0, r_rows=0, g_columns=0, g_rows=0, b_columns=0, b_rows=0, delay=0.002, max_rgb_value=255):
        """
        Initialize BlinkStickProMatrix class.

        @type r_columns: int
        @param r_columns: number of matric columns for R channel
        @type g_columns: int
        @param g_columns: number of matric columns for R channel
        @type b_columns: int
        @param b_columns: number of matric columns for R channel
        @type delay: int
        @param delay: default transmission delay between frames
        @type max_rgb_value: int
        @param max_rgb_value: maximum color value for RGB channels
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
        Set the color of a single pixel in the internal framebuffer.

        @type x: int
        @param x: the x location in the matrix
        @type y: int
        @param y: the y location in the matrix
        @type r: int
        @param r: red color byte
        @type g: int
        @param g: green color byte
        @type b: int
        @param b: blue color byte
        @type remap_values: bool
        @param remap_values: Automatically remap values based on the {max_rgb_value} supplied in the constructor
        """

        if remap_values:
            r, g, b = [_remap_color(val, self.max_rgb_value) for val in [r, g, b]]

        self.matrix_data[self._coord_to_index(x, y)] = [g, r, b]

    def _coord_to_index(self, x, y):
        return y * self.cols + x

    def get_color(self, x, y):
        """
        Get the current color of a single pixel.

        @type  x: int
        @param x: x coordinate of the internal framebuffer
        @type  y: int
        @param y: y coordinate of the internal framebuffer

        @rtype: (int, int, int)
        @return: 3-tuple for R, G and B values
        """

        val = self.matrix_data[self._coord_to_index(x, y)]
        return [val[1], val[0], val[2]]

    def shift_left(self, remove=False):
        """
        Shift all LED values in the matrix to the left

        @type remove: bool
        @param remove: whether to remove the pixels on the last column or move the to the first column
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
        """
        Shift all LED values in the matrix to the right

        @type remove: bool
        @param remove: whether to remove the pixels on the last column or move the to the first column
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
        """
        Shift all LED values in the matrix down

        @type remove: bool
        @param remove: whether to remove the pixels on the last column or move the to the first column
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
        """
        Shift all LED values in the matrix up

        @type remove: bool
        @param remove: whether to remove the pixels on the last column or move the to the first column
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

        @type x: int
        @param x: the x location in the matrix (left of the number)
        @type y: int
        @param y: the y location in the matrix (top of the number)
        @type n: int
        @param n: number digit to render 0..9
        @type r: int
        @param r: red color byte
        @type g: int
        @param g: green color byte
        @type b: int
        @param b: blue color byte
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

        @type x1: int
        @param x1: the x1 location in the matrix for first corner of the rectangle
        @type y1: int
        @param y1: the y1 location in the matrix for first corner of the rectangle
        @type x2: int
        @param x2: the x2 location in the matrix for second corner of the rectangle
        @type y2: int
        @param y2: the y2 location in the matrix for second corner of the rectangle
        @type r: int
        @param r: red color byte
        @type g: int
        @param g: green color byte
        @type b: int
        @param b: blue color byte
        """

        self.line(x1, y1, x1, y2, r, g, b)
        self.line(x1, y1, x2, y1, r, g, b)
        self.line(x2, y1, x2, y2, r, g, b)
        self.line(x1, y2, x2, y2, r, g, b)

    def line(self, x1, y1, x2, y2, r, g, b):
        """
        Draw a line from x1:y1 and x2:y2

        @type x1: int
        @param x1: the x1 location in the matrix for the start of the line
        @type y1: int
        @param y1: the y1 location in the matrix for the start of the line
        @type x2: int
        @param x2: the x2 location in the matrix for the end of the line
        @type y2: int
        @param y2: the y2 location in the matrix for the end of the line
        @type r: int
        @param r: red color byte
        @type g: int
        @param g: green color byte
        @type b: int
        @param b: blue color byte
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
        Send data stored in the internal buffer to the channel.

        @param channel:
            - 0 - R pin on BlinkStick Pro board
            - 1 - G pin on BlinkStick Pro board
            - 2 - B pin on BlinkStick Pro board
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
    """
    Find all attached BlinkStick devices.

    @rtype: BlinkStick[]
    @return: a list of BlinkStick objects or None if no devices found
    """
    result = []
    for d in _find_blicksticks():
        result.extend([BlinkStick(device=d)])

    return result


def find_first():
    """
    Find first attached BlinkStick.

    @rtype: BlinkStick
    @return: BlinkStick object or None if no devices are found
    """
    d = _find_blicksticks(find_all=False)

    if d:
        return BlinkStick(device=d)


def find_by_serial(serial=None):
    """
    Find BlinkStick device based on serial number.

    @rtype: BlinkStick
    @return: BlinkStick object or None if no devices are found
    """

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
            except Exception as e:
                print("{0}".format(e))

    if devices:
        return BlinkStick(device=devices[0])


def _remap(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return int(rightMin + (valueScaled * rightSpan))

def _remap_color(value, max_value):
    return _remap(value, 0, 255, 0, max_value)

def _remap_color_reverse(value, max_value):
    return _remap(value, 0, max_value, 0, 255)

def _remap_rgb_value(rgb_val, max_value):
    return [_remap_color(rgb_val[0], max_value),
        _remap_color(rgb_val[1], max_value),
        _remap_color(rgb_val[2], max_value)]

def _remap_rgb_value_reverse(rgb_val, max_value):
    return [_remap_color_reverse(rgb_val[0], max_value),
        _remap_color_reverse(rgb_val[1], max_value),
        _remap_color_reverse(rgb_val[2], max_value)]

def get_blinkstick_package_version():
    return __version__

