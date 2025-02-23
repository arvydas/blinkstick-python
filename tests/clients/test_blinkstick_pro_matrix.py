from blinkstick.clients import BlinkStickPro


def test_instantiate():
    bs = BlinkStickPro()
    assert bs is not None
