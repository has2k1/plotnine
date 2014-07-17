from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys

from .geom import geom
from ggplot.utils import is_categorical
import numpy as np


class geom_linerange(geom):
    """Plot intervals represented by vertical lines

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
                   'linetype': 'solid',
                   'size': 2}
    REQUIRED_AES = {'x', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity', 'cmap': None}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}
    _units = {'alpha', 'color', 'linestyle'}

    def __init__(self, *args, **kwargs):
        super(geom_linerange, self).__init__(*args, **kwargs)
        self._warning_printed = False

    def _plot_unit(self, pinfo, ax):
        # If x is categorical, calculate positions to plot
        categorical = is_categorical(pinfo['x'])
        if categorical:
            x = pinfo.pop('x')
            new_x = np.arange(len(x))
            ax.set_xticks(new_x)
            ax.set_xticklabels(x)
            pinfo['x'] = new_x

        if 'linewidth' in pinfo and isinstance(pinfo['linewidth'], list):
            # ggplot also supports aes(size=...) but the current mathplotlib
            # is not. See https://github.com/matplotlib/matplotlib/issues/2658
            pinfo['linewidth'] = 4
            if not self._warning_printed:
                msg = "'geom_line()' currenty does not support the mapping of " +\
                      "size ('aes(size=<var>'), using size=4 as a replacement.\n" +\
                      "Use 'geom_line(size=x)' to set the size for the whole line.\n"
                sys.stderr.write(msg)
                self._warning_printed = True

        x = pinfo.pop('x')
        x = np.vstack([x, x])

        ymin = pinfo.pop('ymin')
        ymax = pinfo.pop('ymax')
        y = np.vstack([ymin, ymax])

        ax.plot(x, y, **pinfo)
