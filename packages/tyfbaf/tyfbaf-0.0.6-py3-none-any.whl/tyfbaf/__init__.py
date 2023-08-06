"""
tyfbaf
"""
from .http import _setup

__version__ = "0.0.6"


def setup(server_name: str, *, port: int = 6405):
    _setup(server_name, port)
