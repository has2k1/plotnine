from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
from six.moves import xrange

from nose.tools import assert_equal, assert_true, assert_raises
from matplotlib.testing.decorators import image_comparison, cleanup

import os

import pandas as pd
import numpy as np

from ggplot import *
from ggplot.exampledata import diamonds


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
    meat = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     '..', 'exampledata', 'meat.csv'))
    meat['date'] = pd.to_datetime(meat.date)
    return meat

@image_comparison(baseline_images=['geom_density'], extensions=["png"])
def test_geom_density():
    df = _build_testing_df()
    gg = ggplot(aes(x="x", color="c"), data=df)
    print(gg + geom_density() + xlab("x label") + ylab("y label"))

@image_comparison(baseline_images=['geom_hist', 'geom_hist_title'], extensions=["png"])
def test_geom_histogram():
    df = _build_testing_df()
    gg = ggplot(aes(x="x", y="y", shape="cat2", color="cat"), data=df)
    print(gg + geom_histogram())
    print(gg + geom_histogram() + ggtitle("My Histogram"))
    
@image_comparison(baseline_images=['geom_point', 'geom_point_vline'], extensions=["png"])
def test_geom_point():
    df = _build_testing_df()
    gg = ggplot(aes(x="x", y="y", shape="cat2", color="cat"), data=df)
    print(gg + geom_point())
    print(gg + geom_point() + geom_vline(x=50, ymin=-10, ymax=10))
    
@image_comparison(baseline_images=[ 'geom_area'], extensions=["png"])
def test_geom_area():
    df = _build_testing_df()
    gg = ggplot(aes(x='x', ymax='y', ymin='z', color="cat2"), data=df)
    print(gg + geom_area())

@image_comparison(baseline_images=['geom_text'], extensions=["png"])
def test_geom_text():
    print(ggplot(aes(x='wt',y='mpg',label='name'),data=mtcars) + geom_text())
    

@image_comparison(baseline_images=['factor_geom_line' ], extensions=["png"])
def test_geom_line():
    p = ggplot(mtcars, aes(x='wt', y='mpg', colour='factor(cyl)', size='mpg', linetype='factor(cyl)'))
    print(p + geom_line())
    
@image_comparison(baseline_images=['factor_geom_point' ], extensions=["png"])
def test_factor_geom_point():
    p = ggplot(mtcars, aes(x='wt', y='mpg', colour='factor(cyl)', size='mpg', linetype='factor(cyl)'))
    print(p + geom_point())
    
@image_comparison(baseline_images=['factor_geom_point_line'], extensions=["png"])
def test_factor_geom_point_line():
    p = ggplot(mtcars, aes(x='wt', y='mpg', colour='factor(cyl)', size='mpg', linetype='factor(cyl)'))
    print(p + geom_line() + geom_point())
    
@image_comparison(baseline_images=['factor_complicated' ], extensions=["png"])
def test_factor_point_line_title_lab():
    p = ggplot(mtcars, aes(x='wt', y='mpg', colour='factor(cyl)', size='mpg', linetype='factor(cyl)'))
    print(p + geom_point() + geom_line(color='lightblue') + ggtitle("Beef: It's What's for Dinner") + xlab("Date") + ylab("Head of Cattle Slaughtered"))
  
@image_comparison(baseline_images=['factor_geom_bar' ], extensions=["png"])
def test_factor_bar():
    p = ggplot(aes(x='factor(cyl)'), data=mtcars)
    print(p + geom_bar())
    
@image_comparison(baseline_images=['stat_smooth'], extensions=["png"])
def test_stats_smooth():
    df = _build_testing_df()
    gg = ggplot(aes(x="x", y="y", shape="cat2", color="cat"), data=df)
    print(gg + stat_smooth(color="blue") + ggtitle("My Smoothed Chart"))
    
@image_comparison(baseline_images=['stat_bin2d'], extensions=["png"])
def test_stats_bin2d():
    df = _build_testing_df()
    gg = ggplot(aes(x='x', y='y', shape='cat', color='cat2'), data=df)
    print(gg + stat_bin2d())
    
@image_comparison(baseline_images=[ 'geom_density_alpha' ], extensions=["png"])
def test_alpha_density():
    df = _build_testing_df()
    gg = ggplot(aes(x='mpg', fill=True, alpha=0.3), data=mtcars)
    print(gg + geom_density())

@image_comparison(baseline_images=['geom_bar_facet', 'geom_area_facet' ], extensions=["png"])   
def test_facet_wrap():
    df = _build_testing_df()
    gg = ggplot(aes(x='x', ymax='y', ymin='z'), data=df)
    print(gg + geom_bar() + facet_wrap(x="cat2"))
    print(gg + geom_area() + facet_wrap(x="cat2"))

@image_comparison(baseline_images=['geom_density_facet', 'geom_line_facet' ], extensions=["png"])   
def test_facet_wrap2():
    meat = _build_meat_df()
    meat_lng = pd.melt(meat, id_vars=['date'])
    p = ggplot(aes(x='date', y='value', colour='variable', fill=True, alpha=0.3), data=meat_lng)
    print(p + geom_density() + facet_wrap("variable"))
    print(p + geom_line() + facet_wrap("variable"))

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
    #print(p + geom_point() + facet_grid(y="variable", x=))
    # Todo: real testcase for facet_grid

@image_comparison(baseline_images=['diamonds_big', 'diamonds_facet' ], extensions=["png"])  
def test_facet_grid():
    # only use a small subset of the data to speedup tests
    # N=53940 -> N=7916 and only 2x2 facets
    _mask1 = (diamonds.cut == "Ideal") | (diamonds.cut == "Good")
    _mask2 = (diamonds.clarity == "SI2") | (diamonds.clarity == "VS1")
    _df = diamonds[_mask1 & _mask2]
    p = ggplot(aes(x='x', y='y', colour='z'), data=_df)
    p = p + geom_point() + scale_colour_gradient(low="white", high="red") 
    p = p + facet_grid("cut", "clarity")
    print(p)   
    p = ggplot(aes(x='carat'), data=_df)
    print(p + geom_density() + facet_grid("cut", "clarity"))    

@image_comparison(baseline_images=['point_smooth_se', 'smooth_se'], extensions=["png"])   
def test_smooth_se():
    meat = _build_meat_df()
    p = ggplot(aes(x='date', y='beef'), data=meat)
    print(p + geom_point() + stat_smooth(se=True))
    print(p + stat_smooth(se=True))
    
@image_comparison(baseline_images=['scale1'], extensions=["png"])   
def test_scale_xy_continous():
    meat = _build_meat_df()
    p = ggplot(aes(x='date', y='beef'), data=meat)
    print(p + geom_point() + scale_x_continuous("This is the X") + scale_y_continuous("Squared", limits=[0, 1500]))
    
@image_comparison(baseline_images=['ylim'], extensions=["png"])   
def test_ylim():
    meat = _build_meat_df()
    p = ggplot(aes(x='date', y='beef'), data=meat)
    print(p + geom_point() + ylim(0, 1500))
    
@image_comparison(baseline_images=['scale_date'], extensions=["png"])   
def test_scale_date():
    meat = _build_meat_df()
    gg = ggplot(aes(x='date', y='beef'), data=meat) + geom_line() 
    print(gg+scale_x_date(labels="%Y-%m-%d"))

@image_comparison(baseline_images=['diamonds_small'], extensions=["png"])   
def test_diamond():    
    p = ggplot(aes(x='x', y='y', colour='z'), data=diamonds.head(4))
    p = p + geom_point() + scale_colour_gradient(low="white", high="red") 
    p = p + facet_wrap("cut")
    print(p)

def test_aes_positional_args():
    result = aes("weight", "hp")
    expected = {"x": "weight", "y": "hp"}
    assert_equal(result,expected)

    result3 = aes("weight", "hp", "qsec")
    expected3 =  {"x": "weight", "y": "hp", "color": "qsec"}
    assert_equal(result3,expected3)


def test_aes_keyword_args():
    result = aes(x="weight", y="hp")
    expected = {"x": "weight", "y": "hp"}
    assert_equal(result,expected)

    result3 = aes(x="weight", y="hp", color="qsec")
    expected3 =  {"x": "weight", "y": "hp", "color": "qsec"}
    assert_equal(result3,expected3)


def test_aes_mixed_args():
    result = aes("weight", "hp", color="qsec")
    expected = {"x": "weight", "y": "hp", "color": "qsec"}
    assert_equal(result,expected)
