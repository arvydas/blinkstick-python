from __future__ import annotations


class BlinkStickException(Exception):
    pass


class NotConnected(BlinkStickException):
    pass


class USBBackendNotAvailable(BlinkStickException):
    pass
