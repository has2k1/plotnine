import pandas as pd
import pytest

from plotnine import (
    aes,
    after_stat,
    geom_density_2d,
    geom_point,
    ggplot,
    lims,
    scale_size_radius,
    stat_density_2d,
)
from plotnine.exceptions import PlotnineWarning

n = 20
adj = n // 4

data = pd.DataFrame({"x": range(n), "y": range(n)})

p0 = ggplot(data, aes("x", "y")) + lims(x=(-adj, n + adj), y=(-adj, n + adj))


def test_contours():
    p = p0 + geom_density_2d(aes(color=after_stat("level")))
    assert p == "contours"


def test_points():
    p = (
        p0
        + geom_point(
            aes(fill=after_stat("density"), size=after_stat("density")),
            stat="density_2d",
            stroke=0,
            n=16,
            contour=False,
        )
        + scale_size_radius(range=(0, 6))
    )

    assert p == "points"


def test_polygon():
    p = p0 + stat_density_2d(aes(fill=after_stat("level")), geom="polygon")
    assert p == "polygon"


def test_density_contours_with_bin_count():
    p = p0 + geom_density_2d(bins=3)
    assert p == "bins"


def test_density_contours_use_count():
    p = p0 + geom_density_2d(contour_var="count")
    assert p == "contour_var_count"


def test_levels_parameter_is_deprecated():
    p = p0 + geom_density_2d(levels=3)
    with pytest.warns(PlotnineWarning):
        p.draw_test()


def test_uncontoured_density_exposes_grid_variables():
    p = p0 + geom_density_2d(contour=False)
    data = p.build_test().layers[0].data
    assert {"density", "ndensity", "count", "n"} <= set(data.columns)
    assert data["ndensity"].max() == 1


def test_contoured_density_excludes_grid_variables():
    p = p0 + geom_density_2d()
    data = p.build_test().layers[0].data
    assert not {"z", "density", "ndensity", "count", "n"} & set(data.columns)


def test_default_uses_more_than_three_contour_levels():
    data = (p0 + geom_density_2d()).build_test().layers[0].data
    # The former five-band default produced only three contour levels for
    # this fixture. The new ten-band default must produce more.
    assert len(data["level"].unique()) > 3
