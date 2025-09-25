import pytest

from plotnine import (
    element_text,
    facet_grid,
    facet_wrap,
    labs,
    theme,
    theme_gray,
)
from plotnine._utils.yippie import geom as g
from plotnine._utils.yippie import legend, plot, rotate, tag
from plotnine.composition._plot_layout import plot_layout


def test_basic_horizontal_align_resize():
    p1 = plot.red + rotate.axis_title_x + rotate.axis_title_y
    p2 = plot.green + rotate.plot_title
    p = p1 | p2
    assert p == "basic_horizontal_align_resize"


def test_basic_vertical_align_resize():
    p1 = plot.red + rotate.axis_title_y
    p2 = plot.green + rotate.axis_title_x + rotate.plot_title
    p = p1 / p2
    assert p == "basic_vertical_align_resize"


def test_nested_horizontal_align_1():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue + g.cols
    p = p1 | (p2 | p3)
    assert p == "test_nested_horizontal_align_1"


def test_nested_horizontal_align_2():
    p1 = plot.red + g.points
    p2 = plot.green
    p3 = plot.blue
    p = p1 | (p2 | p3)
    assert p == "test_nested_horizontal_align_2"


def test_nested_vertical_align_1():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue + g.cols
    p = p1 / (p2 / p3)
    assert p == "test_nested_vertical_align_1"


def test_nested_vertical_align_2():
    p1 = plot.red + g.points
    p2 = plot.green
    p3 = plot.blue
    p = p1 / (p2 / p3)
    assert p == "test_nested_vertical_align_2"


def test_nested_horizontal_align_resize():
    p1 = plot.red + tag("a)")
    p2 = plot.green + tag("g)")
    p3 = plot.blue + tag("b)")
    p4 = plot.yellow + tag("y)") + rotate.plot_title
    p = p1 | p2 | (p3 | p4)
    assert p == "nested_horizontal_align_resize"


def test_nested_vertical_align_resize():
    p1 = plot.red + tag("a)")
    p2 = plot.green + tag("g)")
    p3 = plot.blue + tag("b)")
    p4 = plot.yellow + tag("y)") + rotate.plot_title
    p = p1 / p2 / (p3 / p4)
    assert p == "nested_vertical_align_resize"


def test_vertical_tag_align():
    p1 = plot.red + tag("long tag a)")
    p2 = plot.green + tag("g)")
    p3 = plot.blue + tag("b)") + theme(plot_tag=element_text(ha="left"))
    p4 = (
        plot.yellow
        + tag("y)")
        + theme(plot_tag=element_text(ha="left", margin={"l": 10}))
    )
    p = p1 / p2 / p3 / p4
    assert p == "vertical_tag_align"


def test_horizontal_tag_align():
    p1 = plot.red + tag("long\ntag\na)")
    p2 = plot.green + tag("g)")
    p3 = plot.blue + tag("b)") + theme(plot_tag=element_text(va="top"))
    p4 = (
        plot.yellow
        + tag("y)")
        + theme(plot_tag=element_text(va="top", margin={"t": 10}))
    )
    p = p1 | p2 | p3 | p4
    assert p == "horizontal_tag_align"


def test_facets():
    p1 = plot.purple + g.points + facet_wrap("cat") + legend.top
    p2 = plot.brown + g.points + legend.bottom
    p3 = plot.steelblue + g.cols + facet_grid("cat ~ cat2")
    p = (p1 / p3) | p2
    assert p == "facets"


def test_complex_composition():
    p1 = plot.red
    p2 = plot.green + g.points + rotate.plot_title + legend.bottom
    p3 = plot.blue + g.cols + legend.left + tag("b)")
    p4 = plot.yellow + g.points + rotate.axis_title_y
    p5 = plot.cyan + tag("c)") + theme(plot_tag=element_text(margin={"t": 10}))
    p6 = (
        plot.orange
        + rotate.axis_title_y
        + tag("o)", "topright")
        + theme(plot_tag=element_text(va="bottom"))
    )
    p = p1 | p2 | p3 / p4 / (p5 | p6)
    assert p == "complex_composition"


def test_minus_operator():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue
    p4 = plot.brown
    p = (p1 / p2) - p3 - p4
    assert p == "minus"


def test_and_operator():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue
    p4 = plot.brown
    p = (p1 | p2 | (p3 / p4)) & theme_gray()
    assert p == "and_operator"


def test_mul_operator():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue
    p4 = plot.brown
    p = (p1 | p2 | (p3 / p4)) * theme_gray()
    assert p == "mul_operator"


def test_plus_operator():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue
    p4 = plot.brown
    p = (p1 | p2 | (p3 / p4)) + theme_gray()
    assert p == "plus_operator"


def test_plot_layout_widths():
    p1 = plot.red
    p2 = plot.green
    p = (p1 | p2) + plot_layout(widths=[1, 4])
    assert p == "plot_layout_widths"


def test_plot_layout_heights():
    p1 = plot.red
    p2 = plot.green
    p = (p1 / p2) + plot_layout(heights=[1, 4])
    assert p == "plot_layout_heights"


def test_plot_layout_nested_resize():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue
    p4 = plot.brown

    ws = plot_layout(widths=[1, 4])
    hs = plot_layout(heights=[1, 3])

    p = (((p1 | p2) + ws) / ((p3 | p4) + ws)) + hs
    assert p == "plot_layout_nested_resize"


def test_plot_layout_extra_cols():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue
    p = (p1 | p2 | p3) + plot_layout(ncol=5)
    assert p == "plot_layout_extra_cols"


def test_plot_layout_extra_col_width():
    # An extra column is extactly panel_width wide (no margin)
    # By stacking two rows, where one has an extra column, we can
    # confirm the size.
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue
    p4 = plot.yellow + labs(y="") + theme(plot_margin=0)

    c1 = (p1 | p2 | p3) + plot_layout(ncol=4)
    c2 = p1 | p2 | p3 | p4
    p = c1 / c2
    assert p == "plot_layout_extra_col_width"


def test_plot_layout_extra_rows():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue
    p = (p1 / p2 / p3) + plot_layout(nrow=5)
    assert p == "plot_layout_extra_rows"


def test_plot_layout_extra_row_width():
    # An extra row is extactly panel_width wide (no margin)
    # By stacking two rows, where one has an extra row, we can
    # confirm the size.
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue
    p4 = plot.yellow + labs(x="", title="") + theme(plot_margin=0)

    c1 = (p1 / p2 / p3) + plot_layout(nrow=4)
    c2 = p1 / p2 / p3 / p4
    p = c1 | c2
    assert p == "plot_layout_extra_row_width"


def test_wrap_complicated():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue + g.points
    p4 = plot.yellow
    p5 = plot.cyan
    p6 = plot.orange
    p7 = plot.purple + g.cols

    c1 = (p1 + p2 + p3) + plot_layout(ncol=2)
    c2 = (p4 + p5 + p6 + p7) + plot_layout(ncol=4, widths=[1, 2, 4, 8])

    # The top composition has two rows and the bottom one has one.
    # With [1, 2] height ratios, the panels in each row should have
    # the same height.
    p = (c1 / c2) + plot_layout(heights=[2, 1])
    assert p == "wrap_complicated"


def test_plot_layout_association():
    # A plot or composition added to a composition becomes part of that
    # composition and its layout.
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue
    p4 = plot.yellow
    p5 = plot.cyan

    # Test that the layout of c1 is the layout of c1 + c2
    c1 = (p1 + p2 + p3) + plot_layout(nrow=2, widths=(1, 2))
    c2 = (p4 + p5) + plot_layout(widths=(2, 1))
    p = c1 + c2
    assert p == "plot_layout_association"

    c1 = p1 + p2 + p3
    c2 = (p4 + p5) + plot_layout(widths=(2, 1))
    p = (c1 + c2) + plot_layout(nrow=2, widths=(1, 2))
    assert p == "plot_layout_association"


def test_add_into_beside():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue

    p = (p1 | p2) + p3
    assert p == "add_into_ncol"


def test_add_into_stack():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue

    p = (p1 / p2) + p3
    assert p == "add_into_stack"


def test_add_into_beside_error():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue

    c1 = (p1 | p2) + plot_layout(ncol=2)

    with pytest.raises(ValueError) as ve:
        (c1 + p3).draw()

    assert "more items than the layout columns" in str(ve.value)


def test_add_into_stack_error():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue

    c1 = (p1 / p2) + plot_layout(nrow=2)

    with pytest.raises(ValueError) as ve:
        (c1 + p3).draw()

    assert "more items than the layout rows" in str(ve.value)


def test_plot_layout_byrow():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue
    p4 = plot.yellow

    p = (p1 + p2 + p3 + p4) + plot_layout(nrow=3, byrow=False)
    assert p == "plot_layout_byrow"
