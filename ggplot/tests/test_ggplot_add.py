from nose.tools import assert_equal, assert_true

from ggplot import *

def test_ggplot_add1():
    "Adding a complete theme should replace the existing theme."
    gg = ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")
    theme_mpl = theme_matplotlib()
    gg_mpl1 = gg + theme_mpl
    assert_equal(gg_mpl1.theme, theme_mpl)

def test_ggplot_add2():
    "Adding a partial them should be combined with a base theme."
    gg = ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")
    theme_mpl = theme_matplotlib()
    partial_theme = theme()
    gg_themed = gg + theme_mpl + partial_theme
    assert_equal(gg_themed.theme.partial_themes, [partial_theme])
