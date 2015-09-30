from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd

from ..utils import make_iterable, suppress
from ..components import aes
from .geom import geom
from .geom_segment import geom_segment


class geom_vline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 1.5, 'alpha': 1}
    REQUIRED_AES = {'xintercept'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'show_guide': False, 'inherit_aes': False}
    guide_geom = 'path'

    def __init__(self, *args, **kwargs):
        with suppress(KeyError):
            xintercept = make_iterable(kwargs.pop('xintercept'))
            data = pd.DataFrame({'xintercept': xintercept})
            kwargs['mapping'] = aes(xintercept='xintercept')
            kwargs['data'] = data

        geom.__init__(self, *args, **kwargs)

    def draw_groups(self, data, panel_scales, coord, ax, **params):
        """
        Plot all groups
        """
        ranges = coord.range(panel_scales)
        data['x'] = data['xintercept']
        data['xend'] = data['xintercept']
        data['y'] = ranges.y[0]
        data['yend'] = ranges.y[1]
        data.drop_duplicates(inplace=True)

        for _, gdata in data.groupby('group'):
            pinfos = self._make_pinfos(gdata, params)
            for pinfo in pinfos:
                geom_segment.draw(pinfo, panel_scales, coord, ax, **params)
