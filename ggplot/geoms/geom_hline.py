from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd

from ..utils import make_iterable, suppress
from ..components import aes
from .geom import geom
from .geom_segment import geom_segment


class geom_hline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 1.5, 'alpha': 1, 'y': None,
                   'xmin': None, 'xmax': None}
    REQUIRED_AES = {'yintercept'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'show_guide': False, 'inherit_aes': False}
    guide_geom = 'path'

    def __init__(self, *args, **kwargs):
        with suppress(KeyError):
            yintercept = make_iterable(kwargs.pop('yintercept'))
            data = pd.DataFrame({'yintercept': yintercept})
            kwargs['mapping'] = aes(yintercept='yintercept')
            kwargs['data'] = data

        geom.__init__(self, *args, **kwargs)

    def draw_groups(self, data, scales, coordinates, ax, **params):
        """
        Plot all groups
        """
        data['y'] = data['yintercept']
        data['yend'] = data['yintercept']
        data['x'] = scales['x_range'][0]
        data['xend'] = scales['x_range'][1]
        data.drop_duplicates(inplace=True)

        for _, gdata in data.groupby('group'):
            pinfos = self._make_pinfos(gdata, params)
            for pinfo in pinfos:
                geom_segment.draw(pinfo, scales, coordinates, ax, **params)
