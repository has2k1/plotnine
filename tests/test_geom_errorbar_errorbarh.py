import pandas as pd

from plotnine import aes, geom_errorbar, geom_errorbarh, ggplot

n = 4
data = pd.DataFrame(
    {
        "x": [1] * n,
        "ymin": range(1, 2 * n + 1, 2),
        "ymax": range(2, 2 * n + 2, 2),
        "z": range(n),
    }
)


def test_errorbar_aesthetics():
    p = (
        ggplot(data, aes(ymin="ymin", ymax="ymax"))
        + geom_errorbar(aes("x"), size=2)
        + geom_errorbar(aes("x+1", alpha="z"), width=0.2, size=2)
        + geom_errorbar(aes("x+2", linetype="factor(z)"), size=2)
        + geom_errorbar(aes("x+3", color="z"), size=2)
        + geom_errorbar(aes("x+4", size="z"))
    )

    assert p == "errorbar_aesthetics"


def test_errorbarh_aesthetics():
    p = (
        ggplot(data, aes(xmin="ymin", xmax="ymax"))
        + geom_errorbarh(aes(y="x"), size=2)
        + geom_errorbarh(aes(y="x+1", alpha="z"), height=0.2, size=2)
        + geom_errorbarh(aes(y="x+2", linetype="factor(z)"), size=2)
        + geom_errorbarh(aes(y="x+3", color="factor(z)"), size=2)
        + geom_errorbarh(aes(y="x+4", size="z"))
    )

    assert p == "errorbarh_aesthetics"
