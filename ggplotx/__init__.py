from __future__ import absolute_import

# This is the only place the version is specified and
# used in both setup.py and docs/conf.py to set the
# version of ggplotx.
__version__ = '0.1.0'

from .qplot import qplot
from .ggplot import ggplot
from .aes import *
from .labels import *
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

        from ggplotx import *

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

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
