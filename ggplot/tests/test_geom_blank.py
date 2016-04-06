from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ggplot import *
from ggplot.data import *

from . import image_comparison


@image_comparison(['blank'])
def test_blank():
    gg = ggplot(aes(x='wt', y='mpg'), data=mtcars)
    gg = gg + geom_blank()
    print(gg)
