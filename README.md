# {ggplot} from [Yhat](http://yhathq.com)
```
from ggplot import *

ggplot(aes(x='date', y='beef'), data=meat) + \
    geom_point(color='lightblue') + \
    geom_line(alpha=0.25) + \
    stat_smooth(span=.05, color='black') + \
    ggtitle("Beef: It's What's for Dinner") + \
    xlab("Date") + \
    ylab("Head of Cattle Slaughtered")
```
<img src="public/img/ggplot_demo_beef.png" style="max-height: 300px">

### What is it?
Yes, it's another implementation of [`ggplot2`](https://github.com/hadley/ggplot2). One of the biggest reasons why I continue to reach for `R` instead of `Python` for data analysis is the lack of an easy to use, high level plotting package like `ggplot`. I've tried other libraries like `Bockah` and `d3py` but what I really want is `ggplot2`.

`ggplot` is just that. It's an extremely un-pythonic package for doing exactly what `ggplot2` does. The goal of the package is to mimic the `ggplot2` API. This makes it super easy for people coming over from `R` to use, and prevents you from having to re-learn how to plot stuff.

### Goals
- same API as `ggplot2` for `R`
- tight integration with [`pandas`](https://github.com/pydata/pandas)
- pip installable
- never use matplotlib again

### Getting Started
#### Dependencies
- `matplotlib`
- `pandas`
- `numpy`
- `scipy`
- `statsmodels`

#### Installation

    # matplotlibrc from Huy Nguyen (http://www.huyng.com/posts/sane-color-scheme-for-matplotlib/)
    $ curl https://github.com/yhat/ggplot/raw/master/matplotlibrc.zip > matplotlibrc.zip 
    $ unzip matplotlibrc.zip -d ~/
    # install ggplot using pip
    $ pip install ggplot

#### Loading `ggplot`

    # run an Ipython shell (or don't)
    $ ipython
    In [1]: from ggplot import *
That's it! You're ready to go!

### Examples
```
meat_lng = pd.melt(meat[['date', 'beef', 'pork', 'broilers']], id_vars='date')
ggplot(aes(x='date', y='value', colour='variable'), data=meat_lng) + \
    geom_point() + \
    stat_smooth()
```
<img src="public/img/ggplot_meat.png">

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

####`geom_density`
```
ggplot(diamonds, aes(x='price', color='cut')) + \
    geom_density()
```
<img src="public/img/geom_density_example.png">

####`geom_bar`
```
p = ggplot(mtcars, aes('cyl'))
p + geom_bar()
```
<img src="public/img/mtcars_geom_bar_cyl.png">


### TODO
see [TODO](https://github.com/yhat/ggplot/blob/master/TODO.md)
