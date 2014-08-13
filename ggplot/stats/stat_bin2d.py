from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import itertools

import pandas as pd
import numpy as np

from .stat import stat


class stat_bin2d(stat):
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'rect', 'position': 'identity',
                      'bins': 30, 'drop': True}
    DEFAULT_AES = {'fill': '..count..'}
    CREATES = {'xmin', 'xmax', 'ymin', 'ymax', 'fill'}

    def _calculate(self, data, scales, **kwargs):
        x = data.pop('x')
        y = data.pop('y')
        bins = self.params['bins']
        drop = self.params['drop']
        weight = data.get('weight', 1)  # hidden feature

        # The bins will be over the dimension(full size) of the
        # trained x and y scales
        range_x = scales.x.dimension((0, 0))
        range_y = scales.y.dimension((0, 0))

        # Trick pd.cut into creating cuts over the range of
        # the scale
        x = np.append(x, range_x)
        y = np.append(y, range_y)

        # create the cutting parameters
        xbins, xbreaks = pd.cut(x, bins=bins, labels=False,
                                right=True, retbins=True)
        ybins, ybreaks = pd.cut(y, bins=bins, labels=False,
                                right=True, retbins=True)

        # Remove the spurious points
        xbins = xbins[:-2]
        ybins = ybins[:-2]

        # Because we are graphing, we want to see equal breaks
        # The original breaks have an extra room to the left
        ybreaks[0] -= np.diff(np.diff(ybreaks))[0]
        xbreaks[0] -= np.diff(np.diff(xbreaks))[0]

        df = pd.DataFrame({'xbins': xbins,
                           'ybins': ybins,
                           'weights': weight})
        table = pd.pivot_table(df, values='weights',
                               index=['xbins', 'ybins'], aggfunc=np.sum)

        # create rectangles
        rects = []
        keys = itertools.product(range(len(ybreaks)-1),
                                 range(len(xbreaks)-1))
        for (j, i) in keys:
            try:
                cval = table[(i, j)]
            except KeyError:
                if drop:
                    continue
                cval = 0
            # xmin, xmax, ymin, ymax, count
            row = [xbreaks[i], xbreaks[i+1],
                   ybreaks[j], ybreaks[j+1],
                   cval]
            rects.append(row)

        new_data = pd.DataFrame(rects, columns=['xmin', 'xmax',
                                                'ymin', 'ymax',
                                                'count'])
        new_data['density'] = new_data['count'] / new_data['count'].sum()
        return new_data
