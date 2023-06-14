import numpy as np
import pandas as pd

from plotnine import aes, geom_linerange, geom_pointrange, ggplot

n = 4
data = pd.DataFrame(
    {
        "x": range(n),
        "y": np.arange(n) + 0.5,
        "ymin": range(n),
        "ymax": range(1, n + 1),
        "z": range(n),
    }
)


def test_linerange_aesthetics():
    p = (
        ggplot(data, aes("x"))
        + geom_linerange(aes(ymin="ymin", ymax="ymax"), size=2)
        + geom_linerange(aes(ymin="ymin+1", ymax="ymax+1", alpha="z"), size=2)
        + geom_linerange(
            aes(ymin="ymin+2", ymax="ymax+2", linetype="factor(z)"), size=2
        )
        + geom_linerange(aes(ymin="ymin+3", ymax="ymax+3", color="z"), size=2)
        + geom_linerange(aes(ymin="ymin+4", ymax="ymax+4", size="z"))
    )
    assert p == "linerange_aesthetics"


def test_pointrange_aesthetics():
    p = (
        ggplot(data, aes("x"))
        + geom_pointrange(aes(y="y", ymin="ymin", ymax="ymax"), size=2)
        + geom_pointrange(
            aes(y="y+1", ymin="ymin+1", ymax="ymax+1", alpha="z"), size=2
        )
        + geom_pointrange(
            aes(y="y+2", ymin="ymin+2", ymax="ymax+2", linetype="factor(z)"),
            size=2,
        )
        + geom_pointrange(
            aes(y="y+3", ymin="ymin+3", ymax="ymax+3", color="z"), size=2
        )
        + geom_pointrange(aes(y="y+4", ymin="ymin+4", ymax="ymax+4", size="z"))
    )
    assert p == "pointrange_aesthetics"
