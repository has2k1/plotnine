import numpy as np
import numpy.testing as npt
import pandas as pd

from plotnine import aes, coord_flip, geom_beeswarm, geom_violin, ggplot
from plotnine.stats._swarm import (
    _alternate_extremes,
    frowney_offset,
    smiley_offset,
    van_der_corput,
)

n = 50
random_state = np.random.RandomState(123)
uni = random_state.chisquare(17, n)
bi = np.hstack(
    [random_state.normal(4, 0.25, n), random_state.normal(6, 0.25, n)]
)
tri = np.hstack(
    [
        random_state.normal(4, 0.125, n),
        random_state.normal(5, 0.125, n),
        random_state.normal(6, 0.125, n),
    ]
)

cats = ["uni", "bi", "tri"]

data = pd.DataFrame(
    {
        "dist": pd.Categorical(
            np.repeat(cats, [len(uni), len(bi), len(tri)]), categories=cats
        ),
        "value": np.hstack([uni, bi, tri]),
    }
)


def test_scale_area():
    p = (
        ggplot(data, aes("dist", "value"))
        + geom_violin(scale="area")
        + geom_beeswarm(scale="area")
    )

    assert p == "scale_area"


def test_scale_count():
    p = (
        ggplot(data, aes("dist", "value"))
        + geom_violin(scale="count")
        + geom_beeswarm(scale="count")
    )

    assert p == "scale_count"


def test_coord_flip():
    p = (
        ggplot(data, aes("dist", "value"))
        + geom_violin(scale="area")
        + geom_beeswarm(scale="area")
        + coord_flip()
    )

    assert p == "scale_area+coord_flip"


def test_method_counts():
    p = (
        ggplot(data, aes("dist", "value"))
        + geom_violin()
        + geom_beeswarm(method="counts")
    )

    assert p == "method_counts"


def test_style():
    p = (
        ggplot(data, aes("dist", "value"))
        + geom_violin(style="left-right")
        + geom_beeswarm(style="left-right")
    )

    assert p == "style"


def test_equal_points_not_collapsed():
    # Two identical y-values must not collapse to the same x position.
    df = pd.DataFrame({"x": [1, 1]})
    p = ggplot(df, aes(y="x", x=1)) + geom_beeswarm()
    p.draw_test()


# --- van_der_corput ---


def test_van_der_corput_n0():
    assert len(van_der_corput(0)) == 0


def test_van_der_corput_n1():
    npt.assert_array_equal(van_der_corput(1), [0.0])


def test_van_der_corput_n7():
    npt.assert_array_almost_equal(
        van_der_corput(7), [0.5, 0.25, 0.75, 0.125, 0.625, 0.375, 0.0]
    )


def test_van_der_corput_first_element_closest_to_half():
    # The rotation guarantees seq[0] is the value in the raw sequence
    # closest to 0.5, placing the minimum-y point at the swarm centre.
    for n in [2, 3, 8, 50]:
        seq = van_der_corput(n)
        assert seq[0] == seq[np.argmin(np.abs(seq - 0.5))]


def test_van_der_corput_space_filling():
    # After k points the maximum gap between consecutive sorted values
    # should shrink as k grows.
    result = van_der_corput(32)
    prev_max_gap = np.inf
    for k in [2, 4, 8, 16, 32]:
        sorted_pts = np.sort(result[:k])
        gaps = np.diff(np.concatenate([[0], sorted_pts, [1]]))
        max_gap = gaps.max()
        assert max_gap < prev_max_gap
        prev_max_gap = max_gap


# --- _alternate_extremes ---


def test_alternate_extremes_mirrors_ascending_and_descending():
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    smiley = _alternate_extremes(y, ascending=True)
    frowney = _alternate_extremes(y, ascending=False)
    npt.assert_array_almost_equal(smiley, [0.5, 0.75, 0.25, 1.0, 0.0])
    npt.assert_array_almost_equal(frowney, [0.0, 1.0, 0.25, 0.75, 0.5])


def test_alternate_extremes_ties_collapse():
    # Equal values have no directional ordering, so both rankings must
    # produce the same positions.
    y = np.array([5.0] * 8)
    smiley = _alternate_extremes(y, ascending=True)
    frowney = _alternate_extremes(y, ascending=False)
    npt.assert_array_equal(smiley, frowney)


def test_alternate_extremes_single_point():
    npt.assert_array_equal(_alternate_extremes(np.array([3.0]), True), [0.5])


# --- smiley_offset / frowney_offset ---

_extremes_params = {
    "bw": "nrd0",
    "adjust": 1,
    "kernel": "gau",
    "cut": 0,
    "gridsize": None,
    "clip": (-np.inf, np.inf),
    "bounds": (-np.inf, np.inf),
}


def test_smiley_offset_bounded_and_shaped():
    df = pd.DataFrame(
        {
            "group": [1] * 10,
            "y": np.arange(10, dtype=float),
            "width_fraction": np.ones(10),
        }
    )
    offset = smiley_offset(df, 0.9, "width_fraction", _extremes_params)
    assert len(offset) == 10
    assert (offset.abs() <= 0.9 / 2 + 1e-9).all()


def test_frowney_offset_bounded_and_shaped():
    df = pd.DataFrame(
        {
            "group": [1] * 10,
            "y": np.arange(10, dtype=float),
            "width_fraction": np.ones(10),
        }
    )
    offset = frowney_offset(df, 0.9, "width_fraction", _extremes_params)
    assert len(offset) == 10
    assert (offset.abs() <= 0.9 / 2 + 1e-9).all()


def test_smiley_offset_independent_groups():
    # Each group is binned and ranked independently. Removing one group
    # must not change another group's offsets.
    df = pd.DataFrame(
        {
            "group": [1] * 10 + [2] * 3,
            "y": list(np.arange(10, dtype=float)) + [0.0, 1.0, 2.0],
            "width_fraction": np.ones(13),
        }
    )
    combined = smiley_offset(df, 0.9, "width_fraction", _extremes_params)
    solo = smiley_offset(df.iloc[10:], 0.9, "width_fraction", _extremes_params)
    npt.assert_array_almost_equal(combined.to_numpy()[10:], solo.to_numpy())
