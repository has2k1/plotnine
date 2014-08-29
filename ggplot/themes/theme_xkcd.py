from copy import copy, deepcopy

from .theme import theme
import matplotlib.pyplot as plt
import matplotlib as mpl


class theme_xkcd(theme):
    """
    xkcd theme

    The theme internaly uses the settings from pyplot.xkcd().

    @todo: testme.

    """
    def __init__(self, scale=1, length=100, randomness=2):
        super(theme_xkcd, self).__init__(complete=True)
        with plt.xkcd(scale=scale, length=length, randomness=randomness):
            _xkcd = mpl.rcParams.copy()
        # no need to a get a deprecate warning for nothing...
        for key in mpl._deprecated_map:
            if key in _xkcd:
                del _xkcd[key]
        if 'tk.pythoninspect' in _xkcd:
                del _xkcd['tk.pythoninspect']
        self._rcParams.update(_xkcd)

    def __deepcopy__(self, memo):
        class _empty(object):
            pass
        result = _empty()
        result.__class__ = self.__class__
        result.__dict__['element_themes'] = deepcopy(self.element_themes)
        result.__dict__["_rcParams"] = {}
        for k, v in self._rcParams.items():
            try:
                result.__dict__["_rcParams"][k] = deepcopy(v, memo)
            except NotImplementedError:
                # deepcopy raises an error for objects that are drived from or
                # composed of matplotlib.transform.TransformNode.
                # Not desirable, but probably requires upstream fix.
                # In particular, XKCD uses matplotlib.patheffects.withStrok
                # -gdowding
                result.__dict__["_rcParams"][k] = copy(v)

        return result

    def apply_theme(self, ax, params):
        """"
        Styles x,y axes to appear like ggplot2
        Must be called after all plot and axis manipulation operations have
        been carried out (needs to know final tick spacing)

        From:
        https://github.com/wrobstory/climatic/blob/master/climatic/stylers.py
        """
        # Restyle the tick lines
        for line in ax.get_xticklines() + ax.get_yticklines():
            line.set_markersize(5)
            line.set_markeredgewidth(1.4)

        # set parameters
        for att, val in params['xaxis']:
            getattr(ax.xaxis, att)(val)

        for att, val in params['yaxis']:
            getattr(ax.yaxis, att)(val)
