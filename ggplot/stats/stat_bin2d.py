from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import defaultdict
import numpy as np
from .stat import stat


class stat_bin2d(stat):
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'rect', 'position': 'identity',
                      'bins': 30, 'drop': True}
    CREATES = {'xmin', 'xmax', 'ymin', 'ymax', 'fill'}

    def _calculate(self, pinfo):
        # x = pinfo['x']
        # y = pinfo['y']
        # TODO: Do not remove stuff, when groups
        # are handled properly, revert to the above
        x = pinfo.pop('x')
        y = pinfo.pop('y')
        bins = self.params['bins']
        drop = self.params['drop']

        # range
        xptp, yptp = np.ptp(x), np.ptp(y)
        xlow, ylow = np.min(x), np.min(y)

        xbinwidth = xptp / bins
        ybinwidth = yptp / bins
        # bin boundaries
        xlimits = [(xlow+i*xbinwidth, xlow+(i+1)*xbinwidth)
                   for i in range(bins)]
        ylimits = [(ylow+i*ybinwidth, ylow+(i+1)*ybinwidth)
                   for i in range(bins)]

        # TODO: Try generators
        # indices
        x_idx = [min(int(np.floor_divide(num-xlow, xbinwidth)), bins-1)
                 for num in x]
        y_idx = [min(int(np.floor_divide(num-ylow, ybinwidth)), bins-1)
                 for num in y]

        if drop:
            rects = defaultdict(int)
        else:
            # TODO: Make this different
            rects = defaultdict(int)

        for (i, j) in zip(x_idx, y_idx):
            rects[(xlimits[i][0], xlimits[i][1], ylimits[j][0], ylimits[j][1])] += 1

        xmin = [0] * len(rects)
        ymin = [0] * len(rects)
        xmax = [0] * len(rects)
        ymax = [0] * len(rects)
        count = np.zeros(len(rects))

        # Assign values
        for i, k in enumerate(rects):
            xmin[i], xmax[i], ymin[i], ymax[i] = k
            count[i] = rects[k]

        pinfo['xmin'] = xmin
        pinfo['xmax'] = xmax
        pinfo['ymin'] = ymin
        pinfo['ymax'] = ymax
        # !!! assign colors???
        # pinfo['fill'] = count / count.sum()
        pinfo['fill'] = ['#333333'] * len(count)
        return pinfo
