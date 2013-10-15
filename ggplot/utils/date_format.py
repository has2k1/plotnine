#!/usr/bin/env python
# -*- coding: utf-8 -*-
from matplotlib.dates import DateFormatter

def date_format(format='%Y-%m-%d'):
    """
    "Formatted dates."

    Arguments:
        format => Date format using standard strftime format.

    Example:
        date_format('%b-%y')
        date_format('%B %d, %Y')
    """
    return DateFormatter(format)
