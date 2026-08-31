"""
Visual tests for composition axis and title collection
"""

from plotnine import (
    dup_axis,
    facet_wrap,
    labs,
    scale_x_discrete,
    scale_y_continuous,
)
from plotnine._utils.yippie import geom as g
from plotnine._utils.yippie import plot
from plotnine.composition import plot_layout


def test_collect_axes_across_row():
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p3 = plot.blue + g.points
    p = (p1 | p2 | p3) + plot_layout(axes="collect")
    assert p == "collect_row"


def test_collect_axes_down_column():
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p3 = plot.blue + g.points
    p = (p1 / p2 / p3) + plot_layout(axes="collect")
    assert p == "collect_column"


def test_collect_axes_across_grid():
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p3 = plot.blue + g.points
    p4 = plot.yellow + g.points
    p = (p1 + p2 + p3 + p4) + plot_layout(ncol=2, axes="collect")
    assert p == "collect_grid"


def test_collect_only_x_axes():
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p3 = plot.blue + g.points
    p4 = plot.yellow + g.points
    p = (p1 + p2 + p3 + p4) + plot_layout(ncol=2, axes="collect_x")
    assert p == "collect_x_only"


def test_collect_only_y_axes():
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p3 = plot.blue + g.points
    p4 = plot.yellow + g.points
    p = (p1 + p2 + p3 + p4) + plot_layout(ncol=2, axes="collect_y")
    assert p == "collect_y_only"


def test_collect_axes_across_design_gap():
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p3 = plot.blue + g.points
    design = """
        AB
        C#
    """
    p = (p1 | p2 | p3) + plot_layout(design=design, axes="collect")
    assert p == "collect_over_a_design_gap"


def test_collect_titles_without_axes():
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p = (p1 | p2) + plot_layout(axes="keep", axis_title="collect")
    assert p == "collect_titles_only"


def test_collect_axes_but_keep_each_title():
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p = (p1 | p2) + plot_layout(axes="collect", axis_title="keep")
    assert p == "collect_axes_keeping_titles"


def test_leave_differing_titles_uncollected():
    p1 = plot.red + g.points + labs(x="Category")
    p2 = plot.green + g.points
    p = (p1 | p2) + plot_layout(axes="collect")
    assert p == "collect_with_differing_titles"


def test_collect_top_axes():
    p1 = plot.red + g.points + scale_x_discrete(position="top")
    p2 = plot.green + g.points + scale_x_discrete(position="top")
    p = (p1 / p2) + plot_layout(axes="collect")
    assert p == "collect_axis_on_the_top"


def test_collect_primary_and_secondary_axes():
    p1 = plot.red + g.points + scale_y_continuous(sec_axis=dup_axis())
    p2 = plot.green + g.points + scale_y_continuous(sec_axis=dup_axis())
    p = (p1 | p2) + plot_layout(axes="collect")
    assert p == "collect_secondary_axis"


def test_collect_axes_with_facetted_plot():
    p1 = plot.red + g.points + facet_wrap("cat2")
    p2 = plot.green + g.points
    p = (p1 | p2) + plot_layout(axes="collect")
    assert p == "collect_with_a_facetted_plot"


def test_outer_collection_skips_nested_composition():
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p3 = plot.blue + g.points
    p = (p1 | (p2 | p3)) + plot_layout(axes="collect")
    assert p == "collect_leaves_a_sub_composition_alone"


def test_collect_axes_within_nested_composition():
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p3 = plot.blue + g.points
    p = p1 | ((p2 | p3) + plot_layout(axes="collect"))
    assert p == "collect_inside_a_sub_composition"
