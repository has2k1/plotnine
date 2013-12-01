from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.testing.decorators import image_comparison
from nose.tools import assert_true

from ggplot import *

import matplotlib.pyplot as plt

@image_comparison(baseline_images=["free", "free_x", "free_y", "none"], extensions=["png"])
def test_scale_facet_wrap():
    def convertText(t):
        """Return a float for the text value of a matplotlib Text object."""
        return float(t.get_text())

    def empty(t):
        """Return True if the Text object is an empty string."""
        return len(t.get_text().strip()) == 0

    p = ggplot(aes(x="price"), data=diamonds) + geom_histogram()

    print(p + facet_wrap("cut", scales="free"))

    # FIXME: n_high is the number of columns, not rows, because n_high and
    # n_wide are being passed backwards to plt.subplot in ggplot.py
    columns = p.n_high

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
            assert_true(all(map(convertText, ax.get_yticklabels()) == yticks))
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
            assert_true(all(map(convertText, ax.get_xticklabels()) == xticks))

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
            assert_true(all(map(convertText, ax.get_xticklabels()) == xticks))

        if pos % columns == 0:
            assert_true(all(map(convertText, ax.get_yticklabels()) == yticks))
        else:
            assert_true(all(map(empty, ax.get_yticklabels())))
