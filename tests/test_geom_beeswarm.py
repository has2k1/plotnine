import numpy as np
import pandas as pd

from plotnine import aes, coord_flip, geom_beeswarm, geom_violin, ggplot

n = 50
random_state = np.random.RandomState(123)
uni = random_state.chisquare(3, n)
bi = np.hstack(
    [random_state.normal(2.5, 0.5, n), random_state.normal(7.5, 0.5, n)]
)
tri = np.hstack(
    [
        random_state.normal(2.5, 0.325, n),
        random_state.normal(5, 0.325, n),
        random_state.normal(7.5, 0.325, n),
    ]
)

cats = ["uni", "bi", "tri"]

data = pd.DataFrame(
    {
        "dist": pd.Categorical(
            np.repeat(cats, [len(uni), len(bi), len(tri)]), categories=cats
        ),
        "value": np.hstack([uni, bi, tri]),
    }
)


def test_scale_area():
    p = (
        ggplot(data, aes("dist", "value"))
        + geom_violin(scale="area")
        + geom_beeswarm(scale="area")
    )

    assert p == "scale_area"


def test_scale_count():
    p = (
        ggplot(data, aes("dist", "value"))
        + geom_violin(scale="count")
        + geom_beeswarm(scale="count")
    )

    assert p == "scale_count"


def test_coord_flip():
    p = (
        ggplot(data, aes("dist", "value"))
        + geom_violin(scale="area")
        + geom_beeswarm(scale="area")
        + coord_flip()
    )

    assert p == "scale_area+coord_flip"


def test_method_counts():
    p = (
        ggplot(data, aes("dist", "value"))
        + geom_violin()
        + geom_beeswarm(method="counts")
    )

    assert p == "method_counts"


def test_style():
    p = (
        ggplot(data, aes("dist", "value"))
        + geom_violin(style="left")
        + geom_beeswarm(style="left")
    )

    assert p == "style"


def test_spread_smiley():
    p = (
        ggplot(data, aes("dist", "value"))
        + geom_violin()
        + geom_beeswarm(spread="smiley")
    )

    assert p == "spread_smiley"


def test_spread_frowney():
    p = (
        ggplot(data, aes("dist", "value"))
        + geom_violin()
        + geom_beeswarm(spread="frowney")
    )

    assert p == "spread_frowney"


def test_spread_pseudorandom():
    p = (
        ggplot(data, aes("dist", "value"))
        + geom_violin()
        + geom_beeswarm(spread="pseudorandom", random_state=123)
    )
    assert p == "spread_pseudorandom"
