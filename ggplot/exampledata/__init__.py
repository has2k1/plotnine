from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd
import os

__all__ = ['diamonds', 'economics', 'midwest', 'movies',
           'mpg', 'msleep', 'presidential', 'seals',
           # extras for backward compatibility!
           'meat', 'mtcars', 'pageviews']

__all__ = [str(u) for u in __all__]
_ROOT = os.path.abspath(os.path.dirname(__file__))

mtcars = pd.read_csv(os.path.join(_ROOT, 'mtcars.csv'))
meat = pd.read_csv(os.path.join(_ROOT, 'meat.csv'), parse_dates=[0])
pageviews = pd.read_csv(os.path.join(_ROOT, 'pageviews.csv'), parse_dates=[0])
huron = pd.read_csv(os.path.join(_ROOT, 'huron.csv'))
seals = pd.read_csv(os.path.join(_ROOT, 'seals.csv'))
economics = pd.read_csv(os.path.join(_ROOT, 'economics.csv'), parse_dates=[0])
presidential = pd.read_csv(os.path.join(_ROOT, 'presidential.csv'),
                           parse_dates=[1, 2])


# add factors
def _ordered_categories(df, categories):
    """
    Make the columns in df categorical

    Parameters:
    -----------
    categories: dict
        Of the form {str: list},
        where the key the column name and the value is
        the ordered category list
    """
    for col, cats in categories.items():
        df[col] = df[col].astype('category', categories=cats, ordered=True)
    return df


def _unordered_categories(df, columns):
    """Make the columns in df categorical"""
    for col in columns:
        df[col] = df[col].astype('category', ordered=False)
    return df


diamonds = pd.read_csv(os.path.join(_ROOT, 'diamonds.csv'))
categories = {
    'cut': ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal'],
    'clarity': ['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF'],
    'color': ['D', 'E', 'F', 'G', 'H', 'I', 'J']}
diamonds = _ordered_categories(diamonds, categories)

movies = pd.read_csv(os.path.join(_ROOT, 'movies.csv'))
movies['mpaa'] = movies['mpaa'].astype('category')

midwest = pd.read_csv(os.path.join(_ROOT, 'midwest.csv'))
midwest = _unordered_categories(midwest, ['category'])

mpg = pd.read_csv(os.path.join(_ROOT, 'mpg.csv'))
columns = ['manufacturer', 'model', 'trans', 'fl', 'drv', 'class']
mpg = _unordered_categories(mpg, columns)

msleep = pd.read_csv(os.path.join(_ROOT, 'msleep.csv'))
msleep = _unordered_categories(msleep, ['vore', 'conservation'])
