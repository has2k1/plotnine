from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd
import os

__all__ = ["diamonds", "mtcars", "meat", "pageviews"]
__all__ = [str(u) for u in __all__]
_ROOT = os.path.abspath(os.path.dirname(__file__))

diamonds = pd.read_csv(os.path.join(_ROOT, "diamonds.csv"))
mtcars = pd.read_csv(os.path.join(_ROOT, "mtcars.csv"))
meat = pd.read_csv(os.path.join(_ROOT, "meat.csv"), parse_dates=[0])
movies = pd.read_csv(os.path.join(_ROOT, "movies.csv"))
pageviews = pd.read_csv(os.path.join(_ROOT, "pageviews.csv"), parse_dates=[0])
huron = pd.read_csv(os.path.join(_ROOT, "huron.csv"))

# add factors
diamonds['cut'] = pd.Categorical(diamonds['cut'])
diamonds['color'] = pd.Categorical(diamonds['color'])
diamonds['clarity'] = pd.Categorical(diamonds['clarity'])

diamonds['cut'].cat.reorder_categories(
    ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal'])
diamonds['clarity'].cat.reorder_categories(
    ['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF'])
diamonds['color'].cat.reorder_categories(
    ['D', 'E', 'F', 'G', 'H', 'I', 'J'])
