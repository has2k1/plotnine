import warnings

import numpy as np
import pandas as pd

from ..doctools import document
from ..exceptions import PlotnineWarning
from .smoothers import predictdf
from .stat import stat


@document
class stat_smooth(stat):
    """
    Calculate a smoothed conditional mean

    {usage}

    Parameters
    ----------
    {common_parameters}

    method : str or callable, optional (default: 'auto')
        The available methods are::

            'auto'       # Use loess if (n<1000), glm otherwise
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
    formula : formula_like
        An object that can be used to construct a patsy design matrix.
        This is usually a string. You can only use a formula if ``method``
        is one of *lm*, *ols*, *wls*, *glm*, *rlm* or *gls*, and in the
        :ref:`formula <patsy:formulas>` you may refer to the ``x`` and
        ``y`` aesthetic variables.
    se : bool (default: True)
        If :py:`True` draw confidence interval around the smooth line.
    n : int (default: 80)
        Number of points to evaluate the smoother at. Some smoothers
        like *mavg* do not support this.
    fullrange : bool (default: False)
        If :py:`True` the fit will span the full range of the plot.
    level : float (default: 0.95)
        Level of confidence to use if :py:`se=True`.
    span : float (default: 2/3.)
        Controls the amount of smoothing for the *loess* smoother.
        Larger number means more smoothing. It should be in the
        ``(0, 1)`` range.
    method_args : dict (default: {})
        Additional arguments passed on to the modelling method.

    See Also
    --------
    statsmodels.regression.linear_model.OLS
    statsmodels.regression.linear_model.WLS
    statsmodels.robust.robust_linear_model.RLM
    statsmodels.genmod.generalized_linear_model.GLM
    statsmodels.regression.linear_model.GLS
    statsmodels.nonparametric.smoothers_lowess.lowess
    skmisc.loess.loess
    pandas.DataFrame.rolling
    sklearn.gaussian_process.GaussianProcessRegressor

    Notes
    -----
    :class:`~plotnine.geoms.geom_smooth` and :class:`.stat_smooth` are
    effectively aliases, they both use the same arguments.
    Use :class:`~plotnine.geoms.geom_smooth` unless
    you want to display the results with a non-standard geom.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    .. rubric:: Options for computed aesthetics

    ::

         'se'    # Standard error of points in bin
         'ymin'  # Lower confidence limit
         'ymax'  # Upper confidence limit

    Calculated aesthetics are accessed using the `stat` function.
    e.g. :py:`'stat(se)'`.
    """

    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'smooth', 'position': 'identity',
                      'na_rm': False,
                      'method': 'auto', 'se': True, 'n': 80,
                      'formula': None,
                      'fullrange': False, 'level': 0.95,
                      'span': 0.75, 'method_args': {}}
    CREATES = {'se', 'ymin', 'ymax'}

    def setup_data(self, data):
        """
        Overide to modify data before compute_layer is called
        """
        data = data[np.isfinite(data['x']) &
                    np.isfinite(data['y'])]
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
                    "facets".format(window), PlotnineWarning)
                params['method_args']['window'] = window

        if params['formula']:
            allowed = {'lm', 'ols', 'wls', 'glm', 'rlm', 'gls'}
            if params['method'] not in allowed:
                raise ValueError(
                    "You can only use a formula with `method` is "
                    "one of {}".format(allowed)
                )
            params['enviroment'] = self.environment

        return params

    @classmethod
    def compute_group(cls, data, scales, **params):
        data = data.sort_values('x')
        n = params['n']

        x_unique = data['x'].unique()

        if len(x_unique) < 2:
            warnings.warn(
                "Smoothing requires 2 or more points. Got {}. "
                "Not enough points for smoothing. If this message "
                "a surprise, make sure the column mapped to the x "
                "aesthetic has the right dtype.".format(len(x_unique)),
                PlotnineWarning
            )
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

        return predictdf(data, xseq, **params)
