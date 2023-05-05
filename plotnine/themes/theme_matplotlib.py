from ..options import get_option
from .elements import element_rect, element_text
from .theme import theme


class theme_matplotlib(theme):
    """
    The default matplotlib look and feel.

    The theme can be used (and has the same parameter
    to customize) like a :class:`matplotlib.rc_context` manager.

    Parameters
    ----------
    rc :  dict, optional
        rcParams which should be applied on top of
        mathplotlib default.
    fname : str, optional
        Filename to a matplotlibrc file
    use_defaults : bool
        If `True` (the default) resets the plot setting
        to the (current) `matplotlib.rcParams` values
    """

    def __init__(self, rc=None, fname=None, use_defaults=True):
        import matplotlib as mpl

        m = get_option("base_margin")
        base_size = mpl.rcParams.get("font.size", 11)
        super().__init__(
            text=element_text(
                size=base_size,
                linespacing=1,
                rotation=0,
            ),
            aspect_ratio=get_option("aspect_ratio"),
            dpi=get_option("dpi"),
            figure_size=get_option("figure_size"),
            axis_text=element_text(margin={"t": 2.4, "r": 2.4, "units": "pt"}),
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
            legend_box_spacing=m * 3,
            legend_direction="auto",
            legend_entry_spacing_x=5,
            legend_entry_spacing_y=2,
            legend_key=element_rect(fill="None", colour="None"),
            legend_key_size=16,
            legend_margin=0,
            legend_position="right",
            legend_spacing=10,
            legend_text=element_text(
                margin={"t": 3, "b": 3, "l": 3, "r": 3, "units": "pt"}
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
                ha="right",
                va="bottom",
                ma="right",
                margin={"t": m, "units": "fig"},
            ),
            plot_margin=m,
            plot_subtitle=element_text(
                size=base_size * 0.9,
                ha="left",
                va="top",
                ma="left",
                margin={"b": m, "units": "fig"},
            ),
            plot_title=element_text(
                ha="left",
                va="top",
                ma="left",
                margin={"b": m, "units": "fig"},
            ),
            strip_align=0,
            strip_background=element_rect(
                fill="#D9D9D9", color="black", size=0.72
            ),
            strip_text=element_text(
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

        if use_defaults:
            _copy = mpl.rcParams.copy()
            if "tk.pythoninspect" in _copy:
                del _copy["tk.pythoninspect"]
            self._rcParams.update(_copy)

        if fname:
            self._rcParams.update(mpl.rc_params_from_file(fname))
        if rc:
            self._rcParams.update(rc)
