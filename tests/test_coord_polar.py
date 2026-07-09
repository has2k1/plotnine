import numpy as np
import pandas as pd
from numpy.testing import assert_allclose

from plotnine import (
    aes,
    coord_radial,
    element_blank,
    element_line,
    element_text,
    geom_col,
    geom_point,
    ggplot,
    theme,
)
from plotnine.coords.coord_polar import coord_polar
from plotnine.data import mtcars
from plotnine.iapi import labels_view, panel_view, scale_view
from plotnine.scales import scale_x_continuous, scale_y_continuous


def _dummy_scale_view() -> scale_view:
    """A minimal scale_view; polar transforms only read theta/r ranges."""
    return scale_view(
        scale=None,  # type: ignore[arg-type]
        aesthetics=[],
        name=None,
        limits=(0, 1),
        range=(0, 1),
        breaks=[],
        minor_breaks=np.array([], dtype=float),
        labels=[],
    )


def make_panel_view(theta_range, r_range) -> panel_view:
    """A panel_view carrying just the per-panel theta/r ranges."""
    return panel_view(
        x=_dummy_scale_view(),
        y=_dummy_scale_view(),
        theta_range=theta_range,
        r_range=r_range,
    )


def trained_scales(
    x=(0, 10),
    y=(0, 10),
    x_breaks=(0, 5, 10),
    y_breaks=(0, 5, 10),
    x_labels=("0", "5", "10"),
    y_labels=("0", "5", "10"),
):
    scale_x = scale_x_continuous(breaks=x_breaks, labels=x_labels)
    scale_y = scale_y_continuous(breaks=y_breaks, labels=y_labels)
    scale_x.train(x)
    scale_y.train(y)
    return scale_x, scale_y


def test_coord_polar_setup_panel_params_theta_x():
    scale_x, scale_y = trained_scales(
        y_breaks=(0, 2, 5, 10),
        y_labels=("0", "2", "5", "10"),
    )
    coord = coord_polar(theta="x", start=np.pi / 4, expand=False)

    panel_params = coord.setup_panel_params(scale_x, scale_y)

    assert panel_params.theta_range == (0, 10)
    assert panel_params.r_range == (0, 10)
    assert panel_params.x.range == (np.pi / 4, np.pi / 4 + 2 * np.pi)
    assert panel_params.x.breaks == []
    assert panel_params.x.labels == []
    assert panel_params.y.breaks == [0, 2, 5, 10]


def test_coord_polar_setup_panel_params_theta_y():
    scale_x, scale_y = trained_scales(
        x_breaks=(0, 2, 5, 10),
        x_labels=("0", "2", "5", "10"),
    )
    coord = coord_polar(theta="y", expand=False)

    panel_params = coord.setup_panel_params(scale_x, scale_y)

    assert panel_params.theta_range == (0, 10)
    assert panel_params.r_range == (0, 10)
    assert panel_params.y.breaks == [0, 2, 5, 10]


def test_coord_polar_setup_panel_params_per_panel_independent():
    # one instance reused across panels (faceting)
    coord = coord_polar(expand=False)
    sx1, sy1 = trained_scales(y=(0, 10))
    pv1 = coord.setup_panel_params(sx1, sy1)
    sx2, sy2 = trained_scales(y=(0, 100))
    pv2 = coord.setup_panel_params(sx2, sy2)
    assert pv1.y.range == (0, 10)
    assert pv2.y.range == (0, 100)


def test_coord_polar_transform_uses_per_panel_range_not_last():
    coord = coord_polar()  # one instance reused across panels (faceting)
    sx1, sy1 = trained_scales(x=(0, 10), y=(0, 10))
    pv1 = coord.setup_panel_params(sx1, sy1)
    sx2, sy2 = trained_scales(x=(0, 20), y=(0, 20))
    coord.setup_panel_params(sx2, sy2)  # would clobber shared state
    # Transform a point against panel 1 AFTER panel 2 was set up.
    out = coord.transform(pd.DataFrame({"x": [5], "y": [5]}), pv1)
    # x=5 in panel 1's theta range (0,10) -> norm 0.5 -> pi (half turn).
    assert_allclose(out.loc[0, "x"], np.pi)


def test_coord_polar_to_radians_zero_width_range():
    coord = coord_polar()
    pv = panel_view(
        x=_dummy_scale_view(),
        y=_dummy_scale_view(),
        theta_range=(1, 1),
        r_range=(0, 10),
    )

    assert_allclose(
        coord._to_radians(np.array([1, 2, 3]), pv.theta_range), [0, 0, 0]
    )


def test_coord_polar_transforms_segment_endpoints_theta_x():
    coord = coord_polar(theta="x")
    pv = make_panel_view((0, 10), (0, 10))
    data = pd.DataFrame({"x": [0], "y": [1], "xend": [10], "yend": [2]})

    out = coord.transform(data, pv)

    assert out.loc[0, "x"] == 0
    assert out.loc[0, "y"] == 1
    assert np.isclose(out.loc[0, "xend"], 2 * np.pi)
    assert out.loc[0, "yend"] == 2


def test_coord_polar_transforms_segment_endpoints_theta_y():
    coord = coord_polar(theta="y")
    pv = make_panel_view((0, 10), (0, 10))
    data = pd.DataFrame({"x": [1], "y": [0], "xend": [2], "yend": [10]})

    out = coord.transform(data, pv)

    assert out.loc[0, "x"] == 0
    assert out.loc[0, "y"] == 1
    assert np.isclose(out.loc[0, "xend"], 2 * np.pi)
    assert out.loc[0, "yend"] == 2


def test_coord_polar_transforms_theta_y_without_endpoints():
    coord = coord_polar(theta="y")
    pv = make_panel_view((0, 10), (0, 10))
    data = pd.DataFrame({"x": [1], "y": [5]})

    out = coord.transform(data, pv)

    assert_allclose(out.loc[0, "x"], np.pi)
    assert out.loc[0, "y"] == 1


def test_coord_polar_munches_before_radian_transform():
    coord = coord_polar()
    pv = make_panel_view((0, 10), (0, 10))
    data = pd.DataFrame({"x": [0, 10], "y": [1, 2], "group": [1, 1]})

    out = coord.transform(data, pv, munch=True)

    assert len(out) > len(data)
    assert out["x"].between(0, 2 * np.pi).all()


def test_coord_polar_leaves_non_position_data_unchanged():
    coord = coord_polar()
    data = pd.DataFrame({"label": ["A"]})

    assert coord.transform(data, None) is data


def test_coord_polar_distance_and_backtransform_theta_x():
    coord = coord_polar()
    pv = make_panel_view((0, 10), (0, 20))

    distance = coord.distance(pd.Series([0, 10]), pd.Series([0, 10]), pv)

    assert_allclose(distance, [np.sqrt(1.25)])
    assert coord.backtransform_range(pv).x == (0, 10)
    assert coord.backtransform_range(pv).y == (0, 20)


def test_coord_polar_distance_and_backtransform_theta_y():
    coord = coord_polar(theta="y")
    pv = make_panel_view((0, 10), (0, 20))

    distance = coord.distance(pd.Series([0, 10]), pd.Series([0, 10]), pv)

    assert_allclose(distance, [np.sqrt(1.25)])
    assert coord.backtransform_range(pv).x == (0, 20)
    assert coord.backtransform_range(pv).y == (0, 10)


def test_coord_polar_aspect_is_square():
    assert coord_polar().aspect(None) == 1


def test_coord_polar_swaps_labels_when_theta_y():
    coord = coord_polar(theta="y")
    out = coord.labels(labels_view(x="xlab", y="ylab"))
    assert out.x == "ylab"
    assert out.y == "xlab"


def test_coord_polar_keeps_labels_when_theta_x():
    coord = coord_polar(theta="x")
    out = coord.labels(labels_view(x="xlab", y="ylab"))
    assert out.x == "xlab"
    assert out.y == "ylab"


def test_coord_radial_default_theme_hides_theta_and_r_boundaries():
    # theme_gray blanks axis_line_x/axis_line_y; axis_line_theta and
    # axis_line_r nest under them, so a default plot shows none of the
    # wedge/donut boundary lines without any explicit theme() call.
    p = (
        ggplot(mtcars, aes("disp", "mpg"))
        + geom_point()
        + coord_radial(start=-0.4 * np.pi, end=0.4 * np.pi, inner_radius=0.3)
    )
    assert p == "coord_radial_default_theme_hides_theta_and_r_boundaries"


def test_coord_polar_axis_line_controls_polar_spine():
    # panel_border no longer owns the outer circle; axis_line does, and
    # unlike panel_border it can style it, not just hide it.
    data = pd.DataFrame({"x": ["a", "b"], "y": [1, 2]})
    p = (
        ggplot(data, aes("x", "y"))
        + geom_col()
        + coord_polar()
        + theme(
            panel_border=element_blank(),
            axis_line=element_line(color="red", size=2),
        )
    )
    assert p == "coord_polar_axis_line_controls_polar_spine"


def test_coord_polar_axis_line_r_start_shows_on_full_circle():
    # coord_polar() is a full circle, so matplotlib's own default hides
    # the 'start'/'end' spokes. Explicitly theming axis_line_r_start
    # must show it anyway, and the choice must survive the real draw.
    data = pd.DataFrame({"x": ["a", "b"], "y": [1, 2]})
    p = (
        ggplot(data, aes("x", "y"))
        + geom_col()
        + coord_polar()
        + theme(axis_line_r_start=element_line(color="blue", size=2))
    )
    assert p == "coord_polar_axis_line_r_start_shows_on_full_circle"


def test_coord_polar_ticks_visible_by_default():
    # Ticks were previously invisible on every polar panel regardless of
    # theme, because activation was skipped entirely; this is the
    # regression test for that fix.
    data = pd.DataFrame({"x": ["a", "b"], "y": [1, 2]})
    p = ggplot(data, aes("x", "y")) + geom_col() + coord_polar()
    assert p == "coord_polar_ticks_visible_by_default"


def test_coord_polar_default_theme_does_not_crash():
    data = pd.DataFrame({"x": ["a", "b"], "y": [1, 2]})
    p = ggplot(data, aes("x", "y")) + geom_col() + coord_polar()

    p.draw_test()


def test_coord_radial_arc_uses_end_or_full_turn():
    assert coord_radial(start=1, end=4)._arc == 3
    assert coord_radial()._arc == 2 * np.pi


def test_coord_radial_no_longer_has_r_axis_inside():
    import pytest

    with pytest.raises(TypeError, match="r_axis_inside"):
        coord_radial(r_axis_inside=True)  # type: ignore[call-arg]


def test_coord_radial_full_circle_position_right_warns():
    import pytest

    from plotnine.exceptions import PlotnineWarning

    p = (
        ggplot(mtcars, aes("disp", "mpg"))
        + geom_point()
        + coord_radial()
        + scale_y_continuous(position="right")
    )
    with pytest.warns(PlotnineWarning, match="end.*boundary"):
        p.draw_test()


def test_coord_radial_setup_panel_params_for_partial_arc():
    scale_x, scale_y = trained_scales(
        y_breaks=(0, 2, 4, 8, 10),
        y_labels=("0", "2", "4", "8", "10"),
    )
    coord = coord_radial(
        start=0,
        end=np.pi,
        thetalim=(0, 10),
        rlim=(2, 8),
        expand=False,
    )

    panel_params = coord.setup_panel_params(scale_x, scale_y)

    assert panel_params.theta_range == (0, 10)
    assert panel_params.r_range == (2, 8)
    assert_allclose(panel_params.x.breaks, [0, np.pi / 2, np.pi])
    assert panel_params.x.labels == ["0", "5", "10"]
    assert panel_params.x.range == (0, np.pi)
    assert panel_params.y.range == (2, 8)
    assert panel_params.y.breaks == [2, 4, 8]
    assert panel_params.y.labels == ["2", "4", "8"]


def test_coord_radial_rlim_recomputes_breaks():
    # Auto breaks (breaks=True), so the scale recomputes nice breaks over the
    # zoomed range. Full-range breaks would be [0, 5, 10]; the naive filter to
    # (2, 8) would leave only [5].
    scale_x = scale_x_continuous()
    scale_y = scale_y_continuous()
    scale_x.train((0, 10))
    scale_y.train((0, 10))
    coord = coord_radial(rlim=(2, 8), expand=False)
    pv = coord.setup_panel_params(scale_x, scale_y)
    breaks = list(pv.y.breaks)
    # Recomputed nice breaks over (2, 8) — NOT the naive filter, which would
    # leave only [5]. Must be within the zoom and contain more than one break.
    assert len(breaks) > 1
    assert all(2 <= b <= 8 for b in breaks)
    assert len(pv.y.labels) == len(breaks)


def test_coord_radial_reverse_r_inverts_radial_range():
    scale_x, scale_y = trained_scales(y=(0, 10))
    base = coord_radial(expand=False)
    rev = coord_radial(reverse="r", expand=False)
    pv_base = base.setup_panel_params(scale_x, scale_y)
    pv_rev = rev.setup_panel_params(scale_x, scale_y)
    assert tuple(pv_base.y.range) == (0, 10)
    assert tuple(pv_rev.y.range) == (10, 0)  # reversed: large r toward centre


def test_coord_radial_shows_theta_labels_by_default():
    scale_x, scale_y = trained_scales()
    coord = coord_radial(expand=False)  # no theta_labels arg
    pv = coord.setup_panel_params(scale_x, scale_y)
    assert list(pv.x.breaks)  # theta breaks present by default
    assert list(pv.x.labels)


def test_coord_radial_to_radians_zero_width_range():
    coord = coord_radial()

    assert_allclose(coord._to_radians(np.array([1, 2, 3]), (1, 1)), [0, 0, 0])


def test_coord_radial_transform_rotates_angle():
    coord = coord_radial(rotate_angle=True)
    pv = make_panel_view((0, 10), (0, 10))
    data = pd.DataFrame({"x": [0, 5], "y": [1, 1], "angle": [10, 20]})

    out = coord.transform(data, pv)

    # x=0 -> top spoke (rotation 0); x=5 -> bottom spoke (180deg) which
    # folds back to a horizontal, readable label (rotation 0).
    assert_allclose(out["x"], [0, np.pi])
    assert_allclose(out["angle"], [10, 20])


def test_coord_radial_rotate_angle_aligns_upright():
    coord = coord_radial(rotate_angle=True)
    pv = make_panel_view((0, 3), (0, 10))
    # theta data 0 -> top, 1 -> 120deg clockwise, 2 -> 240deg clockwise.
    data = pd.DataFrame(
        {"x": [0.0, 1.0, 2.0], "y": [1, 1, 1], "angle": [0.0, 0.0, 0.0]}
    )

    out = coord.transform(data, pv)

    # Labels align tangentially to the arc and are folded into (-90, 90]
    # so they stay upright (a bottom label reads "6", not "9").
    assert all(-90 <= a <= 90 for a in out["angle"])
    assert_allclose(out["angle"], [0.0, 60.0, -60.0], atol=1e-6)


def test_coord_polar_axis_clearance():
    data = pd.DataFrame(
        {"x": ["a", "a", "a"], "y": [2, 3, 5], "group": ["a", "b", "c"]}
    )
    p = (
        ggplot(data, aes("x", "y", fill="group"))
        + geom_col()
        + coord_polar("y")
    )
    assert p == "coord_polar_axis_clearance"


def test_coord_radial_axis_text_theming():
    # axis_text used to be a no-op on a polar panel's tick labels;
    # axis_text_theta_* / axis_text_r_* now nest under axis_text_x/y
    # so a plain axis_text= theme reaches both the theta and r labels.
    p = (
        ggplot(mtcars, aes("disp", "mpg"))
        + geom_point()
        + coord_radial(start=0.5 * np.pi, end=-0.5 * np.pi, inner_radius=0.3)
        + theme(axis_text=element_text(color="red", size=5))
    )
    assert p == "coord_radial_axis_text_theming"


def test_coord_radial_axis_ticks_major_theming():
    # axis_ticks used to be a no-op on a polar panel's theta tick
    # marks; axis_ticks_major_theta_* / axis_ticks_major_r_* now nest
    # under axis_ticks_major_x/y so a plain axis_ticks= theme reaches
    # both the theta and r tick marks.
    p = (
        ggplot(mtcars, aes("disp", "mpg"))
        + geom_point()
        + coord_radial(start=0.5 * np.pi, end=-0.5 * np.pi, inner_radius=0.3)
        + theme(axis_ticks=element_line(color="blue", size=2))
    )
    assert p == "coord_radial_axis_ticks_major_theming"


def test_coord_radial_axis_ticks_minor_theming():
    # theme_gray blanks axis_ticks_minor globally, so minor ticks stay
    # invisible everywhere until a user overrides axis_ticks_minor
    # explicitly. axis_ticks_minor_theta_* / axis_ticks_minor_r_* now
    # nest under axis_ticks_minor_x/y so a plain axis_ticks_minor=
    # theme reaches both the theta and r minor tick marks.
    p = (
        ggplot(mtcars, aes("disp", "mpg"))
        + geom_point()
        + coord_radial(start=0.5 * np.pi, end=-0.5 * np.pi, inner_radius=0.3)
        + theme(
            axis_ticks_minor=element_line(color="green", size=1),
        )
    )
    assert p == "coord_radial_axis_ticks_minor_theming"
