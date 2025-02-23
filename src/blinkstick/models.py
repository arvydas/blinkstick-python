import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SerialDetails:
    """
    A BlinkStick serial number representation.

        BSnnnnnn-1.0
        ||  |    | |- Software minor version
        ||  |    |--- Software major version
        ||  |-------- Denotes sequential number
        ||----------- Denotes BlinkStick backend


    """

    serial: str
    major_version: int = field(init=False)
    minor_version: int = field(init=False)
    sequence_number: int = field(init=False)

    def __post_init__(self):
        serial_number_regex = r"BS(\d+)-(\d+)\.(\d+)"
        match = re.match(serial_number_regex, self.serial)
        if not match:
            raise ValueError(f"Invalid serial number: {self.serial}")

        object.__setattr__(self, "sequence_number", int(match.group(1)))
        object.__setattr__(self, "major_version", int(match.group(2)))
        object.__setattr__(self, "minor_version", int(match.group(3)))
