import numpy as np
import pandas as pd
from scipy.stats import norm

from plotnine import aes, geom_qq, geom_qq_line, ggplot

random_state = np.random.RandomState(1234567890)
normal_data = pd.DataFrame({"x": random_state.normal(size=100)})


def test_normal():
    p = ggplot(normal_data, aes(sample="x")) + geom_qq()
    # Roughly a straight line of points through the origin
    assert p == "normal"


def test_normal_with_line():
    p = ggplot(normal_data, aes(sample="x")) + geom_qq() + geom_qq_line()
    # Roughly a straight line of points through the origin
    assert p == "normal_with_line"


def test_line_through_sample_quartiles():
    # The line passes through the quartiles of the sample computed
    # with R's default quantile type, as in ggplot2
    data = pd.DataFrame({"x": [1.0, 2, 3, 4, 10]})
    p = ggplot(data, aes(sample="x")) + geom_qq_line()
    line = p.layer_data()
    slope = np.diff(line["y"])[0] / np.diff(line["x"])[0]
    intercept = line["y"].iloc[0] - slope * line["x"].iloc[0]

    x_coords = norm.ppf([0.25, 0.75])
    y_coords = slope * x_coords + intercept
    np.testing.assert_allclose(y_coords, [2, 4])
