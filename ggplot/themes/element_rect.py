class element_rect(object):
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
