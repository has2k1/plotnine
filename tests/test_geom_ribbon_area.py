import numpy as np
import pandas as pd

from plotnine import (
    aes,
    coord_flip,
    facet_wrap,
    geom_area,
    geom_ribbon,
    ggplot,
    scale_x_continuous,
    theme
)


n = 4            # No. of ribbions in a vertical stack
m = 100          # Points
width = 2*np.pi  # width of each ribbon
x = np.linspace(0, width, m)

df = pd.DataFrame({
        'x': np.tile(x, n),
        'ymin': np.hstack([np.sin(x)+2*i for i in range(n)]),
        'ymax': np.hstack([np.sin(x)+2*i+1 for i in range(n)]),
        'z': np.repeat(range(n), m)
    })
_theme = theme(subplots_adjust={'right': 0.85})


def test_ribbon_aesthetics():
    p = (ggplot(df, aes('x', ymin='ymin', ymax='ymax',
                        group='factor(z)')) +
         geom_ribbon() +
         geom_ribbon(aes('x+width', alpha='z')) +
         geom_ribbon(aes('x+2*width', linetype='factor(z)'),
                     color='black', fill=None, size=2) +
         geom_ribbon(aes('x+3*width', color='z'),
                     fill=None, size=2) +
         geom_ribbon(aes('x+4*width', fill='factor(z)')) +
         geom_ribbon(aes('x+5*width', size='z'),
                     color='black', fill=None) +
         scale_x_continuous(
             breaks=[i*2*np.pi for i in range(7)],
             labels=['0'] + [fr'${2*i}\pi$' for i in range(1, 7)])
         )

    assert p + _theme == 'ribbon_aesthetics'


def test_area_aesthetics():
    p = (ggplot(df, aes('x', 'ymax+2', group='factor(z)')) +
         geom_area() +
         geom_area(aes('x+width', alpha='z')) +
         geom_area(aes('x+2*width', linetype='factor(z)'),
                   color='black', fill=None, size=2) +
         geom_area(aes('x+3*width', color='z'),
                   fill=None, size=2) +
         geom_area(aes('x+4*width', fill='factor(z)')) +
         geom_area(aes('x+5*width', size='z'),
                   color='black', fill=None) +
         scale_x_continuous(
             breaks=[i*2*np.pi for i in range(7)],
             labels=['0'] + [fr'${2*i}\pi$' for i in range(1, 7)])
         )

    assert p + _theme == 'area_aesthetics'


def test_ribbon_facetting():
    p = (ggplot(df, aes('x', ymin='ymin', ymax='ymax',
                        fill='factor(z)')) +
         geom_ribbon() +
         facet_wrap('~ z')
         )

    assert p + _theme == 'ribbon_facetting'


def test_ribbon_coord_flip():
    df = pd.DataFrame({
        'x': [0, 1, 2, 3, 4, 5],
        'y': [0, 3, 5, 5, 3, 0]
    })

    p = (ggplot(df, aes('x'))
         + geom_ribbon(aes(ymax='y'), ymin=0)
         + coord_flip()
         )

    assert p + _theme == 'ribbon_coord_flip'
