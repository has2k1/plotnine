import pandas as pd

from plotnine import ggplot, aes, geom_point, labs, theme

_theme = theme(subplots_adjust={'right': 0.80})


df = pd.DataFrame({
    'x': [1, 2],
    'y': [3, 4],
    'cat': ['a', 'b']
})


def test_labelling_with_colour():
    p = (ggplot(df, aes('x', 'y', color='cat'))
         + geom_point()
         + labs(colour='Colour Title')
         )

    assert p + _theme == 'labelling_with_colour'
