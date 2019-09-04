import pandas as pd

from plotnine import ggplot, aes, geom_col, theme

_theme = theme(subplots_adjust={'right': 0.80})

df = pd.DataFrame({
    'x': ['b', 'd', 'c', 'a'],
    'y': [1, 2, 3, 4]
})


def test_reorder():
    p = (
        ggplot(df, aes('reorder(x, y)', 'y', fill='reorder(x, y, True)'))
        + geom_col()
    )
    assert p + _theme == 'reorder'


def test_reorder_index():
    # The dataframe is created with ordering according to the y
    # variable. So the x index should be ordered acc. to y too
    p = (
        ggplot(df, aes('reorder(x, x.index)', 'y'))
        + geom_col()
    )
    assert p + _theme == 'reorder_index'
