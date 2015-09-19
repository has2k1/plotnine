"""
Provide theamables, that is the elements can be themed.

From the ggplot2 documentation the axis.title inherits from text.
What this means is that axis.title and text have the same elements
that may be themed, but the scope of what they apply to is different.
The scope of text covers all text in the plot, axis.title applies
only to the axis.title. In matplotlib terms this means that a theme
that covers text also has to cover axis.title.
"""
from collections import OrderedDict

from six import add_metaclass

from ..utils import RegisteredMeta
from ..utils.exceptions import GgplotError


other_targets = {
    'legend_direction': None,
    'legend_margin': '0.2',
    'legend_key_size': '1.2',
    'legend_key_height': None,
    'legend_key_width': None,
    'legend_text_align': None,
    'legend_title_align': None,
    'legend_box': None,
    'legend_box_just': None,
    'legend_justification': 'center',
    'legend_position': 'right'
}


@add_metaclass(RegisteredMeta)
class themeable(object):
    """
    themeable is an abstract class of things that can be themed.

    Every subclass of themeable is stored in a dict at
    `themeable.register` with the name of the subclass as the key.

    It is the base of a class hierarchy that uses inheritance in a
    non-traditional manner. In the textbook use of class inheritance,
    superclasses are general and subclasses are specializations. In some
    since the hierarchy used here is the opposite in that superclasses
    are more specific than subclasses.

    It is probably better to think if this hierarchy of leveraging
    Python's multiple inheritance to implement composition. For example
    the axis_title themeable is *composed of* the x_axis_title and the
    y_axis_title. We are just using multiple inheritance to specify
    this composition.

    When implementing a new themeable based on the ggplot2 documentation,
    it is important to keep this in mind and reverse the order of the
    "inherits from" in the documentation.

    For example, to implement,

    axis.title.x x axis label (element_text; inherits from axis.title)
    axis.title.y y axis label (element_text; inherits from axis.title)

    You would have this implementation:

    class axis_title_x(themeable):
        ...

    class axis_title_y(themeable):
        ...

    class axis_title(axis_title_x, axis_title_y):
       ...


    If the superclasses fully implement the subclass, the body of the
    subclass should be "pass". Python(__mro__) will do the right thing.

    When a method does require implementation, call super() then add
    the themeable's implementation to the axes.
    """

    def __init__(self, element_theme=None):
        # @todo: fix unittests in test_themeable or leave this as is?
        if element_theme:
            self.properties = element_theme.properties
        else:
            self.properites = {}

    def __eq__(self, other):
        "Mostly for unittesting."
        return ((self.__class__ == other.__class__) and
                (self.properties == other.properties))

    @property
    def rcParams(self):
        """
        Return themeables rcparams to an rcparam dict before plotting.

        Returns
        -------
        dict
            Dictionary of legal matplotlib parameters.

        This method should always call super(...).rcParams and
        update the dictionary that it returns with its own value, and
        return that dictionary.

        This method is called before plotting. It tends to be more
        useful for general themeables. Very specific themeables
        often cannot be be themed until they are created as a
        result of the plotting process.
        """
        return {}

    def apply(self, ax):
        """
        Called after a chart has been plotted.

        Subclasses should override this method to customize the plot
        according to the theme.

        Parameters
        ----------
        ax : matplotlib.axes.Axes

        This method should be implemented as super(...).apply()
        followed by extracting the portion of the axes specific to this
        themeable then applying the properties.
        """
        pass


def make_themeable(name, theme_element):
    """
    Create an themeable by name.
    """
    try:
        klass = themeable.registry[name]
    except KeyError:
        msg = "No such themeable element {}"
        raise GgplotError(msg.format(name))
    return klass(theme_element)


def merge_themeables(th1, th2):
    """
    Merge two lists of themeables by first sorting them according to
    precedence, then retaining the last instance of a themeable
    in case of ties.
    """
    return unique_themeables(sorted_themeables(th1 + th2))


def unique_themeables(themeables):
    """
    Return a unique list of themeables, keep the last if there is more
    than one of the same type.

    This is not strictly necessary, but is an optimaztion when combining
    themes to prevent carrying around themes that will be completely
    overridden.
    """
    d = OrderedDict()
    for th in themeables:
        d[th.__class__] = th
    return list(d.values())


def sorted_themeables(themeable_list):
    """
    Sort themeables in reverse based on the their depth in the
    inheritance hierarchy.

    This will make sure any general themeable, like text will be
    applied by a specific themeable like axis_text_x.
    """
    def key(themeable_):
        return len(themeable_.__class__.__mro__)

    return sorted(themeable_list, key=key, reverse=True)


class axis_title_x(themeable):
    def apply(self, ax):
        super(axis_title_x, self).apply(ax)
        x_axis_label = ax.get_xaxis().get_label()
        x_axis_label.set(**self.properties)


class axis_title_y(themeable):
    def apply(self, ax):
        super(axis_title_y, self).apply(ax)
        y_axis_label = ax.get_yaxis().get_label()
        y_axis_label.set(**self.properties)


class axis_title(axis_title_x, axis_title_y):
    pass


class legend_title(themeable):
    def apply(self, ax):
        super(legend_title, self).apply(ax)
        legend = ax.get_legend()
        if legend:
            legend.set(**self.properties)


class legend_text(legend_title):
    # @todo: implement me
    pass


class plot_title(themeable):
    def apply(self, ax):
        super(plot_title, self).apply(ax)
        ax.title.set(**self.properties)


class strip_text_x(themeable):
    # @todo implement me
    pass


class strip_text_y(themeable):
    # @todo implement me
    pass


class strip_text(strip_text_x, strip_text_y):
    pass


class title(axis_title, legend_title, plot_title):
    # @todo: also need to inherit from plot_title and legend_title
    pass


class axis_text_x(themeable):

    def apply(self, ax):
        super(axis_text_x, self).apply(ax)
        labels = ax.get_xticklabels()
        for l in labels:
            l.set(**self.properties)


class axis_text_y(themeable):

    def apply(self, ax):
        super(axis_text_y, self).apply(ax)
        labels = ax.get_yticklabels()
        for l in labels:
            l.set(**self.properties)


class axis_text(title, axis_text_x, axis_text_y):
    """
    Set theme the text on x and y axis.
    """
    pass


class text(axis_text, legend_text, strip_text, title):
    """
    Scope of theme that applies to all text in plot
    """

    @property
    def rcParams(self):
        rcParams = super(text, self).rcParams
        family = self.properties.get("family")
        if family:
            rcParams["font.family"] = family
        style = self.properties.get("style")
        if style:
            rcParams["font.style"] = style
        weight = self.properties.get("weight")
        if weight:
            rcParams["font.weight"] = weight
        size = self.properties.get("size")
        if size:
            rcParams["font.size"] = size
            rcParams["xtick.labelsize"] = size
            rcParams["ytick.labelsize"] = size
            rcParams["legend.fontsize"] = size
        color = self.properties.get("color")
        if color:
            rcParams["text.color"] = color

        return rcParams
