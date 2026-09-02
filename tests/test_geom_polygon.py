import numpy as np
import pandas as pd

from plotnine import aes, coord_radial, geom_polygon, ggplot

data = pd.DataFrame(
    {
        "x": ([1, 2, 3, 2] + [5, 6, 7] + [9, 9, 10, 11, 11, 10]),
        "y": ([2, 3, 2, 1] + [1, 3, 1] + [1.5, 2.5, 3, 2.5, 1.5, 1]),
        "z": ([1] * 4 + [2] * 3 + [3] * 6),
    }
)


def test_aesthetics():
    p = (
        ggplot(data, aes("x", group="factor(z)"))
        + geom_polygon(aes(y="y"))
        + geom_polygon(aes(y="y+3", alpha="z"))
        + geom_polygon(
            aes(y="y+6", linetype="factor(z)"),
            color="brown",
            fill=None,
            size=2,
        )
        + geom_polygon(aes(y="y+9", color="z"), fill=None, size=2)
        + geom_polygon(aes(y="y+12", fill="factor(z)"))
        + geom_polygon(
            aes(y="y+15", size="z"), color="yellow", show_legend=False
        )
    )

    assert p == "aesthetics"


def test_no_fill():
    p = (
        ggplot(data, aes("x", group="factor(z)"))
        + geom_polygon(aes(y="y"), fill=None, color="red", size=2)
        + geom_polygon(aes(y="y+2"), fill="none", color="green", size=2)
        + geom_polygon(aes(y="y+4"), fill="none", color="blue", size=2)
    )
    assert p == "no_fill"


def holed_and_solid(solid_subgroup=0):
    """
    Create a holed square beside a solid square

    `solid_subgroup` identifies the solid square's only ring. A missing
    value represents the same ring as an explicit number.
    """
    outer = {"x": [0, 4, 4, 0], "y": [0, 0, 4, 4], "sub": 0, "g": "holed"}
    # Opposite winding makes this inner ring a hole.
    hole = {"x": [1, 1, 3, 3], "y": [1, 3, 3, 1], "sub": 1, "g": "holed"}
    solid = {
        "x": [5, 9, 9, 5],
        "y": [0, 0, 4, 4],
        "sub": solid_subgroup,
        "g": "solid",
    }
    return pd.concat(
        [pd.DataFrame(d) for d in (outer, hole, solid)], ignore_index=True
    )


def test_numbered_subgroups_draw_polygon_holes():
    p = ggplot(
        holed_and_solid(), aes("x", "y", group="g", subgroup="sub")
    ) + geom_polygon(fill="steelblue", color="black", size=1)
    assert p == "holes"


def test_numbered_subgroups_preserve_polar_polygon_holes():
    # A non-linear coord munches every edge, and could bridge a ring
    # boundary if it were not subgroup-aware.
    p = (
        ggplot(holed_and_solid(), aes("x", "y", group="g", subgroup="sub"))
        + geom_polygon(fill="steelblue", color="black", size=1)
        + coord_radial()
    )
    assert p == "holes_polar"


def test_missing_subgroup_draws_solid_polygon():
    # A missing subgroup identifies the solid polygon's only ring.
    data = holed_and_solid(solid_subgroup=np.nan)
    p = ggplot(data, aes("x", "y", group="g", subgroup="sub")) + geom_polygon(
        fill="steelblue", color="black", size=1
    )
    p.draw_test()


def test_missing_subgroup_remains_one_polar_ring():
    # Consecutive missing subgroup values form one continuous ring, so
    # non-linear coordinates interpolate its edges instead of splitting it
    # at every vertex.
    data = holed_and_solid(solid_subgroup=np.nan)
    p = (
        ggplot(data, aes("x", "y", group="g", subgroup="sub"))
        + geom_polygon(fill="steelblue", color="black", size=1)
        + coord_radial()
    )
    assert p == "holes_missing_subgroup_polar"
