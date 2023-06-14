import numpy as np
import pandas as pd
import pytest

from plotnine import qplot
from plotnine.exceptions import PlotnineWarning


def test_scalars():
    p = qplot(x=2, y=3)
    assert p == "scalars"


def test_arrays():
    p = qplot(x=np.arange(5), y=np.arange(5))
    assert p == "arrays"


def test_string_arrays():
    p = qplot(x="np.arange(5)", y="np.arange(5)")
    assert p == "string-arrays"


def test_range():
    p = qplot(x=range(5), y=range(5))

    assert p == "range"


def test_onlyx():
    p = qplot(x="np.arange(5)")
    with pytest.warns(PlotnineWarning):
        assert p == "onlyx"


def test_onlyy():
    p = qplot(y=np.arange(5))

    assert p == "onlyy"


def test_sample():
    p = qplot(sample="np.arange(5)")
    assert p == "sample"


def test_xlim():
    p = qplot(x="np.arange(5)", y="np.arange(5)", xlim=(-10, 10))
    assert p == "xlim"


def test_ylim():
    p = qplot(x="np.arange(5)", y="np.arange(5)", ylim=(-10, 10))
    assert p == "ylim"


def test_multiple_geoms():
    n = 3
    m = 10
    # n stairs of points, each m points high
    data = pd.DataFrame(
        {"x": np.repeat(range(n), m), "y": np.linspace(0, n, n * m)}
    )
    p = qplot("factor(x)", "y", data=data, geom=("boxplot", "point"))
    assert p == "multiple_geoms"


def test_series_labelling():
    data = pd.DataFrame(
        {
            "x_axis_label": [1, 2, 3],
            "y_axis_label": [1, 2, 3],
            "color_label": ["a", "b", "c"],
        }
    )
    p = qplot(data.x_axis_label, data.y_axis_label, color=data.color_label)
    assert p == "series_labelling"
