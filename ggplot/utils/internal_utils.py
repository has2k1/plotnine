"""Internal helper methods for ggplot.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
from ggplot.components import colors, shapes

__ALL__ = ["build_df_from_transforms","is_identity"]

def build_df_from_transforms(data, aes)
    """Adds columns from the in aes included transformations
    
    Possible transformations are "factor(<col>)" and 
    expresions which can be used with eval.
    
    Parameters
    ----------
    data : DataFrame
        the original dataframe
    aes : aesthetics
        the aesthetic

    Returns
    -------
    data : DateFrame 
        Transformend DataFrame
    """
    for ae, name in aes.items():
        if name not in data and not is_identity(name):
            # Look for alias/lambda functions
            result = re.findall(r'(?:[A-Z])|(?:[A-Za_-z0-9]+)|(?:[/*+_=\(\)-])', name)
            if re.match("factor[(][A-Za-z_0-9]+[)]", name):
                m = re.search("factor[(]([A-Za-z_0-9]+)[)]", name)
                data[name] = data[m.group(1)].apply(str)
            else:
                lambda_column = ""
                for item in result:
                    if re.match("[/*+_=\(\)-]", item):
                        pass
                    elif re.match("^[0-9.]+$", item):
                        pass
                    else:
                        item = "data.get('%s')" % item
                    lambda_column += item
                data[name] = eval(lambda_column)
    return data

def is_identity(x):
    if x in colors.COLORS:
        return True
    elif x in shapes.SHAPES:
        return True
    elif isinstance(x, (float, int)):
        return True
    else:
        return False
   