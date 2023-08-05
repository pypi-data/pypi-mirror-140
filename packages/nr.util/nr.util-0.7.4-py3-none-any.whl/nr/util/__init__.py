
""" General purpose utility library. """

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = "0.7.4"


# Backwards compatibility
from .functional._coalesce import coalesce
from .chaindict import ChainDict
from .optional import Optional
from .orderedset import OrderedSet
from .refreshable import Refreshable
from .stream import Stream
