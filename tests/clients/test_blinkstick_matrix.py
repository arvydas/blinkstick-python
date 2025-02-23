from blinkstick.clients import BlinkStickProMatrix


def test_instantiate():
    bs = BlinkStickProMatrix()
    assert bs is not None
