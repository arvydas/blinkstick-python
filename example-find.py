#!/usr/bin/python

from BlinkStick import blinkstick

print "Find BlinkStick by serial number"
print "(c) Agile Innovative Ltd"
print ""

bstick = blinkstick.find_by_serial("BS000001-1.0")

if bstick is None:
    print "Not found..."
else: 
    print "BlinkStick found. Current color: " + bstick.get_color_string()
