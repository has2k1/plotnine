import warnings
from math import pi

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

from plotnine import (
    aes,
    coord_radial,
    element_blank,
    element_line,
    element_text,
    facet_wrap,
    geom_col,
    geom_path,
    geom_point,
    geom_ribbon,
    geom_text,
    ggplot,
    scale_y_continuous,
    theme,
)
from plotnine.coords.coord_radial import polar_bbox
from plotnine.data import mtcars
from plotnine.exceptions import PlotnineWarning
from plotnine.iapi import labels_view
from plotnine.scales import scale_x_continuous, sec_axis
from plotnine.themes.elements import margin

p_point = ggplot(mtcars, aes("wt", "mpg")) + geom_point()
p_col = (
    ggplot(mtcars, aes("factor(cyl)", "mpg", fill="factor(cyl)")) + geom_col()
)

# Points spread evenly around theta, so a chord and an arc differ visibly
path_data = pd.DataFrame({"x": range(6), "y": [3, 8, 5, 9, 4, 7]})

pie_data = pd.DataFrame(
    {"one": ["a"] * 4, "value": [3, 5, 2, 6], "slice": list("wxyz")}
)

# A wedge with a hole shows both sets of tick marks and labels clearly
p_wedge = p_point + coord_radial(
    start=0.5 * pi, end=-0.5 * pi, inner_radius=0.3
)


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


def test_half_disc():
    p = p_point + coord_radial(start=-pi / 2, end=pi / 2)
    assert p == "half_disc"


def test_thin_wedge():
    p = p_point + coord_radial(start=-pi / 2, end=-pi / 3)
    assert p == "thin_wedge"


def test_arc_wraps_past_twelve():
    # end < start, so the end normalises forward and the arc sweeps through
    # 12 o'clock rather than backwards to meet the start.
    p = p_point + coord_radial(start=pi, end=pi / 2)
    assert p == "arc_wraps_past_twelve"


def test_rotated_full_circle():
    # The theta labels and the labelling r spoke both follow `start`.
    p = p_point + coord_radial(start=pi / 4)
    assert p == "rotated_full_circle"


def test_donut_full_circle():
    p = p_point + coord_radial(inner_radius=0.3)
    assert p == "donut_full_circle"


def test_donut_narrow_arc():
    # The inner ring must sit at inner_radius * outer_radius. When it did
    # not, the panel aspect mismatched the wedge and the sector under-filled.
    p = p_point + coord_radial(start=pi / 4, end=3 * pi / 4, inner_radius=0.3)
    assert p == "donut_narrow_arc"


def test_theta_y():
    # theta="y" puts mpg on the arc and wt on the radius, and swaps which
    # axis title the layout treats as the theta title.
    p = p_point + coord_radial("y")
    assert p == "theta_y"


def test_discrete_theta():
    # A discrete theta scale spans the whole circle rather than leaving the
    # last category short of the first.
    p = p_col + coord_radial()
    assert p == "discrete_theta"


def test_expand_false():
    # Every other image in this file uses the default buffer, which holds the
    # data clear of the arc ends and the outer radius. Turning it off is what
    # needs an image of its own: the bars then run flush to both ends of the
    # arc and out to the rim.
    p = p_col + coord_radial(start=0, end=pi, inner_radius=0.1, expand=False)
    assert p == "expand_false"


def test_zoom():
    # Both axes zoom on one coordinate system. The radius recomputes nice
    # breaks over (10, 25) rather than filtering the full-range breaks, which
    # would leave almost none, and (2, 4) of wt spans the whole circle.
    p = p_point + coord_radial(rlim=(10, 25), thetalim=(2, 4))
    assert p == "zoom"


def test_reverse_theta_full_circle():
    # The sweep is still clockwise; the data runs the other way along it.
    p = p_col + coord_radial(reverse="theta")
    assert p == "reverse_theta_full_circle"


def test_reverse_theta_partial_arc():
    # On a partial arc the data runs from end back to start, so the
    # labelling r spoke follows it to the end spoke.
    p = p_col + coord_radial(
        start=pi, end=pi / 2, inner_radius=0.1, reverse="theta"
    )
    assert p == "reverse_theta_partial_arc"


def test_reverse_r():
    p = p_point + coord_radial(reverse="r")
    assert p == "reverse_r"


def test_reverse_r_donut():
    p = p_point + coord_radial(reverse="r", inner_radius=0.3)
    assert p == "reverse_r_donut"


def test_path_munched_into_arc():
    # Each segment is subdivided before the radian transform, so it bends
    # along the arc instead of cutting a straight chord across it.
    p = ggplot(path_data, aes("x", "y")) + geom_path(size=1) + coord_radial()
    assert p == "path_munched_into_arc"


def test_ribbon():
    p = (
        ggplot(path_data, aes("x", ymin="y - 2", ymax="y + 2"))
        + geom_ribbon(alpha=0.5)
        + coord_radial()
    )
    assert p == "ribbon"


def test_rotate_angle_text():
    # The labels align tangentially to the arc and fold into (-90, 90], so
    # the one at the bottom of the circle stays readable.
    p = (
        ggplot(path_data, aes("x", "y", label="y"))
        + geom_text(angle=0, size=18, color="green")
        + coord_radial(rotate_angle=True)
    )
    assert p == "rotate_angle_text"


def test_pie():
    p = (
        ggplot(pie_data, aes("one", "value", fill="slice"))
        + geom_col()
        + coord_radial("y")
    )
    assert p == "pie"


def test_axis_line_styles_polar_boundaries():
    # panel_border no longer owns the outer circle. axis_line does, and
    # unlike panel_border it can style it rather than only hide it. On a
    # donut arc the same themeable shows which boundaries it owns: the outer
    # arc and the spoke holding the radial axis are drawn, while the hole,
    # which no angular axis sits on, is left bare.
    p = (
        p_col
        + coord_radial(start=-pi / 2, end=pi / 2, inner_radius=0.3)
        + theme(
            panel_border=element_blank(),
            axis_line=element_line(color="red", size=2),
        )
    )
    assert p == "axis_line_styles_polar_boundaries"


def test_axis_line_r_start_on_full_circle():
    # A full circle's start and end spokes coincide, so matplotlib hides
    # them by default. Theming axis_line_r_start must show it anyway.
    p = (
        p_col
        + coord_radial()
        + theme(axis_line_r_start=element_line(color="blue", size=2))
    )
    assert p == "axis_line_r_start_on_full_circle"


def test_axis_line_r_end_on_reversed_arc():
    # A spoke is themeable only where a radial axis lives, and reverse=
    # "theta" moves the only one to the end spoke. So axis_line_r_end
    # styles that spoke and the start spoke stays bare.
    p = (
        p_col
        + coord_radial(
            start=-pi / 2, end=pi / 2, inner_radius=0.1, reverse="theta"
        )
        + theme(axis_line_r_end=element_line(color="blue", size=2))
    )
    assert p == "axis_line_r_end_on_reversed_arc"


def test_axis_line_r_reaches_both_spokes():
    # A secondary axis puts a radial axis on each spoke, so the parent
    # themeable styles both leaves at once.
    p = (
        p_col
        + scale_y_continuous(sec_axis=sec_axis(lambda x: x * 2))
        + coord_radial(start=-pi / 2, end=pi / 2, inner_radius=0.1)
        + theme(axis_line_r=element_line(color="blue", size=2))
    )
    assert p == "axis_line_r_reaches_both_spokes"


def test_theming_reaches_all_decorations():
    # The general themeables reach every polar decoration and the polar
    # leaves refine them. Both label sets are red at size 13 from axis_text,
    # and the angular labels sit further out because their own leaf adds a
    # margin while inheriting that colour and size. Major marks are blue and
    # minor ones green, on the arc and on the spokes alike. The angular marks
    # are the longer pair, each axis taking its own themed length. The grid
    # thickens on the rings and the spokes together. A secondary radial axis
    # gives axis_text a second set of radial labels to reach.
    p = (
        p_wedge
        + scale_y_continuous(sec_axis=sec_axis(lambda x: x * 2))
        + theme(
            axis_text=element_text(color="red", size=13),
            axis_text_theta=element_text(margin=margin(r=12)),
            axis_ticks=element_line(color="blue", size=2),
            axis_ticks_minor=element_line(color="green", size=1),
            axis_ticks_length_major_theta=10,
            panel_grid=element_line(color="white", size=1.5),
        )
    )
    assert p == "theming_reaches_all_decorations"


def test_axis_ticks_theta_blank_keeps_label_gap():
    # A blank tick contributes no length, so the label keeps its plain gap
    # to the arc rather than being pushed out by the themed length.
    p = p_wedge + theme(
        axis_ticks_major_theta=element_blank(),
        axis_ticks_length_major_theta=20,
    )
    assert p == "axis_ticks_theta_blank_keeps_label_gap"


def test_scale_positions_move_only_titles():
    # On a polar panel a scale's position moves its axis title and nothing
    # else. Moving both at once shows each title on its new side while the
    # angular axis stays outside the arc and the radial axis stays on the
    # start spoke.
    p = (
        p_point
        + coord_radial(start=-1.0, end=1.0, inner_radius=0.3)
        + scale_x_continuous(position="top")
        + scale_y_continuous(position="right")
    )
    assert p == "scale_positions_move_only_titles"


def test_secondary_r_axis_partial_arc():
    p = (
        p_point
        + scale_y_continuous(
            sec_axis=sec_axis(lambda x: x * 0.354006, name="km/L")
        )
        + coord_radial(start=-pi / 2, end=pi / 2, inner_radius=0.1)
        + theme(axis_line_r=element_line())
    )
    assert p == "secondary_r_axis_partial_arc"


def test_secondary_r_axis_full_circle():
    # A full circle's start and end spokes coincide, so the secondary axis
    # shares the primary's spoke. Its labels and marks go to the other side
    # of that spoke rather than onto a spoke of their own.
    p = (
        p_point
        + scale_y_continuous(
            sec_axis=sec_axis(lambda x: x * 2, breaks=[20, 40, 60])
        )
        + coord_radial()
        + theme(
            axis_line_r=element_line(),
            axis_ticks_length_major=20,
        )
    )
    assert p == "secondary_r_axis_full_circle"


def test_secondary_r_axis_theta_y():
    p = (
        p_point
        + scale_x_continuous(
            sec_axis=sec_axis(lambda x: x * 0.354006, name="scaled")
        )
        + coord_radial("y", start=-pi / 2, end=pi / 2)
    )
    assert p == "secondary_r_axis_theta_y"


def test_facet_wrap():
    # Every polar panel draws its full theta and radial decorations, so the
    # gulley must hold them and the strip band must clear the arc apex.
    p = p_point + facet_wrap("gear", nrow=2) + coord_radial(start=-1, end=1)
    assert p == "facet_wrap"
