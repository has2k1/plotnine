import numpy as np
import pandas as pd
import pytest
import scipy.stats as stats

from plotnine import aes, geom_density, ggplot, lims, stat_function
from plotnine.exceptions import PlotnineWarning
from plotnine.stats.stat_density import nrd0

n = 6  # Some even number greater than 2

# ladder: 0 1 times, 1 2 times, 2 3 times, ...
data = pd.DataFrame(
    {
        "x": np.repeat(range(n + 1), range(n + 1)),
        "z": np.repeat(range(n // 2), range(3, n * 2, 4)),
    }
)

p = ggplot(data, aes("x", fill="factor(z)"))


def test_gaussian():
    p1 = p + geom_density(kernel="gaussian", alpha=0.3)
    assert p1 == "gaussian"


def test_gaussian_weighted():
    p1 = p + geom_density(aes(weight="x"), kernel="gaussian", alpha=0.3)
    assert p1 == "gaussian_weighted"


def test_gaussian_trimmed():
    p2 = p + geom_density(kernel="gaussian", alpha=0.3, trim=True)
    assert p2 == "gaussian-trimmed"


def test_triangular():
    p3 = p + geom_density(
        kernel="triangular", bw="normal_reference", alpha=0.3
    )  # other
    assert p3 == "triangular"


def test_few_datapoints():
    data = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3], "z": list("abbccc")})

    # Bandwidth not set
    p = ggplot(data, aes("x", color="z")) + geom_density() + lims(x=(-3, 9))
    with pytest.warns(PlotnineWarning) as record:
        p.draw_test()

    record = list(record)  # iterate more than 1 time
    assert any("e.g `bw=0.1`" in str(r.message) for r in record)
    assert any("Groups with fewer than 2" in str(r.message) for r in record)

    p = (
        ggplot(data, aes("x", color="z"))
        + geom_density(bw=0.1)
        + lims(x=(0, 4))
    )
    assert p == "few_datapoints"


def test_nrd0_uses_sd_when_iqr_is_zero():
    # As in R's bw.nrd0, the sd is used when the IQR is 0
    x = np.array([0, 0, 0, 0, 0, 0, 0, 0, 5, 10])
    bw = 0.9 * np.std(x, ddof=1) * len(x) ** -0.2
    assert nrd0(x) == pytest.approx(bw)
    assert nrd0(x[::-1]) == pytest.approx(bw)

    # When all the values are equal, the sd is 0 too
    assert nrd0(np.array([2, 2])) == pytest.approx(0.9 * 2 * 2**-0.2)
    assert nrd0(np.array([0, 0])) == pytest.approx(0.9 * 2**-0.2)


def test_bounds():
    rs = np.random.RandomState(123)
    data = pd.DataFrame({"x": rs.uniform(size=1000)})

    p = (
        ggplot(data, aes("x"))
        + geom_density()
        + geom_density(bounds=(0, 1), color="blue")
        + stat_function(fun=stats.uniform.pdf, color="red")
    )

    assert p == "bounds"
