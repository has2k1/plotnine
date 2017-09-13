from __future__ import absolute_import, division, print_function

import pandas as pd

from plotnine import ggplot, aes, geom_errorbar, geom_errorbarh, theme

n = 4
df = pd.DataFrame({
        'x': [1]*n,
        'ymin': range(1, 2*n+1, 2),
        'ymax': range(2, 2*n+2, 2),
        'z': range(n)
    })
_theme = theme(subplots_adjust={'right': 0.85})


def test_errorbar_aesthetics():
    p = (ggplot(df, aes(ymin='ymin', ymax='ymax')) +
         geom_errorbar(aes('x'), size=2) +
         geom_errorbar(aes('x+1', alpha='z'), width=0.2, size=2) +
         geom_errorbar(aes('x+2', linetype='factor(z)'), size=2) +
         geom_errorbar(aes('x+3', color='z'), size=2) +
         geom_errorbar(aes('x+4', size='z'))
         )

    assert p + _theme == 'errorbar_aesthetics'


def test_errorbarh_aesthetics():
    p = (ggplot(df, aes(xmin='ymin', xmax='ymax')) +
         geom_errorbarh(aes(y='x'), size=2) +
         geom_errorbarh(aes(y='x+1', alpha='z'), height=0.2, size=2) +
         geom_errorbarh(aes(y='x+2', linetype='factor(z)'), size=2) +
         geom_errorbarh(aes(y='x+3', color='factor(z)'), size=2) +
         geom_errorbarh(aes(y='x+4', size='z'))
         )

    assert p + _theme == 'errorbarh_aesthetics'
