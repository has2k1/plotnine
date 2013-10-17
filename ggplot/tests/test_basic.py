from __future__ import print_function
import os

import pandas as pd
import numpy as np

from ggplot import *

def test_smoke():
    import pylab as pl
    pl.interactive(False)
    meat = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     '..', 'exampledata', 'meat.csv'))
    meat['date'] = pd.to_datetime(meat.date)

    df = pd.DataFrame({
        "x": np.arange(0, 100),
        "y": np.arange(0, 100),
        "z": np.arange(0, 100)
    })

    df['cat'] = np.where(df.x*2 > 50, 'blah', 'blue')
    df['cat'] = np.where(df.y > 50, 'hello', df.cat)
    df['cat2'] = np.where(df.y < 15, 'one', 'two')
    df['y'] = np.sin(df.y)

    gg = ggplot(aes(x="x", y="z", color="cat", alpha=0.2), data=df)
    gg = ggplot(aes(x="x", color="c"), data=pd.DataFrame({"x": np.random.normal(0, 1, 10000), "c": ["blue" if i%2==0 else "red" for i in range(10000)]}))
    #print gg + geom_density() + xlab("x label") + ylab("y label")
    gg = ggplot(aes(x="x", y="y", shape="cat2", color="cat"), data=df)
    #print gg + geom_point() + facet_wrap(x="cat", y="cat2")
    #print gg + geom_point() + facet_wrap(y="cat2") + ggtitle("My Single Facet")
    #print gg + stat_smooth(color="blue") + ggtitle("My Smoothed Chart")
    #print gg + geom_hist() + ggtitle("My Histogram")
    #print gg + geom_point() + geom_vline(x=50, ymin=-10, ymax=10)
    #print gg + geom_point() + geom_hline(y=50, xmin=-10, xmax=10)
    df['z'] = df['y'] + 100
    gg = ggplot(aes(x='x', ymax='y', ymin='z'), data=df)
    #print gg + geom_bar() + facet_wrap(x="cat2")
    #print gg + geom_area() + facet_wrap(x="cat2")
    gg = ggplot(aes(x='x', ymax='y', ymin='z', color="cat2"), data=df)
    #print gg + geom_area()
    df['x'] = np.random.randint(0, 10, 100)
    df['y'] = np.random.randint(0, 10, 100)
    gg = ggplot(aes(x='x', y='y', shape='cat', color='cat2'), data=df)
    #print df.head()
    #print gg + geom_point()

    #print gg + stat_bin2d()

    #print ggplot(aes(x='mpg', fill=True, alpha=0.3), data=mtcars) + \
     #       geom_density()
    #plt.show(block=True)

    #p = ggplot(mtcars, aes(x='wt', y='mpg', colour='factor(cyl)', size='mpg', linetype='factor(cyl)'))
    #print p + geom_line() + geom_point()

    # p + geom_point() + geom_line(color='lightblue') + ggtitle("Beef: It's What's for Dinner") + xlab("Date") + ylab("Head of Cattle Slaughtered")

    meat_lng = pd.melt(meat[['date', 'beef', 'broilers', 'pork']], id_vars=['date'])
    meat_lng = pd.melt(meat, id_vars=['date'])


    p = ggplot(aes(x='date', y='value', colour='variable', fill=True, alpha=0.3), data=meat_lng)
    #print p + geom_density() + facet_wrap("variable")
    #print(p + geom_line() + facet_wrap("variable"))
    plt.show(1)
    # ggsave(p + geom_density(), "densityplot.png")


    p = ggplot(aes(x="date", y="value", colour="variable", shape="variable"), meat_lng)
    #print p + geom_point() + facet_grid(y="variable")
    p = p + stat_smooth(se=False) + geom_point()

    p = ggplot(aes(x='date', y='beef'), data=meat)
    # print p + geom_point() + stat_smooth(se=True)

    #p = ggplot(aes(x='x', y='y', colour='z'), data=diamonds.head(4))
    #print p + geom_point() + \
    #    scale_colour_gradient(low="white", high="red") + \
    #    facet_wrap("cut")
    #plt.show(block=True)

    #p = ggplot(aes(x='x', y='y', colour='z'), data=diamonds.head(1000))
    #print p + geom_point() + \
    #    scale_colour_gradient(low="white", high="red") + \
    #    facet_grid("cut", "clarity")
    #plt.show(block=True)

    #p = ggplot(aes(x='date', y='beef'), data=meat)
    #print p + geom_point() + scale_x_continuous("This is the X") + scale_y_continuous("Squared", limits=[0, 1500])
    #print p + geom_point() + ylim(0, 1500)
    #gg = ggplot(aes(x='date', y='beef'), data=meat)
    #print gg + stat_smooth(se=True)


    #print ggplot(aes(x='date', y='beef'), data=meat) + geom_line() + \
    #    scale_x_date(labels="%Y-%m-%d")
    #plt.show(block=True)

    #p = ggplot(aes(x='carat'), data=diamonds)
    #print p + geom_now_its_art()
    #print p + geom_density() + facet_grid("cut", "clarity")
    #plt.show(block=True)

    p = ggplot(aes(x='factor(cyl)'), data=mtcars)
    #print(p + geom_bar())
    plt.show(block=True)
    #ggsave(p + geom_bar(), "public/img/mtcars_geom_bar_cyl.png")

    p = ggplot(aes(x='date_hour', y='pageviews'), data=pageviews)
    #print(p + geom_point())
    plt.show(1)



