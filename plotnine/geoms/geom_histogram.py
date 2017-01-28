from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils.doctools import document
from .geom_bar import geom_bar


@document
class geom_histogram(geom_bar):
    """
    Histogram

    {documentation}
    """
    DEFAULT_PARAMS = {'stat': 'bin', 'position': 'stack'}
