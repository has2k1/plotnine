from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
import matplotlib.lines as mlines

from ..utils import make_iterable, suppress, SIZE_FACTOR
from ..doctools import document
from ..aes import aes
from .geom import geom
from .geom_segment import geom_segment


@document
class geom_vline(geom):
    """
    Vertical line

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}
    """
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 0.5, 'alpha': 1}
    REQUIRED_AES = {'xintercept'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'inherit_aes': False}

    def __init__(self, *args, **kwargs):
        with suppress(KeyError):
            xintercept = make_iterable(kwargs.pop('xintercept'))
            data = pd.DataFrame({'xintercept': xintercept})
            kwargs['mapping'] = aes(xintercept='xintercept')
            kwargs['data'] = data
            kwargs['show_legend'] = False

        geom.__init__(self, *args, **kwargs)

    def draw_panel(self, data, panel_params, coord, ax, **params):
        """
        Plot all groups
        """
        ranges = coord.range(panel_params)
        data['x'] = data['xintercept']
        data['xend'] = data['xintercept']
        data['y'] = ranges.y[0]
        data['yend'] = ranges.y[1]
        data = data.drop_duplicates()

        for _, gdata in data.groupby('group'):
            gdata.reset_index(inplace=True)
            gdata.is_copy = None
            geom_segment.draw_group(gdata, panel_params,
                                    coord, ax, **params)

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw a vertical line in the box

        Parameters
        ----------
        data : dataframe
        da : DrawingArea
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        x = [0.5 * da.width] * 2
        y = [0, da.height]
        data['size'] *= SIZE_FACTOR
        key = mlines.Line2D(x,
                            y,
                            alpha=data['alpha'],
                            linestyle=data['linetype'],
                            linewidth=data['size'],
                            color=data['color'],
                            solid_capstyle='butt',
                            antialiased=False)
        da.add_artist(key)
        return da
