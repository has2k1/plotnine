from dataclasses import replace
from typing import Any, Literal

import numpy as np
import pandas as pd
import pytest
from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
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
    guide_axis_theta,
    guides,
    scale_x_reverse,
    scale_y_reverse,
    theme,
)
from plotnine._mpl._radial_axis import p9ThetaTick
from plotnine.data import mtcars
from plotnine.iapi import (
    labels_view,
    radial_panel_view,
    scale_position_view,
)
from plotnine.scales import scale_x_continuous, scale_y_continuous
from plotnine.themes.elements import margin


def _dummy_scale_view() -> scale_position_view:
    """Minimal position-scale state for radial coordinate unit tests"""
    return scale_position_view(
        scale=None,  # type: ignore[arg-type]
        aesthetics=[],
        name=None,
        limits=(0, 1),
        range=(0, 1),
        breaks=[],
        minor_breaks=np.array([], dtype=float),
        labels=[],
        position="bottom",
    )


def make_panel_view(
    theta_range: tuple[float, float],
    r_range: tuple[float, float],
) -> radial_panel_view:
    """Radial panel state with distinct data and display ranges"""
    theta = replace(_dummy_scale_view(), range=theta_range)
    r = replace(_dummy_scale_view(), range=r_range)
    return radial_panel_view(
        x=replace(theta, range=(0, 2 * np.pi)),
        y=replace(r),
        theta=theta,
        r=r,
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


def radial_axis_sides(
    start: float,
    *,
    direction: Literal[-1, 1] = 1,
) -> tuple[float, float]:
    """
    Signed start-spoke sides occupied by the first r tick and label
    """
    p = (
        ggplot(mtcars, aes("factor(cyl)", "mpg", fill="factor(cyl)"))
        + geom_col()
        + coord_radial(
            start=start,
            direction=direction,
            inner_radius=0.1,
        )
        + theme(axis_line_y=element_line())
    )
    p.draw_test()
    ax = p.axs[0]
    ax.figure.draw_without_rendering()
    tick = next(
        t
        for t in ax.yaxis.get_major_ticks()
        if t.get_loc() > 0 and t.label1.get_text()
    )
    radius = tick.get_loc()
    spoke_point = ax.transData.transform((start, radius))
    centre = ax.transData.transform((start, 0))
    label_box = tick.label1.get_window_extent(
        renderer=ax.figure._get_renderer()  # pyright: ignore
    )
    label_point = np.asarray(label_box.get_points()).mean(axis=0)
    spoke = spoke_point - centre
    label_offset = label_point - spoke_point
    label_side = spoke[0] * label_offset[1] - spoke[1] * label_offset[0]

    marker = tick.tick1line._marker  # pyright: ignore[reportPrivateUsage]
    marker_vertices = (
        marker.get_path().transformed(marker.get_transform()).vertices
    )
    tick_offset = marker_vertices[
        np.argmax(np.linalg.norm(marker_vertices, axis=1))
    ]
    tick_side = spoke[0] * tick_offset[1] - spoke[1] * tick_offset[0]
    return float(tick_side), float(label_side)


def _theta_margin_plot(
    text_margin: (margin | dict[Literal["t", "r", "b", "l", "unit"], Any]),
    *,
    inner_radius: float = 0,
    labels: tuple[str, str, str] = ("0", "120", "330"),
    **text_properties: Any,
) -> ggplot:
    data = pd.DataFrame({"x": [0, 120, 330], "y": [1, 2, 3]})
    return (
        ggplot(data, aes("x", "y"))
        + geom_point()
        + scale_x_continuous(
            breaks=[0, 120, 330],
            labels=labels,
            limits=(0, 360),
            expand=(0, 0),
        )
        + coord_radial(inner_radius=inner_radius)
        + theme(
            axis_text_x=element_text(
                margin=text_margin,
                **text_properties,
            ),
            axis_text_y=element_blank(),
            axis_ticks_y=element_blank(),
            axis_title=element_blank(),
        )
    )


@pytest.mark.parametrize(
    ("text_margin", "expected"),
    [
        ({"t": 2, "r": 4, "b": 1, "l": 3}, 4),
        ({"t": -2, "r": 0, "b": 0, "l": 0}, 0),
        ({"t": -5, "r": -2, "b": -8, "l": -4}, -2),
        (margin(t=1 / 72, r=3 / 72, unit="in"), 3),
    ],
)
def test_coord_radial_theta_margin_uses_largest_side(
    text_margin: (margin | dict[Literal["t", "r", "b", "l", "unit"], Any]),
    expected: float,
):
    p = _theta_margin_plot(text_margin)
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]

    assert p.axs[0].xaxis.get_major_ticks()[0].get_pad() == expected


def _theta_label_clearance(
    ax: Axes,
    text: str,
    side: Literal["inside", "outside"] = "outside",
) -> float:
    canvas = FigureCanvasAgg(ax.figure)
    canvas.draw()
    renderer = canvas.get_renderer()
    label_name = "label1" if side == "inside" else "label2"
    tickline_name = "tick1line" if side == "inside" else "tick2line"
    tick = next(
        tick
        for tick in ax.xaxis.get_major_ticks()
        if getattr(tick, label_name).get_text() == text
    )
    tick.draw(renderer)

    label = getattr(tick, label_name)
    tickline = getattr(tick, tickline_name)
    boundary = tickline.get_transform().transform(tickline.get_xydata())[0]
    centre = ax.transData.transform((tick.get_loc(), ax.get_rorigin()))
    outward = boundary - centre
    outward /= np.linalg.norm(outward)
    if side == "inside":
        outward *= -1

    tick_length = (
        tick._size  # pyright: ignore[reportPrivateUsage]
        * ax.figure.dpi
        / 72
        if tickline.get_visible()
        else 0
    )
    reference = boundary + outward * tick_length
    assert isinstance(tick, p9ThetaTick)
    corners = tick._label_bounds(label, renderer).corners()
    return float(np.min((corners - reference) @ outward))


def _theta_label_bounds(
    text: str,
) -> tuple[np.ndarray, np.ndarray, float]:
    p = _theta_margin_plot({})
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
    ax = p.axs[0]
    canvas = FigureCanvasAgg(ax.figure)
    canvas.draw()
    renderer = canvas.get_renderer()
    tick = ax.xaxis.get_major_ticks()[0]
    assert isinstance(tick, p9ThetaTick)
    label = tick.label2
    label.set_text(text)

    anchor = label.get_transform().transform(label.get_position())
    logical, parts, _ = label._get_layout(renderer)
    descent = parts[-1][1][2]
    logical = logical.translated(*anchor)
    corrected = tick._label_bounds(label, renderer)
    return logical.get_points(), corrected.get_points(), descent


@pytest.mark.parametrize(
    "text",
    ["300", "-3.0", "+3E0", "3e-2", "\N{MINUS SIGN}300"],
)
def test_coord_radial_numeric_theta_label_bounds_remove_descent(text: str):
    logical, corrected, descent = _theta_label_bounds(text)

    assert_allclose(corrected[0], logical[0] + [0, descent])
    assert_allclose(corrected[1], logical[1])


@pytest.mark.parametrize(
    "text",
    ["3g0", "angle", "3\n0", "$300$", "", "٣٠٠"],
)
def test_coord_radial_other_theta_label_bounds_are_unchanged(text: str):
    logical, corrected, _ = _theta_label_bounds(text)

    assert_allclose(corrected, logical)


def test_coord_radial_theta_label_clearance_is_uniform():
    p = _theta_margin_plot({})
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
    ax = p.axs[0]

    assert_allclose(
        [
            _theta_label_clearance(ax, "120"),
            _theta_label_clearance(ax, "330"),
        ],
        0,
        atol=0.01,
    )


def test_coord_radial_theta_label_descent_correction():
    p = _theta_margin_plot({}, labels=("0", "300", "3g0"))
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
    ax = p.axs[0]

    assert_allclose(
        [
            _theta_label_clearance(ax, "300"),
            _theta_label_clearance(ax, "3g0"),
        ],
        0,
        atol=0.01,
    )


def test_coord_radial_theta_label_ignores_alignment():
    p = _theta_margin_plot({}, ha="left", va="top")
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
    ax = p.axs[0]

    assert_allclose(
        [
            _theta_label_clearance(ax, "120"),
            _theta_label_clearance(ax, "330"),
        ],
        0,
        atol=0.01,
    )


@pytest.mark.parametrize(
    ("text_margin", "expected"),
    [
        ({"t": 2, "r": 4, "b": 1, "l": 3}, 4),
        ({"t": -2, "r": 0, "b": 0, "l": 0}, 0),
        ({"t": -5, "r": -2, "b": -8, "l": -4}, -2),
    ],
)
def test_coord_radial_theta_label_clearance_uses_margin(
    text_margin: dict[Literal["t", "r", "b", "l", "unit"], Any],
    expected: float,
):
    p = _theta_margin_plot(text_margin, size=16)
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
    ax = p.axs[0]
    expected_pixels = expected * ax.figure.dpi / 72

    assert_allclose(
        [
            _theta_label_clearance(ax, "120"),
            _theta_label_clearance(ax, "330"),
        ],
        expected_pixels,
        atol=0.01,
    )


def test_coord_radial_theta_label_clearance_ignores_blank_tick_length():
    p = _theta_margin_plot({}) + theme(
        axis_ticks_x=element_blank(),
        axis_ticks_length_major_x=20,
    )
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
    ax = p.axs[0]

    assert_allclose(
        [
            _theta_label_clearance(ax, "120"),
            _theta_label_clearance(ax, "330"),
        ],
        0,
        atol=0.01,
    )


def test_coord_radial_rotated_theta_label_clearance():
    p = _theta_margin_plot({}) + guides(theta=guide_axis_theta(angle=35))
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
    ax = p.axs[0]

    assert_allclose(
        [
            _theta_label_clearance(ax, "120"),
            _theta_label_clearance(ax, "330"),
        ],
        0,
        atol=0.01,
    )


def test_coord_radial_theta_label_clearance_does_not_accumulate():
    p = _theta_margin_plot({})
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
    ax = p.axs[0]
    first = _theta_label_clearance(ax, "330")

    ax.figure.draw_without_rendering()  # pyright: ignore[reportAttributeAccessIssue]
    second = _theta_label_clearance(ax, "330")
    ax.figure.set_size_inches(8, 5)
    ax.figure.draw_without_rendering()  # pyright: ignore[reportAttributeAccessIssue]
    resized = _theta_label_clearance(ax, "330")

    assert_allclose([first, second, resized], 0, atol=0.01)


def test_coord_radial_inside_theta_label_clearance():
    p = _theta_margin_plot({}, inner_radius=0.3)
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
    ax = p.axs[0]
    ax.tick_params(
        axis="x",
        bottom=True,
        labelbottom=True,
        top=False,
        labeltop=False,
    )

    assert_allclose(
        [
            _theta_label_clearance(ax, "120", "inside"),
            _theta_label_clearance(ax, "330", "inside"),
        ],
        0,
        atol=0.01,
    )


def test_coord_radial_theta_label_clearance():
    p = _theta_margin_plot({}, labels=("0", "300", "3g0"))
    assert p == "coord_radial_theta_label_clearance"


def test_coord_radial_setup_panel_params_theta_x():
    scale_x, scale_y = trained_scales(
        x_breaks=(0, 5, 10),
        x_labels=("0", "5", "10"),
        y_breaks=(0, 2, 5, 10),
        y_labels=("0", "2", "5", "10"),
    )
    coord = coord_radial(theta="x", start=np.pi / 4, expand=False)

    panel_params = coord.setup_panel_params(scale_x, scale_y)

    assert panel_params.theta.range == (0, 10)
    assert panel_params.r.range == (0, 10)
    assert panel_params.x.range == (np.pi / 4, np.pi / 4 + 2 * np.pi)
    assert panel_params.theta is not panel_params.x
    assert panel_params.r is not panel_params.y
    assert panel_params.theta.breaks == [0, 5, 10]
    # Theta breaks are kept as radian positions (0,5,10 over [0,10] ->
    # start + fraction * 2pi), not cleared the way coord_polar used to.
    assert_allclose(
        panel_params.x.breaks,
        [np.pi / 4, np.pi / 4 + np.pi, np.pi / 4 + 2 * np.pi],
    )
    assert panel_params.x.labels == ["0", "5", "10"]
    assert panel_params.y.breaks == [0, 2, 5, 10]


def test_coord_radial_setup_panel_params_theta_y():
    scale_x, scale_y = trained_scales(
        x_breaks=(0, 2, 5, 10),
        x_labels=("0", "2", "5", "10"),
    )
    coord = coord_radial(theta="y", expand=False)

    panel_params = coord.setup_panel_params(scale_x, scale_y)

    assert panel_params.theta.range == (0, 10)
    assert panel_params.r.range == (0, 10)
    assert panel_params.y.breaks == [0, 2, 5, 10]


def test_coord_radial_discrete_theta_spans_full_circle():
    p = (
        ggplot(mtcars, aes("factor(cyl)", "mpg", fill="factor(cyl)"))
        + geom_col()
        + coord_radial(start=0, end=2 * np.pi, inner_radius=0)
    )
    built = p.build_test()
    panel_params = built.layout.panel_params[0]
    transformed = built.coordinates.transform(
        built.layers[0].data.copy(),
        panel_params,
    )

    expected = built.coordinates._to_radians(
        [1, 2, 3],
        panel_params.theta.range,
    )
    actual = np.sort(transformed["x"].unique())

    assert_allclose(actual, expected)
    assert np.ptp(actual) > np.pi


def test_coord_radial_setup_panel_params_per_panel_independent():
    # one instance reused across panels (faceting)
    coord = coord_radial(expand=False)
    sx1, sy1 = trained_scales(y=(0, 10))
    pv1 = coord.setup_panel_params(sx1, sy1)
    sx2, sy2 = trained_scales(y=(0, 100))
    pv2 = coord.setup_panel_params(sx2, sy2)
    assert pv1.y.range == (0, 10)
    assert pv2.y.range == (0, 100)


def test_coord_radial_transform_uses_per_panel_range_not_last():
    coord = coord_radial()  # one instance reused across panels (faceting)
    sx1, sy1 = trained_scales(x=(0, 10), y=(0, 10))
    pv1 = coord.setup_panel_params(sx1, sy1)
    sx2, sy2 = trained_scales(x=(0, 20), y=(0, 20))
    coord.setup_panel_params(sx2, sy2)  # would clobber shared state
    # Transform a point against panel 1 AFTER panel 2 was set up.
    out = coord.transform(pd.DataFrame({"x": [5], "y": [5]}), pv1)
    # x=5 in panel 1's theta range (0,10) -> norm 0.5 -> pi (half turn).
    assert_allclose(out.loc[0, "x"], np.pi)


def test_coord_radial_transforms_segment_endpoints_theta_x():
    coord = coord_radial(theta="x")
    pv = make_panel_view((0, 10), (0, 10))
    data = pd.DataFrame({"x": [0], "y": [1], "xend": [10], "yend": [2]})

    out = coord.transform(data, pv)

    assert out.loc[0, "x"] == 0
    assert out.loc[0, "y"] == 1
    assert np.isclose(out.loc[0, "xend"], 2 * np.pi)
    assert out.loc[0, "yend"] == 2


def test_coord_radial_transforms_segment_endpoints_theta_y():
    coord = coord_radial(theta="y")
    pv = make_panel_view((0, 10), (0, 10))
    data = pd.DataFrame({"x": [1], "y": [0], "xend": [2], "yend": [10]})

    out = coord.transform(data, pv)

    assert out.loc[0, "x"] == 0
    assert out.loc[0, "y"] == 1
    assert np.isclose(out.loc[0, "xend"], 2 * np.pi)
    assert out.loc[0, "yend"] == 2


def test_coord_radial_transforms_theta_y_without_endpoints():
    coord = coord_radial(theta="y")
    pv = make_panel_view((0, 10), (0, 10))
    data = pd.DataFrame({"x": [1], "y": [5]})

    out = coord.transform(data, pv)

    assert_allclose(out.loc[0, "x"], np.pi)
    assert out.loc[0, "y"] == 1


def test_coord_radial_munches_before_radian_transform():
    coord = coord_radial()
    pv = make_panel_view((0, 10), (0, 10))
    data = pd.DataFrame({"x": [0, 10], "y": [1, 2], "group": [1, 1]})

    out = coord.transform(data, pv, munch=True)

    assert len(out) > len(data)
    assert out["x"].between(0, 2 * np.pi).all()


def test_coord_radial_leaves_non_position_data_unchanged():
    coord = coord_radial()
    data = pd.DataFrame({"label": ["A"]})

    assert coord.transform(data, None) is data


def test_coord_radial_distance_and_backtransform_theta_x():
    coord = coord_radial()
    pv = make_panel_view((0, 10), (0, 20))

    distance = coord.distance(pd.Series([0, 10]), pd.Series([0, 10]), pv)

    assert_allclose(distance, [np.sqrt(1.25)])
    assert coord.backtransform_range(pv).x == (0, 10)
    assert coord.backtransform_range(pv).y == (0, 20)


def test_coord_radial_distance_and_backtransform_theta_y():
    coord = coord_radial(theta="y")
    pv = make_panel_view((0, 10), (0, 20))

    distance = coord.distance(pd.Series([0, 10]), pd.Series([0, 10]), pv)

    assert_allclose(distance, [np.sqrt(1.25)])
    assert coord.backtransform_range(pv).x == (0, 20)
    assert coord.backtransform_range(pv).y == (0, 10)


def test_coord_radial_aspect_is_square():
    assert coord_radial().aspect(None) == 1


def test_coord_radial_swaps_labels_when_theta_y():
    coord = coord_radial(theta="y")
    out = coord.labels(labels_view(x="xlab", y="ylab"))
    assert out.x == "ylab"
    assert out.y == "xlab"


def test_coord_radial_keeps_labels_when_theta_x():
    coord = coord_radial(theta="x")
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


def test_coord_radial_partial_arc_expands_off_ends():
    # Regression: outermost bars used to sit flush against the arc ends
    # (angles 0 and pi). With the default expand=True the theta axis is
    # buffered, so the bars sit inside the arc.
    p = (
        ggplot(mtcars, aes("cyl", "mpg"))
        + geom_col()
        + coord_radial(start=0, end=np.pi, inner_radius=0.1)
    )
    assert p == "coord_radial_partial_arc_expands_off_ends"


def test_coord_radial_axis_line_controls_polar_spine():
    # panel_border no longer owns the outer circle; axis_line does, and
    # unlike panel_border it can style it, not just hide it.
    data = pd.DataFrame({"x": ["a", "b"], "y": [1, 2]})
    p = (
        ggplot(data, aes("x", "y"))
        + geom_col()
        + coord_radial()
        + theme(
            panel_border=element_blank(),
            axis_line=element_line(color="red", size=2),
        )
    )
    assert p == "coord_radial_axis_line_controls_polar_spine"


def test_coord_radial_axis_line_r_start_shows_on_full_circle():
    # coord_radial() is a full circle, so matplotlib's own default hides
    # the 'start'/'end' spokes. Explicitly theming axis_line_r_start
    # must show it anyway, and the choice must survive the real draw.
    data = pd.DataFrame({"x": ["a", "b"], "y": [1, 2]})
    p = (
        ggplot(data, aes("x", "y"))
        + geom_col()
        + coord_radial()
        + theme(axis_line_r_start=element_line(color="blue", size=2))
    )
    assert p == "coord_radial_axis_line_r_start_shows_on_full_circle"


def test_coord_radial_ticks_visible_by_default():
    # Ticks were previously invisible on every polar panel regardless of
    # theme, because activation was skipped entirely; this is the
    # regression test for that fix.
    data = pd.DataFrame({"x": ["a", "b"], "y": [1, 2]})
    p = ggplot(data, aes("x", "y")) + geom_col() + coord_radial()
    assert p == "coord_radial_ticks_visible_by_default"


def test_coord_radial_default_theme_does_not_crash():
    data = pd.DataFrame({"x": ["a", "b"], "y": [1, 2]})
    p = ggplot(data, aes("x", "y")) + geom_col() + coord_radial()

    p.draw_test()


def test_coord_radial_arc_range_normalizes_end_forward():
    assert coord_radial(start=1, end=4)._arc_range == (1, 4)
    assert_allclose(
        coord_radial(start=np.pi, end=0)._arc_range,
        (np.pi, 2 * np.pi),
    )
    assert_allclose(
        coord_radial(start=np.pi, end=2 * np.pi)._arc_range,
        (np.pi, 2 * np.pi),
    )
    assert_allclose(
        coord_radial(start=0, end=2 * np.pi)._arc_range,
        (0, 2 * np.pi),
    )
    assert coord_radial(start=1, end=1)._arc_range == (1, 1)
    assert coord_radial(start=1)._arc_range == (1, 1 + 2 * np.pi)


def test_coord_radial_classifies_full_circle_from_arc_range():
    assert coord_radial()._is_full_circle
    assert coord_radial(start=0, end=2 * np.pi)._is_full_circle
    assert coord_radial(start=1, end=1 + 2 * np.pi)._is_full_circle
    assert coord_radial(
        end=2 * np.pi,
        direction=-1,
        reverse="theta",
    )._is_full_circle
    assert not coord_radial(start=0, end=np.pi)._is_full_circle
    assert not coord_radial(start=1, end=1)._is_full_circle


@pytest.mark.parametrize("end", [None, 2 * np.pi])
def test_coord_radial_full_circle_r_axis_uses_start(
    end: float | None,
):
    p = (
        ggplot(mtcars, aes("cyl", "mpg"))
        + geom_col()
        + coord_radial(start=0, end=end, inner_radius=0.1)
        + theme(axis_line_y=element_line())
    )
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
    ax = p.axs[0]
    ax.figure.draw_without_rendering()  # pyright: ignore[reportAttributeAccessIssue]
    tick = next(
        tick
        for tick in ax.yaxis.get_major_ticks()
        if tick.get_loc() > 0 and tick.label1.get_text()
    )
    renderer = ax.figure._get_renderer()  # pyright: ignore[reportAttributeAccessIssue]
    radius = tick.get_loc()
    tick_point = tick.tick1line.get_transform().transform((0, radius))
    label_point = np.asarray(
        tick.label1.get_window_extent(renderer=renderer).get_points()
    ).mean(axis=0)
    start_point = ax.transData.transform((0, radius))

    assert_allclose(ax.get_xlim(), (0, 2 * np.pi))
    assert_allclose((ax.get_thetamin(), ax.get_thetamax()), (0, 360))
    assert ax.get_rlabel_position() == 0
    assert_allclose(tick_point, start_point)
    assert_allclose(label_point[1], start_point[1])


def test_coord_radial_full_circle_panel_params_ignore_end_representation():
    views = []
    for end in (None, 2 * np.pi):
        scale_x, scale_y = trained_scales(
            x_breaks=(0, 5, 10),
            x_labels=("0", "5", "10"),
        )
        views.append(
            coord_radial(start=0, end=end, expand=False).setup_panel_params(
                scale_x,
                scale_y,
            )
        )

    assert_allclose(views[0].x.range, views[1].x.range)
    assert_allclose(views[0].x.breaks, views[1].x.breaks)
    assert_allclose(views[0].x.minor_breaks, views[1].x.minor_breaks)
    assert views[0].x.labels == views[1].x.labels


@pytest.mark.parametrize("direction", [1, -1])
def test_coord_radial_equivalent_endpoints_have_same_sweep(
    direction: Literal[-1, 1],
):
    pi = 3.14159
    coords = [
        coord_radial(start=pi, end=end, direction=direction)
        for end in (0, 2 * pi)
    ]
    angles = [coord._to_radians([1, 2, 3], (0.4, 3.6)) for coord in coords]

    assert_allclose(angles[0], angles[1], rtol=1e-5)
    assert all(np.all(np.diff(values) > 0) for values in angles)
    assert [coord._mpl_direction for coord in coords] == [
        -direction,
        -direction,
    ]


def test_coord_radial_no_longer_has_r_axis_inside():
    import pytest

    with pytest.raises(TypeError, match="r_axis_inside"):
        coord_radial(r_axis_inside=True)  # type: ignore[call-arg]


def test_coord_radial_full_circle_position_right_no_warning():
    import warnings

    from plotnine.exceptions import PlotnineWarning

    # position="right" now moves only the r title, so a full circle no
    # longer warns that it has no visible effect.
    p = (
        ggplot(mtcars, aes("disp", "mpg"))
        + geom_point()
        + coord_radial()
        + scale_y_continuous(position="right")
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", PlotnineWarning)
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

    assert panel_params.theta.range == (0, 10)
    assert panel_params.r.range == (2, 8)
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


def test_coord_radial_reverse_r_builds_reversed_display_view():
    scale_x, scale_y = trained_scales(
        y=(0, 10),
        y_breaks=(0, 5, 10),
        y_labels=("0", "5", "10"),
    )
    panel_params = coord_radial(
        reverse="r",
        expand=False,
    ).setup_panel_params(scale_x, scale_y)

    assert panel_params.r.range == (0, 10)
    assert panel_params.r.limits == (0, 10)
    assert panel_params.y.range == (-10, 0)
    assert panel_params.y.limits == (-10, 0)
    assert_allclose(panel_params.y.breaks, [0, -5, -10])
    assert_allclose(
        panel_params.y.minor_breaks,
        -np.asarray(panel_params.r.minor_breaks),
    )
    assert panel_params.y.labels == ["0", "5", "10"]


@pytest.mark.parametrize(
    ("theta", "data", "expected_y", "expected_yend"),
    [
        (
            "x",
            pd.DataFrame(
                {"x": [2.0], "y": [3.0], "xend": [4.0], "yend": [5.0]}
            ),
            [-3.0],
            [-5.0],
        ),
        (
            "y",
            pd.DataFrame(
                {"x": [3.0], "y": [2.0], "xend": [5.0], "yend": [4.0]}
            ),
            [-3.0],
            [-5.0],
        ),
    ],
)
def test_coord_radial_reverse_r_negates_display_coordinates(
    theta: Literal["x", "y"],
    data: pd.DataFrame,
    expected_y: list[float],
    expected_yend: list[float],
):
    panel_params = make_panel_view((0, 10), (0, 10))
    result = coord_radial(
        theta=theta,
        reverse="r",
        expand=False,
    ).transform(data, panel_params)

    assert_allclose(result["y"], expected_y)
    assert_allclose(result["yend"], expected_yend)


def test_coord_radial_reverse_r_matches_reversed_scale_geometry():
    base = ggplot(mtcars, aes("factor(cyl)", "mpg")) + geom_col()
    plots = [
        base
        + coord_radial(
            start=np.pi,
            end=np.pi / 2,
            inner_radius=0.1,
            reverse="r",
        ),
        base
        + scale_y_reverse()
        + coord_radial(
            start=np.pi,
            end=np.pi / 2,
            inner_radius=0.1,
        ),
    ]

    for plot in plots:
        plot.draw_test()  # pyright: ignore[reportAttributeAccessIssue]

    actual, expected = (plot.axs[0] for plot in plots)
    assert_allclose(actual.get_ylim(), expected.get_ylim())
    assert_allclose(actual.get_rorigin(), expected.get_rorigin())
    assert len(actual.collections) == len(expected.collections)
    for actual_collection, expected_collection in zip(
        actual.collections,
        expected.collections,
        strict=True,
    ):
        actual_paths = actual_collection.get_paths()
        expected_paths = expected_collection.get_paths()
        assert len(actual_paths) == len(expected_paths)
        for actual_path, expected_path in zip(
            actual_paths,
            expected_paths,
            strict=True,
        ):
            distances = np.linalg.norm(
                actual_path.vertices[:, None, :]
                - expected_path.vertices[None, :, :],
                axis=2,
            )
            assert_allclose(distances.min(axis=0), 0, atol=1e-12)
            assert_allclose(distances.min(axis=1), 0, atol=1e-12)

    theta = actual.collections[0].get_paths()[0].vertices[0, 0]
    origin = np.asarray(
        actual.transData.transform((theta, actual.get_rorigin()))
    )
    baseline = np.asarray(actual.transData.transform((theta, 0)))
    inward = np.asarray(actual.transData.transform((theta, -22.8)))
    assert np.linalg.norm(baseline - origin) > np.linalg.norm(inward - origin)


@pytest.mark.parametrize(
    ("theta", "reverse", "inner_radius"),
    [
        ("x", "r", 0),
        ("x", "r", 0.3),
        ("x", "thetar", 0.1),
        ("y", "r", 0.1),
    ],
)
def test_coord_radial_reverse_r_matches_reversed_scale_cases(
    theta: Literal["x", "y"],
    reverse: Literal["r", "thetar"],
    inner_radius: float,
):
    data = pd.DataFrame({"x": [1, 2, 3], "y": [2, 5, 8]})
    mapping = aes("x", "y") if theta == "x" else aes("y", "x")
    scale = scale_y_reverse() if theta == "x" else scale_x_reverse()
    plots = [
        ggplot(data, mapping)
        + geom_point()
        + coord_radial(
            theta=theta,
            start=0,
            end=np.pi if reverse == "thetar" else None,
            inner_radius=inner_radius,
            reverse=reverse,
        ),
        ggplot(data, mapping)
        + geom_point()
        + scale
        + coord_radial(
            theta=theta,
            start=0,
            end=np.pi if reverse == "thetar" else None,
            inner_radius=inner_radius,
            reverse="theta" if reverse == "thetar" else "none",
        ),
    ]

    for plot in plots:
        plot.draw_test()  # pyright: ignore[reportAttributeAccessIssue]

    actual, expected = (plot.axs[0] for plot in plots)
    assert_allclose(actual.get_ylim(), expected.get_ylim())
    assert_allclose(actual.get_rorigin(), expected.get_rorigin())
    assert_allclose(
        actual.collections[0].get_offsets(),
        expected.collections[0].get_offsets(),
    )


def test_coord_radial_reverse_r_respects_rlim():
    scale_x, scale_y = trained_scales(y=(0, 10))
    panel_params = coord_radial(
        reverse="r",
        rlim=(2, 8),
        expand=False,
    ).setup_panel_params(scale_x, scale_y)

    assert panel_params.r.limits == (2, 8)
    assert panel_params.r.range == (2, 8)
    assert panel_params.y.limits == (-8, -2)
    assert panel_params.y.range == (-8, -2)


def test_coord_radial_reverse_r_cancels_reversed_scale_geometry():
    data = pd.DataFrame({"x": [1, 2], "y": [2, 8]})
    plots = [
        ggplot(data, aes("x", "y")) + geom_point() + coord_radial(),
        ggplot(data, aes("x", "y"))
        + geom_point()
        + scale_y_reverse()
        + coord_radial(reverse="r"),
    ]

    for plot in plots:
        plot.draw_test()  # pyright: ignore[reportAttributeAccessIssue]

    ordinary, double_reversed = (plot.axs[0] for plot in plots)
    assert_allclose(ordinary.get_ylim(), double_reversed.get_ylim())
    assert_allclose(ordinary.get_rorigin(), double_reversed.get_rorigin())
    assert_allclose(
        ordinary.collections[0].get_offsets(),
        double_reversed.collections[0].get_offsets(),
    )


def test_coord_radial_reverse_theta_keeps_wedge_flips_order():
    # reverse="theta" runs the data the other way around the SAME arc; it
    # must not mirror the wedge onto the opposite side. So the mapped theta
    # breaks reflect about the arc midpoint (start + end - break), while the
    # arc itself and the physical draw direction are unchanged.
    scale_x, scale_y = trained_scales()
    base = coord_radial(start=np.pi, end=np.pi / 2, expand=False)
    rev = coord_radial(
        start=np.pi, end=np.pi / 2, expand=False, reverse="theta"
    )
    assert base._arc_range == rev._arc_range
    assert base._mpl_direction == rev._mpl_direction

    pv_base = base.setup_panel_params(scale_x, scale_y)
    pv_rev = rev.setup_panel_params(scale_x, scale_y)
    arc_lo, arc_hi = base._arc_range
    assert_allclose(
        list(pv_rev.x.breaks),
        [arc_lo + arc_hi - b for b in pv_base.x.breaks],
    )


def test_coord_radial_shows_theta_labels_by_default():
    scale_x, scale_y = trained_scales()
    coord = coord_radial(expand=False)  # no theta_labels arg
    pv = coord.setup_panel_params(scale_x, scale_y)
    assert list(pv.x.breaks)  # theta breaks present by default
    assert list(pv.x.labels)


def test_coord_radial_restores_theta_minor_breaks():
    # coord_polar clears theta minor breaks (data-space ticks are meaningless
    # on the arc); coord_radial must restore them as radian positions, the
    # same way it restores the major breaks, so the theta minor grid renders.
    scale_x, scale_y = trained_scales()
    coord = coord_radial(expand=False)
    pv = coord.setup_panel_params(scale_x, scale_y)
    minor = list(pv.x.minor_breaks)
    assert minor  # not empty
    assert all(0 <= b <= 2 * np.pi for b in minor)


def test_coord_radial_clips_theta_minor_breaks_to_partial_arc():
    scale_x, scale_y = trained_scales()
    coord = coord_radial(start=0, end=np.pi, expand=False)
    pv = coord.setup_panel_params(scale_x, scale_y)
    minor = list(pv.x.minor_breaks)
    assert minor
    assert all(0 <= b <= np.pi for b in minor)


def test_coord_radial_discrete_theta_has_no_minor_breaks():
    # A discrete theta scale has no minor breaks and no get_minor_breaks
    # method, so setting one up must not crash and leaves the theta minor
    # grid empty.
    df = pd.DataFrame({"cat": ["a", "b", "c"], "y": [2, 3, 5]})
    p = ggplot(df, aes("cat", "y")) + geom_col() + coord_radial(theta="x")
    pv = p.build_test().layout.panel_params[0]
    assert list(pv.x.minor_breaks) == []


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


def test_coord_radial_axis_clearance():
    data = pd.DataFrame(
        {"x": ["a", "a", "a"], "y": [2, 3, 5], "group": ["a", "b", "c"]}
    )
    p = (
        ggplot(data, aes("x", "y", fill="group"))
        + geom_col()
        + coord_radial("y")
    )
    assert p == "coord_radial_axis_clearance"


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
    # theme reaches minor ticks on both axes. This plot only exercises
    # the r-axis half: coord_radial doesn't currently populate theta
    # minor breaks, so there are no theta minor ticks to render here.
    p = (
        ggplot(mtcars, aes("disp", "mpg"))
        + geom_point()
        + coord_radial(start=0.5 * np.pi, end=-0.5 * np.pi, inner_radius=0.3)
        + theme(
            axis_ticks_minor=element_line(color="green", size=1),
        )
    )
    assert p == "coord_radial_axis_ticks_minor_theming"


def test_coord_radial_ticks_length_themed_nonzero():
    # axis_ticks_length_major_x/_y used to zero the tick length on a
    # polar panel because the first major tick's tick1line/tick2line
    # visibility check never held before Task 5 activated polar tick
    # visibility. axis_ticks_length_major_theta/_r are the leaves that
    # now apply length on a polar panel, so a themed nonzero length
    # actually renders long tick marks.
    p = (
        ggplot(mtcars, aes("disp", "mpg"))
        + geom_point()
        + coord_radial(start=0.5 * np.pi, end=-0.5 * np.pi, inner_radius=0.3)
        + theme(axis_ticks_length=10)
    )
    assert p == "coord_radial_ticks_length_themed_nonzero"


def test_coord_radial_ticks_length_themed_zero_stays_invisible():
    # Counterpart to the nonzero case above: a themed length of 0
    # should still render with no visible tick marks.
    p = (
        ggplot(mtcars, aes("disp", "mpg"))
        + geom_point()
        + coord_radial(start=0.5 * np.pi, end=-0.5 * np.pi, inner_radius=0.3)
        + theme(axis_ticks_length=0)
    )
    assert p == "coord_radial_ticks_length_themed_zero_stays_invisible"


def test_coord_radial_scale_x_position_top_keeps_theta_outside():
    # On a polar panel scale.position moves only the axis title; the
    # primary theta axis stays on the outside regardless of position.
    from plotnine._mpl.axes import axis_at

    p = (
        ggplot(mtcars, aes("disp", "mpg"))
        + geom_point()
        + coord_radial(start=-1.0, end=1.0, inner_radius=0.3)
        + scale_x_continuous(position="top")
    )
    p.draw_test()
    ax = p.axs[0]
    assert axis_at(ax, "theta_outside") is ax.xaxis
    assert axis_at(ax, "theta_inside") is None


def test_coord_radial_scale_y_position_right_keeps_r_start():
    # On a polar panel scale.position moves only the axis title; the
    # primary r axis stays on r_start regardless of position.
    from plotnine._mpl.axes import axis_at

    p = (
        ggplot(mtcars, aes("disp", "mpg"))
        + geom_point()
        + coord_radial(start=-1.0, end=1.0, inner_radius=0.3)
        + scale_y_continuous(position="right")
    )
    p.draw_test()
    ax = p.axs[0]
    assert axis_at(ax, "r_start") is ax.yaxis
    assert axis_at(ax, "r_end") is None


def test_coord_radial_reverse_theta_moves_r_axis_to_end():
    # reverse="theta" runs a partial arc from end back to start, so the
    # radial axis follows the data to the end spoke; a full circle has a
    # single shared spoke and keeps the axis at the start.
    from plotnine._mpl.axes import axis_at

    def r_side(**kwargs) -> ggplot:
        p = (
            ggplot(mtcars, aes("factor(cyl)", "mpg"))
            + geom_col()
            + coord_radial(inner_radius=0.1, **kwargs)
            + theme(axis_line_y=element_line())
        )
        p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
        return p.axs[0]

    partial = r_side(start=np.pi, end=np.pi / 2, reverse="theta")
    assert axis_at(partial, "r_end") is partial.yaxis
    assert axis_at(partial, "r_start") is None

    full = r_side(reverse="theta")
    assert axis_at(full, "r_start") is full.yaxis
    assert axis_at(full, "r_end") is None


def test_p9_radial_axes_build_plotnine_ticks():
    from plotnine._mpl._radial_axis import (
        p9RadialAxis,
        p9RadialTick,
        p9ThetaAxis,
        p9ThetaTick,
    )

    assert p9ThetaAxis._tick_class is p9ThetaTick
    assert p9RadialAxis._tick_class is p9RadialTick

    p = ggplot(mtcars, aes("disp", "mpg")) + geom_point() + coord_radial()
    p.draw_test()
    assert isinstance(p.axs[0].yaxis, p9RadialAxis)


def test_coord_radial_r_axis_uses_pre_sweep_side():
    tick_side, label_side = radial_axis_sides(0)

    assert tick_side > 0
    assert label_side > 0


def test_coord_radial_r_axis_rotates_with_start():
    tick_side, label_side = radial_axis_sides(np.pi / 2)

    assert tick_side > 0
    assert label_side > 0


def test_coord_radial_r_axis_flips_with_effective_sweep():
    clockwise_tick, clockwise_label = radial_axis_sides(0)
    counter_tick, counter_label = radial_axis_sides(0, direction=-1)

    assert clockwise_tick > 0
    assert clockwise_label > 0
    assert counter_tick < 0
    assert counter_label < 0


@pytest.mark.parametrize(
    ("start", "end", "expected_end"),
    [(0, np.pi, np.pi), (np.pi, 0, 2 * np.pi)],
)
def test_coord_radial_partial_r_axis_uses_start(
    start: float,
    end: float,
    expected_end: float,
):
    p = (
        ggplot(mtcars, aes("factor(cyl)", "mpg"))
        + geom_col()
        + coord_radial(start=start, end=end, inner_radius=0.1)
        + theme(axis_line_y=element_line())
    )
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
    ax = p.axs[0]
    ax.figure.draw_without_rendering()  # pyright: ignore[reportAttributeAccessIssue]
    tick = next(
        tick
        for tick in ax.yaxis.get_major_ticks()
        if tick.get_loc() > 0 and tick.label1.get_text()
    )
    radius = tick.get_loc()
    tick_point = tick.tick1line.get_transform().transform((0, radius))
    expected = ax.transData.transform((start, radius))

    assert_allclose(ax.get_xlim(), (start, expected_end))
    assert_allclose(tick_point, expected)
    assert tick.tick1line.get_visible()
    assert tick.label1.get_visible()
    assert not tick.tick2line.get_visible()
    assert not tick.label2.get_visible()
    assert ax.spines["start"].get_visible()
    assert not ax.spines["end"].get_visible()


def test_coord_polar_is_alias_of_coord_radial():
    # coord_polar is superseded; it is exported only as an alias so old
    # code keeps working. It IS coord_radial with the same signature.
    from plotnine import coord_polar

    assert issubclass(coord_polar, coord_radial)
    c = coord_polar(theta="y", inner_radius=0.4, end=3.14)
    assert isinstance(c, coord_radial)
    assert coord_polar.__doc__ == (
        "alias of [coord_radial](`plotnine.coords.coord_radial.coord_radial`)"
    )
