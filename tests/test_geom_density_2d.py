import pandas as pd

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
