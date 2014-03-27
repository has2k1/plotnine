from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
from .geom import geom

class geom_text(geom):
    DEFAULT_AES = {'alpha': None, 'angle': 0, 'color': 'black', 'family': None,
                   'fontface': 1, 'hjust': None, 'size': 12, 'vjust': None,
                   'lineheight': 1.2}
    REQUIRED_AES = {'label','x','y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity', 'parse': False}

    _aes_renames = {'angle': 'rotation', 'lineheight': 'linespacing'}
    _groups = {'alpha', 'color', 'family', 'size'}

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        y = pinfo.pop('y')
        label = pinfo.pop('label')
        # TODO: Deal with the fontface
        # from ggplot2
        # 1 = plain, 2 = bold, 3 = italic, 4 = bold italic
        # "plain", "bold", "italic", "oblique", and "bold.italic"
        pinfo.pop('fontface')

        # before taking max and min make sure x is not empty
        if len(x) == 0:
            return

        # plt.text does not resize axes, must do manually
        xmax = max(x)
        xmin = min(x)
        ymax = max(y)
        ymin = min(y)

        margin = 0.1
        xmargin = (xmax - xmin) * margin
        ymargin = (ymax - ymin) * margin
        xmax = xmax + xmargin
        xmin = xmin - xmargin
        ymax = ymax + ymargin
        ymin = ymin - ymargin

        # Take current plotting dimension in account for the case that we
        # work on a special dataframe just for this geom!
        if not self.data is None:  # NOTE: not working??
            cxmin, cxmax = ax.get_xlim()
            cymin, cymax = ax.get_ylim()
            # there is a problem if geom_text is the first plot, as
            # then the dimension are 0-1 for all axis :-(
            xmax = max(xmax, cxmax)
            xmin = min(xmin, cxmin)
            ymax = max(ymax, cymax)
            ymin = min(ymin, cymin)

        # TODO: Fix the defaults for this
        # try out 0.5
        if pinfo['hjust'] is not None:
            x = (np.array(x) + pinfo['hjust']).tolist()
        else:
            pinfo['horizontalalignment'] = 'center'

        if pinfo['vjust'] is not None:
            y = (np.array(y) + pinfo['vjust']).tolist()
        else:
            pinfo['verticalalignment'] = 'center'

        del pinfo['hjust']
        del pinfo['vjust']
        for x_g,y_g,s in zip(x,y,label):
            ax.text(x_g,y_g,s,**pinfo)

        # TODO: Find out why this isn't working as desired
        # resize axes
        ax.axis([xmin, xmax, ymin, ymax])
