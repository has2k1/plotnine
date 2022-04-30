import pandas as pd

from plotnine import ggplot, aes, geom_count, theme

_theme = theme(subplots_adjust={'right': 0.85})

df = pd.DataFrame({
    'x': list('aaaaaaaaaabbbbbbbbbbcccccccccc'),
    'y': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
          1, 1, 1, 1, 1, 6, 6, 8, 10, 10,
          1, 1, 2, 4, 4, 4, 4, 9, 9, 9]})


def test_discrete_x():
    p = ggplot(df, aes('x', 'y')) + geom_count()

    assert p + _theme == 'discrete_x'


def test_discrete_y():
    p = ggplot(df, aes('y', 'x')) + geom_count()

    assert p + _theme == 'discrete_y'


def test_continuous_x_y():
    p = ggplot(df, aes('y', 'y')) + geom_count()

    assert p + _theme == 'continuous_x_y'
