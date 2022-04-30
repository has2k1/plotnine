import pandas as pd
import numpy as np

from plotnine import ggplot, aes, geom_point, geom_rect, geom_tile, labs, theme
from plotnine import coord_trans

n = 4

df = pd.DataFrame({
        'xmin': range(1, n*2, 2),
        'xmax': range(2, n*2+1, 2),
        'ymin': [1] * n,
        'ymax': [2] * n,
        'z': range(n)
    })

# geom_rect and geom_tile are similar but
# parameterised different
# for geom_tile
df['x'] = df['xmin'] + 0.5
df['y'] = df['ymin'] + 0.5

# To leave enough room for the legend
_theme = theme(subplots_adjust={'right': 0.85})


def test_rect_aesthetics():
    p = (ggplot(df, aes(xmin='xmin', xmax='xmax',
                        ymin='ymin', ymax='ymax')) +
         geom_rect() +
         geom_rect(aes(ymin='ymin+2', ymax='ymax+2',
                       alpha='z'),
                   show_legend=False) +
         geom_rect(aes(ymin='ymin+4', ymax='ymax+4',
                       fill='factor(z)')) +
         geom_rect(aes(ymin='ymin+6', ymax='ymax+6',
                       color='factor(z+1)'), size=2) +
         geom_rect(aes(ymin='ymin+8', ymax='ymax+8',
                       linetype='factor(z+2)'),
                   color='yellow', size=2) +
         _theme +
         # for comparison with geom_tile which
         # has labels by default
         labs(x='x', y='y'))

    assert p == 'rect-aesthetics'


def test_rect_nofill():
    p = (ggplot(df)
         + aes(xmin='xmin', xmax='xmax', ymin='ymin', ymax='ymax')
         + geom_rect(color='red', fill=None, size=2)
         + geom_rect(aes(ymin='ymin+2', ymax='ymax+2'),
                     color='blue', fill='None', size=2)
         + geom_rect(aes(ymin='ymin+4', ymax='ymax+4'),
                     color='green', fill='', size=2)
         + geom_rect(aes(ymin='ymin+6', ymax='ymax+6'),
                     color='yellow', fill='gray', size=2))

    assert p == 'rect-nofill'


def test_tile_aesthetics():
    p = (ggplot(df, aes('x', 'y', width=1, height=1)) +
         geom_tile() +
         geom_tile(aes(y='y+2', alpha='z'),
                   show_legend=False) +
         geom_tile(aes(y='y+4', fill='factor(z)')) +
         geom_tile(aes(y='y+6', color='factor(z+1)'), size=2) +
         geom_tile(aes(y='y+8', linetype='factor(z+2)'),
                   color='yellow', size=2) +
         _theme)

    assert p == 'tile-aesthetics'


def test_infinite_rects():
    df = pd.DataFrame({
        'x': range(10),
        'y': range(10)
    })
    rdf = pd.DataFrame({
        'xmin': [3],
        'xmax': 7,
        'ymin': -np.inf,
        'ymax': np.inf,
    })

    p = (ggplot(df, aes('x', 'y'))
         + geom_point()
         + geom_rect(
             data=rdf,
             mapping=aes(xmin='xmin', xmax='xmax', ymin='ymin', ymax='ymax'),
             alpha=0.2,
             inherit_aes=False)
         )

    assert p == 'infinite-rects'


def test_coord_trans():
    df = pd.DataFrame({
        'x': range(10),
        'y': range(10)
    })
    rdf = pd.DataFrame({
        'xmin': [3],
        'xmax': 7,
        'ymin': -np.inf,
        'ymax': np.inf,
    })

    p = (ggplot(df, aes('x', 'y'))
         + geom_point()
         + geom_rect(
             data=rdf,
             mapping=aes(xmin='xmin', xmax='xmax', ymin='ymin', ymax='ymax'),
             alpha=0.2,
             inherit_aes=False)
         + coord_trans()
         )

    assert p == 'coord-trans'


def test_coord_trans_groups():
    df = pd.DataFrame({
        'xmin': [0, 2, 4],
        'xmax': [1, 3, 5],
        'ymin': [0, 2, 4],
        'ymax': [1, 3, 5],
        'c': list('abc')
    })

    p = (ggplot(df)
         + geom_rect(
             aes(xmin='xmin', xmax='xmax', ymin='ymin', ymax='ymax', fill='c'))
         + coord_trans()
         )
    assert p == 'coord-trans-groups'
