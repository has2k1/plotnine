import numpy as np
import pandas as pd

from plotnine import (ggplot, aes, geom_pointdensity, after_stat,
                      geom_point, scale_size_radius, theme)

n = 16  # Some even number > 2

df = pd.DataFrame({
    'x': range(n),
    'y': np.repeat(range(n//2), 2)
})
_theme = theme(subplots_adjust={'right': 0.85})

p0 = (ggplot(df, aes('x', 'y'))
      + _theme)


def test_pointdensity():
    p = p0 + geom_pointdensity(size=10)
    assert p == 'contours'


def test_points():
    p = (p0
         + geom_point(
             aes(fill=after_stat('density'), size=after_stat('density')),
             stat='pointdensity')
         + scale_size_radius(range=(10, 20)))

    assert p == 'points'
