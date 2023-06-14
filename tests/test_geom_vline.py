import pandas as pd
import pytest

from plotnine import aes, geom_point, geom_vline, ggplot
from plotnine.exceptions import PlotnineError, PlotnineWarning

data = pd.DataFrame(
    {"xintercept": [1, 2], "x": [0.5, 3], "y": [-1, 1], "z": range(2)}
)


def test_aesthetics():
    p = (
        ggplot(data)
        + geom_point(aes("x", "y"))
        + geom_vline(aes(xintercept="xintercept"), size=2)
        + geom_vline(aes(xintercept="xintercept+.1", alpha="z"), size=2)
        + geom_vline(
            aes(xintercept="xintercept+.2", linetype="factor(z)"), size=2
        )
        + geom_vline(
            aes(xintercept="xintercept+.3", color="factor(z)"), size=2
        )
        + geom_vline(aes(xintercept="xintercept+.4", size="z"))
    )

    assert p == "aesthetics"


def test_aes_inheritance():
    with pytest.raises(PlotnineError):
        p = (
            ggplot(data, aes("x", "y", xintercept="xintercept"))
            + geom_point()
            + geom_vline(size=2)
        )
        p.draw_test()


def test_aes_overwrite():
    with pytest.warns(PlotnineWarning):
        geom_vline(aes(color="x"), xintercept=2)
