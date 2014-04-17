from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib as mpl
import six

from nose.tools import assert_true
from ggplot.tests import image_comparison, cleanup

from ggplot import *


def _diff(a, b):
    ret = {}
    for key, val in a.items():
        if key in b:
            if b[key] != val:
                ret[key] = "%s: %s -> %s" % (key, val, b[key])
        else:
            ret[key] = "%s: %s -> %s" % (key, val, "--")
    for key, val in b.items():
        if key not in a:
            ret[key] = "%s: %s -> %s" % (key, "--", val)
    return ret

@cleanup
def test_theme_matplotlib():
    gg = ggplot(aes(x='date', y='beef'), data=meat)
    a = mpl.rcParams.copy()
    _theme = theme_matplotlib({"font.family": "serif"}, matplotlib_defaults=False)
    assert_true(len(_theme._rcParams) < 2, "setting font.family changed more than that in the theme. %s" % list(six.iterkeys(_theme._rcParams))[:5])
    gg = gg + _theme
    b = mpl.rcParams.copy()
    assert_true(len(_diff(a,b)) < 2, "setting font.family changed more than that in ggplot object: %s" % list(six.iterkeys(_diff(a,b)))[:5])

@image_comparison(baseline_images=['theme_clean', 'theme_mpl_completly'])
def test_theme_matplotlib2():
    gg = ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        ggtitle("Beef: It's What's for Dinner") + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")
    a = mpl.rcParams.copy()
    print(gg)
    b = mpl.rcParams.copy()
    assert_true(len(_diff(a,b)) < 1, "Just plotting changed something in the ggplot object: %s" % list(six.iterkeys(_diff(a,b)))[:5])
    print(gg + theme_matplotlib())

@image_comparison(baseline_images=['theme_clean2', 'theme_mpl_only_one'])
def test_theme_matplotlib3():
    gg = ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        ggtitle("Beef: It's What's for Dinner") + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")
    a = mpl.rcParams.copy()
    print(gg)
    b = mpl.rcParams.copy()
    assert_true(len(_diff(a,b)) < 1, "Just plotting changed something in the ggplot object: %s" % list(six.iterkeys(_diff(a,b)))[:5])
    _theme = theme_matplotlib({"font.family": "serif"}, matplotlib_defaults=False)
    gg = gg + _theme
    b = mpl.rcParams.copy()
    assert_true(len(_diff(a,b)) < 2, "Setting just one param changed more in the ggplot object: %s" % list(six.iterkeys(_diff(a,b)))[:5])
    print(gg)
    b = mpl.rcParams.copy()
    assert_true(len(_diff(a,b)) < 2, "Plotting after setting just one param changed more in the ggplot object: %s" % list(six.iterkeys(_diff(a,b)))[:5])

@image_comparison(baseline_images=['theme_mpl_all_before', 'theme_mpl_all_after'])
def test_theme_matplotlib4():
    gg = ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        ggtitle("Beef: It's What's for Dinner") + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")
    print(gg + theme_matplotlib())
    print(gg + theme_matplotlib({"font.family": "serif"}, matplotlib_defaults=False))

@image_comparison(baseline_images=['theme_mpl_all_before'])
def test_theme_matplotlib5():
    # Make sure the last complete theme wins.
    gg = ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        ggtitle("Beef: It's What's for Dinner") + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")
    print(gg + theme_xkcd() + theme_matplotlib())

def test_theme_matplotlib6():
    tmpl = theme_matplotlib()
    assert_true(tmpl.complete)
