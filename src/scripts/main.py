#!/usr/bin/env python3

from optparse import OptionParser, IndentedHelpFormatter, OptionGroup
import textwrap
import sys
import logging

from blinkstick import (
    find_all,
    find_by_serial,
    get_blinkstick_package_version,
    BlinkStickVariant,
)

logging.basicConfig()


class IndentedHelpFormatterWithNL(IndentedHelpFormatter):
    def format_description(self, description):
        if not description:
            return ""

        desc_width = self.width - self.current_indent
        indent = " " * self.current_indent
        # the above is still the same
        bits = description.split("\n")
        formatted_bits = [
            textwrap.fill(
                bit, desc_width, initial_indent=indent, subsequent_indent=indent
            )
            for bit in bits
        ]
        result = "\n".join(formatted_bits) + "\n"
        return result

    def format_option(self, option):
        # The help for each option consists of two parts:
        #   * the opt strings and metavars
        #   eg. ("-x", or "-fFILENAME, --file=FILENAME")
        #   * the user-supplied help string
        #   eg. ("turn on expert mode", "read data from FILENAME")
        #
        # If possible, we write both of these on the same line:
        #   -x    turn on expert mode
        #
        # But if the opt string list is too long, we put the help
        # string on a second line, indented to the same column it would
        # start in if it fit on the first line.
        #   -fFILENAME, --file=FILENAME
        #       read data from FILENAME
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2

        if len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        else:  # start help on same line as opts
            opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
            indent_first = 0

        result.append(opts)

        if option.help:
            help_text = self.expand_default(option)
            # Everything is the same up through here
            help_lines = []
            for para in help_text.split("\n"):
                help_lines.extend(textwrap.wrap(para, self.help_width))
                # Everything is the same after here
            result.append("%*s%s\n" % (indent_first, "", help_lines[0]))
            result.extend(
                ["%*s%s\n" % (self.help_position, "", line) for line in help_lines[1:]]
            )
        elif opts[-1] != "\n":
            result.append("\n")
        return "".join(result)

    def format_usage(self, usage):
        return (
            "BlinkStick control script %s\n(c) Agile Innovative Ltd 2013-2014\n\n%s"
            % (
                get_blinkstick_package_version(),
                IndentedHelpFormatter.format_usage(self, usage),
            )
        )


def print_info(stick):
    print("Found backend:")
    print("    Manufacturer:  {0}".format(stick.get_manufacturer()))
    print("    Description:   {0}".format(stick.get_description()))
    print("    Variant:       {0}".format(stick.get_variant_string()))
    print("    Serial:        {0}".format(stick.get_serial()))
    print("    Current Color: {0}".format(stick.get_color(color_format="hex")))
    print("    Mode:          {0}".format(stick.get_mode()))
    if stick.get_variant() == BlinkStickVariant.BLINKSTICK_FLEX:
        try:
            count = stick.get_led_count()
        except:
            count = -1

        if count == -1:
            count = "Error"
        print("    LED conf:      {0}".format(count))
    print("    Info Block 1:  {0}".format(stick.get_info_block1()))
    print("    Info Block 2:  {0}".format(stick.get_info_block2()))


def main():
    global options
    global sticks

    parser = OptionParser(
        usage="usage: %prog [options] [color]", formatter=IndentedHelpFormatterWithNL()
    )

    parser.add_option(
        "-i", "--info", action="store_true", dest="info", help="Display BlinkStick info"
    )

    parser.add_option(
        "-s",
        "--serial",
        dest="serial",
        help="Select backend by serial number. If unspecified, action will be performed on all BlinkSticks.",
    )

    parser.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="Display debug output",
    )

    group = OptionGroup(
        parser, "Change color", "These options control the color of the backend  "
    )

    group.add_option(
        "--channel",
        default=0,
        dest="channel",
        help="Select channel. Applies only to BlinkStick Pro.",
    )

    group.add_option(
        "--index",
        default=0,
        dest="index",
        help="Select index. Applies only to BlinkStick Pro.",
    )

    group.add_option(
        "--brightness",
        default=100,
        dest="limit",
        help="Limit the brightness of the color 0..100",
    )

    group.add_option(
        "--limit", default=100, dest="limit", help="Alias to --brightness option"
    )

    group.add_option(
        "--set-color",
        dest="color",
        help="Set the color for the backend. This can also be the last argument for the script. "
        "The value can either be a named color, hex value, 'random' or 'off'.\n\n"
        "CSS color names are defined http://www.w3.org/TR/css3-color/ e.g. red, green, blue. "
        "Specify color using hexadecimal color value e.g. 'FF3366'",
    )
    group.add_option(
        "--inverse",
        action="store_true",
        dest="inverse",
        help="Control BlinkSticks in inverse mode",
    )

    group.add_option(
        "--set-led-count",
        dest="led_count",
        help="Set the number of LEDs to control for supported devices.",
    )

    parser.add_option_group(group)

    group = OptionGroup(
        parser,
        "Control animations",
        "These options will blink, morph or pulse selected color.  ",
    )

    group.add_option(
        "--blink",
        dest="blink",
        action="store_true",
        help="Blink LED (requires --set-color or color set as last argument, and optionally --delay)",
    )

    group.add_option(
        "--pulse",
        dest="pulse",
        action="store_true",
        help="Pulse LED (requires --set-color or color set as last argument, and optionally --duration).",
    )

    group.add_option(
        "--morph",
        dest="morph",
        action="store_true",
        help="Morph to specified color (requires --set-color or color set as last argument, and optionally --duration).",
    )

    group.add_option(
        "--duration",
        dest="duration",
        default=1000,
        help="Set duration of transition in milliseconds (use with --morph and --pulse).",
    )

    group.add_option(
        "--delay",
        dest="delay",
        default=500,
        help="Set time in milliseconds to light LED for (use with --blink).",
    )

    group.add_option(
        "--repeats",
        dest="repeats",
        default=1,
        help="Number of repetitions (use with --blink and --pulse).",
    )

    parser.add_option_group(group)

    group = OptionGroup(
        parser,
        "Device data and behaviour",
        "These options will change backend mode and data stored internally.  ",
    )

    group.add_option(
        "--set-mode",
        default=0,
        dest="mode",
        help="Set mode for BlinkStick Pro:\n\n    0 - default\n\n    1 - inverse\n\n    2 - ws2812\n\n    3 - ws2812 mirror",
    )

    group.add_option(
        "--set-infoblock1",
        dest="infoblock1",
        help="Set the first info block for the backend.",
    )

    group.add_option(
        "--set-infoblock2",
        dest="infoblock2",
        help="Set the second info block for the backend.",
    )

    parser.add_option_group(group)

    group = OptionGroup(parser, "Advanced options", "")

    group.add_option(
        "--add-udev-rule",
        action="store_true",
        dest="udev",
        help="Add udev rule to access BlinkSticks without root permissions. Must be run as root e.g. `sudo $(which blinkstick) --add-udev-rule`.",
    )

    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    # Global action
    if options.udev:

        try:
            filename = "/etc/udev/rules.d/85-blinkstick.rules"
            file = open(filename, "w")
            file.write(
                'SUBSYSTEM=="usb", ATTR{idVendor}=="20a0", ATTR{idProduct}=="41e5", MODE:="0666"'
            )
            file.close()

            print("Rule added to {0}".format(filename))
        except IOError as e:
            print(str(e))
            print(
                "Make sure you run this script as root: sudo blinkstick --add-udev-rule"
            )
            return 64

        print("Reboot your computer for changes to take effect")
        return 0

    if options.serial is None:
        sticks = find_all()
    else:
        sticks = [find_by_serial(options.serial)]

        if len(sticks) == 0:
            print("BlinkStick with serial number " + options.serial + " not found...")
            return 64

    for stick in sticks:
        if options.inverse:
            stick.set_inverse(True)

        stick.set_max_rgb_value(int(float(options.limit) / 100.0 * 255))

        stick.set_error_reporting(False)

    # Actions here work on all BlinkSticks
    for stick in sticks:
        if options.infoblock1:
            stick.set_info_block1(options.infoblock1)

        if options.infoblock2:
            stick.set_info_block2(options.infoblock2)

        if options.mode:
            if (
                options.mode == "0"
                or options.mode == "1"
                or options.mode == "2"
                or options.mode == "3"
            ):
                stick.set_mode(int(options.mode))
            else:
                print("Error: Invalid mode parameter value")

        elif options.led_count:
            led_count = int(options.led_count)

            if led_count > 0 and led_count <= 32:
                stick.set_led_count(led_count)
            else:
                print("Error: Invalid led-count parameter value")

        elif options.info:
            print_info(stick)
        elif options.color or len(args) > 0:
            if options.color:
                color = options.color
            else:
                color = args[0]

            # determine color
            fargs = {}
            if color.startswith("#"):
                fargs["hex"] = color
            elif color == "random":
                fargs["name"] = "random"
            elif color == "off":
                fargs["hex"] = "#000000"
            else:
                if len(color) == 6:
                    # If color contains 6 chars check if it's hex
                    try:
                        int(color, 16)
                        fargs["hex"] = "#" + color
                    except:
                        fargs["name"] = color
                else:
                    fargs["name"] = color

            fargs["index"] = int(options.index)
            fargs["channel"] = int(options.channel)

            # handle blink/pulse/morph
            func = stick.set_color
            if options.blink:
                func = stick.blink
                fargs["delay"] = options.delay
                fargs["repeats"] = int(options.repeats)
            elif options.pulse:
                func = stick.pulse
                fargs["duration"] = options.duration
                fargs["repeats"] = int(options.repeats)
            elif options.morph:
                func = stick.morph
                fargs["duration"] = options.duration

            func(**fargs)

        else:
            parser.print_help()
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
