from collections.abc import Sequence
from typing import Any, cast

import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest

from plotnine import aes, geom_bar, ggplot
from plotnine.exceptions import PlotnineError, PlotnineWarning
from plotnine.scales.scale_alpha import scale_alpha_binned
from plotnine.scales.scale_binned import scale_binned
from plotnine.scales.scale_linetype import scale_linetype_binned
from plotnine.scales.scale_shape import scale_shape_binned, unfilled_shapes
from plotnine.scales.scale_size import (
    scale_size_binned,
    scale_size_binned_area,
)
from plotnine.scales.scale_xy import scale_x_binned, scale_y_binned


@pytest.mark.parametrize(
    ("right", "expected"),
    [
        (True, [0.25, 0.25, 0.75]),
        (False, [0.25, 0.75, 0.75]),
    ],
)
def test_binned_scale_maps_boundary_values(right, expected):
    scale = scale_binned(
        breaks=[5],
        limits=(0, 10),
        right=right,
        guide=None,
        aesthetics=["color"],
    )
    scale.palette = cast("Any", np.asarray)

    result = scale.map(np.array([0, 5, 10]))

    npt.assert_allclose(result, expected)


def test_binned_scale_squishes_out_of_bounds_values():
    scale = scale_binned(
        breaks=[5],
        limits=(0, 10),
        guide=None,
        aesthetics=["color"],
    )
    scale.palette = cast("Any", np.asarray)

    result = scale.map(np.array([-1, 11]))

    npt.assert_allclose(result, [0.25, 0.75])


def test_callable_breaks_receive_requested_break_count():
    def breaks(limits: tuple[float, float], n: int) -> Sequence[float]:
        return np.linspace(*limits, n + 2)[1:-1].tolist()

    scale = scale_binned(
        breaks=breaks,
        limits=(0, 10),
        n_breaks=3,
        guide=None,
        aesthetics=["color"],
    )

    npt.assert_allclose(scale.get_breaks(), [2.5, 5, 7.5])


def test_disabling_nice_breaks_generates_the_exact_requested_count():
    scale = scale_binned(
        limits=(0, 10),
        n_breaks=3,
        nice_breaks=False,
        guide=None,
        aesthetics=["color"],
    )

    npt.assert_allclose(scale.get_breaks(), [2.5, 5, 7.5])


def test_inferred_limits_give_terminal_bins_equal_widths():
    scale = scale_binned(
        breaks=[2, 4],
        guide=None,
        aesthetics=["color"],
    )
    scale.train([1, 5])

    partition = scale._resolve_partition()

    npt.assert_allclose(partition.limits, [0, 6])
    npt.assert_allclose(partition.boundaries, [0, 2, 4, 6])


def test_constant_range_creates_finite_bins():
    scale = scale_binned(
        breaks=[],
        guide=None,
        aesthetics=["color"],
    )
    scale.train([5, 5])

    partition = scale._resolve_partition()

    assert partition.limits[0] < 5 < partition.limits[1]
    assert np.all(np.isfinite(partition.boundaries))


@pytest.mark.parametrize("n_breaks", [0, -1, 1.5, True])
def test_requested_break_count_must_be_a_positive_integer(n_breaks):
    with pytest.raises(PlotnineError, match="positive integer"):
        scale_binned(
            n_breaks=n_breaks,
            guide=None,
            aesthetics=["color"],
        )


def test_requested_break_count_warns_when_callable_cannot_accept_it():
    scale = scale_binned(
        breaks=lambda limits: [np.mean(limits)],
        limits=(0, 10),
        n_breaks=3,
        guide=None,
        aesthetics=["color"],
    )

    with pytest.warns(PlotnineWarning, match=r"Ignoring `n_breaks`"):
        scale.get_breaks()


def test_binned_scale_maps_transformed_values():
    scale = scale_binned(
        breaks=[10],
        limits=(1, 100),
        trans="log10",
        guide=None,
        aesthetics=["color"],
    )
    scale.palette = cast("Any", np.asarray)

    result = scale.map(np.log10([1, 10, 100]))

    npt.assert_allclose(result, [0.25, 0.25, 0.75])


def test_fixed_labels_follow_breaks_within_the_limits():
    scale = scale_binned(
        breaks=[-5, 5, 15],
        labels=["low", "middle", "high"],
        limits=(0, 10),
        guide=None,
        aesthetics=["color"],
    )

    assert scale.get_labels(scale.get_breaks()) == ["middle"]


def test_training_discards_resolved_bins():
    scale = scale_binned(
        breaks=[5],
        guide=None,
        aesthetics=["color"],
    )
    scale.train([0, 10])
    first = scale._resolve_partition()

    scale.train([-10, 10])
    second = scale._resolve_partition()

    assert first is not second
    assert first.limits != second.limits


def test_binned_scale_maps_missing_values_to_na_value():
    scale = scale_binned(
        breaks=[5],
        limits=(0, 10),
        na_value="missing",
        guide=None,
        aesthetics=["color"],
    )
    scale.palette = cast("Any", lambda x: ["low", "high"])

    result = scale.map(np.array([1, np.nan, 9]))

    assert list(result) == ["low", "missing", "high"]


def test_binned_scale_rejects_non_numeric_training_data():
    scale = scale_binned(guide=None, aesthetics=["color"])

    with pytest.raises(PlotnineError, match="continuous data"):
        scale.train(cast("Any", ["a", "b"]))


def test_omitting_breaks_disables_a_non_position_guide():
    scale = scale_binned(
        breaks=None,
        limits=(0, 10),
        aesthetics=["color"],
    )

    assert scale.guide is None


def test_binned_position_restores_bar_coordinates_after_statistics():
    data = pd.DataFrame({"x": [1, 2, 8, 9]})
    p = (
        ggplot(data, aes("x"))
        + geom_bar()
        + scale_x_binned(breaks=[5], limits=(0, 10))
    )

    layer = p.layer_data().sort_values("x")

    npt.assert_allclose(layer["x"], [2.5, 7.5])
    npt.assert_allclose(layer["count"], [2, 2])
    npt.assert_allclose(layer["xmin"], [0.25, 5.25])
    npt.assert_allclose(layer["xmax"], [4.75, 9.75])


def test_binned_position_keeps_bins_across_the_statistical_phase():
    scale = scale_x_binned(breaks=[5], limits=(0, 10))
    scale.train([1, 2, 8, 9])
    before = scale._resolve_partition()

    mapped = scale.map(np.array([1, 5, 9]))
    scale.reset()
    scale.train(mapped)

    assert scale._resolve_partition() is before
    npt.assert_allclose(scale.map(np.array([1, 1.5, 2])), [2.5, 5, 7.5])


def test_binned_y_scale_maps_each_position_aesthetic():
    scale = scale_y_binned(breaks=[5], limits=(0, 10))
    scale.train([1, 9])

    npt.assert_array_equal(scale.map(np.array([1, 9])), [1, 2])
    assert {"y", "ymin", "ymax", "lower", "middle", "upper"} <= set(
        scale.aesthetics
    )


@pytest.mark.parametrize(
    "scale",
    [
        scale_alpha_binned(breaks=[0.5], limits=(0, 1)),
        scale_size_binned(breaks=[0.5], limits=(0, 1)),
        scale_size_binned_area(breaks=[0.5], limits=(0, 1)),
        scale_shape_binned(breaks=[0.5], limits=(0, 1)),
        scale_linetype_binned(breaks=[0.5], limits=(0, 1)),
    ],
)
def test_aesthetic_binned_scales_map_each_bin_to_one_value(scale):
    result = scale.map(np.array([0.1, 0.2, 0.8, 0.9]))

    assert result[0] == result[1]
    assert result[2] == result[3]
    assert result[0] != result[2]


def test_alpha_binned_honours_range():
    scale = scale_alpha_binned(
        range=(0.2, 0.8),
        breaks=[0.5],
        limits=(0, 1),
    )

    npt.assert_allclose(scale.map([0.1, 0.9]), [0.35, 0.65])


def test_size_binned_area_honours_max_size():
    scale = scale_size_binned_area(
        max_size=8,
        breaks=[2],
        limits=(1, 3),
    )

    npt.assert_allclose(
        scale.map([1.1, 2.9]),
        np.sqrt([0.5, 5 / 6]) * 8,
    )


def test_shape_binned_honours_unfilled():
    scale = scale_shape_binned(
        unfilled=True,
        breaks=[0.5],
        limits=(0, 1),
    )

    assert set(scale.map([0.1, 0.9])) <= set(unfilled_shapes)
