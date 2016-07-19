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

from six import add_metaclass

from ..utils import Registry, suppress
from ..utils.exceptions import GgplotError
from .elements import (element_line, element_rect,
                       element_text, element_blank)


@add_metaclass(Registry)
class themeable(object):
    """
    themeable is an abstract class of things that can be themed.

    Every subclass of themeable is stored in a dict at
    :python:`themeable.register` with the name of the subclass as
    the key.

    It is the base of a class hierarchy that uses inheritance in a
    non-traditional manner. In the textbook use of class inheritance,
    superclasses are general and subclasses are specializations. In some
    since the hierarchy used here is the opposite in that superclasses
    are more specific than subclasses.

    It is probably better to think if this hierarchy of leveraging
    Python's multiple inheritance to implement composition. For example
    the ``axis_title`` themeable is *composed of* the ``x_axis_title`` and the
    ``y_axis_title``. We are just using multiple inheritance to specify
    this composition.

    When implementing a new themeable based on the ggplot2 documentation,
    it is important to keep this in mind and reverse the order of the
    "inherits from" in the documentation.

    For example, to implement,

    ``axis_title_x`` `x`` axis label (element_text;
    inherits from ``axis_title``)

    ``axis_title_y`` ``y`` axis label (element_text;
    inherits from ``axis_title``)

    You would have this implementation:

    ::

        class axis_title_x(themeable):
            ...

        class axis_title_y(themeable):
            ...

        class axis_title(axis_title_x, axis_title_y):
           ...


    If the superclasses fully implement the subclass, the body of the
    subclass should be "pass". Python(__mro__) will do the right thing.

    When a method does require implementation, call :python:`super()`
    then add the themeable's implementation to the axes.
    """
    order = 0

    def __init__(self, theme_element=None):
        self.theme_element = theme_element
        element_types = (element_text, element_line,
                         element_rect, element_blank)
        if isinstance(theme_element, element_types):
            self.properties = theme_element.properties
        else:
            # The specific themeable takes this value and
            # does stuff with rcParams or sets something
            # on some object attached to the axes/figure
            self.properties = {'value': theme_element}

        if isinstance(theme_element, element_blank):
            self.apply = self.blank
            self.apply_figure = self.blank_figure

    @staticmethod
    def from_class_name(name, theme_element):
        """
        Create an themeable by name

        Parameters
        ----------
        name : str
            Class name
        theme_element : element object
            One of :class:`element_line`, :class:`element_rect`,
            :class:`element_text` or :class:`element_blank`

        Returns
        -------
        out : Themeable
        """
        # FIXME: There is no need of a the global registry,
        # a local one would do. i.e. change the metaclass
        # ideas - GlobalRegistry, ClassRegistry, Registry
        # GgplotRegistry
        msg = "No such themeable element {}".format(name)
        try:
            klass = Registry[name]
        except KeyError:
            raise GgplotError(msg)

        if not issubclass(klass, themeable):
            raise GgplotError(msg)

        return klass(theme_element)

    def is_blank(self):
        """
        Return True if theme_element is made of element_blank
        """
        return isinstance(self.theme_element, element_blank)

    def merge(self, other):
        """
        Merge properties of other into self

        Raises ValueError if any them are a blank
        """
        if self.is_blank() or other.is_blank():
            raise ValueError('Cannot merge if there is a blank.')
        else:
            self.properties.update(other.properties)

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

    def apply_figure(self, figure):
        """
        Apply theme to the figure

        Compared to :meth:`setup_figure`, this method is called
        after plotting and all the elements are drawn onto the
        figure.
        """
        pass

    def setup_figure(self, figure):
        """
        Apply theme to the figure

        Compared to :meth:`apply_figure`, this method is called
        before any plotting is done. This is necessary in some
        cases where the drawing functions need(or can make use of)
        this information.
        """
        pass

    def blank(self, ax):
        """
        Blank out theme elements
        """
        pass

    def blank_figure(self, figure):
        """
        Blank out elements on the figure
        """
        pass


class Themeables(dict):
    """
    Collection of themeables

    The `key` to the value is the name of
    the class.
    """

    def update(self, other):
        """
        Update themeables with those from `other`

        This method takes care of inserting the `themeable`
        into the underlying dictionary. Before doing the
        insertion, any existing themeables that will be
        affected by a new from `other` will either be merged
        or removed. This makes sure that a general themeable
        of type :class:`text` can be added to override an
        existing specific one of type :class:`axis_text_x`.
        """
        for new in other.values():
            new_key = new.__class__.__name__

            # 1st in the mro is self, the
            # last 2 are (themeable, object)
            for child in new.__class__.mro()[1:-2]:
                child_key = child.__name__
                try:
                    self[child_key].merge(new)
                except KeyError:
                    pass
                except ValueError:
                    # Blank child is will be overridden
                    del self[child_key]
            try:
                self[new_key].merge(new)
            except (KeyError, ValueError):
                # Themeable type is new or
                # could not merge blank element.
                self[new_key] = new

    def values(self):
        """
        Return a list themeables sorted in reverse based
        on the their depth in the inheritance hierarchy.

        The sorting is key applying and merging the themeables
        so that they do not clash i.e :class:`axis_line`
        applied before :class:`axis_line_x`.
        """
        def key(th):
            return len(th.__class__.__mro__)

        return sorted(dict.values(self), key=key, reverse=True)


def _blankout_rect(rect):
    """
    Make rect invisible
    """
    # set_visible(False) does not clear the attributes
    rect.set_edgecolor('None')
    rect.set_facecolor('None')
    rect.set_linewidth(0)
    rect.set_fill(False)


# element_text themeables

class axis_title_x(themeable):
    """
    x axis label

    Parameters
    ----------
    theme_element : element_text
    """
    def apply_figure(self, figure):
        super(axis_title_x, self).apply_figure(figure)
        with suppress(KeyError):
            text = figure._themeable['axis_title_x']
            text.set(**self.properties)

    def blank_figure(self, figure):
        super(axis_title_x, self).blank_figure(figure)
        with suppress(KeyError):
            text = figure._themeable['axis_title_x']
            text.set_visible(False)


class axis_title_y(themeable):
    """
    y axis label

    Parameters
    ----------
    theme_element : element_text
    """
    def apply_figure(self, figure):
        super(axis_title_y, self).apply_figure(figure)
        with suppress(KeyError):
            text = figure._themeable['axis_title_y']
            text.set(**self.properties)

    def blank_figure(self, figure):
        super(axis_title_y, self).blank_figure(figure)
        with suppress(KeyError):
            text = figure._themeable['axis_title_y']
            text.set_visible(False)


class axis_title(axis_title_x, axis_title_y):
    """
    Axis labels

    Parameters
    ----------
    theme_element : element_text
    """
    pass


class legend_title(themeable):
    """
    Legend title

    Parameters
    ----------
    theme_element : element_text
    """
    def apply_figure(self, figure):
        super(legend_title, self).apply_figure(figure)
        with suppress(KeyError):
            textareas = figure._themeable['legend_title']
            for ta in textareas:
                ta._text.set(**self.properties)

    def blank_figure(self, figure):
        super(legend_title, self).blank_figure(figure)
        with suppress(KeyError):
            textareas = figure._themeable['legend_title']
            for ta in textareas:
                ta.set_visible(False)


class legend_text_legend(themeable):
    """
    Legend text for the common legend

    Parameters
    ----------
    theme_element : element_text

    Note
    ----
    This themeable exists mainly to cater for differences
    in how the text is aligned, compared to the colorbar.
    Unless you experience those alignment issues (i.e when
    using parameters **va** or **ha**), you should use
    :class:`legend_text`.
    """
    def apply_figure(self, figure):
        super(legend_text_legend, self).apply_figure(figure)
        with suppress(KeyError):
            texts = figure._themeable['legend_text_legend']
            for text in texts:
                if not hasattr(text, '_x'):  # textarea
                    text = text._text
                text.set(**self.properties)

    def blank_figure(self, figure):
        super(legend_text_legend, self).blank_figure(figure)
        with suppress(KeyError):
            texts = figure._themeable['legend_text_legend']
            for text in texts:
                text.set_visible(False)


class legend_text_colorbar(themeable):
    """
    Colorbar text

    Parameters
    ----------
    theme_element : element_text

    Note
    ----
    This themeable exists mainly to cater for differences
    in how the text is aligned, compared to the entry based
    legend. Unless you experience those alignment issues
    (i.e when using parameters **va** or **ha**), you should
    use :class:`legend_text`.
    """
    def apply_figure(self, figure):
        super(legend_text_colorbar, self).apply_figure(figure)
        with suppress(KeyError):
            texts = figure._themeable['legend_colorbar_text']
            for text in texts:
                if not hasattr(text, '_x'):  # textarea
                    text = text._text
                text.set(**self.properties)

    def blank_figure(self, figure):
        super(legend_text_colorbar, self).blank_figure(figure)
        with suppress(KeyError):
            texts = figure._themeable['legend_colorbar_text']
            for text in texts:
                text.set_visible(False)


legend_text_colourbar = legend_text_colorbar


class legend_text(legend_text_legend, legend_text_colorbar):
    """
    Legend text

    Parameters
    ----------
    theme_element : element_text
    """


class plot_title(themeable):
    """
    Plot title

    Parameters
    ----------
    theme_element : element_text
    """
    def apply_figure(self, figure):
        super(plot_title, self).apply_figure(figure)
        with suppress(KeyError):
            text = figure._themeable['plot_title']
            text.set(**self.properties)

    def blank_figure(self, figure):
        super(plot_title, self).blank_figure(figure)
        with suppress(KeyError):
            text = figure._themeable['plot_title']
            text.set_visible(False)


class strip_text_x(themeable):
    """
    Facet labels along the horizontal axis

    Parameters
    ----------
    theme_element : element_text
    """
    def apply_figure(self, figure):
        super(strip_text_x, self).apply_figure(figure)
        with suppress(KeyError):
            texts = figure._themeable['strip_text_x']
            for text in texts:
                text.set(**self.properties)

        with suppress(KeyError):
            rects = figure._themeable['strip_background_x']
            for rect in rects:
                rect.set_visible(True)

    def blank_figure(self, figure):
        super(strip_text_x, self).blank_figure(figure)
        with suppress(KeyError):
            texts = figure._themeable['strip_text_x']
            for text in texts:
                text.set_visible(False)

        with suppress(KeyError):
            rects = figure._themeable['strip_background_x']
            for rect in rects:
                rect.set_visible(False)


class strip_text_y(themeable):
    """
    Facet labels along the vertical axis

    Parameters
    ----------
    theme_element : element_text
    """
    def apply_figure(self, figure):
        super(strip_text_y, self).apply_figure(figure)
        with suppress(KeyError):
            texts = figure._themeable['strip_text_y']
            for text in texts:
                text.set(**self.properties)

        with suppress(KeyError):
            rects = figure._themeable['strip_background_y']
            for rect in rects:
                rect.set_visible(True)

    def blank_figure(self, figure):
        super(strip_text_y, self).blank_figure(figure)
        with suppress(KeyError):
            texts = figure._themeable['strip_text_y']
            for text in texts:
                text.set_visible(False)

        with suppress(KeyError):
            rects = figure._themeable['strip_background_y']
            for rect in rects:
                rect.set_visible(False)


class strip_text(strip_text_x, strip_text_y):
    """
    Facet labels along both axes

    Parameters
    ----------
    theme_element : element_text
    """
    pass


class title(axis_title, legend_title, plot_title):
    """
    All titles on the plot

    Parameters
    ----------
    theme_element : element_text
    """
    pass


class axis_text_x(themeable):
    """
    x-axis tick labels

    Parameters
    ----------
    theme_element : element_text
    """
    def apply(self, ax):
        super(axis_text_x, self).apply(ax)
        labels = ax.get_xticklabels()
        for l in labels:
            l.set(**self.properties)

    def blank(self, ax):
        super(axis_text_x, self).blank(ax)
        labels = ax.get_xticklabels()
        for l in labels:
            l.set_visible(False)


class axis_text_y(themeable):
    """
    x-axis tick labels

    Parameters
    ----------
    theme_element : element_text
    """
    def apply(self, ax):
        super(axis_text_y, self).apply(ax)
        labels = ax.get_yticklabels()
        for l in labels:
            l.set(**self.properties)

    def blank(self, ax):
        super(axis_text_y, self).blank(ax)
        labels = ax.get_yticklabels()
        for l in labels:
            l.set_visible(False)


class axis_text(axis_text_x, axis_text_y):
    """
    Axis tick labels

    Parameters
    ----------
    theme_element : element_text
    """
    pass


class text(axis_text, legend_text, strip_text, title):
    """
    All text elements in the plot

    Parameters
    ----------
    theme_element : element_text
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
    """
    x-axis line

    Parameters
    ----------
    theme_element : element_line
    """
    position = 'bottom'

    def apply(self, ax):
        super(axis_line_x, self).apply(ax)
        with suppress(KeyError):
            del self.properties['solid_capstyle']

        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set(**self.properties)

    def blank(self, ax):
        super(axis_line_x, self).blank(ax)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)


class axis_line_y(themeable):
    """
    y-axis line

    Parameters
    ----------
    theme_element : element_line
    """
    position = 'left'

    def apply(self, ax):
        super(axis_line_y, self).apply(ax)
        with suppress(KeyError):
            del self.properties['solid_capstyle']

        ax.spines['right'].set_visible(False)
        ax.spines['left'].set(**self.properties)

    def blank(self, ax):
        super(axis_line_y, self).blank(ax)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)


class axis_line(axis_line_x, axis_line_y):
    """
    x & y axis lines

    Parameters
    ----------
    theme_element : element_line
    """
    pass


class axis_ticks_x(themeable):
    """
    x-axis tick lines

    Parameters
    ----------
    theme_element : element_line
    """
    def apply(self, ax):
        super(axis_ticks_x, self).apply(ax)

        d = deepcopy(self.properties)
        with suppress(KeyError):
            d['markeredgewidth'] = d.pop('linewidth')

        for line in ax.get_xticklines():
            line.set(**d)

    def blank(self, ax):
        super(axis_ticks_x, self).blank(ax)
        ax.tick_params(axis='x', which='both', length=0)


class axis_ticks_y(themeable):
    """
    y-axis tick lines

    Parameters
    ----------
    theme_element : element_line
    """
    def apply(self, ax):
        super(axis_ticks_y, self).apply(ax)

        d = deepcopy(self.properties)
        with suppress(KeyError):
            d['markeredgewidth'] = d.pop('linewidth')

        for line in ax.get_yticklines():
            line.set(**d)

    def blank(self, ax):
        super(axis_ticks_y, self).blank(ax)
        ax.tick_params(axis='y', which='both', length=0)


class axis_ticks(axis_ticks_x, axis_ticks_y):
    """
    x & y axis tick lines

    Parameters
    ----------
    theme_element : element_line
    """
    pass


class panel_grid_major_x(themeable):
    """
    Vertical major grid lines

    Parameters
    ----------
    theme_element : element_line
    """
    def apply(self, ax):
        super(panel_grid_major_x, self).apply(ax)
        ax.xaxis.grid(which='major', **self.properties)

    def blank(self, ax):
        super(panel_grid_major_x, self).blank(ax)
        ax.grid(False, which='major', axis='x')


class panel_grid_major_y(themeable):
    """
    Horizontal major grid lines

    Parameters
    ----------
    theme_element : element_line
    """
    def apply(self, ax):
        super(panel_grid_major_y, self).apply(ax)
        ax.yaxis.grid(which='major', **self.properties)

    def blank(self, ax):
        super(panel_grid_major_y, self).blank(ax)
        ax.grid(False, which='major', axis='y')


class panel_grid_minor_x(themeable):
    """
    Vertical minor grid lines

    Parameters
    ----------
    theme_element : element_line
    """
    def apply(self, ax):
        super(panel_grid_minor_x, self).apply(ax)
        ax.xaxis.grid(which='minor', **self.properties)

    def blank(self, ax):
        super(panel_grid_minor_x, self).blank(ax)
        ax.grid(False, which='minor', axis='x')


class panel_grid_minor_y(themeable):
    """
    Horizontal minor grid lines

    Parameters
    ----------
    theme_element : element_line
    """
    def apply(self, ax):
        super(panel_grid_minor_y, self).apply(ax)
        ax.yaxis.grid(which='minor', **self.properties)

    def blank(self, ax):
        super(panel_grid_minor_y, self).blank(ax)
        ax.grid(False, which='minor', axis='y')


class panel_grid_major(panel_grid_major_x, panel_grid_major_y):
    """
    Major grid lines

    Parameters
    ----------
    theme_element : element_line
    """
    pass


class panel_grid_minor(panel_grid_minor_x, panel_grid_minor_y):
    """
    Minor grid lines

    Parameters
    ----------
    theme_element : element_line
    """
    pass


class panel_grid(panel_grid_major, panel_grid_minor):
    """
    Grid lines

    Parameters
    ----------
    theme_element : element_line
    """
    pass


class line(axis_line, axis_ticks, panel_grid):
    """
    All line elements

    Parameters
    ----------
    theme_element : element_line
    """

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
    """
    Legend key background

    Parameters
    ----------
    theme_element : element_rect
    """
    def apply_figure(self, figure):
        super(legend_key, self).apply_figure(figure)
        with suppress(KeyError):
            das = figure._themeable['legend_key']
            for da in das:
                da.patch.set(**self.properties)

    def blank_figure(self, figure):
        super(legend_key, self).blank_figure(figure)
        with suppress(KeyError):
            das = figure._themeable['legend_key']
            for da in das:
                _blankout_rect(da.patch)


class legend_background(themeable):
    """
    Legend background

    Parameters
    ----------
    theme_element : element_rect
    """
    def apply_figure(self, figure):
        super(legend_background, self).apply_figure(figure)
        # anchored offset box
        with suppress(KeyError):
            aob = figure._themeable['legend_background']
            aob.patch.set(**self.properties)
            if self.properties:
                aob._drawFrame = True
                # some small sensible padding
                if not aob.pad:
                    aob.pad = .2

    def blank_figure(self, figure):
        super(legend_background, self).blank_figure(figure)
        with suppress(KeyError):
            aob = figure._themeable['legend_background']
            _blankout_rect(aob.patch)


class panel_background(themeable):
    """
    Panel background

    Parameters
    ----------
    theme_element : element_rect
    """
    def apply(self, ax):
        super(panel_background, self).apply(ax)
        ax.patch.set(**self.properties)

    def blank(self, ax):
        super(panel_background, self).blank(ax)
        _blankout_rect(ax.patch)


class panel_border(themeable):
    """
    Panel border

    Parameters
    ----------
    theme_element : element_rect
    """
    def apply(self, ax):
        super(panel_border, self).apply(ax)
        d = deepcopy(self.properties)
        # Be lenient, if using element_line
        with suppress(KeyError):
            d['edgecolor'] = d.pop('color')

        with suppress(KeyError):
            del d['facecolor']

        ax.patch.set(**d)

    def blank(self, ax):
        super(panel_border, self).blank(ax)
        ax.patch.set_linewidth(0)


class plot_background(themeable):
    """
    Plot background

    Parameters
    ----------
    theme_element : element_rect
    """
    def setup_figure(self, figure):
        figure.patch.set(**self.properties)

    def blank_figure(self, figure):
        super(plot_background, self).blank_figure(figure)
        _blankout_rect(figure.patch)


class strip_background_x(themeable):
    """
    Horizontal facet label background

    Parameters
    ----------
    theme_element : element_rect
    """
    def apply_figure(self, figure):
        super(strip_background_x, self).apply_figure(figure)
        with suppress(KeyError):
            bboxes = figure._themeable['strip_background_x']
            for bbox in bboxes:
                bbox.set(**self.properties)

    def blank_figure(self, figure):
        super(strip_background_x, self).blank_figure(figure)
        with suppress(KeyError):
            rects = figure._themeable['strip_background_x']
            for rect in rects:
                _blankout_rect(rect)


class strip_background_y(themeable):
    """
    Vertical facet label background

    Parameters
    ----------
    theme_element : element_rect
    """
    def apply_figure(self, figure):
        super(strip_background_y, self).apply_figure(figure)
        with suppress(KeyError):
            bboxes = figure._themeable['strip_background_y']
            for bbox in bboxes:
                bbox.set(**self.properties)

    def blank_figure(self, figure):
        super(strip_background_y, self).blank_figure(figure)
        with suppress(KeyError):
            rects = figure._themeable['strip_background_y']
            for rect in rects:
                _blankout_rect(rect)


class strip_background(strip_background_x, strip_background_y):
    """
    Facet label background

    Parameters
    ----------
    theme_element : element_rect
    """
    pass


class rect(legend_key, legend_background,
           panel_background, panel_border,
           plot_background, strip_background):
    """
    All rectangle elements

    Parameters
    ----------
    theme_element : element_rect
    """
    pass


class axis_ticks_major_length(themeable):
    """
    Axis major-tick length

    Parameters
    ----------
    theme_element : float
    """
    @property
    def rcParams(self):
        rcParams = super(axis_ticks_major_length, self).rcParams
        val = self.properties['value']
        rcParams['xtick.major.size'] = val
        rcParams['ytick.major.size'] = val
        return rcParams


class axis_ticks_minor_length(themeable):
    """
    Axis minor-tick length

    Parameters
    ----------
    theme_element : float
    """
    @property
    def rcParams(self):
        rcParams = super(axis_ticks_minor_length, self).rcParams
        val = self.properties['value']
        rcParams['xtick.minor.size'] = val
        rcParams['ytick.minor.size'] = val
        return rcParams


class axis_ticks_length(axis_ticks_major_length,
                        axis_ticks_minor_length):
    """
    Axis tick length

    Parameters
    ----------
    theme_element : float
    """
    pass


class axis_ticks_major_pad(themeable):
    """
    Axis major-tick padding

    Parameters
    ----------
    theme_element : float
    """
    @property
    def rcParams(self):
        rcParams = super(axis_ticks_minor_pad, self).rcParams
        val = self.properties['value']
        rcParams['xtick.major.pad'] = val
        rcParams['ytick.major.pad'] = val
        return rcParams


class axis_ticks_minor_pad(themeable):
    """
    Axis minor-tick padding

    Parameters
    ----------
    theme_element : float
    """
    @property
    def rcParams(self):
        rcParams = super(axis_ticks_minor_pad, self).rcParams
        val = self.properties['value']
        rcParams['xtick.minor.pad'] = val
        rcParams['ytick.minor.pad'] = val
        return rcParams


class axis_ticks_pad(axis_ticks_major_pad,
                     axis_ticks_minor_pad):
    """
    Axis tick padding

    Parameters
    ----------
    theme_element : float
    """
    pass


class axis_ticks_direction_x(themeable):
    """
    x-axis tick direction

    Parameters
    ----------
    theme_element : 'in' | 'out' | 'inout'
    """
    @property
    def rcParams(self):
        rcParams = super(axis_ticks_direction_x, self).rcParams
        rcParams['xtick.direction'] = self.properties['value']
        return rcParams


class axis_ticks_direction_y(themeable):
    """
    y-axis tick direction

    Parameters
    ----------
    theme_element : 'in' | 'out' | 'inout'
    """
    @property
    def rcParams(self):
        rcParams = super(axis_ticks_direction_y, self).rcParams
        rcParams['ytick.direction'] = self.properties['value']
        return rcParams


class axis_ticks_direction(axis_ticks_direction_x,
                           axis_ticks_direction_y):
    """
    axis tick direction

    Parameters
    ----------
    theme_element : 'in' | 'out' | 'inout'
    """
    pass


class panel_margin_x(themeable):
    """
    Horizontal margin around the facet panels

    Parameters
    ----------
    theme_element : float
        Must be in the [0, 1] range. It is specified
        as a fraction of the panel width.
    """
    def setup_figure(self, figure):
        val = self.properties['value']
        if val is not None:
            figure.subplots_adjust(wspace=val)


class panel_margin_y(themeable):
    """
    Vertical margin around the facet panels

    Parameters
    ----------
    theme_element : float
        Must be in the [0, 1] range. It is specified
        as a fraction of the panel height.
    """
    def setup_figure(self, figure):
        val = self.properties['value']
        if val is not None:
            figure.subplots_adjust(hspace=val)


class panel_margin(panel_margin_x, panel_margin_y):
    """
    Margin around the facet panels

    Parameters
    ----------
    theme_element : float
        Must be in the [0, 1] range. It is specified
        as a fraction of the panel width and panel
        height.
    """
    pass


class plot_margin(themeable):
    """
    Plot Margin

    Parameters
    ----------
    theme_element : float
        Must be in the [0, 1] range. It is specified
        as a fraction of the figure width and figure
        height. Values outside that range will
        stretch the figure.
    """
    def setup_figure(self, figure):
        val = self.properties['value']
        if val is not None:
            figure.subplots_adjust(left=val,
                                   right=1-val,
                                   bottom=val,
                                   top=1-val)


class panel_ontop(themeable):
    """
    Place panel background & gridlines over/under the data layers

    Parameters
    ----------
    theme_element : bool
        Default is False.
    """
    def apply(self, ax):
        super(panel_ontop, self).apply(ax)
        ax.set_axisbelow(self.properties['value'])


class aspect_ratio(themeable):
    """
    Aspect ratio of the panel

    Parameters
    ----------
    theme_element : float
    """
    def apply(self, ax):
        super(aspect_ratio, self).apply(ax)
        ax.set_aspect(self.properties['value'])


class dpi(themeable):
    """
    DPI with which to draw/save the figure

    Parameters
    ----------
    theme_element : int
    """
    @property
    def rcParams(self):
        rcParams = super(dpi, self).rcParams
        val = self.properties['value']
        rcParams['figure.dpi'] = val
        rcParams['savefig.dpi'] = val
        return rcParams


class figure_size(themeable):
    """
    Figure size in inches

    Parameters
    ----------
    theme_element : tuple
        (width, height) in inches
    """
    @property
    def rcParams(self):
        rcParams = super(figure_size, self).rcParams
        try:
            width, height = self.properties['value']
        except ValueError:
            raise GgplotError(
                'figure_size should be a tuple (width, height) '
                'with the values in inches')

        rcParams['figure.figsize'] = '{}, {}'.format(width,
                                                     height)
        return rcParams


class facet_spacing(themeable):
    """
    Facet spacing

    Full access to the underlying Matplolib subplot
    adjustment parameters

    Parameters
    ----------
    theme_element : dict
        See :class:`matplotlib.figure.SubplotParams`
        for the keys that the dictionary *can* have.
    """
    def setup_figure(self, figure):
        kwargs = self.properties['value']
        figure.subplots_adjust(**kwargs)
