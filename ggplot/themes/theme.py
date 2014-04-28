"""
Theme elements:

* element_line
* element_rect
* element_text
* element_title

These elements define what operations can be performed. The specific targets,
eg. line, rect, text, title and their derivatives axis_title or axis_title_x
specify the scope of the theme application.

"""
from copy import deepcopy

from .element_target import element_target_factory, merge_element_targets


class theme(object):

    """This is an abstract base class for themes.

    In general, only complete themes should should subclass this class.


    Notes
    ----- 
    When subclassing there are really only two methods that need to be
    implemented.

    __init__: This should call super().__init__ which will define
    self._rcParams. Subclasses should customize self._rcParams after calling
    super().__init__. That will ensure that the rcParams are applied at
    the appropriate time.

    The other method is apply_theme(ax). This method takes an axes object that
    has been created during the plot process. The theme should modify the
    axes according.

    """

    def __init__(self, complete=False, **kwargs):
        """
        Provide ggplot2 themeing capabilities.

        Parameters
        -----------
        complete : bool
            Themes that are complete will override any existing themes.
            themes that are not complete (ie. partial) will add to or
            override specific elements of the current theme.

            eg. theme_matplotlib() + theme_xkcd() will be completely
            determined by theme_xkcd, but
            theme_matplotlib() + theme(axis_text_x=element_text(angle=45)) will
            only modify the x axis text.

        kwargs**: theme_element
            kwargs are theme_elements based on http://docs.ggplot2.org/current/theme.html.
            Currently only a subset of the elements are implemented. In addition,
            Python does not allow using '.' in argument names, so we are using '_'
            instead.

            For example, ggplot2 axis.ticks.y will be  axis_ticks_y in Python ggplot.

        """
        self.element_themes = []
        self.complete = complete
        self._rcParams = {}

        for target_name, theme_element in kwargs.items():
            self.element_themes.append(element_target_factory(target_name,
                                                              theme_element))

    def apply_theme(self, ax):
        """apply_theme will be called with an axes object after plot has completed.

        Complete themes should implement this method if post plot themeing is
        required.

        """
        pass

    def get_rcParams(self):
        """Get an rcParams dict for this theme.

        Notes
        -----
        Subclasses should not need to override this method method as long as
        self._rcParams is constructed properly.

        rcParams are used during plotting. Sometimes the same theme can be
        achieved by setting rcParams before plotting or a post_plot_callback
        after plotting. The choice of how to implement it is is a matter of
        convenience in that case.

        There are certain things can only be themed after plotting. There
        may not be an rcParam to control the theme or the act of plotting
        may cause an entity to come into existence before it can be themed.

        """
        rcParams = deepcopy(self._rcParams)
        if self.element_themes:
            for element_theme in self.element_themes:
                rcparams = element_theme.get_rcParams()
            rcParams.update(rcparams)
        return rcParams

    def post_plot_callback(self, ax):
        """Apply this theme, then apply additional modifications in order.

        This method should not be overridden. Subclasses should override
        the apply_theme subclass. This implementation will ensure that the
        a theme that includes partial themes will be themed properly.

        """
        self.apply_theme(ax)
        # does this need to be ordered first?
        for element_theme in self.element_themes:
            element_theme.post_plot_callback(ax)

    def add_theme(self, other):
        """Add themes together.

        Subclasses should not override this method.

        This will be called when adding two instances of class 'theme'
        together.
        A complete theme will annihilate any previous themes. Partial themes
        can be added together and can be added to a complete theme.
        """
        if other.complete:
            return other
        else:
            theme_copy = deepcopy(self)
            theme_copy.element_themes = merge_element_targets(
                deepcopy(self.element_themes),
                deepcopy(other.element_themes))
            return theme_copy

    def __add__(self, other):
        if isinstance(other, theme):
            return self.add_theme(other)
        else:
            raise TypeError()

    def __radd__(self, other):
        """Subclasses should not override this method.

        This will be called in one of two ways:
        gg + theme which is translated to self=theme, other=gg
        or
        theme1 + theme2 which is translated into self=theme2, other=theme1

        """
        if not isinstance(other, theme):
            gg_copy = deepcopy(other)
            if self.complete:
                gg_copy.theme = self
            else:
                gg_copy.theme = other.theme.add_theme(self)
            return gg_copy
        # other _ self is theme + self
        else:
            # adding theme and theme here
            # other + self
            # if self is complete return self
            if self.complete:
                return self
            # else make a copy of other combined with self.
            else:
                theme_copy = deepcopy(other)
                theme_copy.element_themes.append(self)
                return theme_copy
