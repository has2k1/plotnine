from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .scale import scale
from copy import deepcopy


class scale_colour_manual(scale):
    """
    Specify a list of colors to use manually.
    
    Parameters
    ----------
    values : list of colors/strings
        List of colors with length greater than or equal to the number
        of unique discrete items to which you want to apply color.
        
    Examples
    --------
    >>> from ggplot import *
    >>> color_list = ['#FFAAAA', '#ff5b00', '#c760ff', '#f43605', '#00FF00',
    ...               '#0000FF', '#4c9085']
    >>> lng = pd.melt(meat, ['date'])
    >>> gg = ggplot(lng, aes('date', 'value', color='variable')) + \\
    ...     geom_point()
    >>> print(gg + scale_colour_manual(values=color_list) + \\
    ...     ggtitle('With manual colors'))
    >>> print(gg + ggtitle('Without manual colors'))
    """
    VALID_SCALES = ['values']
    def __radd__(self, gg):
        gg = deepcopy(gg)
        if not (self.values is None):
            n_colors_needed = gg.data[gg.aesthetics['color']].nunique()
            n_colors_provided = len(self.values)
            if n_colors_provided < n_colors_needed:
                msg = 'Error: Insufficient values in manual scale. {0} needed but only {1} provided.'
                raise Exception(msg.format(n_colors_needed, n_colors_provided))
            gg.manual_color_list = self.values[:n_colors_needed]
        return gg

