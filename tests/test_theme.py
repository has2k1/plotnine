import os

import numpy as np
import pandas as pd
import pytest

from plotnine import (
    aes,
    element_blank,
    element_line,
    element_rect,
    element_text,
    facet_grid,
    facet_wrap,
    geom_blank,
    geom_point,
    ggplot,
    guide_colorbar,
    guide_legend,
    guides,
    labs,
    scale_y_continuous,
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


def test_axis_ticks_and_length():
    # https://github.com/has2k1/plotnine/issues/703
    p = (
        ggplot(mtcars, aes("wt", "mpg"))
        + geom_blank()
        + theme_minimal()
        + theme(
            plot_margin=0.04,
            axis_ticks_major_x=element_line(color="green", size=5),
            axis_ticks_major_y=element_line(color="blue", size=5),
            axis_ticks_length_major=9,
        )
    )
    assert p == "axis_ticks_and_length"


def test_no_ticks():
    # Without ticks, there should not be padding
    p = (
        ggplot(mtcars, aes("wt", "mpg"))
        + geom_blank()
        + theme(axis_ticks_x=element_blank())
    )
    assert p == "no_ticks"


def test_element_text_with_sequence_values():
    p = (
        ggplot(mtcars, aes("wt", "mpg"))
        + geom_point()
        + facet_grid("am", "cyl")
        + theme(
            axis_text=element_text(color="gray"),
            axis_text_x=element_text(
                color=("red", "green", "blue", "purple"), size=(8, 12, 16, 20)
            ),
            strip_text_x=element_text(color=("black", "brown", "cyan")),
            strip_text_y=element_text(color=("teal", "orange")),
        )
    )
    assert p == "element_text_with_sequence_values"


black_frame = theme(
    legend_frame=element_rect(color="black"),
    legend_ticks=element_line(color="black"),
)

red_frame = theme(
    legend_frame=element_rect(color="red"),
    legend_ticks=element_line(color="red"),
)


class TestThemes:
    g = (
        ggplot(mtcars, aes(x="wt", y="mpg", color="factor(gear)"))
        + geom_point()
        + facet_grid("vs", "am")
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

    def test_turn_off_guide(self):
        p1 = self.g + theme(legend_position="none")
        p2 = self.g + guides(color="none")
        p3 = self.g + guides(color=False)

        assert p1 == "turn_off_guide"
        assert p2 == "turn_off_guide"
        assert p3 == "turn_off_guide"

    def test_legends_in_different_positions(self):
        p = (
            self.g
            + aes(color="gear", fill="am", shape="factor(cyl)", alpha="vs")
            + guides(
                shape=guide_legend(position="bottom"),
                color=guide_legend(position="left"),
                alpha=guide_legend(position="left"),
            )
        )

        assert p == "legends_in_different_positions"

    def test_facet_grid(self):
        p = self.g + facet_grid("am", "gear")
        assert p == "facet_grid"

    def test_facet_wrap(self):
        p = self.g + facet_wrap("carb", nrow=2)
        assert p == "facet_wrap"

    def test_facet_wrap_scales_free(self):
        p = self.g + facet_wrap("carb", scales="free")
        assert p == "facet_wrap_scales_free"

    def test_plot_margin_aspect_ratio(self):
        # The margin should be exact in both directions even if
        # the figure has an aspect ratio != 1.
        p = (
            ggplot()
            + geom_blank()
            + theme(plot_margin=0.025, figure_size=(4, 3))
        )
        assert p == "plot_margin_aspect_ratio"

    def test_plot_margin_protruding_axis_text(self):
        data = pd.DataFrame({"x": np.arange(5), "y": np.arange(5) - 0.2})

        p = (
            ggplot(data, aes("x", "y"))
            + geom_point()
            + scale_y_continuous(labels="0 1 2 3 four-four-four-four".split())
            + labs(title="Protruding Axis Text")
            + theme(
                axis_text_y=element_text(
                    rotation=(0, 0, 0, 0, 90),
                    color=("black", "black", "black", "black", "red"),
                    va="center",
                ),
            )
        )
        assert p == "plot_margin_protruding_axis_text"

    def test_colorbar_frame(self):
        p = self.g + aes(color="gear") + black_frame
        assert p == "colorbar_frame"

    def test_different_colorbar_themes(self):
        p = (
            self.g
            + aes(color="gear", fill="am")
            + guides(
                color=guide_colorbar(theme=black_frame),
                fill=guide_colorbar(theme=red_frame),
            )
        )

        assert p == "different_colorbar_themes"


class TestLegendPositioning:
    g = ggplot(mtcars, aes(x="wt", y="mpg", color="gear")) + geom_point()

    def test_outside_legend_right_bottom(self):
        p = self.g + theme(legend_justification=0)
        assert p == "outside_legend_right_bottom"

    def test_outside_legend_left_top(self):
        p = self.g + theme(
            legend_position="left",
            legend_justification=1,
        )
        assert p == "outside_legend_left_top"

    def test_outside_legend_bottom_left(self):
        p = self.g + theme(
            legend_position="bottom",
            legend_justification=0,
        )
        assert p == "outside_legend_bottom_left"

    def test_outside_legend_top_right(self):
        p = self.g + theme(
            legend_position="top",
            legend_justification=1,
        )
        assert p == "outside_legend_top_right"

    def test_inside_legend_left(self):
        p = self.g + theme(
            legend_position="inside",
            legend_justification="left",
        )
        assert p == "inside_legend_left"

    def test_inside_legend_left2(self):
        p = self.g + theme(
            legend_position="inside",
            legend_justification=(0, 0.5),
        )
        assert p == "inside_legend_left"

    def test_inside_legend_top(self):
        p = self.g + theme(
            legend_position="inside",
            legend_justification="top",
        )
        assert p == "inside_legend_top"

    def test_inside_legend_top2(self):
        p = self.g + theme(legend_position=(0.5, 1))
        assert p == "inside_legend_top"

    def test_inside_legend_top_right(self):
        p = self.g + theme(
            legend_position="inside",
            legend_justification=(1, 1),
        )
        assert p == "inside_legend_top_right"

    def test_inside_legend_top_right2(self):
        p = self.g + theme(
            legend_position="inside",
            legend_position_inside=(1, 1),
        )
        assert p == "inside_legend_top_right"

    def test_inside_legend_top_right3(self):
        p = (
            self.g
            + guides(color=guide_colorbar(position="inside"))
            + theme(legend_position_inside=(1, 1))
        )
        assert p == "inside_legend_top_right"

    def test_inside_legend_top_right4(self):
        p = self.g + guides(color=guide_colorbar(position=(1, 1)))
        assert p == "inside_legend_top_right"

    def test_inside_legend_90pct_top_right(self):
        # Use an equal aspect ratio to easily check that the
        # top-right tip of the legend is at 90% along both dimensions
        p = self.g + theme(
            aspect_ratio=1,
            legend_position=(0.9, 0.9),
            legend_justification=(1, 1),
        )
        assert p == "inside_legend_90pct_top_right"
