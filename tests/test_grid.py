import pytest

from plotnine._mpl.layout_manager._grid import Grid


def test_reduce_cols_basic():
    grid = Grid[int](2, 3, [1, 2, 3, 4, 5, 6])
    # row_major: [[1, 2, 3], [4, 5, 6]]
    assert grid.reduce_cols(lambda n: n, default=0) == [4, 5, 6]


def test_reduce_cols_with_none():
    grid = Grid[int](2, 3, [10, 20])
    # row_major: [[10, 20, None], [None, None, None]]
    assert grid.reduce_cols(lambda n: n, default=99) == [10, 20, 99]


def test_reduce_cols_all_columns_have_some_none():
    grid = Grid[int](2, 2, [1, 2, 3])
    # row_major: [[1, 2], [3, None]]
    assert grid.reduce_cols(lambda n: n, default=0) == [3, 2]


def test_reduce_cols_empty_column_default():
    grid = Grid[int](2, 3, [1, 2])
    # row_major: [[1, 2, None], [None, None, None]] — col 2 is entirely None
    assert grid.reduce_cols(lambda n: n, default=42)[2] == 42


def test_reduce_cols_transforms_with_fn():
    grid = Grid[int](2, 2, [1, 2, 3, 4])
    assert grid.reduce_cols(lambda n: n * 10, default=0) == [30, 40]


def test_reduce_rows_basic():
    grid = Grid[int](2, 3, [1, 2, 3, 4, 5, 6])
    # row_major: [[1, 2, 3], [4, 5, 6]]
    assert grid.reduce_rows(lambda n: n, default=0) == [3, 6]


def test_reduce_rows_with_none():
    grid = Grid[int](3, 2, [10, 20, 30])
    # row_major: [[10, 20], [30, None], [None, None]]
    assert grid.reduce_rows(lambda n: n, default=99) == [20, 30, 99]


def test_reduce_rows_empty_row_default():
    grid = Grid[int](3, 2, [1, 2])
    # row_major: [[1, 2], [None, None], [None, None]] — rows 1 & 2 are empty
    out = grid.reduce_rows(lambda n: n, default=42)
    assert out[1] == 42
    assert out[2] == 42


def test_items_on_edge_top_bottom_degenerate():
    # Without spans, top and bottom of a row are the same items.
    grid = Grid[int](2, 3, [1, 2, 3, 4, 5, 6])
    assert grid.items_on_edge("top", 0) == [1, 2, 3]
    assert grid.items_on_edge("bottom", 0) == [1, 2, 3]
    assert grid.items_on_edge("top", 1) == [4, 5, 6]
    assert grid.items_on_edge("bottom", 1) == [4, 5, 6]


def test_items_on_edge_left_right_degenerate():
    # Without spans, left and right of a col are the same items.
    grid = Grid[int](2, 3, [1, 2, 3, 4, 5, 6])
    assert grid.items_on_edge("left", 0) == [1, 4]
    assert grid.items_on_edge("right", 0) == [1, 4]
    assert grid.items_on_edge("left", 2) == [3, 6]
    assert grid.items_on_edge("right", 2) == [3, 6]


def test_items_on_edge_filters_none():
    grid = Grid[int](2, 2, [1, 2, 3])
    # row_major: [[1, 2], [3, None]]
    assert grid.items_on_edge("top", 1) == [3]
    assert grid.items_on_edge("right", 1) == [2]


def test_grid_order_row_major():
    grid = Grid[int](2, 3, [1, 2, 3, 4, 5, 6], order="row_major")
    assert grid[0, 0] == 1
    assert grid[0, 1] == 2
    assert grid[0, 2] == 3
    assert grid[1, 0] == 4
    assert grid[1, 1] == 5
    assert grid[1, 2] == 6


def test_grid_order_col_major():
    grid = Grid[int](2, 3, [1, 2, 3, 4, 5, 6], order="col_major")
    assert grid[0, 0] == 1
    assert grid[1, 0] == 2
    assert grid[0, 1] == 3
    assert grid[1, 1] == 4
    assert grid[0, 2] == 5
    assert grid[1, 2] == 6


def test_reduce_cols_does_not_call_fn_on_none():
    # Verify None items are filtered out before fn is invoked
    grid = Grid[int](2, 2, [1, 2])

    def fn(n):
        if n is None:
            pytest.fail("fn should not be called with None")
        return n

    grid.reduce_cols(fn, default=0)
