from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from six.moves import xrange

from nose.tools import assert_equal, assert_true, assert_raises

from . import get_assert_same_ggplot, cleanup
assert_same_ggplot = get_assert_same_ggplot(__file__)

from ggplot import *
from ggplot.exampledata import diamonds

import numpy as np
import pandas as pd

def _build_line_df():
    np.random.seed(7776)
    df = pd.DataFrame({'wt': mtcars['wt'][:10],
                       'mpg': mtcars['mpg'][:10],
                       'a': np.random.normal(15, size=10),
                       'b': np.random.normal(0, size=10)
                       })
    return df

@cleanup
def test_geom_abline():
    df = _build_line_df()
    gg = ggplot(df, aes(x='wt', y='mpg'))
    gg = gg + geom_point() +  geom_abline(intercept=22, slope=.8, size=10)
    assert_same_ggplot(gg, 'geom_abline')


@cleanup
def test_geom_abline_multiple():
    df = _build_line_df()
    gg = ggplot(df, aes(x='wt', y='mpg'))
    gg = gg + geom_point() + geom_abline(intercept=(20, 12),
                                         slope=(.8, 2),
                                         color=('red', 'blue'),
                                         alpha=(.3, .9),
                                         size=(10, 20))
    assert_same_ggplot(gg, 'geom_abline_multiple')

@cleanup
def test_geom_abline_mapped():
    df = _build_line_df()
    gg = ggplot(df, aes(x='wt', y='mpg', intercept='a', slope='b'))
    gg = gg + geom_point() +  geom_abline(size=2)
    assert_same_ggplot(gg, 'geom_abline_mapped')

# TODO: Uncomment when the handling is proper
# @cleanup
# def test_geom_abline_functions():
#     df = _build_line_df()
#
#     def sfunc(x, y):
#         return (y[-1] - y[0]) / (x[-1] - x[0])
#
#     def ifunc(y):
#         return np.mean(y)
#     gg = ggplot(df, aes(x='wt', y='mpg'))
#
#     # Note, could have done intercept=np.mean
#     gg = gg + geom_point() +  geom_abline(aes(x='wt', y='mpg'),
#                                           slope=sfunc,
#                                           intercept=ifunc)
#     assert_same_ggplot(gg, 'geom_abline_functions')

@cleanup
def test_geom_vline():
    df = _build_line_df()
    gg = ggplot(df, aes(x='wt', y='mpg'))
    gg = gg + geom_point() +  geom_vline(xintercept=3, size=10)
    assert_same_ggplot(gg, 'geom_vline')

@cleanup
def test_geom_vline_multiple():
    df = _build_line_df()
    gg = ggplot(df, aes(x='wt', y='mpg'))
    gg = gg + geom_point() +  geom_vline(xintercept=[2.5, 3.5], size=10)
    assert_same_ggplot(gg, 'geom_vline_multiple')

@cleanup
def test_geom_vline_mapped():
    df = _build_line_df()
    gg = ggplot(df, aes(x='wt', y='mpg', xintercept='wt'))
    gg = (gg + geom_point(size=200, color='green', fill='blue', alpha=.7) +
          geom_vline(size=2))
    assert_same_ggplot(gg, 'geom_vline_mapped')

# @cleanup
# def test_geom_vline_function():
#     df = _build_line_df()
#     gg = ggplot(df, aes(x='wt', y='mpg'))
#     def ifunc(x):
#         return np.mean(x)
#     gg = gg + geom_point() +  geom_vline(aes(x='wt'), xintercept=ifunc)
#     assert_same_ggplot(gg, 'geom_vline_function')

@cleanup
def test_geom_hline():
    df = _build_line_df()
    gg = ggplot(df, aes(x='wt', y='mpg'))
    gg = gg + geom_point() +  geom_hline(yintercept=20, size=10)
    assert_same_ggplot(gg, 'geom_hline')

@cleanup
def test_geom_hline_multiple():
    df = _build_line_df()
    gg = ggplot(df, aes(x='wt', y='mpg'))
    gg = gg + geom_point() +  geom_hline(yintercept=[16., 24.], size=10)
    assert_same_ggplot(gg, 'geom_hline_multiple')

@cleanup
def test_geom_hline_mapped():
    df = _build_line_df()
    gg = ggplot(df, aes(x='wt', y='mpg', yintercept='mpg'))
    gg = (gg + geom_point(size=150, color='blue', alpha=.5) +
          geom_hline(size=2))
    assert_same_ggplot(gg, 'geom_hline_mapped')

# @cleanup
# def test_geom_hline_function():
#     df = _build_line_df()
#     gg = ggplot(df, aes(x='wt', y='mpg'))
#     def ifunc(y):
#         return np.mean(y)
#     gg = gg + geom_point() +  geom_hline(aes(y='mpg'), yintercept=ifunc)
#     assert_same_ggplot(gg, 'geom_hline_function')

@cleanup
def test_geom_festival_of_lines():
    df = _build_line_df()
    df['m'] = [5] * len(df)
    df['c'] = df['mpg'] - df['m'] * df['wt']
    colors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF',
              '#4B0082','#8F00FF', '#FB00FF', '#808080', '#000000']
    gg = ggplot(df, aes(x='wt', y='mpg', xintercept='wt',
                        yintercept='mpg', slope='m', intercept='c'))
    gg = (gg + geom_point(size=150, color=colors, alpha=.9) +
          geom_abline(size=2, color=colors) +
          geom_vline(size=2, color=colors) +
          geom_hline(size=2, color=colors))
    assert_same_ggplot(gg, 'geom_festival_of_lines')
