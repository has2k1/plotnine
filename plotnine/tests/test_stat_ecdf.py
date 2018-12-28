import pandas as pd

from plotnine import ggplot, aes, stat_ecdf


df = pd.DataFrame({'x': range(10)})
p = ggplot(df, aes('x')) + stat_ecdf(size=2)


def test_ecdf():
    p = ggplot(df, aes('x')) + stat_ecdf(size=2)

    assert p == 'ecdf'


def test_computed_y_column():
    p = (ggplot(df, aes('x'))
         + stat_ecdf(size=2)
         # Should be able to used computed y column & create a
         # new mapped column also called y
         + stat_ecdf(aes(y='stat(y-0.2)'), size=2, color='blue')
         )
    assert p == 'computed_y_column'
