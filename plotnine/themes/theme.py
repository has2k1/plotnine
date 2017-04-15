from copy import copy, deepcopy

from ..options import get_option, set_option
from ..exceptions import PlotnineError
from .themeable import themeable, Themeables


# All complete themes are initiated with these rcparams. They
# can be overridden.
default_rcparams = {
    'axes.axisbelow': 'True',
    'font.sans-serif': ['DejaVu Sans', 'Helvetica', 'Avant Garde',
                        'Computer Modern Sans serif', 'Arial'],
    'font.serif': ['Times', 'Palatino',
                   'New Century Schoolbook', 'Bookman',
                   'Computer Modern Roman', 'Times New Roman'],
    'lines.antialiased': 'True',
    'patch.antialiased': 'True',
    'timezone': 'UTC',
    # Choosen to match MPL 2.0 defaults
    'savefig.dpi': 'figure',
    'figure.subplot.left': 0.125,
    'figure.subplot.right': 0.9,
    'figure.subplot.top': 0.88,
    'figure.subplot.bottom': 0.11,
}


class theme(object):
    """
    This is a base class for themes.

    In general, only complete themes should subclass this class.

    Parameters
    -----------
    complete : bool
        Themes that are complete will override any existing themes.
        themes that are not complete (ie. partial) will add to or
        override specific elements of the current theme. e.g::

            theme_gray() + theme_xkcd()

        will be completely determined by :class:`theme_xkcd`, but::

            theme_gray() + theme(axis_text_x=element_text(angle=45))

        will only modify the x-axis text.

    kwargs: dict
        kwargs are themeables. The themeables are elements that
        are subclasses of `themeable`. Many themeables are defined
        using theme elements i.e

            - :class:`element_line`
            - :class:`element_rect`
            - :class:`element_text`

        These simply bind together all the aspects of a themeable
        that can be themed. See
        :class:`~plotnine.themes.themeable.themeable`.

    Note
    ----
    When subclassing, make sure to call :python:`theme.__init__`.
    After which you can customise :python:`self._rcParams` within
    the ``__init__`` method of the new theme. The ``rcParams``
    should not be modified after that.
    """

    def __init__(self, complete=False, **kwargs):
        self.themeables = Themeables()
        self.complete = complete

        if complete:
            self._rcParams = deepcopy(default_rcparams)
        else:
            self._rcParams = {}

        # This is set when the figure is created,
        # it is useful at legend drawing time and
        # when applying the theme.
        self.figure = None

        new = themeable.from_class_name
        for name, element in kwargs.items():
            self.themeables[name] = new(name, element)

    def __eq__(self, other):
        """
        Test if themes are equal

        Mostly for testing purposes
        """
        # criteria for equality are
        # - Equal themeables
        # - Equal rcParams
        c1 = self.themeables == other.themeables
        c2 = self.rcParams == other.rcParams
        return c1 and c2

    def apply_axs(self, axs):
        """
        Apply this theme to all the axes

        Parameters
        ----------
        axs : iterable
            Sequence of axes to be themed
        """
        for ax in axs:
            self.apply(ax)

    def apply(self, ax):
        """
        Apply this theme, then apply additional modifications in order.

        Subclasses that override this method should make sure that
        the base class method is called.
        """
        for th in self.themeables.values():
            th.apply(ax)

    def setup_figure(self, figure):
        """
        Makes any desired changes to the figure object

        This method will be called once with a figure object
        before any plotting has completed. Subclasses that
        override this method should make sure that the base
        class method is called.
        """
        for th in self.themeables.values():
            th.setup_figure(figure)

    def apply_figure(self, figure):
        """
        Makes any desired changes to the figure object

        This method will be called once with a figure object
        after plot has completed. Subclasses that override this
        method should make sure that the base class method is
        called.
        """
        for th in self.themeables.values():
            th.apply_figure(figure)

    def apply_rcparams(self):
        """
        Set the rcParams
        """
        from matplotlib import rcParams
        for key, val in self.rcParams.items():
            try:
                rcParams[key] = val
            except Exception as e:
                msg = ("""Setting "mpl.rcParams['{}']={}" """
                       "raised an Exception: {}")
                raise PlotnineError(msg.format(key, val, e))

    @property
    def rcParams(self):
        """
        Return rcParams dict for this theme.

        Notes
        -----
        Subclasses should not need to override this method method as long as
        self._rcParams is constructed properly.

        rcParams are used during plotting. Sometimes the same theme can be
        achieved by setting rcParams before plotting or a apply
        after plotting. The choice of how to implement it is is a matter of
        convenience in that case.

        There are certain things can only be themed after plotting. There
        may not be an rcParam to control the theme or the act of plotting
        may cause an entity to come into existence before it can be themed.

        """

        try:
            rcParams = deepcopy(self._rcParams)
        except NotImplementedError:
            # deepcopy raises an error for objects that are drived from or
            # composed of matplotlib.transform.TransformNode.
            # Not desirable, but probably requires upstream fix.
            # In particular, XKCD uses matplotlib.patheffects.withStrok
            rcParams = copy(self._rcParams)

        for th in self.themeables.values():
            rcParams.update(th.rcParams)
        return rcParams

    def add_theme(self, other, inplace=False):
        """Add themes together.

        Subclasses should not override this method.

        This will be called when adding two instances of class 'theme'
        together.
        A complete theme will annihilate any previous themes. Partial themes
        can be added together and can be added to a complete theme.
        """
        if other.complete:
            return other

        theme_copy = self if inplace else deepcopy(self)
        theme_copy.themeables.update(deepcopy(other.themeables))
        return theme_copy

    def __add__(self, other):
        if not isinstance(other, theme):
            msg = ("Adding theme failed. "
                   "{} is not a theme").format(str(other))
            raise PlotnineError(msg)
        return self.add_theme(other)

    def __radd__(self, other, inplace=False):
        """
        Add theme to ggplot object or to another theme

        This will be called in one of two ways::

             ggplot() + theme()
             theme1() + theme2()

        In both cases, `self` is the :class:`theme`
        on the right hand side.

        Subclasses should not override this method.
        """
        # ggplot() + theme
        if hasattr(other, 'theme'):
            gg = other if inplace else deepcopy(other)
            if self.complete:
                gg.theme = self
            else:
                # If no theme has been added yet,
                # we modify the default theme
                gg.theme = gg.theme or theme_get()
                gg.theme = gg.theme.add_theme(self, inplace=inplace)
            return gg
        # theme1 + theme2
        else:
            if self.complete:
                return self
            else:
                # other combined with self.
                return other.add_theme(self, inplace=inplace)

    def __iadd__(self, other):
        """
        Add theme to theme
        """
        return self.add_theme(other, inplace=True)

    def __deepcopy__(self, memo):
        """
        Deep copy without copying the figure
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        for key, item in old.items():
            if key in {'figure'}:
                new[key] = old[key]
            else:
                new[key] = deepcopy(old[key], memo)

        return result


def theme_get():
    """
    Return the default theme

    The default theme is the one set (using :func:`theme_set`) by
    the user. If none has been set, then :class:`theme_gray` is
    the default.
    """
    from .theme_gray import theme_gray
    _theme = get_option('current_theme')
    if isinstance(_theme, type):
        _theme = _theme()
    return _theme or theme_gray()


def theme_set(new):
    """
    Change the current(default) theme

    Parameters
    ----------
    new : theme
        New default theme

    Returns
    -------
    out : theme
        Previous theme
    """
    if (not isinstance(new, theme) and
            not issubclass(new, theme)):
        raise PlotnineError("Expecting object to be a theme")

    out = get_option('current_theme')
    set_option('current_theme', new)
    return out


def theme_update(**kwargs):
    """
    Modify elements of the current theme

    Parameters
    ----------
    kwargs : dict
        Theme elements
    """
    theme_set(theme_get() + theme(**kwargs))
