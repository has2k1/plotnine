from .element_base import element_base


class element_blank(element_base):
    """
    Theme element: Blank
    """

    def __init__(self):
        self.properties = {"visible": False}
