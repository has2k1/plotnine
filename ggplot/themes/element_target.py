"""provide element targets, that is the elements that are targetd for theming.


From the ggplot2 documentation the axis.title inherits from text.
What this means is that axis.title and text have the same elements
that may be themed, but the scope of what they apply to is different.
The scope of text covers all text in the plot, axis.title applies
only to the axis.title. In matplotlib terms this means that a theme
that covers text also has to cover axis.title.

"""

from types import FunctionType


class Trace(type):

    def __new__(meta, class_name, bases, class_dict):
        def wrapper(class_name, func_name, func, depth):
            def trace(*args, **kwargs):
                print("%s>> enter %s %s" % (
                    " " * 2 * depth, class_name, func_name))
                result = func(*args, **kwargs)
                print("%s<< exit %s %s" % (
                    " " * 2 * depth, class_name, func_name))
                return result
            return trace

        traced = {}
        for k, v in class_dict.items():
            if type(v) == FunctionType and not k.startswith("_"):
                traced[k] = wrapper(class_name, k, v, len(bases))
        class_dict.update(traced)
        return super(Trace, meta).__new__(meta, class_name, bases, class_dict)


def element_target_factory(element_target, element_theme):
    if element_target == "text":
        return text(element_theme)
    elif element_target == "axis_title":
        return axis_title(element_theme)
    elif element_target == "axis_text":
        return axis_text(element_theme)
    elif element_target == "axis_text_x":
        return axis_text_x(element_theme)
    elif element_target == "axis_text_y":
        return axis_text_y(element_theme)
    elif element_target == "axis_ticks":
        return axis_ticks(element_theme)
    else:
        return None


def unique_element_targets(element_targets):
    """From a list of elment targets, save the last element target for targets
    of the same type.

    This is not strictly necessary, but is an optimaztion when combining themes
    to prevent carying arround themes that will be completely overridden.

    """
    target_seen = set()
    reversed_targets = []
    for element_target in reversed(element_targets):
        if element_target.__class__ not in target_seen:
            target_seen.add(element_target.__class__)
            reversed_targets.append(element_target)

    return [i for i in reversed(reversed_targets)]


def sorted_element_targets(element_target_list):
    """Sort element_targets in reverse based on the their depth in the
    inheritence heirarchy.

    This will make sure any general target, like text will be applied by
    a specific target like axis_text_x.

    """
    def key(element_target_):
        return len(element_target_.__class__.__mro__)

    return sorted(element_target_list, key=key, reverse=True)


class __element_target(object):
    #__metaclass__ = Trace

    def __init__(self, element_theme=None):
        # @todo: fix unittests in test_element_target or leave this as is?
        if element_theme:
            self.properties = element_theme.properties
        else:
            self.properites = {}

    def __eq__(self, other):
        "Mostly for unittesting."
        return ((self.__class__ == other.__class__) and
                (self.properties == other.properties))

    def get_rcparams(self):
        return {}

    def post_plot_callback(self, ax):
        pass


class axis_ticks(__element_target):
    # @todo: line_element
    def get_rcparams(self):
        rcParams = super(axis_ticks, self).get_rcparams()
        color = self.properties.get("color")
        if color:
            rcParams["xtick.color"] = color
            rcParams["ytick.color"] = color
        return rcParams


class axis_title_x(__element_target):
    def post_plot_callback(self, ax):
        super(axis_title_x, self).post_plot_callback(ax)

        x_axis_label = ax.get_xaxis().get_label()
        x_axis_label.set(**self.properties)


class axis_title_y(__element_target):
    def post_plot_callback(self, ax):
        super(axis_title_y, self).post_plot_callback(ax)
        y_axis_label = ax.get_yaxis().get_label()
        y_axis_label.set(**self.properties)


class axis_title(axis_title_x, axis_title_y):
    pass


class axis_text_x(__element_target):

    def post_plot_callback(self, ax):
        super(axis_text_x, self).post_plot_callback(ax)
        labels = ax.get_xticklabels()
        for l in labels:
            l.set(**self.properties)


class axis_text_y(__element_target):

    def post_plot_callback(self, ax):
        super(axis_text_y, self).post_plot_callback(ax)
        labels = ax.get_yticklabels()
        for l in labels:
            l.set(**self.properties)


class axis_text(axis_text_x, axis_text_y):
    pass


class text(axis_text, axis_title):
    """
    Scope of theme that applies to all text in plot
    """

    def get_rcparams(self):
        rcParams = super(text, self).get_rcparams()
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
