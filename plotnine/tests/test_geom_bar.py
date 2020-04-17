import pandas as pd

from plotnine import ggplot, aes, geom_bar


def test_bar_alpha():
    df = pd.DataFrame(
        {
            "x": ["a%i" % i for i in range(10)],
            "y": range(1, 11),
            "alpha": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
        }
    )
    p = ggplot(df, aes("x")) + geom_bar(
        aes(y="y", alpha="alpha"),
        stat="identity", color="blue", position="dodge"
    )
    assert p == "bar_alpha"
