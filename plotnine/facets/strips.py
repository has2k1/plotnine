import types
from contextlib import suppress

with suppress(ImportError):
    import matplotlib.text as mtext
    import matplotlib.patches as mpatch


class strips(list):
    """
    List of all strips for a plot
    """
    @staticmethod
    def initialise(facet):
        new = strips()
        new.facet = facet
        return new

    @property
    def axs(self):
        return self.facet.axs

    @property
    def layout(self):
        return self.facet.layout.layout

    @property
    def theme(self):
        return self.facet.theme

    @property
    def top_strips(self):
        return [s for s in self if s.location == 'top']

    @property
    def right_strips(self):
        return [s for s in self if s.location == 'right']

    def draw(self):
        for s in self:
            s.draw()

    def generate(self):
        """
        Calculate the box information for all strips

        It is stored in self.strip_info
        """
        for pidx, layout_info in self.layout.iterrows():
            ax = self.axs[pidx]
            lst = self.facet.make_ax_strips(layout_info, ax)
            self.extend(lst)

        top_strips = self.top_strips
        right_strips = self.right_strips

        # All top strips should have the same height and x text location,
        # and right strips should have the same width and y text location
        with suppress(ValueError):
            top_height = max(s.info.box_height for s in top_strips)
            top_y = max(s.info.y for s in top_strips)
            for s in top_strips:
                s.info.box_height = top_height
                s.info.y = top_y

        with suppress(ValueError):
            right_width = max(s.info.box_width for s in right_strips)
            right_x = max(s.info.x for s in right_strips)
            for s in right_strips:
                s.info.box_width = right_width
                s.info.x = right_x

        with suppress(ValueError):
            breadth = max(s.info.breadth_inches for s in self)
            for s in self:
                s.info.breadth_inches = breadth

    def breadth(self, location='top'):
        lst = self.top_strips if location == 'top' else self.right_strips
        try:
            return lst[0].info.breadth_inches
        except IndexError:
            return 0


class strip:
    """
    A strip

    This class exists to have in one place all that is required to draw
    strip text onto an axes. As Matplotlib does not have a layout manager
    that makes it easy to adorn an axes with artists, we have to compute
    the space required for the text and the background strip on which it
    is drawn. This is very finicky and fails once the facets become
    complicated.
    """

    def __init__(self, vars, layout_info, facet, ax, location):
        self.vars = vars
        self.ax = ax
        self.location = location
        self.figure = facet.figure
        self.theme = facet.theme

        def _calc_num_lines(label_info):
            n = len(label_info)
            for row in label_info:
                if isinstance(row, str):
                    n = max(n, len(row.split('\n')))
            return n

        dimension = 'cols' if location == 'top' else 'rows'
        label_info = layout_info[list(vars)]
        label_info._meta = {'dimension': dimension}
        label_info = facet.labeller(label_info)
        self.label_info = label_info
        self.num_lines = _calc_num_lines(label_info)
        self.info = self.details()

    @property
    def inner_margins(self):
        if self.location == 'right':
            strip_name = 'strip_text_y'
            side1, side2 = 'l', 'r'
        else:
            strip_name = 'strip_text_x'
            side1, side2 = 't', 'b'

        margin = self.theme.themeables.property(strip_name, 'margin')
        m1 = margin.get_as(side1, 'pt')
        m2 = margin.get_as(side2, 'pt')
        return m1, m2

    @property
    def breadth(self):
        """
        Breadth of the strip background in inches

        Parameters
        ----------
        num_lines : int
            Number of text lines
        """
        dpi = 72
        theme = self.theme
        _property = theme.themeables.property

        if self.location == 'right':
            strip_name = 'strip_text_y'
            num_lines = self.num_lines or self.num_vars_y
        else:
            strip_name = 'strip_text_x'
            num_lines = self.num_lines or self.num_vars_x

        if not num_lines:
            return 0

        # The facet labels are placed onto the figure using
        # transAxes dimensions. The line height and line
        # width are mapped to the same [0, 1] range
        # i.e (pts) * (inches / pts) * (1 / inches)
        fontsize = _property(strip_name, 'size')
        linespacing = _property(strip_name, 'linespacing')

        # margins on either side of the strip text
        m1, m2 = self.inner_margins
        # Using figure.dpi value here does not workout well!
        breadth = (linespacing*fontsize) * num_lines / dpi
        breadth = breadth + (m1 + m2) / dpi
        return breadth

    def details(self):
        """
        Calculate the location and size of the strip box for an axis

        Returns
        -------
        out : types.SimpleNamespace
            A structure with all the coordinates (x, y) required
            to draw the strip text and the background box
            (box_x, box_y, box_width, box_height).
        """
        dpi = 72
        ax = self.ax
        location = self.location
        _property = self.theme.themeables.property
        bbox = ax.get_window_extent().transformed(
            self.figure.dpi_scale_trans.inverted()
        )
        ax_width, ax_height = bbox.width, bbox.height  # in inches
        strip_size = self.breadth
        m1, m2 = self.inner_margins
        m1, m2 = m1/dpi, m2/dpi

        if location == 'right':
            box_x = 1
            box_y = 0
            box_width = strip_size/ax_width
            box_height = 1
            # y & height properties of the background slide and
            # shrink the strip vertically. The x margin slides
            # it horizontally.
            with suppress(KeyError):
                box_y = _property('strip_background_y', 'y')
            with suppress(KeyError):
                box_height = _property('strip_background_y', 'height')

            margin = _property('strip_margin_x')
            x = 1 + (strip_size-m2+m1) / (2*ax_width)
            y = (2*box_y+box_height)/2
            # margin adjustment
            hslide = 1 + margin*strip_size/ax_width
            x *= hslide
            box_x *= hslide
            rotation = -90
            label = '\n'.join(reversed(self.label_info))
        else:  # top
            box_x = 0
            box_y = 1
            box_width = 1
            box_height = strip_size/ax_height
            # x & width properties of the background slide and
            # shrink the strip horizontally. The y margin slides
            # it vertically.
            with suppress(KeyError):
                box_x = _property('strip_background_x', 'x')
            with suppress(KeyError):
                box_width = _property('strip_background_x', 'width')

            margin = _property('strip_margin_y')
            x = (2*box_x+box_width)/2
            y = 1 + (strip_size-m1+m2)/(2*ax_height)
            # margin adjustment
            vslide = 1 + margin*strip_size/ax_height
            y *= vslide
            box_y *= vslide
            rotation = 0
            label = '\n'.join(self.label_info)

        info = types.SimpleNamespace(
            x=x,
            y=y,
            box_x=box_x,
            box_y=box_y,
            box_width=box_width,
            box_height=box_height,
            breadth_inches=strip_size,
            location=location,
            label=label,
            ax=ax,
            rotation=rotation,
        )
        return info

    def draw(self):
        """
        Create a background patch and put a label on it
        """
        themeable = self.figure._themeable
        info = self.info
        ax = info.ax

        rect = mpatch.FancyBboxPatch(
            (info.box_x, info.box_y),
            width=info.box_width,
            height=info.box_height,
            facecolor='lightgrey',
            edgecolor='None',
            transform=ax.transAxes,
            zorder=2.2,  # > ax line & boundary
            boxstyle='square, pad=0',
            clip_on=False
        )

        text = mtext.Text(
            info.x,
            info.y,
            info.label,
            rotation=info.rotation,
            verticalalignment='center',
            horizontalalignment='center',
            transform=ax.transAxes,
            zorder=3.3,  # > rect
            clip_on=False
        )

        ax.add_artist(rect)
        ax.add_artist(text)

        for key in ('strip_text_x', 'strip_text_y',
                    'strip_background_x', 'strip_background_y'):
            if key not in themeable:
                themeable[key] = []

        if info.location == 'right':
            themeable['strip_background_y'].append(rect)
            themeable['strip_text_y'].append(text)
        else:
            themeable['strip_background_x'].append(rect)
            themeable['strip_text_x'].append(text)
