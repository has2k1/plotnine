from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import make_color_tuples
from .geom import geom


class geom_hline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 1.0, 'alpha': 1, 'y': None,
                   'xmin': None, 'xmax': None}
    REQUIRED_AES = {'yintercept'}
    DEFAULT_PARAMS = {'stat': 'hline', 'position': 'identity',
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

    @staticmethod
    def draw(pinfo, scales, ax, **kwargs):
        try:
            del pinfo['y']
        except KeyError:
            pass
        y = pinfo.pop('yintercept')
        xmin = pinfo.pop('xmin')
        xmax = pinfo.pop('xmax')

        range_x = scales['x'].coord_range()
        if xmin is None:
            xmin = range_x[0]

        if xmax is None:
            xmax = range_x[1]

        alpha = pinfo.pop('alpha')
        pinfo['color'] = make_color_tuples(pinfo['color'], alpha)
        ax.hlines(y, xmin, xmax, **pinfo)
