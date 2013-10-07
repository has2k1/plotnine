import pandas as pd
import numpy as np
from ggplot import *


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
print gg + geom_density() + xlab("x label") + ylab("y label")
gg = ggplot(aes(x="x", y="y", shape="cat2", color="cat"), data=df)
print gg + geom_point() + facet_wrap(x="cat", y="cat2") 
print gg + geom_point() + facet_wrap(y="cat2") + ggtitle("My Single Facet") 
print gg + stat_smooth(color="blue") + ggtitle("My Smoothed Chart")
print gg + geom_hist() + ggtitle("My Histogram")
print gg + geom_point()

