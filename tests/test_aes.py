import pandas as pd

from plotnine import aes, geom_col, ggplot

data = pd.DataFrame(
    {
        "x": pd.Categorical(["b", "d", "c", "a"], ordered=True),
        "y": [1, 2, 3, 4],
    }
)


def test_reorder():
    p = (
        ggplot(data, aes("reorder(x, y)", "y", fill="reorder(x, y)"))
        + geom_col()
    )
    assert p == "reorder"


def test_reorder_index():
    # The dataframe is created with ordering according to the y
    # variable. So the x index should be ordered acc. to y too
    p = ggplot(data, aes("reorder(x, x.index)", "y")) + geom_col()
    assert p == "reorder_index"


def test_labels_series():
    p = ggplot(data, aes(x=data.x, y=data.y)) + geom_col()
    assert p.labels.x == "x"
    assert p.labels.y == "y"


def test_labels_lists():
    p = ggplot(data, aes(x=[1, 2, 3], y=[1, 2, 3])) + geom_col()
    assert p.labels.x is None
    assert p.labels.y is None
