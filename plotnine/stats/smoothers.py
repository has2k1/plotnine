from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import warnings

import numpy as np
import pandas as pd
import six
import scipy.stats as stats
import statsmodels.api as sm

from ..exceptions import PlotnineError

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
            prediction = results.get_prediction(Xseq)
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

    extrapolate = (min(xseq) < min(data['x']) or
                   max(xseq) > max(data['x']))
    if 'surface' not in kwargs and extrapolate:
        # Creates a loess model that allows extrapolation
        # when making predictions
        kwargs['surface'] = 'direct'
        warnings.warn(
            "Making prediction outside the data range, "
            "setting loess control parameter `surface='direct'`.")

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
    data.reset_index(inplace=True, drop=True)

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


# Override wls_prediction_std from statsmodels to calculate the confidence
# interval instead of only the prediction interval
def wls_prediction_std(res, exog=None, weights=None, alpha=0.05,
                       interval='confidence'):
    """
    calculate standard deviation and confidence interval

    Applies to WLS and OLS, not to general GLS,
    that is independently but not identically distributed observations

    Parameters
    ----------
    res : regression result instance
        results of WLS or OLS regression required attributes see notes
    exog : array_like (optional)
        exogenous variables for points to predict
    weights : scalar or array_like (optional)
        weights as defined for WLS (inverse of variance of observation)
    alpha : float (default: alpha = 0.05)
        confidence level for two-sided hypothesis

    Returns
    -------
    predstd : array_like, 1d
        standard error of prediction
        same length as rows of exog
    interval_l, interval_u : array_like
        lower und upper confidence bounds

    Notes
    -----
    The result instance needs to have at least the following
    res.model.predict() : predicted values or
    res.fittedvalues : values used in estimation
    res.cov_params() : covariance matrix of parameter estimates

    If exog is 1d, then it is interpreted as one observation,
    i.e. a row vector.

    testing status: not compared with other packages

    References
    ----------
    Greene p.111 for OLS, extended to WLS by analogy
    """
    # work around current bug:
    #    fit doesn't attach results to model, predict broken
    # res.model.results

    covb = res.cov_params()
    if exog is None:
        exog = res.model.exog
        predicted = res.fittedvalues
        if weights is None:
            weights = res.model.weights
    else:
        exog = np.atleast_2d(exog)
        if covb.shape[1] != exog.shape[1]:
            raise ValueError('wrong shape of exog')
        predicted = res.model.predict(res.params, exog)
        if weights is None:
            weights = 1.
        else:
            weights = np.asarray(weights)
            if weights.size > 1 and len(weights) != exog.shape[0]:
                raise ValueError('weights and exog do not have matching shape')

    # full covariance:
    # predvar = res3.mse_resid + np.diag(np.dot(X2,np.dot(covb,X2.T)))
    # predication variance only
    predvar = res.mse_resid/weights
    ip = (exog * np.dot(covb, exog.T).T).sum(1)
    if interval == 'confidence':
        predstd = np.sqrt(ip)
    elif interval == 'prediction':
        predstd = np.sqrt(ip + predvar)

    tppf = stats.t.isf(alpha/2., res.df_resid)
    interval_u = predicted + tppf * predstd
    interval_l = predicted - tppf * predstd
    return predstd, interval_l, interval_u
