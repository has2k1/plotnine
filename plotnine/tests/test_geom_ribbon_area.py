import numpy as np
import pandas as pd

from plotnine import (ggplot, aes, geom_area, geom_ribbon,
                      facet_wrap, scale_x_continuous, theme)

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
             labels=['0'] + [r'${}\pi$'.format(2*i) for i in range(1, 7)])
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
             labels=['0'] + [r'${}\pi$'.format(2*i) for i in range(1, 7)])
         )

    assert p + _theme == 'area_aesthetics'


def test_ribbon_facetting():
    p = (ggplot(df, aes('x', ymin='ymin', ymax='ymax',
                        fill='factor(z)')) +
         geom_ribbon() +
         facet_wrap('~ z')
         )

    assert p + _theme == 'ribbon_facetting'
