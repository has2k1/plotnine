from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import get_assert_same_ggplot, cleanup, assert_same_elements
assert_same_ggplot = get_assert_same_ggplot(__file__)


from nose.tools import (assert_true, assert_raises, assert_is,
                        assert_is_not, assert_equal)

from ggplot import *

import six
import pandas as pd
from ggplot.components import assign_visual_mapping

def test_legend_structure():
    df = pd.DataFrame({
        'xmin': [1, 3, 5],
        'xmax': [2, 3.5, 7],
        'ymin': [1, 4, 6],
        'ymax': [5, 5, 9],
        'fill': ['blue', 'red', 'green'],
        'quality': ['good', 'bad', 'ugly'],
        'alpha': [0.1, 0.5, 0.9],
        'texture': ['hard', 'soft', 'medium']})

    gg = ggplot(df, aes(xmin='xmin', xmax='xmax', ymin='ymin', ymax='ymax',
                        colour='quality', fill='fill', alpha='alpha',
                        linetype='texture'))
    new_df, legend = assign_visual_mapping(df, gg.aesthetics, gg)

    # All mapped aesthetics must have an entry in the legend
    for aesthetic in ('color', 'fill', 'alpha', 'linetype'):
        assert(aesthetic in legend)

    # None of the unassigned aesthetic should have an entry in the legend
    assert('size' not in legend)
    assert('shape' not in legend)

    # legend entries should remember the column names
    # to which they were mapped
    assert(legend['fill']['column_name'] == 'fill')
    assert(legend['color']['column_name'] == 'quality')
    assert(legend['linetype']['column_name'] == 'texture')
    assert(legend['alpha']['column_name'] == 'alpha')

    # Discrete columns for non-numeric data
    assert(legend['fill']['scale_type'] == 'discrete')
    assert(legend['color']['scale_type'] == 'discrete')
    assert(legend['linetype']['scale_type'] == 'discrete')
    assert(legend['alpha']['scale_type'] == 'continuous')

    # Alternate
    df2 = pd.DataFrame.copy(df)
    df2['fill'] = [90, 3.2, 8.1]
    gg = ggplot(df2, aes(xmin='xmin', xmax='xmax', ymin='ymin', ymax='ymax',
                        colour='quality', fill='fill', alpha='alpha',
                        linetype='texture'))
    new_df, legend = assign_visual_mapping(df2, gg.aesthetics, gg)
    assert(legend['fill']['scale_type'] == 'continuous')
