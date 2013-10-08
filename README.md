# {ggplot}

<img src="public/img/ggplot_demo_beef.png" style="max-height: 300px">

### What is it?
Yes, it's another implementation of [`ggplot2`](https://github.com/hadley/ggplot2). One of the biggest reasons why I continue to reach for `R` instead of `Python` for data analysis is the lack of an easy to use, high level plotting package like `ggplot`. I've tried other libraries like `Bockah` and `d3py` but what I really want is `ggplot2`.

`ggplot` is just that. It's an extremely un-pythonic package for doing exactly what `ggplot2` does. The goal of the package is to mimic the `ggplot2` API. This makes it super easy for people coming over from `R` to use, and prevents you from having to re-learn how to plot stuff.

### Goals
- same API as `ggplot2` for `R`
- tight integration with [`pandas`](https://github.com/pydata/pandas)
- pip installable

### Getting Started
    # unzip the matplotlibrc
    $ unzip matplotlibrc.zip ~/
    $ pip install ggplot

### Examples
####`geom_point`
```
from ggplot import *
ggplot(diamonds, aes('carat', 'price')) + \
    geom_point(alpha=1/20.)
```
<img src="public/img/diamonds_geom_point_alpha.png">

####`geom_hist`
```
p = ggplot(aes(x='carat'), data=diamonds)
p + geom_hist() + ggtitle("Histogram of Diamond Carats") + labs("Carats", "Freq") 
```
<img src="public/img/diamonds_carat_hist.png">

####`geom_bar`
```
p = ggplot(mtcars, aes('cyl'))
p + geom_bar()
```
<img src="public/img/mtcars_geom_bar_cyl.png">


### TODO
- finish README
- add matplotlibrc to build script
- distribute on PyPi
- come up with better name
- handle NAs gracefully
- make `aes` guess what the user actually means (DONE)
- aes:
    - size
    - se for stat_smooth
    - fix fill/colour
- geoms:
    - geom_abline (DONE)
    - geom_area (DONE)
    - geom_bar (IN PROGRESS)
    - geom_boxplot
    - geom_hline (DONE)
    - geom_ribbon (same as geom_ribbon?)
    - geom_vline (DONE)
    - stat_bin2d (DONE)
    - geom_jitter
    - stat_smooth (bug)
- scales:
    - scale_colour_brewer
    - scale_colour_gradient
    - scale_colour_gradient2
    - scale_x_continuous
    - scale_x_discrete
    - scale_y_continuous
- facets:
    - facet_grid (DONE)

