# ggplot

## Installation
#### Dependencies
I realize that these are not fun to install. My best luck has always been using `brew` if you're on a Mac or just using the binaries if you're on Windows. If you're using Linux then this should be relatively painless. You should be able to `apt-get` or `yum` all of these.
- `scipy`
- `numpy`
- `matplotlib`
- `pandas`
- `statsmodels`

#### 

## Quickstart

    $ pip install ggplot
    $ ipython
    >>> from ggplot import *
    >>> p = ggplot(aes(x='wt', y='mpg', colour='factor(cyl)'), data=mtcars)
    >>> p + geom_point()

## Plotting

## geoms
#### geom_abline
###### Aesthetics
- `slope`
- `intercept`
- `linetype`
- `size`
- `color`
- `alpha`

- - -

#### geom_area
###### Aesthetics
- `x`
- `ymin`
- `ymax`
- `color`
- `alpha`

- - -

#### geom_bar
###### Aesthetics
- `x`
- `weight`
- `color`
- `fill`
- `alpha`

- - -

#### geom_density
###### Aesthetics
- `x`
- `weight`
- `color`
- `fill`
- `alpha`

- - -

#### geom_hist
###### Aesthetics
- `x`
- `color`
- `fill`
- `alpha`

- - -

#### geom_hline
###### Aesthetics
- `y`
- `xmin`
- `xmax`
- `color`
- `alpha`

- - -

#### geom_jitter

###### Aesthetics
- `jitter`

- - -

#### geom_line
###### Aesthetics
- `x`
- `y`
- `linetype`
- `color`
- `alpha`

- - -

#### geom_point
###### Aesthetics
- `x`
- `y`
- `size`
- `color`
- `shape`
- `alpha`

- - -

#### geom_vline
###### Aesthetics
- `x`
- `ymin`
- `ymax`
- `color`
- `alpha`

## stats
#### stat_bin2d
###### Aesthetics
- `x`
- `y`
- `alpha`

- - -

#### stat_smooth
###### Aesthetics
- `x`
- `y`
- `color`
- `alpha`
- `method` (`lm`, `lowess`, `ma`)

- - -

## scales

## faceting

## themes
####theme
####theme_bw
####theme_xkcd

## datasets

## plots
#### ggplot

## aesthetics
#### aes

## utils
#### ggsave




