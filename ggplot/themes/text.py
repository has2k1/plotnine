from pprint import pprint


class element_text(object):

    def __init__(self, family="", face="", colour="", size="", hjust=None,
                 vjust=None, angle=0, lineheight=0, color=""):
        """Set element_text properties according to the ggplot2 API.

        vjust and hjust are not fully implemented, 0 or 1 is translated
        to left, bottom; right, top. Any other value is translated to center.

        """
        self.element = None
        self.properties = {}
        if family:
            self.properties["family"] = family
        if face:
            if face == "plain":
                self.properties["style"] = "normal"
            elif face == "italic":
                self.properties["style"] = "italic"
            elif face == "bold":
                self.properties["weight"] = "bold"
            elif face == "bold.italic":
                self.properties["style"] = "italic"
                self.properties["weight"] = "bold"
        if colour or color:
            if colour:
                self.properties["color"] = colour
            else:
                self.properties["color"] = color
        if size:
            self.properties["size"] = size
        if hjust is not None:
            self.properties["ha"] = self._translate_hjust(hjust)
        if vjust is not None:
            self.properties["va"] = self._translate_vjust(vjust)
        if angle:
            self.properties["rotation"] = angle
        if lineheight is not None:
            # I'm not sure if this is the right translation. Couldn't find an
            # example and this property doesn't seem to have any effect.
            # -gdowding
            self.properties["linespacing"] = lineheight

    def _translate_hjust(self, just):
        "Translate ggplot2 justification from [0, 1] to left, right, center."
        if just == 0:
            return "left"
        elif just == 1:
            return "right"
        else:
            return "center"

    def _translate_vjust(self, just):
        "Translate ggplot2 justification from [0, 1] to top, bottom, center."
        if just == 0:
            return "bottom"
        elif just == 1:
            return "top"
        else:
            return "center"

    def apply_rcparams(self, rcParams):
        element = self.element
        family = self.properties.get("family")
        if family:
            if element == "text":
                rcParams["font.family"] = family
        style = self.properties.get("style")
        if style:
            if element == "text":
                rcParams["font.style"] = style
        weight = self.properties.get("weight")
        if weight:
            if element == "text":
                rcParams["font.weight"] = weight
        size = self.properties.get("size")
        if size:
            if element == "text":
                rcParams["font.size"] = size
            if element in ("text", "axis_title"):
                rcParams["axes.titlesize"] = size
            if element in ("text", "axes_title"):
                rcParams["axes.labelsize"] = size
                rcParams["xtick.labelsize"] = size
            if element in ("text", "axes_title"):
                rcParams["axes.labelsize"] = size
                rcParams["ytick.labelsize"] = size
            if element in ("text", "legend_text"):
                rcParams["legend.fontsize"] = size
        color = self.properties.get("color")
        if color:
            if element == "text":
                rcParams["text.color"] = color
            if element == "text":
                rcParams["xtick.color"] = color
            if element in ("text", "axis_text"):
                rcParams["ytick.color"] = color
            if element in ("text", "axis_title"):
                rcParams["axes.labelcolor"] = color

        # rcParams that affect axis_title or what matplotlib refers to as
        # x or y axis label.
        # axes.labelsize, axes.labelweight, axes.labelcolor

    def post_plot_callback(self, ax):
        pass

    def __call__(self, ax):
        # todo elements
        # X text - all text
        # X axis_text - text along axes
        # X axis_text_x
        # X axis_text_y
        # legend_text - legend item labels
        # legend_text_align - alignment of labes [0, 1] left, to right
        # plot_title
        # strip_text -  facet labels
        # strip_text_x
        # strip_text_y

        if self.element == "axis_text" or self.element == "axis_text_x":
            labels = ax.get_xticklabels()
            for l in labels:
                l.set(**self.properties)
        if self.element == "axis_text" or self.element == "axis_text_y":
            labels = ax.get_yticklabels()
            for l in labels:
                l.set(**self.properties)

        else:
            print "unknown element %s" % self.element
