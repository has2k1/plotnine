from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom



class geom_area(geom):
    VALID_AES = {'x', 'ymax', 'ymin', 'alpha', 'color',
                 'fill', 'linetype', 'size'}
    REQUIRED_AES = {'x', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'stack'}

    _groups = {'color', 'alpha'}
    _aes_renames = {'linetype': 'linestyle'}

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        y1 = pinfo.pop('ymin')
        y2 = pinfo.pop('ymax')
        ax.fill_between(x, y1, y2, **pinfo)

