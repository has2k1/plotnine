from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
from six.moves import xrange

from nose.tools import assert_equal, assert_true, assert_raises
from matplotlib.testing.decorators import image_comparison, cleanup

import numpy as np
import pandas as DataFrame

from ggplot import *


@image_comparison(baseline_images=['scale_without_reverse', 'scale_y_reverse', 'scale_x_reverse', 'scale_both_reverse'], extensions=["png"])
def test_scale_reverse():

    df = pd.DataFrame({"x": np.arange(0, 100),
                       "y": np.arange(0, 100),
                       "z": np.arange(0, 100)})

    df['cat'] = np.where(df.x*2 > 50, 'blah', 'blue')
    df['cat'] = np.where(df.y > 50, 'hello', df.cat)
    df['cat2'] = np.where(df.y < 15, 'one', 'two')
    df['y'] = np.sin(df.y)

#    gg = ggplot(aes(x="x", y="z", color="cat", alpha=0.2), data=df)
#    gg = ggplot(aes(x="x", color="c"), data=pd.DataFrame({"x": np.random.normal(0, 1, 10000), "c": ["blue" if i%2==0 else "red" for i in range(10000)]}))

    gg = ggplot(aes(x="x", y="y", shape="cat2", color="cat"), data=df) + geom_line()

    print(gg)
    print(gg + scale_y_reverse())
    print(gg + scale_x_reverse())
    print(gg + scale_x_reverse()+ scale_y_reverse())
