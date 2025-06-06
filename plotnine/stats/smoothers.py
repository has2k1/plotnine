from __future__ import annotations

import warnings
from contextlib import suppress
from typing import TYPE_CHECKING, Callable, cast

import numpy as np
import pandas as pd

from .._utils import get_valid_kwargs
from ..exceptions import PlotnineError, PlotnineWarning

if TYPE_CHECKING:
    import statsmodels.api as sm
    from patsy.eval import EvalEnvironment

    from plotnine.mapping import Environment


def predictdf(data, xseq, params) -> pd.DataFrame:
    """
    Make prediction on the data

    This is a general function responsible for dispatching
    to functions that do predictions for the specific models.
    """
    methods: dict[str, Callable[..., pd.DataFrame]] = {
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

    method = cast("str | Callable[..., pd.DataFrame]", params["method"])

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

    return method(data, xseq, params)


def lm(data, xseq, params) -> pd.DataFrame:
    """
    Fit OLS / WLS if data has weight
    """
    import statsmodels.api as sm

    if params["formula"]:
        return lm_formula(data, xseq, params)

    X = sm.add_constant(data["x"])
    Xseq = sm.add_constant(xseq)
    weights = data.get("weights", None)

    if weights is None:
        init_kwargs, fit_kwargs = separate_method_kwargs(
            params["method_args"], sm.OLS, sm.OLS.fit
        )
        model = sm.OLS(data["y"], X, **init_kwargs)
    else:
        if np.any(weights < 0):
            raise ValueError("All weights must be greater than zero.")
        init_kwargs, fit_kwargs = separate_method_kwargs(
            params["method_args"], sm.WLS, sm.WLS.fit
        )
        model = sm.WLS(data["y"], X, weights=data["weight"], **init_kwargs)

    results = model.fit(**fit_kwargs)
    data = pd.DataFrame({"x": xseq})
    data["y"] = results.predict(Xseq)

    if params["se"]:
        alpha = 1 - params["level"]
        prstd, iv_l, iv_u = wls_prediction_std(results, Xseq, alpha=alpha)
        data["se"] = prstd
        data["ymin"] = iv_l
        data["ymax"] = iv_u

    return data


def lm_formula(data, xseq, params) -> pd.DataFrame:
    """
    Fit OLS / WLS using a formula
    """
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    eval_env = _to_patsy_env(params["environment"])
    formula = params["formula"]
    weights = data.get("weight", None)

    if weights is None:
        init_kwargs, fit_kwargs = separate_method_kwargs(
            params["method_args"], sm.OLS, sm.OLS.fit
        )
        model = smf.ols(formula, data, eval_env=eval_env, **init_kwargs)
    else:
        if np.any(weights < 0):
            raise ValueError("All weights must be greater than zero.")
        init_kwargs, fit_kwargs = separate_method_kwargs(
            params["method_args"], sm.OLS, sm.OLS.fit
        )
        model = smf.wls(
            formula, data, weights=weights, eval_env=eval_env, **init_kwargs
        )

    results = model.fit(**fit_kwargs)
    data = pd.DataFrame({"x": xseq})
    data["y"] = results.predict(data)

    if params["se"]:
        from patsy import dmatrices  # pyright: ignore

        _, predictors = dmatrices(formula, data, eval_env=eval_env)
        alpha = 1 - params["level"]
        prstd, iv_l, iv_u = wls_prediction_std(
            results, predictors, alpha=alpha
        )
        data["se"] = prstd
        data["ymin"] = iv_l
        data["ymax"] = iv_u
    return data


def rlm(data, xseq, params) -> pd.DataFrame:
    """
    Fit RLM
    """
    import statsmodels.api as sm

    if params["formula"]:
        return rlm_formula(data, xseq, params)

    X = sm.add_constant(data["x"])
    Xseq = sm.add_constant(xseq)

    init_kwargs, fit_kwargs = separate_method_kwargs(
        params["method_args"], sm.RLM, sm.RLM.fit
    )
    model = sm.RLM(data["y"], X, **init_kwargs)
    results = model.fit(**fit_kwargs)

    data = pd.DataFrame({"x": xseq})
    data["y"] = results.predict(Xseq)

    if params["se"]:
        warnings.warn(
            "Confidence intervals are not yet implemented for RLM smoothing.",
            PlotnineWarning,
        )

    return data


def rlm_formula(data, xseq, params) -> pd.DataFrame:
    """
    Fit RLM using a formula
    """
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    eval_env = _to_patsy_env(params["environment"])
    formula = params["formula"]
    init_kwargs, fit_kwargs = separate_method_kwargs(
        params["method_args"], sm.RLM, sm.RLM.fit
    )
    model = smf.rlm(formula, data, eval_env=eval_env, **init_kwargs)
    results = model.fit(**fit_kwargs)
    data = pd.DataFrame({"x": xseq})
    data["y"] = results.predict(data)

    if params["se"]:
        warnings.warn(
            "Confidence intervals are not yet implemented for RLM smoothing.",
            PlotnineWarning,
        )

    return data


def gls(data, xseq, params) -> pd.DataFrame:
    """
    Fit GLS
    """
    import statsmodels.api as sm

    if params["formula"]:
        return gls_formula(data, xseq, params)

    X = sm.add_constant(data["x"])
    Xseq = sm.add_constant(xseq)

    init_kwargs, fit_kwargs = separate_method_kwargs(
        params["method_args"], sm.OLS, sm.OLS.fit
    )
    model = sm.GLS(data["y"], X, **init_kwargs)
    results = model.fit(**fit_kwargs)

    data = pd.DataFrame({"x": xseq})
    data["y"] = results.predict(Xseq)

    if params["se"]:
        alpha = 1 - params["level"]
        prstd, iv_l, iv_u = wls_prediction_std(results, Xseq, alpha=alpha)
        data["se"] = prstd
        data["ymin"] = iv_l
        data["ymax"] = iv_u

    return data


def gls_formula(data, xseq, params):
    """
    Fit GLL using a formula
    """
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    eval_env = _to_patsy_env(params["environment"])
    formula = params["formula"]
    init_kwargs, fit_kwargs = separate_method_kwargs(
        params["method_args"], sm.GLS, sm.GLS.fit
    )
    model = smf.gls(formula, data, eval_env=eval_env, **init_kwargs)
    results = model.fit(**fit_kwargs)
    data = pd.DataFrame({"x": xseq})
    data["y"] = results.predict(data)

    if params["se"]:
        from patsy import dmatrices  # pyright: ignore

        _, predictors = dmatrices(formula, data, eval_env=eval_env)
        alpha = 1 - params["level"]
        prstd, iv_l, iv_u = wls_prediction_std(
            results, predictors, alpha=alpha
        )
        data["se"] = prstd
        data["ymin"] = iv_l
        data["ymax"] = iv_u
    return data


def glm(data, xseq, params) -> pd.DataFrame:
    """
    Fit GLM
    """
    import statsmodels.api as sm

    if params["formula"]:
        return glm_formula(data, xseq, params)

    X = sm.add_constant(data["x"])
    Xseq = sm.add_constant(xseq)

    init_kwargs, fit_kwargs = separate_method_kwargs(
        params["method_args"], sm.GLM, sm.GLM.fit
    )

    if isinstance(family := init_kwargs.get("family"), str):
        init_kwargs["family"] = _glm_family(family)

    model = sm.GLM(data["y"], X, **init_kwargs)
    results = model.fit(**fit_kwargs)

    data = pd.DataFrame({"x": xseq})
    data["y"] = results.predict(Xseq)

    if params["se"]:
        prediction = results.get_prediction(Xseq)
        ci = prediction.conf_int(alpha=1 - params["level"])
        data["ymin"] = ci[:, 0]
        data["ymax"] = ci[:, 1]

    return data


def glm_formula(data, xseq, params):
    """
    Fit with GLM formula
    """
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    eval_env = _to_patsy_env(params["environment"])
    init_kwargs, fit_kwargs = separate_method_kwargs(
        params["method_args"], sm.GLM, sm.GLM.fit
    )

    if isinstance(family := init_kwargs.get("family"), str):
        init_kwargs["family"] = _glm_family(family)

    model = smf.glm(params["formula"], data, eval_env=eval_env, **init_kwargs)
    results = model.fit(**fit_kwargs)
    data = pd.DataFrame({"x": xseq})
    data["y"] = results.predict(data)

    if params["se"]:
        xdata = pd.DataFrame({"x": xseq})
        prediction = results.get_prediction(xdata)
        ci = prediction.conf_int(alpha=1 - params["level"])
        data["ymin"] = ci[:, 0]
        data["ymax"] = ci[:, 1]
    return data


def lowess(data, xseq, params) -> pd.DataFrame:
    """
    Lowess fitting
    """
    import statsmodels.api as sm

    for k in ("is_sorted", "return_sorted"):
        with suppress(KeyError):
            del params["method_args"][k]
            warnings.warn(f"Smoothing method argument: {k}, has been ignored.")

    result = sm.nonparametric.lowess(
        data["y"],
        data["x"],
        frac=params["span"],
        is_sorted=True,
        **params["method_args"],
    )
    data = pd.DataFrame({"x": result[:, 0], "y": result[:, 1]})

    if params["se"]:
        warnings.warn(
            "Confidence intervals are not yet implemented"
            " for lowess smoothings.",
            PlotnineWarning,
        )

    return data


def loess(data, xseq, params) -> pd.DataFrame:
    """
    Loess smoothing
    """
    try:
        from skmisc.loess import loess as loess_klass
    except ImportError as e:
        msg = "For loess smoothing, install 'scikit-misc'"
        raise PlotnineError(msg) from e

    try:
        weights = data["weight"]
    except KeyError:
        weights = None

    kwargs = params["method_args"]

    extrapolate = min(xseq) < min(data["x"]) or max(xseq) > max(data["x"])
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

    lo = loess_klass(data["x"], data["y"], weights, **kwargs)
    lo.fit()

    data = pd.DataFrame({"x": xseq})

    if params["se"]:
        alpha = 1 - params["level"]
        prediction = lo.predict(xseq, stderror=True)
        ci = prediction.confidence(alpha=alpha)
        data["se"] = prediction.stderr
        data["ymin"] = ci.lower
        data["ymax"] = ci.upper
    else:
        prediction = lo.predict(xseq, stderror=False)

    data["y"] = prediction.values  # noqa: PD011

    return data


def mavg(data, xseq, params) -> pd.DataFrame:
    """
    Fit moving average
    """
    window = params["method_args"]["window"]

    # The first average comes after the full window size
    # has been swept over
    rolling = data["y"].rolling(**params["method_args"])
    y = rolling.mean()[window:]
    n = len(data)
    stderr = rolling.std()[window:]
    x = data["x"][window:]
    data = pd.DataFrame({"x": x, "y": y})
    data.reset_index(inplace=True, drop=True)

    if params["se"]:
        dof = n - window  # Original - Used
        data["ymin"], data["ymax"] = tdist_ci(y, dof, stderr, params["level"])
        data["se"] = stderr

    return data


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
    X = np.atleast_2d(data["x"]).T
    n = len(data)
    Xseq = np.atleast_2d(xseq).T
    regressor.fit(X, data["y"])

    data = pd.DataFrame({"x": xseq})
    if params["se"]:
        y, stderr = regressor.predict(Xseq, return_std=True)
        data["y"] = y
        data["se"] = stderr
        data["ymin"], data["ymax"] = tdist_ci(
            y, n - 1, stderr, params["level"]
        )
    else:
        data["y"] = regressor.predict(Xseq, return_std=True)

    return data


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


def _to_patsy_env(environment: Environment) -> EvalEnvironment:
    """
    Convert a plotnine environment to a patsy environment
    """
    from patsy.eval import EvalEnvironment

    eval_env = EvalEnvironment(environment.namespaces)
    return eval_env


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
