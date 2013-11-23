from ggplot import *
import sys

p = ggplot(aes(x='wt', y='mpg', color='factor(cyl)'), data=mtcars)
print p + geom_point()
print p + geom_point() + facet_wrap("gear")
print p + geom_point() + facet_grid("gear", "cyl")
plt.show(block=True)
sys.exit()

p = ggplot(aes(x='wt', y='cyl', color='mpg'), data=mtcars)
#print p + geom_point() + scale_color_gradient(low="gray", high="red")

p = ggplot(aes(x='wt', y='mpg', shape='factor(cyl)'), data=mtcars)
print p + geom_point() + facet_wrap('cyl')
p = ggplot(aes(x='wt', y='cyl', size='cyl'), data=mtcars)
print p + geom_point() + facet_wrap('cyl')
plt.show(block=True)


p = ggplot(aes(x='wt', y='mpg', group='cyl', linestyle='cyl'), data=mtcars)
print p + geom_line() + facet_wrap('cyl')
plt.show(block=True)

p = ggplot(aes(x='wt', y='mpg', colour='factor(cyl)', group='cyl', linestyle='cyl'), data=mtcars)
print p + geom_line()
print p + geom_line() + facet_wrap('cyl')
plt.show(block=True)

