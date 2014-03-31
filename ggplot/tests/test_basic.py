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

def _build_testing_df():
    df = pd.DataFrame({
        "x": np.arange(0, 100),
        "y": np.arange(0, 100),
        "z": np.arange(0, 100)
    })

    df['cat'] = np.where(df.x*2 > 50, 'blah', 'blue')
    df['cat'] = np.where(df.y > 50, 'hello', df.cat)
    df['cat2'] = np.where(df.y < 15, 'one', 'two')
    df['y'] = np.sin(df.y)
    df['z'] = df['y'] + 100
    df['c'] = np.where(df.x%2==0,"red", "blue")
    return df

def _build_meat_df():
    meat['date'] = pd.to_datetime(meat.date)
    return meat

@cleanup
def test_geom_density():
    df = _build_testing_df()
    gg = ggplot(aes(x="x", color="c"), data=df)
    gg = gg + geom_density() + xlab("x label") + ylab("y label")
    assert_same_ggplot(gg, "geom_density")

@cleanup
def test_geom_histogram():
    df = _build_testing_df()
    # TODO: use fill aesthetic for a better test
    gg = ggplot(aes(x="x", y="y", shape="cat2", color="cat"), data=df)
    assert_same_ggplot(gg + geom_histogram(), "geom_hist")
    assert_same_ggplot(gg + geom_histogram() + ggtitle("My Histogram"), "geom_hist_title")

@cleanup
def test_geom_point():
    df = _build_testing_df()
    gg = ggplot(aes(x="x", y="y", shape="cat2", color="cat"), data=df)
    assert_same_ggplot(gg + geom_point(), "geom_point")
    gg = gg + geom_point() + geom_vline(x=50, ymin=-10, ymax=10)
    assert_same_ggplot(gg, "geom_point_vline")

@cleanup
def test_geom_area():
    df = _build_testing_df()
    gg = ggplot(aes(x='x', ymax='y', ymin='z', color="cat2"), data=df)
    assert_same_ggplot(gg + geom_area(), "geom_area")

@cleanup
def test_geom_text():
    gg = ggplot(aes(x='wt',y='mpg',label='name'),data=mtcars) + geom_text()
    assert_same_ggplot(gg, "geom_text")

@cleanup
def test_geom_line():
    p = ggplot(mtcars, aes(x='wt', y='mpg', colour='factor(cyl)', size='mpg', linetype='factor(cyl)'))
    assert_same_ggplot(p + geom_line(), "factor_geom_line")

@cleanup
def test_geom_rect():
    df = pd.DataFrame({
        'xmin':[3, 5, 3, 3, 9, 4, 8, 3, 9, 2, 9, 1, 11, 4, 7, 1],
        'xmax':[10, 8, 10, 4, 10, 5, 9, 4, 10, 4, 11, 2, 12, 6, 9, 12],
        'ymin':[3, 3, 6, 2, 2, 6, 6, 8, 8, 4, 4, 2, 2, 1, 1, 4],
        'ymax':[5, 7, 7, 7, 7, 8, 8, 9, 9, 6, 6, 5, 5, 2, 2, 5]})
    p = ggplot(df, aes(xmin='xmin', xmax='xmax', ymin='ymin', ymax='ymax'))
    p += geom_rect(xmin=0, xmax=13, ymin=0, ymax=10)
    p += geom_rect(colour="white", fill="white")
    p += xlim(0, 13)
    assert_same_ggplot(p, "geom_rect_inv")

@cleanup
def test_factor_geom_point():
    p = ggplot(mtcars, aes(x='wt', y='mpg', colour='factor(cyl)', size='mpg', linetype='factor(cyl)'))
    assert_same_ggplot(p + geom_point(), "factor_geom_point")

@cleanup
def test_factor_geom_point_line():
    p = ggplot(mtcars, aes(x='wt', y='mpg', colour='factor(cyl)', size='mpg', linetype='factor(cyl)'))
    assert_same_ggplot(p + geom_line() + geom_point(), "factor_geom_point_line")

@cleanup
def test_factor_point_line_title_lab():
    p = ggplot(mtcars, aes(x='wt', y='mpg', colour='factor(cyl)', size='mpg', linetype='factor(cyl)'))
    p = p + geom_point() + geom_line(color='lightblue') + ggtitle("Beef: It's What's for Dinner")
    p = p + xlab("Date") + ylab("Head of Cattle Slaughtered")
    assert_same_ggplot(p, "factor_complicated")

@cleanup
def test_labs():
    p = ggplot(mtcars, aes(x='wt', y='mpg', colour='factor(cyl)', size='mpg', linetype='factor(cyl)'))
    p = p + geom_point() + geom_line(color='lightblue')
    p = p + labs(title="Beef: It's What's for Dinner", x="Date", y="Head of Cattle Slaughtered")
    assert_same_ggplot(p, "labs")

@cleanup
def test_factor_bar():
    p = ggplot(aes(x='factor(cyl)'), data=mtcars)
    assert_same_ggplot(p + geom_bar(), "factor_geom_bar")

@cleanup
def test_stats_smooth():
    df = _build_testing_df()
    gg = ggplot(aes(x="x", y="y", color="cat"), data=df)
    gg = gg + stat_smooth(se=False) + ggtitle("My Smoothed Chart")
    assert_same_ggplot(gg, "stat_smooth")

@cleanup
def test_stats_bin2d():
    import matplotlib.pyplot as plt
    if not hasattr(plt, "hist2d"):
        import nose
        raise nose.SkipTest("stat_bin2d only works with newer matplotlib (1.3) versions.")
    df = _build_testing_df()
    gg = ggplot(aes(x='x', y='y', shape='cat', color='cat2'), data=df)
    assert_same_ggplot(gg + stat_bin2d(), "stat_bin2d")

@cleanup
def test_alpha_density():
    gg = ggplot(aes(x='mpg'), data=mtcars)
    assert_same_ggplot(gg + geom_density(fill=True, alpha=0.3), "geom_density_alpha")

@cleanup
def test_facet_wrap():
    df = _build_testing_df()
    gg = ggplot(aes(x='x', ymax='y', ymin='z'), data=df)
    #assert_same_ggplot(gg + geom_bar() + facet_wrap(x="cat2"), "geom_bar_facet")
    assert_same_ggplot(gg + geom_area() + facet_wrap(x="cat2"), "geom_area_facet")

@cleanup
def test_facet_wrap2():
    meat = _build_meat_df()
    meat_lng = pd.melt(meat, id_vars=['date'])
    p = ggplot(aes(x='date', y='value', colour='variable'), data=meat_lng)
    assert_same_ggplot(p + geom_density(fill=True, alpha=0.3) + facet_wrap("variable"), "geom_density_facet")
    assert_same_ggplot(p + geom_line(alpha=0.3) + facet_wrap("variable"), "geom_line_facet")

@cleanup 
def test_facet_grid_exceptions():
    meat = _build_meat_df()
    meat_lng = pd.melt(meat, id_vars=['date'])    
    p = ggplot(aes(x="date", y="value", colour="variable", shape="variable"), meat_lng)
    with assert_raises(Exception):
        print(p + geom_point() + facet_grid(y="variable"))
    with assert_raises(Exception):
        print(p + geom_point() + facet_grid(y="variable", x="NOT_AVAILABLE"))
    with assert_raises(Exception):
        print(p + geom_point() + facet_grid(y="NOT_AVAILABLE", x="variable"))

@cleanup
def test_facet_grid():
    # only use a small subset of the data to speedup tests
    # N=53940 -> N=7916 and only 2x2 facets
    _mask1 = (diamonds.cut == "Ideal") | (diamonds.cut == "Good")
    _mask2 = (diamonds.clarity == "SI2") | (diamonds.clarity == "VS1")
    _df = diamonds[_mask1 & _mask2]
    p = ggplot(aes(x='x', y='y', colour='z'), data=_df)
    p = p + geom_point() + scale_colour_gradient(low="white", high="red") 
    p = p + facet_grid("cut", "clarity")
    assert_same_ggplot(p, "diamonds_big")
    p = ggplot(aes(x='carat'), data=_df)
    p = p + geom_density() + facet_grid("cut", "clarity")
    assert_same_ggplot(p, "diamonds_facet")

@cleanup
def test_smooth_se():
    meat = _build_meat_df()
    p = ggplot(aes(x='date', y='beef'), data=meat)
    assert_same_ggplot(p + geom_point() + stat_smooth(), "point_smooth_se")
    assert_same_ggplot(p + stat_smooth(), "smooth_se")

@cleanup
def test_scale_xy_continous():
    meat = _build_meat_df()
    p = ggplot(aes(x='date', y='beef'), data=meat)
    p = p + geom_point() + scale_x_continuous("This is the X")
    p = p + scale_y_continuous("Squared", limits=[0, 1500])
    assert_same_ggplot(p, "scale1")

@cleanup
def test_ylim():
    meat = _build_meat_df()
    p = ggplot(aes(x='date', y='beef'), data=meat)
    assert_same_ggplot(p + geom_point() + ylim(0, 1500), "ylim")

@cleanup
def test_scale_date():
    meat = _build_meat_df()
    gg = ggplot(aes(x='date', y='beef'), data=meat) + geom_line() 
    assert_same_ggplot(gg+scale_x_date(labels="%Y-%m-%d"), "scale_date")

@cleanup
def test_diamond():    
    p = ggplot(aes(x='x', y='y', colour='z'), data=diamonds.head(4))
    p = p + geom_point() + scale_colour_gradient(low="white", high="red") 
    p = p + facet_wrap("cut")
    assert_same_ggplot(p, "diamonds_small")

def test_aes_positional_args():
    result = aes("weight", "hp")
    expected = {"x": "weight", "y": "hp"}
    assert_equal(result, expected)

    result3 = aes("weight", "hp", "qsec")
    expected3 = {"x": "weight", "y": "hp", "color": "qsec"}
    assert_equal(result3, expected3)


def test_aes_keyword_args():
    result = aes(x="weight", y="hp")
    expected = {"x": "weight", "y": "hp"}
    assert_equal(result, expected)

    result3 = aes(x="weight", y="hp", color="qsec")
    expected3 = {"x": "weight", "y": "hp", "color": "qsec"}
    assert_equal(result3,expected3)


def test_aes_mixed_args():
    result = aes("weight", "hp", color="qsec")
    expected = {"x": "weight", "y": "hp", "color": "qsec"}
    assert_equal(result, expected)
