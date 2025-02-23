from typing import Callable
from unittest.mock import MagicMock

import pytest

from blinkstick.clients.blinkstick import BlinkStick


@pytest.fixture
def make_blinkstick() -> Callable[[], BlinkStick]:
    def _make_blinkstick() -> BlinkStick:
        bs = BlinkStick()
        bs.backend = MagicMock()
        return bs

    return _make_blinkstick
