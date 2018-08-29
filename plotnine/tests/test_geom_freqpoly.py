import numpy as np
import pandas as pd

from plotnine import ggplot, aes, geom_histogram, geom_freqpoly, geom_point
from plotnine import theme

n = 10  # Some even number greater than 2

# ladder: 0 1 times, 1 2 times, 2 3 times, ...
df = pd.DataFrame({'x': np.repeat(range(n+1), range(n+1)),
                   'z': np.repeat(range(n//2), range(3, n*2, 4))})

_theme = theme(subplots_adjust={'right': 0.85})


def test_midpoint():
    p = (ggplot(df, aes('x')) +
         geom_histogram(aes(fill='factor(z)'), bins=n, alpha=0.25) +
         geom_freqpoly(bins=n, size=4) +
         geom_point(stat='bin', bins=n, size=4, stroke=0, color='red'))

    assert p + _theme == 'midpoint'
