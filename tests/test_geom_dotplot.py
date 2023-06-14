import pandas as pd

from plotnine import aes, geom_dotplot, ggplot

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


def test_stackdir_down():
    p = ggplot(data, aes("x")) + geom_dotplot(bins=15, stackdir="down")

    assert p == "stackdir_down"


def test_stackdir_center():
    p = ggplot(data, aes("x")) + geom_dotplot(bins=15, stackdir="center")

    assert p == "stackdir_center"


def test_stackdir_centerwhole():
    p = ggplot(data, aes("x")) + geom_dotplot(bins=15, stackdir="centerwhole")

    assert p == "stackdir_centerwhole"


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

    def test_group_stackgroups_binaxis_y(self):
        p = self.p + geom_dotplot(
            bins=15, binpositions="all", stackgroups=True, binaxis="y"
        )

        assert p == "group_stackgroups_binaxis_y"
