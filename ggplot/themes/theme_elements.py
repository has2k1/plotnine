"""
Theme elements used to decorate the graph. These conform
to the ggplot2 API.
"""


class element_line(object):
    """
    Theme element: Line
    """

    def __init__(self, colour=None, size=None, linetype=None,
                 lineend=None, color=None):
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

        self.properties = d


class element_rect(object):
    """
    Theme element: Rectangle

    Used for backgrounds and borders
    """

    def __init__(self, fill=None, colour=None, size=None,
                 linetype=None, color=None):

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

        self.properties = d


class element_text(object):
    """
    Theme element: Text
    """

    def __init__(self, family='', face='', colour='', size='',
                 hjust=None, vjust=None, angle=0, lineheight=0,
                 color='', backgroundcolor=''):
        """
        Note
        ----
        vjust and hjust are not fully implemented, 0 or 1 is
        translated to left, bottom; right, top. Any other value is
        translated to center.
        """
        self.properties = {}
        if family:
            self.properties['family'] = family
        if face:
            if face == 'plain':
                self.properties['style'] = 'normal'
            elif face == 'italic':
                self.properties['style'] = 'italic'
            elif face == 'bold':
                self.properties['weight'] = 'bold'
            elif face == 'bold.italic':
                self.properties['style'] = 'italic'
                self.properties['weight'] = 'bold'
        if colour or color:
            if colour:
                self.properties['color'] = colour
            else:
                self.properties['color'] = color
        if size:
            self.properties['size'] = size
        if hjust is not None:
            self.properties['ha'] = self._translate_hjust(hjust)
        if vjust is not None:
            self.properties['va'] = self._translate_vjust(vjust)
        if angle:
            self.properties['rotation'] = angle
        if lineheight is not None:
            # I'm not sure if this is the right translation. Couldn't find an
            # example and this property doesn't seem to have any effect.
            # -gdowding
            self.properties['linespacing'] = lineheight
        if backgroundcolor:
            self.properties['backgroundcolor'] = backgroundcolor

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
