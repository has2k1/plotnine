"""
The ports of statsmodels give the same results as statsmodels
"""

import numpy as np
import pytest

from plotnine.stats._kde import KDEUnivariate, kde_multivariate
from plotnine.stats._ols import add_constant, fit_least_squares
from plotnine.stats.smoothers import wls_prediction_std

sm = pytest.importorskip("statsmodels.api")

rng = np.random.default_rng(123)
x = np.hstack([rng.normal(0, 1, 200), rng.normal(4, 0.5, 80)])
points = np.linspace(x.min() - 1, x.max() + 1, 256)


def statsmodels_evaluate(kde, points):
    """
    Evaluate the density as plotnine did with statsmodels
    """
    try:
        y = kde.evaluate(points)
        if np.isscalar(y) and np.isnan(y):
            raise ValueError
    except ValueError:
        y = []
        for p in points:
            r = kde.evaluate(p)
            y.append(r if isinstance(r, (float, int)) else r[0])
    return np.asarray(y, dtype=float)


@pytest.mark.parametrize(
    "kernel", ["gau", "epa", "uni", "tri", "biw", "triw", "cos", "cos2"]
)
@pytest.mark.parametrize(
    "bw", ["normal_reference", "scott", "silverman", 0.3, lambda x, k: 0.4]
)
@pytest.mark.parametrize("weighted", [False, True])
def test_kde_univariate(kernel, bw, weighted):
    if kernel == "gau" and not weighted:
        fft, weights = True, None
    else:
        fft = False
        weights = rng.uniform(0.5, 2, len(x)) if weighted else None

    kwargs = {
        "kernel": kernel,
        "bw": bw,
        "fft": fft,
        "weights": weights,
        "adjust": 1.2,
        "cut": 2,
        "clip": (-1.5, np.inf),
    }
    expected = sm.nonparametric.KDEUnivariate(x).fit(**kwargs)
    result = KDEUnivariate(x).fit(**kwargs)

    assert result.bw == expected.bw
    assert result.support[0] == pytest.approx(expected.support[0])
    assert result.support[1] == pytest.approx(expected.support[-1])

    y_expected = statsmodels_evaluate(expected, points)
    y_result = result.evaluate(points)
    np.testing.assert_array_equal(np.isnan(y_result), np.isnan(y_expected))
    np.testing.assert_allclose(y_result, y_expected, rtol=1e-12)


def test_kde_univariate_errors():
    with pytest.raises(ValueError, match="Unknown kernel"):
        KDEUnivariate(x).fit(kernel="xyz")

    with pytest.raises(NotImplementedError):
        KDEUnivariate(x).fit(kernel="epa", fft=True)

    with pytest.raises(NotImplementedError):
        KDEUnivariate(x).fit(weights=np.ones(len(x)), fft=True)

    with pytest.raises(ValueError, match="not understood"):
        KDEUnivariate(x).fit(bw="xyz")

    with pytest.raises(RuntimeError, match="bandwidth is 0"):
        KDEUnivariate(np.ones(10)).fit()


def test_kde_multivariate():
    from statsmodels.nonparametric.kernel_density import KDEMultivariate

    data = np.column_stack([rng.normal(size=300), rng.normal(size=300) * 3])
    grid = np.column_stack(
        [rng.uniform(-3, 3, 1000), rng.uniform(-9, 9, 1000)]
    )
    expected = KDEMultivariate(data, var_type="cc").pdf(grid)
    result = kde_multivariate(data, grid, var_type="cc")
    np.testing.assert_allclose(result, expected, rtol=1e-14)

    # A given bandwidth
    expected = KDEMultivariate(data, var_type="cc", bw=[0.5, 1]).pdf(grid)
    result = kde_multivariate(data, grid, bw=[0.5, 1], var_type="cc")
    np.testing.assert_allclose(result, expected, rtol=1e-14)

    with pytest.raises(ValueError):
        kde_multivariate(data, grid, var_type="cu")

    with pytest.raises(ValueError):
        kde_multivariate(data, grid, bw="cv_ml")


@pytest.mark.parametrize("weighted", [False, True])
def test_least_squares(weighted):
    xs = rng.uniform(0, 10, 100)
    ys = 2 + 0.5 * xs + rng.normal(size=100)
    weights = rng.uniform(0.5, 2, 100) if weighted else None
    xseq = add_constant(np.linspace(0, 10, 20))

    X = add_constant(xs)
    np.testing.assert_array_equal(X, sm.add_constant(xs))

    if weighted:
        expected = sm.WLS(ys, X, weights=weights).fit()
    else:
        expected = sm.OLS(ys, X).fit()
    result = fit_least_squares(ys, X, weights)

    np.testing.assert_allclose(result.params, expected.params, rtol=1e-12)
    np.testing.assert_allclose(
        result.cov_params(), expected.cov_params(), rtol=1e-12
    )
    assert result.df_resid == expected.df_resid
    for a, b in zip(
        wls_prediction_std(result, xseq), wls_prediction_std(expected, xseq)
    ):
        np.testing.assert_allclose(a, b, rtol=1e-12)
