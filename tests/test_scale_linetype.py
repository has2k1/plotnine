import pandas as pd
from plotnine import ggplot, geom_line, scale_linetype_manual, aes


def test_scale_linetype_manual_tuples():
    # linetype_manual accepts tuples as mapping results
    # this must be tested specifically.
    df = pd.DataFrame(
        {
            "x": [0, 1, 0, 1, 0, 1],
            "y": [0, 1, 0, 2, 0, 3],
            "lt": ["A", "A", "B", "B", "C", "C"],
        }
    )

    p = ggplot(df)
    p += geom_line(aes(x="x", y="y", ymax="y+1", linetype="lt", group="lt"))
    p += scale_linetype_manual(values=(
        (2, (5, 3, 1, 3)),
        (1, (10, 2)),
        (1, (1, 2)),))
    assert p == "scale_linetype_manual_tuples"


def test_scale_linetype_strings_tuples():
    # linetype_manual accepts tuples as mapping results
    # this must be tested specifically.
    df = pd.DataFrame(
        {
            "x": [0, 1, 0, 1, 0, 1],
            "y": [0, 1, 0, 2, 0, 3],
            "lt": ["A", "A", "B", "B", "C", "C"],
        }
    )

    p = ggplot(df)
    p += geom_line(aes(x="x", y="y", ymax="y+1", linetype="lt", group="lt"))
    p += scale_linetype_manual(values=['solid', 'dashed', 'dotted'])
    assert p == "scale_linetype_manual_strings"
