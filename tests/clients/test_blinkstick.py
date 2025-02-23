from unittest.mock import MagicMock

import pytest

from blinkstick.colors import ColorFormat
from blinkstick.enums import BlinkStickVariant, Mode
from blinkstick.clients.blinkstick import BlinkStick
from pytest_mock import MockFixture

from blinkstick.exceptions import NotConnected
from tests.conftest import make_blinkstick


def test_instantiate():
    """Test that we can instantiate a BlinkStick object."""
    bs = BlinkStick()
    assert bs is not None


def test_all_methods_require_backend():
    """Test that all methods require a backend."""
    # Create an instance of BlinkStick. Note that we do not use the mock, or pass a device.
    # This is deliberate, as we want to test that all methods raise an exception when the backend is not set.
    bs = BlinkStick()

    class_methods = (
        method
        for method in dir(BlinkStick)
        if callable(getattr(bs, method)) and not method.startswith("__")
    )
    for method_name in class_methods:
        method = getattr(bs, method_name)
        with pytest.raises(NotConnected):
            method()


@pytest.mark.parametrize(
    "serial, version_attribute, expected_variant, expected_variant_value",
    [
        ("BS12345-1.0", 0x0000, BlinkStickVariant.BLINKSTICK, 1),
        ("BS12345-2.0", 0x0000, BlinkStickVariant.BLINKSTICK_PRO, 2),
        (
            "BS12345-3.0",
            0x200,
            BlinkStickVariant.BLINKSTICK_SQUARE,
            4,
        ),  # major version 3, version attribute 0x200 is BlinkStickSquare
        (
            "BS12345-3.0",
            0x201,
            BlinkStickVariant.BLINKSTICK_STRIP,
            3,
        ),  # major version 3 is BlinkStickStrip
        ("BS12345-3.0", 0x202, BlinkStickVariant.BLINKSTICK_NANO, 5),
        ("BS12345-3.0", 0x203, BlinkStickVariant.BLINKSTICK_FLEX, 6),
        ("BS12345-4.0", 0x0000, BlinkStickVariant.UNKNOWN, 0),
        ("BS12345-3.0", 0x9999, BlinkStickVariant.UNKNOWN, 0),
        ("BS12345-0.0", 0x0000, BlinkStickVariant.UNKNOWN, 0),
    ],
    ids=[
        "v1==BlinkStick",
        "v2==BlinkStickPro",
        "v3,0x200==BlinkStickSquare",
        "v3,0x201==BlinkStickStrip",
        "v3,0x202==BlinkStickNano",
        "v3,0x203==BlinkStickFlex",
        "v4==Unknown",
        "v3,Unknown==Unknown",
        "v0,0==Unknown",
    ],
)
def test_get_variant(
    make_blinkstick, serial, version_attribute, expected_variant, expected_variant_value
):
    bs = make_blinkstick()
    synthesised_variant = BlinkStickVariant.from_version_attrs(
        int(serial[-3]), version_attribute
    )
    bs.backend.get_variant = MagicMock(return_value=synthesised_variant)
    assert bs.get_variant() == expected_variant
    assert bs.get_variant().value == expected_variant_value


@pytest.mark.parametrize(
    "expected_variant, expected_name",
    [
        (BlinkStickVariant.BLINKSTICK, "BlinkStick"),
        (BlinkStickVariant.BLINKSTICK_PRO, "BlinkStick Pro"),
        (BlinkStickVariant.BLINKSTICK_STRIP, "BlinkStick Strip"),
        (BlinkStickVariant.BLINKSTICK_SQUARE, "BlinkStick Square"),
        (BlinkStickVariant.BLINKSTICK_NANO, "BlinkStick Nano"),
        (BlinkStickVariant.BLINKSTICK_FLEX, "BlinkStick Flex"),
        (BlinkStickVariant.UNKNOWN, "Unknown"),
    ],
    ids=[
        "1==BlinkStick",
        "2==BlinkStickPro",
        "3==BlinkStickStrip",
        "4==BlinkStickSquare",
        "5==BlinkStickNano",
        "6==BlinkStickFlex",
        "0==Unknown",
    ],
)
def test_get_variant_string(make_blinkstick, expected_variant, expected_name):
    """Test get_variant method for version 0 returns BlinkStick.UNKNOWN (0)"""
    bs = make_blinkstick()
    bs.get_variant = MagicMock(return_value=expected_variant)
    assert bs.get_variant_string() == expected_name


def test_get_color_rgb_color_format(mocker: MockFixture, make_blinkstick):
    """Test get_color with color_format='rgb'. We expect it to return the color in RGB format."""
    bs = make_blinkstick()
    mock_get_color_rgb = mocker.Mock(return_value=(255, 0, 0))
    bs._get_color_rgb = mock_get_color_rgb
    assert bs.get_color() == (255, 0, 0)
    assert mock_get_color_rgb.call_count == 1


def test_get_color_hex_color_format(mocker: MockFixture, make_blinkstick):
    """Test get_color with color_format='hex'. We expect it to return the color in hex format."""
    bs = make_blinkstick()
    mock_get_color_hex = mocker.Mock(return_value="#ff0000")
    bs._get_color_hex = mock_get_color_hex
    assert bs.get_color(color_format="hex") == "#ff0000"
    assert mock_get_color_hex.call_count == 1


def test_get_color_invalid_color_format(mocker: MockFixture, make_blinkstick):
    """Test get_color with invalid color_format. We expect it not to raise an exception, but to default to RGB."""
    bs = make_blinkstick()
    mock_get_color_rgb = mocker.Mock(return_value=(255, 0, 0))
    bs._get_color_rgb = mock_get_color_rgb
    bs.get_color(color_format="invalid_format")
    assert mock_get_color_rgb.call_count == 1


def test_max_rgb_value_default(make_blinkstick):
    """Test that the default max_rgb_value is 255."""
    bs = make_blinkstick()
    assert bs.get_max_rgb_value() == 255


def test_max_rgb_value_not_class_attribute(make_blinkstick):
    """Test that the max_rgb_value is not a class attribute."""
    bs = make_blinkstick()
    assert not hasattr(BlinkStick, "max_rgb_value")
    assert hasattr(bs, "max_rgb_value")


def test_set_and_get_max_rgb_value(make_blinkstick):
    """Test that we can set and get the max_rgb_value."""
    # Create multiple instances of BlinkStick using the fixture
    bs = make_blinkstick()

    # Set different max_rgb_value for each instance
    bs.set_max_rgb_value(100)

    # Assert that each instance has its own max_rgb_value
    assert bs.get_max_rgb_value() == 100

    # Change the max_rgb_value again to ensure independence
    bs.set_max_rgb_value(150)

    # Assert the new values
    assert bs.get_max_rgb_value() == 150


def test_set_max_rgb_value_bounds(make_blinkstick):
    """Test that set_max_rgb_value performs bounds checking."""
    bs = make_blinkstick()

    # Test setting a value within bounds
    bs.set_max_rgb_value(100)
    assert bs.get_max_rgb_value() == 100

    # Test setting a value below the lower bound
    bs.set_max_rgb_value(-1)
    assert bs.get_max_rgb_value() == 0

    # Test setting a value above the upper bound
    bs.set_max_rgb_value(256)
    assert bs.get_max_rgb_value() == 255


def test_set_max_rgb_value_type_checking(make_blinkstick):
    """Test that set_max_rgb_value performs type checking and coercion."""
    bs = make_blinkstick()

    # Test setting a valid integer value
    bs.set_max_rgb_value(100)
    assert bs.get_max_rgb_value() == 100

    # Test setting a value that can be coerced to an integer
    bs.set_max_rgb_value("150")
    assert bs.get_max_rgb_value() == 150

    # Test setting a value that cannot be coerced to an integer
    with pytest.raises(ValueError):
        bs.set_max_rgb_value("invalid")

    # Test setting a float value
    bs.set_max_rgb_value(100.5)
    assert bs.get_max_rgb_value() == 100


def test_inverse_default(make_blinkstick):
    """Test that the default inverse is False."""
    bs = make_blinkstick()
    assert bs.get_inverse() == False


def test_inverse_not_class_attribute(make_blinkstick):
    """Test that the inverse is not a class attribute."""
    bs = make_blinkstick()
    assert not hasattr(BlinkStick, "inverse")
    assert hasattr(bs, "inverse")


@pytest.mark.parametrize(
    "input_value, expected_result",
    [
        pytest.param(True, True, id="True==True"),
        pytest.param(False, False, id="False==False"),
    ],
)
def test_inverse_set_and_get(make_blinkstick, input_value, expected_result):
    """Test that we can set and get the inverse."""
    bs = make_blinkstick()
    bs.set_inverse(input_value)
    assert bs.get_inverse() == expected_result


@pytest.mark.parametrize(
    "input_value, expected_result",
    [
        pytest.param(True, True, id="True==True"),
        pytest.param("True", True, id="StringTrue==True"),
        pytest.param(1.0, True, id="1.0==True"),
        pytest.param(0, False, id="0==False"),
        pytest.param("False", False, id="StringFalse==False"),
        pytest.param(False, False, id="False==False"),
        pytest.param(0.0, False, id="0.0==False"),
        pytest.param("", False, id="EmptyString==False"),
        pytest.param([], False, id="EmptyList==False"),
        pytest.param({}, False, id="EmptyDict==False"),
        pytest.param(None, False, id="None==False"),
    ],
)
def test_set_inverse_type_checking(make_blinkstick, input_value, expected_result):
    """Test that set_inverse performs type checking and coercion."""
    bs = make_blinkstick()
    bs.set_inverse(input_value)
    assert bs.get_inverse() == expected_result


@pytest.mark.parametrize(
    "color_mode, ctrl_transfer_bytes, color, inverse, expected_color",
    [
        pytest.param(
            ColorFormat.RGB,
            (0, 255, 0, 0),
            (255, 0, 0),
            False,
            (255, 0, 0),
            id="RGB, NoInverse",
        ),
        pytest.param(
            ColorFormat.HEX,
            (0, 255, 0, 0),
            "#ff0000",
            False,
            "#ff0000",
            id="Hex, NoInverse",
        ),
        pytest.param(
            ColorFormat.RGB,
            (0, 255, 0, 0),
            (255, 0, 0),
            True,
            (0, 255, 255),
            id="RGB, Inverse",
        ),
        pytest.param(
            ColorFormat.HEX,
            (0, 255, 0, 0),
            "#ff0000",
            True,
            "#00ffff",
            id="Hex, Inverse",
        ),
    ],
)
def test_inverse_correctly_inverts_rgb_color(
    make_blinkstick, color_mode, ctrl_transfer_bytes, color, inverse, expected_color
):
    """Test that the color is correctly inverted when the inverse flag is set."""
    bs = make_blinkstick()
    # mock the backend control_transfer method to return the 3 bytes of the color
    bs.backend.control_transfer = MagicMock(return_value=ctrl_transfer_bytes)

    bs.set_inverse(inverse)
    assert bs.get_color(color_mode=color_mode) == expected_color


def test_inverse_does_not_affect_max_rgb_value(make_blinkstick):
    """Test that the inverse flag does not affect the max_rgb_value."""
    bs = make_blinkstick()
    bs.set_max_rgb_value(100)
    bs.set_inverse(True)
    assert bs.get_max_rgb_value() == 100


@pytest.mark.parametrize(
    "mode, is_valid",
    [
        (1, True),
        (2, True),
        (3, True),
        (4, False),
        (-1, False),
        (Mode.RGB, True),
        (Mode.RGB_INVERSE, True),
        (Mode.ADDRESSABLE, True),
    ],
)
def test_set_mode_raises_on_invalid_mode(make_blinkstick, mode, is_valid):
    """Test that set_mode raises an exception when an invalid mode is passed."""
    bs = make_blinkstick()
    if is_valid:
        bs.set_mode(mode)
    else:
        with pytest.raises(ValueError):
            bs.set_mode("invalid_mode")  # noqa
