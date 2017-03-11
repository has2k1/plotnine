from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..doctools import document
from .geom import geom
from .geom_segment import geom_segment


@document
class geom_linerange(geom):
    """
    Vertical interval represented by lines

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}
    """
    DEFAULT_AES = {'alpha': 1, 'color': 'black',
                   'linetype': 'solid', 'size': 0.5}
    REQUIRED_AES = {'x', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False}
    legend_geom = 'path'

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        data.eval("""
                     xend = x
                     y = ymin
                     yend = ymax""",
                  inplace=True)
        geom_segment.draw_group(data, panel_params, coord, ax, **params)
