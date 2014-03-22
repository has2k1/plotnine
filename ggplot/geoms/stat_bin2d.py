from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom

import matplotlib.pyplot

if hasattr(matplotlib.pyplot, 'hist2d'):
    class stat_bin2d(geom):
        VALID_AES = {'x', 'y', 'fill'}
        REQUIRED_AES = {'x', 'y'}
        DEFAULT_PARAMS = {'geom': None, 'position': 'identity',
                'bins': 30, 'drop': True}

        _groups = {'color', 'alpha'}

        def _plot_unit(self, pinfo, ax):
            x = pinfo.pop('x')
            y = pinfo.pop('y')

            ax.hist2d(x, y, cmap=matplotlib.pyplot.cm.Blues, **pinfo)
else:
    def stat_bin2d(*args, **kwargs):
        import matplotlib
        print("stat_bin2d only works with newer matplotlib versions, but found only %s" %
              matplotlib.__version__)
