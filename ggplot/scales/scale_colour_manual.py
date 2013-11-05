from .scale import scale
from copy import deepcopy
import numpy as np

class scale_colour_manual(scale):
    """
    Specify a list of colors to use manually.
    args:
        values:
            List of colors with length greater than or equal to the number
            of unique discrete items to which you want to apply color.
    examples:
        from ggplot import *

        color_list = ['#FFAAAA', '#ff5b00', '#c760ff', '#f43605', '#00FF00', '#0000FF', '#4c9085']
        lng = pd.melt(meat, ['date'])

        print ggplot(lng, aes('date', 'value', color='variable')) + \
            geom_point() + \
            scale_colour_manual(values=color_list) + \
            ggtitle('With manual colors')

        print ggplot(lng, aes('date', 'value', color='variable')) + \
            geom_point() + \
            ggtitle('Without manual colors')

        plt.show(1)
    """
    VALID_SCALES = ['values']
    def __radd__(self, gg):
        gg = deepcopy(gg)
        if self.values:
            n_colors_needed   = gg.data[gg.aesthetics['color']].nunique()
            n_colors_provided = len(self.values)
            if n_colors_provided < n_colors_needed:
                msg = 'Error: Insufficient values in manual scale. {0} needed but only {1} provided.'
                raise Exception(msg.format(n_colors_needed, n_colors_provided))
            gg.manual_color_list = self.values[:n_colors_needed]
        return gg

