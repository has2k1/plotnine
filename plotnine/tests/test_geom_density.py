import pytest
import numpy as np
import pandas as pd

from plotnine import ggplot, aes, geom_density, theme, lims
from plotnine.exceptions import PlotnineWarning

n = 6  # Some even number greater than 2

# ladder: 0 1 times, 1 2 times, 2 3 times, ...
df = pd.DataFrame({'x': np.repeat(range(n+1), range(n+1)),
                   'z': np.repeat(range(n//2), range(3, n*2, 4))})

p = ggplot(df, aes('x', fill='factor(z)'))
_theme = theme(subplots_adjust={'right': 0.85})


def test_gaussian():
    p1 = p + geom_density(kernel='gaussian', alpha=.3)
    assert p1 + _theme == 'gaussian'


def test_gaussian_weighted():
    p1 = p + geom_density(aes(weight='x'), kernel='gaussian', alpha=.3)
    assert p1 + _theme == 'gaussian_weighted'


def test_gaussian_trimmed():
    p2 = p + geom_density(kernel='gaussian', alpha=.3, trim=True)
    assert p2 + _theme == 'gaussian-trimmed'


def test_triangular():
    p3 = p + geom_density(
        kernel='triangular',
        bw='normal_reference',
        alpha=.3)  # other
    assert p3 + _theme == 'triangular'


def test_few_datapoints():
    df = pd.DataFrame({
        'x': [1, 2, 2, 3, 3, 3],
        'z': list('abbccc')
    })

    # Bandwidth not set
    p = (ggplot(df, aes('x', color='z'))
         + geom_density()
         + lims(x=(-3, 9))
         )
    with pytest.warns(PlotnineWarning) as record:
        p.draw_test()

    record = list(record)  # iterate more than 1 time
    assert any('e.g `bw=0.1`' in str(r.message) for r in record)
    assert any('Groups with fewer than 2' in str(r.message) for r in record)

    p = (ggplot(df, aes('x', color='z'))
         + geom_density(bw=.1)
         + lims(x=(0, 4))
         )
    assert p == 'few_datapoints'
