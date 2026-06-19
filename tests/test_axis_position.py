from plotnine import (
    aes,
    coord_flip,
    facet_wrap,
    geom_point,
    ggplot,
    scale_x_continuous,
    scale_x_discrete,
    scale_y_continuous,
)
from plotnine.data import mtcars

p0 = ggplot(mtcars, aes("wt", "mpg")) + geom_point()


def test_x_axis_top_continuous():
    p = p0 + scale_x_continuous(position="top")
    assert p == "x_axis_top_continuous"


def test_y_axis_right_continuous():
    p = p0 + scale_y_continuous(position="right")
    assert p == "y_axis_right_continuous"


def test_coord_flip_x_top():
    # Before flipping, the y-axis is on the non-default side,
    # after flipping the x-axis will be on the non-default side.
    p = p0 + scale_y_continuous(position="right") + coord_flip()
    assert p == "coord_flip_x_top"


def test_facet_wrap_y_right():
    p = (
        ggplot(mtcars, aes("wt", "mpg"))
        + geom_point()
        + facet_wrap("gear")
        + scale_y_continuous(position="right")
    )
    assert p == "facet_wrap_y_right"


def test_x_axis_top_discrete():
    p = (
        ggplot(mtcars, aes("factor(cyl)", "mpg"))
        + geom_point()
        + scale_x_discrete(position="top")
    )
    assert p == "x_axis_top_discrete"
