"""
Theme elements used to decorate the graph.
"""

from ..utils import suppress


class element_line(object):
    """
    Theme element: Line

    Used for backgrounds and borders

    Parameters
    ----------
    color : str | tuple
        Line color
    colour : str | tuple
        Alias of color
    linetype : str | tuple
        Line style. See
        :meth:`matplotlib.lines.Line2D.set_linestyle`
        for specification.
    size : float
        Line thickness
    kwargs : dict
        Parameters recognised by
        :class:`matplotlib.lines.Line2D`.
    """

    def __init__(self, color=None, size=None, linetype=None,
                 lineend=None, colour=None, **kwargs):
        color = color if color else colour
        d = {'visible': True}
        if color:
            d['color'] = color
        if size:
            d['linewidth'] = size
        if linetype:
            d['linestyle'] = linetype

        if linetype in ('solid', '-') and lineend:
            d['solid_capstyle'] = lineend
        elif linetype and lineend:
            d['dashed_capstyle'] = lineend

        d.update(**kwargs)
        self.properties = d


class element_rect(object):
    """
    Theme element: Rectangle

    Used for backgrounds and borders

    Parameters
    ----------
    fill : str | tuple
        Rectangle background color
    color : str | tuple
        Line color
    colour : str | tuple
        Alias of color
    size : float
        Line thickness
    kwargs : dict
        Parameters recognised by
        :class:`matplotlib.patches.Rectangle`. In some cases
        you use the fancy parameters from
        :class:`matplotlib.patches.FancyBboxPatch`
    """

    def __init__(self, fill=None, color=None, size=None,
                 linetype=None, colour=None, **kwargs):

        color = color if color else colour
        d = {'visible': True}
        if fill:
            d['facecolor'] = fill
        if color:
            d['edgecolor'] = color
        if size:
            d['linewidth'] = size
        if linetype:
            d['linestyle'] = linetype

        d.update(**kwargs)
        self.properties = d


class element_text(object):
    """
    Theme element: Text

    Parameters
    ----------
    family : str
        Font family
    style : 'normal' | 'italic' | 'oblique'
        Font style
    color : str | tuple
        Text color
    weight : str
        Should be one of *normal*, *bold*, *heavy*, *light*,
        *ultrabold* or *ultralight*.
    size : float
        text size
    ha : 'center' | 'left' | 'right'
        Horizontal Alignment.
    va : 'center' | 'top' | 'bottom' | 'baseline'
        Vertical alignment.
    rotation : float
        Rotation angle in the range [0, 360]
    linespacing : float
        Line spacing
    backgroundcolor : str | tuple
        Background color
    kwargs : dict
        Parameters recognised by :class:`matplotlib.text.Text`

    Note
    ----
    :class:`element_text` will accept parameters that conform to the
    **ggplot2** *element_text* API, but it is preferable the
    **Matplotlib** based API described above.
    """

    def __init__(self, family=None, style=None, weight=None,
                 color=None, size=None, ha=None, va=None,
                 rotation=0, linespacing=None, backgroundcolor=None,
                 **kwargs):
        d = {'visible': True}

        # ggplot2 translation
        with suppress(KeyError):
            linespacing = kwargs.pop('lineheight')
        with suppress(KeyError):
            color = color or kwargs.pop('colour')
        with suppress(KeyError):
            _face = kwargs.pop('face')
            if _face == 'plain':
                style = 'normal'
            elif _face == 'italic':
                style = 'italic'
            elif _face == 'bold':
                weight = 'bold'
            elif _face == 'bold.italic':
                style = 'italic'
                weight = 'bold'
        with suppress(KeyError):
            ha = self._translate_hjust(kwargs.pop('hjust'))
        with suppress(KeyError):
            va = self._translate_vjust(kwargs.pop('vjust'))
        with suppress(KeyError):
            rotation = kwargs.pop('angle')

        # Use the parameters that have been set
        names = ('backgroundcolor', 'color', 'family', 'ha',
                 'linespacing', 'rotation', 'size', 'style',
                 'va', 'weight',)
        variables = locals()
        for name in names:
            if variables[name] is not None:
                d[name] = variables[name]

        d.update(**kwargs)
        self.properties = d

    def _translate_hjust(self, just):
        """
        Translate ggplot2 justification from [0, 1] to left, right, center.
        """
        if just == 0:
            return 'left'
        elif just == 1:
            return 'right'
        else:
            return 'center'

    def _translate_vjust(self, just):
        """
        Translate ggplot2 justification from [0, 1] to top, bottom, center.
        """
        if just == 0:
            return 'bottom'
        elif just == 1:
            return 'top'
        else:
            return 'center'


class element_blank(object):
    """
    Theme element: Blank
    """
    def __init__(self):
        self.properties = {}
