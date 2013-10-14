from ggplot import *

p = ggplot(mtcars, aes('cyl'))
print p + geom_bar()

plt.show(1)
