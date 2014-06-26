from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


from . import get_assert_same_ggplot, cleanup
assert_same_ggplot = get_assert_same_ggplot(__file__)


from ggplot import *

import pandas as pd

@cleanup
def test_demo_beef():
    gg = ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        ggtitle("Beef: It's What's for Dinner") + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")
    assert_same_ggplot(gg, 'ggplot_demo_beef')

@cleanup
def test_meat():
    meat_lng = pd.melt(meat[['date', 'beef', 'pork', 'broilers']], id_vars='date')
    gg = ggplot(aes(x='date', y='value', colour='variable'), data=meat_lng) + \
        geom_point() + \
        stat_smooth(color='red', se=False)
    assert_same_ggplot(gg, 'ggplot_meat')

@cleanup
def test_diamonds_geom_point_alpha():
    gg = ggplot(diamonds, aes('carat', 'price')) + \
        geom_point(alpha=1/20.) + \
        ylim(0, 20000)
    assert_same_ggplot(gg, 'diamonds_geom_point_alpha')

@cleanup
def test_diamonds_carat_hist():
    gg = ggplot(aes(x='carat'), data=diamonds)
    gg = gg + geom_histogram() + ggtitle("Histogram of Diamond Carats") + labs("Carats", "Freq")
    assert_same_ggplot(gg, 'diamonds_carat_hist')

@cleanup
def test_geom_density_example():
    gg = ggplot(diamonds, aes(x='price', color='cut')) + \
        geom_density()
    assert_same_ggplot(gg, 'geom_density_example')

@cleanup
def test_density_with_fill():
    meat_lng = pd.melt(meat[['date', 'beef', 'broilers', 'pork']], id_vars=['date'])
    gg = ggplot(aes(x='value', colour='variable'), data=meat_lng)
    gg = gg + geom_density(fill=True, alpha=0.3)
    assert_same_ggplot(gg, 'density_with_fill')

@cleanup
def test_mtcars_geom_bar_cyl():
    meat_lng = pd.melt(meat[['date', 'beef', 'broilers', 'pork']], id_vars=['date'])
    gg = ggplot(mtcars, aes('factor(cyl)'))
    gg = gg + geom_histogram()
    assert_same_ggplot(gg, 'mtcars_geom_bar_cyl')
