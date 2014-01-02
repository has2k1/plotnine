from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
from six.moves import xrange

from nose.tools import assert_equal, assert_true, assert_raises
from matplotlib.testing.decorators import image_comparison, cleanup

import numpy as np
import pandas as DataFrame

from ggplot import *


@image_comparison(baseline_images=['scale_without_log', 'scale_y_log', 'scale_x_log', 'scale_both_log', 'scale_both_log_base2'], extensions=["png"])
def test_scale_log():

    df = pd.DataFrame({"x": np.linspace(0, 10, 10),
                       "y": np.linspace(0, 3, 10),})

    df['y'] = 10.**df.y

    gg = ggplot(aes(x="x", y="y"), data=df) + geom_line()

    print(gg)
    print(gg + scale_y_log())
    print(gg + scale_x_log())
    print(gg + scale_x_log()+ scale_y_log())
    print(gg + scale_x_log(2)+ scale_y_log(2))
