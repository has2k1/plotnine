from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import get_assert_same_ggplot, cleanup, assert_same_elements
assert_same_ggplot = get_assert_same_ggplot(__file__)


from nose.tools import (assert_true, assert_raises, assert_is, assert_is_not, assert_equal)

from ggplot import *

import six
import pandas as pd


def test_data_transforms():
    import numpy as np
    p = ggplot(aes(x="np.log(price)"), data=diamonds)
    with assert_raises(Exception):
        #no numpy available
        p = ggplot(aes(x="ap.log(price)"), data=diamonds)


def test_no_data_leak():
    cols_before = diamonds.columns.copy()
    import numpy as np
    p = ggplot(aes(x="np.log(price)"), data=diamonds)
    cols_after = diamonds.columns.copy()
    assert_same_elements(cols_before, cols_after)
    assert_is_not(diamonds, p.data)

def test_geom_with_data():
    gg = ggplot(mtcars, aes("wt", "mpg")) + geom_point()
    cols_before = gg.data.columns.copy()
    _text = geom_text(aes(label="name"), data=mtcars[mtcars.cyl == 6])
    g2 = gg + _text
    # Datasets are shared between ggplot objects but it is not allowed to change the columns in a
    # dataset after the initial ggplot(aes) call.
    assert_is_not(g2.data, mtcars, "Adding a dataset to a geom changed the data in ggplot")
    assert_same_elements(cols_before, g2.data.columns)


def test_deepcopy():
    from copy import deepcopy
    p = ggplot(aes(x="price"), data=diamonds) + geom_histogram()
    p2 = deepcopy(p)
    assert_is_not(p, p2)
    # Not sure what we have to do for that...
    #assert_equal(p, p2)
    assert_is(p.data, p2.data)
    assert_equal(len(p.geoms), len(p2.geoms))
    assert_is_not(p.geoms[0], p2.geoms[0])
    assert_equal(len(p.aesthetics), len(p2.aesthetics))
    assert_is_not(p.aesthetics, p2.aesthetics)
    assert_is(p.aesthetics.__eval_env__, p2.aesthetics.__eval_env__)


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
    new_df, _ = assign_visual_mapping(df,aes(x="x", y="y", shape="a", color="b"), gg)
    data = gg._make_plot_data(new_df)
    assert_true("shape" in data, "no shape was assigned")
    assert_true(data["shape"][0] != data["shape"][1], "wrong marker was assigned")
    # And now a visual test that both shapes are there. Make them big so that the test is failing
    # if something is wrong
    gg = ggplot(aes(x="x", y="y", shape="a", color="b"), data=df)
    assert_same_ggplot(gg + geom_point(size=3000), "geom_point_marker")

