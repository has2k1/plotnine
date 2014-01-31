from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import get_assert_same_ggplot, cleanup
assert_same_ggplot = get_assert_same_ggplot(__file__)


from nose.tools import assert_true, assert_raises

from ggplot import *

from ggplot.utils import six
import pandas as pd

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
def test_axis_changes_applied_to_all_axis_visual():
    # see https://github.com/yhat/ggplot/issues/147
    # http://stackoverflow.com/questions/20807212/in-ggplot-for-python-specify-global-xlim-in-facet-wrap
    p = ggplot(aes(x="price"), data=diamonds) + geom_histogram()
    p = p + facet_wrap("cut", scales="free_y")
    assert_same_ggplot(p + xlim(-10,5100) + xlab(u"test"), "axis_changes_to_all")

@cleanup
def test_different_markers():
    from ggplot.components import assign_visual_mapping
    from ggplot.components.shapes import shape_gen
    # First the generator which assigns the shapes
    shape = shape_gen()
    assert_true(six.next(shape) != six.next(shape), "Subsequent shapes are not different!")
    shape = shape_gen()
    assert_true(six.next(shape) == 'o', "First shape is not 'o'")
    assert_true(six.next(shape) == '^', "Second shape is not '^'")
    # Do shapes show up in the transformed layer?
    df = pd.DataFrame({"x":[1,2],"y":[1,2], "a":["a","b"], "b":["c","d"]})
    gg = ggplot(aes(x="x", y="y", shape="a", color="b"), data=df)
    new_df = assign_visual_mapping(df,aes(x="x", y="y", shape="a", color="b"), gg)
    layer = gg._get_layers(new_df)
    assert_true("shape" in layer[0], "no shape was assigned")
    assert_true(layer[0]["shape"] != layer[1]["shape"], "wrong marker was assigned")
    # And now a visual test that both shapes are there. Make them big so that the test is failing
    # if something is wrong
    gg = ggplot(aes(x="x", y="y", shape="a", color="b"), data=df)
    assert_same_ggplot(gg + geom_point(size=3000), "geom_point_marker")


