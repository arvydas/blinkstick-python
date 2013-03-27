#!/usr/bin/python

from BlinkStick import blinkstick

print "Display BlinkStick info"
print "(c) Agile Innovative Ltd"
print ""

for bstick in blinkstick.find_all():
    print "Found device:"
    print "    Manufacturer:  " + bstick.get_manufacturer()
    print "    Description:   " + bstick.get_description()
    print "    Serial:        " + bstick.get_serial()
    print "    Current Color: " + bstick.get_color_string()
    print "    Info Block 1:  " + bstick.get_info_block1()
    print "    Info Block 2:  " + bstick.get_info_block2()
