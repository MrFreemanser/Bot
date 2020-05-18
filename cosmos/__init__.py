from .core import Cosmos
from .core.functions import exceptions


__release__ = "MY DICK"
__version__ = "IS VERY BIG"


def get_bot():
    return Cosmos(version=__version__, release=__release__)
