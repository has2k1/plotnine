from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.patches import Rectangle

from .geom_text import geom_text

_aes = geom_text.DEFAULT_AES.copy()
_aes['fill'] = 'white'


_params = geom_text.DEFAULT_PARAMS.copy()
_params.update({
    # boxstyle is one of
    #   cirle, larrow, rarrow, round, round4,
    #   roundtooth, sawtooth, square
    #
    # Documentation at matplotlib.patches.BoxStyle
    'boxstyle': 'round',
    'label_padding': 0.25,
    'label_r': 0.25,
    'label_size': 0.7})


class geom_label(geom_text):
    DEFAULT_AES = _aes
    DEFAULT_PARAMS = _params

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw letter 'a' in the box

        Parameters
        ----------
        data : dataframe
        da : DrawingArea
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        if data['fill']:
            rect = Rectangle((0, 0),
                             width=da.width,
                             height=da.height,
                             linewidth=0,
                             alpha=data['alpha'],
                             facecolor=data['fill'],
                             capstyle='projecting')
            da.add_artist(rect)
        return geom_text.draw_legend(data, da, lyr)
