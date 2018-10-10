from plotnine.scales.scale import scale
from plotnine.doctools import document


@document
class scale_expand(scale):
    """
    Expand

    Parameters
    ----------
    base_param_1 : int or float
        Base Param 1 Description
    base_param_2 : str
        Base Param 2 Description
    base_param_3 : dict
        Base Param 3 Description
    specific_parameter : str, optional
        Base Specific Parameter Description
    """


class mixin:
    """
    Expand

    Parameters
    ----------
    mixin_param_1 : int or float
        Mixin Param 1 Description
    mixin_param_2 : str
        Mixin Param 2 Description
    """


@document
class scale_expand_earth(mixin, scale_expand):
    """
    Expand Earth

    Parameters
    ----------
    {superclass_parameters}
    derived_param_1 : int or float
        Derived Param 1 Description
    derived_param_2: float
        Derived Param 2 Description
    specific_parameter : str
        Derived Specific Parameter Description
    """


def test_document_scale():
    doc = scale_expand_earth.__doc__
    assert doc.count('base_param_1') == 1
    assert doc.count('base_param_2') == 1
    assert doc.count('base_param_3') == 1
    assert doc.count('derived_param_1') == 1
    assert doc.count('derived_param_2') == 1
    assert doc.count('mixin_param_1') == 1
    assert doc.count('mixin_param_2') == 1

    # overridden parameter
    assert 'specific_parameter : str, optional' not in doc
    assert 'Base Specific Parameter Description' not in doc
    assert doc.count('specific_parameter : str') == 1
    assert doc.count('Derived Specific Parameter Description') == 1
