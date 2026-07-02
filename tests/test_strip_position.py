import pytest

from plotnine import aes, facet_wrap, geom_point, ggplot, theme
from plotnine.data import mtcars
from plotnine.exceptions import PlotnineError

p = ggplot(mtcars, aes("wt", "mpg")) + geom_point()


def test_invalid_strip_position():
    with pytest.raises(PlotnineError):
        facet_wrap("cyl", strip_position="north")


@pytest.mark.parametrize(
    "position, target",
    [
        ("top", "strip_text_x_top"),
        ("bottom", "strip_text_x_bottom"),
        ("left", "strip_text_y_left"),
        ("right", "strip_text_y_right"),
    ],
)
def test_strips_land_on_requested_side(position, target):
    plot = p + facet_wrap("cyl", strip_position=position)
    plot.draw_test()
    strips = getattr(plot.theme.targets, target)
    assert len(strips) == 3  # one strip per panel of cyl


def test_strip_position_top():
    plot = p + facet_wrap("cyl", nrow=2)
    assert plot == "strip_position_top"


def test_strip_position_bottom():
    plot = p + facet_wrap("cyl", nrow=2, strip_position="bottom")
    assert plot == "strip_position_bottom"


def test_strip_position_left():
    plot = p + facet_wrap("cyl", nrow=2, strip_position="left")
    assert plot == "strip_position_left"


def test_strip_position_right():
    plot = p + facet_wrap("cyl", nrow=2, strip_position="right")
    assert plot == "strip_position_right"


def test_strip_position_bottom_free_x():
    plot = p + facet_wrap(
        "cyl", nrow=2, strip_position="bottom", scales="free_x"
    )
    assert plot == "strip_position_bottom_free_x"


def test_strip_position_left_free_y():
    plot = p + facet_wrap(
        "cyl", nrow=2, strip_position="left", scales="free_y"
    )
    assert plot == "strip_position_left_free_y"


def test_strip_position_bottom_outside():
    plot = (
        p
        + facet_wrap("cyl", nrow=2, strip_position="bottom")
        + theme(strip_placement="outside")
    )
    assert plot == "strip_position_bottom_outside"


def test_composition_bottom_strip_title_alignment():
    plot = (p + facet_wrap("cyl", strip_position="bottom")) | p
    assert plot == "composition_bottom_strip"
