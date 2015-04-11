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
            try:
                setattr(self, k, v)
            except AttributeError:
                tpl = "{} does not undestand attribute '{}'"
                raise GgplotError(tpl.format(self.__class__.__name__), k)
