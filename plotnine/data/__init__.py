"""
Plotnine Data
"""

from pathlib import Path

import pandas as pd
from pandas.api.types import CategoricalDtype

__all__ = (
    "anscombe_quartet",
    "diamonds",
    "economics",
    "economics_long",
    "faithful",
    "faithfuld",
    "huron",
    "luv_colours",
    "meat",
    "midwest",
    "mpg",
    "msleep",
    "mtcars",
    "pageviews",
    "penguins",
    "presidential",
    "seals",
    "txhousing",
)

DATA_DIR = Path(__file__).parent

mtcars = pd.read_csv(DATA_DIR / "mtcars.csv")
meat = pd.read_csv(DATA_DIR / "meat.csv", parse_dates=[0])
pageviews = pd.read_csv(DATA_DIR / "pageviews.csv", parse_dates=[0])
huron = pd.read_csv(DATA_DIR / "huron.csv")
seals = pd.read_csv(DATA_DIR / "seals.csv")
economics = pd.read_csv(DATA_DIR / "economics.csv", parse_dates=[0])
economics_long = pd.read_csv(DATA_DIR / "economics_long.csv", parse_dates=[0])
presidential = pd.read_csv(DATA_DIR / "presidential.csv", parse_dates=[1, 2])
txhousing = pd.read_csv(DATA_DIR / "txhousing.csv")
penguins = pd.read_csv(DATA_DIR / "penguins.csv")
luv_colours = pd.read_csv(DATA_DIR / "luv_colours.csv")
faithfuld = pd.read_csv(DATA_DIR / "faithfuld.csv")
faithful = pd.read_csv(DATA_DIR / "faithful.csv")
anscombe_quartet = pd.read_csv(DATA_DIR / "anscombe-quartet.csv")

# For convenience to the user, we set some columns in these
# dataframes to categoricals.
diamonds = pd.read_csv(DATA_DIR / "diamonds.csv")
midwest = pd.read_csv(DATA_DIR / "midwest.csv")
mpg = pd.read_csv(DATA_DIR / "mpg.csv")
msleep = pd.read_csv(DATA_DIR / "msleep.csv")


# add factors
def _ordered_categories(df, categories):
    """
    Make the columns in df categorical

    Parameters
    ----------
    df : pd.Dataframe
        Dataframe
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


def _process_categories():
    """
    Set columns in some of the dataframes to categoricals
    """
    global diamonds, penguins
    diamonds = _ordered_categories(
        diamonds,
        {
            "cut": ["Fair", "Good", "Very Good", "Premium", "Ideal"],
            "clarity": [
                "I1",
                "SI2",
                "SI1",
                "VS2",
                "VS1",
                "VVS2",
                "VVS1",
                "IF",
            ],
            "color": list("DEFGHIJ"),
        },
    )
    penguins = _unordered_categories(penguins, ["species", "island", "sex"])


_process_categories()


# Documentation

mtcars.__doc__ = """
Motor Trend Car Road Tests

## Description

The data was extracted from the 1974 *Motor Trend* US magazine,
and comprises fuel consumption and 10 aspects of automobile
design and performance for 32 automobiles (1973–74 models).

## Format

A data frame with 32 observations on 11 variables.

| Column | Description                              |
|--------|------------------------------------------|
| mpg    | Miles/(US) gallon                        |
| cyl    | Number of cylinders                      |
| disp   | Displacement (cu.in.)                    |
| hp     | Gross horsepower                         |
| drat   | Rear axle ratio                          |
| wt     | Weight (1000 lbs)                        |
| qsec   | 1/4 mile time                            |
| vs     | V/S                                      |
| am     | Transmission (0 = automatic, 1 = manual) |
| gear   | Number of forward gears                  |
| carb   | Number of carburetors                    |

## Source

Henderson and Velleman (1981), Building multiple regression
models interactively. *Biometrics*, **37**, 391–411.
"""

meat.__doc__ = """
US Meat Production

Description**

Monthly production weight of red meat and poultry. The values are in
units of 1 million lbs.

| Column            | Description           |
|-------------------|-----------------------|
| date              | Month of the year     |
| beef              | Beef weight           |
| veal              | Veal weight           |
| pork              | Pork weight           |
| lamb_and_mutton   | Lamb & Mutton weight  |
| broilers          | Broiler weight        |
| other_chicken     | Other Chicken weight  |
| turkey            | Turkey weight         |

## Source

[Livestock and Meat Dosmestic Data]\
(https://www.ers.usda.gov/data-products/livestock-and-meat-domestic-data/)
from the Economic Research Service of the U.S. DEPARTMENT OF AGRICULTURE.

"""

pageviews.__doc__ = """
"""

huron.__doc__ = """
Level of Lake Huron 1875–1972

Description**

Annual measurements of the level, in feet, of Lake Huron 1875–1972.

## Format

| Column | Description |
|--------|-------------|
| year   | Year        |
| level  | Water level |
| decade | Decade      |

Source**

Brockwell, P. J. and Davis, R. A. (1991). Time Series and Forecasting Methods.
Second edition. Springer, New York. Series A, page 555.

Brockwell, P. J. and Davis, R. A. (1996). Introduction to Time Series and
Forecasting. Springer, New York. Sections 5.1 and 7.6.
"""

seals.__doc__ = """
Vector field of seal movements.

## Description

This vector field was produced from the data described in Brillinger,
D.R., Preisler, H.K., Ager, A.A. and Kie, J.G.
"An exploratory data analysis (EDA) of the paths of moving animals". J.
Statistical Planning and Inference 122 (2004), 43-63, using the methods
of Brillinger, D.R., "Learning a potential function from a trajectory",
Signal Processing Letters. December (2007).

## Format

A data frame with 1155 rows and 4 variables

| Column     | Description         |
|------------|---------------------|
| lat        | Latitude            |
| long       | Longitude           |
| delta_long | Change in Longitude |
| delta_lat  | Change in Latitude  |

## References

<http://www.stat.berkeley.edu/~brill/Papers/jspifinal.pdf>
"""

economics.__doc__ = """
US economic time series.

## Description

This dataset was produced from US economic time series data available
from http://research.stlouisfed.org/fred2.
`economics` is in "wide" format, `economics_long` is in "long" format.

## Format

A data frame with 478 rows and 6 variables

| Column   | Description                                                    |
|----------|----------------------------------------------------------------|
| date     | Month of data collection                                       |
| psavert  | personal savings rate [^1]                                     |
| pce      | personal consumption expenditures, in billions of dollars [^2] |
| unemploy | number of unemployed in thousands [^3]                         |
| uempmed  | median duration of unemployment, in week [^4]                  |
| pop      | total population, in thousands [^5]                            |

[^1]: <http://research.stlouisfed.org/fred2/series/PSAVERT>
[^2]: <http://research.stlouisfed.org/fred2/series/PCE>
[^3]: <http://research.stlouisfed.org/fred2/series/UNEMPLOY>
[^4]: <http://research.stlouisfed.org/fred2/series/UEMPMED>
[^5]: <http://research.stlouisfed.org/fred2/series/POP>
"""

economics_long.__doc__ = economics.__doc__

penguins.__doc__ = """
Palmer Penguins

## Description

Data about 3 different species of penguins collected from 3 islands
in the Palmer Archipelago, Antarctica.

## Format

A dataframe with 344 rows and 8 variables

+--------------------+------------------------------------------------+
| Column             | Description                                    |
+====================+================================================+
| species            | Penguin species (Adélie, Chinstrap and Gentoo) |
+--------------------+------------------------------------------------+
| island             | Island in Palmer Archipelago, Antarctica       |
|                    | (Biscoe, Dream or Torgersen)                   |
+--------------------+------------------------------------------------+
| bill_length_mm     | Bill length (millimeters)                      |
+--------------------+------------------------------------------------+
| bill_depth_mm      | Bill depth (millimeters)                       |
+--------------------+------------------------------------------------+
| flipper_length_mm  | Flipper length (millimeters)                   |
+--------------------+------------------------------------------------+
| body_mass_g        | Body mass (grams)                              |
+--------------------+------------------------------------------------+
| sex                | Penguin sex (female, male)                     |
+--------------------+------------------------------------------------+
| year               | The study year (2007, 2008, or 2009)           |
+--------------------+------------------------------------------------+

## Source

Collected by [Dr. Kristen Gorman]\
(https://www.uaf.edu/cfos/people/faculty/detail/kristen-gorman.php)
and the [Palmer Station, Antarctica LTER](https://pallter.marine.rutgers.edu/).

Made conveniently available by
[Alison Horst](https://github.com/allisonhorst/palmerpenguins/) to serve as
a dataset exploration and visualisation.
"""

presidential.__doc__ = """
Terms of 11 presidents from Eisenhower to Obama.

## Description

The names of each president, the start and end date
of their term, and their party of 11 US presidents
from Eisenhower to Obama.

## Format

A data frame with 11 rows and 4 variables

| Column | Description                |
|--------|----------------------------|
| name   | Name of president          |
| start  | Start of presidential term |
| end    | End of presidential term   |
| party  | Political Party            |

"""

txhousing.__doc__ = """
Housing sales in TX.

## Description

Information about the housing market in Texas provided
by the TAMU real estate center, http://recenter.tamu.edu/.

## Format

A data frame with 8602 observations and 9 variables:

+-----------+-----------------------------------------------+
| Column    | Description                                   |
+===========+===============================================+
| city      | Name of MLS area                              |
+-----------+-----------------------------------------------+
| year      | Year                                          |
+-----------+-----------------------------------------------+
| month     | Month                                         |
+-----------+-----------------------------------------------+
| sales     | Number of sales                               |
+-----------+-----------------------------------------------+
| volume    | Total value of sales                          |
+-----------+-----------------------------------------------+
| median    | Median sale price                             |
+-----------+-----------------------------------------------+
| listings  | Total active listings                         |
+-----------+-----------------------------------------------+
| inventory | "Months inventory": amount of time it would   |
|           | take to sell all current listings at current  |
|           | pace of sales.                                |
+-----------+-----------------------------------------------+
| date      | Date                                          |
+-----------+-----------------------------------------------+

"""

luv_colours.__doc__ = """
colors in Luv space.

## Description

Named colors translated into Luv colour space.

## Format

A data frame with 657 observations and 4 variables:

| Column | Description                    |
|--------|--------------------------------|
| L      | L position in Luv colour space |
| u      | u position in Luv colour space |
| v      | v position in Luv colour space |
| col    | Colour name                    |
"""

faithful.__doc__ = """
Old Faithful Geyser Data

## Description

Waiting time between eruptions and the duration of the
eruption for the Old Faithful geyser in Yellowstone
National Park, Wyoming, USA.

## Format

A data frame with 272 observations on 2 variables.

| Column    | Description                            |
|-----------|----------------------------------------|
| eruptions | Eruption time in mins                  |
| waiting W | aiting time to next eruption (in mins) |

## Details

A closer look at `faithful.eruptions` reveals that these are
heavily rounded times originally in seconds, where multiples
of 5 are more frequent than expected under non-human measurement.
For a better version of the eruption times, see the example below.

There are many versions of this dataset around:
Azzalini and Bowman (1990) use a more complete version.

## Source

W. Härdle.

## References

Härdle, W. (1991) *Smoothing Techniques with Implementation in S*.
New York: Springer.

Azzalini, A. and Bowman, A. W. (1990). A look at some data
on the Old Faithful geyser. **Applied Statistics** *39*, 357–365.
"""

faithfuld.__doc__ = """
Old Faithful Geyser Data

## Description

Waiting time between eruptions and the duration of the
eruption for the Old Faithful geyser in Yellowstone
National Park, Wyoming, USA.

## Format

A data frame with *grid data* for 272 observations on 2
variables and the density at those locations.

| Column    | Description                            |
|-----------|----------------------------------------|
| eruptions | Eruption time in mins                  |
| waiting W | aiting time to next eruption (in mins) |
| density D | ensity Estimate                        |

## Details

A closer look at `faithful.eruptions` reveals that these are
heavily rounded times originally in seconds, where multiples
of 5 are more frequent than expected under non-human measurement.
For a better version of the eruption times, see the example below.

There are many versions of this dataset around:
Azzalini and Bowman (1990) use a more complete version.

## Source

W. Härdle.

## References

Härdle, W. (1991) *Smoothing Techniques with Implementation in S*.
New York: Springer.

Azzalini, A. and Bowman, A. W. (1990). A look at some data
on the Old Faithful geyser. **Applied Statistics** *39*, 357–365.
"""

diamonds.__doc__ = """
Prices of 50,000 round cut diamonds

## Description

A dataset containing the prices and other attributes
of almost 54,000 diamonds. The variables are as follows:

## Format

A data frame with 53940 rows and 10 variables:

+----------+------------------------------------------------------------+
| Column   | Description                                                |
+==========+============================================================+
| price    | price in US dollars ($326–$18,823)                         |
+----------+------------------------------------------------------------+
| carat    | weight of the diamond (0.2–5.01)                           |
+----------+------------------------------------------------------------+
| cut      | quality of the cut (Fair, Good, Very Good, Premium, Ideal) |
+----------+------------------------------------------------------------+
| color    | diamond colour, from J (worst) to D (best)                 |
+----------+------------------------------------------------------------+
| clarity  | a measurement of how clear the diamond is                  |
|          | (I1 (worst), SI1, SI2, VS1, VS2, VVS1, VVS2, IF (best))    |
+----------+------------------------------------------------------------+
| x        | length in mm (0–10.74)                                     |
+----------+------------------------------------------------------------+
| y        | width in mm (0–58.9)                                       |
+----------+------------------------------------------------------------+
| z        | depth in mm (0–31.8)                                       |
+----------+------------------------------------------------------------+
| depth    | total depth percentage                                     |
|          | = z / mean(x, y) = 2 * z / (x + y) (43–79)                 |
+----------+------------------------------------------------------------+
| table    | width of top of diamond relative to widest point (43–95)   |
+----------+------------------------------------------------------------+
"""

midwest.__doc__ = """
Midwest demographics.

## Description

Demographic information of midwest counties

## Format

A data frame with 437 rows and 28 variables

|Column                | Description                  |
|----------------------|------------------------------|
|PID                   |                              |
|county                |                              |
|state                 |                              |
|area                  |                              |
|poptotal              | Total population             |
|popdensity            | Population density           |
|popwhite              | Number of whites             |
|popblack              | Number of blacks             |
|popamerindian         | Number of American Indians   |
|popasian              | Number of Asians             |
|popother              | Number of other races        |
|percwhite             | Percent white                |
|percblack             | Percent black                |
|percamerindan         | Percent American Indian      |
|percasian             | Percent Asian                |
|percother             | Percent other races          |
|popadults             | Number of adults             |
|perchsd               |                              |
|percollege            | Percent college educated     |
|percprof              | Percent profession           |
|poppovertyknown       |                              |
|percpovertyknown      |                              |
|percbelowpoverty      |                              |
|percchildbelowpovert  |                              |
|percadultpoverty      |                              |
|percelderlypoverty    |                              |
|inmetro               | In a metro area              |
|category              |                              |
"""

mpg.__doc__ = """
Fuel economy data from 1999 and 2008 for 38 popular models of car

## Description

This dataset contains a subset of the fuel economy data that
the EPA makes available on http://fueleconomy.gov.
It contains only models which had a new release every year
between 1999 and 2008 - this was used as a proxy for
the popularity of the car.

## Format

A data frame with 234 rows and 11 variables

+--------------+---------------------------------+
| Column       | Description                     |
+==============+=================================+
| manufacturer |                                 |
+--------------+---------------------------------+
| model        |                                 |
+--------------+---------------------------------+
| displ        | engine displacement, in litres  |
+--------------+---------------------------------+
| year         |                                 |
+--------------+---------------------------------+
| cyl          | number of cylinders             |
+--------------+---------------------------------+
| trans        | type of transmission            |
+--------------+---------------------------------+
| drv          | f = front-wheel drive           |
|              | r = rear wheel drive            |
|              | 4 = 4wd                         |
+--------------+---------------------------------+
| cty          | city miles per gallon           |
+--------------+---------------------------------+
| hwy          | highway miles per gallon        |
+--------------+---------------------------------+
| fl           |                                 |
+--------------+---------------------------------+
| class        |                                 |
+--------------+---------------------------------+
"""

msleep.__doc__ = """
An updated and expanded version of the mammals sleep dataset.

## Description

This is an updated and expanded version of the mammals
sleep dataset. Updated sleep times and weights were taken
from V. M. Savage and G. B. West. A quantitative, theoretical
framework for understanding mammalian sleep. Proceedings of
the National Academy of Sciences, 104 (3):1051-1056, 2007.

## Format

A data frame with 83 rows and 11 variables

| Column       | Description                           |
|--------------|---------------------------------------|
| name genus   | common name                           |
| vore order   | carnivore, omnivore or herbivore?     |
| conservation | the conservation status of the animal |
| sleep_total  | total amount of sleep, in hours       |
| sleep_rem    | rem sleep, in hours                   |
| sleep_cycle  | length of sleep cycle, in hours       |
| awake        | amount of time spent awake, in hours  |
| brainwt      | brain weight in kilograms             |
| bodywt       | body weight in kilograms              |

## Details

Additional variables order, conservation status and
vore were added from wikipedia.
"""

anscombe_quartet.__doc__ = """
Anscombe's Quartet

## Description

A dataset by Statistician Francis Anscombe that challenged the commonly held
belief that "numerical calculations are exact, but graphs are rough"
(Anscombe, 1973). 

It comprises of 4 (the quartet!) small sub-datasets, each with 11 points that
have different distributions but nearly identical descriptive statistics.
It is perhaps the best argument for visualising data.

## Format

A dataframe with 44 rows and 3 variables

| Column       | Description                           |
|--------------|---------------------------------------|
| dataset      | The Dataset                           |
| x            | x                                     |
| y            | y                                     |

## References

Anscombe, F. J. (1973). "Graphs in Statistical Analysis".
American Statistician. 27 (1): 17–21.
"""
