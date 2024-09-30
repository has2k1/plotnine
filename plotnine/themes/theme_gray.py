from .._utils.registry import alias
from ..options import get_option
from .elements import element_blank, element_line, element_rect, element_text
from .theme import theme


class theme_gray(theme):
    """
    A gray background with white gridlines.

    This is the default theme

    Parameters
    ----------
    base_size : int
        Base font size. All text sizes are a scaled versions of
        the base font size.
    base_family : str
        Base font family. If `None`, use [](`plotnine.options.base_family`).
    """

    def __init__(self, base_size=11, base_family=None):
        base_family = base_family or get_option("base_family")
        quarter_line = base_size / 4
        fifth_line = base_size / 5
        eighth_line = base_size / 8
        m = get_option("base_margin")

        super().__init__(
            line=element_line(
                color="black", size=1, linetype="solid", lineend="butt"
            ),
            rect=element_rect(
                fill="white", color="black", size=1, linetype="solid"
            ),
            text=element_text(
                family=base_family,
                style="normal",
                color="black",
                size=base_size,
                linespacing=0.9,
                rotation=0,
                margin={},
            ),
            aspect_ratio=get_option("aspect_ratio"),
            axis_line=element_line(),
            axis_line_x=element_blank(),
            axis_line_y=element_blank(),
            axis_text=element_text(size=base_size * 0.8, color="#4D4D4D"),
            axis_text_x=element_text(va="top", margin={"t": fifth_line}),
            axis_text_y=element_text(ha="right", margin={"r": fifth_line}),
            axis_ticks=element_line(color="#333333"),
            axis_ticks_length=0,
            axis_ticks_length_major=quarter_line,
            axis_ticks_length_minor=eighth_line,
            axis_ticks_minor=element_blank(),
            axis_ticks_pad=2,
            axis_title_x=element_text(
                va="bottom", ha="center", margin={"t": m, "units": "fig"}
            ),
            axis_title_y=element_text(
                angle=90,
                va="center",
                ha="left",
                margin={"r": m, "units": "fig"},
            ),
            dpi=get_option("dpi"),
            figure_size=get_option("figure_size"),
            # legend, None values are for parameters where the
            # drawing routines can make better decisions than
            # can be pre-determined in the theme.
            legend_background=element_rect(color="none"),
            legend_box_margin=0,  # points
            legend_box_spacing=m * 3,  # figure units
            legend_frame=element_blank(),
            legend_key_spacing_x=6,
            legend_key_spacing_y=2,
            legend_key=element_rect(fill="#F2F2F2", colour="none"),
            legend_key_size=base_size * 0.8 * 1.8,
            legend_ticks_length=0.2,
            legend_margin=0,  # points
            legend_position="right",
            legend_spacing=10,  # points
            legend_text=element_text(
                size=base_size * 0.8,
                margin={
                    "t": m / 1.5,
                    "b": m / 1.5,
                    "l": m / 1.5,
                    "r": m / 1.5,
                    "units": "fig",
                },
            ),
            legend_ticks=element_line(color="#CCCCCC", size=1),
            legend_title=element_text(
                margin={
                    "t": m,
                    "b": m / 2,
                    "l": m * 2,
                    "r": m * 2,
                    "units": "fig",
                },
            ),
            panel_background=element_rect(fill="#EBEBEB"),
            panel_border=element_blank(),
            panel_grid_major=element_line(color="white", size=1),
            panel_grid_minor=element_line(color="white", size=0.5),
            panel_spacing=m,
            plot_background=element_rect(color="white"),
            plot_caption=element_text(
                size=base_size * 0.8,
                ha="right",
                va="bottom",
                ma="left",
                margin={"t": m, "units": "fig"},
            ),
            plot_margin=m,
            plot_subtitle=element_text(
                va="top",
                ma="left",
                margin={"b": m, "units": "fig"},
            ),
            plot_title=element_text(
                size=base_size * 1.2,
                va="top",
                ma="left",
                margin={"b": m, "units": "fig"},
            ),
            strip_align=0,
            strip_background=element_rect(color="none", fill="#D9D9D9"),
            strip_background_x=element_rect(width=1),
            strip_background_y=element_rect(height=1),
            strip_text=element_text(
                color="#1A1A1A",
                size=base_size * 0.8,
                linespacing=1.0,
                margin={
                    "t": 1 / 3,
                    "b": 1 / 3,
                    "l": 1 / 3,
                    "r": 1 / 3,
                    "units": "lines",
                },
            ),
            strip_text_y=element_text(rotation=-90),
            complete=True,
        )


@alias
class theme_grey(theme_gray):
    pass
