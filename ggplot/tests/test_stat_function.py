from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nose.tools import assert_true, assert_raises
from ggplot.tests import image_comparison

from ggplot import *

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
from pandas import DataFrame

@image_comparison(baseline_images=["fun_dnorm","fun_sin_vs_cos","fun_args","fun_dict_args"])
def test_stat_function():
    np.random.seed(7776)
    dnorm = lambda x : (1.0 / np.sqrt(2 * np.pi)) * (np.e ** (-.5 * (x ** 2)))
    print(ggplot(DataFrame({'x':np.random.normal(size=100)}),aes(x='x')) + \
              geom_density() + \
              stat_function(fun=dnorm,n=200))
    print(ggplot(DataFrame({'x':np.arange(10)}),aes(x='x')) + \
              stat_function(fun=np.sin,color="red") + \
              stat_function(fun=np.cos,color="blue"))
    # Test when args = list
    def to_the_power_of(n,p):
        return n ** p
    x = np.random.randn(100)
    y = x ** 3
    y += np.random.randn(100)
    data = DataFrame({'x':x,'y':y})
    print(ggplot(aes(x='x',y='y'),data) + geom_point() + \
              stat_function(fun=to_the_power_of,args=[3]))
    # Test when args = dict
    def dnorm(x,mean,var):
        return scipy.stats.norm(mean,var).pdf(x)
    data = DataFrame({'x':np.arange(-5,6)})
    print(ggplot(aes(x='x'),data=data) + \
        stat_function(fun=dnorm,color="blue",args={'mean':0.0,'var':0.2})   + \
        stat_function(fun=dnorm,color="red",args={'mean':0.0,'var':1.0})    + \
        stat_function(fun=dnorm,color="yellow",args={'mean':0.0,'var':5.0}) + \
        stat_function(fun=dnorm,color="green",args={'mean':-2.0,'var':0.5}))

def test_stat_function_exception():
    with assert_raises(Exception):
        # 'fun' is a required aes
        print(ggplot(aes(x='price'),data=diamonds) + stat_function())


