from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd

from ..utils import make_iterable, suppress
from ..doctools import document
from ..aes import aes
from .geom import geom
from .geom_segment import geom_segment


@document
class geom_abline(geom):
    """
    Lines specified by slope and intercept

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}
    """
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'alpha': 1, 'size': 0.5}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'inherit_aes': False}
    REQUIRED_AES = {'slope', 'intercept'}
    legend_geom = 'path'

    def __init__(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, aes):
                break
        else:
            # Nothing is set, default to y=x
            if 'slope' not in kwargs:
                kwargs['slope'] = 1
            if 'intercept' not in kwargs:
                kwargs['intercept'] = 0

        with suppress(KeyError):
            intercept = make_iterable(kwargs.pop('intercept'))
            data = pd.DataFrame({'intercept': intercept,
                                 'slope': kwargs.pop('slope')})
            kwargs['mapping'] = aes(intercept='intercept', slope='slope')
            kwargs['data'] = data
            kwargs['show_legend'] = False

        geom.__init__(self, *args, **kwargs)

    def draw_panel(self, data, panel_params, coord, ax, **params):
        """
        Plot all groups
        """
        ranges = coord.range(panel_params)
        data['x'] = ranges.x[0]
        data['xend'] = ranges.x[1]
        data['y'] = ranges.x[0] * data['slope'] + data['intercept']
        data['yend'] = ranges.x[1] * data['slope'] + data['intercept']
        data = data.drop_duplicates()

        for _, gdata in data.groupby('group'):
            gdata.reset_index(inplace=True)
            gdata.is_copy = None
            geom_segment.draw_group(gdata, panel_params,
                                    coord, ax, **params)
