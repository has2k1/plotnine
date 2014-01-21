from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nose.tools import assert_equal, assert_true, assert_raises

from . import get_assert_same_ggplot, cleanup
assert_same_ggplot = get_assert_same_ggplot(__file__)

import numpy as np
import pandas as pd

from ggplot import *


@cleanup
def test_scale_log():
    df = pd.DataFrame({"x": np.linspace(0, 10, 10),
                       "y": np.linspace(0, 3, 10),})

    df['y'] = 10.**df.y

    gg = ggplot(aes(x="x", y="y"), data=df) + geom_line()

    assert_same_ggplot(gg, 'scale_without_log')
    assert_same_ggplot(gg + scale_y_log(),'scale_y_log')
    assert_same_ggplot(gg + scale_x_log(),'scale_x_log')
    assert_same_ggplot(gg + scale_x_log()+ scale_y_log(),'scale_both_log')
    assert_same_ggplot(gg + scale_x_log(2)+ scale_y_log(2),'scale_both_log_base2')
