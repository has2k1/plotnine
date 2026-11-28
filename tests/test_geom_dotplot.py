import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg

from plotnine import aes, geom_dotplot, ggplot, stage, stat_bindot

data = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]})


def test_dotdensity():
    p = ggplot(data, aes("x")) + geom_dotplot(bins=15)

    assert p == "dotdensity"


def test_histodot():
    p = ggplot(data, aes("x")) + geom_dotplot(bins=15, method="histodot")

    assert p == "histodot"


def test_stackratio():
    p = ggplot(data, aes("x")) + geom_dotplot(bins=15, stackratio=0.75)

    assert p == "stackratio"


def test_binaxis_y():
    p = ggplot(data, aes("x", "x")) + geom_dotplot(bins=15, binaxis="y")

    assert p == "binaxis_y"


@pytest.mark.parametrize("binaxis", ["x", "y"])
def test_dots_stay_circular_after_layout_and_resize(binaxis):
    binwidth = 0.25
    stackratio = 0.75
    mapping = aes("x") if binaxis == "x" else aes("x", "x")
    p = ggplot(data, mapping) + geom_dotplot(
        binaxis=binaxis, binwidth=binwidth, stackratio=stackratio
    )
    fig = p.draw()
    canvas = FigureCanvasAgg(fig)
    try:
        ax = fig.axes[0]
        dots = ax.collections[0]
        along = 0 if binaxis == "x" else 1
        across = 1 - along
        for figsize, xlim in [
            ((8, 3), None),
            ((4, 6), None),
            ((4, 6), (0, 8)),
        ]:
            fig.set_size_inches(*figsize)
            if xlim is not None:
                ax.set_xlim(*xlim)
            canvas.draw()
            transform = dots.get_transform()
            boxes = [path.get_extents(transform) for path in dots.get_paths()]
            coordinates = np.zeros((2, 2))
            coordinates[1, along] = binwidth
            binned = ax.transData.transform(coordinates)
            diameter = abs(binned[1, along] - binned[0, along])
            np.testing.assert_allclose(
                [(box.width, box.height) for box in boxes],
                np.full((len(data), 2), diameter),
            )
            centers = np.array(
                [
                    [(box.x0 + box.x1) / 2, (box.y0 + box.y1) / 2]
                    for box in boxes
                ]
            )
            last_bin = np.isclose(centers[:, along], centers[:, along].max())
            spacing = np.diff(np.sort(centers[last_bin, across]))
            np.testing.assert_allclose(spacing, [diameter * stackratio] * 3)
    finally:
        plt.close(fig)


def test_stackdir_down():
    p = ggplot(data, aes("x")) + geom_dotplot(bins=15, stackdir="down")

    assert p == "stackdir_down"


def test_stackdir_center():
    p = ggplot(data, aes("x")) + geom_dotplot(bins=15, stackdir="center")

    assert p == "stackdir_center"


def test_stackdir_centerwhole():
    p = ggplot(data, aes("x")) + geom_dotplot(bins=15, stackdir="centerwhole")

    assert p == "stackdir_centerwhole"


def test_binaxis_y_binpositions_all():
    # The y values are not sorted, stat_bindot sorts them before
    # assigning the bins found across all the groups. The counts
    # must remain with the right group and bin center.
    data = pd.DataFrame(
        {
            "g": list("abababbaba"),
            "y": [4, 1, 3, 2, 4, 3, 4, 2, 3, 4],
        }
    )
    # Keep the bin centers in y instead of the default count
    p = ggplot(data, aes("g", stage("y", after_stat="y"))) + stat_bindot(
        binaxis="y",
        binpositions="all",
        binwidth=1,
        geom="point",
    )
    ldata = p.layer_data()
    result = {
        (group, y): count
        for group, y, count in ldata[["group", "y", "count"]].itertuples(
            index=False
        )
    }

    assert result == {
        (1, 2): 1,
        (1, 3): 1,
        (1, 4): 3,
        (2, 1): 1,
        (2, 2): 1,
        (2, 3): 2,
        (2, 4): 1,
    }


def test_drop():
    # Points with zero weight create empty bins
    data = pd.DataFrame(
        {
            "x": [4, 1, 3, 2, 4, 3, 4, 2, 3, 4],
            "w": [1, 0, 1, 0, 1, 1, 1, 0, 1, 1],
        }
    )
    p = ggplot(data, aes("x", weight="w"))
    kwargs = {"binwidth": 1, "geom": "point"}

    ldata = (p + stat_bindot(drop=False, **kwargs)).layer_data()
    assert list(ldata["x"]) == [1, 2, 3, 4]
    assert list(ldata["count"]) == [0, 0, 3, 4]

    ldata = (p + stat_bindot(drop=True, **kwargs)).layer_data()
    assert list(ldata["x"]) == [3, 4]
    assert list(ldata["count"]) == [3, 4]
    assert list(ldata["ncount"]) == [0.75, 1]


class TestGrouping:
    data = pd.DataFrame(
        {
            "x": [1, 2, 2, 3, 3, 3, 4, 4, 4, 4],
            "g": [1, 2, 22, 3, 33, 333, 4, 44, 444, 4444],
        }
    )

    p = ggplot(data, aes("x", "x", fill="factor(g)", color="factor(g)"))

    def test_group_basic(self):
        p = self.p + geom_dotplot(bins=15)

        assert p == "group_basic"

    def test_group_binpositions_all(self):
        p = self.p + geom_dotplot(bins=15, binpositions="all")

        assert p == "group_basic"  # Yes same as above

    def test_group_stackgroups(self):
        p = self.p + geom_dotplot(
            bins=15, binpositions="all", stackgroups=True
        )

        assert p == "group_stackgroups"

    @pytest.mark.skip(
        "Broken: geom_dotplot needs to account for the aspect ratio of "
        "the axes after the layout manager has run."
    )
    def test_group_stackgroups_binaxis_y(self):
        p = self.p + geom_dotplot(
            bins=15, binpositions="all", stackgroups=True, binaxis="y"
        )

        assert p == "group_stackgroups_binaxis_y"
