import numpy as np
import pandas as pd

from plotnine import aes, coord_flip, geom_rug, ggplot

n = 4
seq = np.arange(1, n + 1)
data = pd.DataFrame(
    {
        "x": seq,
        "y": seq,
        "z": seq,
    }
)


def test_aesthetics():
    p = (
        ggplot(data)
        + geom_rug(aes("x", "y"), size=2)
        + geom_rug(aes("x+2*n", "y+2*n", alpha="z"), size=2, sides="tr")
        + geom_rug(
            aes("x+4*n", "y+4*n", linetype="factor(z)"), size=2, sides="t"
        )
        + geom_rug(aes("x+6*n", "y+6*n", color="factor(z)"), size=2, sides="b")
        + geom_rug(aes("x+8*n", "y+8*n", size="z"), sides="tblr")
    )

    assert p == "aesthetics"


def test_coord_flip():
    p = (
        ggplot(data)
        + geom_rug(aes("x", "y"), size=2, sides="l")
        + coord_flip()
    )

    assert p == "coord_flip"
