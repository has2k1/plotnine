import pandas as pd
import numpy as np
import pytest

from plotnine import ggplot, aes, stat_bin, stat_density, xlim
from plotnine.exceptions import PlotnineError


def test_stat_bin():
    x = [1, 2, 3]
    y = [1, 2, 3]
    df = pd.DataFrame({'x': x, 'y': y})

    # About the default bins
    gg = ggplot(aes(x='x'), df) + stat_bin()

    with pytest.warns(None) as record:
        gg.draw_test()

    res = ('bins' in str(item.message).lower() for item in record)
    assert any(res)

    # About the ignoring the y aesthetic
    gg = ggplot(aes(x='x', y='y'), df) + stat_bin()
    with pytest.raises(PlotnineError):
        gg.draw_test()


def test_changing_xlim_in_stat_density():
    n = 100
    _xlim = (5, 10)
    df = pd.DataFrame({'x': np.linspace(_xlim[0]-1, _xlim[1]+1, n)})
    p = (ggplot(df, aes('x'))
         + stat_density()
         + xlim(*_xlim)
         )
    # No exceptions
    p._build()
