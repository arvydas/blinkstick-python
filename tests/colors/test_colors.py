import pytest

from blinkstick.colors import (
    remap,
    remap_color,
    remap_color_reverse,
    remap_rgb_value,
    remap_rgb_value_reverse,
    Color,
    name_to_hex,
    normalize_hex,
    hex_to_rgb,
    name_to_rgb,
)


def test_remap_value_within_range():
    assert remap(5, 0, 10, 0, 100) == 50


def test_remap_value_at_minimum():
    assert remap(0, 0, 10, 0, 100) == 0


def test_remap_value_at_maximum():
    assert remap(10, 0, 10, 0, 100) == 100


def test_remap_value_below_minimum():
    assert remap(-5, 0, 10, 0, 100) == -50


def test_remap_value_above_maximum():
    assert remap(15, 0, 10, 0, 100) == 150


def test_remap_value_within_negative_range():
    assert remap(-5, -10, 0, -100, 0) == -50


def test_remap_value_within_reverse_range():
    assert remap(5, 0, 10, 100, 0) == 50


def test_remap_color_value_within_range():
    assert remap_color(128, 100) == 50


def test_remap_color_value_at_minimum():
    assert remap_color(0, 100) == 0


def test_remap_color_value_at_maximum():
    assert remap_color(255, 100) == 100


def test_remap_color_value_below_minimum():
    # note: this returns -3 because of the way the remap function is implemented using int(), which always rounds down
    assert remap_color(-10, 100) == -3


def test_remap_color_value_above_maximum():
    assert remap_color(300, 100) == 117


def test_remap_color_reverse_value_within_range():
    assert remap_color_reverse(50, 100) == 127


def test_remap_color_reverse_value_at_minimum():
    assert remap_color_reverse(0, 100) == 0


def test_remap_color_reverse_value_at_maximum():
    assert remap_color_reverse(100, 100) == 255


def test_remap_color_reverse_value_below_minimum():
    assert remap_color_reverse(-10, 100) == -25


def test_remap_color_reverse_value_above_maximum():
    assert remap_color_reverse(150, 100) == 382


def test_remap_rgb_value_within_range():
    assert remap_rgb_value((128, 128, 128), 100) == (50, 50, 50)


def test_remap_rgb_value_at_minimum():
    assert remap_rgb_value((0, 0, 0), 100) == (0, 0, 0)


def test_remap_rgb_value_at_maximum():
    assert remap_rgb_value((255, 255, 255), 100) == (100, 100, 100)


def test_remap_rgb_value_below_minimum():
    assert remap_rgb_value((-10, -10, -10), 100) == (-3, -3, -3)


def test_remap_rgb_value_above_maximum():
    assert remap_rgb_value((300, 300, 300), 100) == (117, 117, 117)


def test_remap_rgb_value_reverse_within_range():
    assert remap_rgb_value_reverse((50, 50, 50), 100) == (127, 127, 127)


def test_remap_rgb_value_reverse_at_minimum():
    assert remap_rgb_value_reverse((0, 0, 0), 100) == (0, 0, 0)


def test_remap_rgb_value_reverse_at_maximum():
    assert remap_rgb_value_reverse((100, 100, 100), 100) == (255, 255, 255)


def test_remap_rgb_value_reverse_below_minimum():
    assert remap_rgb_value_reverse((-10, -10, -10), 100) == (-25, -25, -25)


def test_remap_rgb_value_reverse_above_maximum():
    assert remap_rgb_value_reverse((150, 150, 150), 100) == (382, 382, 382)


def test_all_colors_present(w3c_colors):
    assert len(w3c_colors) == len(Color)


def test_color_from_name_valid_color(w3c_colors):
    for color_name, _ in w3c_colors:
        assert Color.from_name(color_name) == Color[color_name.upper()]


def test_color_from_name_invalid_color():
    with pytest.raises(
        ValueError, match="'invalidcolor' is not defined as a named color."
    ):
        Color.from_name("invalidcolor")


def test_color_from_name_case_insensitive(w3c_colors):
    for color_name, _ in w3c_colors:
        assert Color.from_name(color_name.upper()) == Color[color_name.upper()]
        assert Color.from_name(color_name.lower()) == Color[color_name.upper()]


def test_color_name_to_hex(w3c_colors):
    for color_name, color_hex in w3c_colors:
        assert name_to_hex(color_name) == color_hex


def test_name_to_rgb_white():
    assert name_to_rgb("white") == (255, 255, 255)


def test_name_to_rgb_navy():
    assert name_to_rgb("navy") == (0, 0, 128)


def test_name_to_rgb_goldenrod():
    assert name_to_rgb("goldenrod") == (218, 165, 32)


def test_name_to_rgb_invalid_color():
    with pytest.raises(
        ValueError, match="'invalidcolor' is not defined as a named color."
    ):
        name_to_rgb("invalidcolor")


def test_normalize_hex_valid_six_digit_lowercase():
    assert normalize_hex("#0099cc") == "#0099cc"


def test_normalize_hex_valid_six_digit_uppercase():
    assert normalize_hex("#0099CC") == "#0099cc"


def test_normalize_hex_valid_three_digit_lowercase():
    assert normalize_hex("#09c") == "#0099cc"


def test_normalize_hex_valid_three_digit_uppercase():
    assert normalize_hex("#09C") == "#0099cc"


def test_normalize_hex_missing_hash():
    with pytest.raises(
        ValueError, match="'0099cc' is not a valid hexadecimal color value."
    ):
        normalize_hex("0099cc")


def test_hex_to_rgb_valid_six_digit_lowercase():
    assert hex_to_rgb("#0099cc") == (0, 153, 204)


def test_hex_to_rgb_valid_six_digit_uppercase():
    assert hex_to_rgb("#0099CC") == (0, 153, 204)


def test_hex_to_rgb_valid_three_digit_lowercase():
    assert hex_to_rgb("#09c") == (0, 153, 204)


def test_hex_to_rgb_valid_three_digit_uppercase():
    assert hex_to_rgb("#09C") == (0, 153, 204)


def test_hex_to_rgb_missing_hash():
    with pytest.raises(
        ValueError, match="'0099cc' is not a valid hexadecimal color value."
    ):
        hex_to_rgb("0099cc")


def test_hex_to_rgb_invalid_hex():
    with pytest.raises(
        ValueError, match="'#xyz' is not a valid hexadecimal color value."
    ):
        hex_to_rgb("#xyz")
