import pandas as pd

from plotnine import ggplot, aes, geom_lollipop

df = pd.DataFrame({'x': ['a', 'b', 'c', 'd', 'e'], 'y': [1, 2, -2, 3, 4]})


def test_lollipop():
    p = ggplot(df, aes('x', 'y')) + geom_lollipop()
    assert p == 'lollipop'

