from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import defaultdict
import pandas as pd
import numpy as np

from ggplot.utils import make_iterable_ntimes
from .stat import stat


# TODO: Could use some speed, use a vectorized approach
# and maybe some of the pandas functions
class stat_bin2d(stat):
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'rect', 'position': 'identity',
                      'bins': 30, 'drop': True}
    CREATES = {'xmin', 'xmax', 'ymin', 'ymax', 'fill'}

    def _calculate(self, data):
        x = data.pop('x')
        y = data.pop('y')
        bins = self.params['bins']
        drop = self.params['drop']

        xlow, ylow = x.min(), y.min()
        xbinwidth = x.ptp() / bins
        ybinwidth = y.ptp() / bins

        # bin boundaries
        xlimits = [(xlow+i*xbinwidth, xlow+(i+1)*xbinwidth)
                   for i in range(bins)]
        ylimits = [(ylow+i*ybinwidth, ylow+(i+1)*ybinwidth)
                   for i in range(bins)]

        # indices
        x_idx = (min(int(np.floor_divide(num-xlow, xbinwidth)), bins-1)
                 for num in x)
        y_idx = (min(int(np.floor_divide(num-ylow, ybinwidth)), bins-1)
                 for num in y)

        if drop:
            rects = defaultdict(int)
        else:
            # TODO: Make this different
            # Need to init all bins to zero counts
            rects = defaultdict(int)

        for (i, j) in zip(x_idx, y_idx):
            _t = (xlimits[i][0], xlimits[i][1],
                  ylimits[j][0], ylimits[j][1])
            rects[_t] += 1

        xmin = [0] * len(rects)
        ymin = [0] * len(rects)
        xmax = [0] * len(rects)
        ymax = [0] * len(rects)
        count = np.zeros(len(rects))

        # Assign values
        for i, k in enumerate(rects):
            xmin[i], xmax[i], ymin[i], ymax[i] = k
            count[i] = rects[k]

        new_data = pd.DataFrame({'xmin': xmin, 'xmax': xmax,
                                 'ymin': ymin, 'ymax': ymax})

        # !!! assign colors???
        # TODO: Uncomment this when visual mapping is applied after
        # computing the stats
        # new_data['fill'] = count / count.sum()
        new_data['fill'] = ['#333333'] * len(count)

        # Copy the other aesthetics into the new dataframe
        # Note: There probably shouldn't be any for this stat
        n = len(xmin)
        for ae in data:
            new_data[ae] = make_iterable_ntimes(data[ae].iloc[0], n)
        return new_data
