from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import itertools

import pandas as pd
import numpy as np
from six.moves import range
from matplotlib.cbook import Bunch

from ..utils import is_scalar_or_string, suppress
from ..utils.doctools import document
from .binning import fuzzybreaks
from .stat import stat


@document
class stat_bin_2d(stat):
    """
    2 Dimensional bin counts

    {documentation}

    .. rubric:: Options for computed aesthetics

    y
        - ``..count..`` - number of points in bin
        - ``..density..`` - density of points in bin, scaled to integrate to 1
    """
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'rect', 'position': 'identity',
                      'bins': 30, 'breaks': None, 'origin': None,
                      'binwidth': None, 'drop': True}
    DEFAULT_AES = {'fill': '..count..', 'weight': None}
    CREATES = {'xmin', 'xmax', 'ymin', 'ymax', 'fill'}

    def setup_params(self, data):
        params = self.params.copy()
        params['bins'] = dual_param(params['bins'])
        params['breaks'] = dual_param(params['breaks'])
        params['binwidth'] = dual_param(params['binwidth'])
        params['origin'] = dual_param(params['origin'])
        return params

    @classmethod
    def compute_group(cls, data, scales, **params):
        bins = params['bins']
        breaks = params['breaks']
        binwidth = params['binwidth']
        origin = params['origin']
        drop = params['drop']
        weight = data.get('weight')

        if not weight:
            weight = np.ones(len(data['x']))

        # The bins will be over the dimension(full size) of the
        # trained x and y scales
        range_x = scales.x.dimension()
        range_y = scales.y.dimension()

        # Trick pd.cut into creating cuts over the range of
        # the scale
        x = np.append(data['x'], range_x)
        y = np.append(data['y'], range_y)

        # create the cutting parameters
        xbreaks = fuzzybreaks(scales.x, breaks.x, origin.x,
                              binwidth.x, bins.x)
        ybreaks = fuzzybreaks(scales.y, breaks.y, origin.y,
                              binwidth.y, bins.y)
        xbins = pd.cut(x, bins=xbreaks, labels=False, right=True)
        ybins = pd.cut(y, bins=ybreaks, labels=False, right=True)

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


stat_bin2d = stat_bin_2d


def dual_param(value):
    if is_scalar_or_string(value):
        return Bunch(x=value, y=value)

    with suppress(AttributeError):
        value.x, value.y
        return value

    if len(value) == 2:
        return Bunch(x=value[0], y=value[1])
    else:
        return Bunch(x=value, y=value)
