from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import get_assert_same_ggplot, cleanup
assert_same_ggplot = get_assert_same_ggplot(__file__)

from ggplot import *
from ggplot.exampledata import diamonds

import numpy as np
import pandas as pd
import datetime

def _build_testing_df():
    df = pd.DataFrame({
        "x": np.arange(0, 10),
        "y": np.arange(0, 10),
        "z": np.arange(0, 10),
        "a": [1,1,1,1,1,2,2,2,3,3],
        "b": ["a","a","a","a","a","b","b","b","c","c"]
    })

    df['facets'] = np.where(df.x > 4, 'over', 'under')
    df['facets2'] = np.where((df.x % 2) == 0, 'even', 'uneven')
    return df

@cleanup
def test_labels_auto():
    df = pd.DataFrame({ "y" : [3.362, 1.2, 3.424, 2.574, 0.679],
                        "x" : ["BF","BF","Flann","FastMatch","FastMatch2"],
                        "c" : ["a", "b", "a", "a","a"]})
    p = ggplot(df, aes(x = 'x', y = 'y', fill="c"))
    gg = p + geom_bar(stat="bar")
    assert_same_ggplot(gg, "labels_auto")

@cleanup
def test_labels_manual():
    df = pd.DataFrame({ "y" : [3.362, 1.2, 3.424, 2.574, 0.679],
                        "x" : ["BF","BF","Flann","FastMatch","FastMatch2"],
                        "c" : ["a", "b", "a", "a","a"]})
    p = ggplot(df, aes(x = 'x', y = 'y', fill="c"))
    gg2 = p + geom_bar(stat="bar", labels=["BF","Flann","FastMatch"])
    assert_same_ggplot(gg2, "labels_manual")

@cleanup
def test_facet_grid_discrete():
    df = _build_testing_df()
    gg = ggplot(aes(x='a', y='y', fill='y'), data=df)
    assert_same_ggplot(gg + geom_bar(stat='bar') + facet_grid(x="facets", y="facets2"),
                       "faceting_grid_discrete")

@cleanup
def test_facet_wrap_discrete():
    df = _build_testing_df()
    gg = ggplot(aes(x='a', y='y'), data=df)
    assert_same_ggplot(gg + geom_bar(stat='bar') + facet_wrap(x="facets"), "faceting_wrap_discrete")

@cleanup
def test_facet_colors():
    gg = ggplot(diamonds, aes(x = 'clarity', fill = 'cut', color='cut')) +\
            stat_bin(binwidth=1200) + facet_wrap("color")
    assert_same_ggplot(gg, "facet_colors")

# @cleanup
# def test_date_hist():
#     dates = [datetime.date(2014, 3, i) for i in range(1, 31)]
#     gg = ggplot(pd.DataFrame({"x": dates}), aes(x='x')) + geom_histogram()
#     assert_same_ggplot(gg, "geom_hist_date")

@cleanup
def test_color_hist():
    data = { "a" : np.concatenate([np.repeat("a", int(3.262*100)),
                                    np.repeat("b", int(2.574*100))]),
            "c" : np.concatenate([np.repeat("c1", int(3.262*40)+1),
                                    np.repeat("c2", int(3.262*60)),
                                    np.repeat("c1", int(2.574*55)+1),
                                    np.repeat("c2", int(2.574*45))])}
    df2 = pd.DataFrame(data)

    gg = ggplot(df2, aes(x = 'a', fill="c")) + geom_histogram()
    assert_same_ggplot(gg, "color_hist")
