from .elements import element_blank
from .theme import theme
from .theme_bw import theme_bw


class theme_tufte(theme_bw):
    """
    Tufte Maximal Data, Minimal Ink Theme

    Theme based on Chapter 6 Data-Ink Maximization and Graphical
    Design of Edward Tufte *The Visual Display of Quantitative
    Information*. No border, no axis lines, no grids. This theme
    works best in combination with
    [](`~plotnine.geoms.geom_rug.geom_rug`).

    The default font family is set to "serif" as he uses serif
    fonts for labels in _The Visual Display of Quantitative
    Information_. The serif font used by Tufte in his books is
    a variant of Bembo, while the sans serif font is Gill Sans.
    If these fonts are installed on your system, consider setting
    them explicitly via the argument `base_family`.

    Parameters
    ----------
    base_size : int
        Base font size. All text sizes are a scaled versions of
        the base font size.
    base_family : str
        Base font family. If `None`, use [](`plotnine.options.base_family`).
    ticks: bool
        Whether to show axis ticks.

    References
    ----------
    Tufte, Edward R. (2001) The Visual Display of Quantitative
    Information, Chapter 6.

    Translated from the R ggthemes package by hyiltiz <hyiltiz@gmail.com>.
    Released under GNU GPL v2 license or later.
    """

    def __init__(self, base_size=11, base_family=None, ticks=True):
        theme_bw.__init__(self, base_size, base_family)
        d = {} if ticks else {"axis_ticks": element_blank()}
        self += theme(
            axis_line=element_blank(),
            legend_background=element_blank(),
            legend_key=element_blank(),
            panel_background=element_blank(),
            panel_border=element_blank(),
            panel_grid=element_blank(),
            plot_background=element_blank(),
            strip_background=element_blank(),
            **d,  # pyright: ignore
        )
