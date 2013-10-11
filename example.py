import pandas as pd
import numpy as np
from ggplot import *
from pandasql import load_meat

meat = load_meat()

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



# p + geom_point() + geom_line(color='lightblue') + ggtitle("Beef: It's What's for Dinner") + xlab("Date") + ylab("Head of Cattle Slaughtered")

meat_lng = pd.melt(meat, id_vars=['date'])
p = ggplot(aes(x="date", y="value", colour="variable", shape="variable"), meat_lng)
#print p + geom_point() + facet_grid(y="variable")
p = p + stat_smooth(se=False) + geom_point()
#print p
#ggsave(p, "gregsplot.png")

p = ggplot(aes(x='date', y='beef'), data=meat)
# print p + geom_point() + stat_smooth(se=True)

p = ggplot(aes(x='x', y='y', colour='z'), data=diamonds.head(100))
print p + geom_point() + \
    scale_colour_gradient(low="white", high="red")


p = ggplot(aes(x='date', y='beef'), data=meat)
#print p + geom_point() + scale_x_continuous("This is the X") + scale_y_continuous("Squared", limits=[0, 1500])
#print p + geom_point() + ylim(0, 1500)
#gg = ggplot(aes(x='date', y='beef'), data=meat)
#print gg + stat_smooth(se=True)
