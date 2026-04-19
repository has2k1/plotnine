import pytest

from plotnine import element_text, theme
from plotnine.exceptions import PlotnineError
from plotnine.themes.elements.margin import margin


def setup_margin(
    m: margin, fontsize: float = 11, figure_size=(8.0, 6.0)
) -> margin:
    """Attach margin to a theme and call its setup() as the layout would"""
    t = theme(
        figure_size=figure_size,
        plot_title=element_text(size=fontsize, margin=m),
    )
    m.setup(t, "plot_title")
    return m


def test_conversion_before_setup_raises():
    m = margin(t=5, unit="pt")
    with pytest.raises(PlotnineError, match="set up"):
        m.to("fig")


def test_conversion_same_unit_after_setup_succeeds():
    m = setup_margin(margin(t=5, r=5, b=5, l=5, unit="pt"))
    result = m.to("pt")
    assert result.unit == "pt"
    assert result.t == 5


def test_lines_to_pt_after_setup():
    m = setup_margin(margin(t=3, r=3, b=3, l=3, unit="lines"))
    result = m.to("pt")
    assert result.unit == "pt"
    assert result.t == pytest.approx(33)
    assert result.r == pytest.approx(33)
    assert result.b == pytest.approx(33)
    assert result.l == pytest.approx(33)


def test_conversion_fig_isotropy_after_setup():
    """Physical distances match on all sides for equal lines input"""
    W, H = 12.0, 4.0
    m = setup_margin(
        margin(t=3, r=3, b=3, l=3, unit="lines"), figure_size=(W, H)
    )
    mf = m.to("fig")
    assert mf.t * H == pytest.approx(mf.l * W)
    assert mf.b * H == pytest.approx(mf.r * W)


def test_conversion_with_zero_figure_dimension_raises():
    """Zero figure dimension propagates ZeroDivisionError on conversion"""
    m = setup_margin(
        margin(t=3, r=3, b=3, l=3, unit="lines"), figure_size=(0.0, 6.0)
    )
    with pytest.raises(ZeroDivisionError):
        m.to("fig")
