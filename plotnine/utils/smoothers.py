from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import warnings

import numpy as np
import pandas as pd
import six
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std

from ..utils.exceptions import PlotnineError

smlowess = sm.nonparametric.lowess


def predictdf(data, xseq, **params):
    methods = {
        'lm': lm,
        'ols': lm,
        'wls': lm,
        'rlm': rlm,
        'glm': glm,
        'gls': gls,
        'lowess': lowess,
        'loess': loess,
        'mavg': mavg,
        'gpr': gpr,
    }

    method = params['method']

    if isinstance(method, six.string_types):
        try:
            method = methods[method]
        except KeyError:
            msg = "Method should be one of {}"
            raise PlotnineError(msg.format(list(methods.keys())))

    if not hasattr(method, '__call__'):
        msg = ("'method' should either be a string or a function"
               "with the signature `func(data, xseq, **params)`")
        raise PlotnineError()

    return method(data, xseq, **params)


def lm(data, xseq, **params):
    """
    Fit OLS / WLS if data has weight
    """
    X = sm.add_constant(data['x'])
    Xseq = sm.add_constant(xseq)

    try:
        model = sm.WLS(data['y'], X, weights=data['weight'])
    except KeyError:
        model = sm.OLS(data['y'], X)

    results = model.fit(**params['method_args'])
    data = pd.DataFrame({'x': xseq})
    data['y'] = results.predict(Xseq)

    if params['se']:
        alpha = 1 - params['level']
        prstd, iv_l, iv_u = wls_prediction_std(
            results, Xseq, alpha=alpha)
        data['se'] = prstd
        data['ymin'] = iv_l
        data['ymax'] = iv_u

    return data


def rlm(data, xseq, **params):
    """
    Fit RLM
    """
    X = sm.add_constant(data['x'])
    Xseq = sm.add_constant(xseq)
    results = sm.RLM(data['y'], X).fit(**params['method_args'])
    data = pd.DataFrame({'x': xseq})
    data['y'] = results.predict(Xseq)

    if params['se']:
        warnings.warn("Confidence intervals are not yet implemented"
                      "for RLM smoothing.")

    return data


def gls(data, xseq, **params):
    """
    Fit GLS
    """
    X = sm.add_constant(data['x'])
    Xseq = sm.add_constant(xseq)
    results = sm.GLS(data['y'], X).fit(**params['method_args'])
    data = pd.DataFrame({'x': xseq})
    data['y'] = results.predict(Xseq)

    if params['se']:
        alpha = 1 - params['level']
        prstd, iv_l, iv_u = wls_prediction_std(
            results, Xseq, alpha=alpha)
        data['se'] = prstd
        data['ymin'] = iv_l
        data['ymax'] = iv_u

    return data


def glm(data, xseq, **params):
    """
    Fit GLM
    """
    X = sm.add_constant(data['x'])
    Xseq = sm.add_constant(xseq)
    results = sm.GLM(data['y'], X).fit(**params['method_args'])
    data = pd.DataFrame({'x': xseq})
    data['y'] = results.predict(Xseq)

    if params['se']:
        # TODO: Depends on statsmodel > 0.7
        # https://github.com/statsmodels/statsmodels/pull/2151
        # https://github.com/statsmodels/statsmodels/pull/3406
        # Remove the try/except when a compatible version is released
        try:
            prediction = results.get_prediction(X)
            ci = prediction.conf_int(1 - params['level'])
            data['ymin'] = ci[:, 0]
            data['ymax'] = ci[:, 1]
        except (AttributeError, TypeError):
            warnings.warn(
                "Cannot compute confidence intervals."
                "Install latest/development version of statmodels.")

    return data


def lowess(data, xseq, **params):
    result = smlowess(data['y'], data['x'],
                      frac=params['span'],
                      is_sorted=True)
    data = pd.DataFrame({
        'x': result[:, 0],
        'y': result[:, 1]})

    if params['se']:
        warnings.warn("Confidence intervals are not yet implemented"
                      "for lowess smoothings.")

    return data


def loess(data, xseq, **params):
    try:
        from skmisc.loess import loess as loess_klass
    except ImportError:
        raise PlotnineError(
            "For loess smoothing, install 'scikit-misc'")

    try:
        weights = data['weight']
    except KeyError:
        weights = None

    kwargs = params['method_args']
    if 'span' not in kwargs:
        kwargs['span'] = params['span']
    lo = loess_klass(data['x'], data['y'], weights, **kwargs)
    lo.fit()

    data = pd.DataFrame({'x': xseq})

    if params['se']:
        alpha = 1 - params['level']
        prediction = lo.predict(xseq, stderror=True)
        ci = prediction.confidence(alpha=alpha)
        data['se'] = prediction.stderr
        data['ymin'] = ci.lower
        data['ymax'] = ci.upper
    else:
        prediction = lo.predict(xseq, stderror=False)

    data['y'] = prediction.values

    return data


def mavg(data, xseq, **params):
    """
    Fit moving average
    """
    window = params['method_args']['window']

    # The first average comes after the full window size
    # has been swept over
    rolling = data['y'].rolling(**params['method_args'])
    y = rolling.mean()[window:]
    n = len(data)
    stderr = rolling.std()[window:]
    x = data['x'][window:]
    data = pd.DataFrame({'x': x, 'y': y})

    if params['se']:
        df = n - window  # Original - Used
        data['ymin'], data['ymax'] = tdist_ci(
            y, df, stderr, params['level'])
        data['se'] = stderr

    return data


def gpr(data, xseq, **params):
    """
    Fit gaussian process
    """
    try:
        from sklearn import gaussian_process
    except ImportError:
        raise PlotnineError(
            "To use gaussian process smoothing, "
            "You need to install scikit-learn.")

    kwargs = params['method_args']
    if not kwargs:
        warnings.warn(
            "See sklearn.gaussian_process.GaussianProcessRegressor "
            "for parameters to pass in as 'method_args'")

    regressor = gaussian_process.GaussianProcessRegressor(**kwargs)
    X = np.atleast_2d(data['x']).T
    n = len(data)
    Xseq = np.atleast_2d(xseq).T
    regressor.fit(X, data['y'])

    data = pd.DataFrame({'x': xseq})
    if params['se']:
        y, stderr = regressor.predict(Xseq, return_std=True)
        data['y'] = y
        data['se'] = stderr
        data['ymin'], data['ymax'] = tdist_ci(
            y, n-1, stderr, params['level'])
    else:
        data['y'] = regressor.predict(Xseq, return_std=True)

    return data


def tdist_ci(x, df, stderr, level):
    """
    Confidence Intervals using the t-distribution
    """
    q = (1 + level)/2
    delta = stats.t.ppf(q, df) * stderr
    return x - delta, x + delta
