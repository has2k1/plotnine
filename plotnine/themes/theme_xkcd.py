from copy import copy, deepcopy

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
        stroke_size=4,
        stroke_color="white",
    ):
        from matplotlib import patheffects

        super().__init__(base_size)
        self += theme(
            text=element_text(family=["xkcd", "Humor Sans", "Comic Sans MS"]),
            axis_ticks=element_line(color="black", size=1.5),
            axis_ticks_minor=element_blank(),
            axis_ticks_direction="in",
            axis_ticks_length_major=6,
            legend_background=element_rect(color="black", fill="None"),
            legend_margin=5,
            legend_key=element_rect(fill="None"),
            panel_border=element_rect(color="black", size=1.5),
            panel_grid=element_blank(),
            panel_background=element_rect(fill="white"),
            strip_background=element_rect(color="black", fill="white"),
            strip_background_x=element_rect(width=2 / 3.0),
            strip_background_y=element_rect(height=2 / 3.0),
            strip_align=-0.5,
        )

        d = {
            "axes.unicode_minus": False,
            "path.sketch": (scale, length, randomness),
            "path.effects": [
                patheffects.withStroke(
                    linewidth=stroke_size, foreground=stroke_color
                )
            ],
        }
        self._rcParams.update(d)

    def __deepcopy__(self, memo):
        """
        Deep copy support for theme_xkcd
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        for key, item in old.items():
            if key == "_rcParams":
                continue
            new[key] = deepcopy(item, memo)

        result._rcParams = {}
        for k, v in self._rcParams.items():
            try:
                result._rcParams[k] = deepcopy(v, memo)
            except NotImplementedError:
                # deepcopy raises an error for objects that are
                # drived from or composed of
                # matplotlib.transform. TransformNode.
                # Not desirable, but probably requires upstream fix.
                # In particular, XKCD uses
                # matplotlib.patheffects.withStrok
                # -gdowding
                result._rcParams[k] = copy(v)

        return result
