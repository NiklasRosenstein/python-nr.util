
""" General purpose utility library. """

__version__ = "0.0.0"

from ._coalesce import coalesce
from ._optional import Optional
from ._refreshable import Refreshable
from ._stream import Stream

__all__ = ['coalesce', 'Optional', 'Stream']
