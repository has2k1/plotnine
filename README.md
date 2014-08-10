[![image](https://secure.travis-ci.org/yhat/ggplot.png?branch=master)](http://travis-ci.org/yhat/ggplot)

{ggplot} from [Yhat](http://yhathq.com)
=======================================

read more on our
[blog](http://blog.yhathq.com/posts/ggplot-for-python.html)

    from ggplot import *

    ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        ggtitle("Beef: It's What's for Dinner") + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")

![image](https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/ggplot_demo_beef.png)

What is it?
-----------

Yes, it's another port of [ggplot2](https://github.com/hadley/ggplot2).
One of the biggest reasons why I continue to reach for `R` instead of
`Python` for data analysis is the lack of an easy to use, high level
plotting package like `ggplot2`. I've tried other libraries like
[bokeh](https://github.com/continuumio/bokeh) and
[d3py](https://github.com/mikedewar/d3py) but what I really want is
`ggplot2`.

`ggplot` is just that. It's an extremely un-pythonic package for doing
exactly what `ggplot2` does. The goal of the package is to mimic the
`ggplot2` API. This makes it super easy for people coming over from `R`
to use, and prevents you from having to re-learn how to plot stuff.

Goals
-----

-   same API as `ggplot2` for `R`
-   ability to use both American and British English spellings of
    aesthetics
-   tight integration with [pandas](https://github.com/pydata/pandas)
-   pip installable

Getting Started
---------------

### Dependencies

This package depends on the following packages, although they should be
automatically installed if you use `pip`:

-   `matplotlib`
-   `pandas`
-   `numpy`
-   `scipy`
-   `statsmodels`
-   `patsy`

### Installation

Installing `ggplot` is really easy. Just use `pip`!

    $ pip install ggplot

### Loading `ggplot`

    # run an IPython shell (or don't)
    $ ipython
    In [1]: from ggplot import *

That's it! You're ready to go!

Examples
--------

    meat_lng = pd.melt(meat[['date', 'beef', 'pork', 'broilers']], id_vars='date')
    ggplot(aes(x='date', y='value', colour='variable'), data=meat_lng) + \
        geom_point() + \
        stat_smooth(color='red')

![image](https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/ggplot_meat.png)

### `geom_point`

    from ggplot import *
    ggplot(diamonds, aes('carat', 'price')) + \
        geom_point(alpha=1/20.) + \
        ylim(0, 20000)

![image](https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/diamonds_geom_point_alpha.png)

### `geom_histogram`

    p = ggplot(aes(x='carat'), data=diamonds)
    p + geom_histogram() + ggtitle("Histogram of Diamond Carats") + labs("Carats", "Freq")

![image](https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/diamonds_carat_hist.png)

### `geom_density`

    ggplot(diamonds, aes(x='price', color='cut')) + \
        geom_density()

![image](https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/geom_density_example.png)

    meat_lng = pd.melt(meat[['date', 'beef', 'broilers', 'pork']], id_vars=['date'])
    p = ggplot(aes(x='value', colour='variable', fill=True, alpha=0.3), data=meat_lng)
    p + geom_density()

![image](https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/density_with_fill.png)

### `geom_bar`

    p = ggplot(mtcars, aes('factor(cyl)'))
    p + geom_bar()

![image](https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/mtcars_geom_bar_cyl.png)

## Testing
To generate image test data...

In the base dir, run the tests with python tests.py, afterwards run python visual_tests.py (opens a page in a browser) and compare the plots/ make sure they look as the test intended.

Then copy the missing files from result_images/test_whatever/*.png to ggplot/tests/test_whatever/*.png. Make sure that you DON'T copy images with filenames ending in *-expected.png, as these are the copies from ggplot/tests/test_*/*.png which the test images get compared to.


TODO
----

[The list is long, but
distinguished.](https://github.com/yhat/ggplot/blob/master/TODO.md)
We're looking for contributors! Email greg at yhathq.com for more info.
For getting started with contributing, check out [these
docs](https://github.com/yhat/ggplot/blob/master/docs/contributing.rst)

[![image](https://ga-beacon.appspot.com/UA-46996803-1/ggplot/README.md)](https://github.com/yhat/ggplot)
