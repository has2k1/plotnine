import numpy as np
import pandas as pd
import pytest

from plotnine.exceptions import PlotnineError
from plotnine.stats.contours import contour_breaks, xyz_to_grid


def test_default_breaks_span_surface_range():
    breaks = contour_breaks((0, 0.037))
    assert len(breaks) > 2
    assert breaks.min() <= 0
    assert breaks.max() >= 0.037


def test_explicit_breaks_are_preserved():
    breaks = contour_breaks((0, 10), breaks=[1, 2, 3])
    assert list(breaks) == [1, 2, 3]


def test_break_function_receives_range_and_width():
    breaks = contour_breaks((0, 10), binwidth=2, breaks=lambda r, w: [r[0], w])
    assert list(breaks) == [0, 2]


def test_binwidth_generates_even_breaks():
    breaks = contour_breaks((0.5, 9.5), binwidth=2)
    assert list(breaks) == [0, 2, 4, 6, 8, 10]


def test_bin_count_spans_surface_range():
    # Each band needs a lower and upper break.
    breaks = contour_breaks((0, 10), bins=5)
    assert len(breaks) >= 6
    assert breaks.min() <= 0
    assert breaks.max() >= 10


def test_one_bin_has_two_boundary_breaks():
    breaks = contour_breaks((0.5, 9.5), bins=1)
    assert len(breaks) == 2
    assert breaks[0] <= 0.5 and breaks[1] >= 9.5


def test_non_positive_bin_count_raises():
    with pytest.raises(PlotnineError):
        contour_breaks((0, 10), bins=0)


def test_non_positive_binwidth_raises():
    with pytest.raises(PlotnineError):
        contour_breaks((0, 10), binwidth=0)

    with pytest.raises(PlotnineError):
        contour_breaks((0, 10), binwidth=-1)


def test_xyz_values_are_arranged_on_a_grid():
    data = pd.DataFrame(
        {
            "x": [1, 2, 1, 2],
            "y": [10, 10, 20, 20],
            "z": [1.0, 2.0, 3.0, 4.0],
        }
    )
    x, y, Z = xyz_to_grid(data)
    assert list(x) == [1, 2]
    assert list(y) == [10, 20]
    assert Z.tolist() == [[1.0, 2.0], [3.0, 4.0]]


def test_missing_grid_cell_becomes_nan():
    data = pd.DataFrame(
        {
            "x": [1, 2, 1],
            "y": [10, 10, 20],
            "z": [1.0, 2.0, 3.0],
        }
    )
    _, _, Z = xyz_to_grid(data)
    assert np.isnan(Z[1, 1])
