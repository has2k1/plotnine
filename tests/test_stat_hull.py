from plotnine import aes, geom_point, ggplot, stat_hull
from plotnine.data import mtcars


def test_hull():
    p = (
        ggplot(mtcars)
        + aes("wt", "mpg", color="factor(cyl)")
        + geom_point()
        + stat_hull(size=1)
    )

    assert p == "hull"
