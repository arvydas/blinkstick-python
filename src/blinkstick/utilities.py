def string_to_info_block_data(data: str) -> bytes:
    """
    Helper method to convert a string to byte array of 32 bytes.

    @type  data: str
    @param data: The data to convert to byte array

    @rtype: byte[32]
    @return: It fills the rest of bytes with zeros.
    """
    info_block_data = data[:31]
    byte_array = bytearray([1] + [0] * 31)

    for i, c in enumerate(info_block_data):
        byte_array[i + 1] = ord(c)

    return bytes(byte_array)
