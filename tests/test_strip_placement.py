from plotnine import (
    aes,
    facet_grid,
    facet_wrap,
    geom_point,
    ggplot,
    scale_x_continuous,
    scale_y_continuous,
    theme,
    theme_gray,
)
from plotnine.data import mtcars

p = ggplot(mtcars, aes("wt", "mpg")) + geom_point()


def test_strip_placement_themeable_default_and_set():
    assert theme_gray().getp("strip_placement") == "inside"
    assert theme(strip_placement="outside").getp("strip_placement") == (
        "outside"
    )


def test_facet_wrap_top_inside():
    p1 = p + facet_wrap("cyl") + scale_x_continuous(position="top")
    assert p1 == "facet_wrap_top_inside"


def test_facet_wrap_top_outside():
    p1 = (
        p
        + facet_wrap("cyl")
        + scale_x_continuous(position="top")
        + theme(strip_placement="outside")
    )
    assert p1 == "facet_wrap_top_outside"


def test_facet_grid_top_inside():
    p1 = p + facet_grid("am", "cyl") + scale_x_continuous(position="top")
    assert p1 == "facet_grid_top_inside"


def test_facet_grid_top_outside():
    p1 = (
        p
        + facet_grid("am", "cyl")
        + scale_x_continuous(position="top")
        + theme(strip_placement="outside")
    )
    assert p1 == "facet_grid_top_outside"


def test_facet_grid_right_inside():
    p1 = p + facet_grid("am", "cyl") + scale_y_continuous(position="right")
    assert p1 == "facet_grid_right_inside"


def test_facet_grid_right_outside():
    p1 = (
        p
        + facet_grid("am", "cyl")
        + scale_y_continuous(position="right")
        + theme(strip_placement="outside")
    )
    assert p1 == "facet_grid_right_outside"


def test_facet_grid_top_right_inside():
    p1 = (
        p
        + facet_grid("am", "cyl")
        + scale_x_continuous(position="top")
        + scale_y_continuous(position="right")
    )
    assert p1 == "facet_grid_top_right_inside"


def test_facet_grid_top_right_outside():
    p1 = (
        p
        + facet_grid("am", "cyl")
        + scale_x_continuous(position="top")
        + scale_y_continuous(position="right")
        + theme(strip_placement="outside")
    )
    assert p1 == "facet_grid_top_right_outside"
