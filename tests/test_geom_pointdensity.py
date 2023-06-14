import numpy as np
import pandas as pd

from plotnine import (
    aes,
    after_stat,
    geom_point,
    geom_pointdensity,
    ggplot,
    scale_size_radius,
)

n = 16  # Some even number > 2

data = pd.DataFrame({"x": range(n), "y": np.repeat(range(n // 2), 2)})

p0 = ggplot(data, aes("x", "y"))


def test_pointdensity():
    p = p0 + geom_pointdensity(size=10)
    assert p == "contours"


def test_points():
    p = (
        p0
        + geom_point(
            aes(fill=after_stat("density"), size=after_stat("density")),
            stat="pointdensity",
        )
        + scale_size_radius(range=(10, 20))
    )

    assert p == "points"
