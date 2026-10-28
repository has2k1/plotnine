from __future__ import annotations

import warnings
from contextlib import suppress
from typing import TYPE_CHECKING, Any, Callable, cast

import numpy as np

from .._utils import frame, get_valid_kwargs
from ..exceptions import PlotnineError, PlotnineWarning
from ._ols import add_constant, fit_least_squares
from .stat import as_frame_of

if TYPE_CHECKING:
    import statsmodels.api as sm

    from plotnine._utils.frame import DataFrame
    from plotnine.typing import FloatArray


def predictdf(data, xseq, params) -> DataFrame:
    """
    Make prediction on the data

    This is a general function responsible for dispatching
    to functions that do predictions for the specific models.
    """
    methods: dict[str, Callable[..., DataFrame]] = {
        "lm": lm,
        "ols": lm,
        "wls": lm,
        "rlm": rlm,
        "glm": glm,
        "gls": gls,
        "lowess": lowess,
        "loess": loess,
        "mavg": mavg,
        "gpr": gpr,
    }

    method = cast("str | Callable[..., DataFrame]", params["method"])

    if isinstance(method, str):
        try:
            method = methods[method]
        except KeyError as e:
            msg = f"Method should be one of {list(methods.keys())}"
            raise PlotnineError(msg) from e

    if not callable(method):
        msg = (
            "'method' should either be a string or a function"
            "with the signature `func(data, xseq, params)`"
        )
        raise PlotnineError(msg)

    if method in methods.values():
        return method(data, xseq, params)

    # A method from the user gets a native dataframe
    return as_frame_of(method(data.to_native(), xseq, params), data)


def _xyw(data: DataFrame) -> tuple[FloatArray, FloatArray, FloatArray | None]:
    """
    The x, y and weight values of the data
    """
    x = frame.to_numpy(data["x"])
    y = frame.to_numpy(data["y"])
    w = frame.to_numpy(data["weight"]) if "weight" in data.columns else None
    return x, y, w


def _values(data: DataFrame) -> dict[str, Any]:
    """
    The columns of the data as numpy arrays

    The statsmodels formulas can use them.
    """
    return {c: frame.to_numpy(data[c]) for c in data.columns}


def lm(data, xseq, params) -> DataFrame:
    """
    Fit OLS / WLS if data has weight
    """
    if params["formula"]:
        return lm_formula(data, xseq, params)

    x, y, weights = _xyw(data)
    if weights is not None and np.any(weights < 0):
        raise ValueError("All weights must be greater than zero.")

    X = add_constant(x)
    Xseq = add_constant(xseq)

    if params["method_args"]:
        # Arguments for the statsmodels model
        sm = _import_statsmodels("lm", "with method_args")
        klass = sm.OLS if weights is None else sm.WLS
        init_kwargs, fit_kwargs = separate_method_kwargs(
            params["method_args"], klass, klass.fit
        )
        if weights is not None:
            init_kwargs["weights"] = weights
        results = klass(y, X, **init_kwargs).fit(**fit_kwargs)
    else:
        results = fit_least_squares(y, X, weights)

    res = {"x": xseq, "y": results.predict(Xseq)}

    if params["se"]:
        alpha = 1 - params["level"]
        prstd, iv_l, iv_u = wls_prediction_std(results, Xseq, alpha=alpha)
        res["se"] = prstd
        res["ymin"] = iv_l
        res["ymax"] = iv_u

    return frame.frame_like(data, res)


def lm_formula(data, xseq, params) -> DataFrame:
    """
    Fit OLS / WLS using a formula
    """
    sm = _import_statsmodels("lm")
    import statsmodels.formula.api as smf

    eval_env = params["environment"].to_patsy_env()
    formula = params["formula"]
    values = _values(data)
    weights = values.get("weight", None)

    if weights is None:
        init_kwargs, fit_kwargs = separate_method_kwargs(
            params["method_args"], sm.OLS, sm.OLS.fit
        )
        model = smf.ols(formula, values, eval_env=eval_env, **init_kwargs)
    else:
        if np.any(weights < 0):
            raise ValueError("All weights must be greater than zero.")
        init_kwargs, fit_kwargs = separate_method_kwargs(
            params["method_args"], sm.OLS, sm.OLS.fit
        )
        model = smf.wls(
            formula, values, weights=weights, eval_env=eval_env, **init_kwargs
        )

    results = model.fit(**fit_kwargs)
    res = {"x": xseq}
    res["y"] = np.asarray(results.predict(res))

    if params["se"]:
        from patsy import dmatrices  # pyright: ignore

        _, predictors = dmatrices(formula, res, eval_env=eval_env)
        alpha = 1 - params["level"]
        prstd, iv_l, iv_u = wls_prediction_std(
            results, predictors, alpha=alpha
        )
        res["se"] = prstd
        res["ymin"] = iv_l
        res["ymax"] = iv_u
    return frame.frame_like(data, res)


def rlm(data, xseq, params) -> DataFrame:
    """
    Fit RLM
    """
    sm = _import_statsmodels("rlm")

    if params["formula"]:
        return rlm_formula(data, xseq, params)

    x, y, _ = _xyw(data)
    X = sm.add_constant(x)
    Xseq = sm.add_constant(xseq)

    init_kwargs, fit_kwargs = separate_method_kwargs(
        params["method_args"], sm.RLM, sm.RLM.fit
    )
    model = sm.RLM(y, X, **init_kwargs)
    results = model.fit(**fit_kwargs)

    if params["se"]:
        warnings.warn(
            "Confidence intervals are not yet implemented for RLM smoothing.",
            PlotnineWarning,
        )

    return frame.frame_like(data, {"x": xseq, "y": results.predict(Xseq)})


def rlm_formula(data, xseq, params) -> DataFrame:
    """
    Fit RLM using a formula
    """
    sm = _import_statsmodels("rlm")
    import statsmodels.formula.api as smf

    eval_env = params["environment"].to_patsy_env()
    formula = params["formula"]
    init_kwargs, fit_kwargs = separate_method_kwargs(
        params["method_args"], sm.RLM, sm.RLM.fit
    )
    model = smf.rlm(formula, _values(data), eval_env=eval_env, **init_kwargs)
    results = model.fit(**fit_kwargs)
    y = np.asarray(results.predict({"x": xseq}))

    if params["se"]:
        warnings.warn(
            "Confidence intervals are not yet implemented for RLM smoothing.",
            PlotnineWarning,
        )

    return frame.frame_like(data, {"x": xseq, "y": y})


def gls(data, xseq, params) -> DataFrame:
    """
    Fit GLS
    """
    sm = _import_statsmodels("gls")

    if params["formula"]:
        return gls_formula(data, xseq, params)

    x, y, _ = _xyw(data)
    X = sm.add_constant(x)
    Xseq = sm.add_constant(xseq)

    init_kwargs, fit_kwargs = separate_method_kwargs(
        params["method_args"], sm.OLS, sm.OLS.fit
    )
    model = sm.GLS(y, X, **init_kwargs)
    results = model.fit(**fit_kwargs)
    res = {"x": xseq, "y": results.predict(Xseq)}

    if params["se"]:
        alpha = 1 - params["level"]
        prstd, iv_l, iv_u = wls_prediction_std(results, Xseq, alpha=alpha)
        res["se"] = prstd
        res["ymin"] = iv_l
        res["ymax"] = iv_u

    return frame.frame_like(data, res)


def gls_formula(data, xseq, params):
    """
    Fit GLL using a formula
    """
    sm = _import_statsmodels("gls")
    import statsmodels.formula.api as smf

    eval_env = params["environment"].to_patsy_env()
    formula = params["formula"]
    init_kwargs, fit_kwargs = separate_method_kwargs(
        params["method_args"], sm.GLS, sm.GLS.fit
    )
    model = smf.gls(formula, _values(data), eval_env=eval_env, **init_kwargs)
    results = model.fit(**fit_kwargs)
    res = {"x": xseq}
    res["y"] = np.asarray(results.predict(res))

    if params["se"]:
        from patsy import dmatrices  # pyright: ignore

        _, predictors = dmatrices(formula, res, eval_env=eval_env)
        alpha = 1 - params["level"]
        prstd, iv_l, iv_u = wls_prediction_std(
            results, predictors, alpha=alpha
        )
        res["se"] = prstd
        res["ymin"] = iv_l
        res["ymax"] = iv_u
    return frame.frame_like(data, res)


def glm(data, xseq, params) -> DataFrame:
    """
    Fit GLM
    """
    if params["formula"]:
        return glm_formula(data, xseq, params)

    x, y, _ = _xyw(data)
    X = add_constant(x)
    Xseq = add_constant(xseq)

    if not params["method_args"]:
        # With the default gaussian family and identity link, the
        # GLM is a linear model, but the confidence interval uses the
        # normal distribution.
        import scipy.stats as stats

        results = fit_least_squares(y, X)
        res = {"x": xseq, "y": results.predict(Xseq)}
        if params["se"]:
            cov = results.cov_params()
            se = np.sqrt(np.sum(Xseq * np.dot(cov, Xseq.T).T, axis=1))
            q = stats.norm.ppf(1 - (1 - params["level"]) / 2)
            res["ymin"] = res["y"] - q * se
            res["ymax"] = res["y"] + q * se
        return frame.frame_like(data, res)

    sm = _import_statsmodels("glm", "with method_args")
    init_kwargs, fit_kwargs = separate_method_kwargs(
        params["method_args"], sm.GLM, sm.GLM.fit
    )

    if isinstance(family := init_kwargs.get("family"), str):
        init_kwargs["family"] = _glm_family(family)

    model = sm.GLM(y, X, **init_kwargs)
    results = model.fit(**fit_kwargs)
    res = {"x": xseq, "y": results.predict(Xseq)}

    if params["se"]:
        prediction = results.get_prediction(Xseq)
        ci = prediction.conf_int(alpha=1 - params["level"])
        res["ymin"] = ci[:, 0]
        res["ymax"] = ci[:, 1]

    return frame.frame_like(data, res)


def glm_formula(data, xseq, params):
    """
    Fit with GLM formula
    """
    sm = _import_statsmodels("glm")
    import statsmodels.formula.api as smf

    eval_env = params["environment"].to_patsy_env()
    init_kwargs, fit_kwargs = separate_method_kwargs(
        params["method_args"], sm.GLM, sm.GLM.fit
    )

    if isinstance(family := init_kwargs.get("family"), str):
        init_kwargs["family"] = _glm_family(family)

    model = smf.glm(
        params["formula"], _values(data), eval_env=eval_env, **init_kwargs
    )
    results = model.fit(**fit_kwargs)
    res = {"x": xseq}
    res["y"] = np.asarray(results.predict(res))

    if params["se"]:
        prediction = results.get_prediction({"x": xseq})
        ci = prediction.conf_int(alpha=1 - params["level"])
        res["ymin"] = ci[:, 0]
        res["ymax"] = ci[:, 1]
    return frame.frame_like(data, res)


def lowess(data, xseq, params) -> DataFrame:
    """
    Lowess fitting
    """
    sm = _import_statsmodels("lowess")

    for k in ("is_sorted", "return_sorted"):
        with suppress(KeyError):
            del params["method_args"][k]
            warnings.warn(f"Smoothing method argument: {k}, has been ignored.")

    x, y, _ = _xyw(data)
    result = sm.nonparametric.lowess(
        y,
        x,
        frac=params["span"],
        is_sorted=True,
        **params["method_args"],
    )

    if params["se"]:
        warnings.warn(
            "Confidence intervals are not yet implemented"
            " for lowess smoothings.",
            PlotnineWarning,
        )

    return frame.frame_like(data, {"x": result[:, 0], "y": result[:, 1]})


def loess(data, xseq, params) -> DataFrame:
    """
    Loess smoothing
    """
    try:
        from skmisc.loess import loess as loess_klass
    except ImportError as e:
        msg = "For loess smoothing, install 'scikit-misc'"
        raise PlotnineError(msg) from e

    x, y, weights = _xyw(data)
    kwargs = params["method_args"]

    extrapolate = min(xseq) < min(x) or max(xseq) > max(x)
    if "surface" not in kwargs and extrapolate:
        # Creates a loess model that allows extrapolation
        # when making predictions
        kwargs["surface"] = "direct"
        warnings.warn(
            "Making prediction outside the data range, "
            'setting loess control parameter `surface="direct"`.',
            PlotnineWarning,
        )

    if "span" not in kwargs:
        kwargs["span"] = params["span"]

    lo = loess_klass(x, y, weights, **kwargs)
    lo.fit()

    res = {"x": xseq}

    if params["se"]:
        alpha = 1 - params["level"]
        prediction = lo.predict(xseq, stderror=True)
        ci = prediction.confidence(alpha=alpha)
        res["se"] = prediction.stderr
        res["ymin"] = ci.lower
        res["ymax"] = ci.upper
    else:
        prediction = lo.predict(xseq, stderror=False)

    res["y"] = prediction.values  # noqa: PD011

    return frame.frame_like(data, res)


def mavg(data, xseq, params) -> DataFrame:
    """
    Fit moving average
    """
    method_args = params["method_args"]
    window = method_args["window"]
    x, y, _ = _xyw(data)
    n = len(data)

    # The first average comes after the full window size
    # has been swept over
    mean, std = _rolling_mean_std(y, method_args)
    res = {"x": x[window:], "y": mean[window:]}
    stderr = std[window:]

    if params["se"]:
        dof = n - window  # Original - Used
        res["ymin"], res["ymax"] = tdist_ci(
            res["y"], dof, stderr, params["level"]
        )
        res["se"] = stderr

    return frame.frame_like(data, res)


def _rolling_mean_std(
    y: FloatArray, method_args: dict[str, Any]
) -> tuple[FloatArray, FloatArray]:
    """
    Rolling mean and standard deviation

    For each value, it is the statistic of the window that ends at
    the value. The values before the first full window are NaN.
    Arguments other than the `window` require pandas, whose `rolling`
    method gets all the arguments.
    """
    if set(method_args) - {"window"}:
        import pandas as pd

        rolling = pd.Series(y).rolling(**method_args)
        return rolling.mean().to_numpy(), rolling.std().to_numpy()

    window = method_args["window"]
    mean = np.full(len(y), np.nan)
    std = np.full(len(y), np.nan)
    if 0 < window <= len(y):
        windows = np.lib.stride_tricks.sliding_window_view(y, window)
        mean[window - 1 :] = windows.mean(axis=1)
        if window > 1:
            std[window - 1 :] = windows.std(axis=1, ddof=1)
    return mean, std


def gpr(data, xseq, params):
    """
    Fit gaussian process
    """
    try:
        from sklearn import gaussian_process
    except ImportError as e:
        msg = (
            "To use gaussian process smoothing, "
            "You need to install scikit-learn."
        )
        raise PlotnineError(msg) from e

    kwargs = params["method_args"]
    if not kwargs:
        warnings.warn(
            "See sklearn.gaussian_process.GaussianProcessRegressor "
            "for parameters to pass in as 'method_args'",
            PlotnineWarning,
        )

    regressor = gaussian_process.GaussianProcessRegressor(**kwargs)
    x, y, _ = _xyw(data)
    X = np.atleast_2d(x).T
    n = len(data)
    Xseq = np.atleast_2d(xseq).T
    regressor.fit(X, y)

    res = {"x": xseq}
    if params["se"]:
        y, stderr = regressor.predict(Xseq, return_std=True)
        res["y"] = y
        res["se"] = cast("FloatArray", stderr)
        res["ymin"], res["ymax"] = tdist_ci(y, n - 1, stderr, params["level"])
    else:
        res["y"] = cast(
            "FloatArray", regressor.predict(Xseq, return_std=False)
        )

    return frame.frame_like(data, res)


def tdist_ci(x, dof, stderr, level):
    """
    Confidence Intervals using the t-distribution
    """
    import scipy.stats as stats

    q = (1 + level) / 2
    if dof is None:
        delta = stats.norm.ppf(q) * stderr
    else:
        delta = stats.t.ppf(q, dof) * stderr
    return x - delta, x + delta


# Override wls_prediction_std from statsmodels to calculate the confidence
# interval instead of only the prediction interval
def wls_prediction_std(
    res, exog=None, weights=None, alpha=0.05, interval="confidence"
):
    """
    Calculate standard deviation and confidence interval

    Applies to WLS and OLS, not to general GLS,
    that is independently but not identically distributed observations

    Parameters
    ----------
    res : regression-result
        results of WLS or OLS regression required attributes see notes
    exog : array_like
        exogenous variables for points to predict
    weights : scalar | array_like
        weights as defined for WLS (inverse of variance of observation)
    alpha : float
        confidence level for two-sided hypothesis
    interval : str
        Type of interval to compute. One of "confidence" or "prediction"

    Returns
    -------
    predstd : array_like
        Standard error of prediction. It must be the same length as rows
        of exog.
    interval_l, interval_u : array_like
        Lower und upper confidence bounds

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
    import scipy.stats as stats

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
            raise ValueError("wrong shape of exog")
        predicted = res.model.predict(res.params, exog)
        if weights is None:
            weights = 1.0
        else:
            weights = np.asarray(weights)
            if weights.size > 1 and len(weights) != exog.shape[0]:
                raise ValueError("weights and exog do not have matching shape")

    # full covariance:
    # predvar = res3.mse_resid + np.diag(np.dot(X2,np.dot(covb,X2.T)))
    # predication variance only
    predvar = res.mse_resid / weights
    ip = (exog * np.dot(covb, exog.T).T).sum(1)
    if interval == "confidence":
        predstd = np.sqrt(ip)
    elif interval == "prediction":
        predstd = np.sqrt(ip + predvar)
    else:
        raise ValueError(f"Unknown value for {interval=}")

    tppf = stats.t.isf(alpha / 2.0, res.df_resid)
    interval_u = predicted + tppf * predstd
    interval_l = predicted - tppf * predstd
    return predstd, interval_l, interval_u


def separate_method_kwargs(method_args, init_method, fit_method):
    """
    Categorise kwargs passed to the stat

    Some args are of the init method others for the fit method
    The separation is done by introspecting the init & fit methods
    """
    # inspect the methods
    init_kwargs = get_valid_kwargs(init_method, method_args)
    fit_kwargs = get_valid_kwargs(fit_method, method_args)

    # Warn about unknown kwargs
    known_kwargs = set(init_kwargs) | set(fit_kwargs)
    unknown_kwargs = set(method_args) - known_kwargs
    if unknown_kwargs:
        raise PlotnineError(
            "The following method arguments could not be recognised: "
            f"{list(unknown_kwargs)}"
        )
    return init_kwargs, fit_kwargs


def _glm_family(family: str) -> sm.families.Family:
    """
    Get glm-family instance

    Ref: https://www.statsmodels.org/stable/glm.html#families
    """
    import statsmodels.api as sm

    lookup: dict[str, type[sm.families.Family]] = {
        "binomial": sm.families.Binomial,
        "gamma": sm.families.Gamma,
        "gaussian": sm.families.Gaussian,
        "inverseGaussian": sm.families.InverseGaussian,
        "negativeBinomial": sm.families.NegativeBinomial,
        "poisson": sm.families.Poisson,
        "tweedie": sm.families.Tweedie,
    }
    try:
        return lookup[family.lower()](link=None)  # pyright: ignore
    except KeyError as err:
        msg = f"GLM family should be one of {tuple(lookup)}"
        raise ValueError(msg) from err


def _import_statsmodels(method: str, condition: str = "") -> Any:
    """
    Import statsmodels.api, with a helpful error if it is missing
    """
    try:
        import statsmodels.api as sm
    except ImportError as err:
        what = f"'{method}' {condition}".strip()
        msg = (
            f"Smoothing method {what} requires statsmodels "
            "(which requires pandas). Install them or use another method."
        )
        raise PlotnineError(msg) from err
    return sm
