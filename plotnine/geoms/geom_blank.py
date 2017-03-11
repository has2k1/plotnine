from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..doctools import document
from .geom import geom


@document
class geom_blank(geom):
    """
    An empty plot

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}
    """
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False}

    def draw_panel(self, data, panel_params, coord, ax, **params):
        pass

    def handle_na(self, data):
        return data
