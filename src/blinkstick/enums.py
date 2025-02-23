from __future__ import annotations

from enum import Enum, IntEnum


class BlinkStickVariant(Enum):
    UNKNOWN = (0, "Unknown")
    BLINKSTICK = (1, "BlinkStick")
    BLINKSTICK_PRO = (2, "BlinkStick Pro")
    BLINKSTICK_STRIP = (3, "BlinkStick Strip")
    BLINKSTICK_SQUARE = (4, "BlinkStick Square")
    BLINKSTICK_NANO = (5, "BlinkStick Nano")
    BLINKSTICK_FLEX = (6, "BlinkStick Flex")

    @property
    def value(self) -> int:
        return self._value_[0]

    @property
    def description(self) -> str:
        return self._value_[1]

    @staticmethod
    def from_version_attrs(
        major_version: int, version_attribute: int | None
    ) -> "BlinkStickVariant":
        if major_version == 1:
            return BlinkStickVariant.BLINKSTICK
        elif major_version == 2:
            return BlinkStickVariant.BLINKSTICK_PRO
        elif major_version == 3:
            if version_attribute == 0x200:
                return BlinkStickVariant.BLINKSTICK_SQUARE
            elif version_attribute == 0x201:
                return BlinkStickVariant.BLINKSTICK_STRIP
            elif version_attribute == 0x202:
                return BlinkStickVariant.BLINKSTICK_NANO
            elif version_attribute == 0x203:
                return BlinkStickVariant.BLINKSTICK_FLEX
        return BlinkStickVariant.UNKNOWN


class Mode(IntEnum):
    RGB = 1
    RGB_INVERSE = 2
    ADDRESSABLE = 3
