from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from ..utils.exceptions import GgplotError, gg_warning
from ..scales.utils import zero_range
from ..utils import match, groupby_apply


# Detect and prevent collisions.
# Powers dodging, stacking and filling.
def collide(data, width=None, name='', strategy=None):
    xminmax = ['xmin', 'xmax']
    # Determine width
    if not (width is None):
        # Width set manually
        if not all([col in data.columns for col in xminmax]):
            data['xmin'] = data['x'] - width / 2
            data['xmax'] = data['x'] - width / 2
    else:
        if not all([col in data.columns for col in xminmax]):
            data['xmin'] = data['x']
            data['xmax'] = data['x']

        # Width determined from data, must be floating point constant
        widths = (data['xmax'] - data['xmin']).drop_duplicates()
        widths = widths[~np.isnan(widths)]
        if not zero_range([widths.min(), widths.max()]):
            msg = '{} requires constant width: output may be incorrect'
            gg_warning(msg.format(name))
        width = widths.iloc[0]

    # Reorder by x position, relying on stable sort to preserve existing
    # ordering, which may be by group or order.
    data = data.iloc[data['xmin'].order().index, :]  # !!! reset_index

    # Check for overlap
    intervals = data[xminmax].drop_duplicates().as_matrix().flatten()
    intervals = intervals[~np.isnan(intervals)]

    if (len(np.unique(intervals)) > 1 and
            any(np.diff(intervals - intervals.mean()) < -1e-6)):
        msg = '{} requires non-overlapping x intervals'
        gg_warning(msg.format(name))

    if 'ymax' in data:
        data = groupby_apply(data, 'xmin', strategy, width)
    elif 'y' in data:
        gg_warning('ymax not defined: adjusting position using y instead')

        data['ymax'] = data['y']
        data = groupby_apply(data, 'xmin', strategy, width)
        data['y'] = data['ymax']
    else:
        GgplotError('Neither y nor ymax defined')

    return data


# Stack overlapping intervals.
# Assumes that each set has the same horizontal position
def pos_stack(df, width):
    if len(df) == 1:
        return df

    n = len(df) + 1

    if all(np.isnan(df['x'])):
        heights = [np.nan] * n
    else:
        y = df['y'].copy()
        y[np.isnan(y)] = 0
        heights = np.append(0, y.cumsum())

    df['ymin'] = heights[:-1]
    df['ymax'] = heights[1:]
    df['y'] = df['ymax']
    return df


# Stack overlapping intervals and set height to 1.
# Assumes that each set has the same horizontal position.
def pos_fill(df, width):
    df = pos_stack(df, width)
    df['ymin'] = df['ymin'] / df['ymax'].max()
    df['ymax'] = df['ymax'] / df['ymax'].max()
    df['y'] = df['ymax']
    return df


# Dodge overlapping interval.
# Assumes that each set has the same horizontal position.
def pos_dodge(df, width):
    width = np.asarray(width)
    udf_group = df['group'].drop_duplicates()

    n = len(udf_group)
    if n == 1:
        return df

    if not all([col in df.columns for col in ['xmin', 'xmax']]):
        df['xmin'] = df['x']
        df['xmax'] = df['x']

    d_width = np.max(df['xmax'] - df['xmin'])

    # Have a new group index from 1 to number of groups.
    # This might be needed if the group numbers in this set don't
    # include all of 1:n
    groupidx = match(df['group'],
                     udf_group.sort(inplace=False))
    groupidx = np.asarray(groupidx) + 1

    # Find the center for each group, then use that to
    # calculate xmin and xmax
    df['x'] = df['x'] + width * ((groupidx - 0.5) / n - 0.5)
    df['xmin'] = df['x'] - (d_width / n) / 2
    df['xmax'] = df['x'] + (d_width / n) / 2

    return df
