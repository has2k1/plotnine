"""provide element targets, that is the elements that are targetd for theming.

This is heirarchical, but ggplot uses the terms somewhat revers of
OO inheritence.

From the ggplot2 documentation the axis.title inherits from text.
What this means is that axis.title and text have the same elements
that may be themed, but the scope of what they apply to is different.
The scope of text covers all text in the plot, axis.title applies
only to the axis.title. In matplotlib terms this means that a theme
that covers text also has to cover axis.title.

"""


def element_factory(element_target):
    if element_target == "text":
        return Text()
    elif element_target == "axis_title":
        return AxisTitle()
    elif element_target == "axis_text":
        return AxisText()
    elif element_target == "axis_text_x":
        return AxisTextX()
    elif element_target == "axis_text_y":
        return AxisTextY()
    elif element_target == "axis_ticks":
        return AxisTicks()
    else:
        return None


class ElementTarget(object):
    def get_rcparams(self, properties):
        return {}

    def post_plot_callback(self, ax, properties):
        pass


class AxisTicks(ElementTarget):
    # @todo: line_element
    def get_rcparams(self, properties):
        rcParams = super(AxisTicks, self).get_rcparams(properties)
        color = properties.get("color")
        if color:
            rcParams["xtick.color"] = color
            rcParams["ytick.color"] = color
        return rcParams


class AxisTitle(ElementTarget):
    def get_rcparams(self, properties):
        rcParams = super(AxisTitle, self).get_rcparams(properties)
        size = properties.get("size")
        if size:
            rcParams["axes.titlesize"] = size
            rcParams["axes.labelsize"] = size
        color = properties.get("color")
        if color:
            rcParams["axes.labelcolor"] = color

        return rcParams


class AxisTextX(ElementTarget):
    def post_plot_callback(self, ax, properties):
        super(AxisTextX, self).post_plot_callback(ax, properties)
        labels = ax.get_xticklabels()
        for l in labels:
            l.set(**properties)


class AxisTextY(ElementTarget):
    def post_plot_callback(self, ax, properties):
        super(AxisTextY, self).post_plot_callback(ax, properties)
        labels = ax.get_yticklabels()
        for l in labels:
            l.set(**properties)


class AxisText(AxisTextX, AxisTextY):
    pass


class Text(AxisTitle, AxisText):
    """
    Scope of theme that applies to all text in plot
    """

    def get_rcparams(self, properties):
        rcParams = super(Text, self).get_rcparams(properties)
        family = properties.get("family")
        if family:
            rcParams["font.family"] = family
        style = properties.get("style")
        if style:
            rcParams["font.style"] = style
        weight = properties.get("weight")
        if weight:
            rcParams["font.weight"] = weight
        size = properties.get("size")
        if size:
            rcParams["font.size"] = size
            rcParams["xtick.labelsize"] = size
            rcParams["ytick.labelsize"] = size
            rcParams["legend.fontsize"] = size
        color = properties.get("color")
        if color:
            rcParams["text.color"] = color
            # changes text and tick color, but we just want the text color
            #rcParams["xtick.color"] = color
        return rcParams

