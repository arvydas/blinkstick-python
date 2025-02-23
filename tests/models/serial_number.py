import pytest
from blinkstick.models import SerialDetails


def test_serial_number_initialization():
    serial = "BS123456-1.0"
    serial_number = SerialDetails(serial=serial)

    assert serial_number.serial == serial
    assert serial_number.sequence_number == 123456
    assert serial_number.major_version == 1
    assert serial_number.minor_version == 0


def test_serial_number_invalid_serial():
    with pytest.raises(ValueError, match="Invalid serial number: BS123456"):
        SerialDetails(serial="BS123456")
