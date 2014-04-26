from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from nose.tools import (assert_equal, assert_is, assert_is_not,
                        assert_raises)
import pandas as pd

from ggplot import *
from ggplot.utils.exceptions import GgplotError
from . import cleanup


@cleanup
def test_stat_bin():
    # stat_bin needs the 'x' aesthetic to be numeric or a categorical
    # and should complain if given anything else
    class unknown(object):
        pass
    x = [unknown()] * 3
    y = [1, 2, 3]
    df = pd.DataFrame({'x': x, 'y': y})
    gg = ggplot(aes(x='x', y='y'), df)
    with assert_raises(GgplotError):
        print(gg + stat_bin())


@cleanup
def test_stat_abline():
    # slope and intercept function should return values
    # of the same length
    def fn_xy(x, y):
        return [1, 2]
    def fn_xy2(x, y):
        return [1, 2, 3]

    gg = ggplot(aes(x='wt', y='mpg'), mtcars)

    # same length, no problem
    print(gg + stat_abline(slope=fn_xy, intercept=fn_xy))
    with assert_raises(GgplotError):
        print(gg + stat_abline(slope=fn_xy, intercept=fn_xy2))


@cleanup
def test_stat_vhabline_functions():
    def fn_x(x):
        return 1
    def fn_y(y):
        return 1
    def fn_xy(x, y):
        return 1

    gg = ggplot(aes(x='wt'), mtcars)
    # needs y aesthetic
    with assert_raises(GgplotError):
        print(gg + stat_abline(slope=fn_xy))
    # needs y aesthetic
    with assert_raises(GgplotError):
        print(gg + stat_abline(intercept=fn_xy))

    gg = ggplot(aes(x='wt', y='mpg'), mtcars)
    # Functions with 2 args, no problem
    print(gg + stat_abline(slope=fn_xy, intercept=fn_xy))

    # slope function should take 2 args
    with assert_raises(GgplotError):
        print(gg + stat_abline(slope=fn_x, intercept=fn_xy))

    # intercept function should take 2 args
    with assert_raises(GgplotError):
        print(gg + stat_abline(slope=fn_xy, intercept=fn_y))

    # intercept function should take 1 arg
    with assert_raises(GgplotError):
        print(gg + stat_vline(xintercept=fn_xy))

    # intercept function should take 1 arg
    with assert_raises(GgplotError):
        print(gg + stat_hline(yintercept=fn_xy))
