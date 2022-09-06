"""
Theme elements used to decorate the graph.
"""
from contextlib import suppress


class element_base:
    """
    Base class for all theme elements
    """
    properties = None  # dict of the properties

    def __init__(self):
        self.properties = {'visible': True}

    def __repr__(self):
        """
        Element representation
        """
        return f'{self.__class__.__name__}({self})'

    def __str__(self):
        """
        Element as string
        """
        d = self.properties.copy()
        del d['visible']
        return f'{d}'


class element_line(element_base):
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
        Line style. If a string, it should be one of *solid*, *dashed*,
        *dashdot* or *dotted*. You can create interesting dashed patterns
        using tuples, see :meth:`matplotlib.lines.Line2D.set_linestyle`.
    size : float
        Line thickness
    kwargs : dict
        Parameters recognised by
        :class:`matplotlib.lines.Line2D`.
    """

    def __init__(self, color=None, size=None, linetype=None,
                 lineend=None, colour=None, **kwargs):
        super().__init__()
        self.properties.update(**kwargs)

        color = color if color else colour
        if color:
            self.properties['color'] = color
        if size:
            self.properties['linewidth'] = size
        if linetype:
            self.properties['linestyle'] = linetype

        if linetype in ('solid', '-') and lineend:
            self.properties['solid_capstyle'] = lineend
        elif linetype and lineend:
            self.properties['dash_capstyle'] = lineend


class element_rect(element_base):
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
        you can use the fancy parameters from
        :class:`matplotlib.patches.FancyBboxPatch`.
    """

    def __init__(self, fill=None, color=None, size=None,
                 linetype=None, colour=None, **kwargs):
        super().__init__()
        self.properties.update(**kwargs)

        color = color if color else colour
        if fill:
            self.properties['facecolor'] = fill
        if color:
            self.properties['edgecolor'] = color
        if size:
            self.properties['linewidth'] = size
        if linetype:
            self.properties['linestyle'] = linetype


class element_text(element_base):
    """
    Theme element: Text

    Parameters
    ----------
    family : str
        Font family. See :meth:`matplotlib.text.Text.set_family`
        for supported values.
    style : str in ``['normal', 'italic', 'oblique']``
        Font style
    color : str | tuple
        Text color
    weight : str
        Should be one of *normal*, *bold*, *heavy*, *light*,
        *ultrabold* or *ultralight*.
    size : float
        text size
    ha : str in ``['center', 'left', 'right']``
        Horizontal Alignment.
    va : str in ``['center' , 'top', 'bottom', 'baseline']``
        Vertical alignment.
    rotation : float
        Rotation angle in the range [0, 360]
    linespacing : float
        Line spacing
    backgroundcolor : str | tuple
        Background color
    margin : dict
        Margin around the text. The keys are one of
        ``['t', 'b', 'l', 'r']`` and ``units``. The units are
        one of ``['pt', 'lines', 'in']``. The *units* default
        to ``pt`` and the other keys to ``0``. Not all text
        themeables support margin parameters and other than the
        ``units``, only some of the other keys may apply.
    kwargs : dict
        Parameters recognised by :class:`matplotlib.text.Text`

    Notes
    -----
    :class:`element_text` will accept parameters that conform to the
    **ggplot2** *element_text* API, but it is preferable the
    **Matplotlib** based API described above.
    """

    def __init__(self, family=None, style=None, weight=None,
                 color=None, size=None, ha=None, va=None,
                 rotation=None, linespacing=None, backgroundcolor=None,
                 margin=None, **kwargs):

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

        super().__init__()
        self.properties.update(**kwargs)

        if margin is not None:
            margin = Margin(self, **margin)

        # Use the parameters that have been set
        names = ('backgroundcolor', 'color', 'family', 'ha',
                 'linespacing', 'rotation', 'size', 'style',
                 'va', 'weight', 'margin')
        variables = locals()
        for name in names:
            if variables[name] is not None:
                self.properties[name] = variables[name]

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


class element_blank(element_base):
    """
    Theme element: Blank
    """

    def __init__(self):
        self.properties = {'visible': False}


class Margin(dict):
    """
    Margin
    """

    def __init__(self, element, t=0, b=0, l=0, r=0, units='pt'):
        # Make do with some sloppiness
        if units in {'pts', 'points', 'px', 'pixels'}:
            units = 'pt'
        elif units in {'in', 'inch', 'inches'}:
            units = 'in'

        self.element = element
        dict.__init__(self, t=t, b=b, l=l, r=r, units=units)

    def get_as(self, key, units='pt'):
        """
        Return key in given units
        """
        dpi = 72
        size = self.element.properties.get('size', 0)
        value = self[key]

        functions = {
            'pt-lines': lambda x: x/size,
            'pt-in': lambda x: x/dpi,
            'lines-pt': lambda x: x*size,
            'lines-in': lambda x: x*size/dpi,
            'in-pt': lambda x: x*dpi,
            'in-lines': lambda x: x*dpi/size
        }

        if self['units'] != units:
            conversion = '{}-{}'.format(self['units'], units)
            try:
                value = functions[conversion](value)
            except ZeroDivisionError:
                value = 0

        return value
