# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import os

import pandas as pd
from pandas.api.types import CategoricalDtype

__all__ = ['diamonds', 'economics', 'economics_long',
           'midwest', 'mpg', 'msleep', 'presidential',
           'seals', 'txhousing', 'luv_colours',
           'faithfuld',
           # extras for backward compatibility!
           'huron', 'meat', 'mtcars', 'pageviews']

__all__ = [str(u) for u in __all__]
_ROOT = os.path.abspath(os.path.dirname(__file__))

mtcars = pd.read_csv(os.path.join(_ROOT, 'mtcars.csv'))
meat = pd.read_csv(os.path.join(_ROOT, 'meat.csv'), parse_dates=[0])
pageviews = pd.read_csv(os.path.join(_ROOT, 'pageviews.csv'), parse_dates=[0])
huron = pd.read_csv(os.path.join(_ROOT, 'huron.csv'))
seals = pd.read_csv(os.path.join(_ROOT, 'seals.csv'))
economics = pd.read_csv(os.path.join(_ROOT, 'economics.csv'), parse_dates=[0])
economics_long = pd.read_csv(os.path.join(_ROOT, 'economics_long.csv'),
                             parse_dates=[0])
presidential = pd.read_csv(os.path.join(_ROOT, 'presidential.csv'),
                           parse_dates=[1, 2])
txhousing = pd.read_csv(os.path.join(_ROOT, 'txhousing.csv'))
luv_colours = pd.read_csv(os.path.join(_ROOT, 'luv_colours.csv'))
faithfuld = pd.read_csv(os.path.join(_ROOT, 'faithfuld.csv'))


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
        df[col] = df[col].astype(CategoricalDtype(cats, ordered=True))
    return df


def _unordered_categories(df, columns):
    """Make the columns in df categorical"""
    for col in columns:
        df[col] = df[col].astype(CategoricalDtype(ordered=False))
    return df


diamonds = pd.read_csv(os.path.join(_ROOT, 'diamonds.csv'))
categories = {
    'cut': ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal'],
    'clarity': ['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF'],
    'color': ['D', 'E', 'F', 'G', 'H', 'I', 'J']}
diamonds = _ordered_categories(diamonds, categories)

midwest = pd.read_csv(os.path.join(_ROOT, 'midwest.csv'))
midwest = _unordered_categories(midwest, ['category'])

mpg = pd.read_csv(os.path.join(_ROOT, 'mpg.csv'))
columns = ['manufacturer', 'model', 'trans', 'fl', 'drv', 'class']
mpg = _unordered_categories(mpg, columns)

msleep = pd.read_csv(os.path.join(_ROOT, 'msleep.csv'))
msleep = _unordered_categories(msleep, ['vore', 'conservation'])


# Documentation

mtcars.__doc__ = """
Motor Trend Car Road Tests

.. rubric:: Description

The data was extracted from the 1974 *Motor Trend* US magazine,
and comprises fuel consumption and 10 aspects of automobile
design and performance for 32 automobiles (1973–74 models).


.. rubric:: Format

A data frame with 32 observations on 11 variables.

======  =========================================
Column  Description
======  =========================================
mpg     Miles/(US) gallon
cyl     Number of cylinders
disp    Displacement (cu.in.)
hp      Gross horsepower
drat    Rear axle ratio
wt      Weight (1000 lbs)
qsec    1/4 mile time
vs      V/S
am      Transmission (0 = automatic, 1 = manual)
gear    Number of forward gears
carb    Number of carburetors
======  =========================================

.. rubric:: Source

Henderson and Velleman (1981), Building multiple regression
models interactively. *Biometrics*, **37**, 391–411.
"""

meat.__doc__ = """

"""

pageviews.__doc__ = """
"""

huron.__doc__ = """
Level of Lake Huron 1875–1972

.. rubric:: Description

Annual measurements of the level, in feet, of Lake Huron 1875–1972.

.. rubric:: Format

=========   ==============
Column      Description
=========   ==============
year        Year
level       Water level
decade      Decade
=========   ==============

.. rubric:: Source

Brockwell, P. J. and Davis, R. A. (1991). Time Series and Forecasting Methods.
Second edition. Springer, New York. Series A, page 555.

Brockwell, P. J. and Davis, R. A. (1996). Introduction to Time Series and
Forecasting. Springer, New York. Sections 5.1 and 7.6.
"""

seals.__doc__ = """
Vector field of seal movements.

.. rubric:: Description

This vector field was produced from the data described in Brillinger,
D.R., Preisler, H.K., Ager, A.A. and Kie, J.G.
"An exploratory data analysis (EDA) of the paths of moving animals". J.
Statistical Planning and Inference 122 (2004), 43-63, using the methods
of Brillinger, D.R., "Learning a potential function from a trajectory",
Signal Processing Letters. December (2007).

.. rubric:: Format

A data frame with 1155 rows and 4 variables

===========  ===================
Column       Description
===========  ===================
lat          Latitude
long         Longitude
delta_long   Change in Longitude
delta_lat    Change in Latitude
===========  ===================

.. rubric:: References

http://www.stat.berkeley.edu/~brill/Papers/jspifinal.pdf
"""

economics.__doc__ = """
US economic time series.

.. rubric:: Description

This dataset was produced from US economic time series data available
from http://research.stlouisfed.org/fred2.
`economics` is in "wide" format, `economics_long` is in "long" format.

.. rubric:: Format

A data frame with 478 rows and 6 variables

=========  ==========================================================
Column     Description
=========  ==========================================================
date       Month of data collection
psavert    personal savings rate [1_]
pce        personal consumption expenditures, in billions of dollars [2_]
unemploy   number of unemployed in thousands, [3_]
uempmed    median duration of unemployment, in week [4_]
pop        total population, in thousands [5_]
=========  ==========================================================

.. _1: http://research.stlouisfed.org/fred2/series/PSAVERT/
.. _2: http://research.stlouisfed.org/fred2/series/PCE
.. _3: http://research.stlouisfed.org/fred2/series/UNEMPLOY
.. _4: http://research.stlouisfed.org/fred2/series/UEMPMED
.. _5: http://research.stlouisfed.org/fred2/series/POP
"""

economics_long.__doc__ = economics.__doc__

presidential.__doc__ = """
Terms of 11 presidents from Eisenhower to Obama.

.. rubric:: Description

The names of each president, the start and end date
of their term, and their party of 11 US presidents
from Eisenhower to Obama.

==========     ===========================
Column         Description
==========     ===========================
name           Name of president
start          Start of presidential term
end            End of presidential term
party          Political Party
==========     ===========================

.. rubric:: Format

A data frame with 11 rows and 4 variables
"""

txhousing.__doc__ = """
Housing sales in TX.

.. rubric:: Description

Information about the housing market in Texas provided
by the TAMU real estate center, http://recenter.tamu.edu/.


.. rubric:: Format

A data frame with 8602 observations and 9 variables:

=========   ===============================================
Column      Description
=========   ===============================================
city        Name of MLS area
year        Year
month       Month
sales       Number of sales
volume      Total value of sales
median      Median sale price
listings    Total active listings
inventory   "Months inventory": amount of time it would \n
            take to sell all current listings at current \n
            pace of sales.
date        Date
=========   ===============================================
"""

luv_colours.__doc__ = """
colors in Luv space.

.. rubric:: Description

Named colors translated into Luv colour space.

luv_colours
.. rubric:: Format

A data frame with 657 observations and 4 variables:

======  ============================
Column  Description
======  ============================
L       L position in Luv colour space
u       u position in Luv colour space
v       v position in Luv colour space
col     Colour name
======  ============================
"""

faithfuld.__doc__ = """
Old Faithful Geyser Data

.. rubric:: Description

Waiting time between eruptions and the duration of the
eruption for the Old Faithful geyser in Yellowstone
National Park, Wyoming, USA.

.. rubric:: Format

A data frame with 272 observations on 2 variables.

==========   ========================================
Column       Description
==========   ========================================
eruptions    Eruption time in mins
waiting	     Waiting time to next eruption (in mins)
==========   ========================================

.. rubric:: Details

A closer look at `faithful.eruptions` reveals that these are
heavily rounded times originally in seconds, where multiples
of 5 are more frequent than expected under non-human measurement.
For a better version of the eruption times, see the example below.

There are many versions of this dataset around:
Azzalini and Bowman (1990) use a more complete version.

.. rubric:: Source

W. Härdle.

.. rubric:: References

Härdle, W. (1991) *Smoothing Techniques with Implementation in S*.
New York: Springer.

Azzalini, A. and Bowman, A. W. (1990). A look at some data
on the Old Faithful geyser. **Applied Statistics** *39*, 357–365.
"""

diamonds.__doc__ = """
Prices of 50,000 round cut diamonds

.. rubric:: Description

A dataset containing the prices and other attributes
of almost 54,000 diamonds. The variables are as follows:

.. rubric:: Format

A data frame with 53940 rows and 10 variables:

========  ==================================
Column    Description
========  ==================================
price     price in US dollars ($326–$18,823)
carat     weight of the diamond (0.2–5.01)
cut       quality of the cut (Fair, Good, Very Good, Premium, Ideal)
color     diamond colour, from J (worst) to D (best)
clarity   a measurement of how clear the diamond is \n
          (I1 (worst), SI1, SI2, VS1, VS2, VVS1, VVS2, IF (best))
x         length in mm (0–10.74)
y         width in mm (0–58.9)
z         depth in mm (0–31.8)
depth     total depth percentage = z / mean(x, y) = 2 * z / (x + y) (43–79)
table     width of top of diamond relative to widest point (43–95)
========  ==================================
"""

midwest.__doc__ = """
Midwest demographics.

.. rubric:: Description

Demographic information of midwest counties

.. rubric:: Format

A data frame with 437 rows and 28 variables

=====================  ============================
Column                 Description
=====================  ============================
PID
county
state
area
poptotal               Total population
popdensity             Population density
popwhite               Number of whites
popblack               Number of blacks
popamerindian          Number of American Indians
popasian               Number of Asians
popother               Number of other races
percwhite              Percent white
percblack              Percent black
percamerindan          Percent American Indian
percasian              Percent Asian
percother              Percent other races
popadults              Number of adults
perchsd
percollege             Percent college educated
percprof               Percent profession
poppovertyknown
percpovertyknown
percbelowpoverty
percchildbelowpovert
percadultpoverty
percelderlypoverty
inmetro                In a metro area
category
=====================  ============================
"""

mpg.__doc__ = """
Fuel economy data from 1999 and 2008 for 38 popular models of car

.. rubric:: Description

This dataset contains a subset of the fuel economy data that
the EPA makes available on http://fueleconomy.gov.
It contains only models which had a new release every year
between 1999 and 2008 - this was used as a proxy for
the popularity of the car.

.. rubric:: Format

A data frame with 234 rows and 11 variables

============   ====================================================
Column         Description
============   ====================================================
manufacturer
model
displ          engine displacement, in litres
year
cyl            number of cylinders
trans          type of transmission
drv            f = front-wheel drive, r = rear wheel drive, 4 = 4wd
cty            city miles per gallon
hwy            highway miles per gallon
fl
class
============   ====================================================
"""

msleep.__doc__ = """
An updated and expanded version of the mammals sleep dataset.

.. rubric:: Description

This is an updated and expanded version of the mammals
sleep dataset. Updated sleep times and weights were taken
from V. M. Savage and G. B. West. A quantitative, theoretical
framework for understanding mammalian sleep. Proceedings of
the National Academy of Sciences, 104 (3):1051-1056, 2007.

.. rubric:: Format

A data frame with 83 rows and 11 variables

=============  =====================================
Column         Description
=============  =====================================
name           common name
genus
vore           carnivore, omnivore or herbivore?
order
conservation   the conservation status of the animal
sleep_total    total amount of sleep, in hours
sleep_rem      rem sleep, in hours
sleep_cycle    length of sleep cycle, in hours
awake          amount of time spent awake, in hours
brainwt        brain weight in kilograms
bodywt         body weight in kilograms
=============  =====================================

.. rubric:: Details

Additional variables order, conservation status and
vore were added from wikipedia.
"""
