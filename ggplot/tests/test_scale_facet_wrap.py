from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.testing.decorators import image_comparison

from ggplot import *

@image_comparison(baseline_images=["free", "free_x", "free_y", "none"], extensions=["png"])
def test_scale_facet_wrap():
    p = ggplot(aes(x="price"), data=diamonds) + geom_histogram()

    print(p + facet_wrap("cut", scales="free"))
    print(p + facet_wrap("cut", scales="free_x"))
    print(p + facet_wrap("cut", scales="free_y"))
    print(p + facet_wrap("cut", scales=None))
