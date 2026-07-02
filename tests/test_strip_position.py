import pytest

from plotnine import aes, facet_wrap, geom_point, ggplot
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
