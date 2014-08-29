from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import make_color_tuples
from .geom import geom


class geom_vline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 1.0, 'alpha': 1, 'x': None,
                   'ymin': None, 'ymax': None}
    REQUIRED_AES = {'xintercept'}
    DEFAULT_PARAMS = {'stat': 'vline', 'position': 'identity',
                      'show_guide': False}

    layer_params = {'inherit_aes': False}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}

    def draw_groups(self, data, scales, ax, **kwargs):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, kwargs)
        for pinfo in pinfos:
            self.draw(pinfo, scales, ax, **kwargs)

    def draw(self, pinfo, scales, ax, **kwargs):
        try:
            del pinfo['x']
        except KeyError:
            pass
        x = pinfo.pop('xintercept')
        ymin = pinfo.pop('ymin')
        ymax = pinfo.pop('ymax')

        range_y = scales['y'].coord_range()
        if ymin is None:
            ymin = range_y[0]

        if ymax is None:
            ymax = range_y[1]

        alpha = pinfo.pop('alpha')
        pinfo['color'] = make_color_tuples(pinfo['color'], alpha)
        ax.vlines(x, ymin, ymax, **pinfo)
