from .scale import scale
from copy import deepcopy
import brewer2mpl


def _number_to_palette(ctype, n):
    n -= 1
    palettes = sorted(brewer2mpl.COLOR_MAPS[ctype].keys())
    if n < len(palettes):
        return palettes[n]

def _handle_shorthand(text):
    abbrevs = {
        "seq": "Sequential",
        "qual": "Qualitative",
        "div": "Diverging"
    }
    text = abbrevs.get(text, text)
    text = text.title()
    return text


class scale_colour_brewer(scale):
    """
    Parameters
    ----------
    type: string
        One of seq (sequential), div (diverging) or qual (qualitative)
    palette: string
        If a string, will use that named palette. If a number, will index into
        the list of palettes of appropriate type
    
    Examples
    --------
    >>> from ggplot import *
    >>> p = ggplot(aes(x='carat', y='price', colour='clarity'), data=diamonds)
    >>> p += geom_point()
    >>> print(p + scale_color_brewer(palette=4))
    >>> print(p + scale_color_brewer(type='diverging'))
    >>> print(p + scale_color_brewer(type='div'))
    >>> print(p + scale_color_brewer(type='seq'))
    >>> print(p + scale_color_brewer(type='seq', palette='Blues'))
    """
    VALID_SCALES = ['type', 'palette'] 
    
    def __radd__(self, gg):
        gg = deepcopy(gg)

        if self.type:
            ctype = self.type
        else:
            ctype = "Sequential"
        ctype = _handle_shorthand(ctype)

        if self.palette:
            palette = self.palette
        else:
            palette = _number_to_palette(ctype, 1)
        if isinstance(palette, int):
            palette = _number_to_palette(ctype, palette)

        n_colors = gg.data[gg.aesthetics['color']].nunique()
        bmap = brewer2mpl.get_map(palette, ctype, n_colors)
        gg.manual_color_list = bmap.hex_colors

        return gg

