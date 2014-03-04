from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import cleanup, get_assert_same_ggplot
assert_same_ggplot = get_assert_same_ggplot(__file__)

from nose.tools import assert_true, assert_raises

from ggplot import *

import matplotlib.pyplot as plt

@cleanup
def test_scale_facet_wrap_visual():
    p = ggplot(aes(x="price"), data=diamonds) + geom_histogram()
    assert_same_ggplot(p + facet_wrap("cut", scales="free"), "free")
    assert_same_ggplot(p + facet_wrap("cut", scales="free_x"), "free_x")
    assert_same_ggplot(p + facet_wrap("cut", scales="free_y"), "free_y")
    assert_same_ggplot(p + facet_wrap("cut", scales=None), "none")

def test_scale_facet_wrap_exception():
    with assert_raises(Exception):
        # need at least one variable
        facet_wrap()

def test_add_scale_returns_new_ggplot_object():
    # an older implementation set values on the original ggplot object and only made a deepcopy on the last step.
    # Actually all geoms/... should have such a test...
    p = ggplot(aes(x="price"), data=diamonds) + geom_histogram()
    c, r = p.n_columns, p.n_rows
    p2 = p + facet_wrap("cut", scales="free")
    cn, rn = p.n_columns, p.n_rows
    c2, r2 = p2.n_columns, p2.n_rows
    assert_true(c==cn and r==rn, "Original object changed!")
    assert_true(c!=c2 or r!=r2, "New object not changed!")

@cleanup            
def test_scale_facet_wrap_internals():
    def convertText(t):
        """Return a float for the text value of a matplotlib Text object."""
        try:
            return float(t.get_text())
        except:
            # don't mask the error, just let the assert raise the test failure
            return 0
            
    def empty(t):
        """Return True if the Text object is an empty string."""
        return len(t.get_text().strip()) == 0

    p = ggplot(aes(x="price"), data=diamonds) + geom_histogram()
    # Only p2 has the new measures for column!
    p2 = p + facet_wrap("cut", scales="free")
    print(p2)

    # FIXME: n_columns is the number of columns, not rows, because n_columns and
    # n_rows are being passed backwards to plt.subplot in ggplot.py
    columns = p2.n_columns

    fig = plt.gcf()

    # When the scales are free, every plot should have x and y labels. Don't
    # test the tick values because each plot is free to set its own.
    for ax in fig.axes:
        assert_true(len(ax.get_xticklabels()) > 0)
        assert_true(len(ax.get_yticklabels()) > 0)

    print(p + facet_wrap("cut", scales="free_x"))
    fig = plt.gcf()

    yticks = fig.axes[0].get_yticks()
    for pos, ax in enumerate(fig.axes):
        # When only the x-axis is free, all plots should have the same y scale
        assert_true(all(ax.get_yticks() == yticks))

        if pos % columns == 0:
            # Only plots in the first column should have y labels
            assert_true(all(list(map(convertText, ax.get_yticklabels())) == yticks))
        else:
            # Plots in all other columns should have no labels
            assert_true(all(map(empty, ax.get_yticklabels())))

        # Every plot should have labels on its x-axis
        assert_true(len(ax.get_xticklabels()) > 0)

    print(p + facet_wrap("cut", scales="free_y"))
    fig = plt.gcf()

    xticks = fig.axes[0].get_xticks()
    subplots = len(fig.axes)
    for pos, ax in enumerate(fig.axes):
        assert_true(all(ax.get_xticks() == xticks))

        if subplots - pos > columns:
            # Only the bottom plot of each column gets x labels. So only the
            # last N plots (where N = number of columns) get labels.
            assert_true(all(map(empty, ax.get_xticklabels())))
        else:
            assert_true(all(list(map(convertText, ax.get_xticklabels())) == xticks))

        # All plots should have y labels
        assert_true(len(ax.get_yticklabels()) > 0)

    print(p + facet_wrap("cut", scales=None))
    fig = plt.gcf()

    xticks = fig.axes[0].get_xticks()
    yticks = fig.axes[0].get_yticks()
    for pos, ax in enumerate(fig.axes):
        # Every plot should have the same x and y scales
        assert_true(all(ax.get_xticks() == xticks))
        assert_true(all(ax.get_yticks() == yticks))

        # Repeat the tests for labels from both free_x and free_y
        if subplots - pos > columns:
            assert_true(all(map(empty, ax.get_xticklabels())))
        else:
            assert_true(all(list(map(convertText, ax.get_xticklabels())) == xticks))

        if pos % columns == 0:
            assert_true(all(list(map(convertText, ax.get_yticklabels())) == yticks))
        else:
            assert_true(all(map(empty, ax.get_yticklabels())))
