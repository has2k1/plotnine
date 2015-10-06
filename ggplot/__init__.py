from __future__ import absolute_import

# For testing purposes we might need to set mpl backend before any
# other import of matplotlib.
def _set_mpl_backend():
    import os
    import matplotlib as mpl

    env_backend = os.environ.get('MATPLOTLIB_BACKEND')
    if env_backend:
        # we were instructed
        mpl.use(env_backend)

_set_mpl_backend()

# This is the only place the version is specified and
# used in both setup.py and docs/conf.py to set the
# version of ggplot.
__version__ = '0.6.6'

# from .qplot import qplot
from .ggplot import ggplot
from .components import *
from .coords import *
from .geoms import *
from .stats import *
from .scales import *
from .facets import *
from .themes import *
from .utils import *
from .positions import *
from .guides import *


def _get_all_imports():
    """
    Return list of all the imports

    This prevents sub-modules (geoms, stats, utils, ...)
    from being imported into the user namespace by the
    following import statement

        from ggplot import *

    This is because `from Module import Something`
    leads to `Module` itself coming into the namespace!!
    """
    import types
    lst = [name for name, obj in globals().items()
           if not (name.startswith('_') or
                   name == 'absolute_import' or
                   isinstance(obj, types.ModuleType))]
    return lst


__all__ = _get_all_imports()
