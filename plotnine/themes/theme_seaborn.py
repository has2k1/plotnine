from ..options import get_option
from .elements import element_rect, element_text
from .theme import theme


class theme_seaborn(theme):
    """
    Theme for seaborn.

    Credit to Michael Waskom's seaborn:

        - http://stanford.edu/~mwaskom/software/seaborn
        - https://github.com/mwaskom/seaborn

    Parameters
    ----------
    style: str in ``['whitegrid', 'darkgrid', 'nogrid', 'ticks']``
        Style of axis background.
    context: str in ``['notebook', 'talk', 'paper', 'poster']``
        Intended context for resulting figures.
    font : str
        Font family, see matplotlib font manager.
    font_scale : float, optional
        Separate scaling factor to independently scale the
        size of the font elements.
    """

    def __init__(
        self,
        style="darkgrid",
        context="notebook",
        font="sans-serif",
        font_scale=1,
    ):
        from .seaborn_rcmod import set_theme

        rcparams = set_theme(
            context=context, style=style, font=font, font_scale=font_scale
        )
        base_size = rcparams["font.size"]
        half_line = base_size / 2
        line_margin = half_line * 0.8 / 2
        m = get_option("base_margin")

        super().__init__(
            aspect_ratio=get_option("aspect_ratio"),
            dpi=get_option("dpi"),
            figure_size=get_option("figure_size"),
            text=element_text(size=base_size, rotation=0),
            axis_text=element_text(
                size=base_size * 0.8,
                margin={
                    "t": line_margin,
                    "b": line_margin,
                    "l": line_margin,
                    "r": line_margin,
                    "units": "pt",
                },
            ),
            axis_title_x=element_text(
                va="bottom", ha="center", margin={"t": m, "units": "fig"}
            ),
            axis_title_y=element_text(
                angle=90,
                va="center",
                ha="left",
                margin={"r": m, "units": "fig"},
            ),
            legend_box="auto",
            legend_box_just="auto",
            legend_box_margin=0,
            legend_box_spacing=m * 3,  # figure units
            legend_direction="auto",
            legend_entry_spacing_x=5,
            legend_entry_spacing_y=2,
            legend_key_size=base_size * 0.8 * 1.8,
            legend_margin=0,
            legend_position="right",
            legend_spacing=10,  # points
            legend_text=element_text(
                va="baseline",
                ha="left",
                margin={"t": 3, "b": 3, "l": 3, "r": 3, "units": "pt"},
            ),
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
            strip_background=element_rect(color="None", fill="#D1CDDF"),
            strip_text=element_text(
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

        self._rcParams.update(rcparams)
