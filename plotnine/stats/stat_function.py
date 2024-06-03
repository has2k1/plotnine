from __future__ import annotations

import typing

import numpy as np
import pandas as pd

from ..doctools import document
from ..exceptions import PlotnineError
from ..mapping.evaluation import after_stat
from ..scales.scale_continuous import scale_continuous
from .stat import stat

if typing.TYPE_CHECKING:
    from typing import Callable

    from plotnine.typing import FloatArrayLike


@document
class stat_function(stat):
    """
    Superimpose a function onto a plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    fun : callable
        Function to evaluate.
    n : int, default=101
        Number of points at which to evaluate the function.
    xlim : tuple, default=None
        `x` limits for the range. The default depends on
        the `x` aesthetic. There is not an `x` aesthetic
        then the `xlim` must be provided.
    args : Optional[tuple[Any] | dict[str, Any]], default=None
        Arguments to pass to `fun`.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "x"   # x points at which the function is evaluated
    "fx"  # points evaluated at each x
    ```

    """

    DEFAULT_PARAMS = {
        "geom": "path",
        "position": "identity",
        "na_rm": False,
        "fun": None,
        "n": 101,
        "args": None,
        "xlim": None,
    }

    DEFAULT_AES = {"y": after_stat("fx")}
    CREATES = {"fx"}

    def __init__(self, mapping=None, data=None, **kwargs):
        if data is None:

            def _data_func(data: pd.DataFrame) -> pd.DataFrame:
                if data.empty:
                    data = pd.DataFrame({"group": [1]})
                return data

            data = _data_func

        super().__init__(mapping, data, **kwargs)

    def setup_params(self, data):
        if not callable(self.params["fun"]):
            raise PlotnineError(
                "stat_function requires parameter 'fun' to be "
                "a function or any other callable object"
            )
        return self.params

    @classmethod
    def compute_group(cls, data, scales, **params):
        old_fun: Callable[..., FloatArrayLike] = params["fun"]
        n = params["n"]
        args = params["args"]
        xlim = params["xlim"]
        range_x = xlim or scales.x.dimension((0, 0))

        if isinstance(args, (list, tuple)):

            def fun(x):
                return old_fun(x, *args)

        elif isinstance(args, dict):

            def fun(x):
                return old_fun(x, **args)

        elif args is not None:

            def fun(x):
                return old_fun(x, args)

        else:

            def fun(x):
                return old_fun(x)

        x = np.linspace(range_x[0], range_x[1], n)

        # continuous scale
        if isinstance(scales.x, scale_continuous):
            x = scales.x.inverse(x)

        # We know these can handle array_likes
        if isinstance(old_fun, (np.ufunc, np.vectorize)):
            fx = fun(x)
        else:
            fx = [fun(val) for val in x]

        new_data = pd.DataFrame({"x": x, "fx": fx})
        return new_data
