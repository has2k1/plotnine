from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nose.tools import assert_true
from ggplot.tests import image_comparison

from ggplot import *

@image_comparison(baseline_images=['theme_gray_default'], extensions=["png"])
def test_theme_gray1():
    #theme_gray is the default
    gg = ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        ggtitle("Beef: It's What's for Dinner") + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")
    assert_true(isinstance(gg.theme, theme_gray))
    print(gg)
