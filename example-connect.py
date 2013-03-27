import websocket
import thread
import time
import json
import sys
from BlinkStick import blinkstick

print "Connect to BlinkStick.com and control BlinkStick remotely"
print "(c) Agile Innovative Ltd"
print ""

if (len(sys.argv) > 1):
    access_code = sys.argv[1]
else:
    print "Usage:"
    print "   [sudo] python example-connect.py \"AccessCode\""
    print ""
    print "You can obtain the AccessCode parameter from the device information page on BlinkStick.com"
    sys.exit()

bstick = b.find_first()
blinkstick
if (bstick is None):
    sys.exit("BlinkStick not found...")


def HTMLColorToRGB(colorstring):
    """ convert #RRGGBB to an (R, G, B) tuple """
    colorstring = colorstring.strip()
    if colorstring[0] == '#': colorstring = colorstring[1:]
    if len(colorstring) != 6:
        raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)


def on_message(ws, message):
    global client_id
    global access_code
    global bstick

    #Uncomment this for debugging purposes
    #print message

    m = json.loads(message)

    if m[0]['channel'] == '/meta/connect':
        ws.send(json.dumps(
            {'channel': '/meta/connect',
             'clientId': client_id,
             'connectionType': 'websocket'}))
        return

    elif m[0]['channel'] == '/meta/handshake':
        client_id = m[0]['clientId']

        print "Acquired clientId: " + client_id

        ws.send(json.dumps(
            {'channel': '/meta/subscribe',
             'clientId': client_id,
             'subscription': '/devices/' + access_code}))
        return

    elif m[0]['channel'] == '/devices/' + access_code:
        if 'color' in m[0]["data"]:
            print "Received color: " + m[0]["data"]["color"]

            (r, g, b) = HTMLColorToRGB(m[0]["data"]["color"])
            bstick.set_color(r, g, b)
        elif 'status' in m[0]["data"] and m[0]["data"]['status'] == "off":
            print "Turn off"
            bstick.turn_off()

    elif m[0]['channel'] == '/meta/subscribe':
        if m[0]['successful']:
            print "Subscribed to device. Waiting for color message..."
        else:
            print "Subscription to the device failed. Please check the access_code value in the file."

    #Reconnect again and wait for futher messages
    ws.send(json.dumps(
        {'channel': '/meta/connect',
         'clientId': client_id,
         'connectionType': 'websocket'}))


def on_error(ws, error):
    print error


def on_close(ws):
    print "### closed ###"


def on_open(ws):
    ws.send(json.dumps(
        {'channel': '/meta/handshake',
         'version': '1.0',
         'supportedConnectionTypes': ['long-polling', 'websocket']}))


if __name__ == "__main__":
    # Set this to True for debugging purposes
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("ws://live.blinkstick.com:9292/faye",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open

    ws.run_forever()
