from dataclasses import dataclass, field
from typing import Generic, TypeVar

from blinkstick.enums import BlinkStickVariant
from blinkstick.models import SerialDetails

T = TypeVar("T")


@dataclass
class BlinkStickDevice(Generic[T]):
    """A BlinkStick device representation"""

    raw_device: T
    serial_details: SerialDetails
    manufacturer: str
    version_attribute: int
    description: str
    major_version: int = field(init=False)
    variant: BlinkStickVariant = field(init=False)

    def __post_init__(self):
        self.major_version = self.serial_details.major_version
        self.variant = BlinkStickVariant.from_version_attrs(
            major_version=self.serial_details.major_version,
            version_attribute=self.version_attribute,
        )
