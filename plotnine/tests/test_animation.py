from __future__ import absolute_import, division, print_function

import pytest
import matplotlib.pyplot as plt

from plotnine import qplot, lims, labs, theme, theme_minimal
from plotnine.animation import PlotnineAnimation
from plotnine.exceptions import PlotnineError

plt.switch_backend('Agg')  # TravisCI needs this
_theme = theme(subplots_adjust={'right': 0.80})

x = [1, 2, 3, 4, 5]
y = [1, 2, 3, 4, 5]
colors = [[1, 2, 3, 4, 5],
          [2, 3, 4, 5, 6],
          [3, 4, 5, 6, 7]]


class _PlotnineAnimation(PlotnineAnimation):
    """
    Class used for testing

    By using this class we only test the creation of
    artists and not the animation. This tests all the
    plotnine wrapper code and we can trust matplotlib
    for the rest.
    """
    def __init__(self, plots, interval=200, repeat_delay=None,
                 repeat=True, blit=False):
        figure, artists = self._draw_plots(plots)


def test_animation():
    def plot(i):
        return (qplot(x, y, color=colors[i], xlab='x', ylab='y')
                + lims(color=(1, 7))
                + labs(color='color')
                + theme_minimal()
                + _theme
                )

    plots = [plot(i) for i in range(3)]
    _PlotnineAnimation(plots, interval=100, repeat_delay=500)


def test_animation_different_scale_limits():
    def plot(i):
        if i == 2:
            _lims = lims(color=(3, 7))
        else:
            _lims = lims(color=(1, 7))
        return (qplot(x, y, color=colors[i], xlab='x', ylab='y')
                + _lims
                + labs(color='color')
                + theme_minimal()
                + _theme
                )
    plots = [plot(i) for i in range(3)]
    with pytest.raises(PlotnineError):
        _PlotnineAnimation(plots, interval=100, repeat_delay=500)


def test_animation_different_number_of_scales():
    def plot(i):
        if i == 2:
            p = qplot(x, y, xlab='x', ylab='y')
        else:
            p = (qplot(x, y, color=colors[i], xlab='x', ylab='y')
                 + lims(color=(1, 7))
                 + labs(color='color'))

        return p + theme_minimal()

    plots = [plot(i) for i in range(3)]
    with pytest.raises(PlotnineError):
        _PlotnineAnimation(plots, interval=100, repeat_delay=500)


def test_animation_different_scales():
    def plot(i):
        c = colors[i]
        if i == 2:
            p = (qplot(x, y, color=c, xlab='x', ylab='y')
                 + lims(color=(1, 7))
                 + labs(color='color'))
        else:
            p = (qplot(x, y, stroke=c, xlab='x', ylab='y')
                 + lims(stroke=(1, 7))
                 + labs(stroke='stroke'))
        return p + theme_minimal()

    plots = [plot(i) for i in range(3)]
    with pytest.raises(PlotnineError):
        _PlotnineAnimation(plots, interval=100, repeat_delay=500)
