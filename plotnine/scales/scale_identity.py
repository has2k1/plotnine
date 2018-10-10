from ..doctools import document
from ..utils import identity, alias
from .scale import scale_discrete, scale_continuous


class MapTrainMixin:
    """
    Override map and train methods
    """
    def map(self, x):
        return x

    def train(self, x):
        # do nothing if no guide,
        # otherwise train so we know what breaks to use
        if self.guide is None:
            return

        return super(MapTrainMixin, self).train(x)


@document
class scale_color_identity(MapTrainMixin, scale_discrete):
    """
    No color scaling

    Parameters
    ----------
    {superclass_parameters}
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    """
    _aesthetics = ['color']
    palette = staticmethod(identity)
    guide = None


@document
class scale_fill_identity(scale_color_identity):
    """
    No color scaling

    Parameters
    ----------
    {superclass_parameters}
    """
    _aesthetics = ['fill']


@document
class scale_shape_identity(MapTrainMixin, scale_discrete):
    """
    No shape scaling

    Parameters
    ----------
    {superclass_parameters}
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    """
    _aesthetics = ['shape']
    palette = staticmethod(identity)
    guide = None


@document
class scale_linetype_identity(MapTrainMixin, scale_discrete):
    """
    No linetype scaling

    Parameters
    ----------
    {superclass_parameters}
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    """
    _aesthetics = ['linetype']
    palette = staticmethod(identity)
    guide = None


@document
class scale_alpha_identity(MapTrainMixin, scale_continuous):
    """
    No alpha scaling

    Parameters
    ----------
    {superclass_parameters}
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    """
    _aesthetics = ['alpha']
    palette = staticmethod(identity)
    guide = None


@document
class scale_size_identity(MapTrainMixin, scale_continuous):
    """
    No size scaling

    Parameters
    ----------
    {superclass_parameters}
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    """
    _aesthetics = ['size']
    palette = staticmethod(identity)
    guide = None


# American to British spelling
alias('scale_colour_identity', scale_color_identity)
