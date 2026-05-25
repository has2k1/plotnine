import pytest

from plotnine.composition._design import parse_design


def test_parses_3_regions_into_correct_rects():
    spec = parse_design("1##\n123\n##3")
    assert spec.nrow == 3
    assert spec.ncol == 3
    # Sorted order: 1, 2, 3.
    assert spec._rects == [
        (0, 1, 0, 0),  # label "1" at (0,0) and (1,0)
        (1, 1, 1, 1),  # label "2" at (1,1)
        (1, 2, 2, 2),  # label "3" at (1,2) and (2,2)
    ]


def test_dot_and_hash_are_both_empty():
    a = parse_design("1##\n123\n##3")
    b = parse_design("1..\n123\n..3")
    assert a._rects == b._rects
    assert a.grid == b.grid


def test_space_is_empty():
    # Spaces inside a row act as empty markers, so users can add
    # visual breathing room without producing an opaque "not
    # rectangular" error.
    a = parse_design("1.2\n1.2")
    b = parse_design("1 2\n1 2")
    assert a._rects == b._rects
    assert a.grid == b.grid


def test_character_identity_is_irrelevant():
    base = parse_design("1##\n123\n##3")
    letters = parse_design("A##\nABC\n##C")
    digits = parse_design("x##\nxyz\n##z")
    assert base._rects == letters._rects == digits._rects


def test_leading_trailing_whitespace_lines_are_ignored():
    spec = parse_design("\n  \n1##\n123\n##3\n  \n")
    assert spec.nrow == 3
    assert spec.ncol == 3
    assert len(spec._rects) == 3


def test_mixed_width_rows_raise():
    with pytest.raises(ValueError, match="unequal lengths"):
        parse_design("12\n123")


def test_l_shape_raises():
    # Label "1" spans the bounding box (0,0)..(1,1), but (1,1) is empty.
    with pytest.raises(ValueError, match="region '1' is not rectangular"):
        parse_design("11\n1#")


def test_overlapping_rectangles_raise():
    # Label "1" cells at (0,0) and (1,1) → bounding box covers (0,1)
    # which carries "2".
    with pytest.raises(ValueError, match="region '1' is not rectangular"):
        parse_design("12\n21")


def test_empty_string_raises():
    with pytest.raises(ValueError, match="empty"):
        parse_design("")
    with pytest.raises(ValueError, match="empty"):
        parse_design("   \n  \n")


def test_full_grid_no_empty_cells():
    spec = parse_design("12\n34")
    assert spec.nrow == 2
    assert spec.ncol == 2
    assert spec._rects == [
        (0, 0, 0, 0),
        (0, 0, 1, 1),
        (1, 1, 0, 0),
        (1, 1, 1, 1),
    ]


def test_empty_row_legal():
    spec = parse_design("1.2\n...\n3.4")
    assert spec.nrow == 3
    assert spec.ncol == 3
    assert spec._rects == [
        (0, 0, 0, 0),
        (0, 0, 2, 2),
        (2, 2, 0, 0),
        (2, 2, 2, 2),
    ]


def test_empty_column_legal():
    spec = parse_design("1.2\n1.2")
    assert spec.nrow == 2
    assert spec.ncol == 3
    assert spec._rects == [
        (0, 1, 0, 0),
        (0, 1, 2, 2),
    ]


def test_grid_field_preserves_empty_marker():
    spec = parse_design("1#2\n1#2")
    assert spec.grid == [["1", "", "2"], ["1", "", "2"]]


def test_sorted_character_order_determines_plot_assignment():
    # "B" appears before "A" in the row-major scan, but sorted
    # order puts "A" first — plot 0 → "A" (col 1), plot 1 → "B" (col 0).
    spec = parse_design("BA\nBA")
    assert spec._rects == [
        (0, 1, 1, 1),  # "A": col 1, rows 0-1
        (0, 1, 0, 0),  # "B": col 0, rows 0-1
    ]
