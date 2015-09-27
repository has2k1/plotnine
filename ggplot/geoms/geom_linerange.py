from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .geom import geom
from .geom_segment import geom_segment


class geom_linerange(geom):
    """
    Plot intervals represented by vertical lines

    Parameters
    ---------

    x
        x values of data
    ymin
        lower end of the interval for each x
    ymax
        upper end of the interval for each x
    alpha : float
        alpha value, defaults to 1
    color : string
        line color, defaults to 'black'
    linetype : string
        line type, defaults to 'solid'
    size : string
        width of the line, defaults to 2

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

        data = pd.DataFrame({'x': x, 'ymin': ymin, 'ymax': ymax})

        ggplot(aes(x='x', ymin='ymin', ymax='ymax'), data) \
            + geom_linerange()

    """
    DEFAULT_AES = {'alpha': 1, 'color': 'black',
                   'linetype': 'solid', 'size': 1.5}
    REQUIRED_AES = {'x', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}
    guide_geom = 'path'

    @staticmethod
    def draw(pinfo, panel_scales, coord, ax, **params):
        pinfo['xend'] = pinfo['x']
        pinfo['y'], pinfo['yend'] = pinfo['ymin'], pinfo['ymax']
        geom_segment.draw(pinfo, panel_scales, coord, ax, **params)
