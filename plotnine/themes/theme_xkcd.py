from .elements import element_blank, element_line, element_rect, element_text
from .theme import theme
from .theme_gray import theme_gray


class theme_xkcd(theme_gray):
    """
    xkcd theme

    Parameters
    ----------
    base_size : int
        Base font size. All text sizes are a scaled versions of
        the base font size.
    scale : float
        The amplitude of the wiggle perpendicular to the line (in pixels)
    length : float
        The length of the wiggle along the line (in pixels).
    randomness : float
        The factor by which the length is randomly scaled. Default is 2.
    stroke_size : float
        Size of the stroke to apply to the lines and text paths.
    stroke_color : str | tuple
        Color of the strokes. Use `"none"` for no color.
    """

    def __init__(
        self,
        base_size=12,
        scale=1,
        length=100,
        randomness=2,
        stroke_size=3,
        stroke_color="white",
    ):
        from matplotlib import patheffects

        super().__init__(base_size)
        sketch_params = (scale, length, randomness)
        path_effects = [
            patheffects.withStroke(
                linewidth=stroke_size, foreground=stroke_color
            )
        ]
        self += theme(
            text=element_text(family=["xkcd", "Humor Sans", "Comic Sans MS"]),
            axis_ticks=element_line(color="black", size=1),
            axis_ticks_minor=element_blank(),
            axis_ticks_direction="in",
            axis_ticks_length_major=6,
            legend_background=element_rect(color="black"),
            legend_box_margin=2,
            legend_margin=5,
            legend_key=element_rect(fill="none"),
            panel_border=element_rect(color="black", size=1),
            panel_grid=element_blank(),
            panel_background=element_rect(fill="white"),
            strip_background=element_rect(color="black", fill="white"),
            strip_background_x=element_rect(width=2 / 3),
            strip_background_y=element_rect(height=2 / 3),
            strip_align=-0.5,
        )

        self._rcParams.update(
            {
                "axes.unicode_minus": False,
                "path.sketch": sketch_params,
                "path.effects": path_effects,
            }
        )
