import numpy as np
import pandas as pd
import pytest
from matplotlib.collections import PolyCollection

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
from plotnine.exceptions import PlotnineError
from plotnine.stats.binning import freedman_diaconis_bins

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


def test_col_hatch():
    df = pd.DataFrame(
        {"x": ["a", "b", "c"], "y": [3, 5, 2], "g": ["u", "v", "w"]}
    )
    p = ggplot(df, aes("x", "y", fill="g", hatch="g")) + geom_col(
        color="black"
    )

    assert p == "col_hatch"


def test_col_hatch_continuous_raises():
    df = pd.DataFrame({"x": [1, 2], "y": [1, 2], "g": [0.1, 0.2]})
    p = ggplot(df, aes("x", "y")) + geom_col(aes(hatch="g"))
    with pytest.raises(PlotnineError, match="Cannot interpret hatch"):
        p.draw()


def test_col_no_hatch_no_overlays():
    df = pd.DataFrame({"x": ["a", "b"], "y": [1, 2]})
    p = ggplot(df, aes("x", "y", fill="x")) + geom_col()
    fig = p.draw()
    cols = [
        c for c in fig.axes[0].collections if isinstance(c, PolyCollection)
    ]
    assert len(cols) == 1
    assert cols[0].get_hatch() is None


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
    out1 = p.layer_data()
    out2 = (p + scale_x_sqrt()).layer_data()
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
