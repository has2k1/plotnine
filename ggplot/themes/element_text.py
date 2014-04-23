class element_text(object):

    def __init__(self, family="", face="", colour="", size="", hjust=None,
                 vjust=None, angle=0, lineheight=0, color=""):
        """Set element_text properties according to the ggplot2 API.

        vjust and hjust are not fully implemented, 0 or 1 is translated
        to left, bottom; right, top. Any other value is translated to center.

        """
        self.target = None
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

    def apply_rcparams(self):
        if self.target:
            rc_params = self.target.get_rcParams(self.properties)
            return rcParams

    def post_plot_callback(self, ax):
        if self.target:
            self.target.post_plot_callback(ax, self.properties)

    def __call__(self, ax):
        #@todo: get rid of this
        self.post_plot_callback(ax)
