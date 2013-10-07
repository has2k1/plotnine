# y{et}a{nother}gg{plot}

### What is it?
Yes, it's another implementation of [`ggplot2`](https://github.com/hadley/ggplot2). One of the biggest reasons why I continue to reach for `R` instead of `Python` for data analysis is the lack of an easy to use, high level plotting package like `ggplot`. I've tried other libraries like `Bockah` and `d3py` but what I really want is `ggplot2`.

`yagg` is just that. It's an extremely un-pythonic package for doing exactly what `ggplot2` does. The goal of the package is to mimic the `ggplot2` API. This makes it super easy for people coming over from `R` to use, and prevents you from having to re-learn how to plot stuff.

### Goals
- same API as `ggplot2` for `R`
- tight integration with [`pandas`](https://github.com/pydata/pandas)
- pip installable

### Getting Started

    $ pip install yagg

### Examples

### TODO
- finish README
- geoms:
    - geom_abline
    - geom_bar
    - geom_boxplot
    - geom_hline
    - geom_vline
    - geom_ribbon
    - stat_bin2d
- scales:
    - scale_colour_brewer
    - scale_colour_gradient
    - scale_colour_gradient2
    - scale_x_continuous
    - scale_y_continuous
    - scale_x_discrete
- facets:
    - facet_grid
