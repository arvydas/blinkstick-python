from __future__ import annotations

import usb.core  # type: ignore
import usb.util  # type: ignore

from blinkstick.constants import VENDOR_ID, PRODUCT_ID
from blinkstick.backends.base import BaseBackend
from blinkstick.devices import BlinkStickDevice
from blinkstick.exceptions import BlinkStickException, USBBackendNotAvailable
from blinkstick.models import SerialDetails


class UnixLikeBackend(BaseBackend[usb.core.Device]):
    def __init__(self, device: BlinkStickDevice[usb.core.Device]):
        super().__init__(device=device)
        if device:
            self.open_device()

    def open_device(self) -> None:
        if self.blinkstick_device is None:
            raise BlinkStickException("Could not find BlinkStick...")

        if self.blinkstick_device.raw_device.is_kernel_driver_active(0):
            try:
                self.blinkstick_device.raw_device.detach_kernel_driver(0)
            except usb.core.USBError as e:
                raise BlinkStickException("Could not detach kernel driver: %s" % str(e))

    def _refresh_attached_blinkstick_device(self):
        if not self.blinkstick_device:
            return False
        if devices := self.find_by_serial(self.blinkstick_device.serial_details.serial):
            self.blinkstick_device = devices[0]
            self.open_device()
            return True

    @staticmethod
    def get_attached_blinkstick_devices(
        find_all: bool = True,
    ) -> list[BlinkStickDevice[usb.core.Device]]:
        try:
            raw_devices = (
                usb.core.find(
                    find_all=find_all, idVendor=VENDOR_ID, idProduct=PRODUCT_ID
                )
                or []
            )
        except usb.core.NoBackendError:
            # TODO: improve this error message to provide more information on how to remediate the problem
            raise USBBackendNotAvailable(
                "Could not find USB backend. Is libusb installed?"
            )

        try:
            devices = [
                # TODO: refactor this to DRY up the usb.util.get_string calls
                BlinkStickDevice(
                    raw_device=device,
                    serial_details=SerialDetails(
                        serial=str(usb.util.get_string(device, 3, 1033))
                    ),
                    manufacturer=str(usb.util.get_string(device, 1, 1033)),
                    version_attribute=device.bcdDevice,
                    description=str(usb.util.get_string(device, 2, 1033)),
                )
                for device in raw_devices
            ]
        except usb.core.USBError as e:
            # if the error is due to a permission issue, raise a more specific exception
            if "Operation not permitted" in str(e):
                raise USBBackendNotAvailable(
                    "Permission denied accessing USB backend. Does a udev rule need to be added?"
                )
            raise
        return devices

    @staticmethod
    def find_by_serial(serial: str) -> list[BlinkStickDevice[usb.core.Device]] | None:
        found_devices = UnixLikeBackend.get_attached_blinkstick_devices()
        for d in found_devices:
            if d.serial_details.serial == serial:
                return [d]

        return None

    def control_transfer(
        self,
        bmRequestType: int,
        bRequest: int,
        wValue: int,
        wIndex: int,
        data_or_wLength: bytes | int,
    ):
        try:
            return self.blinkstick_device.raw_device.ctrl_transfer(
                bmRequestType, bRequest, wValue, wIndex, data_or_wLength
            )
        except usb.USBError:
            # Could not communicate with BlinkStick backend
            # attempt to find it again based on serial

            if self._refresh_attached_blinkstick_device():
                return self.blinkstick_device.raw_device.ctrl_transfer(
                    bmRequestType, bRequest, wValue, wIndex, data_or_wLength
                )
            else:
                raise BlinkStickException(
                    "Could not communicate with BlinkStick {0} - it may have been removed".format(
                        self.blinkstick_device.serial_details.serial
                    )
                )
