from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from .geom import geom
from .geom_path import geom_path
from .geom_point import geom_point
from .geom_linerange import geom_linerange


class geom_pointrange(geom):
    """Plot intervals represented by vertical lines with a point in each interval

     Parameters
     ---------

     x
         x values of data
     y
         y value of the point for each x
     ymin
         lower end of the interval for each x
     ymax
         upper end of the interval for each x
     alpha : float
         alpha value, defaults to 1
     color : string
         line color, defaults to 'black'
     fill : string
         Fill type for the points, defaults to 'None'
     linetype : string
         line type, defaults to 'solid'
     shape : string
         shape of the points, defaults to 'o' (i.e. circles)
     size : string
         width of the line and size of the point, defaults to 2

     Examples
     --------

     .. plot::
         :include-source:

         import numpy as np
         import pandas as pd
         from ggplot import *

         np.random.seed(42)
         x = np.linspace(0.5, 9.5, num=10)
         y = np.random.randn(10)
         ymin = y - np.random.uniform(0,1, size=10)
         ymax = y + np.random.uniform(0,1, size=10)

         data = pd.DataFrame({'x': x, 'y': y, 'ymin': ymin, 'ymax': ymax})

         ggplot(aes(x='x', y='y', ymin='ymin', ymax='ymax'), data) \
             + geom_pointrange()

    """

    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'fill': None,
                   'linetype': 'solid', 'shape': 'o', 'size': 1.5}
    REQUIRED_AES = {'x', 'y', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _units = {'shape'}

    @staticmethod
    def draw(pinfo, panel_scales, coord, ax, **params):
        y = pinfo['y']
        geom_linerange.draw(pinfo, panel_scales, coord, ax, **params)
        pinfo['size'] = np.asarray(pinfo['size']) * 4
        pinfo['y'] = y
        pinfo['stroke'] = 1
        geom_point.draw(pinfo, panel_scales, coord, ax, **params)

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw a point in the box

        Parameters
        ----------
        data : dataframe
        params : dict
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        data.is_copy = None
        geom_path.draw_legend(data, da, lyr)
        data['size'] = data['size'] * 4
        data['stroke'] = 1
        geom_point.draw_legend(data, da, lyr)
        return da
