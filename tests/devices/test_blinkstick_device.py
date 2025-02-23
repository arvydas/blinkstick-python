import pytest
from blinkstick.enums import BlinkStickVariant
from blinkstick.models import SerialDetails
from blinkstick.devices.device import BlinkStickDevice


@pytest.fixture
def make_serial_details():
    def _serial_details(serial: str = "BS123456-1.0") -> SerialDetails:
        return SerialDetails(serial=serial)

    return _serial_details


@pytest.fixture
def make_blinkstick_device(mocker, make_serial_details):
    def _make_blinkstick_device(
        manufacturer: str = "Test Manufacturer",
        version_attribute: int = 1,
        description: str = "Test Description",
        serial_number: str = "BS123456-1.0",
    ):
        return BlinkStickDevice(
            raw_device=mocker.MagicMock(),
            serial_details=make_serial_details(serial=serial_number),
            manufacturer=manufacturer,
            version_attribute=version_attribute,
            description=description,
        )

    return _make_blinkstick_device


def test_blinkstick_device_initialization(make_blinkstick_device):
    blinkstick_device = make_blinkstick_device(
        manufacturer="Test Manufacturer",
        version_attribute=1,
        description="Test Description",
    )
    assert blinkstick_device.manufacturer == "Test Manufacturer"
    assert blinkstick_device.version_attribute == 1
    assert blinkstick_device.description == "Test Description"
    assert blinkstick_device.serial_details.serial == "BS123456-1.0"


def test_blinkstick_device_variant(make_blinkstick_device):
    manufacturer = "Test Manufacturer"
    version_attribute = 1
    description = "Test Description"
    serial_number = "BS123456-1.0"

    blinkstick_device = make_blinkstick_device(
        manufacturer=manufacturer,
        version_attribute=version_attribute,
        description=description,
    )
    assert blinkstick_device.variant == BlinkStickVariant.from_version_attrs(
        major_version=1,  #  major version is 1 from the serial number
        version_attribute=version_attribute,
    )
