from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd
import pytest

from plotnine import ggplot, aes, geom_point, geom_smooth


prng = np.random.RandomState(1234567890)
n = 100

# linear relationship
x = np.linspace(0, 1, n)
y = 4*x + 5
y_noisy = y + .1*prng.randn(n)
df_linear = pd.DataFrame({'x': x, 'y': y, 'y_noisy': y_noisy})


# non-linear relationship
x = np.linspace(-2*np.pi, 2*np.pi, n)
y = np.sin(x)
y_noisy = y + .1*prng.randn(n)
df_non_linear = pd.DataFrame({'x': x, 'y': y, 'y_noisy': y_noisy})


def test_linear_smooth():
    p = (ggplot(df_linear, aes('x'))
         + geom_point(aes(y='y_noisy'))
         + geom_smooth(aes(y='y_noisy'), method='lm', span=.3,
                       color='blue')
         )

    assert p == 'linear_smooth'


def test_linear_smooth_no_ci():
    p = (ggplot(df_linear, aes('x'))
         + geom_point(aes(y='y_noisy'))
         + geom_smooth(aes(y='y_noisy'), method='lm', span=.3,
                       color='blue', se=False)
         )

    assert p == 'linear_smooth_no_ci'


def test_non_linear_smooth():
    p = (ggplot(df_linear, aes('x'))
         + geom_point(aes(y='y_noisy'))
         + geom_smooth(aes(y='y_noisy'), method='loess', span=.3,
                       color='blue')
         )

    assert p == 'non_linear_smooth'


def test_non_linear_smooth_no_ci():
    p = (ggplot(df_linear, aes('x'))
         + geom_point(aes(y='y_noisy'))
         + geom_smooth(aes(y='y_noisy'), method='loess', span=.3,
                       color='blue', se=False)
         )

    assert p == 'non_linear_smooth_no_ci'


class TestOther(object):
    p = ggplot(df_linear, aes('x')) + geom_point(aes(y='y_noisy'))

    def test_wls(self):
        p = self.p + geom_smooth(aes(y='y_noisy'), method='wls')
        p.draw_test()

    def test_rlm(self):
        p = self.p + geom_smooth(aes(y='y_noisy'), method='rlm')
        with pytest.warns(UserWarning):
            p.draw_test()

    def test_glm(self):
        p = self.p + geom_smooth(aes(y='y_noisy'), method='glm')
        p.draw_test()

    def test_lowess(self):
        p = self.p + geom_smooth(aes(y='y_noisy'), method='lowess')
        with pytest.warns(UserWarning):
            p.draw_test()

    def test_mavg(self):
        p = self.p + geom_smooth(aes(y='y_noisy'), method='mavg',
                                 method_args={'window': 10})
        p.draw_test()

    def test_gpr(self):
        try:
            from sklearn import gaussian_process  # noqa:401
        except ImportError:
            return

        p = self.p + geom_smooth(aes(y='y_noisy'), method='gpr')
        p.draw_test()
