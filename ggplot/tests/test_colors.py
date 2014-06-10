from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
from nose.tools import assert_true

from ggplot import *
from ggplot.components.legend import get_labels
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

    color_mapping_col = ':::color_mapping:::'
    fill_mapping_col = ':::fill_mapping:::'

    # test integer column
    color_col = "int_col"
    gg_int = ggplot(df, aes(x="values", y="values", color="int_col"))
    gg_int += geom_point()
    gg_int.draw()

    labels, scale_type, indices = get_labels(df, color_col)
    new_data, _ = assign_continuous_colors(df, gg_int, 'color',
                                           color_col, labels, indices)
    expected_cols = new_data[color_mapping_col]
    actual_cols = gg_int.data[color_mapping_col]
    assert_true((actual_cols == expected_cols).all())

    # test numeric column
    color_col = "num_col"
    gg_num = ggplot(df, aes(x="values", y="values", color="num_col"))
    gg_num += geom_point()
    gg_num.draw()

    labels, scale_type, indices = get_labels(df, color_col)
    new_data, _ = assign_continuous_colors(df, gg_num, 'color',
                                           color_col, labels, indices)
    expected_cols = new_data[color_mapping_col]
    actual_cols = gg_num.data[color_mapping_col]
    assert_true((actual_cols == expected_cols).all())

    # test bool column
    color_col = "bool_col"
    gg_bool = ggplot(df, aes(x="values", y="values", color="bool_col"))
    gg_bool += geom_point()
    gg_bool.draw()

    labels, scale_type, indices = get_labels(df, color_col)
    new_data, _ = assign_discrete_colors(df, gg_bool, 'color',
                                           color_col, labels)
    expected_cols = new_data[color_mapping_col]
    actual_cols = gg_bool.data[color_mapping_col]
    assert_true((actual_cols == expected_cols).all())

    # test char column
    color_col = "char_col"
    gg_char = ggplot(df, aes(x="values", y="values", color="char_col"))
    gg_char += geom_point()
    gg_char.draw()

    labels, scale_type, indices = get_labels(df, color_col)
    new_data, _ = assign_discrete_colors(df, gg_char, 'color',
                                           color_col, labels)
    expected_cols = new_data[color_mapping_col]
    actual_cols = gg_char.data[color_mapping_col]
    assert_true((actual_cols == expected_cols).all())

    # Fill mapping

    # test integer column
    fill_col = "int_col"
    gg_int = ggplot(df, aes(x="values", y="values", fill="int_col"))
    gg_int += geom_point()
    gg_int.draw()

    labels, scale_type, indices = get_labels(df, fill_col)
    new_data, _ = assign_continuous_colors(df, gg_int, 'fill',
                                           fill_col, labels, indices)
    expected_cols = new_data[fill_mapping_col]
    actual_cols = gg_int.data[fill_mapping_col]
    assert_true((actual_cols == expected_cols).all())

    # test numeric column
    fill_col = "num_col"
    gg_num = ggplot(df, aes(x="values", y="values", fill="num_col"))
    gg_num += geom_point()
    gg_num.draw()

    labels, scale_type, indices = get_labels(df, fill_col)
    new_data, _ = assign_continuous_colors(df, gg_num, 'fill',
                                           fill_col, labels, indices)
    expected_cols = new_data[fill_mapping_col]
    actual_cols = gg_num.data[fill_mapping_col]
    assert_true((actual_cols == expected_cols).all())

    # test bool column
    fill_col = "bool_col"
    gg_bool = ggplot(df, aes(x="values", y="values", fill="bool_col"))
    gg_bool += geom_point()
    gg_bool.draw()

    labels, scale_type, indices = get_labels(df, fill_col)
    new_data, _ = assign_discrete_colors(df, gg_bool, 'fill',
                                           fill_col, labels)
    expected_cols = new_data[fill_mapping_col]
    actual_cols = gg_bool.data[fill_mapping_col]
    assert_true((actual_cols == expected_cols).all())

    # test char column
    fill_col = "char_col"
    gg_char = ggplot(df, aes(x="values", y="values", fill="char_col"))
    gg_char += geom_point()
    gg_char.draw()

    labels, scale_type, indices = get_labels(df, fill_col)
    new_data, _ = assign_discrete_colors(df, gg_char, 'fill',
                                           fill_col, labels)
    expected_cols = new_data[fill_mapping_col]
    actual_cols = gg_char.data[fill_mapping_col]
    assert_true((actual_cols == expected_cols).all())
