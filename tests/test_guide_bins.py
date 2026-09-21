from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

import numpy.testing as npt
import pandas as pd
import pytest

from plotnine import aes, geom_point, ggplot, guides
from plotnine.exceptions import PlotnineError, PlotnineWarning
from plotnine.guides._binned import _GuideIntervals
from plotnine.guides.guide_colorsteps import guide_colorsteps
from plotnine.scales.scale_color import scale_color_binned
from plotnine.scales.scale_manual import scale_color_manual

if TYPE_CHECKING:
    from plotnine.guides.guide_colorbar import GuideElementsColorbar


def test_colorsteps_trains_segments_and_boundary_labels():
    scale = scale_color_binned(breaks=[5], limits=(0, 10))
    guide = guide_colorsteps(title="value")

    result = guide.train(scale)

    assert result is guide
    npt.assert_allclose(guide.key["value"], [5])
    assert guide.key["label"].tolist() == ["5"]
    npt.assert_allclose(guide.bar["value"], [2.5, 7.5])
    assert guide.bar["color"].tolist() == ["#3b528b", "#5ec962"]
    npt.assert_allclose(guide._intervals.boundaries, [0, 5, 10])


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


@pytest.mark.parametrize(
    "values",
    [
        pd.IntervalIndex.from_breaks([0, 1, 3]),
        ["(0, 1]", "(1, 3]"],
    ],
)
def test_guide_intervals_accept_contiguous_discrete_intervals(values):
    scale = scale_color_manual(values=["red", "blue"])
    scale.train(values)

    intervals = _GuideIntervals.make(scale)

    npt.assert_allclose(intervals.boundaries, [0, 1, 3])
    npt.assert_allclose(intervals.midpoints, [0.5, 2])


@pytest.mark.parametrize(
    "values",
    [
        ["not an interval", "(1, 3]"],
        ["(0, 2]", "(1, 3]"],
        ["(0, 1]", "(2, 3]"],
    ],
)
def test_guide_intervals_reject_invalid_discrete_intervals(values):
    scale = scale_color_manual(values=["red", "blue"])
    scale.train(values)

    with pytest.raises(PlotnineError, match="interval breaks"):
        _GuideIntervals.make(scale)


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
    data = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "z": [0, 1, 3]})
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
