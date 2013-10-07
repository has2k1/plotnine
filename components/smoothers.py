import pandas as pd

def lm(x, y):
    fit = pd.ols(x=x, y=y, intercept=True)
    low = fit.y_fitted - np.std(fit.resid)
    pred = fit.y_fitted
    high = fit.y_fitted + np.std(fit.resid)
    return low.tolist(), pred, high.tolist()
