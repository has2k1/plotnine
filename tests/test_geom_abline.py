import pandas as pd
import pytest

from plotnine import aes, geom_abline, geom_point, ggplot
from plotnine.exceptions import PlotnineWarning

data = pd.DataFrame(
    {
        "slope": [1, 1],
        "intercept": [1, -1],
        "x": [-1, 1],
        "y": [-1, 1],
        "z": range(2),
    }
)


def test_aesthetics():
    p = (
        ggplot(data, aes("x", "y"))
        + geom_point()
        + geom_abline(aes(slope="slope", intercept="intercept"), size=2)
        + geom_abline(
            aes(slope="slope", intercept="intercept+.1", alpha="z"), size=2
        )
        + geom_abline(
            aes(slope="slope", intercept="intercept+.2", linetype="factor(z)"),
            size=2,
        )
        + geom_abline(
            aes(slope="slope", intercept="intercept+.3", color="factor(z)"),
            size=2,
        )
        + geom_abline(aes(slope="slope", intercept="intercept+.4", size="z"))
    )

    assert p == "aesthetics"


def test_aes_inheritance():
    # A default line (intercept = 0, slope = 1)
    p = (
        ggplot(
            data,
            aes(
                "x",
                "y",
                color="factor(z)",
                slope="slope",
                intercept="intercept",
            ),
        )
        + geom_point(size=10, show_legend=False)
        + geom_abline(size=2)
    )

    assert p == "aes_inheritance"


def test_aes_overwrite():
    with pytest.warns(PlotnineWarning):
        geom_abline(aes(intercept="y"), intercept=2)
