import numpy as np
import pandas as pd

from plotnine import ggplot, aes, geom_qq, geom_qq_line

random_state = np.random.RandomState(1234567890)
df_normal = pd.DataFrame({'x': random_state.normal(size=100)})


def test_normal():
    p = ggplot(df_normal, aes(sample='x')) + geom_qq()
    # Roughly a straight line of points through the origin
    assert p == 'normal'


def test_normal_with_line():
    p = (ggplot(df_normal, aes(sample='x'))
         + geom_qq()
         + geom_qq_line()
         )
    # Roughly a straight line of points through the origin
    assert p == 'normal_with_line'
