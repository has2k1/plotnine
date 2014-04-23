from nose.tools import assert_equal, assert_true, assert_raises

from ggplot.tests import image_comparison, cleanup
from ggplot import *


def _test_theme1():
    gg = ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")
    gg_mpl1 = gg + theme_matplotlib()
    gg.rcParams["foo"] = "bar"
    gg_mpl2 = gg + theme_matplotlib()
    assert_equal(gg_mpl1.rcParams, gg_mpl2.rcParams)

def _test_theme2():
    gg = ggplot(aes(x='date', y='beef'), data=meat)
    gg_g1 = gg + theme_gray()
    gg.post_plot_callbacks.append("foo")
    gg_g2 = gg + theme_gray()
    assert_equal(gg_g1.post_plot_callbacks, gg_g2.post_plot_callbacks)

def test_theme3():
    tg = theme_gray()
    assert_true(tg.complete)

@image_comparison(["red_text"], tol=0)
def test_theme4():
    # Incomplete theme should have the default theme plus additinal theme
    # elements.
    gg = ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")
    print(gg + theme(axis_text_x=element_text(color="red")))

def test_theme5():
    # complete theme t2 replaces partial theme t2
    t1 = theme_gray()
    t2 = theme(text=element_text())
    t3 = t2 + t1
    assert_true(t3.complete)

def test_theme6():
    # partial theme t2 is combined with complete theme t1
    t1 = theme_gray()
    t2 = theme(text=element_text())
    t3 = t1 + t2
    assert_equal(t3.element_themes, t2.element_themes)

def test_theme7():
    # partial themes should be combined for later application to a complete
    # theme
    t1 = theme(text=element_text())
    t2 = theme(axis_text=element_text())
    t3 = t1 + t2
    assert_equal(t3.element_themes, t1.element_themes + t2.element_themes)

# based on examples from http://docs.ggplot2.org/current/theme.html
gg = ggplot(aes(x='mpg', y='wt'), data=mtcars) + geom_point()

@image_comparison(["general_first"], tol=0)
def test_theme8():
    # Text element_target properties that can be configured with rcParams.
    print(gg +
          theme(text=element_text(color="red")) +
          theme(axis_text_y=element_text(color="green")) +
          theme(axis_title=element_text(color="blue")))

@image_comparison(["general_last"], tol=0)
def test_theme8():
    print(gg)
    # Text element_target properties that can be configured with rcParams.
    print(gg +
          theme(axis_text_y=element_text(color="green")) +
          theme(axis_title=element_text(color="blue")) +
          theme(text=element_text(color="red")))

def test_theme9():
    assert_raises(TypeError, lambda: theme() + gg)
