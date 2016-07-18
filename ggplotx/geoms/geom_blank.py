from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils.doctools import document
from .geom import geom


@document
class geom_blank(geom):
    """
    An empty plot

    {documentation}
    """
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    def draw_panel(self, data, panel_scales, coord, ax, **params):
        pass
