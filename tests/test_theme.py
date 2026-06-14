import os

import matplotlib as mpl
import pytest
from matplotlib import pyplot as plt
from packaging import version

from plotnine import (
    aes,
    element_blank,
    element_line,
    element_text,
    facet_grid,
    geom_blank,
    geom_point,
    ggplot,
    guide_colorbar,
    guides,
    labs,
    lims,
    scale_color_cmap,
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
from plotnine.coords.coord_cartesian import coord_cartesian
from plotnine.themes.themeable import panel_border, themeable

LT_MPL310 = version.parse(mpl.__version__) < version.parse("3.10")
IS_CI = bool(os.environ.get("CI"))


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


def test_add_element_hierarchy():
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


def test_blank_panel_border_hides_polar_spine():
    th = panel_border(element_blank())
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})

    try:
        th.blank_ax(ax)
        assert not ax.spines["polar"].get_visible()
    finally:
        plt.close(fig)


def test_extension_themeable_applies_from_theme_kwargs():
    class test_extension_panel_facecolor(themeable):
        def apply_ax(self, ax):
            super().apply_ax(ax)
            ax.set_facecolor(self.properties["value"])

    p = (
        ggplot(mtcars, aes(x="wt", y="mpg"))
        + geom_point()
        + theme(test_extension_panel_facecolor="red")
    )

    fig = p.draw()
    try:
        assert fig.axes[0].get_facecolor() == (1.0, 0.0, 0.0, 1.0)
    finally:
        plt.close(fig)


def test_coord_can_read_extension_themeable():
    class test_extension_coord_title(themeable):
        pass

    class coord_reads_themeable(coord_cartesian):
        def setup_ax(self, ax, panel_params, theme):
            super().setup_ax(ax, panel_params, theme)
            ax.set_title(theme.getp("test_extension_coord_title"))

    p = (
        ggplot(mtcars, aes(x="wt", y="mpg"))
        + geom_point()
        + coord_reads_themeable()
        + theme(test_extension_coord_title="coord themeable")
    )

    fig = p.draw()
    try:
        assert fig.axes[0].get_title() == "coord themeable"
    finally:
        plt.close(fig)


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


def test_guide_colorbar_sequence_alignments():
    p = (
        ggplot(mtcars, aes("wt", "mpg", color="cyl"))
        + geom_point()
        + theme(
            legend_text_colorbar=element_text(
                size=12,
                va=("bottom", "center", "center", "center", "top"),
                ha=("left", "center", "center", "center", "right"),
            ),
        )
    )
    assert p == "test_guide_colorbar_sequence_ha_va"


def test_guide_colorbar_text_sequence():
    p = (
        ggplot(mtcars)
        + geom_point(aes("wt", "mpg", fill="wt", color="cyl"))
        + scale_color_cmap("Greens")
        + scale_color_cmap("Blues")
        + guides(
            fill=guide_colorbar(
                theme=theme(
                    legend_title=element_text(ha="center"),
                    legend_text_position="left-right",
                )
            ),
            color=guide_colorbar(
                theme=theme(
                    legend_position="bottom",
                    legend_text_position="bottom-top",
                )
            ),
        )
        + theme(
            legend_ticks=element_line(color=["red", "none", "none", "red"] * 2)
        )
    )
    assert p == "guide_colorbar_text_sequence"


g = (
    ggplot(mtcars, aes(x="wt", y="mpg", color="factor(gear)"))
    + geom_point()
    + facet_grid("vs", "am")
)


def test_theme_538():
    p = g + labs(title="Theme 538") + theme_538()

    assert p == "theme_538"


def test_theme_bw():
    p = g + labs(title="Theme BW") + theme_bw()

    assert p == "theme_bw"


def test_theme_classic():
    p = g + labs(title="Theme Classic") + theme_classic()

    assert p == "theme_classic"


def test_theme_dark():
    p = g + labs(title="Theme Dark") + theme_dark()

    assert p == "theme_dark"


def test_theme_gray():
    p = g + labs(title="Theme Gray") + theme_gray()

    assert p == "theme_gray"


def test_theme_light():
    p = g + labs(title="Theme Light") + theme_light()

    assert p == "theme_light"


def test_theme_linedraw():
    p = g + labs(title="Theme Linedraw") + theme_linedraw()

    assert p == "theme_linedraw"


def test_theme_matplotlib():
    p = g + labs(title="Theme Matplotlib") + theme_matplotlib()

    assert p == "theme_matplotlib"


def test_theme_minimal():
    p = g + labs(title="Theme Minimal") + theme_minimal()

    assert p == "theme_minimal"


def test_theme_tufte():
    p = g + labs(title="Theme Tufte") + theme_tufte(ticks=False)

    assert p == "theme_tufte"


@pytest.mark.xfail(reason="fails on github actions")
def test_theme_seaborn():
    p = g + labs(title="Theme Seaborn") + theme_seaborn()

    assert p == "theme_seaborn"


def test_theme_void():
    p = g + labs(title="Theme Void") + theme_void()

    assert p == "theme_void"


@pytest.mark.skipif(IS_CI, reason="Don't run on CI (Github Actions)")
def test_theme_xkcd():
    p = (
        g
        + labs(title="Theme XKCD")
        + theme_xkcd()
        # High likely hood of Comic Sans being available
        + theme(text=element_text(family=["Comic Sans MS"]))
    )

    assert p == "theme_xkcd"


# Definitely run this one on CI (Github Actions)
def test_theme_xkcd_ci():
    p = (
        g
        + labs(title="Theme XKCD")
        + theme_xkcd()
        # MPL ships with DejaVu Sans
        + theme(text=element_text(family=["DejaVu Sans"]))
    )

    assert p == "theme_xkcd_ci"


def test_override_axis_text():
    p = (
        ggplot()
        + lims(x=(0, 100), y=(0, 100))
        + theme(
            axis_text=element_blank(),
            axis_text_x=element_text(color="purple", margin={"t": 4}),
        )
    )

    assert p == "override_axis_text"
