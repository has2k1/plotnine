from __future__ import absolute_import, division, print_function

import pandas as pd
import numpy as np

from plotnine import (ggplot, aes, geom_text, geom_label,
                      scale_size_continuous, scale_y_continuous)

n = 5
labels = ['ggplot', 'aesthetics', 'data', 'geoms',
          '$\mathbf{statistics^2}$', 'scales', 'coordinates']
df = pd.DataFrame({
        'x': [1] * n,
        'y': range(n),
        'label': labels[:n],
        'z': range(n),
        'angle': np.linspace(0, 90, n)
    })


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
                    size=15, ha='left', show_legend=False) +
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
