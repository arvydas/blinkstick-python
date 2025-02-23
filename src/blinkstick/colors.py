import re
from enum import Enum, auto

HEX_COLOR_RE = re.compile(r"^#([a-fA-F0-9]{3}|[a-fA-F0-9]{6})$")


class Color(Enum):
    ALICEBLUE = "#f0f8ff"
    ANTIQUEWHITE = "#faebd7"
    AQUA = "#00ffff"
    AQUAMARINE = "#7fffd4"
    AZURE = "#f0ffff"
    BEIGE = "#f5f5dc"
    BISQUE = "#ffe4c4"
    BLACK = "#000000"
    BLANCHEDALMOND = "#ffebcd"
    BLUE = "#0000ff"
    BLUEVIOLET = "#8a2be2"
    BROWN = "#a52a2a"
    BURLYWOOD = "#deb887"
    CADETBLUE = "#5f9ea0"
    CHARTREUSE = "#7fff00"
    CHOCOLATE = "#d2691e"
    CORAL = "#ff7f50"
    CORNFLOWERBLUE = "#6495ed"
    CORNSILK = "#fff8dc"
    CRIMSON = "#dc143c"
    CYAN = "#00ffff"
    DARKBLUE = "#00008b"
    DARKCYAN = "#008b8b"
    DARKGOLDENROD = "#b8860b"
    DARKGRAY = "#a9a9a9"
    DARKGREY = "#a9a9a9"
    DARKGREEN = "#006400"
    DARKKHAKI = "#bdb76b"
    DARKMAGENTA = "#8b008b"
    DARKOLIVEGREEN = "#556b2f"
    DARKORANGE = "#ff8c00"
    DARKORCHID = "#9932cc"
    DARKRED = "#8b0000"
    DARKSALMON = "#e9967a"
    DARKSEAGREEN = "#8fbc8f"
    DARKSLATEBLUE = "#483d8b"
    DARKSLATEGRAY = "#2f4f4f"
    DARKSLATEGREY = "#2f4f4f"
    DARKTURQUOISE = "#00ced1"
    DARKVIOLET = "#9400d3"
    DEEPPINK = "#ff1493"
    DEEPSKYBLUE = "#00bfff"
    DIMGRAY = "#696969"
    DIMGREY = "#696969"
    DODGERBLUE = "#1e90ff"
    FIREBRICK = "#b22222"
    FLORALWHITE = "#fffaf0"
    FORESTGREEN = "#228b22"
    FUCHSIA = "#ff00ff"
    GAINSBORO = "#dcdcdc"
    GHOSTWHITE = "#f8f8ff"
    GOLD = "#ffd700"
    GOLDENROD = "#daa520"
    GRAY = "#808080"
    GREY = "#808080"
    GREEN = "#008000"
    GREENYELLOW = "#adff2f"
    HONEYDEW = "#f0fff0"
    HOTPINK = "#ff69b4"
    INDIANRED = "#cd5c5c"
    INDIGO = "#4b0082"
    IVORY = "#fffff0"
    KHAKI = "#f0e68c"
    LAVENDER = "#e6e6fa"
    LAVENDERBLUSH = "#fff0f5"
    LAWNGREEN = "#7cfc00"
    LEMONCHIFFON = "#fffacd"
    LIGHTBLUE = "#add8e6"
    LIGHTCORAL = "#f08080"
    LIGHTCYAN = "#e0ffff"
    LIGHTGOLDENRODYELLOW = "#fafad2"
    LIGHTGRAY = "#d3d3d3"
    LIGHTGREY = "#d3d3d3"
    LIGHTGREEN = "#90ee90"
    LIGHTPINK = "#ffb6c1"
    LIGHTSALMON = "#ffa07a"
    LIGHTSEAGREEN = "#20b2aa"
    LIGHTSKYBLUE = "#87cefa"
    LIGHTSLATEGRAY = "#778899"
    LIGHTSLATEGREY = "#778899"
    LIGHTSTEELBLUE = "#b0c4de"
    LIGHTYELLOW = "#ffffe0"
    LIME = "#00ff00"
    LIMEGREEN = "#32cd32"
    LINEN = "#faf0e6"
    MAGENTA = "#ff00ff"
    MAROON = "#800000"
    MEDIUMAQUAMARINE = "#66cdaa"
    MEDIUMBLUE = "#0000cd"
    MEDIUMORCHID = "#ba55d3"
    MEDIUMPURPLE = "#9370d8"
    MEDIUMSEAGREEN = "#3cb371"
    MEDIUMSLATEBLUE = "#7b68ee"
    MEDIUMSPRINGGREEN = "#00fa9a"
    MEDIUMTURQUOISE = "#48d1cc"
    MEDIUMVIOLETRED = "#c71585"
    MIDNIGHTBLUE = "#191970"
    MINTCREAM = "#f5fffa"
    MISTYROSE = "#ffe4e1"
    MOCCASIN = "#ffe4b5"
    NAVAJOWHITE = "#ffdead"
    NAVY = "#000080"
    OLDLACE = "#fdf5e6"
    OLIVE = "#808000"
    OLIVEDRAB = "#6b8e23"
    ORANGE = "#ffa500"
    ORANGERED = "#ff4500"
    ORCHID = "#da70d6"
    PALEGOLDENROD = "#eee8aa"
    PALEGREEN = "#98fb98"
    PALETURQUOISE = "#afeeee"
    PALEVIOLETRED = "#d87093"
    PAPAYAWHIP = "#ffefd5"
    PEACHPUFF = "#ffdab9"
    PERU = "#cd853f"
    PINK = "#ffc0cb"
    PLUM = "#dda0dd"
    POWDERBLUE = "#b0e0e6"
    PURPLE = "#800080"
    RED = "#ff0000"
    ROSYBROWN = "#bc8f8f"
    ROYALBLUE = "#4169e1"
    SADDLEBROWN = "#8b4513"
    SALMON = "#fa8072"
    SANDYBROWN = "#f4a460"
    SEAGREEN = "#2e8b57"
    SEASHELL = "#fff5ee"
    SIENNA = "#a0522d"
    SILVER = "#c0c0c0"
    SKYBLUE = "#87ceeb"
    SLATEBLUE = "#6a5acd"
    SLATEGRAY = "#708090"
    SLATEGREY = "#708090"
    SNOW = "#fffafa"
    SPRINGGREEN = "#00ff7f"
    STEELBLUE = "#4682b4"
    TAN = "#d2b48c"
    TEAL = "#008080"
    THISTLE = "#d8bfd8"
    TOMATO = "#ff6347"
    TURQUOISE = "#40e0d0"
    VIOLET = "#ee82ee"
    WHEAT = "#f5deb3"
    WHITE = "#ffffff"
    WHITESMOKE = "#f5f5f5"
    YELLOW = "#ffff00"
    YELLOWGREEN = "#9acd32"

    @classmethod
    def from_name(cls, name):
        try:
            return cls[name.upper()]
        except KeyError:
            raise ValueError(f"'{name}' is not defined as a named color.")


def name_to_hex(name: str) -> str:
    """
    Convert a color name to a normalized hexadecimal color value.

    The color name will be normalized to lower-case before being
    looked up, and when no color of that name exists in the given
    specification, ``ValueError`` is raised.

    Examples:

    >>> name_to_hex('white')
    '#ffffff'
    >>> name_to_hex('navy')
    '#000080'
    >>> name_to_hex('goldenrod')
    '#daa520'
    """
    return Color.from_name(name).value


class ColorFormat(Enum):
    RGB = auto()
    HEX = auto()

    @classmethod
    def from_name(cls, name):
        try:
            return cls[name.upper()]
        except KeyError:
            raise ValueError(f"'{name}' is not a supported color format.")


def normalize_hex(hex_value: str) -> str:
    """
    Normalize a hexadecimal color value to the following form and
    return the result::

        #[a-f0-9]{6}

    In other words, the following transformations are applied as
    needed:

    * If the value contains only three hexadecimal digits, it is expanded to six.

    * The value is normalized to lower-case.

    If the supplied value cannot be interpreted as a hexadecimal color
    value, ``ValueError`` is raised.

    Examples:

    >>> normalize_hex('#0099cc')
    '#0099cc'
    >>> normalize_hex('#0099CC')
    '#0099cc'
    >>> normalize_hex('#09c')
    '#0099cc'
    >>> normalize_hex('#09C')
    '#0099cc'
    >>> normalize_hex('0099cc')
    Traceback (most recent call last):
        ...
    ValueError: '0099cc' is not a valid hexadecimal color value.

    """
    invalid_hex_value_msg = "'%s' is not a valid hexadecimal color value."
    if not (hex_match := HEX_COLOR_RE.match(hex_value)):
        raise ValueError(invalid_hex_value_msg % hex_value)
    try:
        hex_digits = hex_match.groups()[0]
    except AttributeError:
        raise ValueError("'%s' is not a valid hexadecimal color value." % hex_value)
    if len(hex_digits) == 3:
        hex_digits = "".join([2 * s for s in hex_digits])
    return "#%s" % hex_digits.lower()


def hex_to_rgb(hex_value: str) -> tuple[int, int, int]:
    """
    Convert a hexadecimal color value to a 3-tuple of integers
    suitable for use in an ``rgb()`` triplet specifying that color.

    The hexadecimal value will be normalized before being converted.

    Examples:

    >>> hex_to_rgb('#fff')
    (255, 255, 255)
    >>> hex_to_rgb('#000080')
    (0, 0, 128)

    """
    hex_digits = normalize_hex(hex_value)
    return int(hex_digits[1:3], 16), int(hex_digits[3:5], 16), int(hex_digits[5:7], 16)


def name_to_rgb(name: str) -> tuple[int, int, int]:
    """
    Convert a color name to a 3-tuple of integers suitable for use in
    an ``rgb()`` triplet specifying that color.

    The color name will be normalized to lower-case before being
    looked up, and when no color of that name exists in the given
    specification, ``ValueError`` is raised.

    Examples:

    >>> name_to_rgb('white')
    (255, 255, 255)
    >>> name_to_rgb('navy')
    (0, 0, 128)
    >>> name_to_rgb('goldenrod')
    (218, 165, 32)

    """
    return hex_to_rgb(name_to_hex(name))


def remap(
    value: int, left_min: int, left_max: int, right_min: int, right_max: int
) -> int:
    """
    Remap a value from one range to another.
    """
    # TODO: decide if we should raise an exception if the value is outside the left range
    # Figure out how 'wide' each range is
    left_span = left_max - left_min
    right_span = right_max - right_min

    # Convert the left range into a 0-1 range (float)
    value_scaled = float(value - left_min) / float(left_span)

    # TODO: decide if we should use round() here, as int() will always round down
    # Convert the 0-1 range into a value in the right range.
    return int(right_min + (value_scaled * right_span))


def remap_color(value: int, max_value: int) -> int:
    return remap(value, 0, 255, 0, max_value)


def remap_color_reverse(value: int, max_value: int) -> int:
    return remap(value, 0, max_value, 0, 255)


def remap_rgb_value(
    rgb_val: tuple[int, int, int], max_value: int
) -> tuple[int, int, int]:
    return (
        remap_color(rgb_val[0], max_value),
        remap_color(rgb_val[1], max_value),
        remap_color(rgb_val[2], max_value),
    )


def remap_rgb_value_reverse(
    rgb_val: tuple[int, int, int], max_value: int
) -> tuple[int, int, int]:
    return (
        remap_color_reverse(rgb_val[0], max_value),
        remap_color_reverse(rgb_val[1], max_value),
        remap_color_reverse(rgb_val[2], max_value),
    )
