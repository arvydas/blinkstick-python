from __future__ import annotations

import sys
import time
import warnings
from typing import Callable

from blinkstick.colors import (
    hex_to_rgb,
    name_to_rgb,
    remap_rgb_value,
    remap_rgb_value_reverse,
    ColorFormat,
)
from blinkstick.decorators import no_backend_required
from blinkstick.devices import BlinkStickDevice
from blinkstick.enums import BlinkStickVariant, Mode
from blinkstick.exceptions import NotConnected
from blinkstick.utilities import string_to_info_block_data

if sys.platform == "win32":
    from blinkstick.backends.win32 import Win32Backend as USBBackend
else:
    from blinkstick.backends.unix_like import UnixLikeBackend as USBBackend

from random import randint

"""
Main module to control BlinkStick and BlinkStick Pro devices.
"""


class BlinkStick:
    """
    BlinkStick class is designed to control regular BlinkStick devices, or BlinkStick Pro
    devices in Normal or Inverse modes. Please refer to L{BlinkStick.set_mode} for more details
    about BlinkStick Pro backend modes.

    Code examples on how you can use this class are available here:

    U{https://github.com/arvydas/blinkstick-python/wiki}
    """

    inverse: bool
    error_reporting = True
    max_rgb_value: int

    backend: USBBackend
    bs_serial: str

    def __init__(
        self, device: BlinkStickDevice | None = None, error_reporting: bool = True
    ):
        """
        Constructor for the class.

        @type  error_reporting: Boolean
        @param error_reporting: display errors if they occur during communication with the backend
        """
        self.error_reporting = error_reporting
        self.max_rgb_value = 255
        self.inverse = False

        if device:
            self.backend = USBBackend(device)
            self.bs_serial = self.get_serial()

    def __getattribute__(self, name):
        """Default all callables to require a backend unless they have the no_backend_required attribute"""
        attr = object.__getattribute__(self, name)
        if callable(attr) and not getattr(attr, "no_backend_required", False):

            def wrapper(*args, **kwargs):
                if not getattr(self, "backend", None):
                    raise NotConnected("No backend set")
                return attr(*args, **kwargs)

            return wrapper
        return attr

    def __repr__(self):
        try:
            serial = self.get_serial()
            variant = self.get_variant().description
        except NotConnected:
            return "<BlinkStick: Not connected>"
        return f"<BlinkStick: Variant={variant} Serial={serial}>"

    def __str__(self):
        try:
            serial = self.get_serial()
            variant = self.get_variant().description
        except NotConnected:
            return "Blinkstick - Not connected"
        return f"{variant} ({serial})"

    def get_serial(self) -> str:
        """
        Returns the serial number of backend.::

            BSnnnnnn-1.0
            ||  |    | |- Software minor version
            ||  |    |--- Software major version
            ||  |-------- Denotes sequential number
            ||----------- Denotes BlinkStick backend

        Software version defines the capabilities of the backend

        @rtype: str
        @return: Serial number of the backend
        """
        return self.backend.get_serial()

    def get_manufacturer(self) -> str:
        """
        Get the manufacturer of the backend

        @rtype: str
        @return: Device manufacturer's name
        """
        return self.backend.get_manufacturer()

    def get_variant(self) -> BlinkStickVariant:
        """
        Get the product variant of the backend.

        @rtype: int
        @return: BlinkStickVariant.UNKNOWN, BlinkStickVariant.BLINKSTICK, BlinkStickVariant.BLINKSTICK_PRO and etc
        """

        return self.backend.get_variant()

    def get_variant_string(self) -> str:
        """
        Get the product variant of the backend as string.

        @rtype: string
        @return: "BlinkStick", "BlinkStick Pro", etc
        """
        return self.get_variant().description

    def get_description(self) -> str:
        """
        Get the description of the backend

        @rtype: str
        @return: Device description
        """
        return self.backend.get_description()

    def set_error_reporting(self, error_reporting: bool) -> None:
        """
        Enable or disable error reporting

        @type  error_reporting: Boolean
        @param error_reporting: display errors if they occur during communication with the backend
        """
        self.error_reporting = error_reporting

    def set_color(
        self,
        channel: int = 0,
        index: int = 0,
        red: int = 0,
        green: int = 0,
        blue: int = 0,
        name: str | None = None,
        hex: str | None = None,
    ) -> None:
        """
        Set the color to the backend as RGB

        @type  channel: int
        @param channel: the channel which to send data to (R=0, G=1, B=2)
        @type  index: int
        @param index: the index of the LED
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

        red, green, blue = self._determine_rgb(
            red=red, green=green, blue=blue, name=name, hex=hex
        )

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
            self.backend.control_transfer(0x20, 0x9, report_id, 0, control_string)
        else:
            try:
                self.backend.control_transfer(0x20, 0x9, report_id, 0, control_string)
            except Exception:
                pass

    def _determine_rgb(
        self,
        red: int = 0,
        green: int = 0,
        blue: int = 0,
        name: str | None = None,
        hex: str | None = None,
    ) -> tuple[int, int, int]:

        try:
            if name:
                # Special case for name="random"
                if name == "random":
                    red = randint(0, 255)
                    green = randint(0, 255)
                    blue = randint(0, 255)
                else:
                    red, green, blue = name_to_rgb(name)
            elif hex:
                red, green, blue = hex_to_rgb(hex)
        except ValueError:
            red = green = blue = 0

        red, green, blue = remap_rgb_value((red, green, blue), self.max_rgb_value)

        # TODO - do smarts to determine input type from red var in case it is not int

        return red, green, blue

    def _get_color_rgb(self, index: int = 0) -> tuple[int, int, int]:
        if index == 0:
            device_bytes = self.backend.control_transfer(
                0x80 | 0x20, 0x1, 0x0001, 0, 33
            )
            if self.inverse:
                return (
                    255 - device_bytes[1],
                    255 - device_bytes[2],
                    255 - device_bytes[3],
                )
            else:
                return device_bytes[1], device_bytes[2], device_bytes[3]
        else:
            data = self.get_led_data((index + 1) * 3)

            return data[index * 3 + 1], data[index * 3], data[index * 3 + 2]

    def _get_color_hex(self, index: int = 0) -> str:
        r, g, b = self._get_color_rgb(index)
        return "#%02x%02x%02x" % (r, g, b)

    def get_color(
        self,
        index: int = 0,
        color_mode: ColorFormat = ColorFormat.RGB,
        color_format: str | None = None,
    ) -> tuple[int, int, int] | str:
        """
                Get the current backend color in the defined format.

                Currently supported formats:

                    1. rgb (default) - Returns values as 3-tuple (r,g,b)
                    2. hex - returns current backend color as hexadecimal string

        import blinkstick.core            >>> b = blinkstick.core.find_first()
                    >>> b.set_color(red=255,green=0,blue=0)
                    >>> (r,g,b) = b.get_color() # Get color as rbg tuple
                    (255,0,0)
                    >>> hex = b.get_color(color_mode=ColorFormat.HEX) # Get color as hex string
                    '#ff0000'

                @type  index: int
                @param index: the index of the LED
                @type  color_mode: ColorFormat
                @param color_mode: the format to return the color in (ColorFormat.RGB or ColorFormat.HEX) - defaults to ColorFormat.RGB
                @type  color_format: str
                @param color_format: "rgb" or "hex". Defaults to "rgb". Deprecated, use color_mode instead.

                @rtype: (int, int, int) or str
                @return: Either 3-tuple for R, G and B values, or hex string
        """
        # color_format is deprecated, and color_mode should be used instead
        # if color_format is specified, then raise a DeprecationWarning, but attempt to convert it to a ColorFormat enum
        # if it's not possible, then default to ColorFormat.RGB, in line with the previous behavior
        if color_format:
            warnings.warn(
                "color_format is deprecated, please use color_mode instead",
                DeprecationWarning,
            )
            try:
                color_mode = ColorFormat.from_name(color_format)
            except ValueError:
                color_mode = ColorFormat.RGB

        color_funcs: dict[ColorFormat, Callable[[int], tuple[int, int, int] | str]] = {
            ColorFormat.RGB: self._get_color_rgb,
            ColorFormat.HEX: self._get_color_hex,
        }

        return color_funcs.get(color_mode, self._get_color_rgb)(index)

    def _determine_report_id(self, led_count: int) -> tuple[int, int]:
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

    def set_led_data(self, channel: int, data: list[int]) -> None:
        """
        Send LED data frame.

        @type  channel: int
        @param channel: the channel which to send data to (R=0, G=1, B=2)
        @type  data: int[0..64*3]
        @param data: The LED data frame in GRB color_mode
        """

        report_id, max_leds = self._determine_report_id(len(data))

        report = [0, channel]

        for i in range(0, max_leds * 3):
            if len(data) > i:
                report.append(data[i])
            else:
                report.append(0)

        self.backend.control_transfer(0x20, 0x9, report_id, 0, bytes(bytearray(report)))

    def get_led_data(self, count: int) -> list[int]:
        """
        Get LED data frame on the backend.

        @type  count: int
        @param count: How much data to retrieve. Can be in the range of 0..64*3
        @rtype: int[0..64*3]
        @return: LED data currently stored in the RAM of the backend
        """

        report_id, max_leds = self._determine_report_id(count)

        device_bytes = self.backend.control_transfer(
            0x80 | 0x20, 0x1, report_id, 0, max_leds * 3 + 2
        )

        return device_bytes[2 : 2 + count * 3]

    def set_mode(self, mode: Mode | int) -> None:
        """
        Set backend mode for BlinkStick Pro. Device currently supports the following modes:

            - 0 - (default) use R, G and B channels to control single RGB LED
            - 1 - same as 0, but inverse mode
            - 2 - control up to 64 WS2812 individual LEDs per each R, G and B channel

        You can find out more about BlinkStick Pro modes:

        U{http://www.blinkstick.com/help/tutorials/blinkstick-pro-modes}

        @type  mode: int
        @param mode: Device mode to set
        """
        # If mode is an enum, get the value
        # this will allow the user to pass in the enum directly, and also gate the value to the enum values
        if not isinstance(mode, int):
            mode = Mode(mode).value
        control_string = bytes(bytearray([4, mode]))

        self.backend.control_transfer(0x20, 0x9, 0x0004, 0, control_string)

    def get_mode(self) -> int:
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

        device_bytes = self.backend.control_transfer(0x80 | 0x20, 0x1, 0x0004, 0, 2)

        if len(device_bytes) >= 2:
            return device_bytes[1]
        else:
            return -1

    def set_led_count(self, count: int) -> None:
        """
        Set number of LEDs for supported devices

        @type  count: int
        @param count: number of LEDs to control
        """
        control_string = bytes(bytearray([0x81, count]))

        self.backend.control_transfer(0x20, 0x9, 0x81, 0, control_string)

    def get_led_count(self) -> int:
        """
        Get number of LEDs for supported devices

        @rtype: int
        @return: Number of LEDs
        """

        device_bytes = self.backend.control_transfer(0x80 | 0x20, 0x1, 0x81, 0, 2)

        if len(device_bytes) >= 2:
            return device_bytes[1]
        else:
            return -1

    def get_info_block1(self) -> str:
        """
        Get the infoblock1 of the backend.

        This is a 32 byte array that can contain any data. It's supposed to
        hold the "Name" of the backend making it easier to identify rather than
        a serial number.

        @rtype: str
        @return: InfoBlock1 currently stored on the backend
        """

        device_bytes = self.backend.control_transfer(0x80 | 0x20, 0x1, 0x0002, 0, 33)
        result = ""
        for i in device_bytes[1:]:
            if i == 0:
                break
            result += chr(i)
        return result

    def get_info_block2(self) -> str:
        """
        Get the infoblock2 of the backend.

        This is a 32 byte array that can contain any data.

        @rtype: str
        @return: InfoBlock2 currently stored on the backend
        """
        device_bytes = self.backend.control_transfer(0x80 | 0x20, 0x1, 0x0003, 0, 33)
        result = ""
        for i in device_bytes[1:]:
            if i == 0:
                break
            result += chr(i)
        return result

    def set_info_block1(self, data: str) -> None:
        """
        Sets the infoblock1 with specified string.

        It fills the rest of 32 bytes with zeros.

        @type  data: str
        @param data: InfoBlock1 for the backend to set
        """
        self.backend.control_transfer(
            0x20, 0x9, 0x0002, 0, string_to_info_block_data(data)
        )

    def set_info_block2(self, data: str) -> None:
        """
        Sets the infoblock2 with specified string.

        It fills the rest of 32 bytes with zeros.

        @type  data: str
        @param data: InfoBlock2 for the backend to set
        """
        self.backend.control_transfer(
            0x20, 0x9, 0x0003, 0, string_to_info_block_data(data)
        )

    def set_random_color(self) -> None:
        """
        Sets random color to the backend.
        """
        self.set_color(name="random")

    def turn_off(self) -> None:
        """
        Turns off LED.
        """
        self.set_color()

    def pulse(
        self,
        channel: int = 0,
        index: int = 0,
        red: int = 0,
        green: int = 0,
        blue: int = 0,
        name: str | None = None,
        hex: str | None = None,
        repeats: int = 1,
        duration: int = 1000,
        steps: int = 50,
    ) -> None:
        """
        Morph to the specified color from black and back again.

        @type  channel: int
        @param channel: the channel which to send data to (R=0, G=1, B=2)
        @type  index: int
        @param index: the index of the LED
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
        self.turn_off()
        for x in range(repeats):
            self.morph(
                channel=channel,
                index=index,
                red=red,
                green=green,
                blue=blue,
                name=name,
                hex=hex,
                duration=duration,
                steps=steps,
            )
            self.morph(
                channel=channel,
                index=index,
                red=0,
                green=0,
                blue=0,
                duration=duration,
                steps=steps,
            )

    def blink(
        self,
        channel: int = 0,
        index: int = 0,
        red: int = 0,
        green: int = 0,
        blue: int = 0,
        name: str | None = None,
        hex: str | None = None,
        repeats: int = 1,
        delay: int = 500,
    ) -> None:
        """
        Blink the specified color.

        @type  channel: int
        @param channel: the channel which to send data to (R=0, G=1, B=2)
        @type  index: int
        @param index: the index of the LED
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
        ms_delay = float(delay) / float(1000)
        for x in range(repeats):
            if x:
                time.sleep(ms_delay)
            self.set_color(
                channel=channel,
                index=index,
                red=red,
                green=green,
                blue=blue,
                name=name,
                hex=hex,
            )
            time.sleep(ms_delay)
            self.set_color(channel=channel, index=index)

    def morph(
        self,
        channel: int = 0,
        index: int = 0,
        red: int = 0,
        green: int = 0,
        blue: int = 0,
        name: str | None = None,
        hex: str | None = None,
        duration: int = 1000,
        steps: int = 50,
    ) -> None:
        """
        Morph to the specified color.

        @type  channel: int
        @param channel: the channel which to send data to (R=0, G=1, B=2)
        @type  index: int
        @param index: the index of the LED
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

        r_end, g_end, b_end = self._determine_rgb(
            red=red, green=green, blue=blue, name=name, hex=hex
        )
        # descale the above values
        r_end, g_end, b_end = remap_rgb_value_reverse(
            (r_end, g_end, b_end), self.max_rgb_value
        )

        r_start, g_start, b_start = remap_rgb_value_reverse(
            self._get_color_rgb(index), self.max_rgb_value
        )

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

        self.set_color(
            channel=channel, index=index, red=r_start, green=g_start, blue=b_start
        )

        for grad in gradient:
            grad_r, grad_g, grad_b = map(int, grad)

            self.set_color(
                channel=channel, index=index, red=grad_r, green=grad_g, blue=grad_b
            )
            time.sleep(ms_delay)

        self.set_color(channel=channel, index=index, red=r_end, green=g_end, blue=b_end)

    def get_inverse(self) -> bool:
        """
        Get the value of inverse mode. This applies only to BlinkStick. Please use L{set_mode} for BlinkStick Pro
        to permanently set the inverse mode to the backend.

        @rtype: bool
        @return: True if inverse mode, otherwise false
        """
        return self.inverse

    def set_inverse(self, value: bool) -> None:
        """
        Set inverse mode. This applies only to BlinkStick. Please use L{set_mode} for BlinkStick Pro
        to permanently set the inverse mode to the backend.

        @type  value: bool
        @param value: True/False to set the inverse mode
        """
        if type(value) is str:
            value = value.lower() == "true"  # type: ignore
        self.inverse = bool(value)

    def set_max_rgb_value(self, value: int) -> None:
        """
        Set RGB color limit. {set_color} function will automatically remap
        the values to maximum supplied.

        @type  value: int
        @param value: 0..255 maximum value for each R, G and B color
        """
        # convert to int and clamp to 0..255
        value = max(0, min(255, int(value)))
        self.max_rgb_value = value

    def get_max_rgb_value(self) -> int:
        """
        Get RGB color limit. {set_color} function will automatically remap
        the values to maximum set.

        @rtype: int
        @return: 0..255 maximum value for each R, G and B color
        """
        return self.max_rgb_value
