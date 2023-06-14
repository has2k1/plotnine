import numpy as np
import pandas as pd

from plotnine import aes, geom_spoke, ggplot

n = 4
data = pd.DataFrame(
    {
        "x": [1] * n,
        "y": range(n),
        "angle": np.linspace(0, np.pi / 2, n),
        "radius": range(1, n + 1),
        "z": range(n),
    }
)


def test_aesthetics():
    p = (
        ggplot(data, aes(y="y", angle="angle", radius="radius"))
        + geom_spoke(aes("x"), size=2)
        + geom_spoke(aes("x+2", alpha="z"), size=2)
        + geom_spoke(aes("x+4", linetype="factor(z)"), size=2)
        + geom_spoke(aes("x+6", color="factor(z)"), size=2)
        + geom_spoke(aes("x+8", size="z"))
    )

    assert p == "aesthetics"


def test_unmapped_angle():
    p = ggplot(data, aes(y="y", angle="angle", radius="radius")) + geom_spoke(
        aes("x", "y"), angle=0, radius=1
    )
    assert p == "test_unmapped_angle"
