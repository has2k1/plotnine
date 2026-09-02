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


def test_numbered_subgroups_draw_polygon_holes():
    # Draw a holed square beside a solid square.
    outer = {"x": [0, 4, 4, 0], "y": [0, 0, 4, 4], "sub": 0, "g": "holed"}
    # Opposite winding makes this inner ring a hole.
    hole = {"x": [1, 1, 3, 3], "y": [1, 3, 3, 1], "sub": 1, "g": "holed"}
    solid = {"x": [5, 9, 9, 5], "y": [0, 0, 4, 4], "sub": 0, "g": "solid"}

    data = pd.concat(
        [pd.DataFrame(d) for d in (outer, hole, solid)], ignore_index=True
    )
    p = ggplot(data, aes("x", "y", group="g", subgroup="sub")) + geom_polygon(
        fill="steelblue", color="black", size=1
    )
    assert p == "holes"


def test_numbered_subgroups_preserve_polar_polygon_holes():
    # Non-linear coordinates interpolate every edge. Ring boundaries
    # must prevent interpolation from connecting the exterior to a hole.
    outer = {"x": [0, 4, 4, 0], "y": [0, 0, 4, 4], "sub": 0, "g": "holed"}
    hole = {"x": [1, 1, 3, 3], "y": [1, 3, 3, 1], "sub": 1, "g": "holed"}
    solid = {"x": [5, 9, 9, 5], "y": [0, 0, 4, 4], "sub": 0, "g": "solid"}

    data = pd.concat(
        [pd.DataFrame(d) for d in (outer, hole, solid)], ignore_index=True
    )
    p = (
        ggplot(data, aes("x", "y", group="g", subgroup="sub"))
        + geom_polygon(fill="steelblue", color="black", size=1)
        + coord_radial()
    )
    assert p == "holes_polar"
