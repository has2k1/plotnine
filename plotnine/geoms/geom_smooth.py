from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.patches import Rectangle

from ..doctools import document
from .geom import geom
from .geom_ribbon import geom_ribbon
from .geom_line import geom_line
from .geom_line import geom_path


@document
class geom_smooth(geom):
    """
    A smoothed conditional mean

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}
    """
    DEFAULT_AES = {'alpha': 0.4, 'color': 'black', 'fill': '#999999',
                   'linetype': 'solid', 'size': 1,
                   'ymin': None, 'ymax': None}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'smooth', 'position': 'identity',
                      'na_rm': False}

    def setup_data(self, data):
        return data.sort_values(['PANEL', 'group', 'x'])

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        has_ribbon = (data.ix[0, 'ymin'] is not None and
                      data.ix[0, 'ymax'] is not None)
        if has_ribbon:
            data2 = data.copy()
            data2['color'] = None
            geom_ribbon.draw_group(data2, panel_params,
                                   coord, ax, **params)

        data['alpha'] = 1
        geom_line.draw_group(data, panel_params, coord, ax, **params)

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw letter 'a' in the box

        Parameters
        ----------
        data : dataframe
        params : dict
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        if lyr.stat.params['se']:
            bg = Rectangle((0, 0),
                           width=da.width,
                           height=da.height,
                           alpha=data['alpha'],
                           facecolor=data['fill'],
                           linewidth=0)
            da.add_artist(bg)

        data['alpha'] = 1
        return geom_path.draw_legend(data, da, lyr)
