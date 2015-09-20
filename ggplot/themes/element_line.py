class element_line(object):

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
