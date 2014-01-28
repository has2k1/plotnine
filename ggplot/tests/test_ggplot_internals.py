from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import get_assert_same_ggplot, cleanup
assert_same_ggplot = get_assert_same_ggplot(__file__)

from nose.tools import assert_true, assert_raises

from ggplot import *

import matplotlib.pyplot as plt

@cleanup            
def test_axis_changes_applied_to_all_axis():
    # see https://github.com/yhat/ggplot/issues/147
    # http://stackoverflow.com/questions/20807212/in-ggplot-for-python-specify-global-xlim-in-facet-wrap
    p = ggplot(aes(x="price"), data=diamonds) + geom_histogram()
    p = p + facet_wrap("cut", scales="free_y")
    fig = (p + xlim(0,1500)).draw()
    for ax in fig.axes:
        assert_true(ax.get_xlim() == (0,1500))
    fig = (p + xlab(u"test")).draw()
    for ax in fig.axes:
        assert_true(ax.get_xlabel() == u"test")

@cleanup
def test_axis_changes_applied_to_all_axis():
    # see https://github.com/yhat/ggplot/issues/147
    # http://stackoverflow.com/questions/20807212/in-ggplot-for-python-specify-global-xlim-in-facet-wrap
    p = ggplot(aes(x="price"), data=diamonds) + geom_histogram()
    p = p + facet_wrap("cut", scales="free_y")
    assert_same_ggplot(p + xlim(-10,5100) + xlab(u"test"), "axis_changes_to_all")