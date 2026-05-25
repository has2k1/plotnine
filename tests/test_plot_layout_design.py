import pytest

from plotnine._utils.yippie import plot
from plotnine.composition import plot_layout


def test_design_mismatched_item_count_raises():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue

    design = """
        12
        34
    """  # 4 regions but only 3 plots

    with pytest.raises(ValueError) as ve:
        ((p1 | p2 | p3) + plot_layout(design=design)).draw()

    msg = str(ve.value)
    assert "4 regions" in msg
    assert "3 items" in msg


def test_design_with_nrow_raises():
    p1 = plot.red
    p2 = plot.green
    with pytest.raises(ValueError, match="cannot be combined with nrow"):
        ((p1 | p2) + plot_layout(nrow=2, design="12")).draw()


def test_design_with_ncol_raises():
    p1 = plot.red
    p2 = plot.green
    with pytest.raises(ValueError, match="cannot be combined with nrow"):
        ((p1 | p2) + plot_layout(ncol=2, design="12")).draw()


def test_design_two_col_span_above_two_col_span():
    p1 = plot.red
    p2 = plot.green

    design = """
        11
        22
    """
    p = (p1 | p2) + plot_layout(design=design)
    assert p == "design_two_col_span_above_two_col_span"


def test_design_with_empty_column():
    p1 = plot.red
    p2 = plot.green

    design = """
        1#2
        1#2
    """
    p = (p1 | p2) + plot_layout(design=design)
    assert p == "design_with_empty_column"


def test_design_with_widths():
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue

    design = """
        1#3
        123
    """
    p = (p1 | p2 | p3) + plot_layout(design=design, widths=(1, 2, 1))
    assert p == "design_with_widths"


def test_design_row_span():
    # Span-weighting verification case: a row-spanning plot adjacent to
    # two single-row plots. Inspect the rendered baseline to confirm
    # the fn/span heuristic looks correct.
    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue

    design = """
        12
        13
    """
    p = (p1 | p2 | p3) + plot_layout(design=design)
    assert p == "design_row_span"


def test_design_row_and_col_span():
    design = """
        ABB
        AEC
        DDC
    """

    p1 = plot.red
    p2 = plot.green
    p3 = plot.blue
    p4 = plot.yellow
    p5 = plot.cyan
    p = (p1 + p2 + p3 + p4 + p5) + plot_layout(design=design)
    assert p == "design_row_and_col_span"
