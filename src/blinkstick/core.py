from __future__ import annotations

import sys
from importlib.metadata import version
from typing import TYPE_CHECKING


if sys.platform == "win32":
    from blinkstick.backends.win32 import Win32Backend as USBBackend
else:
    from blinkstick.backends.unix_like import UnixLikeBackend as USBBackend

if TYPE_CHECKING:
    from blinkstick.clients import BlinkStick


def find_all() -> list[BlinkStick]:
    """
    Find all attached BlinkStick devices.

    @rtype: BlinkStick[]
    @return: a list of BlinkStick objects or None if no devices found
    """
    from blinkstick.clients import BlinkStick

    result: list[BlinkStick] = []
    if (found_devices := USBBackend.get_attached_blinkstick_devices()) is None:
        return result
    for d in found_devices:
        result.extend([BlinkStick(device=d)])

    return result


def find_first() -> BlinkStick | None:
    """
    Find first attached BlinkStick.

    @rtype: BlinkStick
    @return: BlinkStick object or None if no devices are found
    """
    from blinkstick.clients import BlinkStick

    blinkstick_devices = USBBackend.get_attached_blinkstick_devices(find_all=False)

    if blinkstick_devices:
        return BlinkStick(device=blinkstick_devices[0])

    return None


def find_by_serial(serial: str = "") -> BlinkStick | None:
    """
    Find BlinkStick backend based on serial number.

    @rtype: BlinkStick
    @return: BlinkStick object or None if no devices are found
    """

    devices = USBBackend.find_by_serial(serial=serial)

    if devices:
        return BlinkStick(device=devices[0])

    return None


def get_blinkstick_package_version() -> str:
    return version("blinkstick")
