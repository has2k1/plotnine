from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from warnings import warn
import numpy as np

from ..exceptions import PlotnineError
from ..utils import match, groupby_apply, suppress


# Detect and prevent collisions.
# Powers dodging, stacking and filling.
def collide(data, width=None, name='', strategy=None, params=None):
    xminmax = ['xmin', 'xmax']
    # Determine width
    if width is not None:
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
        width = widths.iloc[0]

    # Reorder by x position then on group, relying on stable sort to
    # preserve existing ordering. The default stacking order reverses
    # the group in order to match the legend order.
    if params and 'reverse' in params and params['reverse']:
        idx = data.sort_values(
            ['xmin', 'group'], kind='mergesort').index
    else:
        data['-group'] = -data['group']
        idx = data.sort_values(
            ['xmin', '-group'], kind='mergesort').index
        data.pop('-group')

    data = data.loc[idx, :]

    # Check for overlap
    intervals = data[xminmax].drop_duplicates().as_matrix().flatten()
    intervals = intervals[~np.isnan(intervals)]

    if (len(np.unique(intervals)) > 1 and
            any(np.diff(intervals - intervals.mean()) < -1e-6)):
        msg = "{} requires non-overlapping x intervals"
        warn(msg.format(name))

    if 'ymax' in data:
        data = groupby_apply(data, 'xmin', strategy, width, params)
    elif 'y' in data:
        data['ymax'] = data['y']
        data = groupby_apply(data, 'xmin', strategy, width, params)
        data['y'] = data['ymax']
    else:
        raise PlotnineError('Neither y nor ymax defined')

    return data


# Stack overlapping intervals.
# Assumes that each set has the same horizontal position
def pos_stack(df, width, params):
    vjust = params['vjust']

    y = df['y'].copy()
    y[np.isnan(y)] = 0
    heights = np.append(0, y.cumsum())

    if params['fill']:
        heights = heights / np.abs(heights[-1])

    df['ymin'] = np.min([heights[:-1], heights[1:]], axis=0)
    df['ymax'] = np.max([heights[:-1], heights[1:]], axis=0)
    # less intuitive than (ymin + vjust(ymax-ymin)), but
    # this way avoids subtracting numbers of potentially
    # similar precision
    df['y'] = ((1-vjust)*df['ymin'] + vjust*df['ymax'])
    return df


# Dodge overlapping interval.
# Assumes that each set has the same horizontal position.
def pos_dodge(df, width, params):

    with suppress(TypeError):
        iter(width)
        width = np.asarray(width)
        width = width[df.index]

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
    udf_group = udf_group.sort_values()
    groupidx = match(df['group'], udf_group)
    groupidx = np.asarray(groupidx) + 1

    # Find the center for each group, then use that to
    # calculate xmin and xmax
    df['x'] = df['x'] + width * ((groupidx - 0.5) / n - 0.5)
    df['xmin'] = df['x'] - (d_width / n) / 2
    df['xmax'] = df['x'] + (d_width / n) / 2

    return df
