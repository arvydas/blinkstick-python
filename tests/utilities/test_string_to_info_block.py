from blinkstick.utilities import string_to_info_block_data


def test_string_to_info_block_data_converts_string_to_byte_array():
    block_string = "hello"
    expected_padding_length = 31 - len(block_string)
    result = string_to_info_block_data("hello")
    expected = b"\x01hello" + b"\x00" * expected_padding_length
    assert result == expected


def test_string_to_info_block_data_handles_empty_string():
    result = string_to_info_block_data("")
    expected = b"\x01" + b"\x00" * 31
    assert result == expected


def test_string_to_info_block_data_truncates_long_string():
    long_string = "a" * 40
    result = string_to_info_block_data(long_string)
    expected = b"\x01" + b"a" * 31
    assert result == expected


def test_string_to_info_block_data_handles_exact_31_characters():
    exact_string = "a" * 31
    result = string_to_info_block_data(exact_string)
    expected = b"\x01" + b"a" * 31
    assert result == expected
