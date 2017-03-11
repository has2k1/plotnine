from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd

from ..utils import make_iterable, suppress
from ..doctools import document
from ..aes import aes
from .geom import geom
from .geom_segment import geom_segment


@document
class geom_hline(geom):
    """
    Horizontal line

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}
    """
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 0.5, 'alpha': 1}
    REQUIRED_AES = {'yintercept'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'inherit_aes': False}
    legend_geom = 'path'

    def __init__(self, *args, **kwargs):
        with suppress(KeyError):
            yintercept = make_iterable(kwargs.pop('yintercept'))
            data = pd.DataFrame({'yintercept': yintercept})
            kwargs['mapping'] = aes(yintercept='yintercept')
            kwargs['data'] = data
            kwargs['show_legend'] = False

        geom.__init__(self, *args, **kwargs)

    def draw_panel(self, data, panel_params, coord, ax, **params):
        """
        Plot all groups
        """
        ranges = coord.range(panel_params)
        data['y'] = data['yintercept']
        data['yend'] = data['yintercept']
        data['x'] = ranges.x[0]
        data['xend'] = ranges.x[1]
        data = data.drop_duplicates()

        for _, gdata in data.groupby('group'):
            gdata.reset_index(inplace=True)
            gdata.is_copy = None
            geom_segment.draw_group(gdata, panel_params,
                                    coord, ax, **params)
