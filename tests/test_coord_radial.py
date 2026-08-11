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
    geom_col,
    geom_path,
    geom_point,
    geom_polygon,
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


def test_full_circle():
    p = p_point + coord_radial()
    assert p == "full_circle"


def test_half_disc():
    p = p_point + coord_radial(start=-pi / 2, end=pi / 2)
    assert p == "half_disc"


def test_quarter():
    p = p_point + coord_radial(start=-pi / 2, end=0)
    assert p == "quarter"


def test_thin_wedge():
    p = p_point + coord_radial(start=-pi / 2, end=-pi / 3)
    assert p == "thin_wedge"


def test_sliver():
    p = p_point + coord_radial(start=0, end=0.25)
    assert p == "sliver"


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


def test_donut_half_disc():
    p = p_point + coord_radial(start=-pi / 2, end=pi / 2, inner_radius=0.3)
    assert p == "donut_half_disc"


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


def test_expand_partial_arc():
    # With the default expand=True the theta axis is buffered, so the
    # outermost bars sit inside the arc ends instead of flush against them.
    p = p_col + coord_radial(start=0, end=pi, inner_radius=0.1)
    assert p == "expand_partial_arc"


def test_expand_false_partial_arc():
    p = p_col + coord_radial(start=0, end=pi, inner_radius=0.1, expand=False)
    assert p == "expand_false_partial_arc"


def test_rlim():
    # Zooming the radius recomputes nice breaks over (10, 25) rather than
    # filtering the full-range breaks, which would leave almost none.
    p = p_point + coord_radial(rlim=(10, 25))
    assert p == "rlim"


def test_thetalim():
    p = p_point + coord_radial(thetalim=(2, 4))
    assert p == "thetalim"


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


def test_reverse_thetar():
    p = p_col + coord_radial(
        start=pi, end=pi / 2, inner_radius=0.1, reverse="thetar"
    )
    assert p == "reverse_thetar"


def test_path_munched_into_arc():
    # Each segment is subdivided before the radian transform, so it bends
    # along the arc instead of cutting a straight chord across it.
    p = ggplot(path_data, aes("x", "y")) + geom_path(size=1) + coord_radial()
    assert p == "path_munched_into_arc"


def test_polygon_closes_across_seam():
    # The closing edge from the last vertex back to the first crosses the
    # seam at 12 o'clock and must be munched like every other edge.
    p = (
        ggplot(path_data, aes("x", "y"))
        + geom_polygon(fill="none", color="black", size=1)
        + coord_radial()
    )
    assert p == "polygon_closes_across_seam"


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
        + geom_text(angle=0, size=12)
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


def test_donut_chart():
    p = (
        ggplot(pie_data, aes("one", "value", fill="slice"))
        + geom_col()
        + coord_radial("y", inner_radius=0.4)
    )
    assert p == "donut_chart"


def test_default_theme_hides_boundaries():
    # theme_gray blanks axis_line_x and axis_line_y, and axis_line_theta and
    # axis_line_r nest under them, so a default plot outlines neither the
    # wedge nor the hole without any theme() call.
    p = p_point + coord_radial(start=-0.4 * pi, end=0.4 * pi, inner_radius=0.3)
    assert p == "default_theme_hides_boundaries"


def test_axis_line_styles_polar_spine():
    # panel_border no longer owns the outer circle. axis_line does, and
    # unlike panel_border it can style it rather than only hide it.
    p = (
        p_col
        + coord_radial()
        + theme(
            panel_border=element_blank(),
            axis_line=element_line(color="red", size=2),
        )
    )
    assert p == "axis_line_styles_polar_spine"


def test_axis_line_theta_skips_donut_hole():
    # No theta axis lives on the inner boundary, so the themeable that
    # covers the theta line draws the outer arc only.
    p = (
        p_col
        + coord_radial(start=-pi / 2, end=pi / 2, inner_radius=0.3)
        + theme(axis_line_theta=element_line(color="red", size=2))
    )
    assert p == "axis_line_theta_skips_donut_hole"


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


def test_axis_text_theming():
    # axis_text used to be a no-op on a polar panel. axis_text_theta_* and
    # axis_text_r_* nest under axis_text_x/y, so a plain axis_text= reaches
    # both the theta and the r labels.
    p = p_wedge + theme(axis_text=element_text(color="red", size=13))
    assert p == "axis_text_theming"


def test_axis_text_theta_blank():
    p = p_wedge + theme(axis_text_theta=element_blank())
    assert p == "axis_text_theta_blank"


def test_axis_text_theta_margin():
    # The largest margin side sets the gap between a theta label and the
    # arc, whichever side it is.
    p = p_wedge + theme(axis_text_theta=element_text(margin=margin(r=12)))
    assert p == "axis_text_theta_margin"


def test_axis_ticks_theming():
    # As with axis_text, a plain axis_ticks= reaches both sets of marks, and
    # axis_ticks_minor= overrides it on the minor ones. theme_gray blanks
    # minor marks globally, so they appear only once overridden. Colouring
    # the two differently shows both reaching the arc and the spoke.
    p = p_wedge + theme(
        axis_ticks=element_line(color="blue", size=2),
        axis_ticks_minor=element_line(color="green", size=1),
    )
    assert p == "axis_ticks_theming"


def test_axis_ticks_length_per_axis():
    # Length is themed per axis, so the arc grows long marks while the spoke
    # is left with none. A length of 0 renders no mark rather than failing.
    p = p_wedge + theme(
        axis_ticks_length_major_theta=10,
        axis_ticks_length_major_r=0,
    )
    assert p == "axis_ticks_length_per_axis"


def test_axis_ticks_theta_blank_keeps_label_gap():
    # A blank tick contributes no length, so the label keeps its plain gap
    # to the arc rather than being pushed out by the themed length.
    p = p_wedge + theme(
        axis_ticks_major_theta=element_blank(),
        axis_ticks_length_major_theta=20,
    )
    assert p == "axis_ticks_theta_blank_keeps_label_gap"


def test_panel_grid_theming():
    p = p_wedge + theme(panel_grid=element_line(color="white", size=1.5))
    assert p == "panel_grid_theming"


def test_scale_x_position_top():
    # On a polar panel scale.position moves only the axis title. The theta
    # axis itself stays outside the arc.
    p = (
        p_point
        + coord_radial(start=-1.0, end=1.0, inner_radius=0.3)
        + scale_x_continuous(position="top")
    )
    assert p == "scale_x_position_top"


def test_scale_y_position_right():
    # Likewise the r axis stays on the start spoke; only its title moves.
    p = (
        p_point
        + coord_radial(start=-1.0, end=1.0, inner_radius=0.3)
        + scale_y_continuous(position="right")
    )
    assert p == "scale_y_position_right"


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


def test_secondary_r_axis_themed():
    p = (
        p_point
        + scale_y_continuous(
            sec_axis=sec_axis(lambda x: x * 0.354006, name="km/L")
        )
        + coord_radial(start=-pi / 2, end=pi / 2, inner_radius=0.1)
        + theme(
            axis_line_r=element_line(),
            axis_text_r=element_text(color="blue"),
        )
    )
    assert p == "secondary_r_axis_themed"


def test_secondary_r_axis_theta_y():
    p = (
        p_point
        + scale_x_continuous(
            sec_axis=sec_axis(lambda x: x * 0.354006, name="scaled")
        )
        + coord_radial("y", start=-pi / 2, end=pi / 2)
    )
    assert p == "secondary_r_axis_theta_y"
