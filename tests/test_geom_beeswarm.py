import numpy as np
import numpy.testing as npt
import pandas as pd

from plotnine import aes, coord_flip, geom_beeswarm, geom_violin, ggplot
from plotnine.stats.stat_beeswarm import van_der_corput

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
