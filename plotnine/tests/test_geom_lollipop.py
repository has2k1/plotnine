import pandas as pd

from plotnine import ggplot, aes, geom_lollipop

df = pd.DataFrame({'x': ['a', 'b', 'c', 'd', 'e'], 'y': [1, 2, -2, 3, 4]})


def test_lollipop():
    p = ggplot(df, aes('x', 'y')) + geom_lollipop()
    assert p == 'lollipop'


def test_horizontal_lollipop():
    p = ggplot(df, aes('y', 'x')) + geom_lollipop(horizontal=True)
    assert p == 'lollipop-horizontal'


def test_lollipop_points():
    p = ggplot(df, aes('y', 'x')) + geom_lollipop(point_color='steelblue', point_size=5)
    assert p == 'lollipop-points'
