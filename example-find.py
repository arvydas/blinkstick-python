#!/usr/bin/python

from blinkstick import *

print "Find BlinkStick by serial number"
print "(c) Agile Innovative Ltd"
print ""

bstick = BlinkStick.find_by_serial("BS000000-1.0")

if bstick is None:
    print "Not found..."
else: 
    print "BlinkStick found. Current color: " + bstick.get_color_string()
