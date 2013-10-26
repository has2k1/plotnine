from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
from six.moves import xrange

from nose.tools import assert_equal, assert_true, assert_raises
from matplotlib.testing.decorators import image_comparison, cleanup

import numpy as np
import pandas as DataFrame

from ggplot import *


@image_comparison(baseline_images=['ggplot_demo_beef'], extensions=['png'])
def test_demo_beef():
    gg = ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        ggtitle("Beef: It's What's for Dinner") + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")
    print(gg)
    
@image_comparison(baseline_images=['ggplot_meat'], extensions=['png'])
def test_meat():
    meat_lng = pd.melt(meat[['date', 'beef', 'pork', 'broilers']], id_vars='date')
    gg = ggplot(aes(x='date', y='value', colour='variable'), data=meat_lng) + \
        geom_point() + \
        stat_smooth(color='red')
    print(gg)
    
@image_comparison(baseline_images=['diamonds_geom_point_alpha'], extensions=['png'])
def test_diamonds_geom_point_alpha():
    gg = ggplot(diamonds, aes('carat', 'price')) + \
        geom_point(alpha=1/20.) + \
        ylim(0, 20000)
    print(gg)
    
@image_comparison(baseline_images=['diamonds_carat_hist'], extensions=['png'])
def test_diamonds_carat_hist():
    gg = ggplot(aes(x='carat'), data=diamonds)
    gg = gg + geom_histogram() + ggtitle("Histogram of Diamond Carats") + labs("Carats", "Freq") 
    print(gg)
    
@image_comparison(baseline_images=['geom_density_example'], extensions=['png'])
def test_geom_density_example():
    gg = ggplot(diamonds, aes(x='price', color='cut')) + \
        geom_density() 
    print(gg)

@image_comparison(baseline_images=['density_with_fill'], extensions=['png'])
def test_density_with_fill():
    meat_lng = pd.melt(meat[['date', 'beef', 'broilers', 'pork']], id_vars=['date'])
    gg = ggplot(aes(x='value', colour='variable', fill=True, alpha=0.3), data=meat_lng)
    gg = gg + geom_density()
    print(gg)

@image_comparison(baseline_images=['mtcars_geom_bar_cyl'], extensions=['png'])
def test_mtcars_geom_bar_cyl():
    meat_lng = pd.melt(meat[['date', 'beef', 'broilers', 'pork']], id_vars=['date'])
    gg = ggplot(mtcars, aes('factor(cyl)'))
    gg = gg + geom_bar()
    print(gg)