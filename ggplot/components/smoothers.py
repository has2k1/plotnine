from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
from pandas.lib import Timestamp
import pandas as pd
import statsmodels.api as sm
from statsmodels.nonparametric.smoothers_lowess import lowess as smlowess
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from statsmodels.stats.outliers_influence import summary_table
import scipy.stats as stats

_isdate = lambda x: isinstance(x, Timestamp)
SPAN = 2/3.
ALPHA = 0.05 # significance level for confidence interval

def snakify(txt):
    txt = txt.strip().lower()
    return '_'.join(txt.split())

def plot_friendly(value):
    if not isinstance(value, (np.ndarray, pd.Series)):
        value = pd.Series(value)
    return value

def lm(x, y, alpha=ALPHA):
    "fits an OLS from statsmodels. returns tuple."
    x, y = map(plot_friendly, [x,y])
    if _isdate(x[0]):
        x = np.array([i.toordinal() for i in x])
    X = sm.add_constant(x)
    fit = sm.OLS(y, X).fit()
    prstd, iv_l, iv_u = wls_prediction_std(fit)
    _, summary_values, summary_names = summary_table(fit, alpha=alpha)
    df = pd.DataFrame(summary_values, columns=map(snakify, summary_names))
    fittedvalues        = df['predicted_value']
    predict_mean_se     = df['std_error_mean_predict']
    predict_mean_ci_low = df['mean_ci_95%_low']
    predict_mean_ci_upp = df['mean_ci_95%_upp']
    predict_ci_low      = df['predict_ci_95%_low']
    predict_ci_upp      = df['predict_ci_95%_upp']
    return (fittedvalues.tolist(), predict_mean_ci_low.tolist(),
            predict_mean_ci_upp.tolist())

def lowess(x, y, span=SPAN):
    "returns y-values estimated using the lowess function in statsmodels."
    """
    for more see
        statsmodels.nonparametric.smoothers_lowess.lowess
    """
    x, y = map(plot_friendly, [x,y])
    if _isdate(x[0]):
        x = np.array([i.toordinal() for i in x])
    result = smlowess(np.array(y), np.array(x), frac=span)
    x = pd.Series(result[::,0])
    y = pd.Series(result[::,1])
    lower, upper = stats.t.interval(span, len(x), loc=0, scale=2)
    std = np.std(y)
    y1 = pd.Series(lower * std +  y).tolist()
    y2 = pd.Series(upper * std +  y).tolist()
    return (y, y1, y2)

def mavg(x,y, window):
    "compute moving average"
    x, y = map(plot_friendly, [x,y])
    if _isdate(x[0]):
        x = np.array([i.toordinal() for i in x])
    std_err = pd.rolling_std(y, window)
    y = pd.rolling_mean(y, window)
    y1 = y - std_err
    y2 = y + std_err
    return (y, y1.tolist(), y2.tolist())
