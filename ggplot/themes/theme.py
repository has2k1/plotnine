"""
Theme elements:

* element_line
* element_rect
* element_text
* element_title

These elemenets define what operations can be performed. The specific targets,
eg. line, rect, text, title and their derivities axist_title or axis_title_x
specify the scope of the theme application.

"""
from copy import deepcopy


class theme(object):

    def __init__(self, complete=False, *args, **kwargs):
        """
        Provide ggplot2 themeing capabilities.

        Parameters
        -----------
        complete : Themes that are complete will override any existing themes.
            themes that are not complete (ie. partial) will add to or
            override specific elements of the current theme.

            eg. theme_matplotlib() + theme_xkcd() will be completely
            determined by theme_xkcd, but
            theme_matplotlib() + theme(axis_text_x=elemet_text(angle=45)) will
            only modify the x axis text.

        Theme Elements
        ---------------
        Taken from http://docs.ggplot2.org/current/theme.html

        Python does not allow using '.' in argument names, so we are using '_'
        instead.

        line - all line elements (element_line)
        rect - all rectangular elements (element_rect)
        text - all text elements (element_test)
        title - all title element: plo, axes, legends (element_text; inherits
            from text)

        """
        self.partial_themes = []
        self.elements = []
        self.complete = complete

        legal_elements = ["line", "rect", "text", "title",
                          "axis_text", "axis_title",
                          "axis_text_x", "axis_text_y"]

        for theme_element in legal_elements:
            element = kwargs.get(theme_element)
            if element:
                element.element = theme_element
                self.elements.append(element)

        for k, v in kwargs.items():
            setattr(self, k, v)

        self._rcParams = {}

    def apply_rcparams(self, rcParams):
        "Subclasses may override this method."
        rcParams.update(self._rcParams)
        for partial_theme in self.partial_themes:
            partial_theme.apply_rcparams(rcParams)
        for element in self.elements:
            element.apply_rcparams(rcParams)

    def post_plot_callback(self, ax):
        """Apply this theme, then apply additional modifications in order.

        This method should not be overridden. Override the method that it
        calls.

        """
        self.apply_theme(ax)
        for i in self.partial_themes:
            i.apply_theme(ax)

    def apply_theme(self, ax):
        """Subclasses should override this method.

        It will be called after the plot has been created."""
        for element in self.elements:
            element(ax)

    def __add__(self, other):
        """Add themes together.

        Subclasses should not override this method.

        This will be called when adding two instances of class 'theme'
        together.
        A complete theme will anhilate any previous themes. Partial themes
        can be added together and can be added to a complete theme.
        """
        if other.complete:
            return other
        else:
            theme_copy = deepcopy(self)
            theme_copy.partial_themes.append(other)
            return theme_copy

    def __radd__(self, other):
        "Subclasses should not override this method."
        # @todo: investigate moving this to ggplot
        # probably won't work becasuse all different types get added to themes

        # other + self is ggplot + theme
        if not isinstance(other, theme):
            gg_copy = deepcopy(other)
            if self.complete:
                gg_copy.theme = self
            else:
                gg_copy.theme = other.theme + self
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
                theme_copy.partial_themes.append(self)
                return theme_copy
