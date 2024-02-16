import numpy as np
import pandas as pd
import pytest

from plotnine import aes, arrow, ggplot, stat_function
from plotnine.exceptions import PlotnineError

n = 10
data = pd.DataFrame({"x": range(1, n + 1)})


def test_limits():
    p = (
        ggplot(data, aes("x"))
        + stat_function(
            fun=np.cos, size=2, color="blue", arrow=arrow(ends="first")
        )
        + stat_function(
            fun=np.cos,
            xlim=(10, 20),
            size=2,
            color="red",
            arrow=arrow(ends="last"),
        )
    )
    assert p == "limits"


def test_args():
    def fun(x, f=lambda x: x, mul=1, add=0):
        return f(x) * mul + add

    # no args, single arg, tuple of args, dict of args
    p = (
        ggplot(data, aes("x"))
        + stat_function(fun=fun, size=2, color="blue")
        + stat_function(fun=fun, size=2, color="red", args=np.cos)
        + stat_function(fun=fun, size=2, color="green", args=(np.cos, 2, 1))
        + stat_function(
            fun=fun,
            size=2,
            color="purple",
            args={"f": np.cos, "mul": 3, "add": 2},
        )
    )

    assert p == "args"


def test_exceptions():
    # no mapping, no limits
    p = ggplot(data) + stat_function(fun=np.sin)
    p.draw_test()

    # fun not callable
    with pytest.raises(PlotnineError):
        p = ggplot(data, aes("x"))
        (p + stat_function(fun=1)).show()
