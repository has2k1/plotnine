from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .scale import scale
from copy import deepcopy
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, rgb2hex, ColorConverter


def colors_at_breaks(cmap, breaks=[0, 0.25, 0.5, 0.75, 1.]):
    return [rgb2hex(cmap(bb)[:3]) for bb in breaks]


class scale_colour_gradient(scale):
    """
    Specify a two- or three-point gradient.

    Parameters
    ----------
    name : Name of an existing gradient scheme
    limits : list of the upper and lower bounds of the gradient
    low : colour at the lower bound of the gradient
    mid : colour at the middle of the gradient
    high : Colour at the upper bound of the gradient

    Examples
    --------
    >>> from ggplot import *
    >>> diamons_premium = diamonds[diamonds.cut=='Premium']
    >>> gg = ggplot(diamons_premium, aes(x='depth', y='carat', colour='price')) + \\
    ...     geom_point()
    >>> print(gg + scale_colour_gradient(low='red', mid='white', high='blue', limits=[4000,6000]) + \\
    ...     ggtitle('With red-blue gradient'))
    >>> print(gg + ggtitle('With standard gradient'))
    """
    VALID_SCALES = ['name', 'limits', 'low', 'mid', 'high']

    def __radd__(self, gg):
        gg = deepcopy(gg)
        if self.name:
            gg.color_label = self.name
        if not (self.limits is None):
            gg.color_limits = self.limits
        color_spectrum = []
        if self.low:
            color_spectrum.append(self.low)
        if self.mid:
            color_spectrum.append(self.mid)
        if self.high:
            color_spectrum.append(self.high)

        if self.low and self.high:
            gradient2n = LinearSegmentedColormap.from_list('gradient2n', color_spectrum)
            plt.cm.register_cmap(cmap=gradient2n)
            # add them back to ggplot
            gg.color_scale = colors_at_breaks(gradient2n)
            gg.colormap = gradient2n

        return gg

