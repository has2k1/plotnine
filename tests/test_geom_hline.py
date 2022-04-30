import pandas as pd
import pytest

from plotnine import ggplot, aes, geom_hline, geom_point, theme
from plotnine.exceptions import PlotnineError, PlotnineWarning

df = pd.DataFrame({
        'yintercept': [1, 2],
        'x': [-1, 1],
        'y': [0.5, 3],
        'z': range(2)
    })

_theme = theme(subplots_adjust={'right': 0.85})


def test_aesthetics():
    p = (ggplot(df) +
         geom_point(aes('x', 'y')) +
         geom_hline(aes(yintercept='yintercept'), size=2) +
         geom_hline(aes(yintercept='yintercept+.1', alpha='z'),
                    size=2) +
         geom_hline(aes(yintercept='yintercept+.2',
                        linetype='factor(z)'),
                    size=2) +
         geom_hline(aes(yintercept='yintercept+.3',
                        color='factor(z)'),
                    size=2) +
         geom_hline(aes(yintercept='yintercept+.4', size='z')))

    assert p + _theme == 'aesthetics'


def test_aes_inheritance():
    with pytest.raises(PlotnineError):
        p = (ggplot(df, aes('x', 'y', yintercept='yintercept')) +
             geom_point() +
             geom_hline(size=2))
        p.draw_test()


def test_aes_overwrite():
    with pytest.warns(PlotnineWarning):
        geom_hline(aes(color='y'), yintercept=2)
