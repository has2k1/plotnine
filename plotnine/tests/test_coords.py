import numpy as np
import pandas as pd
from mizani.transforms import trans_new

from plotnine import (ggplot, aes, geom_bar, geom_line, coord_flip,
                      coord_fixed, coord_trans, xlim)

n = 10  # Some even number greater than 2

# ladder: 0 1 times, 1 2 times, 2 3 times, ...
df = pd.DataFrame({'x': np.repeat(range(n+1), range(n+1)),
                   'z': np.repeat(range(n//2), range(3, n*2, 4))})

p = (ggplot(df, aes('x'))
     + geom_bar(aes(fill='factor(z)'), show_legend=False))


def test_coord_flip():
    assert p + coord_flip() == 'coord_flip'


def test_coord_fixed():
    assert p + coord_fixed(0.5) == 'coord_fixed'


def test_coord_trans():
    double_trans = trans_new('double', np.square, np.sqrt)
    assert p + coord_trans(y=double_trans) == 'coord_trans'


def test_coord_trans_reverse():
    # coord trans can reverse continous and discrete data
    p = (ggplot(df, aes('factor(x)'))
         + geom_bar(aes(fill='factor(z)'), show_legend=False)
         + coord_trans(x='reverse', y='reverse')
         )
    assert p == 'coord_trans_reverse'


def test_coord_trans_backtransforms():
    df = pd.DataFrame({'x': [-np.inf, np.inf], 'y': [1, 2]})
    p = (ggplot(df, aes('x', 'y'))
         + geom_line(size=2)
         + xlim(1, 2)
         + coord_trans(x='log10')
         )
    assert p == 'coord_trans_backtransform'
