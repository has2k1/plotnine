import numpy as np
import pandas as pd
import pytest

from plotnine import (
    aes,
    after_stat,
    geom_col,
    geom_crossbar,
    geom_point,
    ggplot,
    scale_x_log10,
    scale_y_log10,
    stage,
    stat_bin_2d,
    stat_ecdf,
    stat_function,
)
from plotnine.mapping.aes import make_labels

data = pd.DataFrame(
    {
        "x": pd.Categorical(["b", "d", "c", "a"], ordered=True),
        "y": [1, 2, 3, 4],
    }
)


data = pd.DataFrame(
    {
        "x": pd.Categorical(["b", "d", "c", "a"], ordered=True),
        "y": [1, 2, 3, 4],
    }
)


def test_reorder():
    p = (
        ggplot(data, aes("reorder(x, y)", "y", fill="reorder(x, y)"))
        + geom_col()
    )
    assert p == "reorder"


def test_reorder_index():
    # The dataframe is created with ordering according to the y
    # variable. So the x index should be ordered acc. to y too
    p = ggplot(data, aes("reorder(x, x.index)", "y")) + geom_col()
    assert p == "reorder_index"


def test_labels_series():
    p = ggplot(data, aes(x=data.x, y=data.y)) + geom_col()
    assert p.labels.x == "x"
    assert p.labels.y == "y"


def test_labels_lists():
    p = ggplot(data, aes(x=[1, 2, 3], y=[1, 2, 3])) + geom_col()
    assert p.labels.x is None
    assert p.labels.y is None


def test_irregular_shapes():
    import matplotlib.path as mpath

    five_point_astericks = (5, 2, 60)
    house = ((-2, -4), (-2, -1), (0, 1), (2, -1), (2, -4), (-2, -4))

    star = mpath.Path.unit_regular_star(6)
    circle = mpath.Path.unit_circle()

    cut_star = mpath.Path(
        vertices=[*circle.vertices, *star.vertices[::-1]],  # pyright: ignore[reportGeneralTypeIssues,reportIndexIssue,reportArgumentType]
        codes=[*circle.codes, *star.codes],  # pyright: ignore[reportOptionalIterable,reportGeneralTypeIssues]
    )

    p = (
        ggplot(data, aes("x", "y"))
        + geom_point(shape=five_point_astericks, size=10)
        + geom_point(aes(y="y-.5"), shape=house, size=10)
        + geom_point(aes(y="y-1"), shape=cut_star, size=10)
    )

    assert p == "irregular_shapes"


class TestTransScale:
    df1 = pd.DataFrame({"var": np.arange(1, 11) / 10})

    def test_stat_function(self):
        p = (
            ggplot(self.df1, aes(x="var"))
            + geom_point(aes(y="var"))
            + stat_function(fun=lambda x: x)
            + scale_y_log10()
        )
        assert p == "test_stat_function"

    def test_stat_ecdf(self):
        p = (
            ggplot(self.df1, aes(x="var"))
            + geom_point(aes(y="var"))
            + stat_ecdf()
            + scale_y_log10()
        )

        with pytest.warns(RuntimeWarning):
            assert p == "stat_ecdf"

    def test_stat_bin_2d(self):
        data = pd.DataFrame({"x": [1, 10, 100, 1000], "y": range(4)})
        p = ggplot(data, aes("x", "y")) + stat_bin_2d(bins=3) + scale_x_log10()
        assert p == "stat_bin_2d"

    def test_geom_crossbar(self):
        data = pd.DataFrame({"x": "x", "y": np.linspace(0.1, 1, 10)})

        p = (
            ggplot(data, aes("x", "y"))
            + geom_crossbar(
                aes(
                    ymin=after_stat("lower"),
                    y=stage(start="y", after_stat="middle"),
                    ymax=after_stat("upper"),
                ),
                stat="boxplot",
            )
            + scale_y_log10()
        )
        assert p == "geom_crossbar"


def test_make_labels():
    mapping = {"y": "y", "color": ["Treatment"]}
    labels = make_labels(mapping)
    assert labels.color == "Treatment"

    mapping = {"y": "y", "color": ["Treatment", "Control"]}
    labels = make_labels(mapping)
    assert labels.color is None
