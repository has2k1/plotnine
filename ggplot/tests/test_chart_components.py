from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd

from nose.tools import assert_raises, assert_equal, assert_is_none

from ggplot import *
from ggplot.utils.exceptions import GgplotError


def test_chart_components():
    """
    Test invalid arguments to chart components
    """

    df = pd.DataFrame({'x': np.arange(10),
                       'y': np.arange(10)})

    gg = ggplot(df, aes(x='x', y='y'))

    # test ggtitle
    assert_raises(GgplotError, ggtitle, None)

    # test xlim
    assert_raises(GgplotError, xlim, 0, None)
    assert_raises(GgplotError, xlim, None, 0)
    assert_raises(GgplotError, xlim, None, None)
    assert_raises(GgplotError, xlim, "foo", 1)
    assert_raises(GgplotError, xlim, "foo", "bar")

    # test ylim
    assert_raises(GgplotError, ylim, 0, None)
    assert_raises(GgplotError, ylim, None, 0)
    assert_raises(GgplotError, ylim, None, None)
    assert_raises(GgplotError, ylim, "foo", 1)
    assert_raises(GgplotError, ylim, "foo", "bar")

    # test xlab
    assert_raises(GgplotError, ylab, None)

    # test ylab
    assert_raises(GgplotError, ylab, None)

    # test labs
    test_xlab = 'xlab'
    gg_xlab = gg + labs(x=test_xlab)

    assert_equal(gg_xlab.xlab, test_xlab)
    assert_is_none(gg_xlab.ylab)
    assert_is_none(gg_xlab.title)

    test_ylab = 'ylab'
    gg_ylab = gg + labs(y=test_ylab)

    assert_is_none(gg_ylab.xlab)
    assert_equal(gg_ylab.ylab, test_ylab)
    assert_is_none(gg_ylab.title)

    test_title = 'title'
    gg_title = gg + labs(title=test_title)

    assert_is_none(gg_title.xlab)
    assert_is_none(gg_title.ylab)
    assert_equal(gg_title.title, test_title)

    gg_labs = gg + labs(x=test_xlab, y=test_ylab, title=test_title)

    assert_equal(gg_labs.xlab, test_xlab)
    assert_equal(gg_labs.ylab, test_ylab)
    assert_equal(gg_labs.title, test_title)
