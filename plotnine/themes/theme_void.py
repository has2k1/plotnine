from ..options import get_option
from .elements import element_blank, element_text
from .theme import theme


class theme_void(theme):
    """
    A classic-looking theme, with x & y axis lines and
    no gridlines.

    Parameters
    ----------
    base_size : int, optional
        Base font size. All text sizes are a scaled versions of
        the base font size. Default is 11.
    base_family : int, optional
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
                ha="center",
                va="center",
                rotation=0,
                margin={},
            ),
            axis_text_x=element_blank(),
            axis_text_y=element_blank(),
            axis_title_x=element_blank(),
            axis_title_y=element_blank(),
            aspect_ratio=get_option("aspect_ratio"),
            dpi=get_option("dpi"),
            figure_size=get_option("figure_size"),
            legend_box="auto",
            legend_box_just="auto",
            legend_box_margin=0,
            legend_box_spacing=m * 3,
            legend_direction="auto",
            legend_entry_spacing_x=5,
            legend_entry_spacing_y=2,
            legend_key_height=18,
            legend_key_width=18,
            legend_margin=0,
            legend_position="right",
            legend_spacing=10,
            legend_text=element_text(
                size=base_size * 0.8,
                ha="left",
                margin={"t": 3, "b": 3, "l": 3, "r": 3, "units": "pt"},
            ),
            legend_text_legend=element_text(va="baseline"),
            legend_title=element_text(
                ha="left",
                margin={
                    "t": m,
                    "b": m,
                    "l": m,
                    "r": m,
                    "units": "fig",
                },
            ),
            legend_title_align="auto",
            panel_spacing=m,
            plot_caption=element_text(
                size=base_size * 0.8,
                ha="right",
                va="bottom",
                ma="left",
                margin={"t": m, "units": "fig"},
            ),
            plot_margin=m,
            plot_subtitle=element_text(
                size=base_size * 1,
                ha="left",
                va="top",
                ma="left",
                margin={"b": m, "units": "fig"},
            ),
            plot_title=element_text(
                size=base_size * 1.2,
                ha="left",
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
