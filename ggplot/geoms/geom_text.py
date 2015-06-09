from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
from matplotlib.text import Text

from .geom import geom


class geom_text(geom):
    DEFAULT_AES = {'alpha': None, 'angle': 0, 'color': 'black', 'family': None,
                   'fontface': 1, 'hjust': None, 'size': 12, 'vjust': None,
                   'lineheight': 1.2}
    REQUIRED_AES = {'label', 'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'parse': False}

    _units = {'alpha', 'color', 'family', 'size'}

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **params):
        x = pinfo.pop('x')
        y = pinfo.pop('y')
        # TODO: Deal with the fontface
        # from ggplot2
        # 1 = plain, 2 = bold, 3 = italic, 4 = bold italic
        # "plain", "bold", "italic", "oblique", and "bold.italic"
        pinfo.pop('fontface')
        pinfo['horizontalalignment'] = 'center'
        pinfo['verticalalignment'] = 'center'

        if pinfo['hjust'] is not None:
            x = (np.array(x) + pinfo['hjust']).tolist()

        if pinfo['vjust'] is not None:
            y = (np.array(y) + pinfo['vjust']).tolist()

        for x_g, y_g, s in zip(x, y, pinfo['label']):
            ax.text(x_g, y_g, s,
                    alpha=pinfo['alpha'],
                    color=pinfo['color'],
                    size=pinfo['size'],
                    linespacing=pinfo['lineheight'],
                    family=pinfo['family'],
                    verticalalignment=pinfo['verticalalignment'],
                    horizontalalignment=pinfo['horizontalalignment'],
                    rotation=pinfo['angle'],
                    zorder=pinfo['zorder'])

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw letter 'a' in the box

        Parameters
        ----------
        data : dataframe
        da : DrawingArea
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        key = Text(x=0.5*da.width,
                   y=0.5*da.height,
                   text='a',
                   alpha=data['alpha'],
                   size=data['size'],
                   family=data['family'],
                   color=data['color'],
                   rotation=data['angle'],
                   horizontalalignment='center',
                   verticalalignment='center')
        da.add_artist(key)
        return da
