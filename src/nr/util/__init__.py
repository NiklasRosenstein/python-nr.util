
""" General purpose utility library. """

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = "0.3.1"

from ._coalesce import coalesce
from ._optional import Optional
from ._refreshable import Refreshable
from ._stream import Stream

__all__ = ['coalesce', 'Optional', 'Refreshable', 'Stream']
