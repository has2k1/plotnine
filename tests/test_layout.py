import numpy as np
import pandas as pd

from plotnine import (
    aes,
    annotate,
    coord_cartesian,
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
    theme_matplotlib,
)
from plotnine.data import mtcars

black_frame = theme(
    legend_frame=element_rect(color="black"),
    legend_ticks=element_line(color="black"),
)

red_frame = theme(
    legend_frame=element_rect(color="red"),
    legend_ticks=element_line(color="red"),
)

data = pd.DataFrame({"x": range(11), "y": range(11)})


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

    def test_axis_title_x_justification(self):
        p = self.g + theme(axis_title_x=element_text(ha=0.2))
        assert p == "axis_title_x_justification"

    def test_axis_title_y_justification(self):
        p = self.g + theme(axis_title_y=element_text(va=0.8))
        assert p == "axis_title_y_justification"

    def test_plot_title_justification(self):
        p = self.g + theme(plot_title=element_text(ha=1))
        assert p == "plot_title_justification"

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
            + scale_y_continuous(
                labels=["0", "1", "2", "3", "four-four-four-four"]
            )
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

    def test_plot_titles_and_caption_positioning(self):
        p = self.g + theme(
            plot_title_position="plot",
            plot_caption_position="plot",
        )
        assert p == "plot_titles_and_caption_positioning"


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

    def test_justification_with_blank_title_and_text(self):
        p = (
            self.g
            + aes(shape="factor(cyl)")
            + guides(color=guide_colorbar(position="top"))
            + theme(
                legend_justification_top="left",
                legend_justification_right="top",
                legend_text=element_blank(),
                legend_title=element_blank(),
            )
        )
        assert p == "justification_with_blank_title_and_text"


class TestPlotTagLayout:
    g = (
        ggplot(data)
        + geom_point(aes("x", "y", color="x"))
        + annotate(
            "point", x=5, y=5, color="green", shape="s", size=10, alpha=0.5
        )
        + annotate("vline", xintercept=5, color="green", size=0.5, alpha=0.5)
        + annotate("hline", yintercept=5, color="green", size=0.5, alpha=0.5)
        + annotate(
            "vline",
            xintercept=[2.5, 7.5],
            color="green",
            size=0.5,
            alpha=0.125,
        )
        + annotate(
            "hline",
            yintercept=[2.5, 7.5],
            color="green",
            size=0.5,
            alpha=0.125,
        )
        + labs(
            tag="ABC",
            title="The Title of the Plot",
            subtitle="The Subtitle of the Plot is Longer than the title",
        )
        + coord_cartesian(expand=False)
        + theme_matplotlib()
        + theme(
            plot_tag=element_text(color="red"),
            plot_background=element_rect(color="black"),
        )
    )

    def test_default_tag_location(self):
        assert self.g == "default_tag_location"

    def test_margin_bottom(self):
        p = self.g + theme(
            plot_tag_location="margin",
            plot_tag_position="bottom",
        )
        assert p == "margin_bottom"

    def test_plot_topright(self):
        p = self.g + theme(
            plot_tag_location="plot",
            plot_tag_position="topright",
        )
        assert p == "plot_topright"

    def test_plot_topright_margin_in_fig(self):
        p = self.g + theme(
            plot_tag=element_text(
                margin={"t": 0.025, "r": 0.45, "unit": "fig"}
            ),
            plot_tag_location="plot",
            plot_tag_position="topright",
        )
        assert p == "plot_topright_margin_in_fig"

    def test_plot_topright_margin_in_pt(self):
        p = self.g + theme(
            plot_tag=element_text(margin={"t": 10, "r": 200, "unit": "pt"}),
            plot_tag_location="plot",
            plot_tag_position="topright",
        )
        assert p == "plot_topright_margin_in_pt"

    def test_panel_bottomleft(self):
        p = self.g + theme(
            plot_tag_location="panel",
            plot_tag_position="bottomleft",
        )
        assert p == "panel_bottomleft"

    def test_panel_topleft_margin_in_fig(self):
        # In the center of the bottom-left quadrant
        p = self.g + theme(
            plot_tag=element_text(
                margin={"t": 0.75, "l": 0.75, "unit": "fig"}
            ),
            plot_tag_location="panel",
            plot_tag_position="topleft",
        )
        assert p == "panel_topleft_margin_in_fig"

    def test_panel_topleft_margin_in_pt(self):
        # The topleft point fo the panel and that of the tag
        # should define a square space. This is easier to confirm
        # when the aspect_ratio = 1
        p = self.g + theme(
            plot_tag=element_text(margin={"t": 150, "l": 150, "unit": "pt"}),
            plot_tag_location="panel",
            plot_tag_position="topleft",
        )
        assert p == "panel_topleft_margin_in_pt"

    def test_panel_topleft_margin_in_pt_ar1(self):
        # The bottomleft point fo the panel and that of the tag
        # should define a square space.
        # When the margins are equal the tag should fall along the diagonal
        p = self.g + theme(
            aspect_ratio=1,
            plot_tag=element_text(margin={"b": 150, "l": 150, "unit": "pt"}),
            plot_tag_location="panel",
            plot_tag_position="bottomleft",
        )
        assert p == "panel_topleft_margin_in_pt_ar1"

    def test_plot_xycoords(self):
        p = self.g + theme(
            plot_tag_location="plot",
            plot_tag_position=(0.15, 0.95),
        )
        assert p == "plot_xycoords"

    def test_panel_xycoords(self):
        p = self.g + theme(
            plot_tag_location="panel",
            plot_tag_position=(0.15, 0.95),
        )
        assert p == "panel_xycoords"


def test_axis_text_justification():
    data = pd.DataFrame(
        {
            "x": ["A", "BB", "CCCC", "DDDDD\nDDDDD"],
            "y": ["A", "BB", "CCCC", "DDDDDDDDDD"],
        }
    )
    p = (
        ggplot(data, aes(x="x", y="y"))
        + geom_point()
        + theme(
            axis_text_y=element_text(ha="left"),
            axis_text_x=element_text(va="bottom"),
        )
    )

    assert p == "axis_text_justification"
