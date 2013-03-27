#!/usr/bin/python

from blinkstick import blinkstick

print "Display BlinkStick Name (InfoBlock1)"
print "(c) Agile Innovative Ltd"
print ""

bstick = blinkstick.find_first()
bstick.set_info_block1("Kitchen BlinkStick")
print bstick.get_info_block1()

#    set and get device info-block2 here
#bstick.set_info_block2("info-block-2data")
#print bstick.get_info_block2()
