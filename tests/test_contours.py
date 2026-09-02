import numpy as np
import pandas as pd
import pytest

from plotnine.exceptions import PlotnineError, PlotnineWarning
from plotnine.stats.contours import (
    band_labels,
    contour_bands,
    contour_breaks,
    contour_lines,
    drop_duplicate_xy,
    estimate_grid_angle,
    rotate_xy,
    xyz_to_grid,
)


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


def peak_grid():
    x = np.linspace(-3, 3, 40)
    y = np.linspace(-3, 3, 40)
    X, Y = np.meshgrid(x, y)
    return x, y, np.exp(-(X**2 + Y**2))


def test_band_labels_use_right_closed_intervals():
    assert band_labels(np.array([0.0, 0.5, 1.0])) == ["(0, 0.5]", "(0.5, 1]"]


def test_band_labels_increase_precision_until_distinct():
    labels = band_labels(np.array([1.0001, 1.0002, 1.0003]))
    assert labels[0] != labels[1]


def test_equal_breaks_cannot_have_distinct_labels():
    with pytest.raises(PlotnineError):
        band_labels(np.array([1.0, 1.0, 2.0]))


def test_contour_lines_record_levels_and_groups():
    x, y, Z = peak_grid()
    df = contour_lines(x, y, Z, np.array([0.2, 0.6]), 1)
    assert set(df["level"]) == {0.2, 0.6}
    assert df["nlevel"].max() == 1
    # Draw each closed contour as a separate group.
    assert df.groupby("group").ngroups == 2


def test_empty_contour_lines_preserve_schema():
    x, y, Z = peak_grid()
    with pytest.warns(PlotnineWarning):
        df = contour_lines(x, y, Z, np.array([5.0]), 1)
    assert len(df) == 0
    assert list(df.columns) == ["x", "y", "level", "nlevel", "piece", "group"]


def test_contour_band_records_hole_rings():
    x, y, Z = peak_grid()
    df = contour_bands(x, y, Z, np.array([0.0, 0.2, 1.0]), 1)
    # The lower band contains an exterior ring and a hole around the peak.
    lower = df[df["level"] == df["level"].cat.categories[0]]
    assert set(lower["subgroup"]) == {0, 1}


def test_contour_bands_record_ordered_levels_and_bounds():
    x, y, Z = peak_grid()
    breaks = np.array([0.0, 0.2, 1.0])
    df = contour_bands(x, y, Z, breaks, 1)
    assert df["level"].cat.ordered
    assert list(df["level"].cat.categories) == band_labels(breaks)
    assert set(df["level_low"]) <= {0.0, 0.2}
    assert set(df["level_high"]) <= {0.2, 1.0}
    assert (df["level_mid"] == (df["level_low"] + df["level_high"]) / 2).all()


def test_duplicate_coordinates_keep_last_value():
    data = pd.DataFrame({"x": [1, 1, 2], "y": [1, 1, 2], "z": [1.0, 2.0, 3.0]})
    with pytest.warns(PlotnineWarning):
        result = drop_duplicate_xy(data)
    assert len(result) == 2
    # Grid population order makes the last duplicate win.
    assert result["z"].tolist() == [2.0, 3.0]


def test_unique_coordinates_remain_unchanged():
    data = pd.DataFrame({"x": [1, 2], "y": [1, 2], "z": [1.0, 2.0]})
    assert len(drop_duplicate_xy(data)) == 2


def test_axis_aligned_grid_has_zero_angle():
    x, y = np.meshgrid(np.arange(5), np.arange(5))
    assert estimate_grid_angle(x.ravel(), y.ravel()) == 0


def test_rotated_grid_angle_is_recovered():
    x, y = np.meshgrid(np.arange(5.0), np.arange(5.0))
    rx, ry = rotate_xy(x.ravel(), y.ravel(), np.pi / 6)
    assert estimate_grid_angle(rx, ry) == pytest.approx(np.pi / 6)


def test_rotation_round_trip_restores_coordinates():
    x = np.array([0.0, 1.0, 2.0])
    y = np.array([0.0, 1.0, 2.0])
    rx, ry = rotate_xy(x, y, 0.4)
    ux, uy = rotate_xy(rx, ry, -0.4)
    assert ux == pytest.approx(x)
    assert uy == pytest.approx(y)


def test_zero_angle_preserves_coordinates():
    x = np.array([0.0, 1.0])
    y = np.array([2.0, 3.0])
    rx, ry = rotate_xy(x, y, 0)
    assert rx.tolist() == [0.0, 1.0]
    assert ry.tolist() == [2.0, 3.0]
