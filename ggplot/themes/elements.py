"""
Theme elements used to decorate the graph. These support
to the ggplot2 API.
"""

from ..utils import suppress


class element_line(object):
    """
    Theme element: Line
    """

    def __init__(self, colour=None, size=None, linetype=None,
                 lineend=None, color=None, **kwargs):
        color = color if color else colour
        d = {}
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
    """

    def __init__(self, fill=None, colour=None, size=None,
                 linetype=None, color=None, **kwargs):

        color = color if color else colour
        d = {}
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
    """

    def __init__(self, family=None, style=None, weight=None,
                 color=None, size=None, ha=None, va=None,
                 rotation=0, linespacing=None, backgroundcolor=None,
                 **kwargs):
        """
        Note
        ----
        vjust and hjust are not fully implemented, 0 or 1 is
        translated to left, bottom; right, top. Any other value is
        translated to center.
        """
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
