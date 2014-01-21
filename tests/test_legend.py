from __future__ import print_function

from ggplot import *

p = ggplot(mtcars, aes(x='qsec', y='mpg', color='cyl', size='hp')) + geom_point()
print(p)
plt.show(1)
