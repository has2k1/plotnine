from plotnine import element_text, facet_grid, facet_wrap, theme, theme_gray
from plotnine._utils.yippie import geom as g
from plotnine._utils.yippie import legend, plot, rotate, tag


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
