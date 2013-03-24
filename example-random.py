#!/usr/bin/python

from blinkstick import *

print "Set random BlinkStick color"
print "(c) Agile Innovative Ltd"
print ""

for bstick in BlinkStick.find_all():
    bstick.set_random_color()
    print bstick.get_serial() + " " + bstick.get_color_string()
