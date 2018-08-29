import pandas as pd

from plotnine import (ggplot, aes, geom_density_2d, stat_density_2d,
                      geom_point, theme, lims, scale_size_radius)

n = 20
adj = n//4

df = pd.DataFrame({'x': range(n), 'y': range(n)})
_theme = theme(subplots_adjust={'right': 0.85})

p0 = (ggplot(df, aes('x', 'y'))
      + lims(x=(-adj, n+adj), y=(-adj, n+adj))
      + _theme)


def test_contours():
    p = p0 + geom_density_2d(aes(color='stat(level)'))
    assert p == 'contours'


def test_points():
    p = (p0
         + geom_point(
             aes(fill='stat(density)', size='stat(density)'),
             stat='density_2d',
             stroke=0, n=16, contour=False)
         + scale_size_radius(range=(0, 6)))

    assert p == 'points'


def test_polygon():
    p = p0 + stat_density_2d(aes(fill='stat(level)'), geom='polygon')
    assert p == 'polygon'
