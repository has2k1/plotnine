from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import get_assert_same_ggplot, cleanup

assert_same_ggplot = get_assert_same_ggplot(__file__)

from ggplot import *

import numpy as np
import pandas as pd


def _build_testing_df():
    df = pd.DataFrame({
        "x": np.arange(0, 10),
        "y": np.arange(0, 10),
        "z": np.arange(0, 10),
        "a": [1,1,1,1,1,2,2,2,3,3]
    })

    df['facets'] = np.where(df.x > 4, 'over', 'under')
    df['facets2'] = np.where((df.x % 2) == 0, 'even', 'uneven')
    return df


def _build_small_df():
    return pd.DataFrame({
        "x": [1, 2, 1, 2],
        "y": [1, 2, 3, 4],
        "a": ["a", "b", "a", "b"],
        "b": ["c", "c", "d", "d"]
    })


# faceting with bar plots does not work yet: see https://github.com/yhat/ggplot/issues/196
#@cleanup
#def test_facet_grid_descrete():
#    df = _build_testing_df()
#    gg = ggplot(aes(x='a'), data=df)
#    assert_same_ggplot(gg + geom_bar() + facet_grid(x="facets", y="facets2"),
#                       "faceting_grid_descrete")

#@cleanup
#def test_facet_wrap_descrete():
#    df = _build_testing_df()
#    gg = ggplot(aes(x='a'), data=df)
#    assert_same_ggplot(gg + geom_bar() + facet_wrap(x="facets"), "faceting_wrap_descrete")

@cleanup
def test_facet_grid_continous():
    df = _build_testing_df()
    p = ggplot(aes(x='x', y='y', colour='z'), data=df)
    p = p + geom_point() + scale_colour_gradient(low="blue", high="red")
    p = p + facet_grid("facets", "facets2")
    assert_same_ggplot(p, "faceting_grid_continous")

@cleanup
def test_facet_wrap_continous():
    df = _build_testing_df()
    p = ggplot(aes(x='x', y='y', colour='z'), data=df)
    p = p + geom_point() + scale_colour_gradient(low="blue", high="red")
    p = p + facet_wrap("facets")
    assert_same_ggplot(p, "faceting_wrap_continous")
