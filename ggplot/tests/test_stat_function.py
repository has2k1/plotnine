from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nose.tools import assert_true, assert_raises
from ggplot.tests import image_comparison, cleanup

from ggplot import *

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats


@image_comparison(baseline_images=['fun_dnorm', 'fun_sin_vs_cos',
                                   'fun_args', 'fun_dict_args'])
def test_stat_function():
    np.random.seed(7776)

    def dnorm(x):
        return (1.0 / np.sqrt(2 * np.pi)) * (np.e ** (-.5 * (x ** 2)))
    df = pd.DataFrame({'x': np.random.normal(size=100)})
    gg = ggplot(df, aes(x='x'))
    gg = gg + geom_density() + stat_function(fun=dnorm, n=200)
    print(gg)

    df = pd.DataFrame({'x': np.arange(10)})
    gg = ggplot(df, aes(x='x'))
    gg = gg + stat_function(fun=np.sin, color='red')
    gg = gg + stat_function(fun=np.cos, color='blue')
    print(gg)

    # Test when args = list
    def to_the_power_of(n, p):
        return n ** p
    x = np.random.randn(100)
    y = x ** 3
    y += np.random.randn(100)
    data = pd.DataFrame({'x': x, 'y': y})
    gg = ggplot(aes(x='x', y='y'), data) + geom_point()
    gg = gg + stat_function(fun=to_the_power_of, args=[3])
    print(gg)

    # Test when args = dict
    def dnorm(x, mean, var):
        return scipy.stats.norm(mean, var).pdf(x)
    data = pd.DataFrame({'x': np.arange(-5, 6)})
    gg = ggplot(aes(x='x'), data=data)
    gg = gg + stat_function(fun=dnorm, color='blue',
                            args={'mean': 0.0, 'var': 0.2})
    gg = gg + stat_function(fun=dnorm, color='red',
                            args={'mean': 0.0, 'var': 1.0})
    gg = gg + stat_function(fun=dnorm, color='yellow',
                            args={'mean': 0.0, 'var': 5.0})
    gg = gg + stat_function(fun=dnorm, color='green',
                            args={'mean': -2.0, 'var': 0.5})
    print(gg)


@cleanup
def test_stat_function_exception():
    with assert_raises(Exception):
        # 'fun' is a required aes
        print(ggplot(aes(x='price'), data=diamonds) + stat_function())
