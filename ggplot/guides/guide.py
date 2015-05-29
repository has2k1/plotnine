from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import waiver
from ..utils.exceptions import GgplotError


class guide(object):
    # title
    title = waiver()
    title_position = None
    title_theme = None
    title_hjust = None
    title_vjust = None

    # label
    label = True
    label_position = None
    label_theme = None
    label_hjust = None
    label_vjust = None

    # key
    keywidth = None
    keyheight = None

    # general
    direction = None
    default_unit = 'line'
    override_aes = {}
    reverse = False
    order = 0

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                tpl = "{} does not undestand attribute '{}'"
                raise GgplotError(tpl.format(self.__class__.__name__, k))

    def _set_defaults(self, theme):
        """
        Set configuration parameters for drawing guide
        """
        valid_locations = {'top', 'bottom', 'left', 'right'}
        horizontal_locations = {'left', 'right'}
        vertical_locations = {'top', 'bottom'}
        # title position
        if self.title_position is None:
            if self.direction == 'vertical':
                self.title_position = 'top'
            elif self.direction == 'horizontal':
                self.title_position = 'left'
        if self.title_position not in valid_locations:
            msg = 'title position "{}" is invalid'
            raise GgplotError(msg.format(self.title_position))

        # direction of guide
        if self.direction is None:
            if self.label_position in horizontal_locations:
                self.direction = 'vertical'
            else:
                self.direction = 'horizontal'

        # label position
        msg = 'label position {} is invalid'
        if self.label_position is None:
            if self.direction == 'vertical':
                self.label_position = 'right'
            else:
                self.label_position = 'bottom'
        if self.label_position not in valid_locations:
            raise GgplotError(msg.format(self.label_position))
        if self.direction == 'vertical':
            if self.label_position not in horizontal_locations:
                raise GgplotError(msg.format(self.label_position))
        else:
            if self.label_position not in vertical_locations:
                raise GgplotError(msg.format(self.label_position))

        # title alignment
        self._title_align = theme._params['legend_title_align']
        if self._title_align is None:
            if self.direction == 'vertical':
                self._title_align = 'left'
            else:
                self._title_align = 'center'
