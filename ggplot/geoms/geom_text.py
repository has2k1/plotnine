from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
from .geom import geom

class geom_text(geom):
    VALID_AES = {'label','x','y','alpha','angle','color','family','fontface',
                 'hjust','size','vjust'}
    REQUIRED_AES = {'label','x','y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity', 'parse': False}

    _groups = {'color', 'family', 'alpha', 'size'}
    _translations = {'angle': 'rotation'}

    def plot(self, layer, ax):
        x = layer.pop('x')
        y = layer.pop('y')
        label = layer.pop('label')

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
        if not self.data is None:
            cxmin, cxmax = ax.get_xlim()
            cymin, cymax = ax.get_ylim()
            # there is a problem if geom_text is the first plot, as
            # then the dimension are 0-1 for all axis :-(
            xmax = max(xmax, cxmax)
            xmin = min(xmin, cxmin)
            ymax = max(ymax, cymax)
            ymin = min(ymin, cymin)

        if 'hjust' in layer:
            x = (np.array(x) + layer['hjust']).tolist()
            del layer['hjust']
        else:
            layer['horizontalalignment'] = 'center'

        if 'vjust' in layer:
            y = (np.array(y) + layer['vjust']).tolist()
            del layer['vjust']
        else:
            layer['verticalalignment'] = 'center'

        for x_g,y_g,s in zip(x,y,label):
            ax.text(x_g,y_g,s,**layer)

        # resize axes
        ax.axis([xmin, xmax, ymin, ymax])
