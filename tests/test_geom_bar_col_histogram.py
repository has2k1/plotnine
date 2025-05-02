import numpy as np
import pandas as pd

from plotnine import (
    aes,
    after_stat,
    geom_bar,
    geom_col,
    geom_histogram,
    geom_text,
    ggplot,
    scale_x_sqrt,
)
from plotnine.stats.binning import freedman_diaconis_bins

from .conftest import layer_data

n = 10  # Some even number greater than 2

# ladder: 0 1 times, 1 2 times, 2 3 times, ...
data = pd.DataFrame(
    {
        "x": np.repeat(range(n + 1), range(n + 1)),
        "z": np.repeat(range(n // 2), range(3, n * 2, 4)),
    }
)


def test_bar_count():
    p = ggplot(data, aes("x")) + geom_bar(aes(fill="factor(z)"))

    assert p == "bar-count"


def test_col():
    # The color indicates reveals the edges and the stacking
    # that is going on.
    p = ggplot(data) + geom_col(aes("x", "z", fill="factor(z)"), color="black")

    assert p == "col"


def test_col_just():
    data = pd.DataFrame({"x": range(1, 4), "y": range(1, 4)})
    p = (
        ggplot(data, aes("x", "y"))
        + geom_col(just=0, fill="red", width=1 / 3)  # left
        + geom_col(just=1, fill="blue", width=1 / 3)  # right
        + geom_col(just=0.5, fill="green", width=1 / 3, alpha=0.7)  # center
    )
    assert p == "col_just"


def test_histogram_count():
    p = ggplot(data, aes("x")) + geom_histogram(aes(fill="factor(z)"), bins=n)

    assert p == "histogram-count"


def test_scale_transformed_breaks():
    data = pd.DataFrame({"x": np.repeat(range(1, 5), range(1, 5))})
    p = ggplot(data, aes("x")) + geom_histogram(breaks=[1, 2.5, 4])
    out1 = layer_data(p)
    out2 = layer_data(p + scale_x_sqrt())
    np.testing.assert_allclose(out1.xmin, [1, 2.5])
    np.testing.assert_allclose(out2.xmin, np.sqrt([1, 2.5]))


def test_stat_count_int():
    data = pd.DataFrame({"x": ["a", "b"], "weight": [1, 2]})

    p = (
        ggplot(data)
        + aes(x="x", weight="weight", fill="x")
        + geom_bar()
        + geom_text(aes(label=after_stat("count")), stat="count")
    )

    assert p == "stat-count-int"


def test_stat_count_float():
    data = pd.DataFrame({"x": ["a", "b"], "weight": [1.5, 2.5]})

    p = (
        ggplot(data)
        + aes(x="x", weight="weight", fill="x")
        + geom_bar()
        + geom_text(aes(label=after_stat("count")), stat="count")
    )

    assert p == "stat-count-float"


def test_freedman_diaconis_bins():
    a1 = np.arange(1, 98, dtype=float)
    a2 = np.arange(100, dtype=float)
    a2[[0, 99]] = np.nan
    iqr1 = freedman_diaconis_bins(a1)
    iqr2 = freedman_diaconis_bins(a2)
    assert iqr1 == iqr2


def test_histogram_weights():
    data = pd.DataFrame(
        {
            "x": list(range(1, 6)),
            "w": list(range(1, 6)),
        }
    )

    p = ggplot(data, aes("x", weight="w")) + geom_histogram(bins=5)
    assert p == "histogram_weights"
