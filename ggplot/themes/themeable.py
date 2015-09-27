"""
Provide theamables, that is the elements can be themed.

From the ggplot2 documentation the axis.title inherits from text.
What this means is that axis.title and text have the same elements
that may be themed, but the scope of what they apply to is different.
The scope of text covers all text in the plot, axis.title applies
only to the axis.title. In matplotlib terms this means that a theme
that covers text also has to cover axis.title.
"""
from __future__ import absolute_import
from copy import deepcopy
from collections import OrderedDict

import six
from six import add_metaclass

from ..utils import RegisteredMeta
from ..utils.exceptions import GgplotError
from .theme_elements import element_line, element_rect, element_text


# These do not have rcParams to modify
scalar_themeables = {
    'legend_box': None,
    'legend_box_just': None,
    'legend_direction': None,
    'legend_justification': 'center',
    'legend_key_height': None,
    'legend_key_size': '1.2',
    'legend_key_width': None,
    'legend_margin': '0.2',
    'legend_position': 'right',
    'legend_text_align': None,
    'legend_title_align': None,
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

    def __init__(self, theme_element=None):
        # @todo: fix unittests in test_themeable or leave this as is?
        element_types = (element_text, element_line, element_rect)
        scalar_types = (int, float, bool, six.string_types)
        if isinstance(theme_element, element_types):
            self.properties = theme_element.properties
        elif isinstance(theme_element, scalar_types):
            # The specific themeable takes this value and
            # does stuff with rcParams or sets something
            # on some object attached to the axes/figure
            self.properties = {'value': theme_element}
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


# element_text themeables

class axis_title_x(themeable):
    def apply(self, ax):
        super(axis_title_x, self).apply(ax)
        text = ax.figure._themeable['axis_title_x']
        text.set(**self.properties)


class axis_title_y(themeable):
    def apply(self, ax):
        super(axis_title_y, self).apply(ax)
        text = ax.figure._themeable['axis_title_y']
        text.set(**self.properties)


class axis_title(axis_title_x, axis_title_y):
    pass


class legend_title(themeable):
    def apply(self, ax):
        super(legend_title, self).apply(ax)
        textarea = ax.figure._themeable['legend_title']
        textarea._text.set(**self.properties)


class legend_text(legend_title):
    def apply(self, ax):
        super(legend_title, self).apply(ax)
        texts = ax.figure._themeable['legend_text']
        for text in texts:
            text.set(**self.properties)


class plot_title(themeable):
    def apply(self, ax):
        super(plot_title, self).apply(ax)
        text = ax.figure._themeable['plot_title']
        text.set(**self.properties)


class strip_text_x(themeable):
    def apply(self, ax):
        super(strip_text_x, self).apply(ax)
        texts = ax.figure._themeable['strip_text_x']
        for text in texts:
            text.set(**self.properties)


class strip_text_y(themeable):
    def apply(self, ax):
        super(strip_text_y, self).apply(ax)
        texts = ax.figure._themeable['strip_text_y']
        for text in texts:
            text.set(**self.properties)


class strip_text(strip_text_x, strip_text_y):
    pass


class title(axis_title, legend_title, plot_title):
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


class axis_text(axis_text_x, axis_text_y):
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
        family = self.properties.get('family')
        style = self.properties.get('style')
        weight = self.properties.get('weight')
        size = self.properties.get('size')
        color = self.properties.get('color')

        if family:
            rcParams['font.family'] = family
        if style:
            rcParams['font.style'] = style
        if weight:
            rcParams['font.weight'] = weight
        if size:
            rcParams['font.size'] = size
            rcParams['xtick.labelsize'] = size
            rcParams['ytick.labelsize'] = size
            rcParams['legend.fontsize'] = size
        if color:
            rcParams['text.color'] = color

        return rcParams


# element_line themeables

class axis_line_x(themeable):
    def apply(self, ax):
        super(axis_line_x, self).apply(ax)
        ax.spines['top'].set(**self.properties)
        ax.spines['bottom'].set(**self.properties)


class axis_line_y(themeable):
    def apply(self, ax):
        super(axis_line_y, self).apply(ax)
        ax.spines['left'].set(**self.properties)
        ax.spines['right'].set(**self.properties)


class axis_line(axis_line_x, axis_line_y):
    pass


class axis_ticks_x(themeable):
    def apply(self, ax):
        super(axis_ticks_x, self).apply(ax)
        d = deepcopy(self.properties)
        d['markeredgewidth'] = d.pop('linewidth')
        for line in ax.get_xticklines():
            line.set(**d)


class axis_ticks_y(themeable):
    def apply(self, ax):
        super(axis_ticks_y, self).apply(ax)
        d = deepcopy(self.properties)
        d['markeredgewidth'] = d.pop('linewidth')
        for line in ax.get_yticklines():
            line.set(**d)


class axis_ticks(axis_ticks_x, axis_ticks_y):
    pass


class panel_grid_major_x(themeable):
    def apply(self, ax):
        super(panel_grid_major_x, self).apply(ax)
        ax.xaxis.grid(which='major', **self.properties)


class panel_grid_major_y(themeable):
    def apply(self, ax):
        super(panel_grid_major_y, self).apply(ax)
        ax.yaxis.grid(which='major', **self.properties)


class panel_grid_minor_x(themeable):
    def apply(self, ax):
        super(panel_grid_minor_x, self).apply(ax)
        ax.xaxis.grid(which='minor', **self.properties)


class panel_grid_minor_y(themeable):
    def apply(self, ax):
        super(panel_grid_minor_y, self).apply(ax)
        ax.yaxis.grid(which='minor', **self.properties)


class panel_grid_major(panel_grid_major_x, panel_grid_major_y):
    pass


class panel_grid_minor(panel_grid_minor_x, panel_grid_minor_y):
    pass


class panel_grid(panel_grid_major, panel_grid_minor):
    pass


class line(axis_line, axis_ticks, panel_grid):

    @property
    def rcParams(self):
        rcParams = super(line, self).rcParams
        color = self.properties.get('color')
        linewidth = self.properties.get('linewidth')
        linestyle = self.properties.get('linestyle')
        d = {}

        if color:
            d['axes.edgecolor'] = color
            d['xtick.color'] = color
            d['ytick.color'] = color
            d['grid.color'] = color
        if linewidth:
            d['axes.linewidth'] = linewidth
            d['xtick.major.width'] = linewidth
            d['xtick.minor.width'] = linewidth
            d['ytick.major.width'] = linewidth
            d['ytick.minor.width'] = linewidth
            d['grid.linewidth'] = linewidth
        if linestyle:
            d['grid.linestyle'] = linestyle

        rcParams.update(d)
        return rcParams


class legend_key(themeable):
    def apply(self, ax):
        super(legend_key, self).apply(ax)
        das = ax.figure._themeable['legend_key']
        for da in das:
            da.patch.set(**self.properties)


class legend_background(themeable):
    def apply(self, ax):
        super(legend_background, self).apply(ax)
        aob = ax.figure._themeable['legend_background']
        aob.patch.set(**self.properties)
        if self.properties:
            aob._drawFrame = True
            # some small sensible padding
            if not aob.pad:
                aob.pad = .2


class panel_background(themeable):
    def apply(self, ax):
        super(panel_background, self).apply(ax)
        ax.patch.set(**self.properties)


# Yeah, this is the same as panel_background
class panel_border(themeable):
    def apply(self, ax):
        super(panel_border, self).apply(ax)
        ax.patch.set(**self.properties)


class plot_background(themeable):
    def apply(self, ax):
        super(plot_background, self).apply(ax)
        ax.figure.patch.set(**self.properties)


class strip_background(themeable):
    def apply(self, ax):
        super(strip_background, self).apply(ax)
        tx = ax.figure._themeable.get('strip_text_x', [])
        ty = ax.figure._themeable.get('strip_text_y', [])
        for text in tx + ty:
            text._bbox.update(**self.properties)


class rect(legend_key, legend_background,
           panel_background, panel_border,
           plot_background, strip_background):
    pass


class axis_ticks_length(themeable):
    @property
    def rcParams(self):
        rcParams = super(axis_ticks_length, self).rcParams
        val = self.properties['value']
        rcParams['xtick.major.size'] = val
        rcParams['ytick.major.size'] = val
        rcParams['xtick.minor.size'] = val
        rcParams['ytick.minor.size'] = val
        return rcParams


class panel_margin_x(themeable):
    def apply(self, ax):
        super(panel_margin_x, self).apply(ax)
        val = self.properties['value']
        ax.figure.subplots_adjust(wspace=val)


class panel_margin_y(themeable):
    def apply(self, ax):
        super(panel_margin_y, self).apply(ax)
        val = self.properties['value']
        ax.figure.subplots_adjust(hspace=val)


class panel_margin(panel_margin_x, panel_margin_y):
    pass


class plot_margin(themeable):
    def apply(self, ax):
        super(plot_margin, self).apply(ax)
        val = self.properties['value']
        ax.figure.subplots_adjust(left=val,
                                  right=1-val,
                                  bottom=val,
                                  top=1-val)


class panel_ontop(themeable):
    def apply(self, ax):
        super(panel_ontop, self).apply(ax)
        ax.set_axisbelow(self.properties['value'])


class aspect_ratio(themeable):
    def apply(self, ax):
        super(aspect_ratio, self).apply(ax)
        ax.set_aspect(self.properties['value'])
