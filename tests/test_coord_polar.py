import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from numpy.testing import assert_allclose

from plotnine import (
    aes,
    coord_radial,
    element_blank,
    element_line,
    geom_col,
    geom_point,
    ggplot,
    theme,
)
from plotnine.coords.coord_cartesian import coord_cartesian
from plotnine.coords.coord_polar import coord_polar
from plotnine.iapi import labels_view
from plotnine.scales import scale_x_continuous, scale_y_continuous


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

    assert coord.params["theta_range"] == (0, 10)
    assert coord.params["r_range"] == (0, 10)
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

    assert coord.params["theta_range"] == (0, 10)
    assert coord.params["r_range"] == (0, 10)
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


def test_coord_polar_to_radians_zero_width_range():
    coord = coord_polar()
    coord.params = {"theta_range": (1, 1)}

    assert_allclose(coord._to_radians(np.array([1, 2, 3])), [0, 0, 0])


def test_coord_polar_transforms_segment_endpoints_theta_x():
    coord = coord_polar(theta="x")
    coord.params = {"theta_range": (0, 10), "r_range": (0, 10)}
    data = pd.DataFrame({"x": [0], "y": [1], "xend": [10], "yend": [2]})

    out = coord.transform(data, None)

    assert out.loc[0, "x"] == 0
    assert out.loc[0, "y"] == 1
    assert np.isclose(out.loc[0, "xend"], 2 * np.pi)
    assert out.loc[0, "yend"] == 2


def test_coord_polar_transforms_segment_endpoints_theta_y():
    coord = coord_polar(theta="y")
    coord.params = {"theta_range": (0, 10), "r_range": (0, 10)}
    data = pd.DataFrame({"x": [1], "y": [0], "xend": [2], "yend": [10]})

    out = coord.transform(data, None)

    assert out.loc[0, "x"] == 0
    assert out.loc[0, "y"] == 1
    assert np.isclose(out.loc[0, "xend"], 2 * np.pi)
    assert out.loc[0, "yend"] == 2


def test_coord_polar_transforms_theta_y_without_endpoints():
    coord = coord_polar(theta="y")
    coord.params = {"theta_range": (0, 10), "r_range": (0, 10)}
    data = pd.DataFrame({"x": [1], "y": [5]})

    out = coord.transform(data, None)

    assert_allclose(out.loc[0, "x"], np.pi)
    assert out.loc[0, "y"] == 1


def test_coord_polar_munches_before_radian_transform():
    coord = coord_polar()
    coord.params = {"theta_range": (0, 10), "r_range": (0, 10)}
    data = pd.DataFrame({"x": [0, 10], "y": [1, 2], "group": [1, 1]})

    out = coord.transform(data, None, munch=True)

    assert len(out) > len(data)
    assert out["x"].between(0, 2 * np.pi).all()


def test_coord_polar_leaves_non_position_data_unchanged():
    coord = coord_polar()
    data = pd.DataFrame({"label": ["A"]})

    assert coord.transform(data, None) is data


def test_coord_polar_distance_and_backtransform_theta_x():
    coord = coord_polar()
    coord.params = {"theta_range": (0, 10), "r_range": (0, 20)}

    distance = coord.distance(pd.Series([0, 10]), pd.Series([0, 10]), None)

    assert_allclose(distance, [np.sqrt(1.25)])
    assert coord.backtransform_range(None).x == (0, 10)
    assert coord.backtransform_range(None).y == (0, 20)


def test_coord_polar_distance_and_backtransform_theta_y():
    coord = coord_polar(theta="y")
    coord.params = {"theta_range": (0, 10), "r_range": (0, 20)}

    distance = coord.distance(pd.Series([0, 10]), pd.Series([0, 10]), None)

    assert_allclose(distance, [np.sqrt(1.25)])
    assert coord.backtransform_range(None).x == (0, 20)
    assert coord.backtransform_range(None).y == (0, 10)


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


def test_coord_polar_draw_uses_polar_axes_and_hides_blank_border():
    data = pd.DataFrame({"x": ["a", "b"], "y": [1, 2]})
    p = (
        ggplot(data, aes("x", "y"))
        + geom_col()
        + coord_polar()
        + theme(panel_border=element_blank(), axis_line=element_line())
    )

    fig = p.draw()

    try:
        ax = fig.axes[0]
        assert ax.name == "polar"
        assert not ax.spines["polar"].get_visible()
    finally:
        plt.close(fig)


def test_coord_projection_creates_projected_axes():
    class coord_custom(coord_cartesian):
        _projection = "polar"

    data = pd.DataFrame({"x": [1, 2], "y": [1, 2]})
    p = ggplot(data, aes("x", "y")) + geom_point() + coord_custom()

    fig = p.draw()

    try:
        assert fig.axes[0].name == "polar"
    finally:
        plt.close(fig)


def test_coord_radial_arc_uses_end_or_full_turn():
    assert coord_radial(start=1, end=4)._arc == 3
    assert coord_radial()._arc == 2 * np.pi


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

    assert coord.params["theta_range"] == (0, 10)
    assert coord.params["r_range"] == (2, 8)
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


def test_coord_radial_shows_theta_labels_by_default():
    scale_x, scale_y = trained_scales()
    coord = coord_radial(expand=False)  # no theta_labels arg
    pv = coord.setup_panel_params(scale_x, scale_y)
    assert list(pv.x.breaks)  # theta breaks present by default
    assert list(pv.x.labels)


def test_coord_radial_to_radians_zero_width_range():
    coord = coord_radial()
    coord.params = {"theta_range": (1, 1)}

    assert_allclose(coord._to_radians(np.array([1, 2, 3])), [0, 0, 0])


def test_coord_radial_transform_rotates_angle():
    coord = coord_radial(rotate_angle=True)
    coord.params = {"theta_range": (0, 10), "r_range": (0, 10)}
    data = pd.DataFrame({"x": [0, 5], "y": [1, 1], "angle": [10, 20]})

    out = coord.transform(data, None)

    # x=0 -> top spoke (rotation 0); x=5 -> bottom spoke (180deg) which
    # folds back to a horizontal, readable label (rotation 0).
    assert_allclose(out["x"], [0, np.pi])
    assert_allclose(out["angle"], [10, 20])


def test_coord_radial_rotate_angle_aligns_upright():
    coord = coord_radial(rotate_angle=True)
    coord.params = {"theta_range": (0, 3), "r_range": (0, 10)}
    # theta data 0 -> top, 1 -> 120deg clockwise, 2 -> 240deg clockwise.
    data = pd.DataFrame(
        {"x": [0.0, 1.0, 2.0], "y": [1, 1, 1], "angle": [0.0, 0.0, 0.0]}
    )

    out = coord.transform(data, None)

    # Labels align tangentially to the arc and are folded into (-90, 90]
    # so they stay upright (a bottom label reads "6", not "9").
    assert all(-90 <= a <= 90 for a in out["angle"])
    assert_allclose(out["angle"], [0.0, 60.0, -60.0], atol=1e-6)
