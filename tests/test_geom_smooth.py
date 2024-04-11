import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm

from plotnine import (
    aes,
    coord_trans,
    geom_point,
    geom_smooth,
    ggplot,
    stat_smooth,
)
from plotnine.exceptions import PlotnineWarning

random_state = np.random.RandomState(1234567890)
n = 100

# linear relationship
x = np.linspace(0, 1, n)
y = 4 * x + 5
y_noisy = y + 0.1 * random_state.randn(n)
linear_data = pd.DataFrame({"x": x, "y": y, "y_noisy": y_noisy})


# non-linear relationship
x = np.linspace(-2 * np.pi, 2 * np.pi, n)
y = np.sin(x)
y_noisy = y + 0.1 * random_state.randn(n)
non_linear_data = pd.DataFrame({"x": x, "y": y, "y_noisy": y_noisy})

# discrete_x
discrete_data_x = pd.DataFrame(
    {"x": range(10), "y": [1, 2, 3, 4, 4, 5, 6, 7, 8, 9]}
)

# continuous_x
continuous_data_x = pd.DataFrame(
    {"x": np.arange(1, 21) + 0.2, "y": range(1, 21)}
)

# linear relationship, values greater than zero
n = 10
x = np.arange(1, 1 + n)
y = x + 11
y_noisy = y + random_state.rand(n)
linear_data_gtz = pd.DataFrame({"x": x, "y": y, "y_noisy": y_noisy})


def test_linear_smooth():
    p = (
        ggplot(linear_data, aes("x"))
        + geom_point(aes(y="y_noisy"))
        + geom_smooth(aes(y="y_noisy"), method="lm", span=0.3, color="blue")
    )

    assert p == "linear_smooth"


def test_linear_smooth_no_ci():
    p = (
        ggplot(linear_data, aes("x"))
        + geom_point(aes(y="y_noisy"))
        + geom_smooth(
            aes(y="y_noisy"), method="lm", span=0.3, color="blue", se=False
        )
    )

    assert p == "linear_smooth_no_ci"


def test_non_linear_smooth():
    p = (
        ggplot(linear_data, aes("x"))
        + geom_point(aes(y="y_noisy"))
        + geom_smooth(aes(y="y_noisy"), method="loess", span=0.3, color="blue")
    )

    assert p == "non_linear_smooth"


def test_non_linear_smooth_no_ci():
    p = (
        ggplot(linear_data, aes("x"))
        + geom_point(aes(y="y_noisy"))
        + geom_smooth(
            aes(y="y_noisy"), method="loess", span=0.3, color="blue", se=False
        )
    )

    assert p == "non_linear_smooth_no_ci"


def test_discrete_x():
    p = (
        ggplot(discrete_data_x, aes("x", "y"))
        + geom_point()
        + geom_smooth(color="blue")
    )

    assert p == "discrete_x"


def test_discrete_x_fullrange():
    p = (
        ggplot(discrete_data_x, aes("x", "y"))
        + geom_point()
        + geom_smooth(color="blue", fullrange=True)
    )

    assert p == "discrete_x_fullrange"


def test_continuous_x():
    n = len(continuous_data_x)
    p = (
        ggplot(continuous_data_x, aes("x", "y"))
        + geom_point()
        + geom_smooth(
            continuous_data_x[3 : n - 3],
            method="loess",
            color="blue",
            fullrange=False,
        )
    )
    assert p == "continuous_x"


def test_continuous_x_fullrange():
    n = len(continuous_data_x)
    p = (
        ggplot(continuous_data_x, aes("x", "y"))
        + geom_point()
        + geom_smooth(
            continuous_data_x[3 : n - 3],
            method="loess",
            color="blue",
            fullrange=True,
            method_args={"surface": "direct"},
        )
    )

    assert p == "continuous_x_fullrange"


def test_coord_trans_se_false():
    # scatter plot with LM fit using log-log coordinates
    p = (
        ggplot(linear_data_gtz, aes(x="x", y="y_noisy"))
        + geom_point()
        + coord_trans(x="log10", y="log10")
        + geom_smooth(method="lm", se=False)
    )
    assert p == "coord_trans_se_false"


class TestOther:
    p = ggplot(linear_data, aes("x")) + geom_point(aes(y="y_noisy"))

    def test_wls(self):
        p = self.p + geom_smooth(aes(y="y_noisy"), method="wls")
        p.draw_test()

    def test_rlm(self):
        p = self.p + geom_smooth(aes(y="y_noisy"), method="rlm")
        with pytest.warns(PlotnineWarning):
            p.draw_test()

    def test_glm(self):
        p = self.p + geom_smooth(
            aes(y="y_noisy"), method="glm", method_args={"family": "gaussian"}
        )
        p.draw_test()

    def test_gls(self):
        p = self.p + geom_smooth(aes(y="y_noisy"), method="gls")
        p.draw_test()

    def test_lowess(self):
        p = self.p + geom_smooth(aes(y="y_noisy"), method="lowess")
        with pytest.warns(PlotnineWarning):
            p.draw_test()

    def test_mavg(self):
        p = self.p + geom_smooth(
            aes(y="y_noisy"), method="mavg", method_args={"window": 10}
        )
        p.draw_test()

    def test_gpr(self):
        try:
            from sklearn import gaussian_process  # noqa: F401
        except ImportError:
            return

        p = self.p + geom_smooth(aes(y="y_noisy"), method="gpr")
        with pytest.warns(UserWarning):
            p.draw_test()


def test_sorts_by_x():
    data = pd.DataFrame({"x": [5, 0, 1, 2, 3, 4], "y": range(6)})
    p = ggplot(data, aes("x", "y")) + geom_smooth(stat="identity")

    assert p == "sorts_by_x"


def test_legend_fill_ratio():
    p = (
        ggplot(linear_data, aes("x", color="x<0.5"))
        + geom_point(aes(y="y_noisy"))
        + geom_smooth(aes(y="y_noisy"), method="lm", size=0.5, span=0.3)
    )

    assert p == "legend_fill_ratio"


def test_init_and_fit_kwargs():
    data = pd.DataFrame(
        {
            "x": np.arange(11),
            "y": [0, 0, 0, 0.05, 0.25, 0.5, 0.75, 0.95, 1, 1, 1],
        }
    )

    p = (
        ggplot(data, aes("x", "y"))
        + geom_point()
        + geom_smooth(
            method="glm",
            method_args={
                "family": sm.families.Binomial(),  # init parameter
                "method": "minimize",  # fit parameter
            },
            se=False,
        )
    )

    assert p == "init_and_fit_kwargs"


n = 100
random_state = np.random.RandomState(123)
mu = 0
sigma = 0.065
noise = random_state.randn(n) * sigma + mu
x = np.linspace(-2 * np.pi, 2 * np.pi, n)
data = pd.DataFrame(
    {
        "x": x,
        "y": np.sin(x) + noise,
    }
)


class TestFormula:
    p = ggplot(data, aes("x", "y")) + geom_point()

    def test_lm(self):
        p = self.p + stat_smooth(
            method="lm", formula="y ~ np.sin(x)", fill="red", se=True
        )
        assert p == "lm_formula"

    def test_lm_weights(self):
        p = (
            self.p
            + aes(weight="x.abs()")
            + stat_smooth(
                method="lm", formula="y ~ np.sin(x)", fill="red", se=True
            )
        )
        assert p == "lm_formula_weights"

    def test_glm(self):
        p = self.p + stat_smooth(
            method="glm", formula="y ~ np.sin(x)", fill="red", se=True
        )
        assert p == "glm_formula"

    def test_rlm(self):
        p = self.p + stat_smooth(
            method="rlm", formula="y ~ np.sin(x)", fill="red", se=False
        )

        assert p == "rlm_formula"

    def test_gls(self):
        p = self.p + stat_smooth(
            method="gls", formula="y ~ np.sin(x)", fill="red", se=True
        )
        assert p == "gls_formula"
