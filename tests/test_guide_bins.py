from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

import numpy.testing as npt
import pandas as pd
import pytest

import plotnine as p9
from plotnine import (
    aes,
    element_line,
    element_text,
    geom_point,
    ggplot,
    guides,
    theme,
)
from plotnine.exceptions import PlotnineError, PlotnineWarning
from plotnine.guides.guide_bins import guide_bins
from plotnine.guides.guide_colorsteps import guide_colorsteps
from plotnine.scales.scale_color import scale_color_binned
from plotnine.scales.scale_manual import scale_color_manual, scale_shape_manual
from plotnine.scales.scale_shape import scale_shape_binned
from plotnine.scales.scale_size import scale_size_binned

if TYPE_CHECKING:
    from plotnine.guides.guide_colorbar import GuideElementsColorbar
    from plotnine.typing import Orientation


data = pd.DataFrame({"x": range(10), "y": range(10), "z": range(10)})


def test_binned_guides_are_part_of_the_public_api():
    names = {"guide_bins", "guide_colorsteps", "guide_coloursteps"}

    assert names <= set(p9.__all__)
    assert all(callable(getattr(p9, name)) for name in names)
    assert p9.guide_coloursteps is p9.guide_colorsteps


@pytest.mark.parametrize(
    ("aesthetic", "scale", "guide_type"),
    [
        ("color", scale_color_binned(), guide_colorsteps),
        ("shape", scale_shape_binned(), guide_bins),
    ],
)
def test_binned_scale_default_guide_is_resolved(aesthetic, scale, guide_type):
    data = pd.DataFrame({"x": [1, 2], "y": [1, 2], "z": [0, 1]})
    p = ggplot(data, aes("x", "y", **{aesthetic: "z"})) + geom_point() + scale

    p.draw_test()

    assert isinstance(next(iter(p.guides._lookup.values()))[1], guide_type)


def test_colorsteps_inherits_limit_labels_from_scale():
    scale = scale_color_binned(
        breaks=[5],
        limits=(0, 10),
        show_limits=True,
    )
    guide = guide_colorsteps(title="value")

    guide.train(scale)

    npt.assert_allclose(guide.key["value"], [0, 5, 10])
    assert guide.key["label"].tolist() == ["0", "5", "10"]


def test_colorsteps_labels_explicit_limit_breaks():
    scale = scale_color_binned(
        breaks=[0, 5, 10],
        limits=(0, 10),
        show_limits=False,
    )
    guide = guide_colorsteps(title="value")

    guide.train(scale)

    npt.assert_allclose(guide.key["value"], [0, 5, 10])


def test_colorsteps_warns_when_fixed_labels_do_not_include_limits():
    scale = scale_color_binned(
        breaks=[5],
        labels=["middle"],
        limits=(0, 10),
        show_limits=True,
    )
    guide = guide_colorsteps(title="value")

    with pytest.warns(PlotnineWarning, match="Fixed labels"):
        guide.train(scale)

    assert guide.key["label"].tolist() == ["0", "middle", "10"]


def test_colorsteps_formats_fixed_labels_at_explicit_limits():
    scale = scale_color_binned(
        breaks=[0, 5],
        labels=["lower", "middle"],
        limits=(0, 10),
        show_limits=True,
    )
    guide = guide_colorsteps(title="value")

    with pytest.warns(PlotnineWarning, match="Fixed labels"):
        guide.train(scale)

    assert guide.key["label"].tolist() == ["lower", "middle", "10"]


def test_colorsteps_formats_limits_after_filtering_fixed_breaks():
    scale = scale_color_binned(
        breaks=[-5, 5, 15],
        labels=["low", "middle", "high"],
        limits=(0, 10),
        show_limits=True,
    )
    guide = guide_colorsteps(title="value")

    with pytest.warns(PlotnineWarning, match="Fixed labels"):
        guide.train(scale)

    assert guide.key["label"].tolist() == ["0", "middle", "10"]


@pytest.mark.parametrize("breaks", [True, lambda limits, n: [5]])
def test_colorsteps_formats_added_limits_for_generated_breaks(breaks):
    scale = scale_color_binned(
        breaks=breaks,
        labels=["middle"],
        limits=(0, 10),
        n_breaks=1,
        nice_breaks=False,
        show_limits=True,
    )
    guide = guide_colorsteps(title="value")

    with pytest.warns(PlotnineWarning, match="Fixed labels"):
        guide.train(scale)

    assert guide.key["label"].tolist() == ["0", "middle", "10"]


def test_colorsteps_trains_from_interval_valued_discrete_scale():
    values = pd.IntervalIndex.from_breaks([0, 1, 3])
    scale = scale_color_manual(values=["red", "blue"])
    scale.train(cast("Any", values))
    guide = guide_colorsteps(title="value")

    guide.train(scale)

    assert guide.bar["color"].tolist() == ["red", "blue"]
    npt.assert_allclose(guide.bar["value"], [0.5, 2])
    npt.assert_allclose(guide.key["value"], [1])


def test_colorsteps_uses_equal_or_proportional_segment_locations():
    scale = scale_color_binned(
        breaks=[1],
        limits=(0, 3),
        show_limits=True,
    )
    elements = SimpleNamespace(key_height=120)
    equal = guide_colorsteps(title="value", even_steps=True)
    proportional = guide_colorsteps(title="value", even_steps=False)
    equal.train(scale)
    proportional.train(scale)

    typed_elements = cast("GuideElementsColorbar", elements)
    npt.assert_allclose(equal._tick_locations(typed_elements), [0, 60, 120])
    npt.assert_allclose(
        proportional._tick_locations(typed_elements), [0, 40, 120]
    )


@pytest.mark.parametrize(
    ("even_steps", "direction", "reverse"),
    [
        (True, "vertical", False),
        (False, "vertical", True),
        (True, "horizontal", False),
    ],
)
def test_colorsteps_draws_in_both_orientations(even_steps, direction, reverse):
    p = (
        ggplot(data, aes("x", "y", color="z"))
        + geom_point(size=4)
        + scale_color_binned(breaks=[1], limits=(0, 3))
        + guides(
            color=guide_colorsteps(
                even_steps=even_steps,
                direction=direction,
                reverse=reverse,
            )
        )
    )

    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]


def test_bins_trains_midpoint_keys_and_boundary_labels():
    scale = scale_shape_binned(breaks=[5], limits=(0, 10))
    guide = guide_bins(title="value")

    result = guide.train(scale)

    assert result is guide
    assert guide.key["shape"].tolist() == ["o", "^"]
    assert guide._boundary_labels == ["5"]
    npt.assert_allclose(guide._boundary_values, [5])


def test_bins_inherits_limit_labels_from_scale():
    scale = scale_shape_binned(
        breaks=[5],
        limits=(0, 10),
        show_limits=True,
    )
    guide = guide_bins(title="value")

    guide.train(scale)

    assert guide._boundary_labels == ["0", "5", "10"]


def test_bins_trains_from_interval_valued_discrete_scale():
    values = pd.IntervalIndex.from_breaks([0, 1, 3])
    scale = scale_shape_manual(values=["o", "s"])
    scale.train(cast("Any", values))
    guide = guide_bins(title="value")

    guide.train(scale)

    assert guide.key["shape"].tolist() == ["o", "s"]
    assert guide._boundary_labels == ["1.0"]


@pytest.mark.parametrize(
    ("direction", "reverse"),
    [("vertical", False), ("horizontal", True)],
)
def test_bins_draws_geom_keys_in_both_orientations(direction, reverse):
    p = (
        ggplot(data, aes("x", "y", shape="z"))
        + geom_point(size=4)
        + scale_shape_binned(breaks=[1], limits=(0, 3))
        + guides(shape=guide_bins(direction=direction, reverse=reverse))
    )

    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]


def test_bins_reuses_legend_geom_key_overrides():
    p = (
        ggplot(data, aes("x", "y", shape="z"))
        + geom_point()
        + scale_shape_binned(breaks=[0.5], limits=(0, 1))
        + guides(shape=guide_bins(override_aes={"size": 9}))
    )

    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]

    ((_, trained),) = p.guides._lookup.values()
    trained = cast("guide_bins", trained)
    assert all(
        (params.data["size"] == 9).all()
        for params in trained._layer_parameters
    )


@pytest.mark.parametrize(
    ("direction", "position"),
    [("vertical", "top"), ("horizontal", "left")],
)
def test_bins_rejects_text_positions_for_other_orientation(
    direction: "Orientation", position: str
) -> None:
    p = (
        ggplot(data, aes("x", "y", shape="z"))
        + geom_point()
        + scale_shape_binned()
        + guides(shape=guide_bins(direction=direction))
        + theme(legend_text_position=position)
    )
    with pytest.raises(PlotnineError, match="legend_text_position"):
        p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]


def test_bins_applies_axis_theme() -> None:
    p = (
        ggplot(data, aes("x", "y", shape="z"))
        + geom_point(size=20)
        + scale_shape_binned()
        + theme(
            legend_axis_line=element_line(color="green"),
            legend_text_position="left",
            legend_text=element_text(color="red", margin={"r": 10}),
            legend_ticks=element_line(color="blue"),
            legend_ticks_length=0.4,
        )
    )
    assert p == "bins_axis_theme"


def test_bins_contains_large_keys_and_labels() -> None:
    labels = [
        "Lower boundary\nwith a long label",
        "Middle boundary\nwith a long label",
        "Upper boundary\nwith a long label",
    ]
    p = (
        ggplot(data, aes("x", "y", size="z"))
        + geom_point()
        + scale_size_binned(range=(4, 20), breaks=[0, 4.5, 9], labels=labels)
        + guides(size=guide_bins(direction="horizontal"))
        + theme(
            legend_position="bottom",
            legend_text=element_text(size=24),
            legend_key_width=220,
            figure_size=(15, 5),
        )
    )
    assert p == "bins_large_keys_and_labels"


def test_colorsteps_draws_equal_segments():
    p = (
        ggplot(data, aes("x", "y", color="z"))
        + geom_point(size=4)
        + scale_color_binned()
    )

    assert p == "colorsteps_equal"


def test_colorsteps_draws_proportional_segments():
    p = (
        ggplot(data, aes("x", "y", color="z"))
        + geom_point(size=4)
        + scale_color_binned(breaks=[1, 2, 4, 8])
        + guides(color=guide_colorsteps(even_steps=False))
    )

    assert p == "colorsteps_proportional"


def test_colorsteps_draws_horizontally():
    p = (
        ggplot(data, aes("x", "y", color="z"))
        + geom_point(size=4)
        + scale_color_binned()
        + guides(color=guide_colorsteps(direction="horizontal"))
    )

    assert p == "colorsteps_horizontal"


def test_bins_draws_shape_keys():
    p = (
        ggplot(data, aes("x", "y", shape="z"))
        + geom_point(size=4)
        + scale_shape_binned()
    )

    assert p == "bins_shape"


def test_bins_draws_horizontally():
    p = (
        ggplot(data, aes("x", "y", shape="z"))
        + geom_point(size=4)
        + scale_shape_binned()
        + guides(shape=guide_bins(direction="horizontal"))
    )

    assert p == "bins_horizontal"
