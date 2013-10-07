import pandas as pd
import numpy as np
from numpy import median

def lowess(x, y, f=2./3., iter=3):
    return y

def lm(x, y):
	fit = pd.ols(x=x, y=y, intercept=True)
	low = fit.y_fitted - np.std(fit.resid)
	pred = fit.y_fitted
	high = fit.y_fitted + np.std(fit.resid)
	return low.tolist(), pred, high.tolist()

def ma(y, period=10):
	pred = pd.rolling_mean(y, 10).tolist()
	low = pred - np.std(pred -  y)
	high = pred + np.std(pred -  y)
	return low, pred, high