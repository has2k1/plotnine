from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
from nose.tools import assert_true

from ggplot import *
from ggplot.components.colors import assign_continuous_colors, \
    assign_discrete_colors
from ggplot.tests import cleanup


@cleanup
def test_assign_colors():
    """
    Test how colors are assigned to different column types.
    """

    df = pd.DataFrame({"values": np.arange(10),
                       "int_col": np.arange(10),
                       "num_col": np.arange(10) / 2,
                       "bool_col": np.random.randn(10) > 0,
                       "char_col": ["a", "b"] * 5})

    color_mapping_col = 'color_mapping'

    # test integer column
    color_col = "int_col"
    gg_int = ggplot(df, aes(x="values", y="values", color="int_col"))
    gg_int += geom_point()
    gg_int.draw()

    new_data = assign_continuous_colors(df, gg_int, color_col)
    expected_cols = new_data[color_mapping_col]
    actual_cols = gg_int.data[color_mapping_col]
    assert_true((actual_cols == expected_cols).all())

    # test numeric column
    color_col = "num_col"
    gg_num = ggplot(df, aes(x="values", y="values", color="num_col"))
    gg_num += geom_point()
    gg_num.draw()

    new_data = assign_continuous_colors(df, gg_int, color_col)
    expected_cols = new_data[color_mapping_col]
    actual_cols = gg_num.data[color_mapping_col]
    assert_true((actual_cols == expected_cols).all())

    # test bool column
    color_col = "bool_col"
    gg_bool = ggplot(df, aes(x="values", y="values", color="bool_col"))
    gg_bool += geom_point()
    gg_bool.draw()

    new_data = assign_discrete_colors(df, gg_bool, color_col)
    expected_cols = new_data[color_mapping_col]
    actual_cols = gg_bool.data[color_mapping_col]
    assert_true((actual_cols == expected_cols).all())

    # test char column
    color_col = "char_col"
    gg_char = ggplot(df, aes(x="values", y="values", color="char_col"))
    gg_char += geom_point()
    gg_char.draw()

    new_data = assign_discrete_colors(df, gg_bool, color_col)
    expected_cols = new_data[color_mapping_col]
    actual_cols = gg_char.data[color_mapping_col]
    assert_true((actual_cols == expected_cols).all())
