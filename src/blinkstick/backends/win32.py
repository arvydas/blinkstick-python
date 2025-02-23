from __future__ import annotations

import sys
from ctypes import *

from pywinusb import hid  # type: ignore

from blinkstick.constants import VENDOR_ID, PRODUCT_ID
from blinkstick.backends.base import BaseBackend
from blinkstick.devices import BlinkStickDevice
from blinkstick.exceptions import BlinkStickException
from blinkstick.models import SerialDetails


class Win32Backend(BaseBackend[hid.HidDevice]):
    reports: list[hid.core.HidReport]

    def __init__(self, device: BlinkStickDevice[hid.HidDevice]):
        super().__init__(device=device)
        if device:
            self.blinkstick_device.raw_device.open()
            self.reports = self.blinkstick_device.raw_device.find_feature_reports()
            self.serial = self.get_serial()

    @staticmethod
    def find_by_serial(serial: str) -> list[BlinkStickDevice[hid.HidDevice]] | None:
        found_devices = Win32Backend.get_attached_blinkstick_devices()
        for d in found_devices:
            if d.serial_details.serial == serial:
                return [d]

        return None

    def _refresh_attached_blinkstick_device(self):
        # TODO This is weird semantics. fix up return values to be more sensible
        if not self.blinkstick_device:
            return False
        if devices := self.find_by_serial(self.blinkstick_device.serial_details.serial):
            self.blinkstick_device = devices[0]
            self.blinkstick_device.raw_device.open()
            self.reports = self.blinkstick_device.raw_device.find_feature_reports()
            return True

    @staticmethod
    def get_attached_blinkstick_devices(
        find_all: bool = True,
    ) -> list[BlinkStickDevice[hid.HidDevice]]:
        devices = hid.HidDeviceFilter(
            vendor_id=VENDOR_ID, product_id=PRODUCT_ID
        ).get_devices()

        blinkstick_devices = [
            BlinkStickDevice(
                raw_device=device,
                serial_details=SerialDetails(serial=device.serial_number),
                manufacturer=device.vendor_name,
                version_attribute=device.version_number,
                description=device.product_name,
            )
            for device in devices
        ]
        if find_all:
            return blinkstick_devices

        return blinkstick_devices[:1]

    def control_transfer(
        self, bmRequestType, bRequest, wValue, wIndex, data_or_wLength
    ):
        if bmRequestType == 0x20:
            if sys.version_info[0] < 3:
                data = (c_ubyte * len(data_or_wLength))(
                    *[c_ubyte(ord(c)) for c in data_or_wLength]
                )
            else:
                data = (c_ubyte * len(data_or_wLength))(
                    *[c_ubyte(c) for c in data_or_wLength]
                )
            data[0] = wValue
            if not self.blinkstick_device.raw_device.send_feature_report(data):
                if self._refresh_attached_blinkstick_device():
                    self.blinkstick_device.raw_device.send_feature_report(data)
                else:
                    raise BlinkStickException(
                        "Could not communicate with BlinkStick {0} - it may have been removed".format(
                            self.serial
                        )
                    )

        elif bmRequestType == 0x80 | 0x20:
            return self.reports[wValue - 1].get()
