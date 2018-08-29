import numpy as np
import pandas as pd
import pytest

from plotnine.exceptions import PlotnineError
from plotnine import ggplot, aes, arrow, stat_function


n = 10
df = pd.DataFrame({'x': range(1, n+1)})


def test_limits():
    p = (ggplot(df, aes('x')) +
         stat_function(fun=np.cos, size=2,
                       color='blue', arrow=arrow(ends='first')) +
         stat_function(fun=np.cos, xlim=(10, 20), size=2,
                       color='red', arrow=arrow(ends='last')))
    assert p == 'limits'


def test_args():
    def fun(x, f=lambda x: x, mul=1, add=0):
        return f(x)*mul + add

    # no args, single arg, tuple of args, dict of args
    p = (ggplot(df, aes('x')) +
         stat_function(fun=fun, size=2, color='blue') +
         stat_function(fun=fun, size=2, color='red', args=np.cos) +
         stat_function(fun=fun, size=2, color='green',
                       args=(np.cos, 2, 1)) +
         stat_function(fun=fun, size=2, color='purple',
                       args=dict(f=np.cos, mul=3, add=2)))

    assert p == 'args'


def test_exceptions():
    # no x limits
    with pytest.raises(PlotnineError):
        p = ggplot(df)
        print(p + stat_function(fun=np.sin))

    # fun not callable
    with pytest.raises(PlotnineError):
        p = ggplot(df, aes('x'))
        print(p + stat_function(fun=1))
