from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import numpy as np
from matplotlib.cbook import Bunch

from ..utils import is_waive
from ..utils.exceptions import GgplotError
from ..scales.scale import scale_continuous, scale_discrete


class coord(object):
    """
    Base class for all coordinate systems
    """
    # If the coordinate system is linear
    is_linear = False

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.coordinates = self
        return gg

    def transform(self, data, panel_scales, munch=False):
        """
        Transform data before it is plotted

        This is used to "transform the coordinate axes".
        Subclasses should override this method
        """
        return data

    def expand_default(self, scale, discrete=(0, 0.6),
                       continuous=(0.05, 0)):
        """
        Expand a single scale
        """
        if is_waive(scale.expand):
            if isinstance(scale, scale_discrete):
                return discrete
            elif isinstance(scale, scale_continuous):
                return continuous
            else:
                name = scale.__class__.__name__
                msg = "Failed to expand scale '{}'".format(name)
                raise GgplotError(msg)
        else:
            return scale.expand

    def range(self, scales):
        """
        Return the range along the dimensions of the coordinate system
        """
        # Defaults to providing the 2D x-y ranges
        return Bunch(x=scales['x_range'], y=scales['y_range'])

    def distance(self, x, y, panel_scales):
        msg = "The coordinate should implement this method."
        raise NotImplementedError(msg)

    def munch(self, data, panel_scales):
        ranges = self.range(panel_scales)

        data.loc[data['x'] == -np.inf, 'x'] = ranges.x[0]
        data.loc[data['x'] == np.inf, 'x'] = ranges.x[1]
        data.loc[data['y'] == -np.inf, 'y'] = ranges.y[0]
        data.loc[data['y'] == np.inf, 'y'] = ranges.y[1]

        dist = self.distance(data['x'], data['y'], panel_scales)
        bool_idx = data['group'].iloc[1:] != data['group'].iloc[:-1]
        dist[bool_idx.values] = np.nan

        # Munch
        munched = munch_data(data, dist)
        return munched


def dist_euclidean(x, y):
    x = np.asarray(x)
    y = np.asarray(y)
    return np.sqrt((x[:-1] - x[1:])**2 +
                   (y[:-1] - y[1:])**2)


def interp(start, end, n):
    return np.linspace(start, end, n, endpoint=False)


def munch_data(data, dist):
    x, y = data['x'], data['y']
    segment_length = 0.01

    # How many endpoints for each old segment,
    # not counting the last one
    extra = np.maximum(np.floor(dist/segment_length), 1)
    extra[np.isnan(extra)] = 1
    extra = extra.astype(int, copy=False)

    # Generate extra pieces for x and y values
    # The final point must be manually inserted at the end
    x = [interp(start, end, n)
         for start, end, n in zip(x[:-1], x[1:], extra)]
    y = [interp(start, end, n)
         for start, end, n in zip(y[:-1], y[1:], extra)]
    x.append(data['x'].iloc[-1])
    y.append(data['y'].iloc[-1])
    x = np.hstack(x)
    y = np.hstack(y)

    # Replicate other aesthetics: defined by start point
    # but also must include final point
    idx = np.hstack([
        np.repeat(np.arange(len(data)-1), extra),
        len(data)-1])

    munched = data.loc[idx, data.columns.difference(['x', 'y'])]
    munched['x'] = x
    munched['y'] = y
    munched.reset_index(drop=True, inplace=True)

    return munched
