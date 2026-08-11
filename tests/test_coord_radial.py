import warnings
from math import pi

import numpy as np
import pytest
from numpy.testing import assert_allclose

from plotnine import (
    aes,
    coord_radial,
    geom_point,
    ggplot,
    scale_y_continuous,
)
from plotnine.coords.coord_radial import polar_bbox
from plotnine.data import mtcars
from plotnine.exceptions import PlotnineWarning
from plotnine.iapi import labels_view


def test_arc_range_normalizes_end_forward():
    assert coord_radial(start=1, end=4)._arc_range == (1, 4)
    assert_allclose(coord_radial(start=pi, end=0)._arc_range, (pi, 2 * pi))
    assert_allclose(
        coord_radial(start=pi, end=2 * pi)._arc_range, (pi, 2 * pi)
    )
    assert_allclose(coord_radial(start=0, end=2 * pi)._arc_range, (0, 2 * pi))
    assert coord_radial(start=1, end=1)._arc_range == (1, 1)
    assert coord_radial(start=1)._arc_range == (1, 1 + 2 * pi)


def test_classifies_full_circle_from_arc_range():
    assert coord_radial()._is_full_circle
    assert coord_radial(start=0, end=2 * pi)._is_full_circle
    assert coord_radial(start=1, end=1 + 2 * pi)._is_full_circle
    assert coord_radial(end=2 * pi, reverse="theta")._is_full_circle
    assert not coord_radial(start=0, end=pi)._is_full_circle
    assert not coord_radial(start=1, end=1)._is_full_circle


def test_polar_bbox_full_circle_is_unit_square():
    assert polar_bbox((0.0, 2 * pi)) == (0.0, 1.0, 0.0, 1.0)


def test_aspect_is_square():
    assert coord_radial().aspect(None) == 1


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        (-pi / 2, pi / 2, 0.5),  # right half-disc: wide box
        (0.0, 0.25, pytest.approx(4.041, abs=1e-2)),  # thin sliver: tall box
        (-pi / 2, 0.0, 1.0),  # quarter: square
        (0.0, 2 * pi, 1.0),  # full circle: square
    ],
)
def test_aspect_matches_wedge(start: float, end: float, expected: float):
    assert coord_radial(start=start, end=end).aspect(None) == expected


def test_aspect_uses_zero_margin_for_half_disc():
    # margin 0 (not ggplot2's 0.05) -> exactly 0.5, so the panel matches the
    # tight wedge and the sector is not stretched.
    assert coord_radial(start=-pi / 2, end=pi / 2).aspect(None) == 0.5


def test_to_radians_zero_width_range():
    assert_allclose(coord_radial()._to_radians(np.array([1, 2, 3]), (1, 1)), 0)


def test_swaps_labels_when_theta_y():
    out = coord_radial(theta="y").labels(labels_view(x="xlab", y="ylab"))
    assert out.x == "ylab"
    assert out.y == "xlab"


def test_keeps_labels_when_theta_x():
    out = coord_radial(theta="x").labels(labels_view(x="xlab", y="ylab"))
    assert out.x == "xlab"
    assert out.y == "ylab"


def test_no_longer_has_r_axis_inside():
    with pytest.raises(TypeError, match="r_axis_inside"):
        coord_radial(r_axis_inside=True)  # type: ignore[call-arg]


def test_coord_polar_is_alias_of_coord_radial():
    # coord_polar is superseded; it is exported only as an alias so old
    # code keeps working. It IS coord_radial with the same signature.
    from plotnine import coord_polar

    assert issubclass(coord_polar, coord_radial)
    assert isinstance(
        coord_polar(theta="y", inner_radius=0.4, end=3.14), coord_radial
    )
    assert coord_polar.__doc__ == (
        "alias of [coord_radial](`plotnine.coords.coord_radial.coord_radial`)"
    )


def test_full_circle_position_right_no_warning():
    # position="right" moves only the r title, so a full circle no longer
    # warns that it has no visible effect. This is the one test that draws;
    # it inspects nothing afterwards.
    p = (
        ggplot(mtcars, aes("disp", "mpg"))
        + geom_point()
        + coord_radial()
        + scale_y_continuous(position="right")
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", PlotnineWarning)
        p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
