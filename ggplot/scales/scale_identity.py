from __future__ import absolute_import, division, print_function

from ..utils import identity, alias
from .scale import scale_discrete, scale_continuous


class MapTrainMixin(object):
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


class scale_color_identity(MapTrainMixin, scale_discrete):
    """
    No color scaling

    Parameters
    ----------
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    kwargs : dict
        Parameters passed on to :class:`.scale_discrete`
    """
    aesthetics = ['color']
    palette = staticmethod(identity)
    guide = None


class scale_fill_identity(scale_color_identity):
    """
    No color scaling

    See :class:`.scale_color_identity` for documentation.
    """
    aesthetics = ['fill']


class scale_shape_identity(MapTrainMixin, scale_discrete):
    """
    No shape scaling

    Parameters
    ----------
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    kwargs : dict
        Parameters passed on to :class:`.scale_discrete`
    """
    aesthetics = ['shape']
    palette = staticmethod(identity)
    guide = None


class scale_linetype_identity(MapTrainMixin, scale_discrete):
    """
    No linetype scaling

    Parameters
    ----------
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    kwargs : dict
        Parameters passed on to :class:`.scale_discrete`
    """
    aesthetics = ['linetype']
    palette = staticmethod(identity)
    guide = None


class scale_alpha_identity(MapTrainMixin, scale_continuous):
    """
    No alpha scaling

    Parameters
    ----------
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    kwargs : dict
        Parameters passed on to :class:`.scale_continuous`
    """
    aesthetics = ['alpha']
    palette = staticmethod(identity)
    guide = None


class scale_size_identity(MapTrainMixin, scale_continuous):
    """
    No size scaling

    Parameters
    ----------
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    kwargs : dict
        Parameters passed on to :class:`.scale_continuous`
    """
    aesthetics = ['size']
    palette = staticmethod(identity)
    guide = None


# American to British spelling
alias('scale_colour_identity', scale_color_identity)
