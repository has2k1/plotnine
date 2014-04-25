from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import defaultdict
import pandas as pd
import numpy as np

from ggplot.utils import make_iterable_ntimes
from .stat import stat


class stat_bin2d(stat):
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'rect', 'position': 'identity',
                      'bins': 30, 'drop': True, 'weight': 1,
                      'right': False}
    CREATES = {'xmin', 'xmax', 'ymin', 'ymax', 'fill'}

    def _calculate(self, data):
        x = data.pop('x')
        y = data.pop('y')
        bins = self.params['bins']
        drop = self.params['drop']
        right = self.params['right']
        weight = make_iterable_ntimes(self.params['weight'], len(x))

        # create the cutting parameters
        x_assignments, xbreaks = pd.cut(x, bins=bins, labels=False,
                                        right=right, retbins=True)
        y_assignments, ybreaks = pd.cut(y, bins=bins, labels=False,
                                        right=right, retbins=True)
        # create rectangles
        # xmin, xmax, ymin, ymax, fill=count
        df = pd.DataFrame({'xbin': x_assignments,
                           'ybin': y_assignments,
                           'weights': weight})
        table = pd.pivot_table(df, values='weights',
                               rows=['xbin', 'ybin'], aggfunc=np.sum)
        rects = np.array([[xbreaks[i], xbreaks[i+1],
                           ybreaks[j], ybreaks[j+1],
                           table[(i, j)]]
                          for (i, j) in table.keys()])
        new_data = pd.DataFrame(rects, columns=['xmin', 'xmax',
                                                'ymin', 'ymax',
                                                'fill'])
        # !!! assign colors???
        # TODO: Remove this when visual mapping is applied after
        # computing the stats
        new_data['fill'] = ['#333333'] * len(new_data)

        # Copy the other aesthetics into the new dataframe
        # Note: There probably shouldn't be any for this stat
        n = len(new_data)
        for ae in data:
            new_data[ae] = make_iterable_ntimes(data[ae].iloc[0], n)
        return new_data
