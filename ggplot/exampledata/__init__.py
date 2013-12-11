import pandas as pd
import matplotlib.image as mpimg
import os

__ALL__ = ["diamonds","mtcars","meat","pageviews"]
_ROOT = os.path.abspath(os.path.dirname(__file__))

diamonds = pd.read_csv(os.path.join(_ROOT, "diamonds.csv"))
mtcars = pd.read_csv(os.path.join(_ROOT, "mtcars.csv"))
meat = pd.read_csv(os.path.join(_ROOT, "meat.csv"), parse_dates=[0])
pageviews = pd.read_csv(os.path.join(_ROOT, "pageviews.csv"), parse_dates=[0])
