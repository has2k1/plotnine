from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd

from ..utils.exceptions import GgplotError
from .stat import stat


class stat_function(stat):
    """
    Superimpose a function onto a plot

    Uses a

    Parameters
    ----------
    x : list, 1darray
        x values of data
    fun : function
        Function to draw.
    n : int
        Number of points to interpolate over. Must be greater than zero.
        Defaults to 101.
    color : str
        Color to draw function with.
    args : list, dict, object
        List or dict of additional arguments to pass to function. If neither
        list or dict, object is passed as second argument.


    Examples
    --------

    Sin vs cos.

    .. plot::
        :include-source:

        import numpy as np
        import pandas as pd
        from ggplot import *
        gg = ggplot(pd.DataFrame({'x':np.arange(10)}), aes(x='x'))
        gg = gg + stat_function(fun=np.sin, color='red')
        gg = gg + stat_function(fun=np.cos, color='blue')
        print(gg)


    Compare random sample density to normal distribution.

    .. plot::
        :include-source:

        import numpy as np
        import pandas as pd
        from ggplot import *
        x = np.random.normal(size=100)
        # normal distribution function
        def dnorm(n):
            return (1.0 / np.sqrt(2 * np.pi)) * (np.e ** (-0.5 * (n ** 2)))
        data = pd.DataFrame({'x':x})
        gg = ggplot(aes(x='x'), data=data) + geom_density()
        gg = gg + stat_function(fun=dnorm, n=150)
        print(gg)

    Passing additional arguments to function as list.

    .. plot::
        :include-source:

        import numpy as np
        import pandas as pd
        from ggplot import *
        x = np.random.randn(100)
        to_the_power_of = lambda n, p: n ** p
        y = x ** 3
        y += np.random.randn(100) # add noise
        data = pd.DataFrame({'x':x, 'y':y})
        gg = ggplot(aes(x='x', y='y'), data=data) + geom_point()
        gg = gg + stat_function(fun=to_the_power_of, args=[3])
        print(gg)

    Passing additional arguments to function as dict.

    .. plot::
        :include-source:

        import scipy
        import numpy as np
        import pandas as pd
        from ggplot import *
        def dnorm(x, mean, var):
            return scipy.stats.norm(mean,var).pdf(x)
        data = pd.DataFrame({'x':np.arange(-5, 6)})
        gg = gg + stat_function(fun=dnorm, color='blue',
                                args={'mean':0.0, 'var':0.2})
        gg = gg + stat_function(fun=dnorm, color='red',
                                args={'mean':0.0, 'var':1.0})
        gg = gg + stat_function(fun=dnorm, color='yellow',
                                args={'mean':0.0, 'var':5.0})
        gg = gg + stat_function(fun=dnorm, color='green',
                                args={'mean':-2.0, 'var':0.5})
        gg = ggplot(aes(x='x'), data=data)
        print(gg)
    """

    DEFAULT_PARAMS = {'geom': 'path', 'position': 'identity',
                      'fun': None, 'n': 101, 'args': None}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}

    CREATES = {'y'}

    def _calculate(self, data, scales, **kwargs):
        fun = self.params['fun']
        n = self.params['n']
        args = self.params['args']

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
