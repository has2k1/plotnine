# ggplot

## Installation
#### Dependencies
I realize that these are not fun to install. My best luck has always been using brew if you're on a Mac or just using the binaries if you're on Windows. If you're using Linux then this should be relatively painless. You should be able to apt-get or yum all of these.
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
#### geom_area
#### geom_bar
#### geom_density
#### geom_hist
#### geom_hline
#### geom_jitter
#### geom_line
#### geom_point
#### geom_vline

## stats
#### stat_bin2d
#### stat_smooth


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




