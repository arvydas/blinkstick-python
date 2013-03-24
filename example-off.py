#!/usr/bin/python

from blinkstick import *

print "Turn BlinkSticks off"
print "(c) Agile Innovative Ltd"
print ""

for bstick in BlinkStick.find_all():
  bstick.turn_off()
  print bstick.get_serial() + " turned off"
