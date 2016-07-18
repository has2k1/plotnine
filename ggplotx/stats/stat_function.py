from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd

from ..utils.doctools import document
from ..utils.exceptions import GgplotError
from .stat import stat


@document
class stat_function(stat):
    """
    Superimpose a function onto a plot

    {documentation}
    """
    DEFAULT_PARAMS = {'geom': 'path', 'position': 'identity',
                      'fun': None, 'n': 101, 'args': None}

    CREATES = {'y'}

    @classmethod
    def compute_group(cls, data, scales, **params):
        fun = params['fun']
        n = params['n']
        args = params['args']

        range_x = scales.x.dimension((0, 0))

        if not hasattr(fun, '__call__'):
            raise GgplotError(
                "stat_function requires parameter 'fun' to be " +
                "a function or any other callable object")

        old_fun = fun
        if isinstance(args, list):
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
        y = [fun(val) for val in x]

        new_data = pd.DataFrame({'x': x, 'y': y})
        return new_data
