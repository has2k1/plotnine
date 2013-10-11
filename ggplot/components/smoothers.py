import numpy as np
from pandas.lib import Timestamp
import pandas as pd
import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from statsmodels.nonparametric.smoothers_lowess import lowess as smlowess
import scipy.stats as stats

_isdate = lambda x: isinstance(x, Timestamp)
SPAN = 2/3.

def _plot_friendly(value):
    if not isinstance(value, (np.ndarray, pd.Series)):
        value = pd.Series(value)
    return value

def lm(x, y):
    "fits an OLS from statsmodels. returns tuple."
    x, y = map(_plot_friendly, [x,y])
    if _isdate(x[0]):
        x = np.array([i.toordinal() for i in x])
    df = pd.DataFrame({'x': x, 'y':y})
    df['const'] = 1.
    fit = sm.OLS(df.y,df[['x','const']]).fit()
    df['predicted_y'] = fit.fittedvalues
    df['predstd'],df['interval_l'],df['interval_u'] = wls_prediction_std(fit)
    return (df.predicted_y, df.interval_l, df.interval_u)

def lowess(x, y, span=SPAN):
    "returns y-values estimated using the lowess function in statsmodels."
    """
    for more see
        statsmodels.nonparametric.smoothers_lowess.lowess
    """
    x, y = map(_plot_friendly, [x,y])
    if _isdate(x[0]):
        x = np.array([i.toordinal() for i in x])
    result = smlowess(np.array(y), np.array(x), frac=span)
    x = pd.Series(result[::,0])
    y = pd.Series(result[::,1])
    lower, upper = stats.t.interval(span, len(x), loc=0, scale=2)
    std = np.std(y)
    y1 = pd.Series(lower * std +  y)
    y2 = pd.Series(upper * std +  y)
    return (y, y1, y2)

def mavg(x,y, span=SPAN):
    "compute moving average"
    x, y = map(_plot_friendly, [x,y])
    if _isdate(x[0]):
        x = np.array([i.toordinal() for i in x])
    std_err = pd.expanding_std(y, span)
    y = pd.rolling_mean(y, span)
    y1 = y - std_err
    y2 = y + std_err
    return (y, y1, y2)
