import numpy as np
import pandas as pd

from plotnine import ggplot, aes, geom_boxplot, coord_flip, theme
from plotnine import position_nudge

n = 4
m = 10
df = pd.DataFrame({
    'x': np.repeat([chr(65+i) for i in range(n)], m),
    'y': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10] +
          [-2, 2, 3, 4, 5, 6, 7, 8, 9, 12] +
          [-7, -5, 3, 4, 5, 6, 7, 8, 12, 15] +
          [1, 2, 3, 4, 5, 8, 8, 8, 9, 10]
          )
})


class TestAesthetics:
    p = (ggplot(df, aes('x')) +
         geom_boxplot(aes(y='y'), size=2) +
         geom_boxplot(df[:2*m], aes(y='y+25', fill='x'), size=2) +
         geom_boxplot(df[2*m:], aes(y='y+30', color='x'), size=2) +
         geom_boxplot(df[2*m:], aes(y='y+55', linetype='x'), size=2)
         )

    def test_aesthetics(self):
        assert self.p == 'aesthetics'

    def test_aesthetics_coordflip(self):
        assert self.p + coord_flip() == 'aesthetics+coord_flip'


def test_params():
    p = (ggplot(df, aes('x')) +
         geom_boxplot(df[:m], aes(y='y'), size=2, notch=True) +
         geom_boxplot(df[m:2*m], aes(y='y'), size=2,
                      notch=True, notchwidth=0.8) +
         # outliers
         geom_boxplot(df[2*m:3*m], aes(y='y'), size=2,
                      outlier_size=4, outlier_color='green') +
         geom_boxplot(df[2*m:3*m], aes(y='y+25'), size=2,
                      outlier_size=4, outlier_alpha=0.5) +
         geom_boxplot(df[2*m:3*m], aes(y='y+60'), size=2,
                      outlier_size=4, outlier_shape='D') +
         # position dodge
         geom_boxplot(df[3*m:4*m], aes(y='y', fill='factor(y%2)')) +
         theme(subplots_adjust={'right': 0.85})
         )
    assert p == 'params'


def test_position_nudge():
    p = (ggplot(df, aes('x', 'y'))
         + geom_boxplot(position=position_nudge(x=-0.1), size=2)
         )
    assert p == 'position_nudge'
