from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd

from ..utils import make_iterable, suppress
from ..components import aes
from .geom import geom
from .geom_segment import geom_segment


class geom_hline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 1.5, 'alpha': 1}
    REQUIRED_AES = {'yintercept'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'show_legend': False, 'inherit_aes': False}
    legend_geom = 'path'

    def __init__(self, *args, **kwargs):
        with suppress(KeyError):
            yintercept = make_iterable(kwargs.pop('yintercept'))
            data = pd.DataFrame({'yintercept': yintercept})
            kwargs['mapping'] = aes(yintercept='yintercept')
            kwargs['data'] = data

        geom.__init__(self, *args, **kwargs)

    def draw_panel(self, data, panel_scales, coord, ax, **params):
        """
        Plot all groups
        """
        ranges = coord.range(panel_scales)
        data['y'] = data['yintercept']
        data['yend'] = data['yintercept']
        data['x'] = ranges.x[0]
        data['xend'] = ranges.x[1]
        data.drop_duplicates(inplace=True)

        for _, gdata in data.groupby('group'):
            pinfos = self._make_pinfos(gdata, params)
            for pinfo in pinfos:
                geom_segment.draw_group(pinfo, panel_scales,
                                        coord, ax, **params)
