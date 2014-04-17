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

from .element_target import element_target_factory, merge_element_targets


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
        text - all text elements (element_text)
        title - all title elements (element_text)

        """
        self.element_themes = []
        self.complete = complete

        # legal_elements = ["line", "rect", "text", "title",
        #                   "axis_text", "axis_title",
        #                   "axis_text_x", "axis_text_y"]

        # for element_name in legal_elements:
        #     element_theme = kwargs.get(element_name)
        #     if element_theme:
        #         element_target = element_target_factory(element_name,
        #                                                 element_theme)
        #         if element_target:
        #             element_theme.target = element_target
        #             print("added %s to %s" % (element_name, element_theme))
        #         else:
        #             print("invalid element target %s" % element_name)
        #         self.element_themes.append(element_target)

        for target_name, theme_element in kwargs.items():
            self.element_themes.append(element_target_factory(target_name, theme_element))

        # for k, v in kwargs.items():
        #     setattr(self, k, v)

        self._rcParams = {}

    def apply_rcparams(self, rcParams):
        """Subclasses may override this method.

        @todo: change to get_rcparams

        """
        rcParams.update(self._rcParams)
        if self.element_themes:
            for element_theme in self.element_themes:
                rcparams = element_theme.get_rcparams()
            rcParams.update(rcparams)
        return rcParams

    def post_plot_callback(self, ax):
        """Apply this theme, then apply additional modifications in order.

        This method should not be overridden. Subclasses should override
        the apply_theme subclass. See theme_gray for an example.
        calls.

        """
        self.apply_theme(ax)
        # does this need to be ordered first?
        for element_theme in self.element_themes:
            element_theme.post_plot_callback(ax)

    def apply_theme(self, ax):
        """Subclasses ie. complete themes should override this method.

        It will be called after the plot has been created."""
        pass

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
            theme_copy.element_themes = merge_element_targets(
                deepcopy(self.element_themes),
                deepcopy(other.element_themes))
            return theme_copy

    def __radd__(self, other):
        "Subclasses should not override this method."

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
                theme_copy.element_themes.append(self)
                return theme_copy
