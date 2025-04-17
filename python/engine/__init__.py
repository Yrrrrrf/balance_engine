from .engine import *


__doc__ = engine.__doc__
if hasattr(engine, "__all__"):
    __all__ = engine.__all__


def some_init():
    """Initialize the engine module."""
    engine.init()
    print("Engine is being initialized...")
