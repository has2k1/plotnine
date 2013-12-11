from ggplot import *

p = ggplot(mtcars, aes(x='mpg', y='wt', label='name'))
print (p + geom_text())

plt.show(1)
