# plotnine <img width="20%" align="right" src="https://github.com/has2k1/plotnine/blob/logos/doc/images/logo-512.png?raw=true">

[![Release](https://img.shields.io/pypi/v/plotnine.svg)](https://pypi.python.org/pypi/plotnine)
[![License](https://img.shields.io/pypi/l/plotnine.svg)](https://pypi.python.org/pypi/plotnine)
[![DOI](https://zenodo.org/badge/89276692.svg)](https://zenodo.org/badge/latestdoi/89276692)
[![Build Status](https://github.com/has2k1/plotnine/workflows/build/badge.svg?branch=main)](https://github.com/has2k1/plotnine/actions?query=branch%3Amain+workflow%3A%22build%22)
[![Coverage](https://codecov.io/github/has2k1/plotnine/coverage.svg?branch=main)](https://codecov.io/github/has2k1/plotnine?branch=main)

plotnine is an implementation of a *grammar of graphics* in Python
based on [ggplot2](https://github.com/tidyverse/ggplot2).
The grammar allows you to compose plots by explicitly mapping variables in a
dataframe to the visual characteristics (position, color, size etc.) of objects that make up the plot.

Plotting with a *grammar of graphics* is powerful. Custom (and otherwise
complex) plots are easy to think about and build incrementally, while the
simple plots remain simple to create.

To learn more about how to use plotnine, check out the
[documentation](https://plotnine.org). Since plotnine
has an API similar to ggplot2, where it lacks in coverage the
[ggplot2 documentation](http://ggplot2.tidyverse.org/reference/index.html)
may be helpful.


## Example

```python
from plotnine import *
from plotnine.data import mtcars
```

Building a complex plot piece by piece.

1. Scatter plot

   ```python
   (
       ggplot(mtcars, aes("wt", "mpg"))
       + geom_point()
   )
   ```

   <img width="90%" align="center" src="https://github.com/has2k1/plotnine/blob/logos/doc/images/readme-image-1.png?raw=true">

2. Scatter plot colored according some variable

   ```python
   (
       ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
       + geom_point()
   )
   ```

   <img width="90%" align="center" src="https://github.com/has2k1/plotnine/blob/logos/doc/images/readme-image-2.png?raw=true">

3. Scatter plot colored according some variable and
   smoothed with a linear model with confidence intervals.

   ```python
   (
       ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
       + geom_point()
       + stat_smooth(method="lm")
   )
   ```

   <img width="90%" align="center" src="https://github.com/has2k1/plotnine/blob/logos/doc/images/readme-image-3.png?raw=true">

4. Scatter plot colored according some variable,
   smoothed with a linear model with confidence intervals and
   plotted on separate panels.

   ```python
   (
       ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
       + geom_point()
       + stat_smooth(method="lm")
       + facet_wrap("gear")
   )
   ```

   <img width="90%" align="center" src="https://github.com/has2k1/plotnine/blob/logos/doc/images/readme-image-4.png?raw=true">

5. Adjust the themes


   I) Make it playful

   ```python
   (
       ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
       + geom_point()
       + stat_smooth(method="lm")
       + facet_wrap("gear")
       + theme_xkcd()
   )
   ```

   <img width="90%" align="center" src="https://github.com/has2k1/plotnine/blob/logos/doc/images/readme-image-5.png?raw=true">

   II) Or professional

   ```python
   (
       ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
       + geom_point()
       + stat_smooth(method="lm")
       + facet_wrap("gear")
       + theme_tufte()
   )
   ```

   <img width="90%" align="center" src="https://github.com/has2k1/plotnine/blob/logos/doc/images/readme-image-5alt.png?raw=true">

## Installation

Official release

```console
# Using pip
$ pip install plotnine             # 1. should be sufficient for most
$ pip install 'plotnine[extra]'    # 2. includes extra/optional packages
$ pip install 'plotnine[test]'     # 3. testing
$ pip install 'plotnine[doc]'      # 4. generating docs
$ pip install 'plotnine[dev]'      # 5. development (making releases)
$ pip install 'plotnine[all]'      # 6. everything

# Or using conda
$ conda install -c conda-forge plotnine
```

Development version

```console
$ pip install git+https://github.com/has2k1/plotnine.git
```

## Contributing

Our documentation could use some examples, but we are looking for something
a little bit special. We have two criteria:

1. Simple looking plots that otherwise require a trick or two.
2. Plots that are part of a data analytic narrative. That is, they provide
   some form of clarity showing off the `geom`, `stat`, ... at their
   differential best.

If you come up with something that meets those criteria, we would love to
see it. See [plotnine-examples](https://github.com/has2k1/plotnine-examples).

If you discover a bug checkout the [issues](https://github.com/has2k1/plotnine/issues)
if it has not been reported, yet please file an issue.

And if you can fix a bug, your contribution is welcome.

Testing
-------

Plotnine has tests that generate images which are compared to baseline images known
to be correct. To generate images that are consistent across all systems you have
to install matplotlib from source. You can do that with ``pip`` using the command.

```console
$ pip install matplotlib --no-binary matplotlib
```

Otherwise there may be small differences in the text rendering that throw off the
image comparisons.
