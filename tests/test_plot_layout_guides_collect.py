"""
Tests for `plot_layout(guides=...)` and cross-plot guide collection
"""

import pandas as pd

from plotnine import (
    aes,
    geom_line,
    geom_point,
    geom_tile,
    theme,
)
from plotnine._utils.yippie import geom as g
from plotnine._utils.yippie import plot
from plotnine.composition import guide_area, plot_layout


def test_no_collect():
    # No plot_layout(guides=...) — each leaf draws its own legend
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p = p1 | p2
    assert p == "no_collect"


def test_collect_canonical():
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p = (p1 | p2) + plot_layout(guides="collect")
    assert p == "collect_canonical"


def test_collect_bottom():
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p = (p1 | p2) + plot_layout(guides="collect") & theme(
        legend_position="bottom"
    )
    assert p == "collect_bottom"


def test_collect_distinct_legends():
    # Two plots with different color limits → two separate legends
    df1 = pd.DataFrame({"x": [0, 1], "y": [0, 1], "c": ["a", "b"]})
    df2 = pd.DataFrame({"x": [0, 1], "y": [0, 1], "c": ["x", "y"]})
    p1 = plot.red + geom_point(aes("x", "y", color="c"), df1)
    p2 = plot.green + geom_point(aes("x", "y", color="c"), df2)
    p = (p1 | p2) + plot_layout(guides="collect")
    assert p == "collect_distinct_legends"


def test_collect_glyph_union():
    # Two plots with the same color scale but different geoms;
    # collected keys should overlay both glyph shapes.
    df = pd.DataFrame(
        {
            "cat": ["a", "b", "c", "d"],
            "cat2": ["r", "r", "s", "s"],
            "value": [1, 2, 3, 4],
        }
    )
    p1 = plot.red + geom_point(aes("cat", "value", color="cat2"), df, size=4)
    p2 = plot.green + geom_line(
        aes("cat", "value", color="cat2", group="cat2"), df
    )
    p = (p1 | p2) + plot_layout(guides="collect")
    assert p == "collect_glyph_union"


def test_keep_blocks_outer_collect():
    # Inner says "keep", outer says "collect" — only p3 is collected
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p3 = plot.blue + g.points
    inner = (p1 | p2) + plot_layout(guides="keep")
    p = (inner / p3) + plot_layout(guides="collect")
    assert p == "keep_blocks_outer_collect"


def test_nested_collect():
    # Both inner and outer say "collect" — inner collects p1/p2 to
    # itself, outer collects p3 separately.
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p3 = plot.blue + g.points
    inner = (p1 | p2) + plot_layout(guides="collect")
    p = (inner / p3) + plot_layout(guides="collect")
    assert p == "nested_collect"


def test_inside_legend_stays_with_plot():
    # A leaf positioned to render its legend inside the panel area
    # should NOT participate in collection — its inside legend
    # remains beside its own plot.
    p1 = (
        plot.red
        + g.points
        + theme(
            legend_position="inside",
            legend_position_inside=(0.85, 0.85),
        )
    )
    p2 = plot.green + g.points
    p = (p1 | p2) + plot_layout(guides="collect")
    assert p == "inside_legend_stays_with_plot"


def test_collect_colorbar():
    # Two plots with the same continuous color scale → one colorbar
    df = pd.DataFrame(
        {
            "cat": ["a", "b", "c", "d"],
            "cat2": ["r", "r", "s", "s"],
            "value": [1, 2, 3, 4],
        }
    )
    p1 = plot.red + geom_tile(aes("cat", "cat2", fill="value"), df)
    p2 = plot.green + geom_tile(aes("cat", "cat2", fill="value"), df)
    p = (p1 | p2) + plot_layout(guides="collect")
    assert p == "collect_colorbar"


def test_guide_area_without_collect():
    # No `guides="collect"` — the guide_area cell renders blank,
    # leaves keep their own legends.
    p1 = plot.red + g.points
    p2 = plot.green + g.points
    p = p1 | p2 | guide_area()
    assert p == "guide_area_without_collect"


def test_collect_into_guide_area():
    # Collected legend lands inside the guide_area cell instead of
    # the composition's side-space.
    p1 = plot.red + g.points
    p2 = plot.green + g.areas
    p = (p1 | p2 | guide_area()) + plot_layout(guides="collect")
    assert p == "collect_into_guide_area"


def test_collect_into_guide_area_and_merge():
    # Collected legend lands inside the guide_area cell instead of
    # the composition's side-space. Since the legends have the same keys,
    # they are merged.
    p1 = plot.red + g.points
    p2 = plot.green + g.cols
    p = (p1 | p2 | guide_area()) + plot_layout(guides="collect")
    assert p == "collect_into_guide_area_and_merge"


def test_multiple_guide_areas_extras_are_blank():
    # First (depth-first) guide_area wins; subsequent ones render
    # as blank cells.
    p1 = plot.red + g.points
    p2 = plot.green + g.cols
    p = (p1 | guide_area() | p2 | guide_area()) + plot_layout(guides="collect")
    assert p == "multiple_guide_areas_extras_are_blank"


def test_inner_guide_area_not_used_by_outer_collect():
    # `guide_area` is only honoured when it is a direct child of
    # the collecting composition. A guide_area placed inside a
    # sub-composition belongs to that sub-grid, so the outer
    # collector cannot reach it and falls back to side placement;
    # the inner guide_area renders blank.
    p1 = plot.red + g.points
    p2 = plot.green + g.cols
    p3 = plot.blue + g.areas
    inner = p2 | guide_area()
    p = (p1 / inner / p3) + plot_layout(guides="collect")
    assert p == "inner_guide_area_not_used_by_outer_collect"


def test_nested_collect_guide_area():
    # Inner-collect with inner guide_area hosts inner's legend.
    # Outer-collect has no eligible host (inner claims the only
    # guide_area) and falls back to side placement.
    p1 = plot.red + g.points
    p2 = plot.green + g.cols
    p3 = plot.blue + g.points
    inner = (p1 | p2 | guide_area()) + plot_layout(guides="collect")
    p = (inner / p3) + plot_layout(guides="collect")
    assert p == "nested_collect_guide_area"
