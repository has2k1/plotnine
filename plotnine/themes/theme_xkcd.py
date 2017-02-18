from copy import copy, deepcopy

from matplotlib import patheffects

from .elements import (element_line, element_rect, element_blank,
                       element_text)
from .theme import theme
from .theme_gray import theme_gray


class theme_xkcd(theme_gray):
    """
    xkcd theme

    Parameters
    ----------
    """
    def __init__(self, base_size=12, scale=1, length=100, randomness=2):
        theme_gray.__init__(self, base_size)
        self.add_theme(
            theme(
                text=element_text(
                    family=['xkcd', 'Humor Sans', 'Comic Sans MS']),
                axis_ticks=element_line(color='black', size=3),
                axis_ticks_direction='in',
                axis_ticks_major_length=8,
                legend_background=element_rect(
                    color='black', fill='None'),
                legend_key=element_rect(fill='None'),
                panel_border=element_rect(color='black', size=1.5),
                panel_grid=element_blank(),
                panel_background=element_rect(fill='white'),
                strip_background=element_rect(
                    color='black', fill='white'),
                strip_background_x=element_rect(width=2/3),
                strip_background_y=element_rect(height=2/3),
                strip_margin=-0.5,
            ),
            inplace=True)

        d = {'axes.unicode_minus': False,
             'path.sketch':  (scale, length, randomness),
             'path.effects':  [
                 patheffects.withStroke(linewidth=4, foreground='white')]
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
            if key == '_rcParams':
                continue
            new[key] = deepcopy(old[key], memo)

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
