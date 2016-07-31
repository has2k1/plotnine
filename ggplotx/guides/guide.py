from __future__ import absolute_import, division, print_function


from six import add_metaclass

from ..utils import waiver, Registry
from ..utils.exceptions import GgplotError


@add_metaclass(Registry)
class guide(object):
    """
    Base class for all guides

    Parameters
    ----------
    title : str | None
        Title of the guide. If ``None``, title is not shown.
        Default is the name of the aesthetic or the name
        specified using :class:`~ggplotx.components.labels.lab`
    title_position : 'top' | 'bottom' | 'left' | 'right'
        Position of title
    title_theme : element_text
        Control over the title theme.
        Default is to use ``legend_title`` in a theme.
    title_hjust : float
        Horizontal justification of title text.
    title_vjust : float
        Vertical justification of title text.
    title_separation : float
        Separation between the title text and the colorbar.
        Value is in pixels.
    label : bool
        Whether to show labels
    label_position : 'top' | 'bottom' | 'left' | 'right'
        Position of the labels.
        The defaults are ``'bottom'`` for a horizontal guide and
        '``right``' for a vertical guide.
    label_theme : element_text
        Control over the label theme.
        Default is to use ``legend_text`` in a theme.
    label_hjust : float
        Horizontal justification of label text.
    label_vjust : float
        Vertical justification of label text.
    label_separation : float
        Separation between the label text and the colorbar.
        Value is in pixels.
    direction : 'horizontal' | 'vertical'
        Direction of the guide.
    default_unit : str
        Unit for ``keywidth`` and ``keyheight``
    override_aes : list_like
        Aesthetic parameters of legend key.
    reverse : bool
        Whether to reverse the order of the legends.
    order : int
        Order of this guide among multiple guides.
        Should be in the range [0, 99]. Default is ``0``.

    Note
    ----
    At the moment not all parameters have been fully implemented.
    """
    __base__ = True

    # title
    title = waiver()
    title_position = None
    title_theme = None
    title_hjust = None
    title_vjust = None
    title_separation = 8

    # label
    label = True
    label_position = None
    label_theme = None
    label_hjust = None
    label_vjust = None
    label_separation = 3

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

        # Must be updated before the draw method is called
        self.theme = None

    def _default(self, key, default=None):
        """
        Lookup value of *key* themeable

        If *key* not in themeable or value is None,
        return the *default* value.
        """
        try:
            value = self.theme.themeables.property(key)
        except KeyError:
            value = None

        return value if value is not None else default

    def _set_defaults(self):
        """
        Set configuration parameters for drawing guide
        """
        valid_locations = {'top', 'bottom', 'left', 'right'}
        horizontal_locations = {'left', 'right'}
        get_property = self.theme.themeables.property

        # label position
        self.label_position = self.label_position or 'right'
        if self.label_position not in valid_locations:
            msg = "label position '{}' is invalid"
            raise GgplotError(msg.format(self.label_position))

        # direction of guide
        if self.direction is None:
            if self.label_position in horizontal_locations:
                self.direction = 'vertical'
            else:
                self.direction = 'horizontal'

        # title position
        if self.title_position is None:
            if self.direction == 'vertical':
                self.title_position = 'top'
            elif self.direction == 'horizontal':
                self.title_position = 'left'
        if self.title_position not in valid_locations:
            msg = "title position '{}' is invalid"
            raise GgplotError(msg.format(self.title_position))

        # title alignment
        tmp = 'left' if self.direction == 'vertical' else 'center'
        self._title_align = self._default('legend_title_align', tmp)

        # by default, direction of each guide depends on
        # the position all the guides
        try:
            position = get_property('legend_position')
        except KeyError:
            position = 'right'

        if position in {'top', 'bottom'}:
            tmp = 'horizontal'
        else:  # left, right, (default)
            tmp = 'vertical'
        self.direction = self._default('legend_direction', tmp)
