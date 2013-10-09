import pandas as pd
import os


_ROOT = os.path.abspath(os.path.dirname(__file__))

diamonds = pd.read_csv(os.path.join(_ROOT, "diamonds.csv"))
mtcars = pd.read_csv(os.path.join(_ROOT, "mtcars.csv"))
meat = pd.read_csv(os.path.join(_ROOT, "meat.csv"), parse_dates=[0]))

