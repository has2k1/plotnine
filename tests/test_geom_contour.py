import numpy as np
import pandas as pd
import pytest

from plotnine import (
    aes,
    after_stat,
    facet_wrap,
    geom_contour,
    geom_contour_filled,
    ggplot,
)
from plotnine.data import faithfuld
from plotnine.exceptions import PlotnineWarning

p0 = ggplot(faithfuld, aes("waiting", "eruptions", z="density"))


def test_default_contour_lines():
    p = p0 + geom_contour()
    assert p == "contour"


def test_contour_lines_with_bin_count():
    p = p0 + geom_contour(bins=3)
    assert p == "bins"


def test_contour_lines_with_binwidth():
    p = p0 + geom_contour(binwidth=0.01)
    assert p == "binwidth"


def test_contour_lines_with_explicit_breaks():
    p = p0 + geom_contour(breaks=[0.005, 0.01, 0.02])
    assert p == "breaks"


def test_contour_level_can_map_to_colour():
    p = p0 + geom_contour(aes(color=after_stat("level")))
    assert p == "mapped_level"


def test_duplicate_coordinates_emit_warning():
    data = pd.concat([faithfuld, faithfuld.iloc[:5]], ignore_index=True)
    p = ggplot(data, aes("waiting", "eruptions", z="density")) + geom_contour()
    with pytest.warns(PlotnineWarning):
        p.draw_test()


def test_contour_lines_expose_computed_variables():
    data = (p0 + geom_contour()).build_test().layers[0].data
    assert {"level", "nlevel", "piece"} <= set(data.columns)
    assert data.groupby("group").ngroups > 1
    assert data["nlevel"].max() == 1
    levels = np.sort(data["level"].unique())
    assert np.allclose(np.diff(levels), 0.005)


def test_default_filled_contours():
    p = p0 + geom_contour_filled()
    assert p == "contour_filled"


def test_filled_contours_with_bin_count():
    p = p0 + geom_contour_filled(bins=4)
    assert p == "contour_filled_bins"


def test_filled_contour_levels_are_ordered():
    p = p0 + geom_contour_filled()
    data = p.build_test().layers[0].data
    assert data["level"].cat.ordered
    assert "subgroup" in data


def test_facet_panels_share_breaks():
    low = faithfuld.assign(panel="low")
    high = faithfuld.assign(density=faithfuld["density"] * 3, panel="high")
    data = pd.concat([low, high], ignore_index=True)

    p = (
        ggplot(data, aes("waiting", "eruptions", z="density"))
        + geom_contour()
        + facet_wrap("panel")
    )
    # Shared breaks produce one evenly spaced sequence of contour values.
    # Per-panel breaks would interleave different sequences.
    levels = np.sort(p.build_test().layers[0].data["level"].unique())
    steps = np.diff(levels)
    assert np.allclose(steps, steps[0])


def test_missing_surface_values_leave_holes():
    data = faithfuld.copy()
    data.loc[data.index[:20], "density"] = np.nan
    p = ggplot(data, aes("waiting", "eruptions", z="density")) + geom_contour()
    assert p == "missing_z"


def test_rotated_grid_draws_complete_contours():
    angle = np.pi / 6
    x, y = faithfuld["waiting"], faithfuld["eruptions"]
    data = faithfuld.assign(
        rx=np.cos(angle) * x - np.sin(angle) * y,
        ry=np.sin(angle) * x + np.cos(angle) * y,
    )
    p = ggplot(data, aes("rx", "ry", z="density")) + geom_contour()
    assert p == "rotated_grid"
