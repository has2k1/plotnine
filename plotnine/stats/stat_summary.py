from __future__ import annotations

from typing import TYPE_CHECKING

import narwhals as nw
import numpy as np

from .._utils import (
    frame,
    get_valid_kwargs,
    normalise_random_state,
    uniquecols,
)
from ..doctools import document
from ..exceptions import PlotnineError
from .stat import as_frame_of, stat

if TYPE_CHECKING:
    from typing import Any, Callable

    from plotnine._utils.frame import DataFrame, Series


def bootstrap_statistics(
    series,
    statistic,
    n_samples=1000,
    confidence_interval=0.95,
    random_state=None,
):
    """
    Default parameters taken from
    R's Hmisc smean.cl.boot
    """
    if random_state is None:
        random_state = np.random

    a = frame.as_numpy(series)
    alpha = 1 - confidence_interval
    size = (n_samples, len(a))
    if isinstance(random_state, np.random.Generator):
        inds = random_state.integers(0, len(a), size=size)
    else:
        inds = random_state.randint(0, len(a), size=size)
    samples = a[inds]
    means = np.sort(statistic(samples, axis=1))
    return _summary_frame(
        series,
        {
            "ymin": means[int((alpha / 2) * n_samples)],
            "ymax": means[int((1 - alpha / 2) * n_samples)],
            "y": [statistic(a)],
        },
    )


def mean_cl_boot(
    series, n_samples=1000, confidence_interval=0.95, random_state=None
):
    """
    Bootstrapped mean with confidence interval

    Parameters
    ----------
    series : array_like
        Values
    n_samples : int, default=1000
        Number of sample to draw.
    confidence_interval : float
        Confidence interval in the range (0, 1).
    random_state :
        Integer seed, [](`~numpy.random.RandomState`), or
        [](`numpy.random.Generator`). If `None`, draw from NumPy's global
        random state.
    """
    return bootstrap_statistics(
        series,
        np.mean,
        n_samples=n_samples,
        confidence_interval=confidence_interval,
        random_state=random_state,
    )


def mean_cl_normal(series, confidence_interval=0.95):
    """
    Mean with confidence interval assuming normal distribution

    Credit: from http://stackoverflow.com/a/15034143

    Parameters
    ----------
    series : array_like
        Values
    confidence_interval : float
        Confidence interval in the range (0, 1).
    """
    import scipy.stats as stats

    a = frame.as_numpy(series)
    m = np.mean(a)
    se = stats.sem(a)
    h = se * stats.t._ppf((1 + confidence_interval) / 2, len(a) - 1)
    return _summary_frame(series, {"y": [m], "ymin": m - h, "ymax": m + h})


def mean_sdl(series, mult=2):
    """
    Mean +/- a constant times the standard deviation

    Parameters
    ----------
    series : array_like
        Values
    mult : float
        Multiplication factor.
    """
    a = frame.as_numpy(series)
    m = np.mean(a)
    s = np.std(a, ddof=1)
    return _summary_frame(
        series, {"y": [m], "ymin": m - mult * s, "ymax": m + mult * s}
    )


def median_hilow(series, confidence_interval=0.95):
    """
    Median and a selected pair of outer quantiles having equal tail areas

    Parameters
    ----------
    series : array_like
        Values
    confidence_interval : float
        Confidence interval in the range (0, 1).
    """
    a = frame.as_numpy(series)
    tail = (1 - confidence_interval) / 2
    return _summary_frame(
        series,
        {
            "y": [np.median(a)],
            "ymin": np.percentile(a, 100 * tail),
            "ymax": np.percentile(a, 100 * (1 - tail)),
        },
    )


def mean_se(series, mult=1):
    """
    Calculate mean and standard errors on either side

    Parameters
    ----------
    series : array_like
        Values
    mult : float
        Multiplication factor.
    """
    a = frame.as_numpy(series)
    m = np.mean(a)
    # ddof=1: the standard error of the mean is built from the sample
    # variance. numpy defaults to ddof=0, which is the population
    # variance and understates the error by a factor of sqrt((n-1)/n).
    se = mult * np.sqrt(np.var(a, ddof=1) / len(a))
    return _summary_frame(series, {"y": [m], "ymin": m - se, "ymax": m + se})


function_dict = {
    "mean_cl_boot": mean_cl_boot,
    "mean_cl_normal": mean_cl_normal,
    "mean_sdl": mean_sdl,
    "median_hilow": median_hilow,
    "mean_se": mean_se,
}


def _call(fun: Callable[..., Any], y: Series, kwargs: dict[str, Any]) -> Any:
    """
    Call a summary function

    The function gets the native series of the values, e.g. a
    pandas series. If that raises a TypeError, which happens when a
    numpy function like np.mean gets a polars series, the function
    gets a numpy array.
    """
    try:
        return fun(y.to_native(), **kwargs)
    except TypeError:
        return fun(frame.to_numpy(y), **kwargs)


def make_summary_fun(fun_data, fun_y, fun_ymin, fun_ymax, fun_args):
    """
    Make summary function

    The summary functions get the native series of the `y` values,
    e.g. a pandas series when the data is a pandas dataframe.
    """
    if isinstance(fun_data, str):
        fun_data = function_dict[fun_data]

    if any([fun_y, fun_ymin, fun_ymax]):

        def func(df: DataFrame) -> DataFrame:
            d = {}
            if fun_y:
                kwargs = get_valid_kwargs(fun_y, fun_args)
                d["y"] = [_call(fun_y, df["y"], kwargs)]
            if fun_ymin:
                kwargs = get_valid_kwargs(fun_ymin, fun_args)
                d["ymin"] = [_call(fun_ymin, df["y"], kwargs)]
            if fun_ymax:
                kwargs = get_valid_kwargs(fun_ymax, fun_args)
                d["ymax"] = [_call(fun_ymax, df["y"], kwargs)]
            return frame.frame_like(df, d)

    elif fun_data:
        kwargs = get_valid_kwargs(fun_data, fun_args)

        def func(df: DataFrame) -> DataFrame:
            return as_frame_of(_call(fun_data, df["y"], kwargs), df)

    else:
        raise ValueError(f"Bad value for function fun_data={fun_data}")

    return func


@document
class stat_summary(stat):
    """
    Calculate summary statistics depending on x

    {usage}

    Parameters
    ----------
    {common_parameters}
    fun_data : str | callable, default="mean_cl_boot"
        If string, it should be one of:

        ```python
        # Bootstrapped mean, confidence interval
        # Arguments:
        #     n_samples - No. of samples to draw
        #     confidence_interval
        #     random_state
        "mean_cl_boot"

        # Mean, C.I. assuming normal distribution
        # Arguments:
        #     confidence_interval
        "mean_cl_normal"

        # Mean, standard deviation * constant
        # Arguments:
        #     mult - multiplication factor
        "mean_sdl"

        # Median, outlier quantiles with equal tail areas
        # Arguments:
        #     confidence_interval
        "median_hilow"

        # Mean, Standard Errors * constant
        # Arguments:
        #     mult - multiplication factor
        "mean_se"
        ```

        or any function that takes a array and returns a dataframe
        with three columns named `y`, `ymin` and `ymax`.
    fun_y : callable, default=None
        Any function that takes a array_like and returns a value
    fun_ymin : callable, default=None
        Any function that takes an array_like and returns a value
    fun_ymax : callable, default=None
        Any function that takes an array_like and returns a value
    fun_args : dict, default=None
        Arguments to any of the functions. Provided the names of the
        arguments of the different functions are in not conflict, the
        arguments will be assigned to the right functions. If there is
        a conflict, create a wrapper function that resolves the
        ambiguity in the argument names.
    random_state :
        Integer seed, [](`~numpy.random.RandomState`), or
        [](`numpy.random.Generator`). If `None`, draw from NumPy's global
        random state.

    Notes
    -----
    If any of `fun_y`, `fun_ymin` or `fun_ymax` are provided, the
    value of `fun_data` will be ignored.

    See Also
    --------
    plotnine.geom_pointrange : The default `geom` for this `stat`.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "ymin"  # ymin computed by the summary function
    "ymax"  # ymax computed by the summary function
    "n"     # Number of observations at a position
    ```

    Calculated aesthetics are accessed using the `after_stat` function.
    e.g. `after_stat('ymin')`{.py}.
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "geom": "pointrange",
        "fun_data": "mean_cl_boot",
        "fun_y": None,
        "fun_ymin": None,
        "fun_ymax": None,
        "fun_args": None,
        "random_state": None,
    }
    CREATES = {"ymin", "ymax", "n"}

    def setup_params(self, data):
        keys = ("fun_data", "fun_y", "fun_ymin", "fun_ymax")
        if not any(self.params[k] for k in keys):
            raise PlotnineError("No summary function")

        if self.params["fun_args"] is None:
            self.params["fun_args"] = {}

        if (
            "random_state" not in self.params["fun_args"]
            and self.params["random_state"] is not None
        ):
            self.params["fun_args"]["random_state"] = normalise_random_state(
                self.params["random_state"]
            )

    def compute_panel(self, data, scales):
        func = make_summary_fun(
            self.params["fun_data"],
            self.params["fun_y"],
            self.params["fun_ymin"],
            self.params["fun_ymax"],
            self.params["fun_args"],
        )

        # break a dataframe into pieces, summarise each piece,
        # and join the pieces back together, retaining original
        # columns unaffected by the summary.
        summaries = []
        for (group, x), df in frame.group_split(data, ["group", "x"]):
            summary = frame.assign(func(df), x=x, group=group, n=len(df))
            unique = uniquecols(df)
            extra = [c for c in unique.columns if c not in summary.columns]
            if extra:
                unique = frame.take(unique.select(extra), [0] * len(summary))
                summary = nw.concat([summary, unique], how="horizontal")
            summaries.append(summary)

        return frame.concat(summaries)


def _summary_frame(series: Any, data: dict[str, Any]) -> Any:
    """
    Create a summary dataframe of the same library as the series

    The dataframe is native, e.g. a pandas dataframe for a pandas
    series. For a numpy array, it is of the default library.
    """
    backend = frame.backend_of(series)
    return frame.frame(data, backend=backend).to_native()
