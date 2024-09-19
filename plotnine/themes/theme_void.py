from ..options import get_option
from .elements import element_blank, element_line, element_text
from .theme import theme


class theme_void(theme):
    """
    A classic-looking theme, with x & y axis lines and
    no gridlines.

    Parameters
    ----------
    base_size : int
        Base font size. All text sizes are a scaled versions of
        the base font size.
    base_family : str
        Base font family.
    """

    def __init__(self, base_size=11, base_family=None):
        base_family = base_family or get_option("base_family")
        m = get_option("base_margin")
        # Use only inherited elements and make everything blank
        theme.__init__(
            self,
            line=element_blank(),
            rect=element_blank(),
            text=element_text(
                family=base_family,
                style="normal",
                color="black",
                size=base_size,
                linespacing=0.9,
                rotation=0,
                margin={},
            ),
            axis_text_x=element_blank(),
            axis_text_y=element_blank(),
            axis_title_x=element_blank(),
            axis_title_y=element_blank(),
            axis_ticks_length=0,
            aspect_ratio=get_option("aspect_ratio"),
            dpi=get_option("dpi"),
            figure_size=get_option("figure_size"),
            legend_box_margin=0,
            legend_box_spacing=m * 3,
            legend_key_spacing_x=6,
            legend_key_spacing_y=2,
            legend_frame=element_blank(),
            legend_key_size=base_size * 0.8 * 1.8,
            legend_ticks_length=0.2,
            legend_margin=0,
            legend_position="right",
            legend_spacing=10,
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
            panel_spacing=m,
            plot_caption=element_text(
                size=base_size * 0.8,
                ha="right",
                va="bottom",
                ma="left",
                margin={"t": m, "units": "fig"},
            ),
            plot_margin=0,
            plot_subtitle=element_text(
                size=base_size * 1,
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
            complete=True,
        )
