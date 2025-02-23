from __future__ import annotations

from functools import wraps


def no_backend_required(func):
    """no-op decorator to mark a function as requiring a backend. See BlinkStick.__getattribute__ for usage."""

    func.no_backend_required = True

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)

    return wrapper
