from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
from matplotlib.dates import AutoDateLocator
from matplotlib.dates import DateLocator, DateFormatter
from .utils import trans_new

from .scale_xy import scale_position_continuous


class scale_datetime(scale_position_continuous):

    def __init__(self, **kwargs):
        if 'breaks' in kwargs:
            if callable(kwargs['breaks']):
                _loc = kwargs['breaks']()
                if isinstance(_loc, DateLocator):
                    locator_factory = kwargs.pop('breaks')
        else:
            locator_factory = AutoDateLocator

        if 'labels' in kwargs:
            if isinstance(kwargs['labels'], DateFormatter):
                formatter = kwargs.pop('labels')
        else:
            formatter = DateFormatter('%Y-%m-%d')

        def trans(series):
            series = pd.Series(
                [pd.Timestamp.toordinal(item) for item in series])
            return series

        def inv(series):
            series = pd.Series(
                [pd.Timestamp.fromordinal(item) for item in series])
            return series

        self.trans = trans_new('datetime', trans, inv)()
        self.trans.locator_factory = locator_factory
        self.trans.formatter = formatter
        scale_position_continuous.__init__(self, **kwargs)


class scale_x_datetime(scale_datetime):
    aesthetics = ['x', 'xmin', 'xmax', 'xend']


class scale_y_datetime(scale_datetime):
    aesthetics = ['y', 'ymin', 'ymay', 'yend']


# users expect theme
scale_x_date = scale_x_datetime
scale_y_date = scale_y_datetime
