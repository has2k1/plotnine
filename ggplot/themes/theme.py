from copy import copy, deepcopy

from ..utils.exceptions import GgplotError
from ..utils import gg_options
from .themeable import themeable, Themeables


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

    **kwargs: dict
        kwargs are either parameters or themeables.
        The parameters are the keys to `theme.params`.
        The themeables are elements that are subclasses of
        `themeable`. Many themeables are defined using theme
        elements i.e

            - :class:`element_line`
            - :class:`element_rect`
            - :class:`element_text`

        These simply bind together all the aspects of a themeable
        that can be themed. See :class:`~ggplot.themes.themeable`.

    Note
    ----
    When subclassing, make sure to call :python:`theme.__init__`.
    After which you can customise :python:`self._rcParams` within
    the ``__init__`` method of the new theme. The ``rcParams``
    should not be modified after that.
    """

    params = {
        'legend_box': None,
        'legend_box_just': None,
        'legend_direction': None,
        'legend_justification': 'center',
        'legend_key_height': None,
        'legend_key_size': 1.2,
        'legend_key_width': None,
        'legend_margin': 0.2,
        'legend_position': 'right',
        'legend_text_align': None,
        'legend_title_align': None,
        # 'axis_line_x_position': 'bottom',
        # 'axis_line_y_position': 'left',
    }

    def __init__(self, complete=False, **kwargs):
        self.themeables = Themeables()
        self.complete = complete
        self._rcParams = {}
        # FIXME: The params are still not properly integrated
        self.params = self.params.copy()
        # This is set when the figure is created,
        # it is useful at legend drawing time and
        # when applying the theme.
        self.figure = None

        new = themeable.from_class_name
        for name, element in kwargs.items():
            if name in self.params:
                self.params[name] = element
            else:
                self.themeables[name] = new(name, element)

    def __eq__(self, other):
        """
        Test if themes are equal

        Mostly for testing purposes
        """
        # criteria for equality are
        # - Equal themeables
        # - Equal rcParams
        # - Equal params (not yet fully implemented)
        c1 = self.themeables == other.themeables
        c2 = self.rcParams == other.rcParams
        c3 = self.params == other.params
        return c1 and c2 and c3

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
        theme_copy.params.update(other.params)
        return theme_copy

    def __add__(self, other):
        if not isinstance(other, theme):
            msg = ("Adding theme failed. "
                   "{} is not a theme").format(str(other))
            raise GgplotError(msg)
        return self.add_theme(other)

    def __radd__(self, other):
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
        if not isinstance(other, theme):
            gg = deepcopy(other)
            if self.complete:
                gg.theme = self
            else:
                # If no theme has been added yet,
                # we modify the default theme
                gg.theme = gg.theme or theme_get()
                gg.theme = gg.theme.add_theme(self)
            return gg
        # theme1 + theme2
        else:
            if self.complete:
                return self
            else:
                # other combined with self.
                return other.add_theme(self)


def theme_get():
    """
    Return the default theme

    The default theme is the one set (using :func:`theme_set`) by
    the user. If none has been set, then :class:`theme_gray` is
    the default.
    """
    from .theme_gray import theme_gray
    return gg_options['current_theme'] or theme_gray()


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
    if not issubclass(new.__class__, theme):
        raise GgplotError("Expecting object to be a theme")

    out = gg_options['current_theme']
    gg_options['current_theme'] = new
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
