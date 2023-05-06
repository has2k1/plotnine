import os

import pytest

from plotnine import (
    aes,
    element_blank,
    element_line,
    element_text,
    facet_grid,
    facet_wrap,
    geom_point,
    ggplot,
    labs,
    theme,
    theme_538,
    theme_bw,
    theme_classic,
    theme_dark,
    theme_gray,
    theme_light,
    theme_linedraw,
    theme_matplotlib,
    theme_minimal,
    theme_seaborn,
    theme_tufte,
    theme_void,
    theme_xkcd,
)
from plotnine.data import mtcars


def test_add_complete_complete():
    theme1 = theme_gray()
    theme2 = theme_matplotlib()
    theme3 = theme1 + theme2
    assert theme3 == theme2


def test_add_complete_partial():
    theme1 = theme_gray()
    theme2 = theme1 + theme(axis_line_x=element_line())
    assert theme2 != theme1
    assert theme2.themeables != theme1.themeables
    assert theme2.rcParams == theme1.rcParams

    # specific difference
    for name in theme2.themeables:
        if name == "axis_line_x":
            assert theme2.themeables[name] != theme1.themeables[name]
        else:
            assert theme2.themeables[name] == theme1.themeables[name]


def test_add_partial_complete():
    theme1 = theme(axis_line_x=element_line())
    theme2 = theme_gray()
    theme3 = theme1 + theme2
    assert theme3 == theme2


def test_add_empty_theme_element():
    # An empty theme element does not alter the theme
    theme1 = theme_gray() + theme(axis_line_x=element_line(color="red"))
    theme2 = theme1 + theme(axis_line_x=element_line())
    assert theme1 == theme2


l1 = element_line(color="red", size=1, linewidth=1, linetype="solid")
l2 = element_line(color="blue", size=2, linewidth=2)
l3 = element_line(color="blue", size=2, linewidth=2, linetype="solid")
blank = element_blank()


def test_add_element_heirarchy():
    # parent themeable modifies child themeable
    theme1 = theme_gray() + theme(axis_line_x=l1)  # child
    theme2 = theme1 + theme(axis_line=l2)  # parent
    theme3 = theme1 + theme(axis_line_x=l3)  # child, for comparison
    assert theme2.themeables["axis_line_x"] == theme3.themeables["axis_line_x"]

    theme1 = theme_gray() + theme(axis_line_x=l1)  # child
    theme2 = theme1 + theme(line=l2)  # grand-parent
    theme3 = theme1 + theme(axis_line_x=l3)  # child, for comparison
    assert theme2.themeables["axis_line_x"] == theme3.themeables["axis_line_x"]

    # child themeable does not affect parent
    theme1 = theme_gray() + theme(axis_line=l1)  # parent
    theme2 = theme1 + theme(axis_line_x=l2)  # child
    theme3 = theme1 + theme(axis_line=l3)  # parent, for comparison
    assert theme3.themeables["axis_line"] != theme2.themeables["axis_line"]


def test_add_element_blank():
    # Adding onto a blanked themeable
    theme1 = theme_gray() + theme(axis_line_x=l1)  # not blank
    theme2 = theme1 + theme(axis_line_x=blank)  # blank
    theme3 = theme2 + theme(axis_line_x=l3)  # not blank
    theme4 = theme_gray() + theme(axis_line_x=l3)  # for comparison
    assert theme3 != theme1
    assert theme3 != theme2
    assert theme3 == theme4  # blanking cleans the slate

    # When a themeable is blanked, the apply_ax method
    # is replaced with the blank method.
    th2 = theme2.themeables["axis_line_x"]
    th3 = theme3.themeables["axis_line_x"]
    assert th2.apply_ax.__name__ == "blank_ax"
    assert th3.apply_ax.__name__ == "apply_ax"


def test_element_line_dashed_capstyle():
    p = ggplot(mtcars, aes(x="wt", y="mpg")) + theme(
        panel_grid=element_line(
            linetype="dashed",
            lineend="butt",
            size=1.0,
        )
    )
    # no exception
    p._build()


def test_element_line_solid_capstyle():
    p = ggplot(mtcars, aes(x="wt", y="mpg")) + theme(
        panel_grid=element_line(
            linetype="solid",
            lineend="butt",
            size=1.0,
        )
    )
    # no exception
    p._build()


class TestThemes:
    g = (
        ggplot(mtcars, aes(x="wt", y="mpg", color="factor(gear)"))
        + geom_point()
        + facet_grid("vs ~ am")
    )

    def test_theme_538(self):
        p = self.g + labs(title="Theme 538") + theme_538()

        assert p == "theme_538"

    def test_theme_bw(self):
        p = self.g + labs(title="Theme BW") + theme_bw()

        assert p == "theme_bw"

    def test_theme_classic(self):
        p = self.g + labs(title="Theme Classic") + theme_classic()

        assert p == "theme_classic"

    def test_theme_dark(self):
        p = self.g + labs(title="Theme Dark") + theme_dark()

        assert p == "theme_dark"

    def test_theme_gray(self):
        p = self.g + labs(title="Theme Gray") + theme_gray()

        assert p == "theme_gray"

    def test_theme_light(self):
        p = self.g + labs(title="Theme Light") + theme_light()

        assert p == "theme_light"

    def test_theme_linedraw(self):
        p = self.g + labs(title="Theme Linedraw") + theme_linedraw()

        assert p == "theme_linedraw"

    def test_theme_matplotlib(self):
        p = self.g + labs(title="Theme Matplotlib") + theme_matplotlib()

        assert p == "theme_matplotlib"

    def test_theme_minimal(self):
        p = self.g + labs(title="Theme Minimal") + theme_minimal()

        assert p == "theme_minimal"

    def test_theme_tufte(self):
        p = self.g + labs(title="Theme Tufte") + theme_tufte(ticks=False)

        assert p == "theme_tufte"

    @pytest.mark.xfail(reason="fails on github actions")
    def test_theme_seaborn(self):
        p = self.g + labs(title="Theme Seaborn") + theme_seaborn()

        assert p == "theme_seaborn"

    def test_theme_void(self):
        p = self.g + labs(title="Theme Void") + theme_void()

        assert p == "theme_void"

    def test_theme_xkcd(self):
        p = (
            self.g
            + labs(title="Theme Xkcd")
            + theme_xkcd()
            # High likely hood of Comic Sans being available
            + theme(text=element_text(family=["Comic Sans MS"]))
        )

        if os.environ.get("CI") or os.environ.get("TRAVIS"):
            # Github Actions and Travis do not have the fonts,
            # we still check to catch any other errors
            assert p != "theme_gray"
        else:
            assert p == "theme_xkcd"


class TestLayout:
    g = (
        ggplot(mtcars, aes(x="wt", y="mpg", color="factor(gear)"))
        + geom_point()
        + labs(  # New
            x="Weight",
            y="Miles Per Gallon",
            title="Relationship between Weight and Fuel Efficiency in Cars",
            subtitle="Should we be driving lighter cars?",
            caption=(
                "The plot shows a negative correlation between car weight\n"
                "and fuel efficiency, with lighter cars generally achieving\n"
                "higher miles per gallon"
            ),
        )
    )

    def test_default(self):
        assert self.g == "default"

    def test_legend_on_top(self):
        p = self.g + theme(legend_position="top")
        assert p == "legend_at_top"

    def test_legend_on_the_left(self):
        p = self.g + theme(legend_position="left")
        assert p == "legend_on_the_left"

    def test_legend_at_the_bottom(self):
        p = self.g + theme(legend_position="bottom")
        assert p == "legend_at_the_bottom"

    def test_facet_grid(self):
        p = self.g + facet_grid("am ~ gear")
        assert p == "facet_grid"

    def test_facet_wrap(self):
        p = self.g + facet_wrap("carb", nrow=2)
        assert p == "facet_wrap"

    def test_facet_wrap_scales_free(self):
        p = self.g + facet_wrap("carb", scales="free")
        assert p == "facet_wrap_scales_free"
