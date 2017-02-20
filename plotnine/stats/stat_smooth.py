from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import warnings

import numpy as np
import pandas as pd

from ..utils.doctools import document
from ..utils import smoothers
from .stat import stat


@document
class stat_smooth(stat):
    """
    Calculate a smoothed conditional mean

    {usage}

    Parameters
    ----------
    {common_parameters}

    Parameters
    ----------
    method : str or callable, optional
        The available methods are::

            'lm', 'ols'  # Linear Model
            'wls'        # Weighted Linear Model
            'rlm'        # Robust Linear Model
            'glm'        # Generalized linear Model
            'gls'        # Generalized Least Squares
            'lowess'     # Locally Weighted Regression (simple)
            'loess'      # Locally Weighted Regression
            'mavg'       # Moving Average
            'gpr'        # Gaussian Process Regressor

        If a `callable` is passed, it must have the signature::

            def my_smoother(data, xseq, **params):
                # * data - has the x and y values for the model
                # * xseq - x values to be predicted
                # * params - stat parameters
                #
                # It must return a new dataframe. Below is the
                # template used internally by Plotnine

                # Input data into the model
                x, y = data['x'], data['y']

                # Create and fit a model
                model = Model(x, y)
                results = Model.fit()

                # Create output data by getting predictions on
                # the xseq values
                data = pd.DataFrame({
                    'x': xseq,
                    'y': results.predict(xseq)})

                # Compute confidence intervals, this depends on
                # the model. However, given standard errors and the
                # degrees of freedom we can compute the confidence
                # intervals using the t-distribution.
                #
                # For an alternative, implement confidence interals by
                # the bootstrap method
                if params['se']:
                    from plotnine.utils.smoothers import tdist_ci
                    y = data['y']            # The predicted value
                    df = 123                 # Degrees of freedom
                    stderr = results.stderr  # Standard error
                    level = params['level']  # The parameter value
                    low, high = tdist_ci(y, df, stderr, level)
                    data['se'] = stderr
                    data['ymin'] = low
                    data['ymax'] = high

                return data

    {aesthetics}

    Note
    ----
    :class:`~plotnine.geoms.geom_smooth` and :class:`.stat_smooth` are
    effectively aliases, they both use the same arguments.
    Use :class:`~plotnine.geoms.geom_smooth` unless
    you want to display the results with a non-standard geom.
    """
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'smooth', 'position': 'identity',
                      'method': 'auto', 'se': True, 'n': 80,
                      'fullrange': False, 'level': 0.95,
                      'span': 2/3., 'method_args': {}}
    CREATES = {'se', 'ymin', 'ymax'}

    def setup_data(self, data):
        """
        Overide to modify data before compute_layer is called
        """
        data = data[np.isfinite(data['x']) &
                    np.isfinite(data['y'])]
        data.is_copy = None
        return data

    def setup_params(self, data):
        params = self.params.copy()
        # Use loess/lowess for small datasets
        # and glm for large
        if params['method'] == 'auto':
            max_group = data['group'].value_counts().max()
            if max_group < 1000:
                try:
                    from skmisc.loess import loess  # noqa: F401
                    params['method'] = 'loess'
                except ImportError:
                    params['method'] = 'lowess'
            else:
                params['method'] = 'glm'

        if params['method'] == 'mavg':
            if 'window' not in params['method_args']:
                window = len(data) // 10
                warnings.warn(
                    "No 'window' specified in the method_args. "
                    "Using window = {}. "
                    "The same window is used for all groups or "
                    "facets".format(window))
                params['method_args']['window'] = window

        return params

    @classmethod
    def compute_group(cls, data, scales, **params):
        data = data.sort_values('x')
        n = params['n']

        x_unique = data['x'].unique()

        if len(x_unique) < 2:
            # Not enough data to fit
            return pd.DataFrame()

        if data['x'].dtype.kind == 'i':
            if params['fullrange']:
                xseq = scales.x.dimension()
            else:
                xseq = np.sort(x_unique)
        else:
            if params['fullrange']:
                rangee = scales.x.dimension()
            else:
                rangee = [data['x'].min(), data['x'].max()]
            xseq = np.linspace(rangee[0], rangee[1], n)

        return smoothers.predictdf(data, xseq, **params)
