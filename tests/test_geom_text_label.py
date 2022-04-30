import pandas as pd
import numpy as np

from plotnine import (ggplot, aes, geom_text, geom_label, geom_point,
                      scale_size_continuous, scale_y_continuous)
from plotnine.data import mtcars

n = 5
labels = ['ggplot', 'aesthetics', 'data', 'geoms',
          r'$\mathbf{statistics^2}$', 'scales', 'coordinates']
df = pd.DataFrame({
        'x': [1] * n,
        'y': range(n),
        'label': labels[:n],
        'z': range(n),
        'angle': np.linspace(0, 90, n)
    })

adjust_text = {
    'expand_points': (2, 2),
    'arrowprops': {
        'arrowstyle': '->',
        'color': 'red'
    }
}


def test_text_aesthetics():
    p = (ggplot(df, aes(y='y', label='label')) +
         geom_text(aes('x', label='label'), size=15, ha='left') +
         geom_text(aes('x+1', angle='angle'),
                   size=15, va='top', show_legend=False) +
         geom_text(aes('x+2', label='label', alpha='z'),
                   size=15, show_legend=False) +
         geom_text(aes('x+3', color='factor(z)'),
                   size=15, show_legend=False) +
         geom_text(aes('x+5', size='z'),
                   ha='right', show_legend=False) +
         scale_size_continuous(range=(12, 30)) +
         scale_y_continuous(limits=(-0.5, n-0.5)))

    assert p == 'text_aesthetics'


def test_label_aesthetics():
    p = (ggplot(df, aes(y='y', label='label')) +
         geom_label(aes('x', label='label', fill='z'),
                    size=15, ha='left', show_legend=False, boxcolor='red') +
         geom_label(aes('x+1', angle='angle'),
                    size=15, va='top', show_legend=False) +
         geom_label(aes('x+2', label='label', alpha='z'),
                    size=15, show_legend=False) +
         geom_label(aes('x+3', color='factor(z)'),
                    size=15, show_legend=False) +
         geom_label(aes('x+5', size='z'),
                    ha='right', show_legend=False) +
         scale_size_continuous(range=(12, 30)) +
         scale_y_continuous(limits=(-0.5, n-0.5)))

    assert p == 'label_aesthetics'


def test_adjust_text():
    p = (ggplot(mtcars.tail(2), aes('mpg', 'disp', label='name'))
         + geom_point(size=5, fill='black')
         + geom_text(adjust_text=adjust_text)
         )
    assert p == 'adjust_text'


def test_adjust_label():
    p = (ggplot(mtcars.tail(2), aes('mpg', 'disp', label='name'))
         + geom_point(size=5, fill='black')
         + geom_label(adjust_text=adjust_text)
         )
    assert p == 'adjust_label'
