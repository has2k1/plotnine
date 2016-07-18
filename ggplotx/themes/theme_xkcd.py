from copy import copy, deepcopy

import matplotlib.pyplot as plt
import matplotlib as mpl

from .elements import element_rect
from .theme import theme


class theme_xkcd(theme):
    """
    xkcd theme

    The theme internally uses the settings from pyplot.xkcd().
    """
    def __init__(self, scale=1, length=100, randomness=2):
        with plt.xkcd(scale=scale,
                      length=length,
                      randomness=randomness):
            _xkcd = mpl.rcParams.copy()

        # no need to a get a deprecate warning for nothing...
        for key in mpl._deprecated_map:
            if key in _xkcd:
                del _xkcd[key]

        if 'tk.pythoninspect' in _xkcd:
            del _xkcd['tk.pythoninspect']

        fill = _xkcd.get('patch.facecolor', 'white')
        if isinstance(fill, tuple):
            d = {'fill': fill+(.1,)}
        else:
            d = {'fill': fill, 'alpha': .1}

        theme.__init__(self,
                       figure_size=(11, 8),
                       legend_key=element_rect(**d),
                       complete=True)

        self._rcParams.update({'axes.grid': True})
        self._rcParams.update(_xkcd)

    def __deepcopy__(self, memo):
        """
        Deep copy support for theme_xkcd
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        for key, item in old.items():
            if key == '_rcParams':
                continue
            new[key] = deepcopy(old[key], memo)

        result._rcParams = {}
        for k, v in self._rcParams.items():
            try:
                result._rcParams[k] = deepcopy(v, memo)
            except NotImplementedError:
                # deepcopy raises an error for objects that are
                # drived from or composed of
                # matplotlib.transform. TransformNode.
                # Not desirable, but probably requires upstream fix.
                # In particular, XKCD uses
                # matplotlib.patheffects.withStrok
                # -gdowding
                result._rcParams[k] = copy(v)

        return result
