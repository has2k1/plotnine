import pandas as pd
import pytest

from plotnine import aes, geom_line, ggplot, scale_linetype_manual
from plotnine.exceptions import PlotnineError
from plotnine.scales.scale_linetype import scale_linetype


def test_scale_linetype_manual_tuples():
    # linetype_manual accepts tuples as mapping results
    # this must be tested specifically.
    data = pd.DataFrame(
        {
            "x": [0, 1, 0, 1, 0, 1],
            "y": [0, 1, 0, 2, 0, 3],
            "lt": ["A", "A", "B", "B", "C", "C"],
        }
    )

    p = ggplot(data)
    p += geom_line(aes(x="x", y="y", ymax="y+1", linetype="lt", group="lt"))
    p += scale_linetype_manual(
        values=(
            (2, (5, 3, 1, 3)),
            (1, (10, 2)),
            (1, (1, 2)),
        )
    )
    assert p == "scale_linetype_manual_tuples"


def test_scale_linetype_strings_tuples():
    # linetype_manual accepts tuples as mapping results
    # this must be tested specifically.
    data = pd.DataFrame(
        {
            "x": [0, 1, 0, 1, 0, 1],
            "y": [0, 1, 0, 2, 0, 3],
            "lt": ["A", "A", "B", "B", "C", "C"],
        }
    )

    p = ggplot(data)
    p += geom_line(aes(x="x", y="y", ymax="y+1", linetype="lt", group="lt"))
    p += scale_linetype_manual(values=["solid", "dashed", "dotted"])
    assert p == "scale_linetype_manual_strings"


def test_default_linetype_palette_limit():
    palette = scale_linetype().palette
    assert list(palette(4)) == ["solid", "dashed", "dashdot", "dotted"]
    msg = "at most 4 categories.*5 were requested"
    with pytest.raises(PlotnineError, match=msg):
        palette(5)


def test_default_linetype_fifth_category_explains_workaround():
    data = pd.DataFrame(
        {
            "x": [0, 1] * 5,
            "y": [0, 1] * 5,
            "group": [f"group{i}" for i in range(5) for _ in range(2)],
        }
    )
    p = ggplot(data, aes("x", "y", group="group", linetype="group"))
    p += geom_line()
    with pytest.raises(PlotnineError, match="scale_linetype_manual"):
        p.draw()


def test_manual_linetype_scale_can_handle_five_patterns():
    scale = scale_linetype_manual(
        values=["solid", "dashed", "dashdot", "dotted", (0, (2, 2))]
    )
    assert len(scale.palette(5)) == 5
