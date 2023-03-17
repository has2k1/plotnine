import matplotlib.transforms as mtransforms
from matplotlib.offsetbox import AuxTransformBox, DrawingArea


class ColoredDrawingArea(DrawingArea):
    """
    A Drawing Area with a background color
    """

    def __init__(
        self,
        width: float,
        height: float,
        xdescent=0.0,
        ydescent=0.0,
        clip=True,
        color="none",
    ):
        from matplotlib.patches import Rectangle

        super().__init__(width, height, xdescent, ydescent, clip=clip)

        self.patch = Rectangle(
            (0, 0),
            width=width,
            height=height,
            facecolor=color,
            edgecolor="None",
            linewidth=0,
            antialiased=False,
        )
        self.add_artist(self.patch)


# Fix AuxTransformBox, Adds a dpi_transform
# See https://github.com/matplotlib/matplotlib/pull/7344
class MyAuxTransformBox(AuxTransformBox):
    def __init__(self):
        aux_transform = mtransforms.IdentityTransform()
        AuxTransformBox.__init__(self, aux_transform)
        self.dpi_transform = mtransforms.Affine2D()

    def get_transform(self):
        """
        Return the :class:`~matplotlib.transforms.Transform` applied
        to the children
        """
        return (
            self.aux_transform
            + self.ref_offset_transform
            + self.dpi_transform
            + self.offset_transform
        )

    def draw(self, renderer):
        """
        Draw the children
        """
        dpi_cor = renderer.points_to_pixels(1.0)
        self.dpi_transform.clear()
        self.dpi_transform.scale(dpi_cor, dpi_cor)

        for c in self._children:
            c.draw(renderer)

        self.stale = False
