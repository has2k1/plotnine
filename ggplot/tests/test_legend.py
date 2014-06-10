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
from ggplot.utils.exceptions import GgplotError

def get_test_df():
    df = pd.DataFrame({
        'xmin': [1, 3, 5],
        'xmax': [2, 3.5, 7],
        'ymin': [1, 4, 6],
        'ymax': [5, 5, 9],
        'fill': ['blue', 'red', 'green'],
        'quality': ['good', 'bad', 'ugly'],
        'alpha': [0.1, 0.5, 0.9],
        'texture': ['hard', 'soft', 'medium']})
    return df

def test_legend_structure():
    df = get_test_df()

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
    assert(legend['alpha']['scale_type'] == 'discrete')

    # Alternate
    df2 = pd.DataFrame.copy(df)
    df2['fill'] = [90, 3.2, 8.1]
    gg = ggplot(df2, aes(xmin='xmin', xmax='xmax', ymin='ymin', ymax='ymax',
                        colour='quality', fill='fill', alpha='alpha',
                        linetype='texture'))
    new_df, legend = assign_visual_mapping(df2, gg.aesthetics, gg)
    assert(legend['fill']['scale_type'] == 'discrete')

    # Test if legend switches to continuous for more than 8 numerical values
    df3 = pd.DataFrame({
        'xmin': [1, 3, 5, 8, 2, 1, 4, 7, 9],
        'xmax': [2, 3.5, 7, 12, 3, 2, 6, 8, 10],
        'ymin': [1, 4, 6, 0, 0, 0, 0, 0, 0],
        'ymax': [5, 5, 9, 1, 1, 1, 1, 1, 1],
        'fill': ['blue', 'red', 'green', 'green', 'green',
                 'green', 'green', 'green', 'brown'],
        'quality': ['good', 'bad', 'ugly', 'horrible', 'quite awful',
                    'impertinent', 'jolly', 'hazardous', 'ok'],
        'alpha': [0.1, 0.2, 0.4, 0.5, 0.6, 0.65, 0.8, 0.82, 0.83],
        'texture': ['hard', 'soft', 'medium', 'fluffy', 'slimy', 'rough',
                    'edgy', 'corny', 'slanted']
    })
    gg = ggplot(df2, aes(xmin='xmin', xmax='xmax', ymin='ymin', ymax='ymax',
                        colour='quality', fill='fill', alpha='alpha',
                        linetype='texture'))
    new_df, legend = assign_visual_mapping(df3, gg.aesthetics, gg)
    assert(legend['alpha']['scale_type'] == 'continuous')

    # Test if legend raises GgplotError when size and alpha is fed non numeric data
    gg = ggplot(df3, aes(size="fill"))
    assert_raises(GgplotError, assign_visual_mapping, df3, gg.aesthetics, gg)
    gg = ggplot(df3, aes(alpha="fill"))
    assert_raises(GgplotError, assign_visual_mapping, df3, gg.aesthetics, gg)

@cleanup
def test_alpha_rect():
    df = get_test_df()
    p = ggplot(df, aes(xmin='xmin', xmax='xmax', ymin='ymin', ymax='ymax',
            colour='quality', fill='fill', alpha='alpha',
            linetype='texture'))
    p += geom_rect(size=5)
    assert_same_ggplot(p, "legend_alpha_rect")

@cleanup
def test_alpha():
    diamonds["test"] = diamonds["clarity"].map(len)
    p = ggplot(diamonds[::50], aes(x='carat', y='price', colour='test',
                                   size='test', alpha='test'))
    #p = ggplot(diamonds[1:60000:50], aes(x='carat', y='price', shape='clarity'))
    p = p + geom_point() + ggtitle("Diamonds: A Plot")
    p = p + xlab("Carat") + ylab("Price")
    assert_same_ggplot(p, "legend_alpha")

@cleanup
def test_linetype():
    meat_lng = pd.melt(meat[['date', 'beef', 'pork', 'broilers']], id_vars='date')
    p = ggplot(aes(x='date', y='value', colour='variable',
               linetype='variable', shape='variable'), data=meat_lng) + \
        geom_line() + geom_point() +\
        ylim(0, 3000)
    assert_same_ggplot(p, "legend_linetype")

@cleanup
def test_shape_alpha():
    diamonds["test"] = diamonds["clarity"].map(len)
    df = diamonds[::50]
    p = ggplot(df, aes(x='carat', y='price', colour='test', size='test',
                       alpha='test', shape='clarity')) + geom_point()
    assert_same_ggplot(p, "legend_shape_alpha")


